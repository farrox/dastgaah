import json, math, struct
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

# Let's inspect all npz files related to Shur and Abuata across performers
# We need to compute exact event counts, performer-level medians, IQRs, Q1, Q3, min, max
npz_files = sorted(list(Path("analysis").glob("strikes_*.npz")))
print(f"Total strike NPZ files available: {len(npz_files)}")

# Define performer mapping and epoch
# Epoch 1: Qajar (1906-1914)
# Epoch 2: Radif masters (1950s-1970s)
# Epoch 3: Modern revival (1980s-Present)

