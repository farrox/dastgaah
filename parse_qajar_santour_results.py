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

tracks = [
    ("analysis/strikes_taherzadeh_1906_abuata_santour_1.npz", "Taherzadeh & Santour Abuata I (1906)"),
    ("analysis/strikes_taherzadeh_1906_abuata_santour_2.npz", "Taherzadeh & Santour Abuata II (1906)"),
    ("analysis/strikes_rezagholikhan_1906_abuata_santour.npz", "Rezagholikhan & Santour Abuata (1906)")
]

for p_str, title in tracks:
    p = Path(p_str)
    if not p.exists():
        continue
    data = read_npz(p)
    freqs = [f for f, c in zip(data['f'], data['conf']) if c > 0.4 and 100 < f < 750]
    if not freqs:
        continue
    log_f = [math.log2(f) for f in freqs]
    min_lf = min(log_f)
    max_lf = max(log_f)
    nbins = int((max_lf - min_lf) * 120) + 1
    bins = [0] * nbins
    for lf in log_f:
        idx = int((lf - min_lf) * 120)
        bins[idx] += 1
    max_idx = bins.index(max(bins))
    tonic_f = 2.0 ** (min_lf + (max_idx + 0.5) / 120.0)
    
    folded = []
    for f in freqs:
        c = 1200.0 * math.log2(f / tonic_f)
        while c < -100: c += 1200
        while c >= 1100: c -= 1200
        folded.append(c)
        
    b_counts = [0] * 120
    for c in folded:
        b_idx = int(round(c / 10.0)) % 120
        b_counts[b_idx] += 1
        
    peaks = []
    for i in range(120):
        prev_i = (i - 1) % 120
        next_i = (i + 1) % 120
        if b_counts[i] > b_counts[prev_i] and b_counts[i] > b_counts[next_i] and b_counts[i] >= 6:
            c_val = i * 10.0
            if c_val > 1050: c_val -= 1200
            peaks.append((round(c_val, 1), b_counts[i]))
            
    peaks.sort(key=lambda x: x[1], reverse=True)
    print(f"\n{title} (Fundamental Peak: {tonic_f:.1f} Hz, N={len(freqs)}):")
    for c, cnt in sorted(peaks[:6], key=lambda x: x[0]):
        print(f"  {c:+6.1f}¢ (count={cnt})")

