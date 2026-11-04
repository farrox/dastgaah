#!/usr/bin/env python3
"""Independent Mathematical Audit of Talā'ī Dāng Model Ratios, Cents, and Step Discrepancies.
Implements the calculations specified in GPT-6 Guide GPT6-DANG-AUDIT-20261104-0012-PST
and verified in the peer review of 2026-11-04.

Outputs:
  - Exact fractions and log2 cents calculations
  - Template step sums and pure fourth comparisons (498.045¢ vs 500¢)
  - Segāh transposition analysis (39/32 = 342.48¢ vs 27/22 = 354.55¢, diff = 12.06¢)
  - Step sum discrepancies (494¢ and 493¢ vs 498.05¢)
  - Exports analysis/dang_model_math_audit.json
"""

import json
import math
from fractions import Fraction
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent

def c(frac: Fraction) -> float:
    """Exact interval in cents from Fraction."""
    return 1200.0 * math.log2(float(frac))

def step_cents(p1: Fraction, p2: Fraction) -> float:
    """Cents interval between two pitch ratios."""
    return 1200.0 * math.log2(float(p2 / p1))

def run_math_audit():
    audit = {}

    # 1. Tetrachord Definitions & Pure Fourth Spans
    f_4th = Fraction(4, 3)
    span_4th = c(f_4th) # 498.044999...

    # Shūr: [1, 13/12, 32/27, 4/3]
    shur_ratios = [Fraction(1, 1), Fraction(13, 12), Fraction(32, 27), Fraction(4, 3)]
    shur_steps = [
        step_cents(shur_ratios[0], shur_ratios[1]), # 13/12 = 138.57¢
        step_cents(shur_ratios[1], shur_ratios[2]), # 32/27 / 13/12 = 128/117 = 155.56¢
        step_cents(shur_ratios[2], shur_ratios[3]), # 4/3 / 32/27 = 9/8 = 203.91¢
    ]
    shur_step_ratios = [
        str(shur_ratios[1] / shur_ratios[0]),
        str(shur_ratios[2] / shur_ratios[1]),
        str(shur_ratios[3] / shur_ratios[2])
    ]

    # Māhūr Pythagorean: [1, 9/8, 81/64, 4/3]
    mahur_pyth = [Fraction(1, 1), Fraction(9, 8), Fraction(81, 64), Fraction(4, 3)]
    mahur_pyth_steps = [
        step_cents(mahur_pyth[0], mahur_pyth[1]), # 9/8 = 203.91¢
        step_cents(mahur_pyth[1], mahur_pyth[2]), # 81/64 / 9/8 = 9/8 = 203.91¢
        step_cents(mahur_pyth[2], mahur_pyth[3]), # 4/3 / 81/64 = 256/243 = 90.22¢
    ]

    # Māhūr Just: [1, 9/8, 5/4, 4/3]
    mahur_just = [Fraction(1, 1), Fraction(9, 8), Fraction(5, 4), Fraction(4, 3)]
    mahur_just_steps = [
        step_cents(mahur_just[0], mahur_just[1]), # 9/8 = 203.91¢
        step_cents(mahur_just[1], mahur_just[2]), # 5/4 / 9/8 = 10/9 = 182.40¢
        step_cents(mahur_just[2], mahur_just[3]), # 4/3 / 5/4 = 16/15 = 111.73¢
    ]

    # Chahārgāh Chart (with 81/64): [1, 13/12, 81/64, 4/3]
    chah_chart = [Fraction(1, 1), Fraction(13, 12), Fraction(81, 64), Fraction(4, 3)]
    chah_chart_steps = [
        step_cents(chah_chart[0], chah_chart[1]), # 13/12 = 138.57¢
        step_cents(chah_chart[1], chah_chart[2]), # 81/64 / 13/12 = 243/208 = 269.25¢
        step_cents(chah_chart[2], chah_chart[3]), # 4/3 / 81/64 = 256/243 = 90.22¢
    ]

    # Chahārgāh Mofakham / Just: [1, 13/12, 5/4, 4/3]
    chah_just = [Fraction(1, 1), Fraction(13, 12), Fraction(5, 4), Fraction(4, 3)]
    chah_just_steps = [
        step_cents(chah_just[0], chah_just[1]), # 13/12 = 138.57¢
        step_cents(chah_just[1], chah_just[2]), # 5/4 / 13/12 = 15/13 = 247.74¢
        step_cents(chah_just[2], chah_just[3]), # 4/3 / 5/4 = 16/15 = 111.73¢
    ]

    # Bayāt-e Eṣfahān: [1, 9/8, 32/27, 4/3]
    esf_chart = [Fraction(1, 1), Fraction(9, 8), Fraction(32, 27), Fraction(4, 3)]
    esf_steps = [
        step_cents(esf_chart[0], esf_chart[1]), # 9/8 = 203.91¢
        step_cents(esf_chart[1], esf_chart[2]), # 32/27 / 9/8 = 256/243 = 90.22¢
        step_cents(esf_chart[2], esf_chart[3]), # 4/3 / 32/27 = 9/8 = 203.91¢
    ]

    audit["tetrachords"] = {
        "pure_fourth_span_cents": round(span_4th, 4),
        "shur": {
            "ratios": [str(x) for x in shur_ratios],
            "step_ratios": shur_step_ratios,
            "step_cents": [round(x, 2) for x in shur_steps],
            "sum_cents": round(sum(shur_steps), 4),
            "talai_reported": [140, 140, 220],
            "talai_sum": 500,
            "discrepancy_vs_talai": [round(shur_steps[0] - 140, 2), round(shur_steps[1] - 140, 2), round(shur_steps[2] - 220, 2)]
        },
        "mahur_pythagorean": {
            "ratios": [str(x) for x in mahur_pyth],
            "step_ratios": ["9/8", "9/8", "256/243"],
            "step_cents": [round(x, 2) for x in mahur_pyth_steps],
            "sum_cents": round(sum(mahur_pyth_steps), 4),
            "talai_reported": [200, 180, 120],
            "talai_sum": 500,
            "discrepancy_vs_talai": [round(mahur_pyth_steps[0] - 200, 2), round(mahur_pyth_steps[1] - 180, 2), round(mahur_pyth_steps[2] - 120, 2)],
            "third_degree_cents": round(c(Fraction(81, 64)), 2),
            "third_degree_vs_talai_380": round(c(Fraction(81, 64)) - 380.0, 2)
        },
        "mahur_just": {
            "ratios": [str(x) for x in mahur_just],
            "step_ratios": ["9/8", "10/9", "16/15"],
            "step_cents": [round(x, 2) for x in mahur_just_steps],
            "sum_cents": round(sum(mahur_just_steps), 4),
            "third_degree_cents": round(c(Fraction(5, 4)), 2),
            "third_degree_vs_talai_380": round(c(Fraction(5, 4)) - 380.0, 2)
        },
        "chahargah_chart": {
            "ratios": [str(x) for x in chah_chart],
            "step_ratios": ["13/12", "243/208", "256/243"],
            "step_cents": [round(x, 2) for x in chah_chart_steps],
            "sum_cents": round(sum(chah_chart_steps), 4),
            "talai_reported": [140, 240, 120],
            "talai_sum": 500,
            "discrepancy_vs_talai": [round(chah_chart_steps[0] - 140, 2), round(chah_chart_steps[1] - 240, 2), round(chah_chart_steps[2] - 120, 2)],
            "augmented_second_cents": round(chah_chart_steps[1], 2),
            "augmented_second_vs_talai_240": round(chah_chart_steps[1] - 240.0, 2)
        },
        "chahargah_just": {
            "ratios": [str(x) for x in chah_just],
            "step_ratios": ["13/12", "15/13", "16/15"],
            "step_cents": [round(x, 2) for x in chah_just_steps],
            "sum_cents": round(sum(chah_just_steps), 4),
            "augmented_second_cents": round(chah_just_steps[1], 2),
            "augmented_second_vs_talai_240": round(chah_just_steps[1] - 240.0, 2)
        },
        "esfahan": {
            "ratios": [str(x) for x in esf_chart],
            "step_ratios": ["9/8", "256/243", "9/8"],
            "step_cents": [round(x, 2) for x in esf_steps],
            "sum_cents": round(sum(esf_steps), 4)
        }
    }

    # 2. Segāh Mathematical Breakdown
    # Construction A: Literal transposition of Shūr to Re (9/8)
    re = Fraction(9, 8)
    literal_shur_on_re = [re * r for r in shur_ratios]
    # literal_shur_on_re: [9/8, 9/8 * 13/12, 9/8 * 32/27, 9/8 * 4/3]
    # = [9/8, 117/96 = 39/32, 4/3, 3/2]
    c_39_32 = c(Fraction(39, 32))
    c_27_22 = c(Fraction(27, 22))
    diff_27_22_minus_39_32 = c_27_22 - c_39_32

    # Construction B: Retuned model yielding 27/22
    # 9/8 * (12/11) = 27/22
    step_re_to_27_22 = c(Fraction(27, 22) / Fraction(9, 8)) # 12/11 = 150.64¢
    step_27_22_to_fa = c(Fraction(4, 3) / Fraction(27, 22))  # 88/81 = 143.50¢
    step_fa_to_sol = c(Fraction(3, 2) / Fraction(4, 3))     # 9/8 = 203.91¢
    retuned_segah_steps = [step_re_to_27_22, step_27_22_to_fa, step_fa_to_sol]

    # Construction C: Illustrative Pure-Fourth rooted at 27/22
    # 27/22, 4/3, 3/2, 18/11
    illustrative_segah_steps = [
        step_cents(Fraction(27, 22), Fraction(4, 3)),   # 88/81 = 143.50¢
        step_cents(Fraction(4, 3), Fraction(3, 2)),     # 9/8 = 203.91¢
        step_cents(Fraction(3, 2), Fraction(18, 11)),   # 12/11 = 150.64¢
    ]
    illustrative_span = c(Fraction(18, 11) / Fraction(27, 22)) # 4/3 = 498.05¢

    audit["segah_transposition"] = {
        "literal_transposition_of_shur": {
            "root": "9/8 (203.91¢)",
            "degree_2_ratio": "39/32",
            "degree_2_factorization": "(9/8) * (13/12) = 117/96 = 39/32",
            "degree_2_cents": round(c_39_32, 4),
            "degree_3_ratio": "4/3 (498.05¢)",
            "degree_4_ratio": "3/2 (701.96¢)"
        },
        "retuned_zalzal_model": {
            "root": "9/8 (203.91¢)",
            "degree_2_ratio": "27/22",
            "degree_2_factorization": "(9/8) * (12/11) = 27/22",
            "degree_2_cents": round(c_27_22, 4),
            "step_from_re_cents": round(step_re_to_27_22, 2),
            "step_to_fa_cents": round(step_27_22_to_fa, 2),
            "step_fa_to_sol_cents": round(step_fa_to_sol, 2),
            "sum_steps_cents": round(sum(retuned_segah_steps), 4)
        },
        "difference_between_models": {
            "cents_difference": round(diff_27_22_minus_39_32, 4),
            "ratio_quotient": str(Fraction(27, 22) / Fraction(39, 32)), # 288/286 = 144/143
            "mathematical_impossibility": "39/32 (342.48¢) and 27/22 (354.55¢) cannot share a single coordinate; 27/22 is NOT (9/8) * (13/12)."
        },
        "chart_sum_discrepancies": {
            "primer_page11_row7_text_sum": "144 + 204 + 146 = 494¢",
            "primer_page11_legend_sum": "141 + 211 + 141 = 493¢",
            "pure_fourth_exact": round(span_4th, 2),
            "gap_row7": round(494.0 - span_4th, 2),
            "gap_legend": round(493.0 - span_4th, 2),
            "max_rounding_error_bound_for_3_integers": 1.5,
            "conclusion": "Neither 494¢ nor 493¢ can be explained by nearest-integer rounding (max error 1.5¢). They represent defective step calculations."
        },
        "illustrative_pure_fourth_rooted_at_27_22": {
            "ratios": ["27/22", "4/3", "3/2", "18/11"],
            "steps_cents": [round(x, 2) for x in illustrative_segah_steps],
            "total_span_cents": round(illustrative_span, 4),
            "spans_pure_fourth": True
        }
    }

    # 3. Conjunct vs. Disjunct Architecture
    conjunct_span = c(Fraction(4, 3) * Fraction(4, 3)) # 16/9 = 996.09¢
    disjunct_span = c(Fraction(4, 3) * Fraction(9, 8) * Fraction(4, 3)) # 2/1 = 1200.0¢

    audit["architecture"] = {
        "conjunct_two_fourths": {
            "formula": "(4/3) * (4/3) = 16/9",
            "cents": round(conjunct_span, 4),
            "semitone_short_of_octave": round(1200.0 - conjunct_span, 4)
        },
        "disjunct_two_fourths_separated_by_tone": {
            "formula": "(4/3) * (9/8) * (4/3) = 2/1",
            "cents": round(disjunct_span, 4),
            "equals_octave": True
        }
    }

    # Save to JSON
    out_path = OUT_DIR / "dang_model_math_audit.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2, ensure_ascii=False)
    print(f"Saved audit output to {out_path}")
    return audit

if __name__ == "__main__":
    run_math_audit()

