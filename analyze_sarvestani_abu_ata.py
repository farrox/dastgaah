import struct, math, json
from pathlib import Path
import numpy as np

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

# Analyze Abu_Ata_Daramad
data = read_npz(Path("analysis/strikes_sarvestani_talai_Abu_Ata_Daramad.npz"))
freqs = [f for f, c in zip(data['f'], data['conf']) if c > 0.4 and 100 < f < 700]

# For Abu Ata, Daramad has base Shur tonic (Do) or Abu Ata Shahed (Fa = +498c).
# Let's inspect the pitch histogram
log_f = [math.log2(f) for f in freqs]
hist, bin_edges = np.histogram(log_f, bins=250)
centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

from scipy.signal import find_peaks
peaks, props = find_peaks(hist, distance=8, prominence=5)
peak_freqs = sorted([2**centers[p] for p in peaks])
print("Prominent pitch peaks in Sarvestani & Talai Abu Ata (Hz):")
for pf in peak_freqs:
    print(f"  {pf:.2f} Hz")

# If base tonic is around 180-240 Hz
# Let's identify the pitch intervals relative to lowest fundamental
