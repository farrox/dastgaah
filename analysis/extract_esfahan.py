#!/usr/bin/env python3
"""Run v3 4-stage strike extractor across the Bayat-e Esfahan Corpus.

Sources:
- Tar Masters:
  * Morteza Neydavud (Radif Tar - Esfahan, 3 tracks)
  * Ali-Akbar Shahnazi (The Advanced Shahnazi Radif III - Homayun / Esfahan, 17 tracks)
  * Jalil Shahnaz (Tar Solo - Esfahan, 3 tracks)
  * Gholamhosein Bigjekhani (Tar - Esfahan, 2 tracks)
- Setar Masters:
  * Ahmad Ebadi (Setar Solo - Esfahan, 1 track)
  * Mehdi Kamalian (Setar - Esfahan, 1 track)
  * Saeed Hormozi (Setar - Esfahan, 1 track)
- Fretless Kamancheh:
  * Ali-Asghar Bahari (Kamancheh - Esfahan, 1 track)
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

ESFAHAN_SOURCES = [
    # --- Tar Masters ---
    dict(name="neydavud_tar", dirs=[YM / "Morteza Neydavud" / "Radif Tar - Esfahan"], fmin=190.0, fmax=720.0, drone=0.0, inst="tar", fretless=False),
    dict(name="shahnazi_tar", dirs=[YM / "Ali-Akbar Shahnazi" / "The Advanced Shahnazi Radif III"], file_filter="Homayun", fmin=190.0, fmax=720.0, drone=0.0, inst="tar", fretless=False),
    dict(name="shahnaz_tar", dirs=[YM / "Jalil Shahnaz" / "Tar Solo - Esfahan"], fmin=190.0, fmax=750.0, drone=0.0, inst="tar", fretless=False),
    dict(name="bigjekhani_tar", dirs=[YM / "Gholamhosein Bigjekhani" / "Tar - Esfahan"], fmin=190.0, fmax=720.0, drone=0.0, inst="tar", fretless=False),

    # --- Setar Masters ---
    dict(name="ebadi_setar", dirs=[YM / "Ahmad Ebadi" / "Setar Solo - Esfahan"], fmin=180.0, fmax=660.0, drone=0.0, inst="setar", fretless=False),
    dict(name="kamalian_setar", dirs=[YM / "Mehdi Kamalian" / "Setar - Esfahan"], fmin=180.0, fmax=660.0, drone=0.0, inst="setar", fretless=False),
    dict(name="hormozi_setar", dirs=[YM / "Saeed Hormozi" / "Setar - Esfahan"], fmin=180.0, fmax=660.0, drone=0.0, inst="setar", fretless=False),

    # --- Fretless Kamancheh Master ---
    dict(name="bahari_kamancheh", dirs=[YM / "Ali-Asghar Bahari" / "Kamancheh - Esfahan"], fmin=220.0, fmax=850.0, drone=0.0, inst="kamancheh", fretless=True),
]


def main() -> None:
    t0 = time.time()
    ensure_dylib()
    tasks = []
    for s in ESFAHAN_SOURCES:
        wavs = []
        filt = s.get("file_filter")
        for d in s["dirs"]:
            for f in sorted(d.glob("*.wav")):
                if filt and filt.lower() not in f.name.lower():
                    continue
                wavs.append(f)
        assert wavs, f"No wavs for {s['name']}"
        s["n_tracks"] = len(wavs)
        for w in wavs:
            tasks.append((s["name"], str(w), w.stem, s["fmin"], s["fmax"], s["drone"], s.get("max_wobble", 18.0), s.get("min_conf", 48.0)))

    print(f"Extracting {len(tasks)} tracks across {len(ESFAHAN_SOURCES)} Bayat-e Esfahan sources...", flush=True)

    res: dict[str, list[dict]] = {s["name"]: [] for s in ESFAHAN_SOURCES}
    done = 0
    with ProcessPoolExecutor(max_workers=min(8, os.cpu_count() or 4)) as ex:
        futs = {
            ex.submit(extract_single_wav, w, stem, fmin, fmax, dr, mw, mc): (src, stem)
            for (src, w, stem, fmin, fmax, dr, mw, mc) in tasks
        }
        for fut in as_completed(futs):
            src, stem = futs[fut]
            try:
                strikes = fut.result()
                res[src].append(strikes)
                done += 1
                n_str = len(strikes["f"]) if isinstance(strikes, dict) and "f" in strikes else len(strikes)
                print(f"[{done:2d}/{len(tasks)}] {src:<20} {stem[:35]:<35} -> {n_str:4d} strikes", flush=True)
            except Exception as e:
                print(f"FAILED {src} {stem}: {e}", file=sys.stderr)

    print(f"\n--- Saving strikes per artist ---")
    tot_all = 0
    for s in ESFAHAN_SOURCES:
        rows = sorted(res[s["name"]], key=lambda r: r["track"])
        A = {k: [] for k in ("f", "t", "track", "method", "conf", "wobble_plat_c", "wobble_sus_c", "drift_c_per_s", "attack_bend_c")}
        for r in rows:
            n = len(r["f"])
            A["f"] += r["f"]
            A["t"] += r["t"]
            A["track"] += [r["track"]] * n
            A["method"] += r["method"]
            A["conf"] += r["conf"]
            A["wobble_plat_c"] += r["wobble_plat_c"]
            A["wobble_sus_c"] += r["wobble_sus_c"]
            A["drift_c_per_s"] += r["drift_c_per_s"]
            A["attack_bend_c"] += r["attack_bend_c"]
        kinds = {k: ("U" if k in ("track", "method") else "f8") for k in A}
        p = OUT / f"strikes_esfahan_{s['name']}.npz"
        save_npz_pure(p, {k: (A[k], kinds[k]) for k in A})
        mc = statistics.median(A["conf"]) if A["conf"] else 0
        tot_all += len(A["f"])
        print(f"[saved] {p.name:36s} tracks={len(rows):2d} strikes={len(A['f']):5d} med_conf={mc:.1f} (fretless={s['fretless']})", flush=True)

    print(f"\nAll Esfahan extraction completed in {time.time()-t0:.1f}s: {tot_all:,} strikes across {len(tasks)} tracks.")


if __name__ == "__main__":
    main()
