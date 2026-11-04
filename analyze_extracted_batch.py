import struct, math, json
from pathlib import Path

def read_npy_f8(raw: bytes):
    header_end = raw.find(b'\n') + 1
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

# Let's inspect Segah tracks across Foroutan, Hormozi, and Safvat
segah_tracks = [
    ("strikes_foroutan_segah_zabol.npz", "Foroutan - Segah Zabol"),
    ("strikes_foroutan_segah_muye.npz", "Foroutan - Segah Muye"),
    ("strikes_foroutan_segah_mokhalef.npz", "Foroutan - Segah Mokhalef"),
    ("strikes_hormozi_segah_zabol.npz", "Hormozi - Segah Zabol"),
    ("strikes_hormozi_segah_muye.npz", "Hormozi - Segah Muye"),
    ("strikes_hormozi_segah_mokhalef.npz", "Hormozi - Segah Mokhalef"),
    ("strikes_Safvat_Setar_1962_LNwPd8_hP74.npz", "Safvat - 1962 Setar"),
    ("strikes_Safvat_Setar_Razavi_Utah_yvZh-u4C6jY.npz", "Safvat & Razavi - Utah Live")
]

results = {}

for fname, title in segah_tracks:
    p = Path("analysis") / fname
    if not p.exists():
        continue
    data = read_npz(p)
    freqs = [f for f, c in zip(data['f'], data['conf']) if c > 0.4 and 100 < f < 750]
    if not freqs:
        continue
    
    # 10 cent histogram
    cents_ref = [1200.0 * math.log2(f / 200.0) for f in freqs]
    min_c = int(math.floor(min(cents_ref) / 10.0)) * 10
    max_c = int(math.ceil(max(cents_ref) / 10.0)) * 10
    nbins = (max_c - min_c) // 10 + 1
    bins = [0] * nbins
    for c in cents_ref:
        idx = int((c - min_c) / 10.0)
        bins[idx] += 1
    
    # Mode
    max_idx = bins.index(max(bins))
    tonic_f = 200.0 * (2.0 ** ((min_c + max_idx * 10.0 + 5.0) / 1200.0))
    
    # Folded relative cents [-100, 1100]
    cents_rel = [1200.0 * math.log2(f / tonic_f) for f in freqs]
    folded = []
    for c in cents_rel:
        while c < -100: c += 1200
        while c >= 1100: c -= 1200
        folded.append(c)
        
    # Find scale degree clusters (peaks)
    nb = 120
    b_counts = [0] * nb
    for c in folded:
        b_idx = int(round(c / 10.0)) % 120
        b_counts[b_idx] += 1
        
    peaks = []
    for i in range(nb):
        prev_i = (i - 1) % nb
        next_i = (i + 1) % nb
        if b_counts[i] > b_counts[prev_i] and b_counts[i] > b_counts[next_i] and b_counts[i] >= 5:
            c_val = i * 10.0
            if c_val > 1050: c_val -= 1200
            peaks.append((round(c_val, 1), b_counts[i]))
            
    peaks.sort(key=lambda x: x[1], reverse=True)
    results[title] = {
        "n_strikes": len(freqs),
        "tonic_f": round(tonic_f, 1),
        "peaks": peaks[:6]
    }

print("=== Segah & Safvat Pitch Degrees ===")
for title, d in results.items():
    print(f"\n{title} (Tonic: {d['tonic_f']} Hz, N={d['n_strikes']}):")
    for c, cnt in sorted(d['peaks'], key=lambda x: x[0]):
        print(f"  {c:+6.1f}¢ (count={cnt})")

