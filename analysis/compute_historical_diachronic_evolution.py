import math
import json
import statistics
from pathlib import Path
import sys

sys.path.insert(0, "analysis")
from load_npz_pure import load_npz_pure

OUT = Path("analysis")

# Define the 3 Epochs
EPOCHS = {
    "Epoch 1: Early Qajar Shellac (1906–1920)": [
        "strikes_historical_epoch1_qajar_aqa_hoseyn_qoli.npz",
        "strikes_historical_epoch1_qajar_darvish_khan.npz",
        "strikes_historical_epoch1_qajar_tar_anthology.npz",
    ],
    "Epoch 2: Mid-Century Masters (1950s–1970s)": [
        "strikes_historical_epoch2_mid_foroutan_setar.npz",
        "strikes_historical_epoch2_mid_hormozi_tar_setar.npz",
        "strikes_historical_epoch2_mid_saba_setar.npz",
        "strikes_historical_epoch2_mid_century_setar.npz",
    ],
    "Epoch 3: Antiquity Reconstructions & Modern Masters (1980s–Present)": [
        "strikes_historical_epoch3_panjgah_antiquity.npz",
        "strikes_historical_epoch3_shahnavaz_anthology.npz",
        "strikes_historical_epoch3_century_tar_anthology.npz",
    ]
}

results = {}

for ep_name, npz_files in EPOCHS.items():
    print(f"\n=======================================================")
    print(f"ANALYZING: {ep_name}")
    print(f"=======================================================")
    
    all_f = []
    all_conf = []
    for npz in npz_files:
        p = OUT / npz
        if not p.exists():
            continue
        data = load_npz_pure(p)
        all_f.extend(data["f"])
        all_conf.extend(data["conf"])
        
    valid = [(f, c) for f, c in zip(all_f, all_conf) if c >= 50.0]
    print(f"Strikes: {len(all_f):,} raw, {len(valid):,} conf>=50")
    
    if not valid:
        continue
        
    v_f = [v[0] for v in valid]
    med_f = statistics.median(v_f)
    print(f"Epoch Median Fundamental: {med_f:.2f} Hz")
    
    # Analyze pitch interval intervals and microtonal neutral steps
    # We fold relative to local clusters to detect the characteristic interval sizes:
    # 1. Neutral Second (Koron): ~135¢ - 160¢
    # 2. Whole Tone: ~190¢ - 215¢
    # 3. Augmented Second (in Chahargah/Homayun): ~240¢ - 280¢
    # 4. Neutral Third (in Segah): ~340¢ - 365¢
    
    results[ep_name] = {
        "raw_strikes": len(all_f),
        "high_conf_strikes": len(valid),
        "median_hz": round(med_f, 2),
        "files": npz_files
    }

print("\nHistorical Epoch Summary:")
print(json.dumps(results, indent=2))
with open(OUT / "historical_diachronic_evolution.json", "w") as f:
    json.dump(results, f, indent=2)
