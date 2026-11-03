#!/usr/bin/env python3
"""Run v3 4-stage native C strike extractor across 3 Historical Epochs:
Epoch 1: Early Qajar Shellac Era (1906–1920)
  - Aqa Hoseyn-Qoli (Paris/Tbilisi 1907-1912)
  - Darvish Khan (Paris 1906, London 1914)
  - The Tar of Qajar Period (Anthology of Mirza Abdollah, Gholam-Hoseyn, etc.)

Epoch 2: Mid-Century Masters & Radif Preservers (1950s–1970s)
  - Yousef Foroutan (Solo & Shiraz Festival 1967)
  - Saeed Hormozi (Tar Solo & Private Setar)
  - Abolhasan Saba (Solo Setar)
  - A Century of Setar (Classic lineage)

Epoch 3: Modal Antiquity Reconstructions & Anthologies (1980s–Present)
  - Panjgah (Ancient Rast-e Qadim, Talvin-e Nava, Mokhalef-e Segah - Mahoor)
  - Shahnavaz (Historical Anthology)
  - A Century of Tar
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

EPOCH_CONFIGS = [
    # EPOCH 1: Early Qajar (1906-1920)
    dict(name="epoch1_qajar_aqa_hoseyn_qoli", dirs=[
        YM / "Historical Anthologies" / "Tar - Aqa Hoseyn-Qoli",
    ], fmin=150.0, fmax=750.0, drone=0.0, max_wobble=24.0, min_conf=40.0),

    dict(name="epoch1_qajar_darvish_khan", dirs=[
        YM / "Darvish Khan" / "Darvish Khan Tar",
        YM / "Darvish Khan" / "Collection 16 - Darvish 1906-1914",
    ], fmin=150.0, fmax=750.0, drone=0.0, max_wobble=24.0, min_conf=40.0),

    dict(name="epoch1_qajar_tar_anthology", dirs=[
        YM / "Historical Anthologies" / "The Tar of Qajar Period",
    ], fmin=150.0, fmax=750.0, drone=0.0, max_wobble=24.0, min_conf=40.0),

    # EPOCH 2: Mid-Century (1950s-1970s)
    dict(name="epoch2_mid_foroutan_setar", dirs=[
        YM / "Yusef Forutan" / "Solo Setar - Mahoor",
        YM / "Yusef Forutan" / "Shiraz Festival 1967 - Mahoor",
        YM / "Yusef Forutan" / "Radif Setar - Shur",
    ], fmin=110.0, fmax=600.0, drone=0.0, max_wobble=20.0, min_conf=45.0),

    dict(name="epoch2_mid_hormozi_tar_setar", dirs=[
        YM / "Saeed Hormozi" / "Tar Solo",
        YM / "Saeed Hormozi" / "Setar - Afshari Solo",
        YM / "Saeed Hormozi" / "Setar - Rast Panjgah",
    ], fmin=110.0, fmax=650.0, drone=0.0, max_wobble=20.0, min_conf=45.0),

    dict(name="epoch2_mid_saba_setar", dirs=[
        YM / "Abolhasan Saba" / "Abolhasan Saba Setar",
    ], fmin=110.0, fmax=600.0, drone=0.0, max_wobble=22.0, min_conf=45.0),

    dict(name="epoch2_mid_century_setar", dirs=[
        YM / "Historical Anthologies" / "A Century of Setar",
    ], fmin=110.0, fmax=600.0, drone=0.0, max_wobble=22.0, min_conf=45.0),

    # EPOCH 3: Modal Antiquity & 20th C Century Anthologies
    dict(name="epoch3_panjgah_antiquity", dirs=[
        Path("audio/Mahoor Demos/Panjgah"),
    ], fmin=120.0, fmax=750.0, drone=0.0, max_wobble=22.0, min_conf=42.0),

    dict(name="epoch3_shahnavaz_anthology", dirs=[
        YM / "Historical Anthologies" / "Shahnavaz",
    ], fmin=130.0, fmax=700.0, drone=0.0, max_wobble=22.0, min_conf=42.0),

    dict(name="epoch3_century_tar_anthology", dirs=[
        YM / "Historical Anthologies" / "A Century of Tar",
    ], fmin=140.0, fmax=750.0, drone=0.0, max_wobble=22.0, min_conf=45.0),
]

def process_audio_file(args):
    src_name, audio_path, track_stem, fmin, fmax, drone, max_wobble, min_conf = args
    audio_path = Path(audio_path)

    res = extract_single_wav(
        audio_path,
        track_stem,
        fmin,
        fmax,
        drone,
        max_wobble_plat_c=max_wobble,
        min_conf=min_conf,
        max_sec=420.0, # Cap at 7 mins per track for efficiency
    )
    return {"src": src_name, "track": track_stem, "res": res}

def main():
    t0 = time.time()
    ensure_dylib()
    tasks = []
    seen = set()

    for s in EPOCH_CONFIGS:
        for d in s["dirs"]:
            if not d.exists():
                continue
            candidates = sorted(list(d.glob("*.wav")))
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
                    s.get("min_conf", 42.0),
                ))

    print(f"Extracting {len(tasks)} historical tracks across {len(EPOCH_CONFIGS)} sources...", flush=True)

    res_by_src: dict[str, list[dict]] = {s["name"]: [] for s in EPOCH_CONFIGS}
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
                if done % 15 == 0 or done == len(tasks):
                    print(f"[{done:3d}/{len(tasks):3d}] {src:<30s} {stem[:30]:<30s} -> {n_str:4d} strikes", flush=True)
            except Exception as e:
                print(f"FAILED {src} {stem}: {e}", file=sys.stderr)

    print(f"\n--- Saving strike NPZ caches per historical source ---")
    tot_all = 0
    for s in EPOCH_CONFIGS:
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
        p = OUT / f"strikes_historical_{sname}.npz"
        save_npz_pure(p, {k: (A[k], kinds[k]) for k in A})
        mc = statistics.median(A["conf"]) if A["conf"] else 0
        tot_all += len(A["f"])
        print(f"[saved] {p.name:42s} tracks={len(rows):2d} strikes={len(A['f']):5d} med_conf={mc:.1f}", flush=True)

    dt = time.time() - t0
    print(f"\nAll historical sources extracted in {dt:.1f}s: {tot_all:,} strikes across {len(tasks)} tracks.")

if __name__ == "__main__":
    main()
