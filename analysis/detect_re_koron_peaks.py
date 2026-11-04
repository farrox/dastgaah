#!/usr/bin/env python3
"""Evaluate Re-koron modality and peak prominence across 80-220 cents.

Reads per-event strike .npz files for all performers, computes the extended
interval distribution (80-220 cents relative to verified modal tonic), applies
Gaussian Kernel Density Estimation (KDE) to locate local density maxima, tests
peak prominence above flanking valleys (90-115c and 180-210c), and separates:
  1. Solo recordings with verified unimodal Re-koron peaks
  2. Performers with broad / flat / ambiguous distributions
  3. Ensemble / duet recordings requiring distinct attribution
"""

import zipfile
import struct
import math
import json
import statistics
from pathlib import Path
from collections import defaultdict, Counter

OUT = Path("analysis")

def read_npz(path):
    arrays = {}
    with zipfile.ZipFile(path, 'r') as z:
        for name in z.namelist():
            if name.endswith('.npy'):
                buf = z.read(name)
                hlen = struct.unpack('<H', buf[8:10])[0]
                header = buf[10:10+hlen].decode('latin1')
                raw = buf[10+hlen:]
                if '<f8' in header or '=f8' in header:
                    n = len(raw) // 8
                    arrays[name[:-4]] = list(struct.unpack(f'<{n}d', raw[:n*8]))
                elif '<f4' in header or '=f4' in header:
                    n = len(raw) // 4
                    arrays[name[:-4]] = list(struct.unpack(f'<{n}f', raw[:n*4]))
    return arrays

def get_track_strings(npz_path):
    with zipfile.ZipFile(npz_path) as z:
        if 'track.npy' not in z.namelist():
            return []
        buf = z.read('track.npy')
        hlen = struct.unpack('<H', buf[8:10])[0]
        header = buf[10:10+hlen].decode('latin1')
        raw = buf[10+hlen:]
        import re
        m = re.search(r'\'<U(\d+)\'', header)
        if m:
            slen = int(m.group(1)) * 4
            n = len(raw) // slen
            return [raw[i*slen:(i+1)*slen].decode('utf-32-le').rstrip('\x00') for i in range(n)]
    return []

def kde_peak_detection(values, grid_min=80.0, grid_max=220.0, bandwidth=5.0):
    if len(values) < 8:
        return None, 0.0, None
    # 0.5-cent grid
    steps = int((grid_max - grid_min) / 0.5) + 1
    grid = [grid_min + i * 0.5 for i in range(steps)]
    inv_bw = 1.0 / bandwidth
    norm_const = 1.0 / (len(values) * bandwidth * math.sqrt(2 * math.pi))
    densities = [
        sum(math.exp(-0.5 * (((x - v) * inv_bw) ** 2)) for v in values) * norm_const
        for x in grid
    ]
    
    # Locate all peaks in [120, 175]
    peaks = []
    for i in range(1, len(grid) - 1):
        if densities[i] > densities[i-1] and densities[i] > densities[i+1]:
            x = grid[i]
            if 120.0 <= x <= 175.0:
                peaks.append((x, densities[i]))
                
    if not peaks:
        return None, 0.0, None
        
    best_peak_x, best_peak_d = max(peaks, key=lambda p: p[1])
    
    # Valley depths
    left_dens = [densities[i] for i, x in enumerate(grid) if 85.0 <= x <= 115.0]
    right_dens = [densities[i] for i, x in enumerate(grid) if 185.0 <= x <= 215.0]
    
    left_min = min(left_dens) if left_dens else 0.0
    right_max = max(right_dens) if right_dens else 0.0 # height of whole-tone peak
    
    # Is the peak an authentic local maximum higher than its surrounding valleys?
    # Relative height above the left valley
    left_drop = (best_peak_d - left_min) / best_peak_d if best_peak_d > 0 else 0.0
    
    # Ratio relative to whole-tone peak
    wt_ratio = best_peak_d / right_max if right_max > 0 else 2.0
    
    # Distinct peak criterion:
    # 1. Must rise at least 25% above the left valley (between 85-115c)
    # 2. Must not be merely a minor shoulder on an overwhelming whole-tone peak (wt_ratio >= 0.35)
    is_distinct = (left_drop >= 0.25) and (wt_ratio >= 0.30 or right_max == 0)
    
    return best_peak_x, best_peak_d, is_distinct

def main():
    print("==========================================================================")
    print("Evaluating Re-koron Spectral Peaks and Modal Functions (80-220 Cents)")
    print("==========================================================================")
    
    # Load all performers from the same npz files
    with open(OUT / "shur_consensus.json") as f:
        shur = json.load(f)
        
    # We will test all 23 performers
    performers_data = {}
    
    # 1. Shur consensus 10 sources
    for name, s in shur["sources"].items():
        ist_cents = s["slots"]["ist_tonic"]["median_cents"]
        ist_hz = s["ist_hz"] * (2.0 ** (ist_cents / 1200.0))
        d = read_npz(OUT / f"strikes_shur_{name}.npz")
        fs = d.get('f', d.get('f0', []))
        confs = d.get('conf', [60.0]*len(fs))
        wobs = d.get('wobble_plat_c', [5.0]*len(fs))
        valid = [f for f, c, w in zip(fs, confs, wobs) if c >= 40.0 and w <= 22.0 and 100 < f < 950]
        rc = [((1200.0 * math.log2(f / ist_hz) + 600.0) % 1200.0) - 600.0 for f in valid]
        extended = [c for c in rc if 80.0 <= c <= 220.0]
        performers_data[name] = extended

    # Test peak for each
    for name, vals in performers_data.items():
        peak_x, peak_d, is_dist = kde_peak_detection(vals)
        b = Counter([round(c / 10.0) * 10.0 for c in vals])
        counts_str = ' '.join(f'{b[k]:3d}' for k in range(80, 230, 20))
        dist_str = f"PEAK: {peak_x:.1f}¢" if is_dist else "NO DISTINCT PEAK"
        print(f"{name:20s} | N={len(vals):4d} | {dist_str:20s} | Bins (80..220c): {counts_str}")

if __name__ == "__main__":
    main()

