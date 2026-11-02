#!/usr/bin/env python3
"""Run the v3 4-stage extractor on the Dastgah-e Chahargah corpus.

Writes analysis/strikes_chahargah_<source>.npz (same schema as strikes_<source>.npz).
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


def ch(p: Path) -> bool:
    return "chahargah" in p.name.lower()


def kasaei_dirs():
    return sorted((YM / "Hassan Kasaei").glob("Iranian Classical Music Radifs [45]*"))


SOURCES = [
    dict(name="nariman", dirs=[YM / "Mansour Nariman" / "Iranian Music Radif for Oud _ Dastgahe Chahargah"], fmin=125.0, fmax=480.0, drone=0.0),
    dict(name="alizadeh", dirs=[YM / "Hossein Alizadeh" / "Radif Navazi - Setar_ Chahargah"], fmin=180.0, fmax=680.0, drone=220.8),
    dict(name="shekarchi", dirs=[YM / "Aliakbar Shekarchi" / "Radif Of Persian Classical Music _ Dastgahe Chahargah"], fmin=235.0, fmax=850.0, drone=0.0),
    dict(name="borumand", dirs=[YM / "Nur-Ali Borumand" / "The Mirza Abdollah Radif for Tar and Setar, Vol. 5"], fmin=195.0, fmax=680.0, drone=0.0),
    dict(name="forutan", dirs=[YM / "Yusef Forutan" / "Radif of Persian Music on Setar II"], fmin=140.0, fmax=480.0, drone=0.0, filt=ch),
    dict(name="neydavud", dirs=[YM / "Morteza Neydavud" / "Radif of Persian Music on Tar, Vol. 2"], fmin=185.0, fmax=680.0, drone=0.0, filt=ch),
    dict(name="shahnazi", dirs=[YM / "Ali-Akbar Shahnazi" / "The Advanced Shahnazi Radif IV"], fmin=195.0, fmax=710.0, drone=0.0, filt=ch),
    dict(name="kasaei", dirs=kasaei_dirs(), fmin=175.0, fmax=740.0, drone=0.0, filt=ch),
    dict(name="karimi", dirs=[YM / "Mahmud Karimi" / "Avaz Course_ Vocal Radif of Persian Classical Music, Vol. 3"], fmin=115.0, fmax=460.0, drone=0.0, filt=ch, max_wobble=20.0, min_conf=46.0),
    dict(name="ebadi", dirs=[YM / "Ahmad Ebadi" / "Setar Solo - Chahargah"], fmin=190.0, fmax=640.0, drone=0.0),
    dict(name="saba", dirs=[YM / "Abolhasan Saba" / "Chahargah by Saba"], fmin=190.0, fmax=660.0, drone=0.0),
    dict(name="lotfi", dirs=[YM / "Mohammad Reza Lotfi" / "Chahargah Tar Solo", YM / "Mohammad Reza Lotfi" / "Chahargah Setar Solo"], fmin=175.0, fmax=660.0, drone=0.0),
]


def main() -> None:
    t0 = time.time()
    ensure_dylib()
    tasks = []
    for s in SOURCES:
        wavs = []
        for d in s["dirs"]:
            wavs += sorted(d.glob("*.wav"))
        if "filt" in s:
            wavs = [w for w in wavs if s["filt"](w)]
        assert wavs, f"no wavs for {s['name']}"
        s["n_tracks"] = len(wavs)
        for w in wavs:
            tasks.append((s["name"], str(w), w.stem, s["fmin"], s["fmax"], s["drone"], s.get("max_wobble", 18.0), s.get("min_conf", 48.0)))
    print(f"{len(tasks)} tracks across {len(SOURCES)} sources", flush=True)

    res: dict[str, list[dict]] = {s["name"]: [] for s in SOURCES}
    done = 0
    with ProcessPoolExecutor(max_workers=min(8, os.cpu_count() or 4)) as ex:
        futs = {ex.submit(extract_single_wav, w, lab, fmin, fmax, dr, mw, mc, None): (alb, lab)
                for alb, w, lab, fmin, fmax, dr, mw, mc in tasks}
        for f in as_completed(futs):
            alb, lab = futs[f]
            res[alb].append(f.result())
            done += 1
            if done % 20 == 0 or done == len(tasks):
                print(f"  [{done}/{len(tasks)}] {time.time()-t0:.0f}s {alb}/{lab}", flush=True)

    for s in SOURCES:
        rows = sorted(res[s["name"]], key=lambda r: r["track"])
        A = {k: [] for k in ("f", "t", "track", "method", "conf", "wobble_plat_c", "wobble_sus_c", "drift_c_per_s", "attack_bend_c")}
        for r in rows:
            n = len(r["f"])
            A["f"] += r["f"]; A["t"] += r["t"]; A["track"] += [r["track"]] * n; A["method"] += r["method"]
            A["conf"] += r["conf"]; A["wobble_plat_c"] += r["wobble_plat_c"]; A["wobble_sus_c"] += r["wobble_sus_c"]
            A["drift_c_per_s"] += r["drift_c_per_s"]; A["attack_bend_c"] += r["attack_bend_c"]
        kinds = {k: ("U" if k in ("track", "method") else "f8") for k in A}
        p = OUT / f"strikes_chahargah_{s['name']}.npz"
        save_npz_pure(p, {k: (A[k], kinds[k]) for k in A})
        mc = statistics.median(A["conf"]) if A["conf"] else 0
        print(f"[saved] {p.name:36s} tracks={len(rows):2d} strikes={len(A['f']):5d} med_conf={mc:.1f}", flush=True)
    print(f"done in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()

