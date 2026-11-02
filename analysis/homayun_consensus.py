#!/usr/bin/env python3
"""Dastgah-e Homayun Consensus Analysis across ALL 18 Master Sources (45,512 note strikes).
With Track-Level Absolute Pitch Anchoring for Multimodal Recitals.

Writes:
  analysis/homayun_consensus.json
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
    # --- Qajar & Radif Lineage ---
    {"name": "borumand_tar_setar", "ist": 373.0, "lineage": "qajar_radif", "category": "tar_setar", "fretless": False},
    {"name": "neydavud_tar",       "ist": 198.8, "lineage": "qajar_radif", "category": "tar",       "fretless": False},
    {"name": "shahnazi_tar",       "ist": 284.2, "lineage": "qajar_radif", "category": "tar",       "fretless": False},
    {"name": "forutan_setar",      "ist": 348.2, "lineage": "qajar_radif", "category": "setar",     "fretless": False},
    {"name": "hormozi_setar",      "ist": 172.0, "lineage": "qajar_radif", "category": "setar",     "fretless": False},
    {"name": "ebadi_setar",        "ist": 226.8, "lineage": "classical",   "category": "setar",     "fretless": False},
    {"name": "talai_tar",          "ist": 541.4, "lineage": "canonical",   "category": "tar",       "fretless": False},

    # --- Classical Fretted Masters & Ensembles ---
    {"name": "alizadeh_setar",     "ist": 165.0, "lineage": "modern",      "category": "setar",     "fretless": False},
    {"name": "lotfi_tar_setar",    "ist": 203.0, "track_anchors": {"Niavaran": 161.0, "Cologne": 203.0}, "lineage": "classical", "category": "tar_setar", "fretless": False},
    {"name": "shahnaz_tar",        "ist": 215.0, "lineage": "classical",   "category": "tar",       "fretless": False},
    {"name": "meshkatian_santur_ensemble", "ist": 279.0, "lineage": "classical", "category": "santur_ensemble", "fretless": False},

    # --- Historical & Fretless Masters (Kamancheh, Oud, Ney, Clarinet, Vocal) ---
    {"name": "bagher_khan_kamancheh", "ist": 221.8, "lineage": "historical_1905", "category": "kamancheh", "fretless": True},
    {"name": "bahari_kamancheh",   "ist": 171.0, "lineage": "historical",  "category": "kamancheh", "fretless": True},
    {"name": "shekarchi_kamancheh","ist": 433.0, "lineage": "canonical",   "category": "kamancheh", "fretless": True},
    {"name": "nariman_oud",        "ist": 196.2, "lineage": "classical",   "category": "oud",       "fretless": True},
    {"name": "kasaei_ney",         "ist": 543.2, "lineage": "classical",   "category": "ney",       "fretless": True},
    {"name": "shirkhodaee_clarinet","ist": 259.0, "lineage": "classical",   "category": "clarinet",  "fretless": True},
    {"name": "karimi_vocal",       "ist": 183.0, "lineage": "canonical",   "category": "voice",     "fretless": True},
]

# Modal scale degrees in Dastgah-e Homayun relative to Tonic / Ist (0.0 cents)
DEGREE_TARGETS = [
    ("zir_e_ist_7th",    -112.0, (-150.0, -70.0)),   # Leading note below tonic: Si natural / limma below (243/256 or 15/16)
    ("ist_tonic",           0.0,  (-40.0,  40.0)),   # Tonic / Ist: Do (1/1)
    ("neutral_2nd_koron", 138.6,  ( 95.0, 180.0)),   # 2nd degree: Re-koron (13/12 = 138.6¢) - Dāng-e Chahārgāh lower step
    ("major_3rd",         395.0,  (355.0, 435.0)),   # 3rd degree: Mi natural (5/4 = 386.3¢ or 81/64 = 407.8¢)
    ("pure_4th",          498.0,  (465.0, 535.0)),   # 4th degree: Fa (4/3 = 498.0¢) - Pivot tone
    ("fifth_sol",         702.0,  (675.0, 735.0)),   # 5th degree: Sol (3/2 = 702.0¢) - Shāhed of Bīdād & Shūshtari
    ("neutral_6th_koron", 840.6,  (800.0, 880.0)),   # 6th degree: La-koron (13/12 above Sol = 840.6¢)
    ("minor_7th",        1017.5,  (980.0, 1055.0)),  # 7th degree: Si-flat in upper excursions / Bābā Tāher (16/9 = 996.1¢ or 9/5 = 1017.5¢)
    ("octave",           1200.0, (1165.0, 1235.0)),  # Upper tonic
]


def main():
    results = {}
    master_strikes = {}

    for s in SOURCES:
        name = s["name"]
        npz_path = OUT / f"strikes_homayun_{name}.npz"
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
        "dastgah": "Dastgah-e Homayun",
        "n_masters": len(SOURCES),
        "total_strikes": sum(master_strikes.values()),
        "consensus": consensus,
        "sources": results,
    }

    out_file = OUT / "homayun_consensus.json"
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
        print(f"{deg_name:<20} | {info['target_theory_cents']:+6.1f}¢ | {info['consensus_median_cents']:+8.1f}¢ | {info['delta_cents']:+5.1f}¢ | {info['spread_sigma_cents']:4.1f}¢ | {fr_str:<9} | {fl_str:<9} | {info['total_strikes']:5d} | {info['active_masters']:2d}/18")
    print("="*88)


if __name__ == "__main__":
    main()

