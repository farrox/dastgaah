import sys, os
from pathlib import Path
sys.path.insert(0, 'analysis')
from extract_upgraded_strikes import extract_single_wav, ensure_dylib, save_npz_pure

ensure_dylib()

wav_path = Path("audio/Abolhasan Saba/Violin_Vol_3/Saba_Dastgah_Segah_Violin_Vol3.wav")
npz_path = Path("analysis/strikes_saba_segah_violin_vol3.npz")

print(f"Extracting strikes for Saba Segah Violin (22 minutes)...")
# Violin spans ~196 Hz (G3) to 1200 Hz
res = extract_single_wav(str(wav_path), "saba_segah_violin_vol3", 150.0, 1100.0)
print(f"  Extracted {len(res['f'])} note strikes/events.")

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
print("Saved to analysis/strikes_saba_segah_violin_vol3.npz")
