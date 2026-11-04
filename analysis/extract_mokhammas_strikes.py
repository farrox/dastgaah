import sys, glob, json, math, os
from pathlib import Path
sys.path.insert(0, 'analysis')
from extract_upgraded_strikes import extract_single_wav, ensure_dylib, save_npz_pure

ensure_dylib()

album_dir = Path("audio/Amir Sharifi/Mokhammas")
wavs = sorted(album_dir.glob("*.wav"))

print(f"Extracting strikes across {len(wavs)} tracks in Mokhammas...")

for w in wavs:
    stem = w.stem
    npz_path = Path(f"analysis/strikes_mokhammas_{stem[:2]}.npz")
    if npz_path.exists():
        print(f"Exists: {npz_path.name}")
        continue
    print(f"Extracting {stem}...")
    res = extract_single_wav(str(w), stem, 100.0, 950.0)
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

print("All Mokhammas tracks extracted!")
