#!/usr/bin/env python3
"""Rebuild consensus_template.json from cached strikes_*.npz only (no audio I/O).

Mahur v2 refinement:
  1. Multi-anchor track Do estimation (`multi_anchor_track_do`) rescues modulating
     gusheh tracks (Delkash, Shekaste, Khosravani, Feyli, Araq, Rak, etc.) whose
     primary shāhed shifts away from Do while the open-string tuning remains fixed.
  2. Selective octave-folding: diatonic skeleton degrees (Re, Fa, Sol, La, Si) pool
     ±1200¢ (`octave_fold=True`), whereas Do, Mi, and chromatic/modal degrees
     (`Mi♭↓`, `Laᵏ↓`, `Siᵏ`, `Reᵏ`, `Miᵏ`, `Laᵏ↑`) are measured natively
     (`octave_fold=False`) within non-bleeding windows so `Miᵏ` (+288¢) is not
     folded into `Mi↓` (−912¢) and `Reᵏ` (+139¢) / `Laᵏ↓` (−354¢) do not bleed
     into `Re` (+201¢) / `La` (−300¢).

Usage:
  python3 analysis/rebuild_consensus_from_cache.py
  micromamba run -n freqs python analysis/rebuild_consensus_from_cache.py
"""
from __future__ import annotations

import ast
import json
import math
import statistics
import struct
import zipfile
from collections import defaultdict
from pathlib import Path

try:
    import numpy as np
except ImportError:
    np = None

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis"

# Structural diatonic skeleton anchors (cents vs Do) for multi-anchor track Do rescue
STRUCTURAL_ANCHORS = (-702.0, -498.0, -294.1, -209.4, 0.0, 203.9, 399.5, 498.0, 702.0, 1200.0)


def _read_npy(fp) -> list:
    fp.read(6)
    major, _ = struct.unpack("<BB", fp.read(2))
    hdr_len = struct.unpack("<H" if major == 1 else "<I", fp.read(2 if major == 1 else 4))[0]
    hdr = ast.literal_eval(fp.read(hdr_len).decode("latin1").strip())
    descr, shape = hdr["descr"], hdr["shape"]
    n = 1
    for s in shape:
        n *= s
    raw = fp.read()
    if descr in ("<f8", "f8"):
        return list(struct.unpack(f"<{n}d", raw[: n * 8]))
    if descr in ("<f4", "f4"):
        return list(struct.unpack(f"<{n}f", raw[: n * 4]))
    if descr in ("<i8", "i8"):
        return list(struct.unpack(f"<{n}q", raw[: n * 8]))
    if "U" in descr:
        w = int(descr.split("U")[1])
        return [raw[i * w * 4 : (i + 1) * w * 4].decode("utf-32-le").rstrip("\x00") for i in range(n)]
    return []


def load_npz_dict(path: Path) -> dict[str, list]:
    if np is not None:
        d = np.load(path, allow_pickle=True)
        out = {}
        for k in d.files:
            arr = d[k]
            if arr.ndim == 0:
                out[k] = [ arr.item() ]
            else:
                out[k] = arr.tolist()
        return out
    with zipfile.ZipFile(path) as z:
        return {name[:-4]: _read_npy(z.open(name)) for name in z.namelist() if name.endswith(".npy")}


def cents_scalar(a: float, b: float) -> float:
    return 1200.0 * math.log2(float(a) / float(b))


def cents(a, b):
    if np is not None and ( hasattr(a, "__len__") or hasattr(b, "__len__") ):
        return 1200.0 * np.log2(np.asarray(a, dtype=float) / np.asarray(b, dtype=float))
    if isinstance(a, list):
        return [cents_scalar(x, b) for x in a]
    return cents_scalar(a, b)


def octave_residual_list(cents_arr: list[float], target: float) -> list[float]:
    """Signed distance to nearest octave copy of target, in (-600, 600]."""
    t = float(target)
    return [((float(c) - t + 600.0) % 1200.0) - 600.0 for c in cents_arr]


def measure_cents(
    cents_arr,
    target: float,
    window: float = 55.0,
    match: float = 40.0,
    min_n: int = 8,
    octave_fold: bool = True,
    bounds: tuple[float, float] | None = None,
):
    """Match a degree, either pooling ±1 octave (`octave_fold=True`) or natively (`octave_fold=False`).

    When `bounds=(lo, hi)` is provided on a native-only slot, only strikes inside `[lo, hi]`
    are considered so adjacent diatonic peaks (e.g. Re at +201¢ or La at −300¢) cannot bleed
    into koron clusters (e.g. Reᵏ at +139¢ or Laᵏ↓ at −354¢).
    """
    c_list = [float(x) for x in cents_arr]
    t = float(target)

    if not octave_fold:
        if bounds is not None:
            lo, hi = bounds
            near = [x for x in c_list if lo <= x <= hi]
        else:
            near = [x for x in c_list if abs(x - t) <= window]
        if len(near) < min_n:
            return None
        ctr = float(statistics.median(near))
        for _ in range(3):
            cl = [x for x in near if abs(x - ctr) <= match]
            if len(cl) < min_n:
                return None
            ctr = float(statistics.median(cl))
        ok_flag = (bounds[0] <= ctr <= bounds[1]) if bounds is not None else (abs(ctr - t) <= match)
        return {
            "matched_cents": ctr,
            "delta": ctr - t,
            "n": int(len(cl)),
            "ok": bool(ok_flag),
            "octave_folded": False,
            "native": True,
            "n_native": int(len(cl)),
        }

    # Native-octave strikes (no wrap)
    native_near = [x for x in c_list if abs(x - t) <= window]
    n_native_raw = len(native_near)

    res = octave_residual_list(c_list, t)
    near_res = [r for r in res if abs(r) <= window]
    if len(near_res) < min_n:
        return None
    ctr_res = float(statistics.median(near_res))
    for _ in range(3):
        cl = [r for r in near_res if abs(r - ctr_res) <= match]
        if len(cl) < min_n:
            return None
        ctr_res = float(statistics.median(cl))
    matched = float(t + ctr_res)

    if n_native_raw >= min_n:
        nctr = float(statistics.median(native_near))
        for _ in range(3):
            ncl = [x for x in native_near if abs(x - nctr) <= match]
            if len(ncl) < min_n:
                n_native = 0
                break
            nctr = float(statistics.median(ncl))
        else:
            n_native = int(len(ncl))
    else:
        n_native = 0

    return {
        "matched_cents": matched,
        "delta": matched - t,
        "n": int(len(cl)),
        "ok": abs(ctr_res) <= match,
        "octave_folded": True,
        "native": n_native >= min_n,
        "n_native": n_native,
    }


def est_track_do(fs, seed: float, window: float = 70.0, min_n: int = 5):
    f_list = [float(x) for x in fs]
    if len(f_list) < min_n:
        return None
    near = [f for f in f_list if abs(cents_scalar(f, seed)) <= window]
    if len(near) < min_n:
        return None
    ctr = float(statistics.median(near))
    for _ in range(3):
        cl = [f for f in near if abs(cents_scalar(f, ctr)) <= 40.0]
        if len(cl) < min_n:
            return None
        ctr = float(statistics.median(cl))
    if abs(cents_scalar(ctr, seed)) > 60.0:
        return None
    return ctr


def multi_anchor_track_do(fs, seed: float, fallback_do: float | None = None):
    """Estimate per-track Do:
    1. Try direct Do peak near `seed` via `est_track_do`.
    2. If a modulating gusheh (e.g. Delkash, Shekaste, Rak, Zirafkand) has too few
       direct Do strikes, lock Do within ±45¢ of `fallback_do` (or `seed`) by maximizing
       alignment of the structural diatonic skeleton (Fa↓, Sol↓, La↓, Si↓, Do, Re, Mi, Fa↑, Sol↑, Do↑).
    """
    f_list = [float(x) for x in fs]
    direct = est_track_do(f_list, seed)
    if direct is not None:
        return direct, "direct"
    ref = float(fallback_do if fallback_do is not None else seed)
    best_do, best_score, best_n = None, -1.0, 0
    for dc in [i * 1.0 for i in range(-45, 46)]:
        cand_do = ref * (2.0 ** (dc / 1200.0))
        score, n_hit = 0.0, 0
        for f in f_list:
            c = cents_scalar(f, cand_do)
            err = min(abs(c - a) for a in STRUCTURAL_ANCHORS)
            if err <= 28.0:
                score += math.exp(-err / 12.0)
                n_hit += 1
        if n_hit >= 6 and score > best_score:
            best_score, best_do, best_n = score, cand_do, n_hit
    if best_do is not None:
        return best_do, f"rescued(n={best_n})"
    return None, "skipped"


def album_cents_from_npz(path: Path, seed: float, rescue_modulating: bool = True):
    d = load_npz_dict(path)
    fs = [float(x) for x in d["f"]]
    tracks = [str(x) for x in d["track"]]
    by_tr: dict[str, list[float]] = {}
    for f, tr in zip(fs, tracks):
        by_tr.setdefault(tr, []).append(f)

    c_all: list[float] = []
    dos: dict[str, float] = {}
    n_direct = 0
    n_rescued = 0
    skipped = 0
    last_do = float(seed)

    for tr in sorted(by_tr):
        if rescue_modulating:
            do, mode = multi_anchor_track_do(by_tr[tr], seed, last_do)
        else:
            do = est_track_do(by_tr[tr], seed)
            mode = "direct" if do is not None else "skipped"
        if do is None:
            skipped += 1
            continue
        dos[tr] = do
        last_do = do
        if mode == "direct":
            n_direct += 1
        else:
            n_rescued += 1
        c_all.extend(cents_scalar(f, do) for f in by_tr[tr])

    do_vals = list(dos.values()) if dos else [float(seed)]
    med_do = float(statistics.median(do_vals))
    if len(do_vals) > 1:
        c_devs = [cents_scalar(v, med_do) for v in do_vals]
        mean_c = sum(c_devs) / len(c_devs)
        std_c = math.sqrt(sum((x - mean_c) ** 2 for x in c_devs) / len(c_devs))
        rng_c = cents_scalar(max(do_vals), min(do_vals))
    else:
        std_c, rng_c = 0.0, 0.0

    stats = {
        "seed": float(seed),
        "median_do": med_do,
        "std_cents": float(std_c),
        "range_cents": float(rng_c),
        "n_tracks_used": len(dos),
        "n_tracks_direct": n_direct,
        "n_tracks_rescued": n_rescued,
        "n_tracks_skipped": skipped,
        "n_strikes": int(len(c_all)),
        "do_mode": "per_track_multi_anchor" if rescue_modulating else "per_track",
    }
    return c_all, stats


# Candidate slots:
# (label, target_cents, octave_fold, bounds_or_None)
CANDS = [
    ("Re↓", -1000.0, True, None),
    ("Mi♭↓", -798.0, False, (-838.0, -755.0)),
    ("Fa", -702.0, True, None),
    ("Sol", -498.0, True, None),
    ("Laᵏ↓", -355.0, False, (-425.0, -338.0)),
    ("La", -298.0, True, None),
    ("Si", -209.0, True, None),
    ("Siᵏ", -100.0, False, (-145.0, -65.0)),
    ("Do", 0.0, False, None),
    ("Reᵏ", 138.0, False, (95.0, 158.0)),
    ("Re", 202.0, True, None),
    ("Miᵏ", 288.0, False, (255.0, 326.0)),
    ("Mi", 400.0, False, None),
    ("Fa↑", 498.0, True, None),
    ("Sol↑", 702.0, True, None),
    ("Laᵏ↑", 838.0, False, (810.0, 862.0)),
    ("La↑", 902.0, True, None),
]


def degrees_from_cents(c_all: list[float], cands=CANDS, min_frac: float = 0.0025):
    dets = []
    n_tot = max(len(c_all), 1)
    for item in cands:
        if len(item) == 2:
            lab, tc = item
            fold, bounds = True, None
        else:
            lab, tc, fold, bounds = item
        # Use slightly lower count floor for Gusheh-specific koron slots
        slot_min_n = max(6, int(min_frac * n_tot)) if fold else max(6, int(0.0015 * n_tot))
        slot_match = 40.0 if fold else (28.0 if bounds is not None else 40.0)
        m = measure_cents(
            c_all,
            tc,
            match=slot_match,
            min_n=slot_min_n,
            octave_fold=fold,
            bounds=bounds,
        )
        if m is None:
            dets.append(
                {
                    "label": lab,
                    "template_cents": float(tc),
                    "ok": False,
                    "matched_cents": None,
                    "delta_cents": None,
                    "n": 0,
                    "octave_folded": bool(fold),
                    "native": False,
                    "n_native": 0,
                }
            )
        else:
            dets.append(
                {
                    "label": lab,
                    "template_cents": float(tc),
                    "ok": bool(m["ok"]),
                    "matched_cents": float(m["matched_cents"]),
                    "delta_cents": float(m["delta"]),
                    "n": int(m["n"]),
                    "octave_folded": bool(m.get("octave_folded", fold)),
                    "native": bool(m.get("native", True)),
                    "n_native": int(m.get("n_native", m["n"])),
                }
            )
    return dets


SEEDS = {
    "nariman": 266.2,
    "alizadeh": 332.2,
    "shekarchi": 441.2,
    "borumand": 327.0,
    "shahnazi": 385.2,
}


def _sliding_stats(d: dict[str, list], default_seed: float, mode_name: str):
    do_hz = [float(x) for x in d["do_hz"]]
    c_arr = [float(x) for x in d["cents"]]
    seed_val = float(d["seed"][0]) if "seed" in d and d["seed"] else float(default_seed)
    med = float(statistics.median(do_hz))
    c_devs = [cents_scalar(x, med) for x in do_hz]
    mean_c = sum(c_devs) / len(c_devs)
    std_c = math.sqrt(sum((x - mean_c) ** 2 for x in c_devs) / len(c_devs))
    return c_arr, {
        "seed": seed_val,
        "median_do": med,
        "std_cents": float(std_c),
        "range_cents": float(cents_scalar(max(do_hz), min(do_hz))),
        "n_tracks_used": int(len(do_hz)),
        "n_tracks_direct": int(len(do_hz)),
        "n_tracks_rescued": 0,
        "n_tracks_skipped": 0,
        "n_strikes": int(len(c_arr)),
        "do_mode": mode_name,
    }


def load_lotfi_cents():
    p = OUT / "lotfi_local_do.npz"
    if not p.exists():
        raise FileNotFoundError(p)
    return _sliding_stats(load_npz_dict(p), 326.3, "sliding_window_45s_hop_15s")


def load_ebadi_cents():
    p = OUT / "ebadi_local_do.npz"
    if not p.exists():
        raise FileNotFoundError(p)
    d = load_npz_dict(p)
    return _sliding_stats(d, float(statistics.median(d["do_hz"])), "sliding_window_45s_hop_15s_mahur_only")


def load_saba_cents():
    p = OUT / "saba_local_do.npz"
    if not p.exists():
        raise FileNotFoundError(p)
    d = load_npz_dict(p)
    return _sliding_stats(d, float(statistics.median(d["do_hz"])), "sliding_window_45s_hop_15s_setar_mahoor")


def load_lotfi_mahur_cents():
    filt = json.loads((OUT / "lotfi_playlist_filter.json").read_text())
    pl = load_npz_dict(OUT / "strikes_lotfi_playlist.npz")
    fs = [float(x) for x in pl["f"]]
    tr = [str(x) for x in pl["track"]]
    do_by = {k["track"]: float(k["do"]) for k in filt["kept"]}
    c_all = [cents_scalar(f, do_by[t]) for f, t in zip(fs, tr) if t in do_by]
    dos = list(do_by.values())
    med = float(filt["median_do"])
    c_devs = [cents_scalar(v, med) for v in dos]
    mean_c = sum(c_devs) / len(c_devs)
    std_c = math.sqrt(sum((x - mean_c) ** 2 for x in c_devs) / len(c_devs)) if len(dos) > 1 else 0.0
    return c_all, {
        "seed": float(filt["seed_do"]),
        "median_do": med,
        "std_cents": float(std_c),
        "range_cents": float(cents_scalar(max(dos), min(dos))) if len(dos) > 1 else 0.0,
        "n_tracks_used": len(dos),
        "n_tracks_direct": len(dos),
        "n_tracks_rescued": 0,
        "n_tracks_skipped": len(filt.get("skipped", [])) + len(filt.get("title_skipped_not_downloaded", [])),
        "n_strikes": int(len(c_all)),
        "do_mode": "per_track_curated_playlist",
    }


def load_forutan_cents():
    prev = OUT / "consensus_template.json"
    seed = 224.8273327278039
    if prev.exists():
        old = json.loads(prev.read_text())
        seed = old.get("forutan_filter", {}).get("seed_do") or old["do_stats"].get("forutan", {}).get("seed", seed)
    c_all, stats = album_cents_from_npz(OUT / "strikes_forutan.npz", float(seed), rescue_modulating=True)
    stats["do_mode"] = "per_track_mahur_only"
    return c_all, stats


def load_neydavud_cents():
    filt = json.loads((OUT / "neydavud_filter.json").read_text())
    seed = float(filt.get("median_do") or filt["seed_do"])
    c_all, stats = album_cents_from_npz(OUT / "strikes_neydavud.npz", seed, rescue_modulating=True)
    stats["do_mode"] = "per_track_multi_anchor_rescued"
    return c_all, stats


def load_kasaei_radif_cents():
    filt = json.loads((OUT / "kasaei_radif_filter.json").read_text())
    seed = float(filt["seed_do"])
    c_all, stats = album_cents_from_npz(OUT / "strikes_kasaei_radif.npz", seed, rescue_modulating=True)
    stats["do_mode"] = "per_track_setar_mahoor_radif_rescued"
    return c_all, stats


def load_karimi_cents():
    filt = json.loads((OUT / "karimi_filter.json").read_text())
    seed = float(filt["seed_do"])
    c_all, stats = album_cents_from_npz(OUT / "strikes_karimi.npz", seed, rescue_modulating=True)
    stats["do_mode"] = "per_track_vocal_mahur_rescued"
    return c_all, stats


def rebuild(write: bool = True):
    artist_cents = {}
    do_stats = {}

    for name, seed in SEEDS.items():
        c_all, stats = album_cents_from_npz(OUT / f"strikes_{name}.npz", seed, rescue_modulating=True)
        artist_cents[name] = c_all
        do_stats[name] = stats

    for name, loader in [
        ("lotfi", load_lotfi_cents),
        ("lotfi_mahur", load_lotfi_mahur_cents),
        ("forutan", load_forutan_cents),
        ("neydavud", load_neydavud_cents),
        ("ebadi", load_ebadi_cents),
        ("kasaei_radif", load_kasaei_radif_cents),
        ("saba", load_saba_cents),
        ("karimi", load_karimi_cents),
    ]:
        c_all, stats = loader()
        artist_cents[name] = c_all
        do_stats[name] = stats

    artist_details = {n: degrees_from_cents(c, CANDS) for n, c in artist_cents.items()}

    by_slot = defaultdict(dict)
    for name, dets in artist_details.items():
        for d in dets:
            if d["ok"] and d["matched_cents"] is not None:
                by_slot[d["label"]][name] = d["matched_cents"]

    n_art = len(artist_details)
    consensus, solo = [], []
    for lab, tc, fold, _ in CANDS:
        vals = by_slot.get(lab, {})
        if lab == "Do":
            consensus.append(
                {
                    "label": "Do",
                    "name": "Do",
                    "cents": 0.0,
                    "octave_folded": False,
                    "n_artists": n_art,
                    "per_artist": {a: 0.0 for a in artist_details},
                }
            )
            continue
        if len(vals) < 2:
            if vals:
                solo.append(
                    {
                        "label": lab,
                        "name": lab,
                        "cents": round(list(vals.values())[0], 1),
                        "artist": list(vals.keys())[0],
                    }
                )
            continue
        med = float(statistics.median(list(vals.values())))
        consensus.append(
            {
                "label": lab,
                "name": lab,
                "cents": round(med, 1),
                "octave_folded": bool(fold),
                "n_artists": len(vals),
                "per_artist": {k: round(v, 1) for k, v in vals.items()},
            }
        )

    prev = {}
    prev_path = OUT / "consensus_template.json"
    if prev_path.exists():
        prev = json.loads(prev_path.read_text())

    out = {
        "method": "rebuild_consensus_from_cache.py v3 — 4-stage HM-LS/PV + Parabolic YIN + NB-Hilbert 140 ms plateau + modulation gate + multi-anchor local-Do rescue + selective octave folding",
        "min_artists": 2,
        "octave_fold": True,
        "do_stats": do_stats,
        "slots": consensus,
        "solo_excluded": solo,
        "albums": {
            name: {
                "median_do": do_stats[name]["median_do"],
                "do_drift_std_cents": do_stats[name]["std_cents"],
                "do_drift_range_cents": do_stats[name]["range_cents"],
                "n_tracks_used": do_stats[name]["n_tracks_used"],
                "n_tracks_direct": do_stats[name].get("n_tracks_direct", do_stats[name]["n_tracks_used"]),
                "n_tracks_rescued": do_stats[name].get("n_tracks_rescued", 0),
                "n_tracks_skipped": do_stats[name]["n_tracks_skipped"],
                "details": artist_details[name],
                "n_strikes": do_stats[name]["n_strikes"],
                "do_mode": do_stats[name]["do_mode"],
            }
            for name in artist_details
        },
        "lotfi_mahur_filter": prev.get("lotfi_mahur_filter"),
        "forutan_filter": prev.get("forutan_filter"),
        "neydavud_filter": prev.get("neydavud_filter"),
        "ebadi_filter": prev.get("ebadi_filter"),
        "shahnazi_filter": prev.get("shahnazi_filter")
        or (
            json.loads((OUT / "shahnazi_filter.json").read_text())
            if (OUT / "shahnazi_filter.json").exists()
            else None
        ),
        "kasaei_radif_filter": (
            json.loads((OUT / "kasaei_radif_filter.json").read_text())
            if (OUT / "kasaei_radif_filter.json").exists()
            else prev.get("kasaei_radif_filter")
        ),
        "saba_filter": prev.get("saba_filter")
        or (
            json.loads((OUT / "saba_filter.json").read_text())
            if (OUT / "saba_filter.json").exists()
            else None
        ),
        "karimi_filter": (
            json.loads((OUT / "karimi_filter.json").read_text())
            if (OUT / "karimi_filter.json").exists()
            else prev.get("karimi_filter")
        ),
    }
    if write:
        prev_path.write_text(json.dumps(out, indent=2))
    return out


def cache_status():
    needed = [
        "strikes_nariman.npz",
        "strikes_alizadeh.npz",
        "strikes_shekarchi.npz",
        "strikes_borumand.npz",
        "strikes_forutan.npz",
        "strikes_neydavud.npz",
        "strikes_shahnazi.npz",
        "strikes_lotfi_playlist.npz",
        "lotfi_local_do.npz",
        "lotfi_playlist_filter.json",
        "neydavud_filter.json",
        "ebadi_local_do.npz",
        "shahnazi_filter.json",
        "strikes_kasaei_radif.npz",
        "kasaei_radif_filter.json",
        "saba_local_do.npz",
        "saba_filter.json",
        "strikes_karimi.npz",
        "karimi_filter.json",
        "consensus_template.json",
    ]
    rows = []
    for name in needed:
        p = OUT / name
        rows.append((name, p.exists(), p.stat().st_size if p.exists() else 0))
    return rows


if __name__ == "__main__":
    print("cache status:")
    for name, ok, sz in cache_status():
        print(f"  {'✓' if ok else '✗'} {name:35} {sz/1e3:.1f} KB" if ok else f"  ✗ {name}")
    out = rebuild(write=True)
    tot_strikes = sum(s["n_strikes"] for s in out["do_stats"].values())
    tot_rescued = sum(s.get("n_tracks_rescued", 0) for s in out["do_stats"].values())
    print(f"\nrebuilt consensus v2: {len(out['slots'])} slots, {len(out['albums'])} artists, {tot_strikes:,} strikes (+{tot_rescued} rescued modulating tracks)")
    for s in out["slots"]:
        vals = list(s["per_artist"].values())
        std = statistics.stdev(vals) if len(vals) > 1 else 0.0
        mode = "folded" if s.get("octave_folded") else "native"
        print(f"  {s['name']:6s} {s['cents']:+7.1f}¢  ({s['n_artists']:2d}/13, σ={std:4.1f}¢, {mode})")
    print("→", OUT / "consensus_template.json")
