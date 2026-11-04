import zipfile, struct, math, json, glob
from pathlib import Path
from collections import defaultdict

def read_npz(path):
    arrays = {}
    with zipfile.ZipFile(path, 'r') as z:
        for name in z.namelist():
            if name.endswith('.npy'):
                buf = z.read(name)
                hlen = struct.unpack('<H', buf[8:10])[0]
                raw = buf[10+hlen:]
                n = len(raw) // 8
                arrays[name[:-4]] = list(struct.unpack(f'<{n}d', raw[:n*8]))
    return arrays

# Partition Mokhammas into Fretted Tar (Sharifi) vs Fretless Kamanche (Mardane) vs Full Ensemble
groups = {
    "Sharifi (Solo Tar - Fretted)": [
        "analysis/strikes_mokhammas_08.npz",
        "analysis/strikes_mokhammas_09.npz",
        "analysis/strikes_mokhammas_10.npz",
    ],
    "Mardane (Kamanche - Fretless)": [
        "analysis/strikes_mokhammas_04.npz",
        "analysis/strikes_mokhammas_02.npz",
    ],
    "Multi-Modal Suite (Track 11: Kereshme-Mokhammas)": [
        "analysis/strikes_mokhammas_11.npz",
    ],
    "All Mokhammas (Complete Album)": sorted(glob.glob("analysis/strikes_mokhammas_*.npz"))
}

results = {}

for gname, paths in groups.items():
    all_f = []
    all_c = []
    for p in paths:
        if not Path(p).exists():
            continue
        d = read_npz(p)
        f = d.get('f', [])
        c = d.get('conf', [])
        all_f.extend(f)
        all_c.extend(c)
        
    valid_f = [f for f, c in zip(all_f, all_c) if c > 52.0 and 100 < f < 900]
    if not valid_f:
        continue
        
    ref_hz = 220.0
    all_cents = [1200.0 * math.log2(f / ref_hz) for f in valid_f]
    
    # 10-cent histogram modulo 1200
    pc_bins = defaultdict(int)
    for c in all_cents:
        pc = round((c % 1200.0) / 10.0) * 10.0
        pc_bins[pc] += 1
        
    tonic_pc = max(pc_bins.items(), key=lambda x: x[1])[0]
    rel_cents = [((c - tonic_pc) % 1200.0) for c in all_cents]
    
    deg_windows = {
        "neutral_2nd (Re_k)": (120, 175),
        "minor_3rd": (270, 315),
        "zalzal_neutral_3rd (Mi_k)": (325, 365),
        "major_3rd (Mi)": (380, 420),
        "fourth": (480, 520),
        "motaghayyer_5th (Sol_k)": (630, 675),
        "pure_fifth": (690, 720),
        "neutral_6th (La_k)": (800, 875),
        "minor_7th": (980, 1030)
    }
    
    stats = {}
    for dname, (low, high) in deg_windows.items():
        sub = [c for c in rel_cents if low <= c <= high]
        if len(sub) >= 8:
            sub.sort()
            stats[dname] = {
                "median": round(sub[len(sub)//2], 1),
                "count": len(sub)
            }
        else:
            stats[dname] = {"median": None, "count": len(sub)}
            
    results[gname] = {
        "total_strikes": len(valid_f),
        "degrees": stats
    }

print(json.dumps(results, indent=2))
with open("analysis/mokhammas_comparative_summary.json", "w") as f:
    json.dump(results, f, indent=2)
