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

npz_path = Path("analysis/strikes_saba_segah_violin_vol3.npz")
data = read_npz(npz_path)

freqs = [f for f, c in zip(data['f'], data['conf']) if c > 0.4 and 150 < f < 900]
print(f"Total confident strikes: {len(freqs)}")

# Build pitch histogram (5 cent bins)
cents_ref = [1200.0 * math.log2(f / 200.0) for f in freqs]
min_c = int(math.floor(min(cents_ref) / 5.0)) * 5
max_c = int(math.ceil(max(cents_ref) / 5.0)) * 5
nbins = (max_c - min_c) // 5 + 1
bins = [0] * nbins
for c in cents_ref:
    idx = int((c - min_c) / 5.0)
    bins[idx] += 1

# Find top peaks
peaks = []
for i in range(2, nbins - 2):
    if bins[i] > bins[i-1] and bins[i] > bins[i+1] and bins[i] >= 15:
        c_val = min_c + i * 5.0 + 2.5
        f_val = 200.0 * (2.0 ** (c_val / 1200.0))
        peaks.append((f_val, c_val, bins[i]))

peaks.sort(key=lambda x: x[2], reverse=True)
print("Top 10 prominent pitch peaks in Saba Violin Segah:")
for f_val, c_val, cnt in peaks[:10]:
    print(f"  {f_val:.1f} Hz (count={cnt})")

# Determine base tonic (Segah tonic / base note)
# Segah in violin is traditionally played with Mi Koron or La Koron base, or Do tonic.
# Let's inspect intervals between the top peaks:
top_fs = sorted([p[0] for p in peaks[:8]])
print("\nTop sorted frequencies (Hz):", [round(f, 1) for f in top_fs])

# Let's find tonic from the fundamental pitch hierarchy
# Usually Segah Daramad rests on the 3rd degree (e.g. 293 Hz or 330 Hz or 220 Hz)
# Let's test each candidate tonic to see which matches modal scale degrees:
candidates = [p[0] for p in peaks[:5]]
for cand in candidates:
    print(f"\n--- Testing Candidate Base Tonic: {cand:.1f} Hz ---")
    deg_matches = []
    for f_val, _, cnt in peaks[:8]:
        cents_diff = 1200.0 * math.log2(f_val / cand)
        folded = cents_diff % 1200
        deg_matches.append((round(folded, 1), cnt, round(f_val, 1)))
    deg_matches.sort(key=lambda x: x[0])
    for c, cnt, f_val in deg_matches:
        print(f"  {c:+6.1f}¢ (count={cnt}, {f_val} Hz)")

