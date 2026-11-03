#!/usr/bin/env python3
"""Run v3 4-stage native C strike extractor across the 5 Secondary Avazes of Shur:
1. Abu'ata
2. Bayat-e Tork
3. Afshari
4. Dashti
5. Bayat-e Kord
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

AVAZ_SOURCES = [
    # 1. Abu'ata
    dict(name="avaz_abuata", dirs=[
        (YM / "Ali-Akbar Shahnazi" / "The Advanced Shahnazi Radif I", "Abuata"),
        (YM / "Mahmud Karimi" / "Abuata", None),
        (YM / "Yusef Forutan" / "Radif Setar - Shur", "Abuata"),
    ], fmin=130.0, fmax=650.0, drone=0.0, fretless=False, max_wobble=25.0, min_conf=40.0),

    # 2. Bayat-e Tork
    dict(name="avaz_bayat_tork", dirs=[
        (YM / "Nur-Ali Borumand" / "Bayat Tork", None),
        (YM / "Mahmud Karimi" / "Bayat Tork", None),
        (YM / "Ali-Akbar Shahnazi" / "The Advanced Shahnazi Radif I", "Tork"),
    ], fmin=130.0, fmax=650.0, drone=0.0, fretless=False, max_wobble=25.0, min_conf=40.0),

    # 3. Afshari
    dict(name="avaz_afshari", dirs=[
        (YM / "Saeed Hormozi" / "Setar - Afshari Solo", None),
        (YM / "Nur-Ali Borumand" / "Afshari", None),
        (YM / "Mahmud Karimi" / "Afshari", None),
        (YM / "Ali-Akbar Shahnazi" / "The Advanced Shahnazi Radif III", "Afshari"),
    ], fmin=110.0, fmax=650.0, drone=0.0, fretless=False, max_wobble=25.0, min_conf=40.0),

    # 4. Dashti
    dict(name="avaz_dashti", dirs=[
        (YM / "Ali-Akbar Shahnazi" / "Radif Tar - Dashti", None),
        (YM / "Mahmud Karimi" / "Vocal Radif - Dashti", None),
        (YM / "Hossein Alizadeh" / "Radif Navazi - Dashti", None),
        (YM / "Abolhasan Saba" / "Dashti Solo", None),
        (YM / "Mohammad Reza Lotfi" / "Dashti Solo", None),
        (YM / "Hassan Kasaei" / "Radifs 4 - Dashti", None),
        (YM / "Aliakbar Shekarchi" / "Radif Kamancheh - Dashti", None),
        (YM / "Ahmad Ebadi" / "Setar Solo - Dashti", None),
    ], fmin=110.0, fmax=750.0, drone=0.0, fretless=False, max_wobble=25.0, min_conf=42.0),

    # 5. Bayat-e Kord
    dict(name="avaz_bayat_kord", dirs=[
        (YM / "Nur-Ali Borumand" / "Kord-e Bayat", None),
        (YM / "Hossein Alizadeh" / "The Art Of Improvisation - Rast-Panjgah", "Kord"),
    ], fmin=130.0, fmax=650.0, drone=0.0, fretless=False, max_wobble=22.0, min_conf=42.0),
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

    for s in AVAZ_SOURCES:
        for d, filt in s["dirs"]:
            if not d.exists():
                continue
            candidates = sorted(list(d.glob("*.wav")))
            for f in candidates:
                if filt is not None and filt.lower() not in f.name.lower():
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
                    s.get("min_conf", 42.0),
                ))

    print(f"Extracting {len(tasks)} tracks across 5 Secondary Avazes...", flush=True)

    res_by_src: dict[str, list[dict]] = {s["name"]: [] for s in AVAZ_SOURCES}
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
                    print(f"[{done:3d}/{len(tasks):3d}] {src:<20s} {stem[:35]:<35s} -> {n_str:4d} strikes", flush=True)
            except Exception as e:
                print(f"FAILED {src} {stem}: {e}", file=sys.stderr)

    print(f"\n--- Saving strike NPZ caches per Avaz ---")
    tot_all = 0
    for s in AVAZ_SOURCES:
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
        print(f"[saved] {p.name:32s} tracks={len(rows):2d} strikes={len(A['f']):5d} med_conf={mc:.1f}", flush=True)

    dt = time.time() - t0
    print(f"\nAll 5 Secondary Avazes extracted in {dt:.1f}s: {tot_all:,} strikes across {len(tasks)} tracks.")

if __name__ == "__main__":
    main()
