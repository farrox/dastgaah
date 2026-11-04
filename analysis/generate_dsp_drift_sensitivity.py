#!/usr/bin/env python3
"""Compute Strict Drift Sensitivity across Shur-family second-degree strikes.
Applies:
  - Base gates: conf >= 40.0, robust_wobble (1.4826 * MAD) <= 22.0¢, 100 < f < 950 Hz
  - Relative window: 120.0 <= rel_cents <= 175.0
  - Drift filter: |drift_c_per_s| <= 15.0¢/s
  - Matched input sets: Both unfiltered and filtered peaks are evaluated on the 80.0–220.0¢ range.
  - Computes bootstrap 95% confidence intervals for both unfiltered and filtered peaks.
Generates:
  - analysis/dsp_drift_sensitivity.json
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path so the script can run directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import zipfile
import struct
import math
import json
from analysis.run_rigorous_modal_audit import extract_file_events, kde_peak_location, bootstrap_peak_ci, read_npz

OUT = Path("analysis")

SOURCES = [
    ("Mahmoud Karimi (Vocal)", "analysis/strikes_shur_karimi_vocal.npz", 235.2, "Vocal (Unconstrained)"),
    ("Ali-Akbar Shahnazi (Tar)", "analysis/strikes_shur_shahnazi_tar.npz", 213.2, "Tar (Fretted)"),
    ("Abolhasan Saba (Violin)", "analysis/strikes_shur_saba_violin.npz", 232.8, "Violin (Fretless)"),
    ("Hossein Alizadeh (Tar)", "analysis/strikes_shur_alizadeh_tar.npz", 368.4, "Tar (Fretted)"),
    ("Yousef Foroutan (Setar)", "analysis/strikes_shur_forutan_setar.npz", 311.2, "Setar (Fretted)")
]

def main():
    results = []
    for name, path, default_ist, inst in SOURCES:
        _, nt, thz = extract_file_events(path, default_ist)
        d = read_npz(path)
        fs = d.get('f', d.get('f0', []))
        confs = d.get('conf', [60.0]*len(fs))
        wobs = d.get('wobble_plat_c', [5.0]*len(fs))
        drifts = d.get('drift_c_per_s', [0.0]*len(fs))
        
        cents_unfilt = []
        cents_filt = []
        n_win_pre = 0
        n_win_post = 0
        for f, c, w, dr in zip(fs, confs, wobs, drifts):
            if c >= 40.0 and w <= 22.0 and 100 < f < 950:
                rel = ((1200.0 * math.log2(f / thz) + 600.0) % 1200.0) - 600.0
                if 80.0 <= rel <= 220.0:
                    cents_unfilt.append(rel)
                    if abs(dr) <= 15.0:
                        cents_filt.append(rel)
                if 120.0 <= rel <= 175.0:
                    n_win_pre += 1
                    if abs(dr) <= 15.0:
                        n_win_post += 1
                        
        pk_unfilt, _, _, _ = kde_peak_location(cents_unfilt)
        ci_u_lo, ci_u_hi, _ = bootstrap_peak_ci(cents_unfilt, n_boot=500) if len(cents_unfilt) >= 8 else (None, None, 0.0)
        
        pk_filt, _, _, _ = kde_peak_location(cents_filt)
        ci_f_lo, ci_f_hi, _ = bootstrap_peak_ci(cents_filt, n_boot=500) if len(cents_filt) >= 8 else (None, None, 0.0)
        
        pct = (n_win_post / n_win_pre * 100) if n_win_pre else 0.0
        shift = (pk_filt - pk_unfilt) if (pk_filt is not None and pk_unfilt is not None) else 0.0
        
        ci_u_w = (ci_u_hi - ci_u_lo) if (ci_u_lo is not None and ci_u_hi is not None) else None
        ci_f_w = (ci_f_hi - ci_f_lo) if (ci_f_lo is not None and ci_f_hi is not None) else None
        
        results.append({
            "performer": name,
            "instrument": inst,
            "tonic_hz": round(thz, 1),
            "unfiltered_peak_cents": round(pk_unfilt, 1) if pk_unfilt is not None else None,
            "unfiltered_ci_95": [ci_u_lo, ci_u_hi] if ci_u_lo is not None else None,
            "unfiltered_ci_width": round(ci_u_w, 1) if ci_u_w is not None else None,
            "filtered_peak_cents": round(pk_filt, 1) if pk_filt is not None else None,
            "filtered_ci_95": [ci_f_lo, ci_f_hi] if ci_f_lo is not None else None,
            "filtered_ci_width": round(ci_f_w, 1) if ci_f_w is not None else None,
            "shift_cents": round(shift, 1),
            "n_before": n_win_pre,
            "n_after": n_win_post,
            "pass_rate_pct": round(pct, 1)
        })

    out = {
        "title": "Peak changes under an additional drift gate in four instrumental recordings and one vocal control",
        "filter_condition": "|drift_c_per_s| <= 15.0 c/s",
        "base_filter": "conf >= 40.0, wobble (1.4826 * MAD) <= 22.0 c",
        "candidate_range": "80.0–220.0¢ relative to refined empirical modal tonic (tonic_hz)",
        "description": "Sensitivity test evaluating the shift of second-degree candidate modal peaks when applying an aggressive drift gate (|drift| <= 15.0 c/s) on matched input pools, reporting post-filter bootstrap 95% confidence intervals.",
        "tested_sources": results
    }

    with open(OUT / "dsp_drift_sensitivity.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"Saved {OUT / 'dsp_drift_sensitivity.json'}:")
    for r in results:
        ci_u_str = f"[{r['unfiltered_ci_95'][0]}, {r['unfiltered_ci_95'][1]}]" if r['unfiltered_ci_95'] else "—"
        ci_f_str = f"[{r['filtered_ci_95'][0]}, {r['filtered_ci_95'][1]}]" if r['filtered_ci_95'] else "—"
        print(f"  {r['performer']:25s}: {r['n_before']:3d} -> {r['n_after']:2d} ({r['pass_rate_pct']:4.1f}%), Peak: {r['unfiltered_peak_cents']} {ci_u_str} -> {r['filtered_peak_cents']} {ci_f_str} (Shift: {r['shift_cents']:+4.1f}¢)")

if __name__ == "__main__":
    main()
