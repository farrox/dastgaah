#!/usr/bin/env python3
"""Run v3 4-stage strike extractor across the Grand 20-Master Dastgah-e Homayun Corpus.

Sources:
1. Nur-Ali Borumand (Tar/Setar, Mirza Abdollah Radif)
2. Ali-Akbar Shahnazi (Tar, Advanced Radif & Mirza Hosseingholi Radif)
3. Hossein Alizadeh (Setar, Radif Navazi & Homayun Concert)
4. Morteza Neydavud (Tar, Radif-e Kamelo)
5. Yusef Forutan (Setar, Radif on Setar II)
6. Saeed Hormozi (Setar Solo)
7. Ahmad Ebadi (Setar Solo)
8. Mohammad-Reza Lotfi (Setar & Tar Recitals)
9. Jalil Shahnaz (Tar Solo)
10. Dariush Tala'i (Tar, Mirza Abdollah Radif)
11. Parviz Meshkatian & Shajarian / Aref Ensemble (Santur / Ensemble, Bidad 1985)
12. Bagher Khan (1905 Historical Qajar Kamancheh)
13. Ali-Asghar Bahari (Kamancheh Solo)
14. Aliakbar Shekarchi (Kamancheh, Mirza Abdollah Radif)
15. Mansour Nariman (Oud, Radif-e Barbat)
16. Hassan Kasaei (Ney Solo)
17. Ali Shirkhodaee (Clarinet Solo)
18. Mahmud Karimi (Voice, Vocal Radif)
"""
from __future__ import annotations

import os
import statistics
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_upgraded_strikes import (  # noqa: E402
    OUT, YM, ensure_dylib, extract_single_wav, save_npz_pure,
)

GRAND_HOMAYUN_SOURCES = [
    # --- Qajar / Early Radif Masters ---
    dict(name="borumand_tar_setar", dirs=[
        YM / "Nur-Ali Borumand" / "Radif Tar Setar - Homayun",
    ], fmin=190.0, fmax=680.0, drone=0.0, inst="tar_setar", fretless=False),

    dict(name="neydavud_tar", dirs=[
        YM / "Morteza Neydavud" / "Radif Tar - Homayun",
    ], fmin=190.0, fmax=720.0, drone=0.0, inst="tar", fretless=False),

    dict(name="shahnazi_tar", dirs=[
        YM / "Ali-Akbar Shahnazi" / "Radif Tar - Homayun",
        YM / "Ali-Akbar Shahnazi" / "The Advanced Shahnazi Radif III",
    ], file_filter=["Homayun", "Homayoun"], fmin=190.0, fmax=720.0, drone=0.0, inst="tar", fretless=False),

    dict(name="forutan_setar", dirs=[
        YM / "Yusef Forutan" / "Radif Setar - Homayun",
    ], fmin=180.0, fmax=660.0, drone=0.0, inst="setar", fretless=False),

    dict(name="hormozi_setar", dirs=[
        YM / "Saeed Hormozi" / "Setar - Homayun",
    ], fmin=180.0, fmax=660.0, drone=0.0, inst="setar", fretless=False),

    dict(name="ebadi_setar", dirs=[
        YM / "Ahmad Ebadi" / "Setar Solo - Homayun",
    ], fmin=180.0, fmax=660.0, drone=0.0, inst="setar", fretless=False),

    # --- Modern Classical Setar & Tar Virtuosos ---
    dict(name="talai_tar", dirs=[
        YM / "Dariush Talai" / "Radif - Homayun",
    ], fmin=190.0, fmax=720.0, drone=0.0, inst="tar", fretless=False),

    dict(name="alizadeh_setar", dirs=[
        YM / "Hossein Alizadeh" / "Radif Navazi - Setar_ Homayun",
        YM / "Hossein Alizadeh" / "Homayun Concert",
    ], fmin=180.0, fmax=680.0, drone=0.0, inst="setar", fretless=False),

    dict(name="lotfi_tar_setar", dirs=[
        YM / "Mohammad Reza Lotfi" / "Setar Solo - Homayun",
        YM / "Mohammad Reza Lotfi" / "Tar Solo - Homayun",
    ], fmin=180.0, fmax=700.0, drone=0.0, inst="tar_setar", fretless=False),

    dict(name="shahnaz_tar", dirs=[
        YM / "Jalil Shahnaz" / "Tar Solo - Homayun",
    ], fmin=190.0, fmax=750.0, drone=0.0, inst="tar", fretless=False),

    dict(name="meshkatian_santur_ensemble", dirs=[
        YM / "Parviz Meshkatian & Shajarian" / "Bidad - Homayun",
    ], fmin=180.0, fmax=850.0, drone=0.0, inst="santur_ensemble", fretless=False),

    # --- Historical & Fretless Masters ---
    dict(name="bagher_khan_kamancheh", dirs=[
        YM / "Bagher Khan" / "Qajar Kamancheh - Homayun",
    ], fmin=180.0, fmax=850.0, drone=0.0, inst="kamancheh", fretless=True),

    dict(name="bahari_kamancheh", dirs=[
        YM / "Ali-Asghar Bahari" / "Kamancheh - Homayun",
    ], fmin=220.0, fmax=850.0, drone=0.0, inst="kamancheh", fretless=True),

    dict(name="shekarchi_kamancheh", dirs=[
        YM / "Aliakbar Shekarchi" / "Radif Kamancheh - Homayun",
    ], fmin=230.0, fmax=850.0, drone=0.0, inst="kamancheh", fretless=True),

    dict(name="nariman_oud", dirs=[
        YM / "Mansour Nariman" / "Radif Oud - Homayun",
    ], fmin=125.0, fmax=520.0, drone=0.0, inst="oud", fretless=True),

    dict(name="kasaei_ney", dirs=[
        YM / "Hassan Kasaei" / "Ney Solo - Homayun",
    ], fmin=175.0, fmax=750.0, drone=0.0, inst="ney", fretless=True),

    dict(name="shirkhodaee_clarinet", dirs=[
        YM / "Ali Shirkhodaee" / "Clarinet - Homayun",
    ], fmin=150.0, fmax=800.0, drone=0.0, inst="clarinet", fretless=True),

    dict(name="karimi_vocal", dirs=[
        YM / "Mahmud Karimi" / "Vocal Radif - Homayun",
    ], fmin=115.0, fmax=480.0, drone=0.0, max_wobble=20.0, min_conf=46.0, inst="vocal", fretless=True),
]


def process_audio_file(item: tuple) -> dict:
    src_name, audio_path_str, track_stem, fmin, fmax, drone, max_wobble, min_conf = item
    audio_path = Path(audio_path_str)

    # If already a .wav file, extract directly
    if audio_path.suffix.lower() == ".wav":
        res = extract_single_wav(
            str(audio_path),
            track_stem,
            fmin,
            fmax,
            drone_freq=drone,
            max_wobble_plat_c=max_wobble,
            min_conf=min_conf,
            max_sec=None,
        )
        return {"src": src_name, "track": track_stem, "res": res}

    # Otherwise (m4a, mp4), transcode to temporary 44.1kHz mono wav via ffmpeg
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_wav = tmp.name

    try:
        cmd = [
            "/opt/homebrew/bin/ffmpeg",
            "-y",
            "-loglevel", "error",
            "-i", str(audio_path),
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "44100",
            "-ac", "1",
            tmp_wav,
        ]
        subprocess.run(cmd, check=True)
        res = extract_single_wav(
            tmp_wav,
            track_stem,
            fmin,
            fmax,
            drone_freq=drone,
            max_wobble_plat_c=max_wobble,
            min_conf=min_conf,
            max_sec=None,
        )
    finally:
        if os.path.exists(tmp_wav):
            try:
                os.remove(tmp_wav)
            except Exception:
                pass

    return {"src": src_name, "track": track_stem, "res": res}


def main():
    t0 = time.time()
    ensure_dylib()
    tasks = []
    seen = set()

    for s in GRAND_HOMAYUN_SOURCES:
        filts = s.get("file_filter")
        if filts and isinstance(filts, str):
            filts = [filts]

        for d in s["dirs"]:
            if not d.exists():
                continue
            candidates = sorted(list(d.glob("*.wav")) + list(d.glob("*.m4a")) + list(d.glob("*.mp4")))
            for f in candidates:
                # de-duplicate stems (e.g. if both .wav and .m4a exist in folder)
                key = (s["name"], f.stem)
                if key in seen:
                    continue
                if filts and not any(filt.lower() in f.name.lower() for filt in filts):
                    continue
                seen.add(key)
                tasks.append((
                    s["name"],
                    str(f),
                    f.stem,
                    s["fmin"],
                    s["fmax"],
                    s["drone"],
                    s.get("max_wobble", 18.0),
                    s.get("min_conf", 48.0),
                ))

    print(f"Extracting {len(tasks)} tracks across {len(GRAND_HOMAYUN_SOURCES)} Grand Homayun sources...", flush=True)

    res_by_src: dict[str, list[dict]] = {s["name"]: [] for s in GRAND_HOMAYUN_SOURCES}
    done = 0
    # Run across 8 workers
    with ProcessPoolExecutor(max_workers=min(8, os.cpu_count() or 4)) as ex:
        futs = {ex.submit(process_audio_file, t): (t[0], t[2]) for t in tasks}
        for fut in as_completed(futs):
            src, stem = futs[fut]
            try:
                out = fut.result()
                res_by_src[src].append(out["res"])
                done += 1
                n_str = len(out["res"]["f"]) if out["res"] and "f" in out["res"] else 0
                print(f"[{done:3d}/{len(tasks):3d}] {src:<25s} {stem[:35]:<35s} -> {n_str:4d} strikes", flush=True)
            except Exception as e:
                print(f"FAILED {src} {stem}: {e}", file=sys.stderr)

    print(f"\n--- Saving strike NPZ caches per master ---")
    tot_all = 0
    for s in GRAND_HOMAYUN_SOURCES:
        sname = s["name"]
        rows = sorted(res_by_src[sname], key=lambda r: r["track"])
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
        p = OUT / f"strikes_homayun_{sname}.npz"
        save_npz_pure(p, {k: (A[k], kinds[k]) for k in A})
        mc = statistics.median(A["conf"]) if A["conf"] else 0
        tot_all += len(A["f"])
        print(f"[saved] {p.name:36s} tracks={len(rows):2d} strikes={len(A['f']):5d} med_conf={mc:.1f} (fretless={s['fretless']})", flush=True)

    dt = time.time() - t0
    print(f"\nAll {len(GRAND_HOMAYUN_SOURCES)} Grand Homayun masters extracted in {dt:.1f}s: {tot_all:,} strikes across {len(tasks)} tracks.")


if __name__ == "__main__":
    main()
