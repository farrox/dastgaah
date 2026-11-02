#!/usr/bin/env python3
"""Refined consensus for Segah with octave-aware slot binning.
In Segah, the resting tonic (Ist) is Mi Koron.
Relative intervals over Ist (0.0¢):
- Zir-e Ist (Re): ~ -150¢
- Ist (Mi Koron): 0.0¢
- Zabol (Fa): +140¢ to +160¢ (Neutral 2nd / superparticular 13/12)
- Muye (Sol): +340¢ to +360¢ (Zalzal neutral 3rd / 27/22 or 11/9)
- Hesar (La Koron): +485¢ to +510¢ (Pure 4th / 4/3)
- Shahkhatayi (Si b): +685¢ to +710¢ (Pure 5th / 3/2)
- Mokhalef (Do): +830¢ to +870¢ (Climax 6th degree / Neutral 6th over Ist)
- Octave (Mi Koron'): +1180¢ to +1220¢
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_upgraded_strikes import OUT

SEGAH_MASTERS = {
    "alizadeh_tar": {"fretless": False, "category": "tar", "lineage": "modern"},
    "shahnazi_tar": {"fretless": False, "category": "tar", "lineage": "qajar_radif"},
    "karimi_vocal": {"fretless": True, "category": "voice", "lineage": "canonical"},
    "borumand_tar_setar": {"fretless": False, "category": "tar_setar", "lineage": "qajar_radif"},
    "kasaei_ney": {"fretless": True, "category": "ney", "lineage": "classical"},
    "nariman_oud": {"fretless": True, "category": "oud", "lineage": "classical"},
    "lotfi_tar_setar": {"fretless": False, "category": "tar_setar", "lineage": "classical"},
    "saba_violin": {"fretless": True, "category": "violin", "lineage": "classical"},
    "shahnaz_tar": {"fretless": False, "category": "tar", "lineage": "classical"},
    "payvar_santur": {"fretless": False, "category": "santur", "lineage": "classical"},
    "bigjekhani_tar": {"fretless": False, "category": "tar", "lineage": "classical"},
    "darvish_khan_tar": {"fretless": False, "category": "tar", "lineage": "historical_shellac"}
}

SLOTS = [
    ("zir_e_ist_re", -150.0, 50.0, "Sub-tonic (Re)", "12/13 (-138.6c)"),
    ("ist_tonic", 0.0, 35.0, "Ist (Mi Koron)", "1/1 (0.0c)"),
    ("zabol_fa", 154.8, 45.0, "Zabol (Fa)", "13/12 (+138.6c)"),
    ("muye_sol", 354.5, 50.0, "Muye (Sol)", "27/22 (+354.5c) / 11/9 (+347.4c)"),
    ("hesar_la_k", 498.0, 45.0, "Hesar (La Koron)", "4/3 (+498.0c)"),
    ("shahkhatayi_si_b", 702.0, 45.0, "Shahkhatayi (Si b)", "3/2 (+702.0c)"),
    ("mokhalef_do", 850.0, 55.0, "Mokhalef (Do)", "18/11 (+852.6c) / 3/2 x 13/12 (+840.6c)"),
    ("octave_ist", 1200.0, 35.0, "Octave (Mi Koron')", "2/1 (+1200.0c)")
]

def detect_tonic_hz(f_arr: np.ndarray):
    # Kernel density / fine histogram
    hist, bin_edges = np.histogram(f_arr, bins=250, range=(120.0, 650.0))
    peak_idx = np.argmax(hist)
    return float(0.5 * (bin_edges[peak_idx] + bin_edges[peak_idx+1]))

def main():
    sources_data = {}
    tot_strikes = 0

    for sname, meta in SEGAH_MASTERS.items():
        npz_path = OUT / f"strikes_segah_{sname}.npz"
        if not npz_path.exists():
            continue
        d = np.load(npz_path)
        f = d["f"]
        if len(f) < 20:
            continue
        ist_hz = detect_tonic_hz(f)
        c = 1200.0 * np.log2(f / ist_hz)
        
        # Fold into fundamental octave [-250, 950] plus exact octaves
        m_slots = {}
        for key, target, tol, label, ratio in SLOTS:
            diff = c - target
            # Match directly or octave-shifted
            if target == 1200.0:
                in_slot = c[np.abs(c - 1200.0) <= tol]
            elif target < 0:
                in_slot = c[np.abs(c - target) <= tol]
            else:
                # Direct or folded octave
                diff_mod = (c - target + 600.0) % 1200.0 - 600.0
                in_slot = c[np.abs(diff_mod) <= tol]
                # Re-reference to slot scale
                in_slot = target + diff_mod[np.abs(diff_mod) <= tol]

            if len(in_slot) >= 8:
                m_slots[key] = {
                    "median_cents": float(np.median(in_slot)),
                    "sigma": float(np.std(in_slot)),
                    "n": int(len(in_slot))
                }
            else:
                m_slots[key] = None

        sources_data[sname] = {
            "category": meta["category"],
            "lineage": meta["lineage"],
            "fretless": meta["fretless"],
            "ist_hz": round(ist_hz, 1),
            "strikes": len(f),
            "slots": m_slots
        }
        tot_strikes += len(f)

    consensus = {}
    for key, target, tol, label, ratio in SLOTS:
        all_meds, fretted, fretless = [], [], []
        n_tot = 0
        act_m = 0
        for sname, sinfo in sources_data.items():
            res = sinfo["slots"].get(key)
            if res:
                act_m += 1
                n_tot += res["n"]
                m = res["median_cents"]
                all_meds.append(m)
                if sinfo["fretless"]:
                    fretless.append(m)
                else:
                    fretted.append(m)
        if all_meds:
            consensus[key] = {
                "label": label,
                "theory_cents": target,
                "theory_ratio": ratio,
                "consensus_median": round(float(statistics.median(all_meds)), 2),
                "spread_sigma": round(float(statistics.stdev(all_meds)) if len(all_meds) > 1 else 0.0, 2),
                "fretted_median": round(float(statistics.median(fretted)), 2) if fretted else None,
                "fretless_median": round(float(statistics.median(fretless)), 2) if fretless else None,
                "strikes": n_tot,
                "masters": act_m
            }

    out_json = {
        "dastgah": "Segah",
        "n_masters": len(sources_data),
        "total_strikes": tot_strikes,
        "consensus": consensus,
        "sources": sources_data
    }
    with open(OUT / "segah_consensus.json", "w", encoding="utf-8") as f:
        json.dump(out_json, f, indent=2, ensure_ascii=False)

    print(f"\n=========================================================================================================")
    print(f"{'Slot':<18s} | {'Theory':<10s} | {'Fretted':<10s} | {'Fretless':<10s} | {'Consensus':<10s} | {'Delta':<8s} | {'Strikes':<8s}")
    print(f"=========================================================================================================")
    for k, v in consensus.items():
        th = v["theory_cents"]
        fr = f"{v['fretted_median']:+.1f}¢" if v['fretted_median'] is not None else "-"
        fl = f"{v['fretless_median']:+.1f}¢" if v['fretless_median'] is not None else "-"
        co = f"{v['consensus_median']:+.1f}¢"
        delta = f"{v['consensus_median'] - th:+.1f}¢"
        print(f"{k:<18s} | {th:+7.1f}¢  | {fr:<10s} | {fl:<10s} | {co:<10s} | {delta:<8s} | {v['strikes']:6d}")
    print(f"=========================================================================================================")

if __name__ == "__main__":
    main()
