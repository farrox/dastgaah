#!/usr/bin/env python3
"""Automated Dashti Consensus & Fretted vs. Fretless Modal Comparison.

Analyzes strikes_dashti_*.npz across all 12 masters:
- Fretted (Tār & Setār): Alizadeh, Kasaei, Ebadi, Saba, Lotfi, Shahnazi
- Fretless (Oud, Barbat, Kamāncheh, Vocal): Nariman, Behroozinia, Shekarchi, Farajpouri, Kalhor, Karimi

Modal Scale degrees in Dāng-e Shur / Āvāz-e Dashti relative to Ist (0 cents):
  - Subtonic (Zir-e Ist): ~ -204¢ / +996¢
  - Degree 0: Ist (Finalis) = 0.0¢
  - Degree 1: 2nd Koron (e.g. Mi-koron) ~ +138¢ (Al-Fārābī / Ibn Sīnā 13/12 superparticular)
  - Degree 2: Minor 3rd (e.g. Fā) ~ +294¢ to +300¢
  - Degree 3: 4th / Shāhed (Pole of tension / center of gravity, e.g. Sol) ~ +498¢
  - Degree 4a: Variable 5th lower (Motaghayyer Koron, e.g. Lā-koron) ~ +640¢ to +670¢
  - Degree 4b: Variable 5th upper (Motaghayyer Natural, e.g. Lā-natural) ~ +702¢
  - Degree 5: 6th (Neutral / Minor 6th, e.g. Si-koron / Si-bemol) ~ +800¢ to +850¢

Outputs:
  analysis/dashti_consensus.json
"""
from __future__ import annotations

import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rebuild_consensus_from_cache as rcc

OUT = Path(__file__).resolve().parent

SOURCES = [
    # Fretless
    {"name": "nariman_oud", "ist": 147.6, "fretless": True, "category": "oud"},
    {"name": "behroozinia_barbat", "ist": 147.1, "fretless": True, "category": "barbat"},
    {"name": "shekarchi_kamancheh", "ist": 431.6, "fretless": True, "category": "kamancheh"},
    {"name": "farajpouri_kamancheh", "ist": 390.6, "fretless": True, "category": "kamancheh"},
    {"name": "kalhor_kamancheh", "ist": 275.2, "fretless": True, "category": "kamancheh"},
    {"name": "karimi_vocal", "ist": 165.5, "fretless": True, "category": "vocal"},
    # Fretted
    {"name": "alizadeh_setar", "ist": 373.7, "fretless": False, "category": "setar"},
    {"name": "kasaei_setar", "ist": 231.9, "fretless": False, "category": "setar"},
    {"name": "ebadi_setar", "ist": 289.0, "fretless": False, "category": "setar"},
    {"name": "saba_setar", "ist": 409.6, "fretless": False, "category": "setar"},
    {"name": "lotfi_setar", "ist": 294.7, "fretless": False, "category": "setar"},
    {"name": "shahnazi_tar", "ist": 215.5, "fretless": False, "category": "tar"},
]

DEGREE_TARGETS = [
    ("zir_e_ist", -204.0, (-260.0, -150.0)),
    ("ist", 0.0, (-40.0, 45.0)),
    ("koron_2nd", 138.6, (100.0, 175.0)),
    ("minor_3rd", 294.1, (250.0, 340.0)),
    ("shahed_4th", 498.0, (460.0, 535.0)),
    ("motaghayyer_koron_5th", 650.0, (620.0, 680.0)),
    ("motaghayyer_natural_5th", 702.0, (685.0, 730.0)),
    ("degree_6th", 814.0, (770.0, 870.0)),
]


def fold_cents(c: float) -> float:
    return (c + 600.0) % 1200.0 - 600.0


def main():
    results = {}
    master_strikes = {}

    for s in SOURCES:
        name = s["name"]
        npz_path = OUT / f"strikes_dashti_{name}.npz"
        d = rcc.load_npz_dict(npz_path)
        fs = d.get("f", [])
        confs = d.get("conf", [])
        tracks = d.get("track", [])
        ist_f0 = s["ist"]

        # calculate cents relative to Ist for each strike
        # Fold into standard octave [-300, +900]
        strike_cents = []
        for f in fs:
            # fold into closest octave to ist_f0
            c = 1200.0 * math.log2(f / ist_f0)
            folded = fold_cents(c)
            # also preserve native octave
            strike_cents.append((f, c, folded))

        master_strikes[name] = strike_cents

        # Slot measurements
        slot_data = {}
        for deg_name, target, (lo, hi) in DEGREE_TARGETS:
            # find strikes matching either folded or native in [lo, hi]
            matched = []
            for f, c, folded in strike_cents:
                # check folded
                if lo <= folded <= hi:
                    matched.append(folded)
                # check c mod 1200 if target is positive
                elif target > 0 and lo <= (c % 1200) <= hi:
                    matched.append(c % 1200)
                elif target < 0 and lo <= (c % 1200 - 1200) <= hi:
                    matched.append(c % 1200 - 1200)

            if len(matched) >= 3:
                matched.sort()
                med = float(statistics.median(matched))
                # compute std dev
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
            "ist_hz": s["ist"],
            "total_strikes": len(fs),
            "slots": slot_data,
        }

    # Now calculate consensus across:
    # 1. All 12 masters
    # 2. Fretless group (n=6: Nariman, Behroozinia, Shekarchi, Farajpouri, Kalhor, Karimi)
    # 3. Fretted group (n=6: Alizadeh, Kasaei, Ebadi, Saba, Lotfi, Shahnazi)
    groups = {
        "all_masters": [s["name"] for s in SOURCES],
        "fretless": [s["name"] for s in SOURCES if s["fretless"]],
        "fretted": [s["name"] for s in SOURCES if not s["fretless"]],
    }

    consensus = {}
    for grp_name, members in groups.items():
        grp_consensus = {}
        for deg_name, target, _ in DEGREE_TARGETS:
            vals = []
            weights = []
            for m in members:
                sl = results[m]["slots"].get(deg_name)
                if sl is not None:
                    vals.append(sl["median_cents"])
                    weights.append(sl["n_strikes"])
            if vals:
                med = float(statistics.median(vals))
                mean = float(statistics.mean(vals))
                sd = float(statistics.pstdev(vals)) if len(vals) > 1 else 0.0
                grp_consensus[deg_name] = {
                    "median_cents": round(med, 2),
                    "mean_cents": round(mean, 2),
                    "std_cents": round(sd, 2),
                    "n_sources": len(vals),
                    "sources_reporting": len(vals),
                    "source_medians": [round(v, 2) for v in vals],
                }
            else:
                grp_consensus[deg_name] = None
        consensus[grp_name] = grp_consensus

    out_file = OUT / "dashti_consensus.json"
    full_output = {
        "sources": results,
        "consensus": consensus,
        "historical_theories": {
            "pythagorean": {"zir_e_ist": -203.9, "ist": 0.0, "koron_2nd": None, "minor_3rd": 294.1, "shahed_4th": 498.0, "motaghayyer_koron_5th": None, "motaghayyer_natural_5th": 702.0},
            "al_farabi_13_12": {"koron_2nd": 138.6, "motaghayyer_koron_5th": 636.6},
            "vaziri_24_tet": {"zir_e_ist": -200.0, "ist": 0.0, "koron_2nd": 150.0, "minor_3rd": 300.0, "shahed_4th": 500.0, "motaghayyer_koron_5th": 650.0, "motaghayyer_natural_5th": 700.0},
            "barkechli_limmas": {"koron_2nd": 90.2, "motaghayyer_koron_5th": 588.3},
        }
    }
    with open(out_file, "w") as fp:
        json.dump(full_output, fp, indent=2)

    print(f"Saved {out_file}")
    # Print summary table
    print("\n" + "=" * 80)
    print("EMPIRICAL ĀVĀZ-E DASHTI CONSENSUS: FRETTED VS FRETLESS")
    print("=" * 80)
    print(f"{'Scale Degree':<24} | {'Fretted Median':<14} | {'Fretless Median':<16} | {'All Masters':<12} | {'Farabi/Pyth Ratios'}")
    print("-" * 80)
    for deg_name, target, _ in DEGREE_TARGETS:
        fretted_val = consensus["fretted"][deg_name]
        fretless_val = consensus["fretless"][deg_name]
        all_val = consensus["all_masters"][deg_name]

        fr_str = f"{fretted_val['median_cents']:+.1f}¢ (±{fretted_val['std_cents']:.1f})" if fretted_val else "N/A"
        fl_str = f"{fretless_val['median_cents']:+.1f}¢ (±{fretless_val['std_cents']:.1f})" if fretless_val else "N/A"
        all_str = f"{all_val['median_cents']:+.1f}¢" if all_val else "N/A"

        theo = ""
        if deg_name == "koron_2nd":
            theo = "13/12 (+138.6¢)"
        elif deg_name == "minor_3rd":
            theo = "32/27 (+294.1¢) / 6/5 (+315.6¢)"
        elif deg_name == "shahed_4th":
            theo = "4/3 (+498.0¢)"
        elif deg_name == "motaghayyer_koron_5th":
            theo = "Neutral 5th (~640-660¢)"
        elif deg_name == "motaghayyer_natural_5th":
            theo = "3/2 (+702.0¢)"
        elif deg_name == "zir_e_ist":
            theo = "9/8 subtonic (-203.9¢)"

        print(f"{deg_name:<24} | {fr_str:<14} | {fl_str:<16} | {all_str:<12} | {theo}")
    print("=" * 80)


if __name__ == "__main__":
    main()

