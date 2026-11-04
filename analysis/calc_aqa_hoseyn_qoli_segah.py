import zipfile, struct, json, math
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

tracks = [
    ('12 - Daramad', 'analysis/strikes_qajar_12.npz'),
    ('13 - Zabol & Hesar', 'analysis/strikes_qajar_13.npz'),
    ('14 - Mokhalef', 'analysis/strikes_qajar_14.npz')
]

all_f = []
all_c = []
for title, p in tracks:
    d = read_npz(p)
    print(f"{title}: {len(d['f'])} raw strikes")
    all_f.extend(d['f'])
    all_c.extend(d['conf'])

valid = [f for f, c in zip(all_f, all_c) if c > 45.0 and 120 < f < 950]
print(f"Total valid strikes: {len(valid)}")

ref = 220.0
cents = [1200.0 * math.log2(f / ref) for f in valid]

# In Track 12 Daramad, find Ist (Mi Koron)
d12 = read_npz('analysis/strikes_qajar_12.npz')
v12 = [f for f, c in zip(d12['f'], d12['conf']) if c > 45.0 and 120 < f < 950]
c12 = [1200.0 * math.log2(f / ref) for f in v12]
b12 = defaultdict(int)
for c in c12:
    b12[round(c / 10.0) * 10.0] += 1
ist_pc = sorted(b12.items(), key=lambda x: x[1], reverse=True)[0][0]
ist_hz = ref * (2.0 ** (ist_pc / 1200.0))
print(f"Aqa Hoseyn-Qoli Segah Ist (Mi Koron): {ist_hz:.1f} Hz")

rel_cents = [c - ist_pc for c in cents]
folded_cents = [((c + 200.0) % 1200.0) - 200.0 for c in rel_cents]

segah_degrees = [
    ("Zir-e Ist (Re)", -175, -125, -147.9),
    ("Ist (Mi Koron)", -25, 25, 0.0),
    ("Zabol (Fa)", 120, 165, 141.5),
    ("Muyeh (Sol)", 330, 375, 352.2),
    ("Hesar (La Koron)", 475, 520, 493.5),
    ("Shahkhatayi (Si flat)", 680, 720, 697.5),
    ("Mokhalef (Do)", 830, 875, 850.4),
    ("Octave (Mi Koron)", 1180, 1220, 1200.0)
]

print("\nAqa Hoseyn-Qoli (1909) Segah Scale Degrees relative to Mi Koron (0.0c):")
results = {}
for deg, low, high, tgt in segah_degrees:
    sub = [c for c in folded_cents if low <= c <= high]
    if sub:
        sub.sort()
        med = sub[len(sub)//2]
        delta = med - tgt
        print(f"  {deg:24s}: {med:+6.1f}c (tgt: {tgt:+6.1f}c, delta: {delta:+4.1f}c, n={len(sub):2d})")
        results[deg] = {"measured": round(med, 1), "target": tgt, "delta": round(delta, 1), "count": len(sub)}
    else:
        print(f"  {deg:24s}: None")

with open('analysis/aqa_hoseyn_qoli_segah_scale_degrees.json', 'w') as f:
    json.dump(results, f, indent=2)
