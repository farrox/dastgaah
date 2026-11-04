import os
import sys
import glob
import numpy as np
import json
import time

sys.path.insert(0, os.path.abspath("."))
from analysis.batch_pitch_extract import extract_single_wav

# The 5 secondary avazes
datasets = {
    "abuata": [
        "audio/YouTube Music/Ali-Akbar Shahnazi/The Advanced Shahnazi Radif I/*Abuata*.wav",
        "audio/YouTube Music/Mahmud Karimi/Abuata/*.wav",
    ],
    "bayat_tork": [
        "audio/YouTube Music/Nur-Ali Borumand/Bayat Tork/*.wav",
        "audio/YouTube Music/Mahmud Karimi/Bayat Tork/*.wav",
        "audio/YouTube Music/Ali-Akbar Shahnazi/The Advanced Shahnazi Radif I/*Tork*.wav",
    ],
    "afshari": [
        "audio/YouTube Music/Saeed Hormozi/Setar - Afshari Solo/*.wav",
        "audio/YouTube Music/Nur-Ali Borumand/Afshari/*.wav",
        "audio/YouTube Music/Mahmud Karimi/Afshari/*.wav",
        "audio/YouTube Music/Ali-Akbar Shahnazi/The Advanced Shahnazi Radif III/*Afshari*.wav",
    ],
    "dashti": [
        "audio/YouTube Music/Ali-Akbar Shahnazi/Radif Tar - Dashti/*.wav",
        "audio/YouTube Music/Mahmud Karimi/Vocal Radif - Dashti/*.wav",
        "audio/YouTube Music/Hossein Alizadeh/Radif Navazi - Dashti/*.wav",
        "audio/YouTube Music/Abolhasan Saba/Dashti Solo/*.wav",
        "audio/YouTube Music/Mohammad Reza Lotfi/Dashti Solo/*.wav",
        "audio/YouTube Music/Hassan Kasaei/Radifs 4 - Dashti/*.wav",
        "audio/YouTube Music/Aliakbar Shekarchi/Radif Kamancheh - Dashti/*.wav",
        "audio/YouTube Music/Ahmad Ebadi/Setar Solo - Dashti/*.wav",
    ],
    "bayat_kord": [
        "audio/YouTube Music/Nur-Ali Borumand/Kord-e Bayat/*.wav",
        "audio/YouTube Music/Hossein Alizadeh/The Art Of Improvisation - Rast-Panjgah/15 - Avaz-E Bayat-E Kord.wav",
    ]
}

def collect_wavs(patterns):
    wavs = []
    for pat in patterns:
        wavs.extend(glob.glob(pat))
    return sorted(list(set(wavs)))

all_results = {}
total_strikes_all = 0
start_time = time.time()

for mode_name, patterns in datasets.items():
    wavs = collect_wavs(patterns)
    print(f"\n=======================================================")
    print(f"Processing mode: {mode_name.upper()} ({len(wavs)} wav files)")
    print(f"=======================================================")
    
    mode_strikes = []
    mode_energies = []
    mode_sources = []
    
    for w in wavs:
        try:
            strikes = extract_single_wav(w, mode=mode_name)
            if len(strikes) > 0:
                print(f"  {os.path.basename(w)}: {len(strikes)} strikes")
                mode_strikes.extend([s['f0'] for s in strikes])
                mode_energies.extend([s['energy'] for s in strikes])
                mode_sources.extend([os.path.basename(w)] * len(strikes))
        except Exception as e:
            print(f"  Error on {w}: {e}")
            
    n_strikes = len(mode_strikes)
    total_strikes_all += n_strikes
    print(f"Total strikes for {mode_name}: {n_strikes}")
    
    # Save npz cache
    npz_path = f"analysis/strikes_avaz_{mode_name}.npz"
    np.savez_compressed(
        npz_path,
        f0=np.array(mode_strikes, dtype=np.float32),
        energy=np.array(mode_energies, dtype=np.float32),
        sources=np.array(mode_sources)
    )
    all_results[mode_name] = {
        "num_files": len(wavs),
        "total_strikes": n_strikes,
        "npz_cache": npz_path
    }

elapsed = time.time() - start_time
print(f"\nAll 5 Avazes extracted in {elapsed:.1f}s. Grand Total Strikes: {total_strikes_all}")
with open("analysis/five_avazes_summary.json", "w") as f:
    json.dump(all_results, f, indent=2)
