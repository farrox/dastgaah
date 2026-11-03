#!/usr/bin/env python3
"""Cross-instrument empirical consensus for Dastgah-e Rast-Panjgah across 12 canonical masters.

In Dastgah-e Rast-Panjgah:
- Base scale mirrors Mahur (Do = 1/1, 0.0c):
  - Tonic (Do): 0.0c
  - 2nd (Re): +203.9c (9/8 major 2nd)
  - 3rd (Mi): +407.8c (81/64 ditone) vs +386.3c (5/4 just 3rd)
  - 4th (Fa): +498.0c (4/3 pure 4th)
  - 5th (Sol - Panjgah / Shahed): +702.0c (3/2 pure 5th)
  - 6th (La): +905.9c (27/16 pyth major 6th)
  - 7th (Si): +1109.8c (243/128 leading tone)
  - Octave (Do'): +1200.0c (2/1)

- Modulatory Gūsheh Centers (The Grand Tour of Dastgahs):
  - Oshshaq: Introduces neutral step towards Isfahan/Homayun (La Koron ~841c)
  - Neyriz: Minor 3rd & neutral shifts
  - Sepehr: Climax modulations
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_upgraded_strikes import OUT

RAST_PANJGAH_MASTERS = {
    "alizadeh_tar_setar": {"fretless": False, "category": "tar_setar", "lineage": "modern"},
    "shahnazi_tar": {"fretless": False, "category": "tar", "lineage": "qajar_radif"},
    "karimi_vocal": {"fretless": True, "category": "voice", "lineage": "canonical"},
    "borumand_tar_setar": {"fretless": False, "category": "tar_setar", "lineage": "qajar_radif"},
    "nariman_oud": {"fretless": True, "category": "oud", "lineage": "classical"},
    "neydavud_tar": {"fretless": False, "category": "tar", "lineage": "historical_radif"},
    "shekarchi_kamancheh": {"fretless": True, "category": "kamancheh", "lineage": "classical"},
    "kasaei_ney": {"fretless": True, "category": "ney", "lineage": "classical"},
    "shahnaz_tar": {"fretless": False, "category": "tar", "lineage": "classical"},
    "ebadi_setar": {"fretless": False, "category": "setar", "lineage": "classical"},
    "saba_violin": {"fretless": True, "category": "violin", "lineage": "classical"},
    "lotfi_tar": {"fretless": False, "category": "tar", "lineage": "classical"},
}

SLOTS = [
    ("zir_e_ist_si", -90.2, 45.0, "Sub-tonic (Si)", "243/256 (-90.2c)"),
    ("tonic_do", 0.0, 35.0, "Tonic (Do - Rast)", "1/1 (0.0c)"),
    ("step_2_re", 203.9, 40.0, "Major 2nd (Re)", "9/8 (+203.9c)"),
    ("step_3_mi", 400.0, 45.0, "Major 3rd (Mi)", "81/64 (+407.8c) vs 5/4 (+386.3c)"),
    ("step_4_fa", 498.0, 35.0, "Pure 4th (Fa)", "4/3 (+498.0c)"),
    ("step_5_sol", 702.0, 35.0, "Pure 5th (Sol - Panjgah)", "3/2 (+702.0c)"),
    ("mod_la_koron", 840.6, 45.0, "Neutral 6th (La Koron - Oshshaq)", "13/8 (+840.6c)"),
    ("step_6_la", 905.9, 45.0, "Major 6th (La)", "27/16 (+905.9c)"),
    ("step_7_si", 1109.8, 50.0, "Leading Tone (Si)", "243/128 (+1109.8c)"),
    ("octave_do", 1200.0, 35.0, "Octave (Do')", "2/1 (+1200.0c)"),
]


def detect_tonic_hz(f_arr: np.ndarray) -> float:
    hist, bin_edges = np.histogram(f_arr, bins=300, range=(110.0, 750.0))
    peak_idx = np.argmax(hist)
    return float(0.5 * (bin_edges[peak_idx] + bin_edges[peak_idx + 1]))


def main():
    sources_data = {}
    tot_strikes = 0

    print("=== Computing Cross-Instrument Consensus for Dastgah-e Rast-Panjgah ===")

    for m_id, meta in RAST_PANJGAH_MASTERS.items():
        npz_p = OUT / f"strikes_rast_panjgah_{m_id}.npz"
        if not npz_p.exists():
            print(f"Skipping {m_id}: {npz_p.name} not found")
            continue

        d = np.load(npz_p, allow_pickle=True)
        f_arr = np.array([float(x) for x in d["f"] if float(x) > 0])
        if len(f_arr) < 20:
            continue

        tot_strikes += len(f_arr)
        t_hz = detect_tonic_hz(f_arr)

        cents = 1200.0 * np.log2(f_arr / t_hz)
        cents_mod = (cents + 150.0) % 1200.0 - 150.0

        slot_medians = {}
        slot_counts = {}

        for s_id, target_c, tol, name, theory_ratio in SLOTS:
            diff = np.abs(cents_mod - target_c)
            in_slot = cents_mod[diff <= tol]
            if len(in_slot) >= 5:
                slot_medians[s_id] = float(np.median(in_slot))
                slot_counts[s_id] = int(len(in_slot))
            else:
                slot_medians[s_id] = None
                slot_counts[s_id] = int(len(in_slot))

        sources_data[m_id] = {
            "meta": meta,
            "tonic_hz": round(t_hz, 1),
            "total_strikes": int(len(f_arr)),
            "slot_medians": slot_medians,
            "slot_counts": slot_counts,
        }
        print(f"[{m_id:<22s}] strikes={len(f_arr):5d}  tonic={t_hz:5.1f} Hz  fretless={meta['fretless']}")

    # Cross-master consensus calculation
    consensus_slots = {}
    for s_id, target_c, tol, name, theory_ratio in SLOTS:
        all_vals = []
        fretted_vals = []
        fretless_vals = []
        total_slot_strikes = 0

        for m_id, dat in sources_data.items():
            cnt = dat["slot_counts"].get(s_id, 0)
            total_slot_strikes += cnt
            val = dat["slot_medians"].get(s_id)
            if val is not None:
                all_vals.append(val)
                if dat["meta"]["fretless"]:
                    fretless_vals.append(val)
                else:
                    fretted_vals.append(val)

        consensus_slots[s_id] = {
            "name": name,
            "theory_target": target_c,
            "theory_ratio": theory_ratio,
            "strikes_binned": total_slot_strikes,
            "masters_contributing": len(all_vals),
            "median_cents": round(float(statistics.median(all_vals)), 1) if all_vals else None,
            "mean_cents": round(float(statistics.mean(all_vals)), 1) if all_vals else None,
            "std_cents": round(float(statistics.stdev(all_vals)), 1) if len(all_vals) > 1 else None,
            "fretted_median": round(float(statistics.median(fretted_vals)), 1) if fretted_vals else None,
            "fretless_median": round(float(statistics.median(fretless_vals)), 1) if fretless_vals else None,
        }

    res = {
        "dastgah": "Rast-Panjgah",
        "total_strikes_analyzed": tot_strikes,
        "masters_count": len(sources_data),
        "consensus_slots": consensus_slots,
        "sources": sources_data,
    }

    out_json = OUT / "rast_panjgah_consensus.json"
    with open(out_json, "w") as fp:
        json.dump(res, fp, indent=2)

    print(f"\nConsensus written to {out_json} ({tot_strikes:,} total strikes across {len(sources_data)} masters).")
    print(f"\n{'Degree / Slot':<35s} | {'Theory':<25s} | {'Consensus':<10s} | {'Fretted':<8s} | {'Fretless':<8s} | {'N strikes':<9s}")
    print("-" * 105)
    for s_id, dat in consensus_slots.items():
        th = f"{dat['theory_target']:+.1f}¢ ({dat['theory_ratio']})"
        cons = f"{dat['median_cents']:+.1f}¢" if dat["median_cents"] is not None else "N/A"
        fr = f"{dat['fretted_median']:+.1f}¢" if dat["fretted_median"] is not None else "N/A"
        fl = f"{dat['fretless_median']:+.1f}¢" if dat["fretless_median"] is not None else "N/A"
        print(f"{dat['name']:<35s} | {th:<25s} | {cons:<10s} | {fr:<8s} | {fl:<8s} | {dat['strikes_binned']:>8d}")


if __name__ == "__main__":
    main()
