#!/usr/bin/env python3
"""Run v3 4-stage strike extractor across the Dastgah-e Nava Corpus.

Sources:
- Fretted Setar / Tar: Hossein Alizadeh, Dariush Talai, Ahmad Ebadi
- Fretless Oud: Mansour Nariman
- Fretless Kamancheh: Aliakbar Shekarchi
- Fretless Vocal: Mahmud Karimi
"""
from __future__ import annotations

import os
import statistics
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_upgraded_strikes import (  # noqa: E402
    OUT, YM, ensure_dylib, extract_single_wav, save_npz_pure,
)

NAVA_SOURCES = [
    # --- Fretted Setar & Tar ---
    dict(name="alizadeh_setar", dirs=[YM / "Hossein Alizadeh" / "Radif Navazi - Nava"], fmin=180.0, fmax=680.0, drone=0.0, inst="setar", fretless=False),
    dict(name="talai_tar", dirs=[YM / "Dariush Talai" / "Radif Nava"], fmin=190.0, fmax=700.0, drone=0.0, inst="tar", fretless=False),
    dict(name="ebadi_setar", dirs=[YM / "Ahmad Ebadi" / "Setar Solo - Nava"], fmin=180.0, fmax=640.0, drone=0.0, inst="setar", fretless=False),
    # --- Fretless Oud ---
    dict(name="nariman_oud", dirs=[YM / "Mansour Nariman" / "Radif Oud - Nava"], fmin=125.0, fmax=500.0, drone=0.0, inst="oud", fretless=True),
    # --- Fretless Kamancheh ---
    dict(name="shekarchi_kamancheh", dirs=[YM / "Aliakbar Shekarchi" / "Radif Kamancheh - Nava"], fmin=230.0, fmax=850.0, drone=0.0, inst="kamancheh", fretless=True),
    # --- Fretless Vocal ---
    dict(name="karimi_vocal", dirs=[YM / "Mahmud Karimi" / "Vocal Radif - Nava"], fmin=115.0, fmax=460.0, drone=0.0, max_wobble=20.0, min_conf=46.0, inst="voice", fretless=True),
]


def main() -> None:
    t0 = time.time()
    ensure_dylib()
    tasks = []
    for s in NAVA_SOURCES:
        wavs = []
        for d in s["dirs"]:
            wavs.extend(sorted(d.glob("*.wav")))
        assert wavs, f"No wavs for {s['name']}"
        s["n_tracks"] = len(wavs)
        for w in wavs:
            tasks.append((s["name"], str(w), w.stem, s["fmin"], s["fmax"], s["drone"], s.get("max_wobble", 18.0), s.get("min_conf", 48.0)))

    print(f"Extracting {len(tasks)} tracks across {len(NAVA_SOURCES)} Nava sources...", flush=True)

    res: dict[str, list[dict]] = {s["name"]: [] for s in NAVA_SOURCES}
    done = 0
    with ProcessPoolExecutor(max_workers=min(8, os.cpu_count() or 4)) as ex:
        futs = {ex.submit(extract_single_wav, w, lab, fmin, fmax, dr, mw, mc, None): (alb, lab)
                for alb, w, lab, fmin, fmax, dr, mw, mc in tasks}
        for f in as_completed(futs):
            alb, lab = futs[f]
            res[alb].append(f.result())
            done += 1
            if done % 3 == 0 or done == len(tasks):
                print(f"  [{done:2d}/{len(tasks)}] {time.time()-t0:4.0f}s {alb} / {lab}", flush=True)

    for s in NAVA_SOURCES:
        rows = sorted(res[s["name"]], key=lambda r: r["track"])
        A = {k: [] for k in ("f", "t", "track", "method", "conf", "wobble_plat_c", "wobble_sus_c", "drift_c_per_s", "attack_bend_c")}
        for r in rows:
            n = len(r["f"])
            A["f"] += r["f"]; A["t"] += r["t"]; A["track"] += [r["track"]] * n; A["method"] += r["method"]
            A["conf"] += r["conf"]; A["wobble_plat_c"] += r["wobble_plat_c"]; A["wobble_sus_c"] += r["wobble_sus_c"]
            A["drift_c_per_s"] += r["drift_c_per_s"]; A["attack_bend_c"] += r["attack_bend_c"]
        p = OUT / f"strikes_nava_{s['name']}.npz"
        save_npz_pure(p, A)
        med_c = statistics.median(A["conf"]) if A["conf"] else 0.0
        n_tr = len(set(A["track"]))
        print(f"[saved] {p.name:<30} tracks={n_tr:2d} strikes={len(A['f']):5d} med_conf={med_c:.1f} (fretless={s['fretless']})")

    print(f"All Nava extraction completed in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()