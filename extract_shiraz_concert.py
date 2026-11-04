import sys, os
from pathlib import Path
sys.path.insert(0, 'analysis')
from extract_upgraded_strikes import extract_single_wav, ensure_dylib, save_npz_pure

ensure_dylib()

wav_path = Path("audio/Shiraz_Arts_Festival_1970s/Shiraz_Festival_Abuata_Taj_Shahnaz_Kasaei.wav")
npz_path = Path("analysis/strikes_shiraz_festival_abuata.npz")

print("Extracting strikes across the complete Shiraz Arts Festival Abuata Concert (172 MB WAV)...")
res = extract_single_wav(str(wav_path), "shiraz_festival_abuata", 110.0, 950.0)
print(f"  Extracted {len(res['f'])} total strikes across Vocal (Taj), Tar (Shahnaz), and Ney (Kasaei).")

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
print("Saved to analysis/strikes_shiraz_festival_abuata.npz")
