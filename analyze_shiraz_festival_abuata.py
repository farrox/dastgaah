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

data = read_npz(Path("analysis/strikes_shiraz_festival_abuata.npz"))
freqs = [f for f, c in zip(data['f'], data['conf']) if c > 0.4 and 100 < f < 750]
print(f"Total confident strikes in Shiraz Festival Abuata: {len(freqs)}")

# Build pitch histogram (5 cent bins)
cents_ref = [1200.0 * math.log2(f / 200.0) for f in freqs]
min_c = int(math.floor(min(cents_ref) / 5.0)) * 5
max_c = int(math.ceil(max(cents_ref) / 5.0)) * 5
nbins = (max_c - min_c) // 5 + 1
bins = [0] * nbins
for c in cents_ref:
    idx = int((c - min_c) / 5.0)
    bins[idx] += 1

peaks = []
for i in range(2, nbins - 2):
    if bins[i] > bins[i-1] and bins[i] > bins[i+1] and bins[i] >= 15:
        c_val = min_c + i * 5.0 + 2.5
        f_val = 200.0 * (2.0 ** (c_val / 1200.0))
        peaks.append((f_val, bins[i]))

peaks.sort(key=lambda x: x[1], reverse=True)
print("Prominent pitch peaks in Shiraz Festival Concert (Taj, Shahnaz, Kasaei):")
for f_val, cnt in peaks[:10]:
    print(f"  {f_val:.1f} Hz (N={cnt})")

# Determine base tonic (Shur / Abuata base)
# Shahnaz Tar & Kasaei Ney in Abuata usually tuned to Do or Re base
# Let's inspect the intervals relative to candidate bases:
for base_cand in [197.0, 220.0, 246.0, 293.5, 330.0]:
    print(f"\n--- Testing Base: {base_cand} Hz ---")
    deg_list = []
    for f_val, cnt in peaks[:8]:
        c = 1200.0 * math.log2(f_val / base_cand)
        deg_list.append((c % 1200, cnt, f_val))
    deg_list.sort(key=lambda x: x[0])
    for c, cnt, f_val in deg_list:
        print(f"  {c:+6.1f}¢ (N={cnt}, {f_val:.1f} Hz)")

