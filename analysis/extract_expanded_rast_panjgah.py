#!/usr/bin/env python3
"""Run v3 4-stage native C strike extractor across the EXPANDED Grand Dastgah-e Rast-Panjgah Corpus,
now incorporating:
1. Saeed Hormozi (Setar Private Recital from Min 27)
2. Ali-Akbar Shahnazi (Complete 36-track Aqa Hoseyn-Qoli Radif Vol. 6)
3. Hossein Alizadeh (The Art of Improvisation Radio France 1993)
4. Mohammad Reza Lotfi & Shajarian (Cheshmeye Noush Concert)
5. Hassan Kasaei (Complete Radif 5 - 19 Ney Gushehs)
6. Morteza Neydavud (Complete Radif Vol. 5 - 21 Tar Gushehs)
7. Sanam Gharacheh (1927-1929 Historical Master)
8. Seyed Ahmadkhan (1907-1912 Early Shellac Master)
9. Nur-Ali Borumand (Mirza Abdollah Radif Vol. 7)
10. Mahmud Karimi (Vocal Radif Vol. 3)
11. Mansour Nariman (Oud Radif)
12. Aliakbar Shekarchi (Kamancheh Radif)
13. Ahmad Ebadi (Setar Solo 112/228)
14. Abolhasan Saba (Violin Vol. 3)
15. Jalil Shahnaz (Tar Solo)
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

EXPANDED_RP_SOURCES = [
    # 1. Saeed Hormozi
    dict(name="hormozi_setar", dirs=[
        YM / "Saeed Hormozi" / "Setar - Rast Panjgah",
    ], fmin=110.0, fmax=550.0, drone=0.0, inst="setar", fretless=False, max_wobble=22.0, min_conf=42.0),

    # 2. Ali-Akbar Shahnazi Complete Vol 6
    dict(name="shahnazi_tar_complete", dirs=[
        YM / "Ali-Akbar Shahnazi" / "The Aqa Hoseyn-Qoli Radif, Vol. 6 - Rast-Panjgah",
        YM / "Ali-Akbar Shahnazi" / "Radif Tar - Rast-Panjgah",
    ], fmin=180.0, fmax=720.0, drone=0.0, inst="tar", fretless=False, max_wobble=22.0, min_conf=45.0),

    # 3. Hossein Alizadeh (Art of Improvisation + Radif Navazi)
    dict(name="alizadeh_tar_setar", dirs=[
        YM / "Hossein Alizadeh" / "The Art Of Improvisation - Rast-Panjgah",
        YM / "Hossein Alizadeh" / "Radif Navazi - Rast-Panjgah",
    ], fmin=180.0, fmax=720.0, drone=0.0, inst="tar_setar", fretless=False, max_wobble=20.0, min_conf=48.0),

    # 4. Mohammad Reza Lotfi & Shajarian (Cheshmeye Noush)
    dict(name="lotfi_shajarian", dirs=[
        YM / "Mohammad Reza Lotfi & Shajarian" / "Cheshmeye Noush - Rast Panjgah",
        YM / "Mohammad Reza Lotfi" / "Tar - Rast-Panjgah",
    ], fmin=140.0, fmax=650.0, drone=0.0, inst="tar_voice", fretless=False, max_wobble=25.0, min_conf=45.0),

    # 5. Hassan Kasaei Complete Radif 5
    dict(name="kasaei_ney_complete", dirs=[
        YM / "Hassan Kasaei" / "Iranian Classical Music Radifs 5 - Rast Panjgah",
        YM / "Hassan Kasaei" / "Ney - Rast-Panjgah",
    ], fmin=180.0, fmax=750.0, drone=0.0, inst="ney", fretless=True, max_wobble=30.0, min_conf=40.0),

    # 6. Morteza Neydavud Complete Vol 5
    dict(name="neydavud_tar_complete", dirs=[
        YM / "Morteza Neydavud" / "Radif on Tar Vol 5 - Rast-Panjgah",
        YM / "Morteza Neydavud" / "Radif Tar - Rast-Panjgah",
    ], fmin=180.0, fmax=720.0, drone=0.0, inst="tar", fretless=False, max_wobble=25.0, min_conf=42.0),

    # 7. Historical Masters: Sanam Gharacheh (1927-1929)
    dict(name="sanam_gharacheh_1927", dirs=[
        YM / "Historical Masters" / "1927-1929 Sanam Gharacheh - Rast Panjgah",
    ], fmin=140.0, fmax=650.0, drone=0.0, inst="historical", fretless=True, max_wobble=35.0, min_conf=38.0),

    # 8. Early Masters: Seyed Ahmadkhan (1907-1912 Shellac)
    dict(name="seyed_ahmadkhan_1907", dirs=[
        YM / "Historical Masters" / "1907-1912 Seyed Ahmadkhan - Rast Panjgah",
    ], fmin=140.0, fmax=600.0, drone=0.0, inst="historical_shellac", fretless=True, max_wobble=35.0, min_conf=38.0),

    # 9. Nur-Ali Borumand
    dict(name="borumand_tar_setar", dirs=[
        YM / "Nur-Ali Borumand" / "Radif Mirza Abdollah - Rast-Panjgah",
    ], fmin=110.0, fmax=600.0, drone=0.0, inst="tar_setar", fretless=False, max_wobble=22.0, min_conf=45.0),

    # 10. Mahmud Karimi
    dict(name="karimi_vocal", dirs=[
        YM / "Mahmud Karimi" / "Vocal Radif - Rast-Panjgah",
        YM / "Mahmud Karimi" / "Avaz Course_ Vocal Radif of Persian Classical Music, Vol. 3",
    ], fmin=140.0, fmax=550.0, drone=0.0, inst="voice", fretless=True, max_wobble=35.0, min_conf=40.0),

    # 11. Mansour Nariman
    dict(name="nariman_oud", dirs=[
        YM / "Mansour Nariman" / "Radif Oud - Rast-Panjgah",
    ], fmin=110.0, fmax=550.0, drone=0.0, inst="oud", fretless=True, max_wobble=25.0, min_conf=42.0),

    # 12. Aliakbar Shekarchi
    dict(name="shekarchi_kamancheh", dirs=[
        YM / "Aliakbar Shekarchi" / "Radif Kamancheh - Rast-Panjgah",
    ], fmin=180.0, fmax=750.0, drone=0.0, inst="kamancheh", fretless=True, max_wobble=30.0, min_conf=40.0),

    # 13. Ahmad Ebadi
    dict(name="ebadi_setar", dirs=[
        YM / "Ahmad Ebadi" / "Setar Solo - Rast-Panjgah",
    ], fmin=110.0, fmax=550.0, drone=0.0, inst="setar", fretless=False, max_wobble=22.0, min_conf=45.0),

    # 14. Abolhasan Saba
    dict(name="saba_violin", dirs=[
        YM / "Abolhasan Saba" / "Violin Vol 3 - Rast-Panjgah",
        YM / "Abolhasan Saba" / "Violin - Rast-Panjgah",
    ], fmin=180.0, fmax=850.0, drone=0.0, inst="violin", fretless=True, max_wobble=30.0, min_conf=42.0),

    # 15. Jalil Shahnaz
    dict(name="shahnaz_tar", dirs=[
        YM / "Jalil Shahnaz" / "Tar Solo - Rast-Panjgah",
    ], fmin=180.0, fmax=720.0, drone=0.0, inst="tar", fretless=False, max_wobble=22.0, min_conf=45.0),
]


def transcode_to_wav(in_path: Path, out_path: Path) -> bool:
    cmd = [
        "/opt/homebrew/bin/ffmpeg", "-y", "-i", str(in_path),
        "-ar", "44100", "-ac", "1", "-f", "wav", str(out_path)
    ]
    p = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return p.returncode == 0


def process_audio_file(args):
    src_name, audio_path, track_stem, fmin, fmax, drone, max_wobble, min_conf = args
    audio_path = Path(audio_path)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
        tmp_wav = Path(tf.name)

    try:
        if audio_path.suffix.lower() == ".wav":
            in_wav = audio_path
        else:
            ok = transcode_to_wav(audio_path, tmp_wav)
            if not ok:
                return {"src": src_name, "track": track_stem, "res": {"track": track_stem, "f": [], "t": [], "method": [], "conf": [], "wobble_plat_c": [], "wobble_sus_c": [], "drift_c_per_s": [], "attack_bend_c": []}}
            in_wav = tmp_wav

        res = extract_single_wav(
            in_wav,
            track_stem,
            fmin,
            fmax,
            drone,
            max_wobble_plat_c=max_wobble,
            min_conf=min_conf,
            max_sec=600.0,
        )
    finally:
        if tmp_wav.exists():
            try:
                tmp_wav.unlink()
            except Exception:
                pass

    return {"src": src_name, "track": track_stem, "res": res}


def main():
    t0 = time.time()
    ensure_dylib()
    tasks = []
    seen = set()

    for s in EXPANDED_RP_SOURCES:
        for d in s["dirs"]:
            if not d.exists():
                continue
            candidates = sorted(list(d.glob("*.wav")) + list(d.glob("*.m4a")) + list(d.glob("*.mp4")))
            for f in candidates:
                # If there is a trimmed version of Hormozi, prefer the trimmed one
                if "Saeed Hormozi Setar Rast Panjgah.wav" == f.name and (d / "01 - Saeed Hormozi Setar Rast Panjgah (Min 27 Onwards).wav").exists():
                    continue
                key = (s["name"], f.stem)
                if key in seen:
                    continue
                seen.add(key)
                tasks.append((
                    s["name"],
                    str(f),
                    f.stem,
                    s["fmin"],
                    s["fmax"],
                    s["drone"],
                    s.get("max_wobble", 22.0),
                    s.get("min_conf", 45.0),
                ))

    print(f"Extracting {len(tasks)} tracks across {len(EXPANDED_RP_SOURCES)} Expanded Grand Rast-Panjgah sources...", flush=True)

    res_by_src: dict[str, list[dict]] = {s["name"]: [] for s in EXPANDED_RP_SOURCES}
    done = 0
    with ProcessPoolExecutor(max_workers=min(8, os.cpu_count() or 4)) as ex:
        futs = {ex.submit(process_audio_file, t): (t[0], t[2]) for t in tasks}
        for fut in as_completed(futs):
            src, stem = futs[fut]
            try:
                out = fut.result()
                res_by_src[src].append(out["res"])
                done += 1
                n_str = len(out["res"]["f"]) if out["res"] and "f" in out["res"] else 0
                if done % 10 == 0 or done == len(tasks):
                    print(f"[{done:3d}/{len(tasks):3d}] {src:<25s} {stem[:35]:<35s} -> {n_str:4d} strikes", flush=True)
            except Exception as e:
                print(f"FAILED {src} {stem}: {e}", file=sys.stderr)

    print(f"\n--- Saving strike NPZ caches per master ---")
    tot_all = 0
    for s in EXPANDED_RP_SOURCES:
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
        p = OUT / f"strikes_expanded_rp_{sname}.npz"
        save_npz_pure(p, {k: (A[k], kinds[k]) for k in A})
        mc = statistics.median(A["conf"]) if A["conf"] else 0
        tot_all += len(A["f"])
        print(f"[saved] {p.name:38s} tracks={len(rows):2d} strikes={len(A['f']):5d} med_conf={mc:.1f} (fretless={s['fretless']})", flush=True)

    dt = time.time() - t0
    print(f"\nAll {len(EXPANDED_RP_SOURCES)} Expanded Grand Rast-Panjgah masters extracted in {dt:.1f}s: {tot_all:,} strikes across {len(tasks)} tracks.")


if __name__ == "__main__":
    main()
