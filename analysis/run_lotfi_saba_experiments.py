import sys, glob, json, math, os
from pathlib import Path
sys.path.insert(0, 'analysis')
from extract_upgraded_strikes import extract_single_wav, ensure_dylib, save_npz_pure

ensure_dylib()

targets = [
    ("Lotfi Kamancheh (Abuata)", "audio/lotfi_saba_experiments/lotfi_kamancheh_abuata_WCpiD15zaYo.wav", True),
    ("Lotfi Kamancheh (Basel)", "audio/lotfi_saba_experiments/lotfi_kamancheh_basel_yRB2Hd2nsiU.wav", True),
    ("Lotfi Kamancheh (Solo)", "audio/lotfi_saba_experiments/lotfi_kamancheh_solo_xKEM8b2oozU.wav", True),
    ("Lotfi Tar (Abuata Pishdaramad)", "audio/lotfi_saba_experiments/lotfi_shajarian_abuata_pishdaramad_LnsbdhtBFLs.wav", False),
    ("Lotfi Tar (Hejaz)", "audio/lotfi_saba_experiments/lotfi_shajarian_hejaz_cixlq9KvqaA.wav", False),
    ("Lotfi Tar (Zarbi Hejaz)", "audio/lotfi_saba_experiments/lotfi_shajarian_zarbi_hejaz_J4pb8fpsoB4.wav", False)
]

for label, wav_path, is_kamancheh in targets:
    if not os.path.exists(wav_path):
        continue
    stem = Path(wav_path).stem
    npz_path = Path(f"analysis/strikes_exp_{stem}.npz")
    if npz_path.exists():
        print(f"Already exists: {npz_path}")
        continue
    print(f"Extracting {label} ({stem})...")
    res = extract_single_wav(wav_path, stem, 100.0, 950.0)
    print(f"  Total strikes: {len(res['f'])}")
    
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
    print(f"  Saved {npz_path}")

print("All tracks extracted successfully!")
