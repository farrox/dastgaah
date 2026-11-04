import subprocess, sys, os
from pathlib import Path
sys.path.insert(0, 'analysis')
from extract_upgraded_strikes import extract_single_wav, ensure_dylib, save_npz_pure

ensure_dylib()

# Tracks 10, 11, 12 in Qajar Santour album are Taherzadeh & Rezagholikhan Abuata!
indir = Path("audio/Qajar_Santour_and_Vocal_78RPM_1906_1909")
targets = [
    ("10 - Avaz Taherzadeh Abuata.wav", "taherzadeh_1906_abuata_santour_1"),
    ("11 - Avaz Taherzadeh Abuata.wav", "taherzadeh_1906_abuata_santour_2"),
    ("12 - Avaz Rezagholikhan Abuata.wav", "rezagholikhan_1906_abuata_santour")
]

print("Extracting strikes for 1906 Qajar Abuata tracks (Taherzadeh & Rezagholikhan with Santour)...")
for fname, tag in targets:
    w = indir / fname
    if not w.exists():
        print(f"Missing {fname}")
        continue
    npz_path = Path(f"analysis/strikes_{tag}.npz")
    if npz_path.exists():
        print(f"Exists: {npz_path.name}")
        continue
    print(f"Extracting {tag}...")
    res = extract_single_wav(str(w), tag, 110.0, 950.0)
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

print("Extraction of 1906 Qajar Abuata finished!")
