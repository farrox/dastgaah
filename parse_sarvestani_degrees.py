import struct, math, json
from pathlib import Path

def read_npy_f8(raw: bytes):
    # Find header end
    header_end = raw.find(b'\n') + 1
    # Skip header
    data = raw[header_end:]
    n = len(data) // 8
    return struct.unpack(f'<{n}d', data[:n*8])

def read_npz(path: Path):
    import zipfile
    out = {}
    with zipfile.ZipFile(path, 'r') as z:
        for name in z.namelist():
            raw = z.read(name)
            arr = read_npy_f8(raw)
            clean_name = name.replace('.npy', '')
            out[clean_name] = arr
    return out

tracks = [
    ("Abu_Ata_Daramad", "Abu Ata"),
    ("Esfahan_Suz_o_Godaz", "Esfahan"),
    ("Homayoun_Masnavi", "Homayoun"),
    ("Mahur_Daramad", "Mahur"),
    ("Nava_Daramad", "Nava"),
    ("Rast_Panjgah_Daramad", "Rast-Panjgah"),
    ("Shur_Daramad", "Shur")
]

summary = {}

for stem, title in tracks:
    npz_path = Path(f"analysis/strikes_sarvestani_talai_{stem}.npz")
    if not npz_path.exists():
        continue
    d = read_npz(npz_path)
    freqs = [f for f, c in zip(d['f'], d['conf']) if c > 0.4 and 100 < f < 800]
    if not freqs:
        continue
    
    # Simple histogram in log2 domain to find base / shahed
    # 10 cent bins
    log_pitches = [math.log2(f) for f in freqs]
    min_lp = min(log_pitches)
    max_lp = max(log_pitches)
    nbins = int((max_lp - min_lp) * 120) + 1
    bins = [0] * nbins
    for lp in log_pitches:
        idx = int((lp - min_lp) * 120)
        bins[idx] += 1
    
    # Find mode (top peak)
    max_idx = bins.index(max(bins))
    base_f = 2**(min_lp + (max_idx + 0.5) / 120.0)
    
    # Compute cents relative to base_f
    cents_list = [1200.0 * math.log2(f / base_f) for f in freqs]
    # Modulo octave into [-200, 1000]
    folded = []
    for c in cents_list:
        while c < -100:
            c += 1200
        while c >= 1100:
            c -= 1200
        folded.append(c)
        
    summary[stem] = {
        "title": title,
        "n_strikes": len(freqs),
        "base_f": round(base_f, 1),
    }

print("Sarvestani & Talai Tracks Extracted:")
for k, v in summary.items():
    print(f"  {v['title']}: {v['n_strikes']} strikes, tonic/shahed estimate: {v['base_f']} Hz")

