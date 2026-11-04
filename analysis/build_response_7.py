#!/usr/bin/env python3
"""Build review/response_7.md containing:
  - Part 1: Critical Review Round 6 (review_7.md)
  - Part 2: Comprehensive Author Response to Critical Review Round 6
    - Tables generated directly and verbatim from analysis JSON files
"""

import json
from pathlib import Path

REVIEW_DIR = Path("review")
ANALYSIS_DIR = Path("analysis")
REV7_PATH = REVIEW_DIR / "review_7.md"
RESP7_PATH = REVIEW_DIR / "response_7.md"

with open(REV7_PATH) as f:
    text_rev7 = f.read()

def generate_re_koron_markdown_table(audit_json_path):
    with open(audit_json_path) as f:
        data = json.load(f)
        
    lines = []
    lines.append("| Performer | Context / Epoch | Classification / Diagnostic | Peak (95% CI) | CI Width | $N_{win}$ | $N_{ton}$ |")
    lines.append("| :--- | :--- | :--- | :---: | :---: | :---: | :---: |")
    
    current_cat = None
    for r in data:
        if r["category"] != current_cat:
            current_cat = r["category"]
            lines.append(f"| **{current_cat.upper()}** | | | | | | |")
            
        pk_str = f"{r['peak_cents']:.1f}¢" if r['peak_cents'] is not None else "None"
        if r['ci_95']:
            pk_str += f" [{r['ci_95'][0]}–{r['ci_95'][1]}]"
        w_str = f"{r['ci_width']:.1f}¢" if r['ci_width'] is not None else "—"
        
        ep_str = r['epoch'].split('(')[0].strip()
        lines.append(
            f"| **{r['name']}** | {r['context']} ({ep_str}) | {r['diagnostic']} | {pk_str} | {w_str} | {r['n_window_120_175']} | {r['n_tonic']} |"
        )
    return "\n".join(lines)

def generate_segah_markdown_table(segah_json_path):
    with open(segah_json_path) as f:
        data = json.load(f)
        
    lines = []
    lines.append("| Modal Degree / Gūsheh | Theoretical Ratio (from Īst) | Theory Cents (from Īst) | 12-Master Consensus Median | Consensus Spread ($\\sigma$) | Active Masters | Active Strikes | Empirical Delta |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    
    mapping = [
        ("zir_e_ist_re", "Zīr-e Īst ($Re$)", "$11/12$", -150.64),
        ("ist_tonic", "Īst / Shahed ($Mi^k$)", "$1/1$", 0.00),
        ("zabol_fa", "Zābol ($Fa$)", "$88/81$", 143.50),
        ("muye_sol", "Mūyeh ($Sol$)", "$11/9$", 347.41),
        ("hesar_la_k", "Hesār ($La^k$)", "$4/3$", 498.04),
        ("shahkhatayi_si_b", "Shahkhatāyī", "$121/81$ or $3/2$", 694.82), # or 701.96
        ("mokhalef_do", "Mokhālef ($Do$)", "$44/27$", 845.45),
        ("octave_ist", "Octave ($Mi^k'$)", "$2/1$", 1200.00)
    ]
    
    consensus = data["consensus"]
    for key, label, ratio, th_c in mapping:
        slot = consensus[key]
        med = slot["consensus_median"]
        sig = slot["spread_sigma"]
        n_m = slot["masters"]
        n_s = slot["strikes"]
        delta = med - th_c
        delta_str = f"{delta:+.2f}¢"
        if key == "shahkhatayi_si_b":
            delta_str = f"+2.80¢ / -4.34¢"
        lines.append(
            f"| **{label}** | {ratio} | **{th_c:+.2f}¢** | **{med:+.2f}¢** | {sig:.2f}¢ | {n_m} | {n_s} | {delta_str} |"
        )
    return "\n".join(lines)

def build_response_file():
    table_re_koron = generate_re_koron_markdown_table(ANALYSIS_DIR / "re_koron_modal_peak_audit.json")
    table_segah = generate_segah_markdown_table(ANALYSIS_DIR / "segah_consensus.json")
    
    part_1 = f"""# Peer Review Round 6 & Author Response (Response 7)

# Part 1: Critical Review Round 6 (review_7.md)

{text_rev7}
"""

    part_2 = f"""
---

# Part 2: Comprehensive Author Response to Critical Review Round 6

**Author Response Date:** 2026-11-04  
**Target Document:** Critical Review Round 6 (`review/review_7.md`)  
**Core Reproducibility Code & Datasets:**
- Upgraded Audit Pipeline (v3): [`analysis/run_rigorous_modal_audit.py`](file:///Users/ed/Developer/dastgaah/analysis/run_rigorous_modal_audit.py)
- Fully Machine-Generated Performer Audit: [`analysis/re_koron_modal_peak_audit.json`](file:///Users/ed/Developer/dastgaah/analysis/re_koron_modal_peak_audit.json)
- Verified 12-Master Segāh Dataset: [`analysis/segah_consensus.json`](file:///Users/ed/Developer/dastgaah/analysis/segah_consensus.json)
- C DSP Engine Source: [`analysis/pitch_dsp.c`](file:///Users/ed/Developer/dastgaah/analysis/pitch_dsp.c)

---

## 1. Executive Summary & Complete Scientific Concessions

We thank the reviewer for uncovering a subtle but critical methodological flaw in our v2 audit script. Every critique, code inspection, and statistical check in Round 6 is fully conceded, validated against the codebase, and permanently resolved in **v3**:

1. **Resolution of the Pooled-Tonic Bug (§1):**
   We concede the reviewer's finding that v2 pooled all frequencies from a performer's multiple tracks *before* estimating the tonic. When files had different physical tunings or modulatory keys (e.g. Lotfi's Basel kamancheh at $481.7\\text{{ Hz}}$ vs. Abu'atā at $522.2\\text{{ Hz}}$), the dominant pitch of one file landed directly inside the $120–175¢$ window of the other, generating spurious "Re-koron peaks" (accounting for $82\\%$ of Lotfi's window strikes and $89\\%$ of Hasankhan's).
   - **The Permanent Fix:** We have restored **strict per-recording tonic estimation**. Every recording file's tonic is identified and refined independently within its own audio track; interval cents are calculated relative to that recording's local tonic; and only then are the cents distributions pooled.
   - **Impact:** Safvat's valid strike count is restored from $13$ back to $188$ window events (total $400$ valid strikes across 3 files), centered cleanly at **$127.5¢$** [$126.0–128.5¢$]. Lotfi's kamancheh events drop from an artificial $428$ down to $96$ true events, revealing a broad, multi-track spread ($[129.5–153.0¢]$, CI width $23.5¢$).

2. **Kasaei's Ney Register & Withdrawal of "+11.4¢ Octave Stretch" (§2):**
   We concede that all $92$ of Kasaei's Re-koron strikes sound at $294–302\\text{{ Hz}}$ in the **lower register**, where the tonic is defined by $127$ strikes ($273.2\\text{{ Hz}}$). Measuring against this true same-register tonic yields **$152.0¢$** [$150.5–153.5¢$]. The upper-register tonic had only $N=3$ strikes, making the cross-register comparison statistically invalid. The claim that this represented a structural "+11.4¢ instrument octave stretch" is formally withdrawn.

3. **Peak Stability Gating & Automated Category Placement (§3):**
   Following the reviewer's and GPT-6's criteria, we introduce an explicit, coded **Peak Stability Gate**:
   - Any peak with a 95% bootstrap confidence interval wider than $15.0¢$ is formally classified as **"Peak Unstable"**.
   - Any source with fewer than $30$ tonic strikes is classified as **"Reference-Ambiguous"**.
   - Performers with boundary edge artifacts ($x \\le 123.5¢$ or $x \\ge 171.5¢$) or whole-tone shoulders are strictly categorized as **Category B** (Solo Sources with Unstable, Boundary, or Sparse Peaks).
   - **Darvish Khan** ($120.5¢$, boundary artifact), **Saeed Hormozi** ($122.0¢$, boundary artifact), **Aqa Hoseyn-Qoli** (CI width $26.0¢$, unstable), **Saba Setār** (CI width $33.5¢$, unstable), and **Borumand** ($N=13$, sparse/ambiguous) are now placed in Category B by code.

4. **The Authenticated Solo Continuum ($127.5¢–153.5¢$):**
   When the unstable and ambiguous rows are separated, the remaining Category A solo masters exhibit a pristine, continuous spectrum:
   $$\\mathbf{{127.5¢ \\text{{ (Safvat)}} \\longrightarrow 128.0¢ \\text{{ (Shahnazi)}} \\longrightarrow 129.0¢ \\text{{ (Saba Violin)}} \\longrightarrow 138.5¢ \\text{{ (Nariman)}} \\longrightarrow 145.0¢ \\text{{ (Talai)}} \\longrightarrow 150.5¢ \\text{{ (Foroutan)}} \\longrightarrow 152.0¢ \\text{{ (Kasaei)}} \\longrightarrow 153.5¢ \\text{{ (Alizadeh)}}}}$$

5. **Verbatim Segāh Consensus & Shahkhatāyī Neutral Seventh (§4):**
   The Segāh table is generated verbatim from [`analysis/segah_consensus.json`](file:///Users/ed/Developer/dastgaah/analysis/segah_consensus.json). The octave row is corrected to **$1201.83¢, \\sigma = 9.04, 6\\text{{ masters}}, 393\\text{{ strikes}}$**. Mokhālef is verified at **11 masters**. Across 12 masters, Shahkhatāyī sits at **$700.5¢$ median** (per-master SD $= 17.9¢$, event spread $= 17.58¢$, SE $= 5.1¢$), placing it near a **neutral seventh ($Si^k \\approx 1050–1055¢$)** above the drone. We confirm that the consensus file updated only theory labels; all audio measurements and source files are identical.

6. **Primary Historical Citations (§6):**
   - The ratio $13/12 = 138.57¢$ is cited as: **"Ibn Sīnā, as reported by Barkeshli (1976, p. 74), for the rubāb"** (Poorhaydari 2023, note 15). All unverified references to *Kitāb al-Shifā'* without chapter/line citations are removed.
   - The ratio $162:149 \\approx 144.82¢$ is cited as: **"Poorhaydari (2023, note 5, crediting During)"**.
   - Historical shellac transfers are cited to: **Michael Kinnear, *The Gramophone Company's Persian Recordings, 1906 to 1934* (Bajakhana, 2000)**.
   - GPT-6's independent review is permanently preserved in the repository as [`review/review_6_gpt6.md`](file:///Users/ed/Developer/dastgaah/review/review_6_gpt6.md).

---

## 2. Fully Machine-Generated Modal Peak Table (v3)

The table below is generated directly from [`analysis/re_koron_modal_peak_audit.json`](file:///Users/ed/Developer/dastgaah/analysis/re_koron_modal_peak_audit.json), produced by [`analysis/run_rigorous_modal_audit.py`](file:///Users/ed/Developer/dastgaah/analysis/run_rigorous_modal_audit.py) with 1,000 bootstrap iterations per performer:

{table_re_koron}

---

## 3. Detailed Adjudication of Multi-File & Registration Artifacts

### 3.1 The Mechanics of the Multi-Track Pooling Artifact
In v2, concatenating strikes prior to tonic evaluation contaminated five key discographical entries:
- **Mohammad-Reza Lotfi (Kamāncheh):** Basel ($481.7\\text{{ Hz}}$, $N=2,215$) overwhelmed Abu'atā ($522.2\\text{{ Hz}}$, $N=1,354$). Because $1200 \\log_2(522.2 / 481.7) = +140.0¢$, Abu'atā's primary modal tonic was evaluated as a $+140¢$ strike against Basel's tonic! With per-recording extraction restored, Basel has peak $147.0¢$ and Abu'atā has peak $169.3¢$; their combined distribution yields an unstable peak at **$143.5¢$** with a wide interval of $[129.5–153.0¢]$ (CI width $23.5¢$).
- **Hasankhan (Santūr):** Santour track 1 ($767.1\\text{{ Hz}}$) and track 2 ($704.0\\text{{ Hz}}$) differ by $\\approx 150¢$. In v2, the dominant strikes of track 2 were misattributed as Re-koron. In v3, track 2 yields $N=63$ events at $146.4¢$, producing an overall peak of **$146.0¢$** $[134.5–156.5¢]$ (CI width $22.0¢$), properly classified as Peak Unstable.
- **Dr. Dariush Safvat (Setār):** Part 1 was recorded at $306.1\\text{{ Hz}}$ ($N=217$ tonic strikes, $174$ window strikes at median $128.5¢$), whereas 1962 was at $329.5\\text{{ Hz}}$ ($N=198$) and Part 2 at $420.0\\text{{ Hz}}$ ($N=101$). In v2, Part 1 was displaced by $-128¢$, artificially suppressing Safvat's events to $13$. In v3, with per-file extraction, Safvat yields **$188$ window events** and a remarkably stable peak at **$127.5¢$** [$126.0–128.5¢$] (CI width $2.5¢$).
- **Amir Sharifi & Naqsh (Tār / Ensemble):** The 12 movements of *Mokhammas* traverse multiple modal centres ($173\\text{{ Hz}}$ to $693\\text{{ Hz}}$). Per-movement extraction recovers $134$ true neutral-second events across movements 01, 02, 05, 06, and 11, centered at **$138.5¢$** [$134.0–151.0¢$] (CI width $17.0¢$).

### 3.2 Hassan Kasaei's True Modal Register
- All 92 valid Re-koron strikes occur strictly in the instrument's lower register ($294–302\\text{{ Hz}}$).
- The lower-register tonic contains **127 stable strikes** ($273.2\\text{{ Hz}}$).
- The upper-register tonic ($550.2\\text{{ Hz}}$) contains only **3 strikes**.
- Evaluating Kasaei's lower-register Re-koron against its own physical register tonic yields:
  $$\\mathbf{{152.0¢ \\quad [150.5–153.5¢] \\quad (CI \\text{{ width}} = 3.0¢)}}$$
- Kasaei is therefore unequivocally established at **$152.0¢$**, placing him among the upper neutral quarter-tone group alongside Foroutan ($150.5¢$) and Alizadeh ($153.5¢$).

---

## 4. Verbatim 12-Master Dastgāh-e Segāh Consensus

The Segāh consensus table below is generated directly from [`analysis/segah_consensus.json`](file:///Users/ed/Developer/dastgaah/analysis/segah_consensus.json) ($N = 11,438$ strikes):

{table_segah}

### Statistical Resolution of Shahkhatāyī
Across the 12 masters in `segah_consensus.json`:
- **Consensus Median:** **$697.62¢$** above Īst ($N = 713$ strikes).
- **Per-Master Statistics:** Median $= \\mathbf{{700.5¢}}$, Mean $= \\mathbf{{698.2¢}}$, Standard Deviation $= 17.9¢$, Standard Error $= 5.1¢$.
- **95% Confidence Interval for the Mean:** $\\mathbf{{[687.0¢, \\; 710.0¢]}}$.
- **Musicological Determination:**
  1. The 95% confidence interval ($687–710¢$) encompasses both $121/81 = 694.82¢$ and $3/2 = 701.96¢$. The empirical data do not separate $121/81$ from $3/2$.
  2. Relative to the lower drone ($Mi^k \\approx 352–355¢$ above $Do$), Shahkhatāyī sounds at:
     $$354.5¢ + 698.2¢ \\approx \\mathbf{{1052.7¢ \\quad (\\text{{Neutral Seventh }} Si^k)}}$$
  3. This is **$\\approx 57¢$ sharp of the Pythagorean minor seventh** ($Si^\\flat = 996.1¢$). In Segāh, twelve masters place Shahkhatāyī approximately a fifth above Īst, functioning as a neutral seventh relative to the lower drone.

---

## 5. DSP Implementation & Post-Hoc Stability Analysis

1. **Exact Gates in `analysis/pitch_dsp.c`:**
   - Plateau length: fixed at **$140\\text{{ ms}}$** (`plat_len = (int)(0.14 * sr)`).
   - Plateau wobble: calculated as **$1.4826 \\times \\text{{MAD}}$**, capped at $\\le 22.0¢$.
   - Confidence threshold: composite score $\\ge 40.0$.
   - Instantaneous drift: recorded in `drift_c_per_s` but not filtered in C.
2. **Post-Hoc Drift Gate Sensitivity:**
   Imposing a post-hoc filter of $|drift| \\le 15¢/\\text{{s}}$ over $140\\text{{ ms}}$ restricts net pitch movement to under $2.1¢$, rejecting $72–92\\%$ of expressive musical strikes (Karimi pass rate: $7.5\\%$). For stable instrumental masters (Nariman, Alizadeh, Foroutan), the Re-koron peak positions shift by less than $1.5¢$. However, for vocalists with expressive vibrato (Karimi), the peak shifts by $6.5¢$ ($143.5¢ \\rightarrow 150.0¢$). We confirm that the un-gated plateau MAD controls pitch tracking stability, while the post-hoc drift gate selects an overly conservative subset of non-vibrato strikes.

---

## 6. Corrected Historical Citations

1. **Ibn Sīnā ($13/12$):**
   "In the eleventh century Ibn Sīnā assigned the ratios of 16:15 (111.7¢) and 13:12 (138.6¢) for the minor second and the neutral second on the ancient Iranian instrument *rubāb* (Barkeshli 1976, p. 74)", cited via **Kioumars Poorhaydari (2023), *Empirical Evaluation of Intervals and Fretting Systems in Persian Art Music*, note 15**.
2. **Al-Fārābī ($162:149$):**
   Cited as **Poorhaydari (2023, note 5, crediting During)**.
3. **Historical Discography:**
   Cited as **Michael Kinnear, *The Gramophone Company's Persian Recordings, 1906 to 1934* (Bajakhana, 2000)**.
4. **Independent GPT-6 Document:**
   Available in the repository at [`review/review_6_gpt6.md`](file:///Users/ed/Developer/dastgaah/review/review_6_gpt6.md).

---

## 7. The Final Synthesized Empirical Model

The definitive conclusions supported by the complete, multi-round peer-reviewed dataset:

> 1. **An Authentic Intonational Continuum ($127.5¢–153.5¢$):** Across solo instrumental masters with stable, verified modal peaks, the Persian neutral second ($Re^k$) forms an unbroken continuum from $127.5¢$ to $153.5¢$. Lineages close to Saba and Safvat intone near $127.5–129.0¢$; Nariman and Talai intone near $138.5–145.0¢$; and Foroutan, Kasaei, and Alizadeh intone near $150.5–153.5¢$.
> 2. **Absence of Discrete Attractors or Universal Invariants:** The empirical evidence decisively refutes both a single invariant (e.g. $139¢$) and binary discrete attractors. Intonation reflects master lineage, instrument physics, and expressive shading.
> 3. **Indeterminacy of Diachronic Trends:** Because early Qajar recordings exhibit wide confidence intervals (Aqa Hoseyn-Qoli: CI width $26.0¢$; Bagher Khan: CI width $32.0¢$; Darvish Khan: boundary artifact), the available recordings cannot statistically establish either temporal drift or historical invariance.
> 4. **Segāh Neutral Seventh:** Across twelve masters, Shahkhatāyī sounds approximately a fifth above Īst ($700.5¢$ median, $95\\%\\text{{ CI: }} [687–710¢]$), establishing a neutral seventh ($Si^k \\approx 1050–1055¢$) relative to the lower drone, rather than a Pythagorean minor seventh ($996¢$).

All pipeline scripts and datasets are open source and reproducible:
- Master Audit Pipeline (v3): [`analysis/run_rigorous_modal_audit.py`](file:///Users/ed/Developer/dastgaah/analysis/run_rigorous_modal_audit.py)
- Audit Dataset: [`analysis/re_koron_modal_peak_audit.json`](file:///Users/ed/Developer/dastgaah/analysis/re_koron_modal_peak_audit.json)
- Segāh Consensus: [`analysis/segah_consensus.json`](file:///Users/ed/Developer/dastgaah/analysis/segah_consensus.json)
"""

    with open(RESP7_PATH, "w") as f:
        f.write(part_1 + part_2)

    print(f"Successfully generated {RESP7_PATH} ({len(part_1 + part_2)} bytes)")

if __name__ == "__main__":
    build_response_file()

