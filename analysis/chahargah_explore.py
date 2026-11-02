#!/usr/bin/env python3
"""Explore pitch-class histograms of Chahargah strikes relative to each source's Mahur Do."""
import json, math, sys
from pathlib import Path
sys.path.insert(0, "/Users/ed/Developer/dastgaah/analysis")
import rebuild_consensus_from_cache as rcc

OUT = Path("/Users/ed/Developer/dastgaah/analysis")
ds = json.load(open(OUT / "consensus_template.json"))["do_stats"]
names = {"nariman": "nariman", "alizadeh": "alizadeh", "shekarchi": "shekarchi", "borumand": "borumand",
         "forutan": "forutan", "neydavud": "neydavud", "shahnazi": "shahnazi", "kasaei": "kasaei_radif",
         "karimi": "karimi", "ebadi": "ebadi", "saba": "saba", "lotfi": "lotfi"}
for src, key in names.items():
    d = rcc.load_npz_dict(OUT / f"strikes_chahargah_{src}.npz")
    do = ds[key]["median_do"]
    cs = [(rcc.cents_scalar(f, do) + 600) % 1200 - 600 for f in d["f"]]
    bins = [0.0] * 400  # 3-cent bins over -600..600
    for c in cs:
        bins[int((c + 600) / 3) % 400] += 1
    sm = [sum(bins[(i + k) % 400] * (1 - abs(k) / 4) for k in range(-3, 4)) for i in range(400)]
    peaks = [i for i in range(400) if sm[i] >= max(sm[(i - 1) % 400], sm[(i + 1) % 400]) and sm[i] > 0.03 * max(sm)]
    peaks.sort(key=lambda i: -sm[i])
    sel = []
    for p in peaks:
        if all(min(abs(p - q), 400 - abs(p - q)) > 8 for q in sel):
            sel.append(p)
        if len(sel) >= 10:
            break
    sel.sort()
    print(f"{src:10s} Do_mahur={do:7.1f}Hz n={len(cs):5d} peaks(¢ rel Mahur Do):", " ".join(f"{p*3-600+1.5:+.0f}" for p in sel))

