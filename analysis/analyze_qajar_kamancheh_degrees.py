import zipfile, struct, json, math, glob
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

files = sorted(glob.glob('analysis/strikes_qajar_kam_*.npz'))
print(f"Found {len(files)} Qajar Kamancheh strike files.")

# Let's inspect Segah, Chahargah, Homayun, Shur, Esfahan, Nava
mode_groups = {
    "Segah (Track 15)": ["analysis/strikes_qajar_kam_15-dastgah-e-segah.npz"],
    "Chahargah (Tracks 4, 16)": [
        "analysis/strikes_qajar_kam_4-dastgah-e-chahargah-i.npz",
        "analysis/strikes_qajar_kam_16-dastgah-e-chahargah-ii.npz"
    ],
    "Homayun & Bidad (Tracks 5, 6, 7, 8, 9)": [
        "analysis/strikes_qajar_kam_5-dastgah-e-homayun-i.npz",
        "analysis/strikes_qajar_kam_6-dastgah-e-homayun-ii.npz",
        "analysis/strikes_qajar_kam_7-bidad.npz",
        "analysis/strikes_qajar_kam_8-dastgah-e-homayun-iii.npz",
        "analysis/strikes_qajar_kam_9-dastgah-e-homayun-iv.npz"
    ],
    "Shur & Hejaz & Kord (Tracks 3, 11, 13, 14)": [
        "analysis/strikes_qajar_kam_3-dastgah-e-shur-i.npz",
        "analysis/strikes_qajar_kam_11-dastgah-e-shur-ii.npz",
        "analysis/strikes_qajar_kam_13-hejaz.npz",
        "analysis/strikes_qajar_kam_14-avaz-e-bayat-e-kord.npz"
    ],
    "Esfahan (Track 2)": ["analysis/strikes_qajar_kam_2-avaz-e-esfahan.npz"],
    "Nava (Track 1)": ["analysis/strikes_qajar_kam_1-dastgah-e-nava.npz"]
}

results = {}

for gname, paths in mode_groups.items():
    all_f = []
    all_c = []
    for p in paths:
        if not Path(p).exists():
            continue
        d = read_npz(p)
        all_f.extend(d.get('f', []))
        all_c.extend(d.get('conf', []))
        
    valid = [f for f, c in zip(all_f, all_c) if c > 40.0 and 120 < f < 950]
    if not valid:
        continue
        
    ref = 220.0
    cents = [1200.0 * math.log2(f / ref) for f in valid]
    
    # 10-cent histogram modulo 1200
    bins = defaultdict(int)
    for c in cents:
        bins[round((c % 1200.0) / 10.0) * 10.0] += 1
        
    tonic_pc = max(bins.items(), key=lambda x: x[1])[0]
    tonic_hz = ref * (2.0 ** (tonic_pc / 1200.0))
    rel_cents = [((c - tonic_pc) % 1200.0) for c in cents]
    
    deg_windows = {
        "neutral_2nd (Re_k)": (120, 175),
        "minor_3rd": (270, 315),
        "zalzal_neutral_3rd (Mi_k)": (325, 365),
        "augmented_2nd": (230, 270),
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
        if len(sub) >= 4:
            sub.sort()
            stats[dname] = {
                "median": round(sub[len(sub)//2], 1),
                "count": len(sub)
            }
        else:
            stats[dname] = {"median": None, "count": len(sub)}
            
    results[gname] = {
        "tonic_hz": round(tonic_hz, 1),
        "valid_strikes": len(valid),
        "degrees": stats
    }

print(json.dumps(results, indent=2))
with open('analysis/qajar_kamancheh_degrees_summary.json', 'w') as f:
    json.dump(results, f, indent=2)
