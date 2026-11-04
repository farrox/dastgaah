import os
import sys
import numpy as np
import json
from pathlib import Path

OUT = Path("analysis")
AVAZES = ["abuata", "bayat_tork", "afshari", "dashti", "bayat_kord"]

# Expected modal structures relative to base Shur Tonic (Do = 0c)
# Base Shur: Do (0c), Re-koron (~139c), Mib (~294c), Fa (~498c), Sol (~702c), La-koron (~841c), Sib (~996c), Do' (1200c)

results = {}

for av in AVAZES:
    npz_path = OUT / f"strikes_avaz_{av}.npz"
    if not npz_path.exists():
        print(f"Missing {npz_path}")
        continue
    data = np.load(npz_path)
    freqs = data["f"]
    confs = data["conf"]
    tracks = data["track"]

    # Filter by high confidence
    mask = confs >= 50.0
    valid_f = freqs[mask]
    valid_c = confs[mask]
    valid_tr = tracks[mask]

    print(f"\n=======================================================")
    print(f"AVAZ: {av.upper()} (Strikes: {len(freqs)} raw, {len(valid_f)} conf>=50)")
    print(f"=======================================================")

    # Frequency histogram to detect prominent modal peaks
    # We use a log-spaced pitch grid
    # Let's inspect the distribution across octaves by wrapping to chromatic pitch classes relative to median
    f_med = float(np.median(valid_f))
    print(f"Median f0: {f_med:.2f} Hz")
    
    # Let's compute cents relative to tonic (we will find the cluster peaks)
    cents_rel = 1200.0 * np.log2(valid_f / f_med)
    # wrap mod 1200 into [-600, +600]
    cents_wrapped = (cents_rel + 600.0) % 1200.0 - 600.0

    # Kernel density estimation / histogram in cents
    bins = np.linspace(-600, 600, 241) # 5 cent bins
    counts, edges = np.histogram(cents_wrapped, bins=bins)
    centers = 0.5 * (edges[:-1] + edges[1:])

    # Find top 7 peaks (scale degrees)
    from scipy.signal import find_peaks
    peaks, props = find_peaks(counts, distance=14, prominence=max(counts)*0.08)
    sorted_peaks = sorted(peaks, key=lambda p: counts[p], reverse=True)[:8]
    peak_cents = sorted([centers[p] for p in sorted_peaks])

    print("Prominent modal pitch centers (wrapped cents rel to median):")
    for pc in peak_cents:
        idx = np.argmin(np.abs(centers - pc))
        print(f"  {pc:+6.1f} cents (weight: {counts[idx]})")

    results[av] = {
        "raw_strikes": int(len(freqs)),
        "high_conf_strikes": int(len(valid_f)),
        "median_hz": f_med,
        "peak_cents": [float(pc) for pc in peak_cents]
    }

with open(OUT / "five_avazes_consensus.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nSummary saved to analysis/five_avazes_consensus.json")
