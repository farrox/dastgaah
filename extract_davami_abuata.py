import sys, os
from pathlib import Path
sys.path.insert(0, 'analysis')
from extract_upgraded_strikes import extract_single_wav, ensure_dylib, save_npz_pure

ensure_dylib()

# Tracks 11 to 16 in Davami Vol 1 are Abuata
indir = Path("audio/Abdollah_Davami_Vocal_Radif/Vol_1")
abuata_wavs = sorted(indir.glob("*Abuata*"))

print(f"Extracting pitch strikes across {len(abuata_wavs)} Davami Abuata tracks...")
for w in abuata_wavs:
    stem = w.stem
    npz_path = Path(f"analysis/strikes_davami_{stem}.npz")
    if npz_path.exists():
        print(f"Exists: {npz_path.name}")
        continue
    print(f"Extracting {stem}...")
    res = extract_single_wav(str(w), stem, 110.0, 750.0)
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

print("All Davami Abuata tracks extracted!")
