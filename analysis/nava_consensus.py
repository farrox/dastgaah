#!/usr/bin/env python3
"""Expanded 11-Master Consensus for Dastgah-e Nava.

Analyzes 11 masters:
- Qajar Masters: Nur-Ali Borumand, Morteza Neydavud, Ali-Akbar Shahnazi
- Setar/Tar Masters: Abolhasan Saba, Ahmad Ebadi, Nima Janmohammadi, Hossein Alizadeh, Dariush Talai
- Fretless Masters: Mansour Nariman (Oud), Aliakbar Shekarchi (Kamancheh), Mahmud Karimi (Vocal)

Outputs:
  analysis/nava_consensus.json
"""
from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rebuild_consensus_from_cache as rcc

OUT = Path(__file__).resolve().parent

SOURCES = [
    # Qajar Masters
    {"name": "borumand_tar_setar", "ist": 211.6, "fretless": False, "category": "tar_setar", "lineage": "qajar"},
    {"name": "neydavud_tar", "ist": 200.2, "fretless": False, "category": "tar", "lineage": "qajar"},
    {"name": "shahnazi_tar", "ist": 225.0, "fretless": False, "category": "tar", "lineage": "qajar"},
    # Classical Setar / Tar
    {"name": "saba_setar", "ist": 236.1, "fretless": False, "category": "setar", "lineage": "transitional"},
    {"name": "ebadi_setar", "ist": 237.2, "fretless": False, "category": "setar", "lineage": "transitional"},
    {"name": "janmohammadi_setar", "ist": 233.9, "fretless": False, "category": "setar", "lineage": "modern"},
    {"name": "alizadeh_setar", "ist": 245.3, "fretless": False, "category": "setar", "lineage": "modern"},
    {"name": "talai_tar", "ist": 275.9, "fretless": False, "category": "tar", "lineage": "modern"},
    # Fretless Masters
    {"name": "nariman_oud", "ist": 149.3, "fretless": True, "category": "oud", "lineage": "classical"},
    {"name": "shekarchi_kamancheh", "ist": 439.3, "fretless": True, "category": "kamancheh", "lineage": "classical"},
    {"name": "karimi_vocal", "ist": 169.9, "fretless": True, "category": "vocal", "lineage": "classical"},
]

DEGREE_TARGETS = [
    ("zir_e_ist", -204.0, (-260.0, -150.0)),
    ("ist", 0.0, (-40.0, 45.0)),
    ("koron_2nd", 138.6, (85.0, 175.0)),
    ("minor_3rd", 294.1, (250.0, 340.0)),
    ("shahed_4th", 498.0, (460.0, 535.0)),
    ("fifth", 702.0, (665.0, 735.0)),
    ("degree_6th_koron", 840.0, (780.0, 875.0)),
    ("octave", 1200.0, (1160.0, 1240.0)),
]


def fold_cents(c: float) -> float:
    return (c + 600.0) % 1200.0 - 600.0


def main():
    results = {}
    for s in SOURCES:
        name = s["name"]
        npz_path = OUT / f"strikes_nava_{name}.npz"
        d = rcc.load_npz_dict(npz_path)
        fs = d.get("f", [])
        ist_f0 = s["ist"]

        strike_cents = []
        for f in fs:
            c = 1200.0 * math.log2(f / ist_f0)
            folded = fold_cents(c)
            strike_cents.append((f, c, folded))

        slot_data = {}
        for deg_name, target, (lo, hi) in DEGREE_TARGETS:
            matched = []
            for f, c, folded in strike_cents:
                if lo <= folded <= hi:
                    matched.append(folded)
                elif target > 0 and lo <= (c % 1200) <= hi:
                    matched.append(c % 1200)
                elif target < 0 and lo <= (c % 1200 - 1200) <= hi:
                    matched.append(c % 1200 - 1200)

            if len(matched) >= 3:
                matched.sort()
                med = float(statistics.median(matched))
                sd = float(statistics.pstdev(matched)) if len(matched) > 1 else 0.0
                slot_data[deg_name] = {
                    "median_cents": round(med, 2),
                    "std_cents": round(sd, 2),
                    "n_strikes": len(matched),
                }
            else:
                slot_data[deg_name] = None

        results[name] = {
            "category": s["category"],
            "fretless": s["fretless"],
            "lineage": s["lineage"],
            "ist_hz": s["ist"],
            "total_strikes": len(fs),
            "slots": slot_data,
        }

    groups = {
        "all_masters": [s["name"] for s in SOURCES],
        "qajar": [s["name"] for s in SOURCES if s["lineage"] == "qajar"],
        "fretted": [s["name"] for s in SOURCES if not s["fretless"]],
        "fretless": [s["name"] for s in SOURCES if s["fretless"]],
    }

    consensus = {}
    for grp_name, members in groups.items():
        grp_consensus = {}
        for deg_name, target, _ in DEGREE_TARGETS:
            vals = []
            for m in members:
                sl = results[m]["slots"].get(deg_name)
                if sl is not None:
                    vals.append(sl["median_cents"])
            if vals:
                med = float(statistics.median(vals))
                mean = float(statistics.mean(vals))
                sd = float(statistics.pstdev(vals)) if len(vals) > 1 else 0.0
                grp_consensus[deg_name] = {
                    "median_cents": round(med, 2),
                    "mean_cents": round(mean, 2),
                    "std_cents": round(sd, 2),
                    "n_sources": len(vals),
                    "source_medians": [round(v, 2) for v in vals],
                }
            else:
                grp_consensus[deg_name] = None
        consensus[grp_name] = grp_consensus

    out_file = OUT / "nava_consensus.json"
    with open(out_file, "w") as fp:
        json.dump({"sources": results, "consensus": consensus}, fp, indent=2)

    print(f"Saved {out_file}")
    print("\n" + "=" * 95)
    print("EXPANDED DASTGĀH-E NAVĀ CONSENSUS: 11 MASTERS (QAJAR vs FRETTED vs FRETLESS)")
    print("=" * 95)
    print(f"{'Scale Degree':<18} | {'Qajar Lineage':<15} | {'Fretted Median':<16} | {'Fretless Median':<16} | {'All 11 Masters':<14} | {'Theory Ratio'}")
    print("-" * 95)
    for deg_name, target, _ in DEGREE_TARGETS:
        qj = consensus["qajar"][deg_name]
        fr = consensus["fretted"][deg_name]
        fl = consensus["fretless"][deg_name]
        al = consensus["all_masters"][deg_name]
        qj_s = f"{qj['median_cents']:+.1f}¢" if qj else "N/A"
        fr_s = f"{fr['median_cents']:+.1f}¢" if fr else "N/A"
        fl_s = f"{fl['median_cents']:+.1f}¢" if fl else "N/A"
        al_s = f"{al['median_cents']:+.1f}¢" if al else "N/A"

        theo = ""
        if deg_name == "zir_e_ist": theo = "9/8 subtonic (-203.9¢)"
        elif deg_name == "koron_2nd": theo = "Farabi 13/12 (+138.6¢) / Limma (90.2¢)"
        elif deg_name == "minor_3rd": theo = "Pythagorean 32/27 (+294.1¢)"
        elif deg_name == "shahed_4th": theo = "Pure 4/3 fourth (+498.0¢)"
        elif deg_name == "fifth": theo = "Pure 3/2 fifth (+702.0¢)"
        elif deg_name == "octave": theo = "Pure 2/1 octave (+1200.0¢)"

        print(f"{deg_name:<18} | {qj_s:<15} | {fr_s:<16} | {fl_s:<16} | {al_s:<14} | {theo}")
    print("=" * 95)


if __name__ == "__main__":
    main()
