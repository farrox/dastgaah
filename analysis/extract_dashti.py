#!/usr/bin/env python3
"""Run v3 4-stage strike extractor across the Expanded Avaz-e Dashti Corpus.

Sources:
- Fretless Oud / Barbat: Mansour Nariman, Hossein Behroozinia
- Fretless Kamancheh: Aliakbar Shekarchi, Saeed Farajpouri, Kayhan Kalhor
- Vocal: Mahmud Karimi
- Fretted Setar / Tar: Hossein Alizadeh, Hassan Kasaei, Ahmad Ebadi, Abolhasan Saba, Mohammad Reza Lotfi, Ali-Akbar Shahnazi
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

DASHTI_SOURCES = [
    # --- Fretless Oud / Barbat ---
    dict(name="nariman_oud", dirs=[YM / "Mansour Nariman" / "Radif Oud - Dashti"], fmin=125.0, fmax=500.0, drone=0.0, inst="oud", fretless=True),
    dict(name="behroozinia_barbat", dirs=[YM / "Hossein Behroozinia" / "Koohestan - Dashti Solo"], fmin=125.0, fmax=520.0, drone=0.0, inst="barbat", fretless=True),
    # --- Fretless Kamancheh ---
    dict(name="shekarchi_kamancheh", dirs=[YM / "Aliakbar Shekarchi" / "Radif Kamancheh - Dashti"], fmin=230.0, fmax=850.0, drone=0.0, inst="kamancheh", fretless=True),
    dict(name="farajpouri_kamancheh", dirs=[YM / "Saeed Farajpouri" / "Rooz va Shab - Dashti"], fmin=230.0, fmax=850.0, drone=0.0, inst="kamancheh", fretless=True),
    dict(name="kalhor_kamancheh", dirs=[YM / "Kayhan Kalhor" / "Dashti Solo"], fmin=220.0, fmax=850.0, drone=0.0, inst="kamancheh", fretless=True),
    # --- Vocal ---
    dict(name="karimi_vocal", dirs=[YM / "Mahmud Karimi" / "Vocal Radif - Dashti"], fmin=115.0, fmax=460.0, drone=0.0, max_wobble=20.0, min_conf=46.0, inst="voice", fretless=True),
    # --- Fretted Setar & Tar ---
    dict(name="alizadeh_setar", dirs=[YM / "Hossein Alizadeh" / "Radif Navazi - Dashti"], fmin=180.0, fmax=680.0, drone=0.0, inst="setar", fretless=False),
    dict(name="kasaei_setar", dirs=[YM / "Hassan Kasaei" / "Radifs 4 - Dashti"], fmin=175.0, fmax=740.0, drone=0.0, inst="setar", fretless=False),
    dict(name="ebadi_setar", dirs=[YM / "Ahmad Ebadi" / "Setar Solo - Dashti"], fmin=190.0, fmax=640.0, drone=0.0, inst="setar", fretless=False),
    dict(name="saba_setar", dirs=[YM / "Abolhasan Saba" / "Dashti Solo"], fmin=190.0, fmax=660.0, drone=0.0, inst="setar", fretless=False),
    dict(name="lotfi_setar", dirs=[YM / "Mohammad Reza Lotfi" / "Dashti Solo"], fmin=175.0, fmax=660.0, drone=0.0, inst="setar", fretless=False),
    dict(name="shahnazi_tar", dirs=[YM / "Ali-Akbar Shahnazi" / "Radif Tar - Dashti"], fmin=195.0, fmax=710.0, drone=0.0, inst="tar", fretless=False),
]


def main() -> None:
    t0 = time.time()
    ensure_dylib()
    tasks = []
    for s in DASHTI_SOURCES:
        wavs = []
        for d in s["dirs"]:
            wavs += sorted(d.glob("*.wav"))
        assert wavs, f"No wavs for {s['name']}"
        s["n_tracks"] = len(wavs)
        for w in wavs:
            tasks.append((s["name"], str(w), w.stem, s["fmin"], s["fmax"], s["drone"], s.get("max_wobble", 18.0), s.get("min_conf", 48.0)))
    print(f"Extracting {len(tasks)} tracks across {len(DASHTI_SOURCES)} Dashti sources...", flush=True)

    res: dict[str, list[dict]] = {s["name"]: [] for s in DASHTI_SOURCES}
    done = 0
    with ProcessPoolExecutor(max_workers=min(8, os.cpu_count() or 4)) as ex:
        futs = {ex.submit(extract_single_wav, w, lab, fmin, fmax, dr, mw, mc, None): (alb, lab)
                for alb, w, lab, fmin, fmax, dr, mw, mc in tasks}
        for f in as_completed(futs):
            alb, lab = futs[f]
            res[alb].append(f.result())
            done += 1
            if done % 10 == 0 or done == len(tasks):
                print(f"  [{done:2d}/{len(tasks)}] {time.time()-t0:4.0f}s {alb} / {lab}", flush=True)

    for s in DASHTI_SOURCES:
        rows = sorted(res[s["name"]], key=lambda r: r["track"])
        A = {k: [] for k in ("f", "t", "track", "method", "conf", "wobble_plat_c", "wobble_sus_c", "drift_c_per_s", "attack_bend_c")}
        for r in rows:
            n = len(r["f"])
            A["f"] += r["f"]; A["t"] += r["t"]; A["track"] += [r["track"]] * n; A["method"] += r["method"]
            A["conf"] += r["conf"]; A["wobble_plat_c"] += r["wobble_plat_c"]; A["wobble_sus_c"] += r["wobble_sus_c"]
            A["drift_c_per_s"] += r["drift_c_per_s"]; A["attack_bend_c"] += r["attack_bend_c"]
        kinds = {k: ("U" if k in ("track", "method") else "f8") for k in A}
        p = OUT / f"strikes_dashti_{s['name']}.npz"
        save_npz_pure(p, {k: (A[k], kinds[k]) for k in A})
        mc = statistics.median(A["conf"]) if A["conf"] else 0
        print(f"[saved] {p.name:36s} tracks={len(rows):2d} strikes={len(A['f']):5d} med_conf={mc:.1f} (fretless={s['fretless']})", flush=True)
    print(f"All Dashti extraction completed in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()

