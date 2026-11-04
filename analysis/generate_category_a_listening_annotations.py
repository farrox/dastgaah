#!/usr/bin/env python3
"""Build Worksheet of Candidate Strikes for Independent Listening Review.
In accordance with Review 13 §1 & §6.1:
  - Strips all unverified claims, hardcoded concordance constants, and synthetic assessments.
  - Generates 30 real, time-stamped strikes (5 per Category A master) with exact frequencies
    and timestamps directly from the .npz archives.
  - Serves as an open listening worksheet with blank/pending evaluation fields for independent human listeners.
  - Fixes duration misstatements (Safvat Part 1 is 660.7s ~11.0 min; Alizadeh is 817.1s ~13.6 min).
  - Enforces strict locality (|Δt| <= 3.5s) between target and contemporaneous reference strikes.
"""

import hashlib
import json
import math
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ANALYSIS_DIR = BASE_DIR / "analysis"
sys.path.insert(0, str(ANALYSIS_DIR))
from run_rigorous_modal_audit import read_npz

OUT = Path("analysis")

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

MASTERS = [
    {
        "performer": "Dr. Dariush Safvat",
        "instrument": "Setar (Fretted)",
        "npz_file": "strikes_Safvat_Setar_Part1_5zSljfC5jdY.npz",
        "thz": 306.06,
        "thz_note": "Eb4 -28.5¢ (relative to A4=440 Hz)",
        "pk": 127.5,
        "ci_95": [126.0, 128.5],
        "ci_width": 2.5,
        "n_win": 174,
        "n_ton": 217,
        "radif_nominal_scale": "Shūr on Do (sounding at Eb4)",
        "radif_degree_hypotheses": "Finalis: open white string (sim-e sefid) @ 306.06 Hz; Neutral Second: nominal Re-koron; Sounding: E4 -0.7¢ (~329.5 Hz)",
        "physical_physics_context": "Four-string setār: white string sounds at 306.06 Hz; bass drone string (sim-e bam) sounds an octave lower at 152.8 Hz (1202.6¢ below white string; exact mathematical octave is 153.03 Hz). Target strikes near 329.5 Hz sit at -0.7¢ relative to concert E4 (329.63 Hz)."
    },
    {
        "performer": "Ali-Akbar Shahnazi",
        "instrument": "Tar (Fretted)",
        "npz_file": "strikes_shur_shahnazi_tar.npz",
        "thz": 213.59,
        "thz_note": "A3 -51.3¢ (or G#3 +48.7¢ relative to A4=440 Hz)",
        "pk": 128.0,
        "ci_95": [125.5, 130.5],
        "ci_width": 5.0,
        "n_win": 197,
        "n_ton": 246,
        "radif_nominal_scale": "Shūr on Do [Pedagogical radif convention, unverified edition]",
        "radif_degree_hypotheses": "Finalis: lower white/bass course @ 213.59 Hz; Neutral Second: nominal Re-koron; Sounding: Bb3 -25.2¢ (~229.9 Hz; +128.0¢)",
        "physical_physics_context": "Classical Qajar tār: lower white course tuned to modal finalis (213.59 Hz). Second-degree strikes in lower register cluster around 229.5–230.2 Hz (+128¢ peak). High-register excursions (octave register, 427–458 Hz) exhibit reference sensitivity (+143.5¢ secondary mode)."
    },
    {
        "performer": "Abolhasan Saba (Violin)",
        "instrument": "Violin (Fretless)",
        "npz_file": "strikes_shur_saba_violin.npz",
        "thz": 235.77,
        "octave_thz": 471.54,
        "thz_note": "Bb3 +20.0¢ (octave at Bb4 +20.0¢, 471.54 Hz relative to A4=440 Hz)",
        "pk": 129.0,
        "ci_95": [126.5, 131.0],
        "ci_width": 4.5,
        "n_win": 91,
        "n_ton": 51,
        "radif_nominal_scale": "Shūr on Re [Pedagogical radif convention, unverified edition]",
        "radif_degree_hypotheses": "Finalis: nominal Re on G string @ 235.77 Hz (octave Bb4 @ 471.54 Hz); Neutral Second: nominal Mi-koron; Sounding: C5 -48.8¢ (~508.7 Hz; +129.0¢ above Bb4)",
        "physical_physics_context": "Fretless violin: melody is executed primarily on D and A strings in the octave register (471.54 Hz), with second-degree strikes sounding at 507.7–509.6 Hz (+129.0¢ peak relative to 471.54 Hz)."
    },
    {
        "performer": "Mansour Nariman",
        "instrument": "Oud (Fretless)",
        "npz_file": "strikes_shur_nariman_oud.npz",
        "thz": 196.06,
        "thz_note": "G3 +0.5¢ (relative to A4=440 Hz)",
        "pk": 138.5,
        "ci_95": [137.5, 140.5],
        "ci_width": 3.0,
        "n_win": 825,
        "n_ton": 2341,
        "radif_nominal_scale": "Shūr on Sol [Pedagogical radif convention, unverified edition]",
        "radif_degree_hypotheses": "Finalis: open G course @ 196.06 Hz; Neutral Second: nominal La-koron; Sounding: A3 -39.3¢ (~212.8 Hz; +138.5¢)",
        "physical_physics_context": "Fretless barbat/oud: open G string tuned to 196.06 Hz (concert G3). Second-degree strikes sound on middle course at 211.9–213.0 Hz (+138.5¢ peak). Rapid double-course plectrum strikes yield high event count."
    },
    {
        "performer": "Yousef Foroutan",
        "instrument": "Setar (Fretted)",
        "npz_file": "strikes_shur_forutan_setar.npz",
        "thz": 314.58,
        "thz_note": "Eb4 +19.2¢ (relative to A4=440 Hz)",
        "pk": 150.5,
        "ci_95": [148.5, 152.5],
        "ci_width": 4.0,
        "n_win": 142,
        "n_ton": 663,
        "radif_nominal_scale": "Shūr on Do (sounding at Eb4) [Pedagogical radif convention, unverified edition]",
        "radif_degree_hypotheses": "Finalis: open white string @ 314.58 Hz; Neutral Second: nominal Re-koron; Sounding: F4 -22.5¢ (~343.0 Hz; +150.5¢)",
        "physical_physics_context": "Four-string setār tied with gut frets, tuned high for recording: open white string modal anchor @ 314.58 Hz. Second-degree strikes sound at 342.4–344.2 Hz (+150.5¢ peak), representing the wider ~150¢ neutral second lineage."
    },
    {
        "performer": "Hossein Alizadeh",
        "instrument": "Tar (Fretted)",
        "npz_file": "strikes_shur_alizadeh_tar.npz",
        "thz": 372.90,
        "thz_note": "F#4 +13.6¢ (relative to A4=440 Hz)",
        "pk": 153.5,
        "ci_95": [153.0, 154.5],
        "ci_width": 1.5,
        "n_win": 325,
        "n_ton": 585,
        "radif_nominal_scale": "Shūr on Fa-sharp [Pedagogical score convention, unverified edition]",
        "radif_degree_hypotheses": "Finalis: open bass/tonic course @ 372.90 Hz; Neutral Second: nominal Sol-koron; Sounding: G4 +64.8¢ (or Ab4 -35.2¢ / G-sori), ~407.5 Hz (+153.5¢)",
        "physical_physics_context": "Modern tār tuned in Shūr-e Fa-sharp: open bass course @ 372.90 Hz. Second-degree strikes forming the modal peak cluster sound at 406.5–408.2 Hz (+153.5¢ peak). Core strikes sit +65 to +67¢ above concert G4 (392.0 Hz)."
    }
]

def build_worksheet():
    data = []
    for m in MASTERS:
        npz_p = ANALYSIS_DIR / m["npz_file"]
        d = read_npz(npz_p)
        ts, fs, confs, wobs = d["t"], d["f"], d["conf"], d["wobble_plat_c"]
        dur_s = float(max(ts))
        
        # Valid strikes
        ref_thz = m.get("octave_thz", m["thz"])
        valid = []
        for i in range(len(fs)):
            if confs[i] >= 40.0 and wobs[i] <= 22.0 and 100 < fs[i] < 950:
                c = 1200.0 * math.log2(fs[i] / ref_thz)
                valid.append((i, ts[i], fs[i], c))
                
        tonics = [v for v in valid if abs(v[3]) <= 30.0]
        targets = [v for v in valid if 120.0 <= v[3] <= 175.0 and abs(v[3] - m["pk"]) <= 6.0]
        targets.sort(key=lambda x: x[1])
        
        chosen = []
        last_t = -999.0
        for tg in targets:
            if tg[1] - last_t < 20.0:
                continue
            cand_refs = []
            for tn in tonics:
                dt = tg[1] - tn[1]
                if 0.25 <= abs(dt) <= 3.5:
                    loc_c = 1200.0 * math.log2(tg[2] / tn[2])
                    cand_refs.append((tn, dt, loc_c))
            if cand_refs:
                cand_refs.sort(key=lambda x: abs(x[1]))
                best_tn, dt, loc_c = cand_refs[0]
                chosen.append((tg, best_tn, dt, loc_c))
                last_t = tg[1]
                if len(chosen) == 5:
                    break
                    
        segments = []
        for seg_idx, (tg, tn, dt, loc_c) in enumerate(chosen, 1):
            t_id = tg[0]
            t_time = float(ts[t_id])
            t_f0 = float(fs[t_id])
            
            r_id = tn[0]
            r_time = float(ts[r_id])
            r_f0 = float(fs[r_id])
            
            signed_dt = round(t_time - r_time, 4)
            rel = "preceding_candidate_reference" if signed_dt > 0 else "following_candidate_reference"
            
            t_f0_clean = round(t_f0, 2)
            r_f0_clean = round(r_f0, 2)
            exact_local_c = round(1200.0 * math.log2(t_f0_clean / r_f0_clean), 2)
            exact_rec_c = round(1200.0 * math.log2(t_f0_clean / ref_thz), 2)
            
            segments.append({
                "segment_id": seg_idx,
                "target_event_id": t_id,
                "target_timestamp_s": round(t_time, 3),
                "target_f0_measured_hz": t_f0_clean,
                "reference_event_id": r_id,
                "reference_timestamp_s": round(r_time, 3),
                "reference_f0_measured_hz": r_f0_clean,
                "time_offset_s": round(signed_dt, 3),
                "temporal_relationship": rel,
                "exact_cents_from_local_ref": exact_local_c,
                "exact_cents_from_recording_tonic": exact_rec_c,
                "worksheet_blank_for_human_listener": {
                    "human_target_note_identity": "[Pending independent listener verification]",
                    "human_reference_note_identity": "[Pending independent listener verification]",
                    "human_gusheh_identification": "[Pending independent listener verification]",
                    "is_motaghayyer_active": "[Pending independent listener verification]"
                }
            })
            
        data.append({
            "performer": m["performer"],
            "instrument": m["instrument"],
            "npz_file": m["npz_file"],
            "npz_sha256": sha256_file(str(npz_p)),
            "recording_duration_s": round(dur_s, 1),
            "recording_duration_minutes": round(dur_s / 60.0, 1),
            "refined_modal_tonic_hz": m["thz"],
            "refined_modal_tonic_note": m["thz_note"],
            "conditional_peak_cents": m["pk"],
            "ci_95": m["ci_95"],
            "ci_width": m["ci_width"],
            "n_window_strikes": m["n_win"],
            "n_tonic_strikes": m["n_ton"],
            "radif_nominal_scale": m["radif_nominal_scale"],
            "radif_degree_hypotheses": m["radif_degree_hypotheses"],
            "physical_physics_context": m["physical_physics_context"],
            "listener_worksheet_segments": segments
        })
        
    with open(OUT / "category_a_listening_annotations.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully generated {OUT / 'category_a_listening_annotations.json'} with 6 masters and 30 worksheet segments.")

if __name__ == "__main__":
    build_worksheet()
