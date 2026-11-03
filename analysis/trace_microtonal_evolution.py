import math
import json
import statistics
from pathlib import Path
import sys

sys.path.insert(0, "analysis")
from load_npz_pure import load_npz_pure

OUT = Path("analysis")

masters = [
    ("Aqa Hoseyn-Qoli (1907-1912)", "strikes_historical_epoch1_qajar_aqa_hoseyn_qoli.npz", 1909),
    ("Darvish Khan (1906-1914)", "strikes_historical_epoch1_qajar_darvish_khan.npz", 1910),
    ("Qajar Tar Anthology (1906-1925)", "strikes_historical_epoch1_qajar_tar_anthology.npz", 1915),
    ("Abolhasan Saba (1950s)", "strikes_historical_epoch2_mid_saba_setar.npz", 1952),
    ("Yousef Foroutan (1960s-1970s)", "strikes_historical_epoch2_mid_foroutan_setar.npz", 1968),
    ("Saeed Hormozi (1970s)", "strikes_historical_epoch2_mid_hormozi_tar_setar.npz", 1974),
    ("Century of Tar / Modern Masters", "strikes_historical_epoch3_century_tar_anthology.npz", 1995),
]

summary = []

for label, fname, approx_year in masters:
    p = OUT / fname
    if not p.exists():
        continue
    data = load_npz_pure(p)
    valid_f = [f for f, c in zip(data["f"], data["conf"]) if c >= 50.0]
    if not valid_f:
        continue
    med_f = statistics.median(valid_f)
    
    # Compute relative cents distribution mod 1200
    cents = []
    for f in valid_f:
        c = 1200.0 * math.log2(f / med_f)
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
    
    # Find top peaks
    peaks = []
    max_c = max(counts) if counts else 1
    for i in range(2, len(counts) - 2):
        if counts[i] > 0.12 * max_c:
            if counts[i] > counts[i-1] and counts[i] > counts[i+1] and counts[i] >= counts[i-2] and counts[i] >= counts[i+2]:
                peaks.append((centers[i], counts[i]))
                
    merged_peaks = []
    for pk, cnt in sorted(peaks, key=lambda x: x[1], reverse=True):
        if not any(abs(pk - mp[0]) < 25.0 for mp in merged_peaks):
            merged_peaks.append((pk, cnt))
    merged_peaks.sort(key=lambda x: x[0])
    
    print(f"[{label}] Year: ~{approx_year} | Strikes: {len(valid_f):,} | Med F0: {med_f:.1f} Hz")
    peak_str = ", ".join([f"{p[0]:+.1f}¢" for p in merged_peaks[:6]])
    print(f"  Dominant Intervals: {peak_str}")
    summary.append({
        "master": label,
        "year": approx_year,
        "strikes": len(valid_f),
        "median_f0": round(med_f, 1),
        "peaks": [round(p[0], 1) for p in merged_peaks]
    })

with open(OUT / "historical_masters_interval_summary.json", "w") as f:
    json.dump(summary, f, indent=2)
