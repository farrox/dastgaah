#!/usr/bin/env python3
"""Dastgah-e Chahargah consensus from strikes_chahargah_*.npz (v3 pipeline output).

1. Data-driven local Do (45 s windows, 15 s hop; per track): coarse fold-score on Do/Fa/Sol/Mi/Re-koron,
   then refined as the median of the Do cluster itself (no template bias in the final value).
2. Measure each scale slot per source; consensus = median over sources.
3. Compare with the Mahur v3 consensus.
Writes analysis/chahargah_consensus.json
"""
from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rebuild_consensus_from_cache as rcc  # noqa: E402

OUT = Path(__file__).resolve().parent
MAHUR = json.load(open(OUT / "consensus_template.json"))
DS = MAHUR["do_stats"]
KEY = {"nariman": "nariman", "alizadeh": "alizadeh", "shekarchi": "shekarchi", "borumand": "borumand",
       "forutan": "forutan", "neydavud": "neydavud", "shahnazi": "shahnazi", "kasaei": "kasaei_radif",
       "karimi": "karimi", "ebadi": "ebadi", "saba": "saba", "lotfi": "lotfi"}
SOURCES = list(KEY)

# coarse anchors (folded pitch classes) and weights
COARSE = [(0.0, 1.0), (498.0, 0.7), (702.0, 0.7), (400.0, 0.4), (138.0, 0.4)]
WIN, HOP, MAXSHIFT = 45.0, 15.0, 150.0


def fold(c: float) -> float:
    return (c + 600.0) % 1200.0 - 600.0


def window_do(fs: list[float], seed: float):
    """Return Do (Hz) for strikes fs, or None."""
    if len(fs) < 8:
        return None
    best, best_s = None, 0.0
    for dc in range(-int(MAXSHIFT), int(MAXSHIFT) + 1, 2):
        do = seed * 2.0 ** (dc / 1200.0)
        s = 0.0
        for f in fs:
            c = rcc.cents_scalar(f, do)
            for a, w in COARSE:
                e = abs(fold(c - a))
                if e < 30.0:
                    s += w * math.exp(-(e / 14.0) ** 2)
        if s > best_s:
            best, best_s = do, s
    if best is None:
        return None
    ctr = best
    for _ in range(3):
        cl = [f for f in fs if abs(fold(rcc.cents_scalar(f, ctr))) <= 18.0]
        if len(cl) < 5:
            return None
        # fold strikes into the same octave as ctr
        cl = [ctr * 2.0 ** (fold(rcc.cents_scalar(f, ctr)) / 1200.0) for f in cl]
        ctr = float(statistics.median(cl))
    return ctr


def local_do_cents(t: list[float], f: list[float], seed: float):
    """Per-strike cents rel local Do for ONE track."""
    if not f:
        return [], []
    tmax = max(t)
    wins = []
    t0 = 0.0
    if tmax <= WIN:
        starts = [0.0]
        wl = tmax + 1e-6
    else:
        starts = []
        x = 0.0
        while x + WIN <= tmax + HOP:
            starts.append(x)
            x += HOP
        wl = WIN
    last = None
    for s in starts:
        fs = [ff for tt, ff in zip(t, f) if s <= tt < s + wl]
        d = window_do(fs, seed if last is None else last)
        if d is not None and abs(rcc.cents_scalar(d, seed)) <= MAXSHIFT + 10:
            wins.append((s + wl / 2.0, d))
            last = d
    if not wins:
        return [], []
    cs, dos = [], []
    for tt, ff in zip(t, f):
        d = min(wins, key=lambda w: abs(w[0] - tt))[1]
        dos.append(d)
        cs.append(rcc.cents_scalar(ff, d))
    return cs, dos


# Chahargah scale slots: (label, target, octave_fold, bounds)
CANDS_CH = [
    ("Fa↓", -702.0, True, None),
    ("Sol↓", -498.0, True, None),
    ("Laᵏ↓", -355.0, False, (-425.0, -338.0)),
    ("La↓", -300.0, False, (-338.0, -270.0)),
    ("Si↓", -209.0, True, None),
    ("Do", 0.0, False, None),
    ("Reᵏ", 138.0, False, (95.0, 175.0)),
    ("Re", 202.0, True, None),
    ("Mi", 400.0, False, (365.0, 440.0)),
    ("Fa↑", 498.0, True, None),
    ("Sol↑", 702.0, True, None),
    ("Laᵏ↑", 840.0, False, (800.0, 880.0)),
    ("Si↑", 991.0, True, None),
]


def main():
    per_source = {}
    all_cents = {}
    for src in SOURCES:
        d = rcc.load_npz_dict(OUT / f"strikes_chahargah_{src}.npz")
        by = {}
        for tt, ff, tr in zip(d["t"], d["f"], d["track"]):
            by.setdefault(str(tr), ([], []))
            by[str(tr)][0].append(float(tt))
            by[str(tr)][1].append(float(ff))
        seed = DS[KEY[src]]["median_do"]
        c_all, do_all = [], []
        n_tr_ok = 0
        for tr in sorted(by):
            c, dos = local_do_cents(by[tr][0], by[tr][1], seed)
            if c:
                n_tr_ok += 1
                c_all += c
                do_all += dos
        med_do = float(statistics.median(do_all)) if do_all else seed
        shift = rcc.cents_scalar(med_do, seed)
        dets = rcc.degrees_from_cents(c_all, CANDS_CH)
        per_source[src] = {
            "median_do": med_do, "mahur_do": seed, "do_shift_vs_mahur_cents": shift,
            "n_tracks": len(by), "n_tracks_used": n_tr_ok, "n_strikes": len(c_all),
            "do_std_cents": float(statistics.pstdev([rcc.cents_scalar(x, med_do) for x in do_all])) if do_all else 0.0,
            "details": dets,
        }
        all_cents[src] = c_all
        print(f"{src:10s} Do={med_do:7.1f}Hz (Mahur {seed:7.1f}, shift {shift:+6.1f}¢)  tracks {n_tr_ok}/{len(by)}  strikes={len(c_all)}", flush=True)

    mahur_slots = {s["label"]: s for s in MAHUR["slots"]}
    slots = []
    for lab, tc, fo, bd in CANDS_CH:
        vals = {}
        for src in SOURCES:
            for dd in per_source[src]["details"]:
                if dd["label"] == lab and dd["ok"] and dd["matched_cents"] is not None:
                    vals[src] = dd["matched_cents"]
        if len(vals) >= 4:
            v = sorted(vals.values())
            med = float(statistics.median(v))
            sd = float(statistics.pstdev(v))
        else:
            med, sd = None, None
        m = mahur_slots.get(lab)
        slots.append({
            "label": lab, "template": tc, "chahargah_cents": med, "chahargah_sd": sd, "n_artists": len(vals),
            "per_artist": vals,
            "mahur_cents": m["cents"] if m else None,
        })
    # pooled pitch-class peaks (equal weight per source)
    bins = [0.0] * 400
    for src, cs in all_cents.items():
        w = 1.0 / max(len(cs), 1)
        for c in cs:
            bins[int(((c + 600) % 1200) / 3) % 400] += w
    sm = [sum(bins[(i + k) % 400] * (1 - abs(k) / 4) for k in range(-3, 4)) for i in range(400)]
    mx = max(sm)
    peaks = [i for i in range(400) if sm[i] >= max(sm[(i - 1) % 400], sm[(i + 1) % 400]) and sm[i] > 0.05 * mx]
    peaks.sort(key=lambda i: -sm[i])
    sel = []
    for p in peaks:
        if all(min(abs(p - q), 400 - abs(p - q)) > 6 for q in sel):
            sel.append(p)
    sel.sort()
    pooled = [{"cents": float(p * 3 - 600 + 1.5), "rel_strength": float(sm[p] / mx)} for p in sel]

    res = {"sources": per_source, "slots": slots, "pooled_peaks": pooled,
           "total_strikes": sum(len(v) for v in all_cents.values())}
    (OUT / "chahargah_consensus.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
    print("\nSlot            Chahargah   sd   n |  Mahur   Δ(Ch−Mahur)")
    for s in slots:
        ch = s["chahargah_cents"]
        mh = s["mahur_cents"]
        print(f"{s['label']:6s} {('%+8.1f' % ch) if ch is not None else '   --   '} "
              f"{('%5.1f' % s['chahargah_sd']) if ch is not None else '  -- '} {s['n_artists']:2d} | "
              f"{('%+8.1f' % mh) if mh is not None else '   --   '}  "
              f"{('%+6.1f' % (ch - mh)) if (ch is not None and mh is not None) else ''}")
    print("\npooled peaks (¢):", " ".join(f"{p['cents']:+.0f}({p['rel_strength']:.2f})" for p in pooled))


if __name__ == "__main__":
    main()
