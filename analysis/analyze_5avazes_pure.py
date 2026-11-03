import math
import json
import statistics
from pathlib import Path
import sys

sys.path.insert(0, "analysis")
from load_npz_pure import load_npz_pure

OUT = Path("analysis")
AVAZES = ["abuata", "bayat_tork", "afshari", "dashti", "bayat_kord"]

# Degree naming for Persian modes relative to Dastgah-e Shur on Do (0c):
# Degree 1: Tonic / Finalis (Do, 0c)
# Degree 2: Neutral Second (Re-koron, ~140c)
# Degree 3: Minor Third (Mib, ~295c)
# Degree 4: Perfect Fourth (Fa, ~498c)
# Degree 5: Perfect Fifth (Sol, ~702c) or Motaghayyer / neutral fifth
# Degree 6: Neutral Sixth (La-koron, ~840c)
# Degree 7: Subtonic / Minor Seventh (Sib, ~996c)
# Degree 8: Octave (Do', 1200c)

results = {}

for av in AVAZES:
    npz_path = OUT / f"strikes_avaz_{av}.npz"
    if not npz_path.exists():
        continue
    data = load_npz_pure(npz_path)
    f_list = data["f"]
    conf_list = data["conf"]
    tr_list = data["track"]

    # Filter conf >= 50.0
    valid = [(f, c, tr) for f, c, tr in zip(f_list, conf_list, tr_list) if c >= 50.0]
    if not valid:
        continue

    v_f = [v[0] for v in valid]
    v_c = [v[1] for v in valid]
    f_med = statistics.median(v_f)

    # Convert to cents relative to f_med wrapped to [-600, +600]
    cents = []
    for f in v_f:
        c = 1200.0 * math.log2(f / f_med)
        cw = (c + 600.0) % 1200.0 - 600.0
        cents.append(cw)

    # Histogram 5-cent bins
    bins = [ -600.0 + i * 5.0 for i in range(241) ]
    counts = [0] * (len(bins) - 1)
    for c in cents:
        idx = int((c + 600.0) / 5.0)
        if 0 <= idx < len(counts):
            counts[idx] += 1

    centers = [ 0.5 * (bins[i] + bins[i+1]) for i in range(len(counts)) ]

    # Simple peak finder
    peaks = []
    max_c = max(counts) if counts else 1
    for i in range(2, len(counts) - 2):
        if counts[i] > 0.08 * max_c:
            if counts[i] > counts[i-1] and counts[i] > counts[i+1] and counts[i] >= counts[i-2] and counts[i] >= counts[i+2]:
                peaks.append((centers[i], counts[i]))

    # Merge nearby peaks (< 25c)
    merged_peaks = []
    for p, cnt in sorted(peaks, key=lambda x: x[1], reverse=True):
        if not any(abs(p - mp[0]) < 25.0 for mp in merged_peaks):
            merged_peaks.append((p, cnt))

    merged_peaks.sort(key=lambda x: x[0])

    print(f"\n=======================================================")
    print(f"AVAZ: {av.upper()} (Strikes: {len(f_list)} raw, {len(v_f)} conf>=50)")
    print(f"Median Pitch: {f_med:.2f} Hz")
    print(f"Prominent Cent Peaks (relative to cluster median):")
    for p, cnt in merged_peaks:
        print(f"  {p:+6.1f}¢ (weight={cnt})")

    results[av] = {
        "raw_strikes": len(f_list),
        "high_conf_strikes": len(v_f),
        "median_hz": f_med,
        "peaks": [{"cent": round(p, 1), "weight": cnt} for p, cnt in merged_peaks]
    }

with open(OUT / "five_avazes_empirical_consensus.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nSaved empirical consensus to analysis/five_avazes_empirical_consensus.json")
