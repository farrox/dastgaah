#!/usr/bin/env python3
"""
Inspect pitch distributions and modal intervals for the newly extracted historical masters.
"""
import numpy as np

NPZ_FILES = [
    ("Habib Sama'i (Santur 1930s)", "analysis/strikes_habib_samai_santur.npz"),
    ("Gholam-Hossein Bigjekhani (Tar - Tabriz)", "analysis/strikes_bigjekhani_tar.npz"),
    ("Jalil Shahnaz (Tar - Isfahan)", "analysis/strikes_jalil_shahnaz_tar.npz"),
    ("Faramarz Payvar (Santur)", "analysis/strikes_faramarz_payvar_santur.npz"),
    ("Early Shellac Masters (1907-1912)", "analysis/strikes_early_masters_shellac.npz")
]

for label, p in NPZ_FILES:
    d = np.load(p)
    f, conf, trk = d["f"], d["conf"], d["track"]
    print(f"==================================================")
    print(f"{label}: {len(f):,} strikes across {len(set(trk))} tracks")
    print(f"Median conf: {np.median(conf):.1f}")
    
    # List unique tracks and strike count
    u_trks, counts = np.unique(trk, return_counts=True)
    for t, c in zip(u_trks, counts):
        sub_f = f[trk == t]
        med_f = np.median(sub_f)
        print(f"  - {t[:35]:<35s} : {c:4d} strikes, med={med_f:.1f} Hz")

