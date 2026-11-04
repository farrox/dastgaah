import sys, glob, json, math, os
from pathlib import Path
sys.path.insert(0, 'analysis')
from extract_upgraded_strikes import extract_single_wav, ensure_dylib, save_npz_pure

ensure_dylib()

tracks = [
    ("Aqa Hoseyn-Qoli (Segah Daramad)", "audio/YouTube Music/Historical Anthologies/Tar - Aqa Hoseyn-Qoli/12 - Dastgah-e Segah.wav"),
    ("Aqa Hoseyn-Qoli (Segah Zabol & Hesar)", "audio/YouTube Music/Historical Anthologies/Tar - Aqa Hoseyn-Qoli/13 - Dastgah-e Segah Zabol & Hesar.wav"),
    ("Aqa Hoseyn-Qoli (Segah Mokhalef)", "audio/YouTube Music/Historical Anthologies/Tar - Aqa Hoseyn-Qoli/14 - Dastgah-e Segah Mokhalef.wav")
]

results = {}

for label, p in tracks:
    stem = Path(p).stem
    npz_path = Path(f"analysis/strikes_qajar_{stem[:2]}.npz")
    print(f"Extracting {label} ({stem})...")
    res = extract_single_wav(p, stem, 100.0, 950.0)
    print(f"  Strikes: {len(res['f'])}")
    npz_data = {
        "t": (res["t"], "f8"),
        "f": (res["f"], "f8"),
        "conf": (res["conf"], "f8"),
        "wobble_plat_c": (res["wobble_plat_c"], "f8"),
        "wobble_sus_c": (res["wobble_sus_c"], "f8"),
        "drift_c_per_s": (res["drift_c_per_s"], "f8"),
        "attack_bend_c": (res["attack_bend_c"], "f8"),
    }
    save_npz_pure(npz_path, npz_data)
    results[label] = {
        "f": res["f"],
        "conf": res["conf"]
    }

print("All Aqa Hoseyn-Qoli Segah tracks extracted!")
