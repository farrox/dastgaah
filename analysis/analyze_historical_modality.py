#!/usr/bin/env python3
"""
Analyze modal intervals in Habib Samai and Bigjekhani Shur recordings to test the Koron and Minor 3rd.
"""
import numpy as np

def analyze_track(npz_path, track_name, ist_hz):
    d = np.load(npz_path)
    mask = (d["track"] == track_name)
    f = d["f"][mask]
    cents = 1200.0 * np.log2(f / ist_hz)
    cents_mod = cents % 1200.0
    
    print(f"\n--- Track: {track_name} (Tonic: {ist_hz:.1f} Hz, Strikes: {len(f)}) ---")
    slots = [
        ("Zir-e Ist (7th)", -200, 45),
        ("Ist (Tonic)", 0, 40),
        ("Koron (2nd)", 140, 50),
        ("Minor 3rd", 300, 45),
        ("4th (Fa)", 500, 45),
        ("5th (Sol)", 700, 45),
        ("Koron (6th)", 840, 50),
        ("7th (Si b)", 1000, 45),
        ("Octave", 1200, 40)
    ]
    for name, target, tol in slots:
        # Wrap cents around target
        diff = (cents - target + 600) % 1200 - 600
        in_slot = cents[np.abs(diff) <= tol]
        if len(in_slot) >= 5:
            med_val = np.median(in_slot)
            std_val = np.std(in_slot)
            print(f"  {name:18s} : target={target:6.1f}c | median={med_val:6.1f}c | std={std_val:4.1f}c | n={len(in_slot):3d}")

# Habib Samai Shur 01
analyze_track("analysis/strikes_habib_samai_santur.npz", "01_shur", ist_hz=429.0)

# Bigjekhani Shur
analyze_track("analysis/strikes_bigjekhani_tar.npz", "dastgah_shur_1", ist_hz=293.0)

# Agha Hossein-Qoli Mahur
analyze_track("analysis/strikes_early_masters_shellac.npz", "agha_hossein_qoli_mahur_1", ist_hz=293.7)

