import os
import sys
import glob
import numpy as np
import json
import subprocess

sys.path.insert(0, os.path.abspath("."))
from analysis.batch_pitch_extract import extract_single_wav

# The 5 secondary avazes datasets
avaz_dirs = {
    "abuata": [
        "audio/YouTube Music/Ali-Akbar Shahnazi/The Advanced Shahnazi Radif I/*Abuata*.wav",
        "audio/YouTube Music/Mahmud Karimi/Abuata/*.wav",
        "audio/YouTube Music/Yusef Forutan/Radif Setar - Shur/*Abuata*.wav",
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

print("5-Avaz Pipeline script configured.")
