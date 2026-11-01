#!/usr/bin/env python3
"""Upgraded 4-Stage Frequency Extraction Pipeline (v3) across all 13 Dastgāh-e Māhur sources.

Stages (implemented in native C in `analysis/pitch_dsp.c`):
  1. Pre-Onset Spectral Drone/Decay Subtraction (`[-110 ms, -10 ms]` soft Wiener mask)
     + Parabolic-Interpolated YIN (CMND) + Multi-Harmonic Least-Squares / Phase-Vocoder (`HM-LS/PV`)
     initial F0 seed on `[+50 ms, +350 ms]`.
  2. Harmonic-Locked Narrowband Hilbert Transform (`NB-Hilbert`, ±6.5% cosine-tapered analytic filter
     around highest-SIR harmonic k* in {1,2,3,4}) for micro-pitch trajectory, attack pluck-bend
     (`attack_bend_c`), and sustain modulation (`wobble_sus_c`, `drift_c_per_s`).
  3. Adaptive 140 ms Stationary Plateau Selection (`[t*, t* + 140 ms]` inside `[+60 ms, +480 ms]`)
     minimizing instantaneous-frequency MAD + drift while avoiding the [0, 60 ms] mezrab transient.
  4. Plateau-Refined `HM-LS/PV + Parabolic YIN + NB-Hilbert` Arbitration & Stationarity/Confidence Gate
     (`wobble_plat_c <= 18.0¢`, `conf >= 48.0`).
"""
from __future__ import annotations

import ctypes
import json
import math
import os
import statistics
import struct
import subprocess
import time
import wave
import zipfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from rebuild_consensus_from_cache import cents_scalar, est_track_do, multi_anchor_track_do

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis"
YM = ROOT / "audio" / "YouTube Music"
DYLIB_PATH = OUT / "libpitch_dsp.dylib"
C_SRC_PATH = OUT / "pitch_dsp.c"

METHOD_NAMES = {
    1: "HMLS+NBH+YIN",
    2: "HMLS+YIN",
    3: "HMLS+NBH",
    4: "YIN+NBH",
}


def ensure_dylib() -> Path:
    if not DYLIB_PATH.exists() or C_SRC_PATH.stat().st_mtime > DYLIB_PATH.stat().st_mtime:
        subprocess.run(
            ["clang", "-O3", "-dynamiclib", str(C_SRC_PATH), "-o", str(DYLIB_PATH), "-lm"],
            check=True,
        )
    return DYLIB_PATH


def _make_npy_bytes(arr: list, kind: str) -> bytes:
    """Create standard NumPy .npy v1.0 bytes in pure Python (no numpy dependency required)."""
    n = len(arr)
    if kind == "f8":
        descr = "<f8"
        shape_str = f"({n},)"
        raw = struct.pack(f"<{n}d", *[float(x) for x in arr])
    elif kind == "f8_scalar":
        descr = "<f8"
        shape_str = "()"
        raw = struct.pack("<d", float(arr[0]))
    elif kind == "i8":
        descr = "<i8"
        shape_str = f"({n},)"
        raw = struct.pack(f"<{n}q", *[int(x) for x in arr])
    elif kind == "U":
        strs = [str(x) for x in arr]
        max_len = max((len(s) for s in strs), default=1)
        if max_len < 1:
            max_len = 1
        descr = f"<U{max_len}"
        shape_str = f"({n},)"
        chunks = []
        row_bytes = max_len * 4
        for s in strs:
            b = s.encode("utf-32-le")
            if len(b) < row_bytes:
                b = b + b"\x00" * (row_bytes - len(b))
            chunks.append(b[:row_bytes])
        raw = b"".join(chunks)
    else:
        raise ValueError(f"Unsupported npy kind: {kind}")

    hdr_dict = f"{{'descr': '{descr}', 'fortran_order': False, 'shape': {shape_str}, }}"
    hdr_raw = hdr_dict.encode("latin1")
    # Total prefix (10 bytes + header_len) must be divisible by 64
    pad_len = (64 - ((10 + len(hdr_raw) + 1) % 64)) % 64
    hdr_padded = hdr_raw + (b" " * pad_len) + b"\n"
    prefix = b"\x93NUMPY\x01\x00" + struct.pack("<H", len(hdr_padded)) + hdr_padded
    return prefix + raw


def save_npz_pure(path: Path, arrays: dict[str, tuple[list, str]]) -> None:
    """Write a compressed .npz file where each entry is (list_of_values, kind)."""
    with zipfile.ZipFile(path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, (vals, kind) in arrays.items():
            zf.writestr(f"{name}.npy", _make_npy_bytes(vals, kind))


def read_wav_mono_f64(wav_path: Path, max_sec: float | None = None) -> tuple[ctypes.Array, int, float]:
    with wave.open(str(wav_path), "rb") as wf:
        sr = float(wf.getframerate())
        nframes = wf.getnframes()
        nch = wf.getnchannels()
        if max_sec is not None:
            nframes = min(nframes, int(max_sec * sr))
        raw = wf.readframes(nframes)

    # Convert 16-bit PCM to C double array
    # Unpack in chunks to avoid huge temporary tuple
    total_samples = len(raw) // (2 * nch)
    c_buf = (ctypes.c_double * total_samples)()
    step = 65536
    scale = 1.0 / 32768.0
    if nch == 1:
        for i0 in range(0, total_samples, step):
            i1 = min(total_samples, i0 + step)
            cnt = i1 - i0
            vals = struct.unpack_from(f"<{cnt}h", raw, i0 * 2)
            for j, v in enumerate(vals):
                c_buf[i0 + j] = v * scale
    else:
        for i0 in range(0, total_samples, step):
            i1 = min(total_samples, i0 + step)
            cnt = i1 - i0
            vals = struct.unpack_from(f"<{cnt * nch}h", raw, i0 * 2 * nch)
            for j in range(cnt):
                s = 0.0
                base = j * nch
                for c in range(nch):
                    s += vals[base + c]
                c_buf[i0 + j] = (s / nch) * scale
    return c_buf, total_samples, sr


def extract_single_wav(
    wav_path_str: str,
    track_label: str,
    fmin: float,
    fmax: float,
    drone_freq: float = 0.0,
    max_wobble_plat_c: float = 18.0,
    min_conf: float = 48.0,
    max_sec: float | None = None,
) -> dict:
    lib = ctypes.CDLL(str(DYLIB_PATH))
    lib.extract_track_strikes_c.argtypes = [
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_int,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_int),
    ]
    lib.extract_track_strikes_c.restype = ctypes.c_int

    wav_path = Path(wav_path_str)
    c_buf, n_samples, sr = read_wav_mono_f64(wav_path, max_sec=max_sec)
    max_out = 12000
    t_out = (ctypes.c_double * max_out)()
    f_out = (ctypes.c_double * max_out)()
    conf_out = (ctypes.c_double * max_out)()
    wob_plat_out = (ctypes.c_double * max_out)()
    wob_sus_out = (ctypes.c_double * max_out)()
    drift_out = (ctypes.c_double * max_out)()
    bend_out = (ctypes.c_double * max_out)()
    method_out = (ctypes.c_int * max_out)()

    n_ext = lib.extract_track_strikes_c(
        c_buf,
        n_samples,
        sr,
        float(fmin),
        float(fmax),
        float(drone_freq),
        float(max_wobble_plat_c),
        float(min_conf),
        max_out,
        t_out,
        f_out,
        conf_out,
        wob_plat_out,
        wob_sus_out,
        drift_out,
        bend_out,
        method_out,
    )

    return {
        "track": track_label,
        "t": [float(t_out[i]) for i in range(n_ext)],
        "f": [float(f_out[i]) for i in range(n_ext)],
        "conf": [float(conf_out[i]) for i in range(n_ext)],
        "wobble_plat_c": [float(wob_plat_out[i]) for i in range(n_ext)],
        "wobble_sus_c": [float(wob_sus_out[i]) for i in range(n_ext)],
        "drift_c_per_s": [float(drift_out[i]) for i in range(n_ext)],
        "attack_bend_c": [float(bend_out[i]) for i in range(n_ext)],
        "method": [METHOD_NAMES.get(int(method_out[i]), "HMLS+YIN") for i in range(n_ext)],
    }


def interp_linear(x_list: list[float], xp: list[float], fp: list[float]) -> list[float]:
    out = []
    n = len(xp)
    for x in x_list:
        if x <= xp[0]:
            out.append(fp[0])
        elif x >= xp[-1]:
            out.append(fp[-1])
        else:
            # binary or linear scan
            for i in range(n - 1):
                if xp[i] <= x <= xp[i + 1]:
                    w = (x - xp[i]) / max(xp[i + 1] - xp[i], 1e-12)
                    out.append(fp[i] * (1.0 - w) + fp[i + 1] * w)
                    break
    return out


def compute_sliding_local_do(
    ts: list[float],
    fs: list[float],
    seed_do: float,
    max_t_win: float,
    max_t_strike: float,
    win: float = 45.0,
    hop: float = 15.0,
) -> dict[str, tuple[list, str]]:
    """Compute sliding-window local Do (with multi-anchor rescue for modulating sections)."""
    pairs = [(t, f) for t, f in zip(ts, fs) if t <= max_t_strike]
    t_strike = [p[0] for p in pairs]
    f_strike = [p[1] for p in pairs]

    t_win = []
    do_hz = []
    n_win = []
    last_do = float(seed_do)
    t0 = 0.0
    while t0 + win <= max_t_win + 1e-6:
        tc = t0 + 0.5 * win
        w_fs = [f for t, f in pairs if t0 <= t < t0 + win]
        if len(w_fs) >= 6:
            do_val, _ = multi_anchor_track_do(w_fs, seed_do, last_do)
            if do_val is not None and abs(cents_scalar(do_val, seed_do)) <= 65.0:
                t_win.append(float(tc))
                do_hz.append(float(do_val))
                n_win.append(int(len(w_fs)))
                last_do = float(do_val)
        t0 += hop

    do_at_strike = interp_linear(t_strike, t_win, do_hz)
    c_arr = [cents_scalar(f, d) for f, d in zip(f_strike, do_at_strike)]

    return {
        "t_win": (t_win, "f8"),
        "do_hz": (do_hz, "f8"),
        "n": (n_win, "i8"),
        "t_strike": (t_strike, "f8"),
        "f_strike": (f_strike, "f8"),
        "do_at_strike": (do_at_strike, "f8"),
        "cents": (c_arr, "f8"),
        "seed": ([float(seed_do)], "f8_scalar"),
        "win": ([float(win)], "f8_scalar"),
        "hop": ([float(hop)], "f8_scalar"),
    }


MULTI_TRACK_ALBUMS = [
    {
        "name": "nariman",
        "dir": YM / "Mansour Nariman" / "Iranian Music Radif for Oud _ Dastgahe Mahour",
        "fmin": 125.0,
        "fmax": 480.0,
        "drone": 0.0,
        "max_wobble": 18.0,
        "min_conf": 48.0,
    },
    {
        "name": "alizadeh",
        "dir": YM / "Hossein Alizadeh" / "Radif Navazi - Setar_ Mahur",
        "fmin": 180.0,
        "fmax": 680.0,
        "drone": 220.8,
        "max_wobble": 18.0,
        "min_conf": 48.0,
    },
    {
        "name": "shekarchi",
        "dir": YM / "Aliakbar Shekarchi" / "Radif Of Persian Classical Music _ Dastgahe Mahour",
        "fmin": 235.0,
        "fmax": 850.0,
        "drone": 0.0,
        "max_wobble": 18.0,
        "min_conf": 48.0,
    },
    {
        "name": "borumand",
        "dir": YM / "Nur-Ali Borumand" / "The Mirza Abdollah Radif for Tar and Setar, Vol. 6",
        "fmin": 195.0,
        "fmax": 680.0,
        "drone": 0.0,
        "max_wobble": 18.0,
        "min_conf": 48.0,
    },
    {
        "name": "forutan",
        "dir": YM / "Yusef Forutan" / "Radif of Persian Music on Setar III - Mahur",
        "fmin": 140.0,
        "fmax": 480.0,
        "drone": 0.0,
        "max_wobble": 18.0,
        "min_conf": 48.0,
    },
    {
        "name": "neydavud",
        "dir": YM / "Morteza Neydavud" / "Radif of Persian Music on Tar, Vol. 4",
        "fmin": 185.0,
        "fmax": 680.0,
        "drone": 0.0,
        "max_wobble": 18.0,
        "min_conf": 48.0,
    },
    {
        "name": "shahnazi",
        "dir": YM / "Ali-Akbar Shahnazi" / "The Advanced Shahnazi Radif III",
        "fmin": 195.0,
        "fmax": 710.0,
        "drone": 0.0,
        "max_wobble": 18.0,
        "min_conf": 48.0,
        "filter_fn": lambda p: "Mahur" in p.name,
    },
    {
        "name": "kasaei_radif",
        "dir": YM / "Hassan Kasaei" / "Iranian Classical Music Radifs 1 - Mahoor, Shur",
        "fmin": 175.0,
        "fmax": 740.0,
        "drone": 0.0,
        "max_wobble": 18.0,
        "min_conf": 48.0,
        "filter_fn": lambda p: "Mahoor" in p.name,
    },
    {
        "name": "karimi",
        "dir": YM / "Mahmud Karimi" / "Avaz Course_ Vocal Radif of Persian Classical Music, Vol. 3",
        "fmin": 115.0,
        "fmax": 460.0,
        "drone": 0.0,
        "max_wobble": 20.0,  # slightly more permissive for vocal sustain plateaus
        "min_conf": 46.0,
        "filter_fn": lambda p: "Mahur" in p.name,
    },
    {
        "name": "lotfi_playlist",
        "dir": YM / "Mohammad Reza Lotfi" / "Mahur playlist curated",
        "fmin": 165.0,
        "fmax": 640.0,
        "drone": 0.0,
        "max_wobble": 18.0,
        "min_conf": 48.0,
    },
]

SINGLE_TRACK_ALBUMS = [
    {
        "name": "lotfi",
        "wav": YM / "Mohammad Reza Lotfi" / "In the Memory of Darvish Khan" / "Mohammad Reza Lotfi - In the Memory of Darvish Khan (2006, CD).wav",
        "track_label": "lotfi_darvish_khan",
        "fmin": 175.0,
        "fmax": 660.0,
        "seed_do": 326.3,
        "max_t_win": 1200.0,
        "max_t_strike": 1200.0,
        "max_sec_read": None,
        "local_do_npz": OUT / "lotfi_local_do.npz",
    },
    {
        "name": "ebadi",
        "wav": YM / "Ahmad Ebadi" / "Setar Solo - Mahur" / "Mahur [A9S5UGMcrkU].wav",
        "track_label": "ebadi_mahur",
        "fmin": 190.0,
        "fmax": 640.0,
        "seed_do": 253.3,
        "max_t_win": 540.0,
        "max_t_strike": 685.0,
        "max_sec_read": None,
        "local_do_npz": OUT / "ebadi_local_do.npz",
    },
    {
        "name": "saba",
        "wav": YM / "Abolhasan Saba" / "Setar by Saba" / "03 - Mahoor.wav",
        "track_label": "saba_mahoor",
        "fmin": 190.0,
        "fmax": 660.0,
        "seed_do": 376.8,
        "max_t_win": 1005.0,
        "max_t_strike": 1020.0,
        "max_sec_read": None,
        "local_do_npz": OUT / "saba_local_do.npz",
    },
]


def main() -> None:
    t_start = time.time()
    ensure_dylib()

    tasks = []
    for cfg in MULTI_TRACK_ALBUMS:
        wavs = sorted(cfg["dir"].glob("*.wav"))
        if "filter_fn" in cfg:
            wavs = [w for w in wavs if cfg["filter_fn"](w)]
        assert wavs, f"No wavs found for {cfg['name']} in {cfg['dir']}"
        for w in wavs:
            tasks.append((cfg["name"], str(w), w.stem, cfg["fmin"], cfg["fmax"], cfg["drone"], cfg["max_wobble"], cfg["min_conf"], None))

    for cfg in SINGLE_TRACK_ALBUMS:
        assert cfg["wav"].exists(), f"Missing {cfg['wav']}"
        tasks.append((cfg["name"], str(cfg["wav"]), cfg["track_label"], cfg["fmin"], cfg["fmax"], 0.0, 18.0, 48.0, cfg["max_sec_read"]))

    print(f"Dispatching {len(tasks)} audio tracks across 13 Mahur albums to C DSP extractor...")

    results_by_album: dict[str, list[dict]] = {c["name"]: [] for c in MULTI_TRACK_ALBUMS + SINGLE_TRACK_ALBUMS}
    max_workers = min(8, os.cpu_count() or 4)
    done_count = 0

    with ProcessPoolExecutor(max_workers=max_workers) as ex:
        fut_to_meta = {
            ex.submit(extract_single_wav, wav_s, tr_lab, fmin, fmax, drone, mwob, mconf, msec): (alb_name, tr_lab)
            for (alb_name, wav_s, tr_lab, fmin, fmax, drone, mwob, mconf, msec) in tasks
        }
        for fut in as_completed(fut_to_meta):
            alb_name, tr_lab = fut_to_meta[fut]
            res = fut.result()
            results_by_album[alb_name].append(res)
            done_count += 1
            if done_count % 25 == 0 or done_count == len(tasks):
                elapsed = time.time() - t_start
                print(f"  [{done_count:3d}/{len(tasks)}] ({elapsed:5.1f}s) latest: {alb_name} / {tr_lab} -> {len(res['f'])} strikes", flush=True)

    # Save multi-track albums
    for cfg in MULTI_TRACK_ALBUMS:
        name = cfg["name"]
        track_rows = sorted(results_by_album[name], key=lambda r: r["track"])
        f_all, t_all, tr_all, m_all = [], [], [], []
        conf_all, wp_all, ws_all, dr_all, bd_all = [], [], [], [], []
        for r in track_rows:
            n_r = len(r["f"])
            f_all.extend(r["f"])
            t_all.extend(r["t"])
            tr_all.extend([r["track"]] * n_r)
            m_all.extend(r["method"])
            conf_all.extend(r["conf"])
            wp_all.extend(r["wobble_plat_c"])
            ws_all.extend(r["wobble_sus_c"])
            dr_all.extend(r["drift_c_per_s"])
            bd_all.extend(r["attack_bend_c"])

        npz_path = OUT / f"strikes_{name}.npz"
        save_npz_pure(
            npz_path,
            {
                "f": (f_all, "f8"),
                "t": (t_all, "f8"),
                "track": (tr_all, "U"),
                "method": (m_all, "U"),
                "conf": (conf_all, "f8"),
                "wobble_plat_c": (wp_all, "f8"),
                "wobble_sus_c": (ws_all, "f8"),
                "drift_c_per_s": (dr_all, "f8"),
                "attack_bend_c": (bd_all, "f8"),
            },
        )
        med_conf = statistics.median(conf_all) if conf_all else 0.0
        med_wob = statistics.median(wp_all) if wp_all else 0.0
        print(f"[saved] {npz_path.name:28s} tracks={len(track_rows):2d}  strikes={len(f_all):5d}  med_conf={med_conf:4.1f}  med_wob_plat={med_wob:4.2f}¢")

    # Update lotfi_playlist_filter.json with upgraded per-track Do estimates
    lp_filt_path = OUT / "lotfi_playlist_filter.json"
    if lp_filt_path.exists():
        lp_filt = json.loads(lp_filt_path.read_text())
        seed_lp = float(lp_filt.get("seed_do", 318.9))
        track_rows = sorted(results_by_album["lotfi_playlist"], key=lambda r: r["track"])
        new_kept = []
        new_skipped = []
        last_do = seed_lp
        for r in track_rows:
            do_val, mode = multi_anchor_track_do(r["f"], seed_lp, last_do)
            if do_val is not None and abs(cents_scalar(do_val, seed_lp)) <= 48.0:
                new_kept.append(
                    {
                        "track": r["track"],
                        "do": float(do_val),
                        "n_strikes": len(r["f"]),
                        "mode": mode,
                    }
                )
                last_do = float(do_val)
            else:
                new_skipped.append(
                    {
                        "track": r["track"],
                        "do": float(do_val) if do_val is not None else None,
                        "n_strikes": len(r["f"]),
                        "reasons": ["Do shift/modulating"],
                    }
                )
        if new_kept:
            lp_filt["kept"] = new_kept
            lp_filt["skipped"] = new_skipped
            lp_filt["median_do"] = float(statistics.median([k["do"] for k in new_kept]))
            lp_filt["n_strikes"] = int(sum(k["n_strikes"] for k in new_kept))
            lp_filt_path.write_text(json.dumps(lp_filt, indent=2))
            print(f"[updated] {lp_filt_path.name} kept={len(new_kept)}/{len(track_rows)} median_do={lp_filt['median_do']:.2f} Hz")

    # Save single-track albums & their sliding-window local_do.npz files
    for cfg in SINGLE_TRACK_ALBUMS:
        name = cfg["name"]
        r = results_by_album[name][0]
        npz_path = OUT / f"strikes_{name}.npz"
        save_npz_pure(
            npz_path,
            {
                "f": (r["f"], "f8"),
                "t": (r["t"], "f8"),
                "track": ([r["track"]] * len(r["f"]), "U"),
                "method": (r["method"], "U"),
                "conf": (r["conf"], "f8"),
                "wobble_plat_c": (r["wobble_plat_c"], "f8"),
                "wobble_sus_c": (r["wobble_sus_c"], "f8"),
                "drift_c_per_s": (r["drift_c_per_s"], "f8"),
                "attack_bend_c": (r["attack_bend_c"], "f8"),
            },
        )
        loc_arrays = compute_sliding_local_do(
            r["t"],
            r["f"],
            seed_do=cfg["seed_do"],
            max_t_win=cfg["max_t_win"],
            max_t_strike=cfg["max_t_strike"],
        )
        save_npz_pure(cfg["local_do_npz"], loc_arrays)
        do_hz_list = loc_arrays["do_hz"][0]
        c_list = loc_arrays["cents"][0]
        med_do = statistics.median(do_hz_list) if do_hz_list else cfg["seed_do"]
        print(
            f"[saved] {npz_path.name:28s} & {cfg['local_do_npz'].name:20s} "
            f"windows={len(do_hz_list):2d}  mahur_strikes={len(c_list):4d}  med_do={med_do:.2f} Hz"
        )

    print(f"\nDone in {time.time() - t_start:.1f}s.")


if __name__ == "__main__":
    main()

