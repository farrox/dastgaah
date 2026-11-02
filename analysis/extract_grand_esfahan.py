#!/usr/bin/env python3
"""Run v3 4-stage strike extractor across the Grand 18-Master Bayat-e Esfahan Corpus.

Sources:
1. Nur-Ali Borumand (Tar & Setar)
2. Morteza Neydavud (Tar)
3. Ali-Akbar Shahnazi (Tar)
4. Yusef Forutan (Setar)
5. Ahmad Ebadi (Setar)
6. Abolhasan Saba (Setar / Violin)
7. Dariush Talai (Tar / Setar)
8. Mohammad Reza Lotfi (Setar & Tar)
9. Hossein Alizadeh (Setar)
10. Hassan Kasaei (Ney / Setar)
11. Mansour Nariman (Oud)
12. Aliakbar Shekarchi (Kamancheh)
13. Ali-Asghar Bahari (Kamancheh)
14. Mahmud Karimi (Voice)
15. Jalil Shahnaz (Tar)
16. Gholamhosein Bigjekhani (Tar)
17. Mehdi Kamalian (Setar)
18. Saeed Hormozi (Setar)
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

GRAND_ESFAHAN_SOURCES = [
    # --- Qajar / Early Radif Masters ---
    dict(name="borumand_tar_setar", dirs=[
        YM / "Nur-Ali Borumand" / "Radif Tar Setar - Esfahan",
        YM / "Nur-Ali Borumand" / "Radif Tar Setar - Homayun",
    ], fmin=190.0, fmax=680.0, drone=0.0, inst="tar_setar", fretless=False),

    dict(name="neydavud_tar", dirs=[YM / "Morteza Neydavud" / "Radif Tar - Esfahan"], fmin=190.0, fmax=720.0, drone=0.0, inst="tar", fretless=False),

    dict(name="shahnazi_tar", dirs=[
        YM / "Ali-Akbar Shahnazi" / "Radif Tar - Esfahan",
        YM / "Ali-Akbar Shahnazi" / "The Advanced Shahnazi Radif III",
    ], file_filter=["Esfahan", "Homayun"], fmin=190.0, fmax=720.0, drone=0.0, inst="tar", fretless=False),

    dict(name="forutan_setar", dirs=[YM / "Yusef Forutan" / "Radif Setar - Esfahan"], fmin=180.0, fmax=660.0, drone=0.0, inst="setar", fretless=False),
    dict(name="ebadi_setar", dirs=[YM / "Ahmad Ebadi" / "Setar Solo - Esfahan"], fmin=180.0, fmax=660.0, drone=0.0, inst="setar", fretless=False),
    dict(name="saba_radif", dirs=[YM / "Abolhasan Saba" / "Radif - Esfahan"], fmin=190.0, fmax=750.0, drone=0.0, inst="setar", fretless=False),
    dict(name="talai_tar", dirs=[YM / "Dariush Talai" / "Radif - Esfahan"], fmin=190.0, fmax=720.0, drone=0.0, inst="tar", fretless=False),
    dict(name="lotfi_solo", dirs=[YM / "Mohammad Reza Lotfi" / "Solo - Esfahan"], fmin=180.0, fmax=700.0, drone=0.0, inst="tar_setar", fretless=False),
    dict(name="alizadeh_setar", dirs=[YM / "Hossein Alizadeh" / "Radif Navazi - Esfahan"], fmin=180.0, fmax=680.0, drone=0.0, inst="setar", fretless=False),
    dict(name="kasaei_solo", dirs=[YM / "Hassan Kasaei" / "Solo - Esfahan"], fmin=175.0, fmax=720.0, drone=0.0, inst="ney_setar", fretless=False),

    # --- Additional Tar & Setar Masters ---
    dict(name="shahnaz_tar", dirs=[YM / "Jalil Shahnaz" / "Tar Solo - Esfahan"], fmin=190.0, fmax=750.0, drone=0.0, inst="tar", fretless=False),
    dict(name="bigjekhani_tar", dirs=[YM / "Gholamhosein Bigjekhani" / "Tar - Esfahan"], fmin=190.0, fmax=720.0, drone=0.0, inst="tar", fretless=False),
    dict(name="kamalian_setar", dirs=[YM / "Mehdi Kamalian" / "Setar - Esfahan"], fmin=180.0, fmax=660.0, drone=0.0, inst="setar", fretless=False),
    dict(name="hormozi_setar", dirs=[YM / "Saeed Hormozi" / "Setar - Esfahan"], fmin=180.0, fmax=660.0, drone=0.0, inst="setar", fretless=False),

    # --- Fretless Masters (Oud, Kamancheh, Vocal) ---
    dict(name="nariman_oud", dirs=[YM / "Mansour Nariman" / "Radif Oud - Esfahan"], fmin=125.0, fmax=520.0, drone=0.0, inst="oud", fretless=True),
    dict(name="shekarchi_kamancheh", dirs=[YM / "Aliakbar Shekarchi" / "Radif Kamancheh - Esfahan"], fmin=230.0, fmax=850.0, drone=0.0, inst="kamancheh", fretless=True),
    dict(name="bahari_kamancheh", dirs=[YM / "Ali-Asghar Bahari" / "Kamancheh - Esfahan"], fmin=220.0, fmax=850.0, drone=0.0, inst="kamancheh", fretless=True),
    dict(name="karimi_vocal", dirs=[YM / "Mahmud Karimi" / "Vocal Radif - Esfahan"], fmin=115.0, fmax=480.0, drone=0.0, max_wobble=20.0, min_conf=46.0, inst="voice", fretless=True),
]


def main() -> None:
    t0 = time.time()
    ensure_dylib()
    tasks = []
    for s in GRAND_ESFAHAN_SOURCES:
        wavs = []
        filts = s.get("file_filter")
        if filts and isinstance(filts, str):
            filts = [filts]
        for d in s["dirs"]:
            for f in sorted(d.glob("*.wav")):
                if filts and not any(filt.lower() in f.name.lower() for filt in filts):
                    continue
                wavs.append(f)
        assert wavs, f"No wavs for {s['name']}"
        s["n_tracks"] = len(wavs)
        for w in wavs:
            tasks.append((s["name"], str(w), w.stem, s["fmin"], s["fmax"], s["drone"], s.get("max_wobble", 18.0), s.get("min_conf", 48.0)))

    print(f"Extracting {len(tasks)} tracks across {len(GRAND_ESFAHAN_SOURCES)} Grand Esfahan sources...", flush=True)

    res: dict[str, list[dict]] = {s["name"]: [] for s in GRAND_ESFAHAN_SOURCES}
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
    for s in GRAND_ESFAHAN_SOURCES:
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

    print(f"\nAll 18 Grand Esfahan masters extracted in {time.time()-t0:.1f}s: {tot_all:,} strikes across {len(tasks)} tracks.")


if __name__ == "__main__":
    main()

