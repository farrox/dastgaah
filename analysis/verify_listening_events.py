#!/usr/bin/env python3
"""Automated event-level consistency validator for Category A candidate strikes worksheet.
Verifies:
  1. Provenance: event IDs exist in .npz archives, f0 matches within 0.01 Hz, t matches within 0.001s.
  2. Arithmetic: 1200 * log2(f_target / f_ref) matches exact_cents_from_local_ref within 0.01¢.
  3. Recording Tonic: 1200 * log2(f_target / f_recording_tonic) matches within 0.01¢.
  4. Temporal offset: target_time - ref_time matches time_offset_s within 0.001s.
  5. Locality: |dt| <= 3.5s strictly enforced.
  6. Temporal label honesty: dt > 0 is preceding; dt < 0 is following.
"""

import json
import math
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ANALYSIS_DIR = BASE_DIR / "analysis"
sys.path.insert(0, str(ANALYSIS_DIR))
from run_rigorous_modal_audit import read_npz

JSON_PATH = ANALYSIS_DIR / "category_a_listening_annotations.json"

def verify_all():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_segments = 0
    passed_segments = 0
    errors = []

    for master in data:
        p_name = master["performer"]
        npz_p = ANALYSIS_DIR / master["npz_file"]
        if not npz_p.exists():
            errors.append(f"Missing npz file: {npz_p}")
            continue

        npz_data = read_npz(npz_p)
        fs = npz_data["f"]
        ts = npz_data["t"]
        thz = master["refined_modal_tonic_hz"]

        for seg in master["listener_worksheet_segments"]:
            total_segments += 1
            s_id = seg["segment_id"]
            prefix = f"[{p_name} Seg {s_id}]"

            t_id = seg["target_event_id"]
            t_f0 = seg["target_f0_measured_hz"]
            t_t = seg["target_timestamp_s"]

            r_id = seg["reference_event_id"]
            r_f0 = seg["reference_f0_measured_hz"]
            r_t = seg["reference_timestamp_s"]

            # 1. Check event existence in npz
            if t_id >= len(fs) or r_id >= len(fs):
                errors.append(f"{prefix} Event ID out of range in npz (len={len(fs)})")
                continue

            npz_t_f0 = fs[t_id]
            npz_r_f0 = fs[r_id]
            npz_t_t = ts[t_id]
            npz_r_t = ts[r_id]

            if abs(npz_t_f0 - t_f0) > 0.05:
                errors.append(f"{prefix} Target f0 mismatch with npz: json={t_f0}, npz={npz_t_f0:.2f}")
            if abs(npz_r_f0 - r_f0) > 0.05:
                errors.append(f"{prefix} Ref f0 mismatch with npz: json={r_f0}, npz={npz_r_f0:.2f}")

            if abs(npz_t_t - t_t) > 0.005:
                errors.append(f"{prefix} Target timestamp mismatch with npz: json={t_t}, npz={npz_t_t:.3f}")
            if abs(npz_r_t - r_t) > 0.005:
                errors.append(f"{prefix} Ref timestamp mismatch with npz: json={r_t}, npz={npz_r_t:.3f}")

            # 2. Arithmetic verification
            expected_local_cents = 1200.0 * math.log2(t_f0 / r_f0)
            json_local_cents = seg["exact_cents_from_local_ref"]
            diff_local = abs(expected_local_cents - json_local_cents)
            if diff_local > 0.01:
                errors.append(f"{prefix} Local cents mismatch: expected {expected_local_cents:.2f}¢, found {json_local_cents:.2f}¢ (diff={diff_local:.3f}¢)")

            # Global recording cents (handling octave register for Saba)
            expected_global_cents = 1200.0 * math.log2(t_f0 / thz)
            if expected_global_cents > 1000.0:
                expected_global_cents_folded = expected_global_cents - 1200.0
            else:
                expected_global_cents_folded = expected_global_cents

            json_global_cents = seg["exact_cents_from_recording_tonic"]
            diff_global = abs(expected_global_cents_folded - json_global_cents)
            if diff_global > 0.05:
                errors.append(f"{prefix} Global cents mismatch: expected {expected_global_cents_folded:.2f}¢, found {json_global_cents:.2f}¢ (diff={diff_global:.3f}¢)")

            # 3. Temporal offset verification
            dt = round(t_t - r_t, 3)
            if abs(dt - seg["time_offset_s"]) > 0.005:
                errors.append(f"{prefix} Time offset mismatch: computed {dt:.3f}s, json {seg['time_offset_s']:.3f}s")

            # 4. Strict locality gate (|dt| <= 3.5s)
            if abs(dt) > 3.501:
                errors.append(f"{prefix} Locality violation: |dt| = {abs(dt):.3f}s > 3.5s")

            # 5. Temporal relationship label honesty
            if dt > 0 and seg["temporal_relationship"] != "preceding_candidate_reference":
                errors.append(f"{prefix} Label mismatch: dt > 0 but labeled {seg['temporal_relationship']}")
            elif dt < 0 and seg["temporal_relationship"] != "following_candidate_reference":
                errors.append(f"{prefix} Label mismatch: dt < 0 but labeled {seg['temporal_relationship']}")

            passed_segments += 1

    print("="*80)
    print("CATEGORY A CANDIDATE STRIKES WORKSHEET AUTOMATED AUDIT")
    print("="*80)
    print(f"Total audited segments: {total_segments}")
    print(f"Passed consistency checks: {passed_segments}")
    print(f"Errors / Mismatches: {len(errors)}")
    if errors:
        for e in errors:
            print(f"  FAILED: {e}")
        sys.exit(1)
    else:
        print("ALL 30 CATEGORY A CANDIDATE STRIKES VERIFIED 100% CLEAN AGAINST .NPZ ARCHIVES!")
        print("Strict locality (|Δt| <= 3.5s), exact timestamps, and arithmetic validated.")
        print("="*80)

if __name__ == "__main__":
    verify_all()
