import math
import struct
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

d = read_npz(Path("analysis/strikes_davami_11 - Abuata： Daramad.npz"))
freqs = [f for f, c in zip(d['f'], d['conf']) if c > 0.4 and 100 < f < 600]

# Compute all prominent clusters
cents_ref = [1200.0 * math.log2(f / 200.0) for f in freqs]
min_c = int(math.floor(min(cents_ref) / 10.0)) * 10
max_c = int(math.ceil(max(cents_ref) / 10.0)) * 10
nbins = (max_c - min_c) // 10 + 1
bins = [0] * nbins
for c in cents_ref:
    idx = int((c - min_c) / 10.0)
    bins[idx] += 1

clusters = []
for i in range(1, nbins - 1):
    if bins[i] > bins[i-1] and bins[i] > bins[i+1] and bins[i] >= 6:
        c_val = min_c + i * 10.0 + 5.0
        f_val = 200.0 * (2.0 ** (c_val / 1200.0))
        clusters.append((f_val, bins[i]))

clusters.sort(key=lambda x: x[1], reverse=True)
print("Davami Daramad Abuata pitch clusters:")
for f_val, cnt in clusters[:8]:
    print(f"  {f_val:.1f} Hz (N={cnt})")

# If base tonic is ~296 Hz (D)
base = 296.0
for f_val, cnt in sorted(clusters[:6], key=lambda x: x[0]):
    c = 1200.0 * math.log2(f_val / base)
    print(f"  Relative to {base} Hz: {f_val:.1f} Hz -> {c:+6.1f}¢ (N={cnt})")

