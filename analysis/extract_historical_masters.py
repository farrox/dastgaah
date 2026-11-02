#!/usr/bin/env python3
"""Run v3 4-stage strike extractor across newly added historical & classical masters:
- Habib Sama'i (Santur 1930s archive)
- Gholam-Hossein Bigjekhani (Tar - Tabriz School)
- Jalil Shahnaz (Tar - Isfahan School)
- Faramarz Payvar (Santur Authority)
- Early Shellac Masters (Agha Hossein-Qoli 1907, Darvish Khan 1910, Bagher Khan Rameshgar 1907, Hossein Khan Esmailzadeh, Saeed Hormozi)
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

MASTERS_SOURCES = [
    dict(name="habib_samai_santur", dirs=[
        YM / "habib_samai_santur",
    ], fmin=120.0, fmax=1200.0, drone=0.0, inst="santur", fretless=False, max_wobble=28.0, min_conf=40.0),

    dict(name="bigjekhani_tar", dirs=[
        YM / "bigjekhani_tar",
    ], fmin=110.0, fmax=900.0, drone=0.0, inst="tar", fretless=False, max_wobble=22.0, min_conf=45.0),

    dict(name="jalil_shahnaz_tar", dirs=[
        YM / "jalil_shahnaz_tar",
    ], fmin=110.0, fmax=900.0, drone=0.0, inst="tar", fretless=False, max_wobble=22.0, min_conf=45.0),

    dict(name="faramarz_payvar_santur", dirs=[
        YM / "faramarz_payvar_santur",
    ], fmin=120.0, fmax=1200.0, drone=0.0, inst="santur", fretless=False, max_wobble=20.0, min_conf=45.0),

    dict(name="early_masters_shellac", dirs=[
        YM / "early_masters",
    ], fmin=100.0, fmax=1000.0, drone=0.0, inst="historical", fretless=False, max_wobble=35.0, min_conf=35.0),
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
            max_sec=420.0,
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

    for s in MASTERS_SOURCES:
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
                    s.get("min_conf", 45.0),
                ))

    print(f"Extracting {len(tasks)} tracks across {len(MASTERS_SOURCES)} Historical / Master sources...", flush=True)

    res_by_src: dict[str, list[dict]] = {s["name"]: [] for s in MASTERS_SOURCES}
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
    for s in MASTERS_SOURCES:
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
        p = OUT / f"strikes_{sname}.npz"
        save_npz_pure(p, {k: (A[k], kinds[k]) for k in A})
        mc = statistics.median(A["conf"]) if A["conf"] else 0
        tot_all += len(A["f"])
        print(f"[saved] {p.name:36s} tracks={len(rows):2d} strikes={len(A['f']):5d} med_conf={mc:.1f}", flush=True)

    dt = time.time() - t0
    print(f"\nAll {len(MASTERS_SOURCES)} historical masters extracted in {dt:.1f}s: {tot_all:,} strikes across {len(tasks)} tracks.")


if __name__ == "__main__":
    main()
