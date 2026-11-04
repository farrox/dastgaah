import zipfile, struct, math, os, glob
from pathlib import Path

def read_npy_f8(raw: bytes):
    header_end = raw.find(b'\n') + 1
    data = raw[header_end:]
    n = len(data) // 8
    return struct.unpack(f'<{n}d', data[:n*8])

def read_npz(path: Path):
    out = {}
    with zipfile.ZipFile(path, 'r') as z:
        for name in z.namelist():
            raw = z.read(name)
            arr = read_npy_f8(raw)
            clean_name = name.replace('.npy', '')
            out[clean_name] = arr
    return out

# Audit existing extracted summary files
summaries = list(Path("analysis").glob("*summary*.json")) + list(Path("analysis").glob("*consensus*.json"))
for s in summaries:
    print(s.name)

