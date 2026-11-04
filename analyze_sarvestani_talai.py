import numpy as np
import subprocess, os, json
from pathlib import Path

# Load pitch extraction DSP
import sys
sys.path.append('.')
from test_c_dsp import extract_single_wav

vocal_dir = Path("audio/Sarvestani_Talai_Vocal_Radif")
wav_files = sorted(list(vocal_dir.glob("*.wav")))

print(f"Found {len(wav_files)} Sarvestani & Talai vocal radif tracks:")
for w in wav_files:
    print(f"  - {w.name} ({w.stat().st_size / 1e6:.1f} MB)")

results = {}

for wav in wav_files:
    stem = wav.stem
    print(f"\nProcessing {stem}...")
    try:
        # Vocal + Tar spans ~120 Hz to 800 Hz
        times, freqs, confs, pitches, energies = extract_single_wav(str(wav), f"sarvestani_{stem}", 110.0, 850.0)
        
        # Filter confident pitches
        mask = (confs > 0.6) & (energies > -40.0) & (pitches > 115.0) & (pitches < 800.0)
        valid_pitches = pitches[mask]
        
        if len(valid_pitches) < 100:
            print(f"  Warning: Only {len(valid_pitches)} valid frames found.")
            continue
            
        print(f"  Extracted {len(valid_pitches)} confident frames.")
        
        # Kernel density estimation or histogram on log pitch to find peaks
        log_p = np.log2(valid_pitches)
        # Compute histogram with fine bins (5 cents)
        hist, bin_edges = np.histogram(log_p, bins=1000)
        bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
        
        # Find dominant peak (Shahed / Base)
        # Smoothed histogram
        from scipy.ndimage import gaussian_filter1d
        smooth = gaussian_filter1d(hist.astype(float), sigma=3)
        
        # Peak finding
        from scipy.signal import find_peaks
        peaks, props = find_peaks(smooth, distance=15, prominence=np.max(smooth)*0.05)
        peak_freqs = 2**bin_centers[peaks]
        peak_counts = smooth[peaks]
        
        # Sort peaks by count
        sorted_indices = np.argsort(peak_counts)[::-1]
        top_peaks = peak_freqs[sorted_indices][:8]
        top_counts = peak_counts[sorted_indices][:8]
        
        results[stem] = {
            "total_frames": int(len(valid_pitches)),
            "top_peaks_hz": [float(round(p, 1)) for p in top_peaks],
            "top_counts": [float(round(c, 1)) for c in top_counts]
        }
        print(f"  Top peaks (Hz): {[round(p, 1) for p in top_peaks]}")
        
    except Exception as e:
        print(f"  Error processing {stem}: {e}")

with open("analysis/sarvestani_talai_peaks.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nAnalysis saved to analysis/sarvestani_talai_peaks.json")
