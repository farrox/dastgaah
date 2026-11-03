#!/usr/bin/env python3
"""Run v3 4-stage native C strike extractor across the Grand Dastgah-e Rast-Panjgah Corpus.

Masters:
1. Hossein Alizadeh (Tar & Setar, Radif Navazi Rast-Panjgah)
2. Ali-Akbar Shahnazi (Tar, Radif Tar - Rast-Panjgah)
3. Mahmud Karimi (Voice, Vocal Radif - Rast-Panjgah)
4. Nur-Ali Borumand (Tar/Setar, Radif Mirza Abdollah - Rast-Panjgah)
5. Mansour Nariman (Oud, Radif Oud - Rast-Panjgah)
6. Morteza Neydavud (Tar, Radif Tar - Rast-Panjgah)
7. Aliakbar Shekarchi (Kamancheh, Radif Kamancheh - Rast-Panjgah)
8. Hassan Kasaei (Ney, Ney - Rast-Panjgah)
9. Jalil Shahnaz (Tar, Tar Solo - Rast-Panjgah)
10. Ahmad Ebadi (Setar, Setar Solo - Rast-Panjgah)
11. Abolhasan Saba (Violin, Violin - Rast-Panjgah)
12. Mohammad Reza Lotfi (Tar, Tar - Rast-Panjgah)
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

GRAND_RP_SOURCES = [
    dict(name="alizadeh_tar_setar", dirs=[
        YM / "Hossein Alizadeh" / "Radif Navazi - Rast-Panjgah",
    ], fmin=180.0, fmax=720.0, drone=0.0, inst="tar_setar", fretless=False, max_wobble=20.0, min_conf=48.0),

    dict(name="shahnazi_tar", dirs=[
        YM / "Ali-Akbar Shahnazi" / "Radif Tar - Rast-Panjgah",
    ], fmin=180.0, fmax=720.0, drone=0.0, inst="tar", fretless=False, max_wobble=22.0, min_conf=45.0),

    dict(name="karimi_vocal", dirs=[
        YM / "Mahmud Karimi" / "Vocal Radif - Rast-Panjgah",
    ], fmin=140.0, fmax=550.0, drone=0.0, inst="voice", fretless=True, max_wobble=35.0, min_conf=40.0),

    dict(name="borumand_tar_setar", dirs=[
        YM / "Nur-Ali Borumand" / "Radif Mirza Abdollah - Rast-Panjgah",
    ], fmin=110.0, fmax=600.0, drone=0.0, inst="tar_setar", fretless=False, max_wobble=22.0, min_conf=45.0),

    dict(name="nariman_oud", dirs=[
        YM / "Mansour Nariman" / "Radif Oud - Rast-Panjgah",
    ], fmin=110.0, fmax=550.0, drone=0.0, inst="oud", fretless=True, max_wobble=25.0, min_conf=42.0),

    dict(name="neydavud_tar", dirs=[
        YM / "Morteza Neydavud" / "Radif Tar - Rast-Panjgah",
    ], fmin=180.0, fmax=720.0, drone=0.0, inst="tar", fretless=False, max_wobble=25.0, min_conf=42.0),

    dict(name="shekarchi_kamancheh", dirs=[
        YM / "Aliakbar Shekarchi" / "Radif Kamancheh - Rast-Panjgah",
    ], fmin=180.0, fmax=750.0, drone=0.0, inst="kamancheh", fretless=True, max_wobble=30.0, min_conf=40.0),

    dict(name="kasaei_ney", dirs=[
        YM / "Hassan Kasaei" / "Ney - Rast-Panjgah",
    ], fmin=180.0, fmax=750.0, drone=0.0, inst="ney", fretless=True, max_wobble=30.0, min_conf=40.0),

    dict(name="shahnaz_tar", dirs=[
        YM / "Jalil Shahnaz" / "Tar Solo - Rast-Panjgah",
    ], fmin=180.0, fmax=720.0, drone=0.0, inst="tar", fretless=False, max_wobble=22.0, min_conf=45.0),

    dict(name="ebadi_setar", dirs=[
        YM / "Ahmad Ebadi" / "Setar Solo - Rast-Panjgah",
    ], fmin=110.0, fmax=550.0, drone=0.0, inst="setar", fretless=False, max_wobble=22.0, min_conf=45.0),

    dict(name="saba_violin", dirs=[
        YM / "Abolhasan Saba" / "Violin - Rast-Panjgah",
    ], fmin=180.0, fmax=850.0, drone=0.0, inst="violin", fretless=True, max_wobble=30.0, min_conf=42.0),

    dict(name="lotfi_tar", dirs=[
        YM / "Mohammad Reza Lotfi" / "Tar - Rast-Panjgah",
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
            max_sec=480.0,
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

    for s in GRAND_RP_SOURCES:
        for d in s["dirs"]:
            if not d.exists():
                continue
            candidates = sorted(list(d.glob("*.wav")) + list(d.glob("*.m4a")) + list(d.glob("*.mp4")))
            for f in candidates:
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
                    s.get("min_conf", 48.0),
                ))

    print(f"Extracting {len(tasks)} tracks across {len(GRAND_RP_SOURCES)} Grand Rast-Panjgah sources...", flush=True)

    res_by_src: dict[str, list[dict]] = {s["name"]: [] for s in GRAND_RP_SOURCES}
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
                if done % 5 == 0 or done == len(tasks):
                    print(f"[{done:2d}/{len(tasks):2d}] {src:<25s} {stem[:35]:<35s} -> {n_str:4d} strikes", flush=True)
            except Exception as e:
                print(f"FAILED {src} {stem}: {e}", file=sys.stderr)

    print(f"\n--- Saving strike NPZ caches per master ---")
    tot_all = 0
    for s in GRAND_RP_SOURCES:
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
        p = OUT / f"strikes_rast_panjgah_{sname}.npz"
        save_npz_pure(p, {k: (A[k], kinds[k]) for k in A})
        mc = statistics.median(A["conf"]) if A["conf"] else 0
        tot_all += len(A["f"])
        print(f"[saved] {p.name:36s} tracks={len(rows):2d} strikes={len(A['f']):5d} med_conf={mc:.1f} (fretless={s['fretless']})", flush=True)

    dt = time.time() - t0
    print(f"\nAll {len(GRAND_RP_SOURCES)} Grand Rast-Panjgah masters extracted in {dt:.1f}s: {tot_all:,} strikes across {len(tasks)} tracks.")


if __name__ == "__main__":
    main()
