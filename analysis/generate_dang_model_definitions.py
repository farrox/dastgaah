#!/usr/bin/env python3
"""Generate Separate 3-Layer Machine-Readable Model Definitions for Dāng Theory.
Implements the 3-layer architecture required by Guide GPT6-DANG-AUDIT-20261104-0012-PST:
  - Layer 1: Source-Faithful Structural Models (Talā'ī approximate descriptions on a ~20¢ grid, 500¢ fourths)
  - Layer 2: Rational Tuning Realizations (Exact pure ratios with pure 4th spans of 498.05¢)
  - Layer 3: Empirical Observations (Extracted directly from analysis/*.json per recording)

Includes the peer reviewer's additions:
  - Source precision field: "~20¢ grid, self-described as personal judgement (Talai 2015 p. 22 via S2 p. 93 [unverified page citation])"
  - View C populated per recording from verified JSON outputs
Exports to analysis/dang_model_definitions.json
"""

import json
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent

def build_model_definitions():
    # 1. Load empirical sources
    with open(OUT_DIR / "re_koron_modal_peak_audit.json", encoding="utf-8") as f:
        re_koron_data = json.load(f)

    with open(OUT_DIR / "segah_consensus.json", encoding="utf-8") as f:
        segah_data = json.load(f)

    with open(OUT_DIR / "shur_consensus.json", encoding="utf-8") as f:
        shur_data = json.load(f)

    with open(OUT_DIR / "consensus_template.json", encoding="utf-8") as f:
        mahur_data = json.load(f)

    # Layer 1: Source-Faithful Models (Talā'ī 1993/2015 via S1, S2, S3)
    source_models = {
        "metadata": {
            "author": "Dariush Talā'ī",
            "source_editions_referenced": [
                "Negareshi no be teori-ye musiqi-ye Irani (1993, cited in S1 p. 17 and S2 p. 92)",
                "Tahlil-e Radif (2015 p. 22, cited in S2 p. 93 [unverified page citation])"
            ],
            "precision": "~20¢ grid, self-described as personal judgement (Talai 2015 p. 22 via S2 p. 93 [unverified page citation])",
            "fourth_definition": "Heuristic interval sum to 500¢ (not rescaled to pure 4th)"
        },
        "primary_dangs": {
            "mahur": {
                "name": "Dāng-e Māhūr",
                "intervals_cents": [200, 180, 120],
                "total_cents": 500,
                "pattern": "Whole Tone (T) + Whole Tone (T) + Semitone (S)",
                "source_evidence": "S1 Fig. 10; S2 p. 92"
            },
            "shur": {
                "name": "Dāng-e Shūr",
                "intervals_cents": [140, 140, 220],
                "total_cents": 500,
                "pattern": "Neutral 2nd (N) + Neutral 2nd (N) + Greater Whole Tone (T+)",
                "source_evidence": "S1 Fig. 10; S2 p. 92"
            },
            "chahargah": {
                "name": "Dāng-e Chahārgāh",
                "intervals_cents": [140, 240, 120],
                "total_cents": 500,
                "pattern": "Neutral 2nd (N) + Augmented 2nd (A) + Semitone (S)",
                "source_evidence": "S1 Fig. 10; S2 p. 92"
            },
            "nava_or_dashti": {
                "name": "Dāng-e Navā (S2) / Dashti (S1)",
                "intervals_cents": [200, 80, 220],
                "total_cents": 500,
                "pattern": "Whole Tone (T) + Limma/Semitone (S) + Greater Whole Tone (T+)",
                "source_evidence": "S1 Fig. 10 (labeled Dashti); S2 p. 92 (labeled Nava)",
                "unresolved_issue": "Edition-specific naming (Nava vs Dashti); middle step is 80¢, not a neutral step."
            }
        },
        "modal_architecture_rules": {
            "mahur_do_dangi": {
                "structure": "Conjunct (G-A-B-C + C-D-E-F)",
                "shared_boundary_note": "C",
                "total_span": "16/9 (approx 1000¢) or octave with lower extension",
                "source_evidence": "S2 p. 93 explicitly demonstrates conjunct do-dangi"
            },
            "segah_derivation": {
                "concept": "Step-shift: Shūr dāng rooted on Re (+204¢) yields resting note on Mi-koron",
                "source_evidence": "Talā'ī 1993 p. 23 (via S1 p. 17); S2 p. 92",
                "unresolved_issue": "Literal transposition gives 342.5¢ (39/32), whereas Zalzal fret gives 354.5¢ (27/22)."
            }
        }
    }

    # Layer 2: Rational Tuning Realizations (Exact Pure Ratios)
    rational_models = {
        "metadata": {
            "model_type": "Rational Just Intonation and Pythagorean Constructions",
            "pure_fourth_cents": 498.045,
            "rule": "Every step is derived as the quotient of consecutive pitch ratios; sum strictly equals 4/3 (498.045¢)"
        },
        "tetrachords": {
            "shur_pure": {
                "ratios": ["1/1", "13/12", "32/27", "4/3"],
                "step_ratios": ["13/12", "128/117", "9/8"],
                "step_cents": [138.57, 155.56, 203.91],
                "total_cents": 498.045
            },
            "mahur_pythagorean": {
                "ratios": ["1/1", "9/8", "81/64", "4/3"],
                "step_ratios": ["9/8", "9/8", "256/243"],
                "step_cents": [203.91, 203.91, 90.22],
                "total_cents": 498.045
            },
            "mahur_just": {
                "ratios": ["1/1", "9/8", "5/4", "4/3"],
                "step_ratios": ["9/8", "10/9", "16/15"],
                "step_cents": [203.91, 182.40, 111.73],
                "total_cents": 498.045
            },
            "chahargah_pythagorean_third": {
                "ratios": ["1/1", "13/12", "81/64", "4/3"],
                "step_ratios": ["13/12", "243/208", "256/243"],
                "step_cents": [138.57, 269.25, 90.22],
                "total_cents": 498.045
            },
            "chahargah_mofakham_just": {
                "ratios": ["1/1", "13/12", "5/4", "4/3"],
                "step_ratios": ["13/12", "15/13", "16/15"],
                "step_cents": [138.57, 247.74, 111.73],
                "total_cents": 498.045
            },
            "esfahan_minor": {
                "ratios": ["1/1", "9/8", "32/27", "4/3"],
                "step_ratios": ["9/8", "256/243", "9/8"],
                "step_cents": [203.91, 90.22, 203.91],
                "total_cents": 498.045
            }
        },
        "segah_variants": {
            "variant_A_literal_shur_transposition": {
                "description": "Literal transposition of Shūr [1, 13/12, 32/27, 4/3] to Re (9/8)",
                "ratios_from_do": ["9/8", "39/32", "4/3", "3/2"],
                "cents_from_do": [203.91, 342.48, 498.05, 701.96],
                "step_cents": [138.57, 155.56, 203.91],
                "total_cents": 498.045,
                "note_on_mi_koron": "39/32 = 342.48¢"
            },
            "variant_B_retuned_zalzal_model": {
                "description": "Retuned model rooted on Re (9/8) yielding Zalzal 27/22 on Mi-koron",
                "ratios_from_do": ["9/8", "27/22", "4/3", "3/2"],
                "cents_from_do": [203.91, 354.55, 498.05, 701.96],
                "step_cents": [150.64, 143.50, 203.91],
                "total_cents": 498.045,
                "note_on_mi_koron": "27/22 = 354.55¢"
            },
            "variant_C_pure_fourth_rooted_on_zalzal": {
                "description": "Illustrative pure fourth rooted at Mi-koron (27/22)",
                "ratios_from_do": ["27/22", "4/3", "3/2", "18/11"],
                "cents_from_do": [354.55, 498.05, 701.96, 852.59],
                "step_cents": [143.50, 203.91, 150.64],
                "total_cents": 498.045
            }
        }
    }

    # Layer 3: Empirical Observations (Per-Recording from Verified JSONs)
    # 1. Shur 2nd degree (Category A masters from re_koron_modal_peak_audit.json)
    shur_2nd_obs = []
    for r in re_koron_data:
        if r["category"].startswith("Category A"):
            shur_2nd_obs.append({
                "performer": r["name"],
                "instrument": r["instrument"],
                "peak_cents": r["peak_cents"],
                "ci_95": r["ci_95"],
                "ci_width": r["ci_width"],
                "n_window_strikes": r["n_window_total"],
                "n_tonic_strikes": r["n_tonic"]
            })

    # 2. Mahur 3rd degree per artist (from consensus_template.json slot 12: Mi)
    mahur_3rd_artist = mahur_data["slots"][12]["per_artist"]

    # 3. Segah degrees (from segah_consensus.json)
    segah_degrees = {}
    for deg_key, deg_info in segah_data["consensus"].items():
        segah_degrees[deg_key] = {
            "label": deg_info["label"],
            "raw_median_cents": deg_info["consensus_median_raw"],
            "ist_normalized_median_cents": deg_info["ist_normalized_median"],
            "total_strikes": deg_info["strikes"],
            "active_masters": deg_info["masters"]
        }

    empirical_models = {
        "metadata": {
            "description": "Acoustic observations extracted from master recordings without theoretical forcing",
            "status": "Acoustic peak estimates conditional on assigned reference tonics; musical note identities pending human listener verification"
        },
        "shur_second_degree_re_koron": {
            "per_recording_category_a": shur_2nd_obs,
            "clusters": {
                "cluster_1_approx_128": ["Safvat (127.5¢)", "Shahnazi (128.0¢)", "Saba (129.0¢)"],
                "cluster_2_approx_138_5": ["Nariman (138.5¢)"],
                "cluster_3_approx_150_154": ["Foroutan (150.5¢)", "Alizadeh (153.5¢)"]
            }
        },
        "shur_third_degree_mi_flat": {
            "raw_consensus_median_cents": shur_data["consensus"]["minor_3rd"]["consensus_median_cents"],
            "ist_tonic_raw_cents": shur_data["consensus"]["ist_tonic"]["consensus_median_cents"],
            "ist_normalized_median_cents": round(shur_data["consensus"]["minor_3rd"]["consensus_median_cents"] - shur_data["consensus"]["ist_tonic"]["consensus_median_cents"], 2),
            "distance_from_32_27": round(294.13 - (shur_data["consensus"]["minor_3rd"]["consensus_median_cents"] - shur_data["consensus"]["ist_tonic"]["consensus_median_cents"]), 2),
            "distance_from_13_11": round((shur_data["consensus"]["minor_3rd"]["consensus_median_cents"] - shur_data["consensus"]["ist_tonic"]["consensus_median_cents"]) - 289.21, 2)
        },
        "mahur_third_degree_mi": {
            "per_artist_cents": mahur_3rd_artist,
            "min_artist": {"artist": "Shekarchi", "cents": 367.7},
            "just_5_4_cluster": [
                {"artist": "Saba", "cents": 386.6},
                {"artist": "Nariman", "cents": 386.9}
            ],
            "pythagorean_81_64_cluster": [
                {"artist": "Forutan", "cents": 400.8},
                {"artist": "Lotfi", "cents": 402.9},
                {"artist": "Shahnazi", "cents": 403.2},
                {"artist": "Kasaei", "cents": 406.5},
                {"artist": "Ebadi", "cents": 412.0},
                {"artist": "Borumand", "cents": 414.7}
            ],
            "conclusion": "The empirical data side with 81/64 (407.8¢) over Talā'ī's 380¢ description; 6 masters sit within ~7¢ of Pythagorean 81/64."
        },
        "segah_degrees": {
            "zabol_fa_second_degree": {
                "ist_normalized_median_cents": segah_degrees["zabol_fa"]["ist_normalized_median_cents"],
                "strikes": segah_degrees["zabol_fa"]["total_strikes"],
                "distance_from_13_12": round(segah_degrees["zabol_fa"]["ist_normalized_median_cents"] - 138.57, 2),
                "distance_from_talai_140": round(segah_degrees["zabol_fa"]["ist_normalized_median_cents"] - 140.0, 2)
            },
            "muye_sol_third_degree": {
                "ist_normalized_median_cents": segah_degrees["muye_sol"]["ist_normalized_median_cents"],
                "strikes": segah_degrees["muye_sol"]["total_strikes"],
                "distance_from_27_22": round(abs(segah_degrees["muye_sol"]["ist_normalized_median_cents"] - 354.55), 2),
                "distance_from_39_32": round(abs(segah_degrees["muye_sol"]["ist_normalized_median_cents"] - 342.48), 2),
                "conclusion": "Empirical Mūyeh at +352.7¢ sits 1.85¢ from Zalzal 27/22 (354.55¢) and 10.22¢ from 39/32 (342.48¢), strongly favoring the retuned 27/22 construction."
            }
        }
    }

    full_definitions = {
        "title": "Three-Layer Machine-Readable Model Definitions for Dāng Theory and Intonation",
        "guide_reference": "GPT6-DANG-AUDIT-20261104-0012-PST",
        "peer_review_reference": "Review 2026-11-04 on Talai Dang Theory Analysis and Correction Guide",
        "layer_1_source_models": source_models,
        "layer_2_rational_models": rational_models,
        "layer_3_empirical_observations": empirical_models
    }

    out_path = OUT_DIR / "dang_model_definitions.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(full_definitions, f, indent=2, ensure_ascii=False)
    print(f"Saved complete 3-layer definitions to {out_path}")
    return full_definitions

if __name__ == "__main__":
    build_model_definitions()
