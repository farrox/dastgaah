#!/usr/bin/env python3
"""Dastgah-e Shur Consensus Analysis across 10 Master Sources (32,075 note strikes).
Empirical test of Dariush Tala'i's Dāng 1 (1/1 -> 13/12 -> 9/8 -> 4/3) and the Mother Mode of the Radif.

Writes:
  analysis/shur_consensus.json
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
    {"name": "alizadeh_tar",        "ist": 368.4, "lineage": "modern",    "category": "tar",       "fretless": False},
    {"name": "shahnazi_tar",        "ist": 213.2, "lineage": "qajar_radif","category": "tar",       "fretless": False},
    {"name": "forutan_setar",       "ist": 311.2, "lineage": "qajar_radif","category": "setar",     "fretless": False},
    {"name": "nariman_oud",         "ist": 194.8, "lineage": "classical",  "category": "oud",       "fretless": True},
    {"name": "shekarchi_kamancheh", "ist": 437.0, "lineage": "canonical",  "category": "kamancheh", "fretless": True},
    {"name": "karimi_vocal",        "ist": 235.2, "lineage": "canonical",  "category": "voice",     "fretless": True},
    {"name": "kasaei_ney_setar",    "ist": 544.6, "lineage": "classical",  "category": "ney_setar", "fretless": True},
    {"name": "lotfi_solo",          "ist": 201.2, "lineage": "classical",  "category": "tar_setar", "fretless": False},
    {"name": "saba_violin",         "ist": 232.8, "lineage": "classical",  "category": "violin",    "fretless": True},
    {"name": "borumand_tar_setar",  "ist": 131.0, "lineage": "qajar_radif","category": "tar_setar", "fretless": False},
]

# Modal scale degrees in Dastgah-e Shur relative to Tonic / Ist (0.0 cents)
DEGREE_TARGETS = [
    ("zir_e_ist_7th",    -203.9, (-245.0, -165.0)),  # Subtonic whole tone below: Si-flat (9/8 or 16/9 below)
    ("ist_tonic",           0.0,  (-40.0,  40.0)),   # Tonic / Ist / Finalis: Do (1/1)
    ("neutral_2nd_koron", 138.6,  ( 95.0, 180.0)),   # 2nd degree: Re-koron (Al-Fārābī 13/12 = 138.6¢) - The primary Shur microtone
    ("minor_3rd",         294.1,  (255.0, 335.0)),   # 3rd degree: Mi-flat (32/27 = 294.1¢ vs 6/5 = 315.6¢)
    ("pure_4th",          498.0,  (465.0, 535.0)),   # 4th degree: Fa (4/3 = 498.0¢) - End of Dāng 1
    ("fifth_sol",         702.0,  (670.0, 735.0)),   # 5th degree: Sol (3/2 = 702.0¢) - Pivot tone / Shahnāz entrance
    ("neutral_6th_koron", 840.6,  (800.0, 880.0)),   # 6th degree: La-koron (13/12 above Sol = 840.6¢) - Qaracheh focal center
    ("minor_7th",         996.1,  (960.0, 1035.0)),  # 7th degree: Si-flat (16/9 = 996.1¢) - Razavi climax
    ("octave",           1200.0, (1165.0, 1235.0)),  # Upper octave: Do (2/1)
]


def main():
    results = {}
    master_strikes = {}

    for s in SOURCES:
        name = s["name"]
        npz_path = OUT / f"strikes_shur_{name}.npz"
        d = rcc.load_npz_dict(npz_path)
        fs = d.get("f", [])
        tracks = d.get("track", [])
        default_ist = s["ist"]
        anchors = s.get("track_anchors", {})

        raw_cents = []
        for i, f in enumerate(fs):
            if f <= 50.0:
                continue
            tr_name = tracks[i] if i < len(tracks) else ""
            ist_f0 = default_ist
            for k, val in anchors.items():
                if k.lower() in tr_name.lower():
                    ist_f0 = val
                    break
            raw_cents.append(1200.0 * math.log2(f / ist_f0))

        master_strikes[name] = len(raw_cents)

        slot_data = {}
        for deg_name, target, (lo, hi) in DEGREE_TARGETS:
            matched = []
            for c in raw_cents:
                for shift in [-1200.0, 0.0, 1200.0]:
                    co = c + shift
                    if lo <= co <= hi:
                        matched.append(co)
                        break

            if len(matched) >= 3:
                med = statistics.median(matched)
                std = statistics.stdev(matched) if len(matched) >= 2 else 0.0
                slot_data[deg_name] = {
                    "median_cents": round(med, 2),
                    "std_cents": round(std, 2),
                    "n_strikes": len(matched),
                    "target_cents": target,
                    "delta_target": round(med - target, 2),
                }
            else:
                slot_data[deg_name] = None

        results[name] = {
            "category": s["category"],
            "lineage": s["lineage"],
            "fretless": s["fretless"],
            "ist_hz": default_ist,
            "total_strikes": len(raw_cents),
            "slots": slot_data,
        }

    # Aggregate consensus per degree
    consensus = {}
    for deg_name, target, _ in DEGREE_TARGETS:
        meds_all = []
        meds_fretted = []
        meds_fretless = []
        tot_strikes = 0

        for s in SOURCES:
            sl = results[s["name"]]["slots"].get(deg_name)
            if sl:
                c_val = sl["median_cents"]
                n_str = sl["n_strikes"]
                meds_all.append(c_val)
                tot_strikes += n_str
                if s["fretless"]:
                    meds_fretless.append(c_val)
                else:
                    meds_fretted.append(c_val)

        if meds_all:
            med_cons = statistics.median(meds_all)
            spread = statistics.stdev(meds_all) if len(meds_all) >= 2 else 0.0
            fr_med = statistics.median(meds_fretted) if meds_fretted else None
            fl_med = statistics.median(meds_fretless) if meds_fretless else None
            consensus[deg_name] = {
                "target_theory_cents": target,
                "consensus_median_cents": round(med_cons, 2),
                "delta_cents": round(med_cons - target, 2),
                "spread_sigma_cents": round(spread, 2),
                "fretted_median_cents": round(fr_med, 2) if fr_med is not None else None,
                "fretless_median_cents": round(fl_med, 2) if fl_med is not None else None,
                "total_strikes": tot_strikes,
                "active_masters": len(meds_all),
            }

    output = {
        "dastgah": "Dastgah-e Shur",
        "n_masters": len(SOURCES),
        "total_strikes": sum(master_strikes.values()),
        "consensus": consensus,
        "sources": results,
    }

    out_file = OUT / "shur_consensus.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"Wrote {out_file} ({len(SOURCES)} masters, {output['total_strikes']:,} strikes)")

    # Print summary table
    print("\n" + "="*88)
    print(f"{'Degree':<20} | {'Target':<8} | {'Consensus':<10} | {'Delta':<7} | {'Sigma':<6} | {'Fretted':<9} | {'Fretless':<9} | {'Strikes':<7} | {'Masters':<7}")
    print("="*88)
    for deg_name, info in consensus.items():
        fr_str = f"{info['fretted_median_cents']:+.1f}¢" if info['fretted_median_cents'] is not None else "—"
        fl_str = f"{info['fretless_median_cents']:+.1f}¢" if info['fretless_median_cents'] is not None else "—"
        print(f"{deg_name:<20} | {info['target_theory_cents']:+6.1f}¢ | {info['consensus_median_cents']:+8.1f}¢ | {info['delta_cents']:+5.1f}¢ | {info['spread_sigma_cents']:4.1f}¢ | {fr_str:<9} | {fl_str:<9} | {info['total_strikes']:5d} | {info['active_masters']:2d}/10")
    print("="*88)


if __name__ == "__main__":
    main()

