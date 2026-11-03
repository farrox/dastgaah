import struct
import zipfile
from pathlib import Path

def load_npz_pure(path: Path) -> dict:
    """Read a .npz file created by save_npz_pure without external dependencies."""
    out = {}
    with zipfile.ZipFile(path, mode="r") as zf:
        for name in zf.namelist():
            if not name.endswith(".npy"):
                continue
            key = name[:-4]
            raw = zf.read(name)
            # Parse NPY header
            # \x93NUMPY + major + minor + header_len
            major, minor = raw[6], raw[7]
            if major == 1:
                hlen = struct.unpack("<H", raw[8:10])[0]
                hbytes = raw[10:10+hlen]
                offset = 10 + hlen
            else:
                hlen = struct.unpack("<I", raw[8:12])[0]
                hbytes = raw[12:12+hlen]
                offset = 12 + hlen
            
            hstr = hbytes.decode("ascii", errors="ignore")
            # Parse descr and shape from dictionary string
            # e.g. {'descr': '<f8', 'fortran_order': False, 'shape': (1234,), }
            import ast
            hdict = ast.literal_eval(hstr.strip())
            descr = hdict["descr"]
            shape = hdict["shape"]
            count = shape[0] if shape else 0
            
            payload = raw[offset:]
            if descr == "<f8":
                vals = list(struct.unpack(f"<{count}d", payload))
            elif descr == "<f4":
                vals = list(struct.unpack(f"<{count}f", payload))
            elif descr.startswith("<U") or descr.startswith("|U") or descr.startswith("<S") or descr.startswith("|S"):
                itemsize = int(''.join(filter(str.isdigit, descr)) or 1)
                # UTF-32 LE for U
                if "U" in descr:
                    elem_len = itemsize * 4
                    vals = []
                    for i in range(count):
                        sub = payload[i*elem_len:(i+1)*elem_len]
                        s = sub.decode("utf-32-le", errors="ignore").rstrip("\x00")
                        vals.append(s)
                else:
                    vals = []
                    for i in range(count):
                        sub = payload[i*itemsize:(i+1)*itemsize]
                        s = sub.decode("utf-8", errors="ignore").rstrip("\x00")
                        vals.append(s)
            else:
                vals = []
            out[key] = vals
    return out
