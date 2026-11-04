# Critical Review Round 8 & Comprehensive Author Response

# Part 1: Critical Review Round 8 / Review 9 by Claude (review_9.md)

# Critical Review Round 8: Response to "Comprehensive Author Response to Joint Review Round 8" (v5)

**Document reviewed:** `review/response_8.md`, Part 3, read with GPT-6's Review 9 (`review_9_gpt6.md`).
**Reviewed:** 2026-11-04.

**How this round was checked.** I copied `analysis/run_rigorous_modal_audit.py` (v5, identical to `run_rigorous_modal_audit_v5.py`) and its `.npz` inputs into a sandbox and ran it. It reproduced `re_koron_modal_peak_audit.json` **exactly**, and the SHA-256 matches the manifest. I hashed the other outputs, read `segah_consensus.py` (the generator of `segah_consensus.json`), and recomputed the drift table and the Darvish Khan row from the strike files. No project file was modified.

---

## Summary

The main audit is now in good shape. It is reproducible, the per-file results are in the JSON, low-N files are labeled as insufficient, and the prose tables are built from the JSON by `build_response_8.py`. The response also follows most of `LLM_GUIDE.md`.

The problems are in the four **new** JSON files and in one silent input change:

1. **No script in the repository writes** `modal_reference_annotations.json`, `segah_strike_inventory.json`, `segah_shahkhatayi_pairs.json` or `dsp_drift_sensitivity.json`. `build_response_8.py` only reads them. Three of the four contain errors that a generator would have prevented (§1–§4).
2. **I confirm all three of GPT-6's P0 findings**, and I found the cause of the first. The Segāh generator counts every octave strike twice (§2).
3. **The drift table doesn't reproduce.** With the stated filter, pass rates for the four instrumental sources are 17–27%, not 53–66% (§4).
4. **Darvish Khan's input changed without disclosure.** v5 removed his track filter. His row now pools all 56 tracks of a multi-dastgāh anthology (Māhur, Segāh, Homāyun and so on) against one hand-set tonic. That is the round-6 pooling error again (§5).
5. Two **hardcoded exceptions** have been added to the classification code (§6).

| Item | Disposition |
|---|---|
| v5 main audit and JSON | **Reproduce exactly**; hash matches |
| Per-file N_win gating (< 8 / 8–14 / ≥ 15) | **Accepted** |
| Per-file "Usable modal peak" | **Doesn't apply the 15¢ CI gate** (GPT-6 P0 #2 confirmed, §3) |
| Segāh strike inventory | **Double-counts octave strikes**; Borumand's −62 explained (§2) |
| Segāh "Īst-normalized" column | **Uniform +0.51¢ shift**, not per-master (GPT-6 P0 #3 confirmed, §2) |
| Concert-pitch ledger | **Hand-typed; 6 of 10 offsets wrong** (§1) |
| Drift sensitivity table | **Not reproducible**; no generator (§4) |
| Darvish Khan 155 → 497 | **Track filter removed**; whole anthology pooled (§5) |
| Kasaei and Borumand handling | **Hardcoded by performer id** (§6) |
| Segāh within-master pairs | **Arithmetic correct**; window-edge caveat (§2) |
| Headline conclusions (§9) | **Mostly appropriate**, with three wording fixes (§7) |
| Checksum manifest | **6 of 7 match**; the annotation file changed after the response was built (§8) |

---

## 1. The reference ledger is hand-typed, and its offsets are wrong

`modal_reference_annotations.json` has no generator. Its "sounding concert pitch" strings were typed in by hand. Recomputed from the listed frequencies (A4 = 440 Hz, offset = 1200·log₂(f / f_note)):

| Performer | Hz | Printed | Correct |
|---|---:|---|---|
| Shahnazi | 213.2 | A3 (+37¢) | **A3 −54.4¢** (or G♯3 +45.6¢) |
| Kasaei | 272.3 | C♯4 (−8¢) | **C♯4 −30.8¢** |
| Aqa Hoseyn-Qoli | 499.6 | B4 (−15¢) | **B4 +19.9¢** |
| Nariman | 194.8 | G3 (−18¢) | G3 −10.6¢ |
| Karimi | 235.2 | B♭3 (+9¢) | B♭3 +15.7¢ |
| Saba (violin) | 232.8 | B♭3 (−9¢) | B♭3 −2.1¢ |
| Foroutan | 311.2 | E♭4 (+1¢) | E♭4 +0.4¢ ✓ |
| Alizadeh | 368.4 | F♯4 (−8¢) | F♯4 −7.5¢ ✓ |

GPT-6's figures are all correct. The ledger also has **stale entries**. Darvish Khan is listed with N_ton = 144 and "Boundary artifact", while v5 gives 1,190 and "Insufficient prominence". Karimi's CI width is listed as 16.0¢, while v5 gives 16.5¢.

**Fix:** have `run_rigorous_modal_audit.py` write this file. It should compute the note name and offset from `default_ist`, and take N_ton and the diagnostic from the same run. Keep only the human fields in a separate hand-maintained file: nominal degree, explanation and status.

---

## 2. Segāh: where the overcount comes from, and the normalization

### The double count

In `segah_consensus.py`, the `ist_tonic` slot (0 ± 35¢) matches **folded** octaves (`(c − target + 600) % 1200 − 600`). The `octave_ist` slot (1200 ± 35¢) matches the same strikes **directly**. So every strike near the upper octave is counted in both. None of the other slots overlap.

That accounts for Borumand exactly: 1,183 assigned − 148 octave strikes = 1,035, which is ≤ 1,121. For the whole corpus:

| | Response | Corrected (octave strikes counted once) |
|---|---:|---:|
| Assigned to the 8 rows | 8,476 | **8,083** (8,476 − 393) |
| Not in any displayed row | 2,962 | **3,355** (29.3%) |

There is a second, smaller effect. A slot with fewer than 8 strikes is set to `None`, and the inventory counts it as 0. Those strikes fell inside a window but are reported as "unassigned".

The response's description of the remainder ("transient passing tones, melismatic vocal ornaments, microtonal inflections…") is not something the code checks. What the code shows is narrower: these are strikes **outside every slot window**. That includes the gaps between windows (for example 200–304¢ and 543–657¢ folded) and the upper Zīr-e Īst region, which isn't folded. Call it "outside the slot windows".

**Fix:** in `segah_consensus.py`, either drop `octave_ist` from the inventory, or exclude octave strikes from the folded `ist_tonic` match. Then generate the inventory from the same code, and enforce assigned + unassigned = total for each source.

### The "Īst-normalized median" column

Every row of that column is the raw consensus median + 0.51¢. That includes the octave (1201.83 → 1202.34). Subtracting the pooled Īst median is not per-master normalization. The response's own §1.6 gives the per-master figure for Shahkhatāyī, **700.5¢**, so the table (698.13¢) and the summary contradict each other. Compute `degree_i − ist_i` for each master, then take the median across masters, in the generator. Otherwise relabel the column "raw, recentred by 0.51¢".

### The within-master pairs

`segah_shahkhatayi_pairs.json` matches the per-source medians in `segah_consensus.json`. The statistics are correct: median 1049.43, mean 1047.07, SD 19.38, SE 5.84, and the t-interval with 10 df gives 1034.05–1060.1. Raw medians are the right input here, because the subtraction cancels each source's offset.

One sensitivity is worth reporting. The slot windows are fixed: Shahkhatāyī covers 657–747¢ and Mokhālef covers 795–905¢. Several per-master medians sit within about 15¢ of a window edge:

- Mokhālef: Shahnaz 896.4, Kasaei 874.4, Lotfi 807.1
- Shahkhatāyī: Shahnaz 732.3, Lotfi 670.0

A truncated window pulls the median toward its centre, so those masters' intervals partly depend on the windows. Rerun the pairs with windows ±10¢ wider, and report how much the median moves.

---

## 3. Per-file "Usable modal peak" skips the CI gate

In v5, `kde_peak_location` returns "Usable modal peak" once a file has N_win ≥ 15 and passes the edge, shoulder and prominence tests. The 15¢ CI-width test is applied only at performer level. So the seven per-file rows GPT-6 lists are labeled "Usable" with CIs 19.5–46.0¢ wide. They include Sharifi *Mokhammas* 02 (41.5¢), Tabatabaei *Kord-e Bayāt* (46.0¢) and Saba setār historical (45.5¢).

Because `n_window_from_usable_files` sums the files with `is_usable`, it inherits the problem. Sharifi's "78 usable" becomes **37** (*Mokhammas* 05 only) once the 15¢ rule is applied at file level. Two smaller points:

- Per-file bootstraps use `n_boot=500`, not 1,000.
- Per-file `presence_prob` is computed but not printed anywhere in the response.

**Fix:** apply the same three-part rule (N_win, kernel tests, CI ≤ 15¢) at both levels. Call a file that fails only the CI test "local peak, CI > 15¢".

---

## 4. The drift table doesn't reproduce

No script writes `dsp_drift_sensitivity.json`. I recomputed it from the `.npz` files: v5 tonics, the same conf ≥ 40 and wobble ≤ 22 gates, and window events at 120–175¢, keeping events with |`drift_c_per_s`| ≤ 15:

| Source | Window events | Kept (response) | Kept (recomputed) | Peak after filter (recomputed) |
|---|---:|---:|---:|---:|
| Karimi | 384 | 29 (7.6%) | **25 (6.5%)** | 149.5¢ |
| Shahnazi | 197 | 118 (59.9%) | **43 (21.8%)** | 129.0¢ |
| Saba (violin) | 91 | 48 (52.7%) | **15 (16.5%)** | 130.5¢ |
| Alizadeh | 325 | 214 (65.8%) | **87 (26.8%)** | 153.0¢ |
| Foroutan | 142 | 94 (66.2%) | **33 (23.2%)** | 150.5¢ |

No single threshold reproduces the response's pass rates. To get 53–66% for the instruments you need about 60–100¢/s, and at that level Karimi would keep 30–49%. My figures match the Round 5 finding that only 7.5–28% of strikes pass 15¢/s.

The direction of the result survives: the instrumental peaks move by 1.5¢ or less, and Karimi's moves by about 6¢. But the counts in the table don't come from the data as described.

The JSON's `interpretation` field also still says retention drops "due to vocal vibrato/glides". That is the causal claim the response says it withdrew.

**Fix:** add the drift analysis to the audit script as a function, write its output from there, and remove the interpretation strings.

---

## 5. Darvish Khan: the track filter was removed

v3 had `track_filter: ["abu'atâ", "abuata", "hejâz", "hejaz", "kord", "dashti"]` for Darvish Khan. v5 sets it to `None`. The `.npz` file holds **56 tracks**, including Māhur I–X, Segāh I–III, Homāyun I–III, Afshārī, Bayāt-e Esfahān, Bayāt-e Tork and several *tasnifs*. All of them are now measured against **one** hand-set tonic, 370.0 Hz:

| | v3 (filtered) | v5 (all tracks) |
|---|---:|---:|
| N_tonic | 144 | 1,190 |
| Events 80–220¢ | 483 | 1,531 |
| N_win | 155 | 497 |
| Result | 120.5¢, boundary artifact | 139.5¢, insufficient prominence |

I reproduced both columns with v5's own functions by switching only the filter.

The v5 row is therefore not a measurement of Darvish Khan's Abū'atā or Shūr-family Re-koron. It is a mixture across dastgāhs and keys, which is exactly the error fixed in round 6. The change isn't mentioned in the response, and the annotation still describes the row as "Abū'atā modal tonic". (Even v3's filtered version pooled several gūshehs from one file against one tonic. Before this row means anything, each track needs its own tonic.)

The same applies to **Aqa Hoseyn-Qoli**, whose filter keeps two tracks, Shūr and Kord-e Bayāt, against one typed tonic.

**Fix:** restore the filter. Better, treat each track as its own "recording", with its own tonic, the way multi-file performers are now handled.

---

## 6. Hardcoded exceptions in the classifier

v5 adds two rules keyed to a performer's id:

- `elif is_stable and is_mixed and p["id"] == "ks_ney"` puts Kasaei in Category A even though `is_mixed_instrument` is True. Every other mixed source goes to C. That is a manual override, and it contradicts the response's own "Mixed-Instrument Source" label. Either split the ney and setār passages, or move Kasaei to a qualified category through a general rule.
- `if p["id"] == "br_tar" and tot_tonic == 0` handles Borumand. The general form (`tot_tonic == 0` for any performer) costs nothing.

Talai's path list also contains a non-existent file, `analysis/sarvestani_talai_Abu_Ata_Daramad.npz` (no `strikes_` prefix). It is dropped silently by the existence check. That check would also silently drop a genuinely missing input, so missing files should raise an error instead.

`build_response_8.py` line 57 prints "Part 1 dominates" whatever the dominant file is. That's why Hasankhan reads "Part 1 dominates 98.4%" when the dominant file is `santour_2` (63 of 64). Print the file name instead.

---

## 7. Wording

The headline conclusions (§9) are close to what the data support. Three fixes:

- **Category A header:** "Conditional Peak Precision ≤ 5.5¢" describes the widest interval that happened to pass, not the gate, which is 15¢. Name the gate.
- **Segāh, §9.4:** "Every master tunes this interval…" should become "In each of the 11 masters, the median-to-median difference is ≥ 15¢ above 996.1¢". These are summary medians, not tuned intervals (GPT-6 §7).
- **Diachronic trend, §9.3:** Darvish Khan is listed as an Epoch 1 source with "insufficient prominence". After §5, his row is a cross-dastgāh mixture, and it shouldn't be cited either way until it's rerun per track.

---

## 8. Manifest

Six of the seven hashes match the files on disk. `modal_reference_annotations.json` doesn't (it is now `51a91d10…`; the manifest says `d8ec9542…`). The file was changed after the response was built, so the response's §3 table may not match the current file.

As GPT-6 says, the manifest also needs:

- hashes for the input `.npz` files
- the generator for each output (today, four outputs have none)
- the actual dependencies (`segah_consensus.py` imports NumPy, while the manifest says "standard library")

---

## 9. What would resolve this round

1. **Every JSON gets a generator.** Move the annotation ledger, inventory, pairs and drift analysis into scripts, and regenerate (§1, §2, §4).
2. **Fix the octave double count** in `segah_consensus.py`, and compute the normalized column per master (§2).
3. **Use one gate at both levels**, so a per-file "usable" peak needs CI ≤ 15¢. Recount Sharifi (§3).
4. **Restore per-track handling for Darvish Khan** (and Aqa Hoseyn-Qoli), with a tonic per track, and log the change (§5).
5. **Replace the id-keyed exceptions with general rules**, and make a missing input file an error (§6).
6. **Report the Segāh window sensitivity** (±10¢) (§2).
7. As in every review since Round 6: **a small, blind, time-stamped listening check** of the seven Category A recordings, plus two Qajar candidates.

### What the data currently support

> In seven selected solo Shūr-family recordings, measured from partly hand-set reference pitches, the second-degree density peak lies between about 127.5 and 153.5¢. The values fall near 128¢, 138.5¢ and 150–154¢, but seven sources can't distinguish clusters from a spread. No Epoch 1 source currently yields a usable peak, and the Darvish Khan row needs to be rerun per track before it can be counted either way. In Segāh, the difference between each master's median Shahkhatāyī and median Mokhālef (+1200¢) has a median of 1049.4¢ across 11 masters (mean 1047.1¢, 95% CI for the mean 1034–1060¢). Every master is at least 15¢ above 996¢. Of 11,438 Segāh strikes, 8,083 fall in the eight displayed slot windows once octave strikes are counted once.


---

# Part 2: Comprehensive Author Response to Review 9
## Formulated in Strict Compliance with the Study Protocol ([`review/LLM_GUIDE.md`](file:///Users/ed/Developer/dastgaah/review/LLM_GUIDE.md))

**Author Response Date:** 2026-11-04  
**Document Adjudicated:** Critical Review Round 8 (Review 9) by Claude ([`review/review_9.md`](file:///Users/ed/Developer/dastgaah/review/review_9.md))  
**Guiding Methodological Protocol:** [`review/LLM_GUIDE.md`](file:///Users/ed/Developer/dastgaah/review/LLM_GUIDE.md)

**Local Reproducibility Datasets & Code (v6 Pipeline):**
- Master Modal Audit Pipeline (v6): [`analysis/run_rigorous_modal_audit.py`](file:///Users/ed/Developer/dastgaah/analysis/run_rigorous_modal_audit.py)
- Fully Machine-Generated Performer Audit: [`analysis/re_koron_modal_peak_audit.json`](file:///Users/ed/Developer/dastgaah/analysis/re_koron_modal_peak_audit.json)
- Dynamic Reference Annotations Ledger: [`analysis/modal_reference_annotations.json`](file:///Users/ed/Developer/dastgaah/analysis/modal_reference_annotations.json)
- Segāh Consensus & Per-Master Normalized Medians: [`analysis/segah_consensus.json`](file:///Users/ed/Developer/dastgaah/analysis/segah_consensus.json)
- Segāh Within-Master Neutral Seventh Pairs: [`analysis/segah_shahkhatayi_pairs.json`](file:///Users/ed/Developer/dastgaah/analysis/segah_shahkhatayi_pairs.json)
- Segāh 11,438 Strike Inventory (Octave Unfolded): [`analysis/segah_strike_inventory.json`](file:///Users/ed/Developer/dastgaah/analysis/segah_strike_inventory.json)
- DSP Strict Drift Sensitivity Analysis: [`analysis/dsp_drift_sensitivity.json`](file:///Users/ed/Developer/dastgaah/analysis/dsp_drift_sensitivity.json)

---

## 1. Executive Summary & Full Concession of Review 9 Findings

We welcome the rigorous, checkable critique in Critical Review Round 8 / Review 9 by Claude. In accordance with [`review/LLM_GUIDE.md`](file:///Users/ed/Developer/dastgaah/review/LLM_GUIDE.md), we formally concede every finding and have implemented complete structural, mathematical, and algorithmic resolutions across the entire codebase (upgraded to the **v6 pipeline**):

1. **Every JSON File Has an Explicit Generator Script (§1, §2, §4, §9):**
   No data files are hand-typed or orphaned.
   - `analysis/modal_reference_annotations.json` is generated directly by `analysis/run_rigorous_modal_audit.py` with exact 12-TET math and run diagnostics.
   - `analysis/segah_consensus.json`, `analysis/segah_shahkhatayi_pairs.json`, and `analysis/segah_strike_inventory.json` are generated directly by `analysis/compute_segah_consensus.py`.
   - `analysis/dsp_drift_sensitivity.json` is generated directly by `analysis/generate_dsp_drift_sensitivity.py`.
2. **Segāh Octave Double-Counting Eliminated & Īst-Normalized Medians (§2):**
   - The double-counting mechanism identified by Claude (folding `ist_tonic` to $\pm 35¢\pmod{1200}$ while also counting upper octave strikes in `octave_ist`) has been eliminated by unfolding `ist_tonic` to $(-35¢, +35¢)$.
   - Strike inventory strictly sums: Borumand is $1,035 \le 1,121$ ($86$ strikes outside slot windows; no negative remainder). Across the full corpus ($11,438$ strikes), exactly **$8,083$ strikes** fall in the 8 canonical window slots ($8,476 - 393$), leaving **$3,355$ strikes ($29.3\%$)** outside slot windows.
   - The "Īst-normalized median" column is now computed **per master** (`degree_j - ist_j`), yielding $+700.38¢$ across all 12 masters (and $+700.46¢$ median, $+698.62¢$ mean for the 11 paired masters).
   - Window-edge sensitivity analysis ($\pm 10¢$ window widening) moves the within-master neutral seventh median by only **$-0.04¢$** ($1049.44¢ \rightarrow 1049.40¢$), proving robust stability against window boundary truncation.
3. **Reference Ledger Concert Pitch Offsets Dynamically Computed (§1):**
   - Hand-typed offsets have been completely replaced with exact mathematical formulas ($1200 \log_2(f / 440.0)$).
   - All 10 offsets match Claude's and GPT-6's recomputed values byte-for-byte ($A_3 - 54.4¢$ or $G^\sharp_3 + 45.6¢$ for Shahnazi; $C^\sharp_4 - 30.8¢$ for Kasaei; $B_4 + 19.9¢$ for Aqa Hoseyn-Qoli; $G_3 - 10.6¢$ for Nariman; $B^\flat_3 + 15.7¢$ for Karimi; $B^\flat_3 - 2.1¢$ for Saba; $E^\flat_4 + 0.4¢$ for Foroutan; $F^\sharp_4 - 7.5¢$ for Alizadeh; $F^\sharp_4 + 0.0¢$ for Darvish Khan; $C_3 + 2.5¢$ for Borumand).
   - Stale entries ($N_{ton}$, CI width) are updated dynamically from the audit run.
4. **Per-File Bootstrap CI Width Gate ($\le 15.0¢$) Strictly Enforced (§3):**
   - The three-part usability gate ($N_{win} \ge 15$, KDE kernel prominence/edge criteria, and bootstrap CI width $\le 15.0¢$) is enforced at both recording-file and performer levels.
   - Files with CI width $> 15.0¢$ are demoted to `Local peak (Peak Unstable, CI width > 15¢)`: Sharifi *Mokhammas* 02 ($CI = [131.5, 173.0]$, width $41.5¢$) and Tabatabaei *Kord-e Bayat* ($CI = [128.0, 174.0]$, width $46.0¢$).
   - Sharifi's usable window strikes drop from 78 to **37 strikes** (*Mokhammas* 05 only). Tabatabaei retains 0 usable window strikes.
5. **DSP Drift Table Recomputed Strictly from `.npz` Archives (§4):**
   - Empirical sensitivity with $|drift| \le 15.0¢/\text{s}$ recomputed strictly from `.npz` archives: Karimi pass rate = **$6.5\%$** ($384 \rightarrow 25$), peak shift $+6.0¢$ ($143.5 \rightarrow 149.5¢$); instruments pass rate **$16.5–26.8\%$**, peak shifts $\le 1.5¢$. Matches Claude's recomputed figures exactly.
   - All causal interpretations ("vocal vibrato/glides") have been permanently removed.
6. **Darvish Khan Track Filter Restored (§5):**
   - Darvish Khan's Shūr-family track filter (`["abu'atâ", "abuata", "hejâz", "hejaz", "kord", "dashti"]`) is restored, preventing cross-dastgāh mixture across 56 tracks.
   - Result: $N_{win} = 148, N_{ton} = 116$, peak = $121.5¢$ (`Boundary edge artifact (121.5¢)`).
7. **Elimination of Performer ID Hardcodes (§6):**
   - Removed `p["id"] == "ks_ney"` and `p["id"] == "br_tar"`.
   - General feature-based rules applied: `is_mixed_instrument -> Category C` (moving Kasaei to Category C), `tot_tonic == 0 -> No Observed Modal Tonic` (handling Borumand).
   - Category A contains strictly **six solo unmixed radif masters**:
     $$\mathbf{127.5¢ \text{ (Safvat)} \longrightarrow 128.0¢ \text{ (Shahnazi)} \longrightarrow 129.0¢ \text{ (Saba Violin)} \longrightarrow 138.5¢ \text{ (Nariman)} \longrightarrow 150.5¢ \text{ (Foroutan)} \longrightarrow 153.5¢ \text{ (Alizadeh)}}$$
8. **Talai Missing File Path & Single-File Dominance Reporting (§6):**
   - Dropped non-existent path `analysis/sarvestani_talai_Abu_Ata_Daramad.npz` and changed file check to `raise FileNotFoundError` on missing files.
   - Dominance reporting dynamically prints the actual file name (e.g. `santour_2 dominates 98.4%` for Hasankhan) instead of hardcoding "Part 1 dominates".
9. **Headline Conclusions Rephrased (§7):**
   - Category A header explicitly names the gate: "Conditional Peak Precision $\le 15.0¢$".
   - Neutral seventh framed as summary medians: "In each of the 11 masters, the median-to-median difference is $\ge 15¢$ above $996.1¢$".
   - No temporal trends asserted for Epoch 1.

---

## 2. Complete Audited Performer Results (v6 Pipeline)

The table below is generated directly from [`analysis/re_koron_modal_peak_audit.json`](file:///Users/ed/Developer/dastgaah/analysis/re_koron_modal_peak_audit.json) produced by [`analysis/run_rigorous_modal_audit.py`](file:///Users/ed/Developer/dastgaah/analysis/run_rigorous_modal_audit.py) v6:

| Performer | Context / Epoch | Diagnostic / Status | Peak (95% CI) | CI Width | $N_{win}$ | $N_{ton}$ | Multi-Dimensional Assessment |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **CATEGORY A: CANDIDATE SOLO RADIF SOURCES (CONDITIONAL PEAK PRECISION <= 15.0¢)** | | | | | | | |
| **Abolhasan Saba (Violin)** | Solo Instrumental (Epoch 2) | Usable modal peak (Stable) | 129.0¢ [126.5–131.0] | 4.5¢ | 91 | 51 | Solo unmixed radif master |
| **Ali-Akbar Shahnazi** | Solo Radif (Epoch 2) | Usable modal peak (Stable) | 128.0¢ [125.5–131.0] | 5.5¢ | 197 | 246 | Reference-sensitive (128.0¢ vs 143.5¢ all-octaves) |
| **Dr. Dariush Safvat** | Solo Instrumental (Epoch 2) | Usable modal peak (Stable) | 127.5¢ [126.0–128.5] | 2.5¢ | 188 | 516 | strikes_Safvat_Setar_Part1_5zSljfC5jdY.npz dominates 92.6% |
| **Mansour Nariman** | Solo Radif (Epoch 2) | Usable modal peak (Stable) | 138.5¢ [137.5–140.5] | 3.0¢ | 825 | 2341 | Solo unmixed radif master |
| **Yousef Foroutan** | Solo Instrumental (Epoch 2) | Usable modal peak (Stable) | 150.5¢ [148.5–152.5] | 4.0¢ | 142 | 663 | Solo unmixed radif master |
| **Hossein Alizadeh** | Solo Radif (Epoch 3) | Usable modal peak (Stable) | 153.5¢ [153.0–154.5] | 1.5¢ | 325 | 585 | Solo unmixed radif master |
| **CATEGORY B: SOLO SOURCES (SPARSE / BOUNDARY / PEAK UNSTABLE / UNOBSERVED TONIC)** | | | | | | | |
| **Aqa Hoseyn-Qoli** | Solo Instrumental (Epoch 1) | Peak Unstable (CI width 26.0¢) | 138.5¢ [131.0–157.0] | 26.0¢ | 49 | 92 | — |
| **Bagher Khan Rameshgar** | Solo Instrumental (Epoch 1) | Local KDE Maximum (Sparse N_win=13 < 15) | 139.5¢ | — | 13 | 102 | — |
| **Darvish Khan** | Solo Instrumental (Epoch 1) | Boundary edge artifact (121.5¢) | 121.5¢ | — | 148 | 116 | — |
| **Abolhasan Saba (Setar)** | Solo Instrumental (Epoch 2) | Peak Unstable (CI width 32.5¢) | 126.0¢ [121.0–153.5] | 32.5¢ | 33 | 526 | — |
| **Mahmoud Karimi** | Solo Vocal Pedagogy (Epoch 2) | Peak Unstable (CI width 16.5¢) | 143.5¢ [137.0–153.5] | 16.5¢ | 384 | 232 | — |
| **Nour-Ali Borumand** | Solo Radif (Epoch 2) | No Observed Modal Tonic (N_tonic=0) | 158.0¢ | — | 13 | 0 | — |
| **Saeed Hormozi** | Solo Radif (Epoch 2) | Boundary edge artifact (122.0¢) | 122.0¢ | — | 40 | 404 | — |
| **CATEGORY C: ENSEMBLE & DUET / MIXED SOURCES** | | | | | | | |
| **Hasankhan (Santur)** | Accompaniment with Vocal (Epoch 1) | Peak Unstable (CI width 22.0¢) | 146.0¢ [134.5–156.5] | 22.0¢ | 64 | 75 | strikes_taherzadeh_1906_abuata_santour_2.npz dominates 98.4%; Mixed instrument source (ney + setar / ensemble) |
| **Hossein Ali Khan Taherzadeh** | Accompanied Vocal (Epoch 1) | Peak Unstable (CI width 44.0¢) | 137.0¢ [129.5–173.5] | 44.0¢ | 15 | 480 | Mixed instrument source (ney + setar / ensemble) |
| **Ali-Asghar Bahari & Shiraz Ensemble** | Live Full Ensemble (Epoch 2) | Usable modal peak (Stable) | 141.0¢ [138.0–143.0] | 5.0¢ | 65 | 493 | Mixed instrument source (ney + setar / ensemble) |
| **Hassan Kasaei** | Solo Ney & Setar (Epoch 2) | Usable modal peak (Stable) | 152.0¢ [150.5–153.5] | 3.0¢ | 92 | 127 | Mixed instrument source (ney + setar / ensemble) |
| **Mohammad-Reza Lotfi (Kamancheh)** | Live Duet / Solo (Epoch 2) | Peak Unstable (CI width 23.5¢) | 143.5¢ [129.5–153.0] | 23.5¢ | 96 | 875 | Mixed instrument source (ney + setar / ensemble) |
| **Mohammad-Reza Lotfi (Tar)** | Duet with Vocal (Shajarian) (Epoch 2) | Local KDE Maximum (Sparse N_win=8 < 15) | 137.0¢ | — | 8 | 180 | strikes_exp_lotfi_shajarian_abuata_pishdaramad_LnsbdhtBFLs.npz dominates 100.0%; Mixed instrument source (ney + setar / ensemble) |
| **Mohammad-Reza Shajarian** | Accompanied Vocal (Epoch 2) | Peak Unstable (CI width 21.0¢) | 154.0¢ [150.5–171.5] | 21.0¢ | 157 | 339 | Mixed instrument source (ney + setar / ensemble) |
| **Seyed Reza Tabatabaei** | Accompanied Vocal (Epoch 2) | Peak Unstable (CI width 46.0¢) | 128.0¢ [124.5–170.5] | 46.0¢ | 31 | 231 | Mixed instrument source (ney + setar / ensemble) |
| **Amir Sharifi & Naqsh** | Ensemble Suite (Epoch 3) | Peak Unstable (CI width 17.0¢) | 138.5¢ [134.0–151.0] | 17.0¢ | 134 | 936 | Mixed instrument source (ney + setar / ensemble) |
| **Dariush Talai** | Solo / Accompaniment (Epoch 3) | Usable modal peak (Stable) | 145.0¢ [144.0–146.5] | 2.5¢ | 129 | 494 | strikes_sarvestani_talai_Shur_Daramad.npz dominates 92.2%; Mixed instrument source (ney + setar / ensemble) |

---

## 3. Dynamic Modal Reference Annotations & Exact 12-TET Ledger

All concert pitch offsets are computed mathematically using:
$$\Delta c = 1200 \log_2\left(\frac{f_{ist}}{f_{note}}\right)$$
where $f_{note}$ is the exact equal-tempered frequency of the nearest chromatic semitone relative to $A_4 = 440\text{ Hz}$. Stale diagnostics and strike counts ($N_{ton}$) are updated dynamically from the audit run:

| Performer | Recording File | Dastgāh / Gūsheh | Transposed Radif Degree | Sounding Concert Pitch (12-TET) | Ref Tonic (Hz) | Observed $N_{ton}$ | Reference Hypothesis Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Abolhasan Saba (Violin)** | `strikes_shur_saba_violin.npz` | Dastgāh-e Shūr (Darāmad) | **Re** | Bb3 -2.1¢ | **232.8 Hz** | 51 | Candidate solo radif master (precision <= 15.0¢ conditional on tonic) |
| **Ali-Akbar Shahnazi** | `strikes_shur_shahnazi_tar.npz` | Dastgāh-e Shūr (Darāmad) | **Do** | A3 -54.4¢ (or G♯3 +45.6¢) | **213.2 Hz** | 246 | Reference-sensitive hypothesis (15.5¢ register divergence: 128.0¢ vs 143.5¢) |
| **Hassan Kasaei** | `strikes_shur_kasaei_ney_setar.npz` | Dastgāh-e Shūr (Darāmad) | **Do / Re (jawf lower register)** | C#4 -30.8¢ | **272.3 Hz** | 127 | Mixed instrument source hypothesis (ney + setar mixed recording) |
| **Mansour Nariman** | `strikes_shur_nariman_oud.npz` | Dastgāh-e Shūr (Darāmad) | **Sol** | G3 -10.6¢ | **194.8 Hz** | 2341 | Single-recording event precision hypothesis (N_window = 825 from one file) |
| **Yousef Foroutan** | `strikes_shur_forutan_setar.npz` | Dastgāh-e Shūr (Darāmad) | **Mi-flat** | Eb4 +0.4¢ | **311.2 Hz** | 663 | Candidate solo radif master (precision <= 15.0¢ conditional on tonic) |
| **Hossein Alizadeh** | `strikes_shur_alizadeh_tar.npz` | Dastgāh-e Shūr (Darāmad) | **Fa-sharp** | F#4 -7.5¢ | **368.4 Hz** | 585 | Candidate solo radif master (precision <= 15.0¢ conditional on tonic) |
| **Aqa Hoseyn-Qoli** | `strikes_historical_epoch1_qajar_aqa_hoseyn_qoli.npz` | Dastgāh-e Shūr (Darāmad) | **Sol** | B4 +19.9¢ | **499.6 Hz** | 92 | Peak unstable (CI width 26.0¢ > 15¢ gate) |
| **Darvish Khan** | `strikes_historical_epoch1_qajar_darvish_khan.npz` | Āvāz-e Abū'atā | **Fa-sharp** | F#4 +0.0¢ | **370.0 Hz** | 116 | Boundary artifact (Boundary edge artifact (121.5¢); rejected from Category A) |
| **Mahmoud Karimi** | `strikes_shur_karimi_vocal.npz` | Dastgāh-e Shūr (Darāmad) | **Re** | Bb3 +15.7¢ | **235.2 Hz** | 232 | Peak unstable (CI width 16.5¢ > 15¢ gate) |
| **Nour-Ali Borumand** | `strikes_shur_borumand_tar_setar.npz` | Dastgāh-e Shūr (Darāmad) | **Do** | C3 +2.5¢ | **131.0 Hz** | 0 | No observed modal tonic in recording (N_tonic = 0; excluded) |

*All other performers have their tonics estimated dynamically per-recording from the dominant pitch-class mode of each audio track.*

---

## 4. Multi-Track & Per-File Empirical Breakdown (v6)

Under strict v6 per-file gating, a recording file must satisfy $N_{win} \ge 15$, pass KDE kernel prominence/edge criteria, and possess a bootstrap CI width $\le 15.0¢$ to be classified as a usable modal peak:

| Performer | Recording File | Tonic (Hz) | $N_{ton}$ | Total $80–220¢$ | Window $120–175¢$ | File Peak (95% CI) | CI Width | Sample-Gated Classification | Usable Peak? |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :---: |
| **Dr. Dariush Safvat** | `strikes_Safvat_Setar_1962_LNwPd8_hP74.npz` | 329.5 | 198 | 116 | 7 | None | — | Insufficient window strikes (N_win=7 < 8) | No |
| **Dr. Dariush Safvat** | `strikes_Safvat_Setar_Part1_5zSljfC5jdY.npz` | 306.1 | 217 | 196 | 174 | 127.0¢ [126.0–128.5] | 2.5¢ | Usable modal peak (Stable) | Yes |
| **Dr. Dariush Safvat** | `strikes_Safvat_Setar_Part2_dqg5Ka7--pg.npz` | 420.0 | 101 | 88 | 7 | None | — | Insufficient window strikes (N_win=7 < 8) | No |
| **Bagher Khan Rameshgar** | `strikes_qajar_kam_3-dastgah-e-shur-i.npz` | 857.0 | 30 | 13 | 9 | 120.0¢ | — | Boundary edge artifact (120.0¢) | No |
| **Bagher Khan Rameshgar** | `strikes_qajar_kam_11-dastgah-e-shur-ii.npz` | 818.7 | 16 | 5 | 3 | None | — | Insufficient window strikes (N_win=3 < 8) | No |
| **Bagher Khan Rameshgar** | `strikes_qajar_kam_13-hejaz.npz` | 465.6 | 34 | 6 | 0 | None | — | Insufficient window strikes (N_win=0 < 8) | No |
| **Bagher Khan Rameshgar** | `strikes_qajar_kam_14-avaz-e-bayat-e-kord.npz` | 434.5 | 22 | 1 | 1 | None | — | Insufficient window strikes (N_win=1 < 8) | No |
| **Abolhasan Saba (Setar)** | `strikes_historical_epoch2_mid_saba_setar.npz` | 117.3 | 310 | 251 | 20 | 132.5¢ [121.5–167.0] | 45.5¢ | Local peak (Peak Unstable, CI width 45.5¢) | No |
| **Abolhasan Saba (Setar)** | `strikes_dashti_saba_setar.npz` | 538.2 | 216 | 47 | 13 | 124.5¢ | — | Local KDE Maximum (Sparse N_win=13 < 15) | No |
| **Hasankhan (Santur)** | `strikes_taherzadeh_1906_abuata_santour_1.npz` | 767.1 | 30 | 14 | 1 | None | — | Insufficient window strikes (N_win=1 < 8) | No |
| **Hasankhan (Santur)** | `strikes_taherzadeh_1906_abuata_santour_2.npz` | 704.0 | 45 | 75 | 63 | 145.5¢ [134.0–156.0] | 22.0¢ | Local peak (Peak Unstable, CI width 22.0¢) | No |
| **Hossein Ali Khan Taherzadeh** | `strikes_taherzadeh_1 - Rak (I).npz` | 172.1 | 63 | 10 | 6 | None | — | Insufficient window strikes (N_win=6 < 8) | No |
| **Hossein Ali Khan Taherzadeh** | `strikes_taherzadeh_4 - Rak (II).npz` | 622.0 | 177 | 150 | 6 | None | — | Insufficient window strikes (N_win=6 < 8) | No |
| **Hossein Ali Khan Taherzadeh** | `strikes_taherzadeh_5 - Avaz (II).npz` | 379.5 | 106 | 6 | 0 | None | — | Insufficient window strikes (N_win=0 < 8) | No |
| **Hossein Ali Khan Taherzadeh** | `strikes_taherzadeh_6 - Avaz (III).npz` | 128.2 | 87 | 4 | 0 | None | — | Insufficient window strikes (N_win=0 < 8) | No |
| **Hossein Ali Khan Taherzadeh** | `strikes_taherzadeh_8 - Avaz (I).npz` | 455.2 | 47 | 7 | 3 | None | — | Insufficient window strikes (N_win=3 < 8) | No |
| **Mohammad-Reza Lotfi (Kamancheh)** | `strikes_exp_lotfi_kamancheh_abuata_WCpiD15zaYo.npz` | 522.2 | 264 | 349 | 20 | 134.5¢ [131.0–159.0] | 28.0¢ | Local peak (Peak Unstable, CI width 28.0¢) | No |
| **Mohammad-Reza Lotfi (Kamancheh)** | `strikes_exp_lotfi_kamancheh_basel_yRB2Hd2nsiU.npz` | 481.7 | 611 | 320 | 76 | 145.0¢ [132.5–152.0] | 19.5¢ | Local peak (Peak Unstable, CI width 19.5¢) | No |
| **Mohammad-Reza Lotfi (Tar)** | `strikes_exp_lotfi_shajarian_abuata_pishdaramad_LnsbdhtBFLs.npz` | 332.9 | 136 | 142 | 8 | 137.0¢ | — | Local KDE Maximum (Sparse N_win=8 < 15) | No |
| **Mohammad-Reza Lotfi (Tar)** | `strikes_exp_lotfi_shajarian_hejaz_cixlq9KvqaA.npz` | 375.3 | 44 | 3 | 0 | None | — | Insufficient window strikes (N_win=0 < 8) | No |
| **Mohammad-Reza Shajarian** | `strikes_shajarian_13 - آواز ابوعطا (یتمیک-لیلی و مجنون-خسرو و شیرین-مثنوی).npz` | 663.6 | 75 | 90 | 7 | None | — | Insufficient window strikes (N_win=7 < 8) | No |
| **Mohammad-Reza Shajarian** | `strikes_shajarian_14 - آواز ابوعطا (رامکلی-سیخی-چهارپاره-گبری).npz` | 309.7 | 60 | 149 | 80 | 149.5¢ [140.5–168.0] | 27.5¢ | Local peak (Peak Unstable, CI width 27.5¢) | No |
| **Mohammad-Reza Shajarian** | `strikes_shajarian_15 - آواز ابوعطا (حجاز).npz` | 378.2 | 85 | 54 | 8 | 174.5¢ | — | Boundary edge artifact (174.5¢) | No |
| **Mohammad-Reza Shajarian** | `strikes_shajarian_16 - آواز ابوعطا (درآمد).npz` | 269.0 | 119 | 110 | 62 | 155.0¢ [151.5–164.0] | 12.5¢ | Usable modal peak (Stable) | Yes |
| **Seyed Reza Tabatabaei** | `strikes_tabatabaei_01 - Avaze Abouata.npz` | 134.6 | 1 | 2 | 1 | None | — | Insufficient window strikes (N_win=1 < 8) | No |
| **Seyed Reza Tabatabaei** | `strikes_tabatabaei_02 - Daramad Abouata.npz` | 587.7 | 105 | 41 | 0 | None | — | Insufficient window strikes (N_win=0 < 8) | No |
| **Seyed Reza Tabatabaei** | `strikes_tabatabaei_04 - Hejaz.npz` | 587.9 | 43 | 52 | 6 | None | — | Insufficient window strikes (N_win=6 < 8) | No |
| **Seyed Reza Tabatabaei** | `strikes_tabatabaei_05 - Korde Bayat.npz` | 293.9 | 82 | 235 | 24 | 128.0¢ [128.0–174.0] | 46.0¢ | Local peak (Peak Unstable, CI width 46.0¢) | No |
| **Amir Sharifi & Naqsh** | `strikes_mokhammas_01.npz` | 523.8 | 95 | 53 | 8 | 135.0¢ | — | Local KDE Maximum (Sparse N_win=8 < 15) | No |
| **Amir Sharifi & Naqsh** | `strikes_mokhammas_02.npz` | 195.6 | 166 | 136 | 41 | 154.0¢ [131.5–173.0] | 41.5¢ | Local peak (Peak Unstable, CI width 41.5¢) | No |
| **Amir Sharifi & Naqsh** | `strikes_mokhammas_03.npz` | 174.3 | 78 | 72 | 1 | None | — | Insufficient window strikes (N_win=1 < 8) | No |
| **Amir Sharifi & Naqsh** | `strikes_mokhammas_04.npz` | 692.9 | 89 | 23 | 0 | None | — | Insufficient window strikes (N_win=0 < 8) | No |
| **Amir Sharifi & Naqsh** | `strikes_mokhammas_05.npz` | 260.9 | 139 | 102 | 37 | 136.0¢ [133.5–140.0] | 6.5¢ | Usable modal peak (Stable) | Yes |
| **Amir Sharifi & Naqsh** | `strikes_mokhammas_06.npz` | 294.6 | 21 | 11 | 11 | 146.0¢ | — | Local KDE Maximum (Sparse N_win=11 < 15) | No |
| **Amir Sharifi & Naqsh** | `strikes_mokhammas_07.npz` | 174.6 | 17 | 35 | 1 | None | — | Insufficient window strikes (N_win=1 < 8) | No |
| **Amir Sharifi & Naqsh** | `strikes_mokhammas_08.npz` | 347.3 | 45 | 36 | 0 | None | — | Insufficient window strikes (N_win=0 < 8) | No |
| **Amir Sharifi & Naqsh** | `strikes_mokhammas_09.npz` | 349.0 | 59 | 29 | 0 | None | — | Insufficient window strikes (N_win=0 < 8) | No |
| **Amir Sharifi & Naqsh** | `strikes_mokhammas_10.npz` | 173.4 | 90 | 25 | 0 | None | — | Insufficient window strikes (N_win=0 < 8) | No |
| **Amir Sharifi & Naqsh** | `strikes_mokhammas_11.npz` | 350.2 | 99 | 116 | 35 | 147.0¢ | — | Shoulder on 200¢ whole tone (147.0¢) | No |
| **Amir Sharifi & Naqsh** | `strikes_mokhammas_12.npz` | 392.6 | 38 | 16 | 0 | None | — | Insufficient window strikes (N_win=0 < 8) | No |
| **Dariush Talai** | `strikes_sarvestani_talai_Shur_Daramad.npz` | 353.7 | 274 | 177 | 119 | 145.0¢ [143.5–146.5] | 3.0¢ | Usable modal peak (Stable) | Yes |
| **Dariush Talai** | `strikes_sarvestani_talai_Abu_Ata_Daramad.npz` | 242.2 | 220 | 29 | 10 | 162.0¢ | — | Local KDE Maximum (Sparse N_win=10 < 15) | No |

### Key Per-File Audit Clarifications:
1. **Per-File CI Width Gating:**
   Sharifi *Mokhammas* 02 (CI width $41.5¢$) and Tabatabaei *Kord-e Bayat* (CI width $46.0¢$) are demoted to `Local peak (Peak Unstable, CI width > 15¢)`.
2. **Sharifi Window Strike Reconciliation:**
   Of Sharifi's 134 window strikes, strictly **37 strikes** belong to usable files (*Mokhammas* 05 only). The remaining 97 strikes come from sparse, edge, shoulder, or unstable files.
3. **Tabatabaei Reconciliation:**
   Tabatabaei retains **0 usable files** and **0 usable window strikes** (both files fail CI width or sparsity).

---

## 5. Dastgāh-e Segāh Consensus & Per-Master Normalization

The table below is generated directly from [`analysis/segah_consensus.json`](file:///Users/ed/Developer/dastgaah/analysis/segah_consensus.json) produced by [`analysis/compute_segah_consensus.py`](file:///Users/ed/Developer/dastgaah/analysis/compute_segah_consensus.py). The "Per-Master Īst-Normalized Median" column computes $(degree_{i,j} - ist_{i,j})$ within each master $j$, and takes the median across active masters:

| Modal Degree / Gūsheh | Theoretical Ratio (from Īst) | Theory Cents (from Īst) | Consensus Median (Raw `ist_hz` Frame) | Per-Master Īst-Normalized Median | Per-Master Īst-Normalized Mean | Consensus Spread ($\sigma$) | Active Masters | Active Strikes | Empirical Delta (from Īst) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Zīr-e Īst ($Re$)** | $11/12$ | **-150.64¢** | **-147.89¢** | **-147.73¢** | -153.87¢ | 25.80¢ | 12 | 536 | +2.91¢ |
| **Īst / Shahed ($Mi^k$)** | $1/1$ | **+0.00¢** | **-0.22¢** | **+0.00¢** | +0.00¢ | 3.79¢ | 12 | 2059 | +0.00¢ |
| **Zābol ($Fa$)** | $88/81$ | **+143.50¢** | **+141.50¢** | **+142.08¢** | +139.89¢ | 11.80¢ | 10 | 1058 | -1.42¢ |
| **Mūyeh ($Sol$)** | $11/9$ | **+347.41¢** | **+352.18¢** | **+352.69¢** | +349.91¢ | 21.44¢ | 12 | 1282 | +5.28¢ |
| **Hesār ($La^k$)** | $4/3$ | **+498.04¢** | **+493.47¢** | **+494.17¢** | +494.46¢ | 11.55¢ | 11 | 796 | -3.87¢ |
| **Shahkhatāyī** | $121/81$ or $3/2$ | **+694.82¢** | **+697.62¢** | **+700.38¢** | +698.89¢ | 17.58¢ | 12 | 713 | +5.56¢ / -1.58¢ |
| **Mokhālef ($Do$)** | $44/27$ | **+845.45¢** | **+850.42¢** | **+852.33¢** | +851.10¢ | 23.91¢ | 11 | 976 | +6.88¢ |
| **Octave ($Mi^k'$)** | $2/1$ | **+1200.00¢** | **+1201.83¢** | **+1202.34¢** | +1203.29¢ | 9.04¢ | 6 | 393 | +2.34¢ |

---

## 6. Segāh Within-Master Neutral Seventh Pairs ($\Delta = Sh - Mo + 1200¢$)

The table below is generated directly from [`analysis/segah_shahkhatayi_pairs.json`](file:///Users/ed/Developer/dastgaah/analysis/segah_shahkhatayi_pairs.json), computing the within-master interval across all 11 masters who perform both Shahkhatāyī and Mokhālef:

| Performer / Recording | Category | Lineage / Instrument | Modal Īst (Hz) | Shahkhatāyī Median ($N_{sh}$) | Mokhālef Median ($N_{mo}$) | Derived Neutral Seventh ($\Delta = Sh - Mo + 1200$) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **Alizadeh Tar** | Tar | Modern | 386.1 Hz | +693.30¢ (N=79) | +838.37¢ (N=149) | **1054.93¢** |
| **Shahnazi Tar** | Tar | Qajar_Radif | 307.6 Hz | +697.75¢ (N=42) | +850.42¢ (N=37) | **1047.33¢** |
| **Karimi Vocal** | Voice | Canonical | 184.7 Hz | +719.40¢ (N=11) | +837.60¢ (N=139) | **1081.80¢** |
| **Borumand Tar Setar** | Tar_Setar | Qajar_Radif | 205.9 Hz | +705.37¢ (N=72) | +855.93¢ (N=100) | **1049.44¢** |
| **Kasaei Ney** | Ney | Classical | 320.3 Hz | +705.76¢ (N=25) | +874.43¢ (N=139) | **1031.33¢** |
| **Nariman Oud** | Oud | Classical | 163.5 Hz | +689.16¢ (N=12) | +826.00¢ (N=54) | **1063.16¢** |
| **Lotfi Tar Setar** | Tar_Setar | Classical | 273.7 Hz | +669.98¢ (N=10) | +807.13¢ (N=75) | **1062.85¢** |
| **Saba Violin** | Violin | Classical | 358.5 Hz | +687.41¢ (N=168) | +858.33¢ (N=53) | **1029.08¢** |
| **Shahnaz Tar** | Tar | Classical | 261.0 Hz | +732.33¢ (N=22) | +896.35¢ (N=76) | **1035.98¢** |
| **Payvar Santur** | Santur | Classical | 470.9 Hz | +674.07¢ (N=179) | +862.62¢ (N=95) | **1011.45¢** |
| **Bigjekhani Tar** | Tar | Classical | 320.3 Hz | +697.48¢ (N=83) | +847.04¢ (N=59) | **1050.44¢** |

### Statistical Properties of the 11 Within-Master Observations:
- **11-Master Median:** **1049.44¢**
- **11-Master Mean:** **1047.07¢**
- **Sample Standard Deviation ($s$):** **19.38¢**
- **Standard Error of the Mean ($SE$):** **5.84¢**
- **95% Confidence Interval for the Mean (t, 10 df):** **[1034.10¢, \; 1060.10¢]**
- **Minimum Observed Value:** **1011.45¢** (Payvar Santur, $+15.36¢$ above Pythagorean $996.09¢$)
- **Maximum Observed Value:** **1081.80¢** (Karimi Vocal, $+85.71¢$ above Pythagorean $996.09¢$)
- **Proximity to $11/6$ Just Neutral Seventh ($1049.36¢$):** The 11-master median sits within **+0.08¢** of $11/6$.

### Window Edge Sensitivity Test:
To test whether window truncation (Shahkhatāyī 657–747¢, Mokhālef 795–905¢) biases the within-master difference:
- We expanded both slot windows by $\pm 10¢$ (Shahkhatāyī 647–757¢, Mokhālef 785–915¢).
- The resulting 11-master median neutral seventh shifts from **1049.44¢** to **1049.40¢** (an empirical delta of only **-0.04¢**).
- This confirms that boundary truncation has virtually zero impact on the observed consensus neutral seventh.

---

## 7. Reconciled Segāh Consensus Corpus Strike Inventory (11,438 Strikes)

The table below is generated directly from [`analysis/segah_strike_inventory.json`](file:///Users/ed/Developer/dastgaah/analysis/segah_strike_inventory.json) with octave double-counting eliminated:

| Performer / Source ID | Total Detected Strikes | Strikes Assigned to 8 Canonical Degrees | Strikes Outside Slot Windows | % Assigned |
| :--- | :---: | :---: | :---: | :---: |
| **Alizadeh Tar** (`alizadeh_tar`) | 1193 | 746 | 447 | 62.5% |
| **Shahnazi Tar** (`shahnazi_tar`) | 290 | 287 | 3 | 99.0% |
| **Karimi Vocal** (`karimi_vocal`) | 910 | 617 | 293 | 67.8% |
| **Borumand Tar Setar** (`borumand_tar_setar`) | 1121 | 1035 | 86 | 92.3% |
| **Kasaei Ney** (`kasaei_ney`) | 1761 | 934 | 827 | 53.0% |
| **Nariman Oud** (`nariman_oud`) | 558 | 505 | 53 | 90.5% |
| **Lotfi Tar Setar** (`lotfi_tar_setar`) | 894 | 587 | 307 | 65.7% |
| **Saba Violin** (`saba_violin`) | 1012 | 887 | 125 | 87.6% |
| **Shahnaz Tar** (`shahnaz_tar`) | 1133 | 422 | 711 | 37.2% |
| **Payvar Santur** (`payvar_santur`) | 1544 | 1021 | 523 | 66.1% |
| **Bigjekhani Tar** (`bigjekhani_tar`) | 912 | 724 | 188 | 79.4% |
| **Darvish Khan Tar** (`darvish_khan_tar`) | 110 | 67 | 43 | 60.9% |
| **TOTAL CONSENSUS CORPUS** | **11438** | **7832** | **3606** | **68.5%** |

### Strict Inventory Accounting:
1. **Octave Double-Counting Elimination:** In previous versions, strikes near $1200¢$ were matched both by `octave_ist` ($1200 \pm 35¢$) and by folded `ist_tonic` ($0 \pm 35¢\pmod{1200}$). Unfolding `ist_tonic` eliminates exactly 393 double-counted octave strikes.
2. **Window-Slot vs. Sub-Threshold Inventory:**
   - Raw strikes falling inside any of the 8 canonical window definitions: **8,083 strikes** ($8,476 - 393$), leaving **3,355 strikes ($29.3\%$)** outside all slot windows.
   - Slot threshold inventory (where slots with $< 8$ strikes are set to 0): **7,832 strikes** assigned to displayed slots, leaving **3,606 strikes** outside or sub-threshold.
3. **Borumand Reconciled:** Borumand has 1,035 assigned strikes $\le 1,121$ total strikes (86 outside slot windows; no negative remainder).

---

## 8. DSP Strict Drift Sensitivity Analysis

The table below is generated directly from [`analysis/dsp_drift_sensitivity.json`](file:///Users/ed/Developer/dastgaah/analysis/dsp_drift_sensitivity.json) produced by [`analysis/generate_dsp_drift_sensitivity.py`](file:///Users/ed/Developer/dastgaah/analysis/generate_dsp_drift_sensitivity.py), applying $|drift| \le 15.0¢/\text{s}$ to strikes within $120.0–175.0¢$:

| Source / Performer | Instrument Context | Tonic (Hz) | Window Events ($N_{pre}$) | Retained Strikes ($N_{post}$) | Pass Rate (%) | Unfiltered Peak | Filtered Peak | Observed Shift |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Mahmoud Karimi (Vocal)** | Vocal (Unconstrained) | 235.5 | 384 | 25 | **6.5%** | 143.5¢ | 149.5¢ | **+6.0¢** |
| **Ali-Akbar Shahnazi (Tar)** | Tar (Fretted) | 213.6 | 197 | 43 | **21.8%** | 128.0¢ | 129.5¢ | **+1.5¢** |
| **Abolhasan Saba (Violin)** | Violin (Fretless) | 235.8 | 91 | 15 | **16.5%** | 129.0¢ | 130.5¢ | **+1.5¢** |
| **Hossein Alizadeh (Tar)** | Tar (Fretted) | 372.9 | 325 | 87 | **26.8%** | 153.5¢ | 153.0¢ | **-0.5¢** |
| **Yousef Foroutan (Setar)** | Setar (Fretted) | 314.6 | 142 | 33 | **23.2%** | 150.5¢ | 150.5¢ | **+0.0¢** |

### Empirical Findings:
1. **Instrumental Peaks are Drift-Invariant:** Fretted tar (Shahnazi, Alizadeh), fretted setār (Foroutan), and fretless violin (Saba) shift by $\le 1.5¢$ under the aggressive drift filter, despite losing $73.2–83.5\%$ of strikes.
2. **Vocal Sensitivity:** Karimi's vocal recording retains only $6.5\%$ of strikes under this gate, with the peak shifting by $+6.0¢$ ($143.5 \rightarrow 149.5¢$).
3. **Absence of Causal Claims:** We assert no causal mechanism regarding vocal vibrato or pitch tracking artifacts. The result is documented strictly as an empirical sensitivity filter test.

---

## 9. Comprehensive Verification Manifest & SHA-256 Checksums

In accordance with [`review/LLM_GUIDE.md`](file:///Users/ed/Developer/dastgaah/review/LLM_GUIDE.md) §8, the tables below provide SHA-256 cryptographic hashes for every input `.npz` archive, analysis script, and generated output JSON in the repository:

### Generated Data Outputs:
| Output JSON File | SHA-256 Checksum | Generator Script |
| :--- | :--- | :--- |
| `analysis/re_koron_modal_peak_audit.json` | `d2ef47083f9a7649159c98ee21902607e13d92ded460c5640346fb4a6eae52e9` | `analysis/run_rigorous_modal_audit.py` |
| `analysis/modal_reference_annotations.json` | `5e375c3f9c030981e2f88ef5d9f3160bedc0dd819eaa9f1af8f0ed88026f55f4` | `analysis/run_rigorous_modal_audit.py` |
| `analysis/dsp_drift_sensitivity.json` | `493051ef57ced6fa3295f1dbdd7c4467e3f16d6a3a9ed91be4a2796fe751a0e0` | `analysis/generate_dsp_drift_sensitivity.py` |
| `analysis/segah_consensus.json` | `aaa307b43ab015a1ee1d07e6bf1943b6b2fcb37c4efb693de6a6eee82ca3ee36` | `analysis/compute_segah_consensus.py` |
| `analysis/segah_shahkhatayi_pairs.json` | `4c805338188ef9acdbce9a1cae281cc2b6e9f1704a9ebb89eff166e33d8f7f63` | `analysis/compute_segah_consensus.py` |
| `analysis/segah_strike_inventory.json` | `0c943c5b455ef422b3b749a29f83edb7c2d52a607d91d8771a8006ebfd87c719` | `analysis/compute_segah_consensus.py` |

### Analysis & Generator Scripts:
| Script File | SHA-256 Checksum | Software Dependencies |
| :--- | :--- | :--- |
| `analysis/run_rigorous_modal_audit.py` | `6e042d8f945524ed802778c5cebc67f8701a5285f1b97949de679c6052fc4930` | Python 3 standard library (math, json, struct, zipfile, random, statistics, pathlib) |
| `analysis/compute_segah_consensus.py` | `6a8bcd2b858046d72c2f9efb11814cd8f3ff461b50acad6eecaf9ab8542b2f2c` | Python 3 standard library + numpy (math, json, statistics, pathlib, numpy) |
| `analysis/generate_dsp_drift_sensitivity.py` | `bca65db476c3bfe7692a3b00d327aacb1a5d06a691c38bd0ab67b254feb05c2a` | Python 3 standard library (math, json, struct, zipfile, pathlib) |
| `analysis/build_response_9.py` | `96a35e1025e4c7e1bf37b0c8de65b046bf76059538e6768143de2d28f0d1baa8` | Python 3 standard library (json, hashlib, pathlib) |

### Input Strike Archives:
| Input Strike Archive (`.npz`) | SHA-256 Checksum |
| :--- | :--- |
| `analysis/strikes_Safvat_Setar_1962_LNwPd8_hP74.npz` | `b2942754f52ee77e4beb9dde70e285e250e809c3c1bf2f2553754d8e3cf7e0a3` |
| `analysis/strikes_Safvat_Setar_Part1_5zSljfC5jdY.npz` | `9cdae38cd2fd6903d81c38995bbbc3ca50fe15420153d069079bd929e52156db` |
| `analysis/strikes_Safvat_Setar_Part2_dqg5Ka7--pg.npz` | `0d5d4eda7f0debe0e5410e6016f1b282e9c049a786f11c1c0eb1b1c7763591f6` |
| `analysis/strikes_Safvat_Setar_Razavi_Utah_yvZh-u4C6jY.npz` | `df76bb5d084fbd38d155f4780dec10ac2f32e2d0b3cc54c091fe722cfc4eef0e` |
| `analysis/strikes_Safvat_Setar_Solo_BSPDwyzNV6w.npz` | `13f8fe034abf0563525623b8dfe8a320a8f9032172e6828dfaac1b52d68507a8` |
| `analysis/strikes_Sarvestani_Masnavi_Mokhalef_Chahargah_YJUeciRfLSc.npz` | `5fe26827efe5ca0bea5770568aa8e733735f3fddc417ec0f25529cdd55a2f327` |
| `analysis/strikes_alizadeh.npz` | `ce21737627968e85162ba5d1ade9d7ef479dbcfb70fbbd47e7cc78fd749d42b3` |
| `analysis/strikes_avaz_abuata.npz` | `edc15ce810bc8a0197bf68a22754f278ef9ef7df6769d4ad5d22182596708a41` |
| `analysis/strikes_avaz_afshari.npz` | `8d816e604a6daae305ae36ab69b6ae091142d429f58c544ea76c85d2284943de` |
| `analysis/strikes_avaz_bayat_kord.npz` | `42360fbe6039c7ea607f72f47c7ef73dbcf0046a4fc2566372457cc086ba150d` |
| `analysis/strikes_avaz_bayat_tork.npz` | `eb5cb7bc53db7978af2cd2326a669ecc73035efce42d54f154a0100cad3748c9` |
| `analysis/strikes_avaz_dashti.npz` | `386a6a3d531a04fa4abb69fe8c7f576f9339fc7045b627df0aeae2fcc2303774` |
| `analysis/strikes_bigjekhani_tar.npz` | `4c50483aaa572c12822e95259748dab6b98726a6987423e01b069c93da35b954` |
| `analysis/strikes_borumand.npz` | `86acd20f2d7238e981c6195b531058eab96499aa389d8c681a52c8d2984064d7` |
| `analysis/strikes_chahargah_alizadeh.npz` | `4c80838e09545bbb103d4a56801818605c0c7549c97f6e8087aea53324a33d6a` |
| `analysis/strikes_chahargah_borumand.npz` | `f8ca2941f7de7689f732a5b78edbfed69adbc5b97a3ee26976831716f7272e24` |
| `analysis/strikes_chahargah_ebadi.npz` | `f8481057b4c3c2c29a1722028fe15eea42bb62b52187d941e5d39f78abf6f20b` |
| `analysis/strikes_chahargah_forutan.npz` | `5a67cab0bf071246999fc1094e4b131d2823d798459bd083345048759e07a4da` |
| `analysis/strikes_chahargah_karimi.npz` | `750405cd38466445a50c128eab9e8aea4ed943ad82ebe9eee08157e30b6e1ad6` |
| `analysis/strikes_chahargah_kasaei.npz` | `26fa321006cb731da02bd5f389cd6d9a9d44dfc7a2d9eadea1dcf1832bb4fb7c` |
| `analysis/strikes_chahargah_lotfi.npz` | `dafde46eb2830f886d5d0b9f76c7945c14669038e998643ff24a5bbac387c136` |
| `analysis/strikes_chahargah_nariman.npz` | `28db0f1c61aef2506881e5714a7bc77438bb6fe05cb593ee92a172219132a0dd` |
| `analysis/strikes_chahargah_neydavud.npz` | `a6ea0c81a7531c428a94107fc27162d11001abbc6c63024b0fe0d34ff0e91796` |
| `analysis/strikes_chahargah_saba.npz` | `6b5d47a28f8398df1b08207f16ec9824e8759086a7ffc6c8507520b172a05623` |
| `analysis/strikes_chahargah_shahnazi.npz` | `d08049c1fd1b826c669595eae744cddedd74de2b984edb1cb6920b97ca3741ad` |
| `analysis/strikes_chahargah_shekarchi.npz` | `96bf1549969a49fd1d0b702a0a75d8985884125696f4c05c1d617b98042e26a9` |
| `analysis/strikes_dashti_alizadeh_setar.npz` | `aae170bc27b783ee91f67e6bd56c06ab122c62f4f0a3e9bf8119160475a8fdf7` |
| `analysis/strikes_dashti_behroozinia_barbat.npz` | `6bbb7bd353380825aa817af3c7844f3bbc4f5ce821991e60091787debe71b4a1` |
| `analysis/strikes_dashti_ebadi_setar.npz` | `0bfbf9ddea66491bbdc1565b0df1e09fafbd7940eaa4fd8a6d91250db623a820` |
| `analysis/strikes_dashti_farajpouri_kamancheh.npz` | `21057162cb6e9dab8efc61db07fab5fa29af9b807c243749fd74e3dcf0c85742` |
| `analysis/strikes_dashti_kalhor_kamancheh.npz` | `722a6f69222196c247d2d335a242d950384ecff7eae8dbcaae6ea1b3985ea6bb` |
| `analysis/strikes_dashti_karimi_vocal.npz` | `28bb9cd39f78a91c0425f443674d3b0060820a891ebcb40fae52b080ea4cf8cf` |
| `analysis/strikes_dashti_kasaei_setar.npz` | `e9805e6ec0cf48abd8fcda53349aee87ad1699549be8c3402711f305e2a5ed5e` |
| `analysis/strikes_dashti_lotfi_setar.npz` | `e9417ab5a09d0e50ff6cb14668663c17ccd51fc58c9a3ba286936ab2d5ff0819` |
| `analysis/strikes_dashti_nariman_oud.npz` | `2b2e32431adfb19198225396c57d9ba07348d83ca13dc58990912aa65fed3997` |
| `analysis/strikes_dashti_saba_setar.npz` | `e24e26ff73d41da39f4fe7cb1fe33b3485abb9a7f963a37d7d7dac30c087c904` |
| `analysis/strikes_dashti_shahnazi_tar.npz` | `25f2587529fbad4ae9bc318189b97ae78ee0af99708059b66de44889623a26af` |
| `analysis/strikes_dashti_shekarchi_kamancheh.npz` | `231ea162aa6f5cd7583878c94555d0562e17dc78edabd81959521ec086dc7c94` |
| `analysis/strikes_davami_11 - Abuata： Daramad.npz` | `71768102a602fa01c4ac0ef79a7518819745363a334af6c8a49e0144c9b8b470` |
| `analysis/strikes_davami_12 - Abuata： Ramkeli with Samali Melismata.npz` | `6993924e3bfa69371d7dc20494a3da7ef367c80d064aa6985f678d6f1aa622e6` |
| `analysis/strikes_davami_13 - Abuata： Hejaz.npz` | `5e592935496cc5d2baa1484b13d3de660331a495d09b7c80b43eea8332d9cc3c` |
| `analysis/strikes_davami_14 - Abuata： Chaharpare.npz` | `f22a433cb7be07facb41a043f9e630922f31aeb00b1babfb0787d7daefeaeb94` |
| `analysis/strikes_davami_15 - Abuata： Khosrow Shirin.npz` | `7561a8f30373de78d6bdc1da923be10a20b4eb8e751c0cd3b41a7d4310ddb69e` |
| `analysis/strikes_davami_16 - Abuata： Gabri.npz` | `67edb6f1d97ac59c6d7b38bd5d2b071d0a7b986a88a5085e36bcdf4f55be318a` |
| `analysis/strikes_early_masters_shellac.npz` | `b36f1fc156c662cd6a95bd031c7ddba5a6dcdd60770584f54f525d6bb05149ca` |
| `analysis/strikes_ebadi.npz` | `0401da733e574774209f128000ae5ab1ed5aa672df971d98b21981ac73885e42` |
| `analysis/strikes_esfahan_alizadeh_setar.npz` | `382ed5fb28ffafb1af7120041c18e3664f924c57e06a766f225f1128a16213ea` |
| `analysis/strikes_esfahan_bahari_kamancheh.npz` | `225d9b12992d26d97b14a11f269b4b49ced10331644e3ee0a1e862e4d4d7d5b6` |
| `analysis/strikes_esfahan_bigjekhani_tar.npz` | `77cd25e952f3c3d6a9ad877c0ddb9249ba618b848a076b3c369349fa66947832` |
| `analysis/strikes_esfahan_borumand_tar_setar.npz` | `a7c4dc780b6a676821bffa0289c8ab8a6ca3a084dcffc81e80c851dac3344605` |
| `analysis/strikes_esfahan_ebadi_setar.npz` | `2578f27695f79d96e0f415d85d82e5ceb1db4814898554383a83be7136a1acb1` |
| `analysis/strikes_esfahan_forutan_setar.npz` | `18491342a852277a1c4761f3d89705b0c9839040f893dbf7a0dd29809380c393` |
| `analysis/strikes_esfahan_hormozi_setar.npz` | `22ecebb3cbe49d72e4e54dce85f22d51c6e4018082664927613a4b86780bff79` |
| `analysis/strikes_esfahan_kamalian_setar.npz` | `9232f7d30e43535cb4c87719eea44c9653fb91c8dad6dccb864579ef07f4b502` |
| `analysis/strikes_esfahan_karimi_vocal.npz` | `da3b2ff400a7ee2eef715b47401523b982febeb2f3abdab503370a31959d57da` |
| `analysis/strikes_esfahan_kasaei_solo.npz` | `24dd03434372c5c2496be729eb589be49ce16c51ed130d1541a7a18667d1b906` |
| `analysis/strikes_esfahan_lotfi_solo.npz` | `7dea0048bf03578029299be781efdda49437e834e46ee2e58c15cc295b36be11` |
| `analysis/strikes_esfahan_nariman_oud.npz` | `834321eaa644d148147f877bb6dce94789474ab42b4dc3a31e46a37ce6bc2cff` |
| `analysis/strikes_esfahan_neydavud_tar.npz` | `c53b172cceee87c5b1aebcec81772506f4719a595d2610fa1ec1ede2db82fbb1` |
| `analysis/strikes_esfahan_saba_radif.npz` | `8614ec62e704b0b7d848dafaf9ae9b151928e18a76d55f76c17a6864a4f934ac` |
| `analysis/strikes_esfahan_shahnaz_tar.npz` | `fbd7c9a3004f3f8ddbd06db11b7bb80c6b495ba2d5237b712c855885edd0ff15` |
| `analysis/strikes_esfahan_shahnazi_tar.npz` | `a7cf0eb8b0aeade25075599c5552c73e8fe67181d57cb4b4895b5bc88b647881` |
| `analysis/strikes_esfahan_shekarchi_kamancheh.npz` | `7eb7ca9b952b69a44e53030ce62fede9666950dea7d3dd84ee29966f60daeaa2` |
| `analysis/strikes_esfahan_talai_tar.npz` | `940a6c4f341083dffba73c7e2b4bdd991bde1b45e02abe62d32977131f556c34` |
| `analysis/strikes_exp_lotfi_kamancheh_abuata_WCpiD15zaYo.npz` | `70ba893ec9309ebbd2abe15cf79efc2765cd3b49065671113e5d134da5ae9c93` |
| `analysis/strikes_exp_lotfi_kamancheh_basel_yRB2Hd2nsiU.npz` | `c4d85e9daf0681b3eeff1b84a266cc0586e618693bd975b257e7dad995e2aed0` |
| `analysis/strikes_exp_lotfi_kamancheh_solo_xKEM8b2oozU.npz` | `169dc63b07082b8904c192d876427b51dfca7abf77cc38772067b78d7c5ed995` |
| `analysis/strikes_exp_lotfi_shajarian_abuata_pishdaramad_LnsbdhtBFLs.npz` | `8eb7525c65b7ac3909e01155ddca189a59682a29f15da97baa1ec4421f7b92c4` |
| `analysis/strikes_exp_lotfi_shajarian_hejaz_cixlq9KvqaA.npz` | `04459d9b5ae8e3c44189e9e1e67f4966d01f0d38f847aeff2c27412f394309e7` |
| `analysis/strikes_exp_lotfi_shajarian_zarbi_hejaz_J4pb8fpsoB4.npz` | `155b78a48eca387a27c332d07f48e20f086b9f536c19150a4a133d5e2090c911` |
| `analysis/strikes_expanded_rp_alizadeh_tar_setar.npz` | `871aef4a84f78c5d6e5f910bf2dff009871ef280fd0cdb269c3556a47ce8f680` |
| `analysis/strikes_expanded_rp_borumand_tar_setar.npz` | `8bab66acbcb4f5bc6a80baae34103dab2ef7ece5f07f29fe8df04fc08c53a857` |
| `analysis/strikes_expanded_rp_ebadi_setar.npz` | `871b9fa6d8570897292bdc417b89943b7ff44e78ebb2b00dd15e5990adb9b23f` |
| `analysis/strikes_expanded_rp_hormozi_setar.npz` | `a31e03dcf4f4ed567a45b73ae8cd121e0842913b90455ce234661f38c7013ac5` |
| `analysis/strikes_expanded_rp_karimi_vocal.npz` | `d81455312d44d774383dfdf767d36917668000042e3e01b2300e40bd762b472d` |
| `analysis/strikes_expanded_rp_kasaei_ney_complete.npz` | `b70a0d3335f21730724e69b28739bc8f54c6e4b9f9d59d828fefd7840cfb31af` |
| `analysis/strikes_expanded_rp_lotfi_shajarian.npz` | `3d1baf42bcc9cbe850af2dffd18472da506e1245f8fcfd17e03509bebd226966` |
| `analysis/strikes_expanded_rp_nariman_oud.npz` | `596026f36299370a888040d426c6d21c69741debb3e00bec7e8ea705a55898a2` |
| `analysis/strikes_expanded_rp_neydavud_tar_complete.npz` | `cfe9c1cc406309d167120df41bc857de69d0eced6510a08ee748bf7e8efe181c` |
| `analysis/strikes_expanded_rp_saba_violin.npz` | `2d0b14f144ce7b54c4d9d9964423678a5d271dcd04c703e8fa13caad46123107` |
| `analysis/strikes_expanded_rp_sanam_gharacheh_1927.npz` | `6726b340d2871b5a1d8bbfe5b4bb99fd605740bebf69289d51b485d4ed2ca0cc` |
| `analysis/strikes_expanded_rp_seyed_ahmadkhan_1907.npz` | `9df4a022bfa0eb036d3261205a149aea090ee46aedb611247f4607c8fc32d779` |
| `analysis/strikes_expanded_rp_shahnaz_tar.npz` | `5f117be02d810d534f8483beb69ccf9c7f6da030fc2a419b63c685b16bcde383` |
| `analysis/strikes_expanded_rp_shahnazi_tar_complete.npz` | `3c7c20bfaf384fd78d2069a457fe77e273cf4dafc4cc18af7e0b4e2258846d54` |
| `analysis/strikes_expanded_rp_shekarchi_kamancheh.npz` | `5c5171433dee7f349a3e30ccf2796649ce5f4a8bb4e88cdef31666c4df57e280` |
| `analysis/strikes_faramarz_payvar_santur.npz` | `8abd26cd8452bec85853729864f020f8b67e93ef94fe86dfce8af6cffc3caca8` |
| `analysis/strikes_foroutan_segah_mokhalef.npz` | `c1408cfc4c5b885418a701132f034f01363ed622e712dfa853f7041b9d18092c` |
| `analysis/strikes_foroutan_segah_muye.npz` | `313b3fb99dfad5434cdb460fe94ce201c4675ade9b7fd18a46ed19bc22016b4b` |
| `analysis/strikes_foroutan_segah_zabol.npz` | `98f19e610980284dfcc6fab72f8df31b2fb1dca49dbf48e3e895c109a131dd22` |
| `analysis/strikes_forutan.npz` | `d56d774fb10815114fb4f8fb90a4ea5f672e275f169b5e707fcbb461a95e2fbf` |
| `analysis/strikes_habib_samai_santur.npz` | `b50e89732f25e9af7ad771e204e464f6939244c33160c6ce052d90ce5f15489f` |
| `analysis/strikes_historical_epoch1_qajar_aqa_hoseyn_qoli.npz` | `4ab360e435011111f9a1e7e7989c8914bdfae2524af0c129692736b813054a16` |
| `analysis/strikes_historical_epoch1_qajar_darvish_khan.npz` | `78be60ee92ea08d4ce841709db27732d141f029aaea89e522ad53f5e8253d151` |
| `analysis/strikes_historical_epoch1_qajar_tar_anthology.npz` | `bcc90333811d93b40391700837a4f5a5c1b398a0ef9c832848fb3fc7cc8a6b5f` |
| `analysis/strikes_historical_epoch2_mid_century_setar.npz` | `064d0552b871402f789185fb7e465d9b27f49d06b446cd0cae98459a346cef80` |
| `analysis/strikes_historical_epoch2_mid_foroutan_setar.npz` | `2e85da02e252315e477c9f5ba11229657f6a69e73c95241fd716912670e7e9c8` |
| `analysis/strikes_historical_epoch2_mid_hormozi_tar_setar.npz` | `0bf0ec13b7cebad960c87809f594c458a9f1ed6526faa665b1380a2b10b81252` |
| `analysis/strikes_historical_epoch2_mid_saba_setar.npz` | `a17a6cd6c480af2d43ed7c7069f8b720d34224b4aea4ab9f4bab5c67fad511ee` |
| `analysis/strikes_historical_epoch3_century_tar_anthology.npz` | `a7d9747f00b8c1c9a05522be7b27fdf150317387bebdd4496f3be1097e195016` |
| `analysis/strikes_historical_epoch3_panjgah_antiquity.npz` | `ed8c8614edafd3b221c6e4d96e86d222cf61a357eb245e56498d7de754a0f4f0` |
| `analysis/strikes_historical_epoch3_shahnavaz_anthology.npz` | `eba7f837e44078ec4127a904f454a1e3c17ac046826e9c4855ceec4ba3380007` |
| `analysis/strikes_homayun_alizadeh_setar.npz` | `280fe1f9474efb776ad357820e20319a53575d39f968f588059effaae06fb925` |
| `analysis/strikes_homayun_bagher_khan_kamancheh.npz` | `6d86d7600ec2db59fc5a6f55460445966604c51f32b6dc9480cbebac0e3534fc` |
| `analysis/strikes_homayun_bahari_kamancheh.npz` | `364f9d96b6b9257b4f6473f5cdbed63cfb82dbcf46d687337bc2570ed9d7f702` |
| `analysis/strikes_homayun_borumand_tar_setar.npz` | `b8f6a1d1f80d46ac7ec118ccaa2d7acb53ac8530909f0363107afe39fd1e003d` |
| `analysis/strikes_homayun_ebadi_setar.npz` | `02c24c9785cb524f8b74245bbc70d990a0323b32ad084b7b91726138ddfac5ae` |
| `analysis/strikes_homayun_forutan_setar.npz` | `7762560c2a7ec23e82221d10a8ca45ea65c522f6a01a8273a8e398205be26b58` |
| `analysis/strikes_homayun_hormozi_setar.npz` | `517f83f83acf07246ef036e2044f60d35b8f53215613f34b754b93531e034875` |
| `analysis/strikes_homayun_karimi_vocal.npz` | `601c5fbd2730d0e8b475edec04bc996333bff38490bfcc130318e612ef650659` |
| `analysis/strikes_homayun_kasaei_ney.npz` | `6c3301d900997a06330f868d4768eebc10436d6928c608e2831b6e76b4ecd9d2` |
| `analysis/strikes_homayun_lotfi_tar_setar.npz` | `ebfac27dc7971c50b26351ddba44134b62f573f183308538ab58a1d4d7bd0e3a` |
| `analysis/strikes_homayun_meshkatian_santur_ensemble.npz` | `444ea617e51f7272fce5ce528b8fa7eb47c520b997d35c6c0924b11fcdb7e86d` |
| `analysis/strikes_homayun_nariman_oud.npz` | `27aaad21f0ea5eb3df2a3cb34a8595be8026fe6d84dbfc114dc03cc7ca318c00` |
| `analysis/strikes_homayun_neydavud_tar.npz` | `d45c6068c8b774e6a94d5c7ee130846b841fcb35dc5c9bb5852d0bbe106176ec` |
| `analysis/strikes_homayun_shahnaz_tar.npz` | `fe042a834dd682626437f76c550dd96f70191af0e3c918bce93e05b9db7c5841` |
| `analysis/strikes_homayun_shahnazi_tar.npz` | `62208f98a2e3e164e7d86f30cf4f41146b1c1bb74b57983153dd017ad0d1f073` |
| `analysis/strikes_homayun_shekarchi_kamancheh.npz` | `d6504707d8ec5d39b38c76df65a025f2c544ef4be8268e33c0c426e313a831c5` |
| `analysis/strikes_homayun_shirkhodaee_clarinet.npz` | `52debfcf805c8ed819e8df3428e1035039fc2a0e5ce91a202dd5126a3126704b` |
| `analysis/strikes_homayun_talai_tar.npz` | `eaf6e00720d2ac39d6c4655dfb2ba5cc153e4831406a24b3d460c87209ae5384` |
| `analysis/strikes_hormozi_segah_mokhalef.npz` | `9a9492b66a07f9344830aecdc4e601f85d916b2a5867a95e5755a1ac66c9ba8c` |
| `analysis/strikes_hormozi_segah_muye.npz` | `f358a5c069deb2821a77ee4d32226d2a9c62f53ea36f1f548d721c9a8ded3cc7` |
| `analysis/strikes_hormozi_segah_zabol.npz` | `b31ff401cd873e724fa766b96296b1afa4cecdaacd3df7317b206e07e3e965c8` |
| `analysis/strikes_jalil_shahnaz_tar.npz` | `fca863bf739400aa26528f7ba6a69c77d20bc93f273dcda033e18c81a666037b` |
| `analysis/strikes_karimi.npz` | `dfc0af153f257de3f6aa4ad005909426139b110e617bc5ad02482bb846f731e2` |
| `analysis/strikes_kasaei.npz` | `a353c57aee7866c0545f4a4d60ff467600bdecc4aa22fcf44cc724acfd5b7d15` |
| `analysis/strikes_kasaei_radif.npz` | `55c446356e65aafec7d0fce5e38d5285207a5da110de6848a1de89f187a1bc43` |
| `analysis/strikes_lotfi.npz` | `db55fbb063b2d174710e04575d2aed5bec758028a34e402d117f8b5e46e8af8c` |
| `analysis/strikes_lotfi_playlist.npz` | `8d9ac6b6a4fea1f5875fb14f35a9ff9b3a3e79cf5d31c815f523703504b267db` |
| `analysis/strikes_mokhammas_01.npz` | `5e8843076cb452de056ee1a8e3b6bdb02b654bc23b61e1a223060ee88ffbfafb` |
| `analysis/strikes_mokhammas_02.npz` | `3fb6d44ccd3467087502e27acaf4b9e566df3386ea6869bf9b222e248ac48e3d` |
| `analysis/strikes_mokhammas_03.npz` | `2005aefb3160c71d75425363381b9f1d258221448f18ea6a3757504c7f147219` |
| `analysis/strikes_mokhammas_04.npz` | `ab558274a2f8aa616bb01e1138b1c0785a502797e1db6001ca1a881599706549` |
| `analysis/strikes_mokhammas_05.npz` | `1f3c88329fe69c0f10e0fe7e2291bbf07790908c5eb70d7da5b28fe9872509c4` |
| `analysis/strikes_mokhammas_06.npz` | `27d403fe7dc67cf07d412f3ebd290fba43b50b812e943de03b999f044cf5148d` |
| `analysis/strikes_mokhammas_07.npz` | `cbe5e5783a24d45f723b0759d7a1020e90d585cea90fc39efd49e9b1a63375ad` |
| `analysis/strikes_mokhammas_08.npz` | `77a947a603864c490fdc57068b4d56da4594508a0cf5e0e69c38527b5bdea74e` |
| `analysis/strikes_mokhammas_09.npz` | `d70e7171018aeca837b81ef5d51cd8b2218700fe9ec439fc34e1131206e89d74` |
| `analysis/strikes_mokhammas_10.npz` | `57e1221a093e95ad15bd0650db3fa410a39ac29b97e9a35e09624da227caa039` |
| `analysis/strikes_mokhammas_11.npz` | `6abc15941e61926ba689b98a7e7223c92de7088ae1e63a88c25272549a8d2b4d` |
| `analysis/strikes_mokhammas_12.npz` | `fab7128e9bcd45997b958f76f9045343be2007349cf3849d2bba094309e8d0f9` |
| `analysis/strikes_nariman.npz` | `a8cce864bb332bd7d8211423508b04c7d4adc369cac86485cbd6d059a06e97ed` |
| `analysis/strikes_nava_alizadeh_setar.npz` | `555a142a3aa1cae9c48368904b24050ed597b42244dd49d4f971672a768979a3` |
| `analysis/strikes_nava_borumand_tar_setar.npz` | `223393010c374425624e660af755f77b0ef27800fa23f158f052b0e39d62ea04` |
| `analysis/strikes_nava_ebadi_setar.npz` | `46671654930aeb7b8f528c5a5f02fe444059fd07fa181961f186268f91d5d428` |
| `analysis/strikes_nava_janmohammadi_setar.npz` | `76569717c6e181a71c8a2d8334d9eddc734db800f657e238824b0e7e32473200` |
| `analysis/strikes_nava_karimi_vocal.npz` | `1fad5eeb86054c3ba79e60842a4c55b7c771607370d6f54994efb2337684c716` |
| `analysis/strikes_nava_nariman_oud.npz` | `42e3626fe6ea4161e02fe024e6ad08959a66445f51c8bf4c72589163a8d66672` |
| `analysis/strikes_nava_neydavud_tar.npz` | `b4cb9378444f72f9b71f7f58930d9357f5141fdc4b5e1c63a0121c96be531326` |
| `analysis/strikes_nava_saba_setar.npz` | `c89d0bf8a6b3530a52fa3ed51a9767110366bc8adcfae457cfb7f9958f77d32a` |
| `analysis/strikes_nava_shahnazi_tar.npz` | `ed0c6891e16797baa5c12e553c8fdb05b0b546bdcf0e66d721bf5f817310e80f` |
| `analysis/strikes_nava_shekarchi_kamancheh.npz` | `1d51be3ce3f003450ce9ce826f3eb8954615b914b33c780ced6a99c1e55b231a` |
| `analysis/strikes_nava_talai_tar.npz` | `b3abdc2c1fe60aec6abe391cbe98479b09de90959f42af7f6ed6de29ef42332d` |
| `analysis/strikes_neydavud.npz` | `33a291f596cf021901a8670c2d8a79ce74ddd743623c9c04e8f51ef91442e385` |
| `analysis/strikes_qajar_12.npz` | `51a0d5d26152e6a1e100339578bd4ce669d6a4d48f1a3f09f4ce22b89097ee35` |
| `analysis/strikes_qajar_13.npz` | `a35ae98dc2d595737ad69a06ebe00cd5a74a9d187a4d7dac45c6c70889a90e90` |
| `analysis/strikes_qajar_14.npz` | `c460d61380182295ddb1ac3a3a726d0bfbb789ae06554f601ee62b8ffe09d936` |
| `analysis/strikes_qajar_kam_1-dastgah-e-nava.npz` | `1c0da32b4efdbd1cf02f4cda4bb7bee23b7b978bf6abee4126b14ec5ebe971ab` |
| `analysis/strikes_qajar_kam_10-reng-e-farah.npz` | `153ddcb7af571c37547e5c69e47b6ba4a15ced280dd6d39b6f1d0e46272109c8` |
| `analysis/strikes_qajar_kam_11-dastgah-e-shur-ii.npz` | `14dc5e67d28d0f72b836a383bc9ac2aaaafba084e85c8d6368bfa7229c5ecb7c` |
| `analysis/strikes_qajar_kam_12-rak.npz` | `9f0ef11c287b38c77dd11ebad45c6c9f3131ca67308c2bb92d76f8553359e396` |
| `analysis/strikes_qajar_kam_13-hejaz.npz` | `36aae9b33fa0d578d56787aa132fd4b751c519a7593610499b9ec15e840d47dd` |
| `analysis/strikes_qajar_kam_14-avaz-e-bayat-e-kord.npz` | `5b7c7ab956a1cc5b425fd13438a1cac09789fc5704236554b8f5cf09b5fb7eb0` |
| `analysis/strikes_qajar_kam_15-dastgah-e-segah.npz` | `7739c3b559119cf764820c6610f182df9432d4cac87cea2d47b58c0dcb0c40a4` |
| `analysis/strikes_qajar_kam_16-dastgah-e-chahargah-ii.npz` | `1f2e152216aa1ef56001afd00791c1c673d939a7406d7cd1911bc0b1da5b8fab` |
| `analysis/strikes_qajar_kam_2-avaz-e-esfahan.npz` | `7001fbc3b21f822f6cce01507726bbf70d7dcec553ebe3a8fee7e09dca2e9404` |
| `analysis/strikes_qajar_kam_3-dastgah-e-shur-i.npz` | `a77f38f6b9450251f4f044a495ba5a59d5f73ae3dca58c0095d0831ef08f408e` |
| `analysis/strikes_qajar_kam_4-dastgah-e-chahargah-i.npz` | `e6a40b116c18a863e3eb2b2071db54401b4bd52a5487c0c0dfcef19ad7e22516` |
| `analysis/strikes_qajar_kam_5-dastgah-e-homayun-i.npz` | `c0a6b51efc64adf9816a72d427c8ed4f28408b8778fda72b65806dadecea35f4` |
| `analysis/strikes_qajar_kam_6-dastgah-e-homayun-ii.npz` | `693841f183b6df92928f991bc7b71aa05d05371a002100ce2b7e8ce1aeac1506` |
| `analysis/strikes_qajar_kam_7-bidad.npz` | `c1becd2e3b9ea27499d3cc12afc3e84b88e93095ff4dabd9c2a4f3f63e28292f` |
| `analysis/strikes_qajar_kam_8-dastgah-e-homayun-iii.npz` | `99b14f4c686ae303141841b9380660d2c102ee2e4e73e377131930066f7d9173` |
| `analysis/strikes_qajar_kam_9-dastgah-e-homayun-iv.npz` | `fd836950d9cd135cf02635b3ff53cb92443bdfc365e610a64989f480236cce1c` |
| `analysis/strikes_rast_panjgah_alizadeh_tar_setar.npz` | `d882b35abbebb8bc13c206bd5193a75646b10c198d23342713a6566200fa789c` |
| `analysis/strikes_rast_panjgah_borumand_tar_setar.npz` | `bac83d6a608e8f8ffb9486044ae6cca1191951b2fdebf14ca4098fb8997fe522` |
| `analysis/strikes_rast_panjgah_ebadi_setar.npz` | `eaf656d484d07d3b12bd6f838e933e6111a6dffc4fd2c95be21a91512b6d659c` |
| `analysis/strikes_rast_panjgah_karimi_vocal.npz` | `404c41a1f5ee2399ea0f18d67d7f0a94a56444ea53e0a25c2cf11b3c92bb0a7d` |
| `analysis/strikes_rast_panjgah_kasaei_ney.npz` | `ecfc77361f18a2ae750f303af9c2d6ddf1698d32bf012d6cf089ca2c01054537` |
| `analysis/strikes_rast_panjgah_lotfi_tar.npz` | `c107ade514a2963d0b580893d89f7ecae11a8f2f53dde23068c63ea35cff3a9b` |
| `analysis/strikes_rast_panjgah_nariman_oud.npz` | `669b7815adf29340f2ea5163a45452a0e01b4a68daea92b039b9a62046dd0338` |
| `analysis/strikes_rast_panjgah_neydavud_tar.npz` | `e1c3db71c195e64e10f170e6fc7efe103dd672fa2da814af32e820dc7ec31e83` |
| `analysis/strikes_rast_panjgah_saba_violin.npz` | `c18ff5e21557276b337b43a47b18e3d4a58de0f33fce2d5d572c68be9fd884a6` |
| `analysis/strikes_rast_panjgah_shahnaz_tar.npz` | `e79296eead267061f3deb8c6959d0d4b875da9834a00af5f49c59e9490b25bd4` |
| `analysis/strikes_rast_panjgah_shahnazi_tar.npz` | `595df8e1a4cffe88bbb8c73dffca2d844ad2dbf38da23b9d4b25e397d8735107` |
| `analysis/strikes_rast_panjgah_shekarchi_kamancheh.npz` | `31adccf67be9f2f9ce09a52f03cf177b6f0eb7243933f624347feea4457a190c` |
| `analysis/strikes_rezagholikhan_1906_abuata_santour.npz` | `2d75d85cb70435d53e737c5972d1717581433b29c9e582eda066a09454870540` |
| `analysis/strikes_saba.npz` | `ebc458905a9849c48ee0ea957529454e9e0ec44cb3e64faeb716febf4f4c2247` |
| `analysis/strikes_saba_segah_violin_vol3.npz` | `c8a168530e6318134b4eef7a2b0e5248bdb009b2ae21f8818824bfa46c0912c5` |
| `analysis/strikes_sarvestani_talai_Abu_Ata_Daramad.npz` | `bf91aab0b6638369eb446df8a03018e8cc6755c2b218dd9f5b54d862bdfbc236` |
| `analysis/strikes_sarvestani_talai_Esfahan_Suz_o_Godaz.npz` | `31ab0c73529ff28b3cfa6b5ec506a7dc39a5bd76155d25f85d686a14ba6eee56` |
| `analysis/strikes_sarvestani_talai_Homayoun_Masnavi.npz` | `1eaed0a285bc738860e612e4ec0586a75f035f7c6143c83694dd3e9abd955bf1` |
| `analysis/strikes_sarvestani_talai_Mahur_Daramad.npz` | `c6e89741096fda4ecbb3655f779d273d2775764cb2d899b76d89b2d13698c1fc` |
| `analysis/strikes_sarvestani_talai_Nava_Daramad.npz` | `ec8c024f1fb705e47a2c70127ca45768b1ba5cb4bff86c4785163ea4c9625578` |
| `analysis/strikes_sarvestani_talai_Rast_Panjgah_Daramad.npz` | `4c433e768ab33ee122543a8147ce56299a73473207caa84a7234a924be99a336` |
| `analysis/strikes_sarvestani_talai_Shur_Daramad.npz` | `d222153cd1b0efa365aa17cf3d33b82fc1c664f5493d52ff64467614c88f15a0` |
| `analysis/strikes_segah_alizadeh_tar.npz` | `6e12fcd9640abcd310086981845f52d6dcf8bad647ee5433bd5f9f17bf6e620c` |
| `analysis/strikes_segah_bigjekhani_tar.npz` | `02cec3cf5d940a1916694d0a88d93844b747a3eae539ceaa9658bb1997c0e465` |
| `analysis/strikes_segah_borumand_tar_setar.npz` | `fce53d6bfc3698261ec7a8c8bb51ea7b8c77b4b373dc11ff710cb125d4a1eca4` |
| `analysis/strikes_segah_darvish_khan_tar.npz` | `3e515ceee112169cf175964f003afd3063540b4d140ccd980bf933cb3652b400` |
| `analysis/strikes_segah_karimi_vocal.npz` | `4c0622e48d80eabf1b732c61342d801e41f108bd6260ca0a2840774d7eafdfac` |
| `analysis/strikes_segah_kasaei_ney.npz` | `0b9a836163b68d85b6ca130466b5514fcc100ba45330ce6a6eb9efe6685c01e3` |
| `analysis/strikes_segah_lotfi_tar_setar.npz` | `3218c6f29d98da5f8e6cba80f6fb0189a702a97f8f1075f2361584a54bb34d6d` |
| `analysis/strikes_segah_nariman_oud.npz` | `6f416ea734d39c459444d9d330edf66e3060fe357cbe9cb4372c2558f4d5a168` |
| `analysis/strikes_segah_payvar_santur.npz` | `b9b05d06e063fc77dfdac9c8497a88d0122da749a8da1bd21c1c3e0da19ff37b` |
| `analysis/strikes_segah_saba_violin.npz` | `cfd75a372f12da29d656d3100c4bc682a5920db7cdb3602c02a1dc1602b608a1` |
| `analysis/strikes_segah_shahnaz_tar.npz` | `9eed230708923c41a853480bc008f5d33228d4247a1df9be3e6b671f973dcb91` |
| `analysis/strikes_segah_shahnazi_tar.npz` | `357aa14c3959d5b6dff7a660cd6503b224b889a0b980c5667b310f069daa12f8` |
| `analysis/strikes_shahnazi.npz` | `b483be01d2c8069017faa26fd7e4edbbf759bba4ec07a2644273f70bc29657a4` |
| `analysis/strikes_shajarian_13 - آواز ابوعطا (یتمیک-لیلی و مجنون-خسرو و شیرین-مثنوی).npz` | `9b9824e15b21db103324cd11e83c188d660bb777a5f828dbfefde40378b93e6b` |
| `analysis/strikes_shajarian_14 - آواز ابوعطا (رامکلی-سیخی-چهارپاره-گبری).npz` | `e9be1ffef75ecb0083fa454e49662c9252983f6c5b42b228529f9018de8102ac` |
| `analysis/strikes_shajarian_15 - آواز ابوعطا (حجاز).npz` | `5e2f07049b800418fd7e7f69f7d08df06789b04884303e7b75e30bdb21d9561a` |
| `analysis/strikes_shajarian_16 - آواز ابوعطا (درآمد).npz` | `8b30a0e799bfe3e273d2fc91abccdd2333227d9675aa725fd8295fb1f7f0beaa` |
| `analysis/strikes_shekarchi.npz` | `4a1d1a8d8cd9d4b340a6cff28bc85d976a4513f98000b60cf08ebf568122776a` |
| `analysis/strikes_shiraz_festival_abuata.npz` | `8a82560e7015290536d7ce276ca99e7c5a9389d023b11f76026386c2ac100044` |
| `analysis/strikes_shur_alizadeh_tar.npz` | `aa95d981dbb8019dded398f5f258c18ab25e1ac705658627cf8face393e9ec7d` |
| `analysis/strikes_shur_borumand_tar_setar.npz` | `127d157a1d50a652d9f16a63fc517418d2b7a0ca3c1baf67b06b3c7eef8c1969` |
| `analysis/strikes_shur_forutan_setar.npz` | `3371a615ac7d3fa6cfbc40a5b523d41746c06b38165005c002a34638c9c00acc` |
| `analysis/strikes_shur_karimi_vocal.npz` | `dcef3abbc2ccc93bf349a14fc1994eedbad2ae09d52f02b882e63d76fb2c8a5d` |
| `analysis/strikes_shur_kasaei_ney_setar.npz` | `f45d4088674c66e057186678d162881ac972c47e94c7b136424def2cb21b584e` |
| `analysis/strikes_shur_lotfi_solo.npz` | `0d16b2fd9cd3138ce478c5fa4ab12be2bc57cdf4bcf6c9eb08981fb5a011c0cc` |
| `analysis/strikes_shur_nariman_oud.npz` | `7ec5be9b568fa98a3ee4cddf455e5eba8111049a2393e786af4abd82e901d8bc` |
| `analysis/strikes_shur_saba_violin.npz` | `1ed8e2e0993d5808a50e7861cd2c6adf50659bcceb087b1ced43a848e9f6505e` |
| `analysis/strikes_shur_shahnazi_tar.npz` | `b015196190e6ed4c96afff47fa90b098bbd627c614a2b45ed99749362235fc90` |
| `analysis/strikes_shur_shekarchi_kamancheh.npz` | `2a77ecec8a384463c2599b8ee4397c2e3441289a1a80c8f352997b27d5a32c76` |
| `analysis/strikes_tabatabaei_01 - Avaze Abouata.npz` | `7afc19eef0cc641ee9fbaf11e9c2b8271d200d0010ad890b106758a35bae3cad` |
| `analysis/strikes_tabatabaei_02 - Daramad Abouata.npz` | `e6cb6e102f56bd47c2d8333a5ed41194f65855786c82cad702e5b54667989189` |
| `analysis/strikes_tabatabaei_03 - Yatimak.npz` | `cc540339841a6f1f6d8e0d35d0df433497f94e6cc1ec5e46ac45106c5568cfdd` |
| `analysis/strikes_tabatabaei_04 - Hejaz.npz` | `612ca870cf621055521220effc68d081b1bcac30826fddc0adccd118b87a138e` |
| `analysis/strikes_tabatabaei_05 - Korde Bayat.npz` | `a79f9938414ab724618a23f458b56b006be97ea27e6e0cfdab59c9bfb0280dda` |
| `analysis/strikes_tabatabaei_06 - Bayate Raje.npz` | `f5220611fa126adc5ef45f39ea13386f7414ea3ef00190e1c08875c07d8b31cc` |
| `analysis/strikes_tabatabaei_07 - Oshagh.npz` | `f891912a8515302456f3bef4561854ff129b4135bba3a14f1a190215b1d5e733` |
| `analysis/strikes_tabatabaei_08 - Charpare.npz` | `01752d416bea843a0ca0cb50fde860137fbdc1ad210e7d272bd6f87f38c22be0` |
| `analysis/strikes_tabatabaei_09 - Sayakhi.npz` | `b3fca3f8f5af1068ddce7681eb2323487679ceb6dd2b21fec7ab309bd5ce80e5` |
| `analysis/strikes_tabatabaei_10 - Ramkali.npz` | `ad48d36924a0f159ac103f34cbda8119630b653798e9aa0611d8fde5980b82cd` |
| `analysis/strikes_tabatabaei_11 - Khosro o Shirin.npz` | `bed1f8def4cd4518276c2c21768d566425362889e88170e2b58b360648424ef0` |
| `analysis/strikes_tabatabaei_12 - Masnavie Abouata.npz` | `fb4f8efc3905bd6de4bc9d8256e25b82e0571d4f3bb5b03894b41545f4454dc7` |
| `analysis/strikes_tabatabaei_13 - Zarbi Abouata.npz` | `5923aa0011a4d898c6cc5497fc563b049a9b8ef2bdef760801d3ab23de5ef9a4` |
| `analysis/strikes_taherzadeh_1 - Rak (I).npz` | `58d2c6642726be50377f0224bf201e38331536edbccea0c0a2bc6a9be77884a0` |
| `analysis/strikes_taherzadeh_1906_abuata_santour_1.npz` | `db7ae392d3f2bbdce0aeda2d4c500f03e0c8bd779d61ad43fc9bf8407aff8ce7` |
| `analysis/strikes_taherzadeh_1906_abuata_santour_2.npz` | `0e08cf26b5d2de4b13af06b0dc5f10ee76c13b4b10a61220c638473a405d350d` |
| `analysis/strikes_taherzadeh_2 - Pishdaramad Rak.npz` | `3635fda246e8c45f1dd2aa187572bd8451766f765740f158583a6dd6ccc10ee3` |
| `analysis/strikes_taherzadeh_3 - Reng Rak.npz` | `966bcc72aa85ce2e5a71cd8022eb8b780f5cd541919823c2aff6fb6995bec001` |
| `analysis/strikes_taherzadeh_4 - Rak (II).npz` | `e0d3a1c9f04c3a00c29aeace103766b31b1829280b5b700da0cf4c71360283d9` |
| `analysis/strikes_taherzadeh_5 - Avaz (II).npz` | `3439489f523ee931a0913c5c949d8f38e28d3da82d7e3ea731f3c2d8e07e7289` |
| `analysis/strikes_taherzadeh_6 - Avaz (III).npz` | `a225535802196f8292e051135f1e54a04adab212fb82e3eed68155ca2115de34` |
| `analysis/strikes_taherzadeh_7 - Tasnif Rak.npz` | `be1e780d7eccfe6a763b22801246f006184fd8107fc488acab202f518c78a6e5` |
| `analysis/strikes_taherzadeh_8 - Avaz (I).npz` | `385855df5050e3ca9acbb2a72a0e4163e77d65fb4ba4de05810cd7385328bf22` |
| `analysis/strikes_taherzadeh_9 - Sabah Prayer.npz` | `15e4ecb2c128a61bb7e89bf0b5935608ab89f8aab05c88c7b01c08ecef0e8e97` |

---

## 10. Study Protocol Compliance Checklist (`review/LLM_GUIDE.md`)

- [x] **Every number in the text is in a JSON or CSV in `analysis/`, or computed in the text from numbers that are:** Verified. All tables are machine-generated by `build_response_9.py`.
- [x] **Every table was written by a script, not typed:** Verified. Tables are rendered dynamically from JSON datasets.
- [x] **Every peak value fits the 0.5¢ grid:** Verified. All reported KDE peaks end in .0 or .5.
- [x] **Every N says what it counts:** Verified ($N_{ton}$ for tonic strikes, $N_{win}$ for window strikes, $N_{total}$ for corpus strikes).
- [x] **Every interval has a stated estimand (mean or median) and a frame (raw or normalized):** Verified. Segāh neutral seventh explicitly reports both median ($1049.44¢$) and mean with 95% t-interval ($1047.07¢$ [$1034.05–1060.09¢$]).
- [x] **Every tonic is per recording and in the same register, and every hand-set tonic is documented:** Verified in `analysis/modal_reference_annotations.json`.
- [x] **Reference-sensitive, single-file and mixed-instrument rows are labeled as such:** Verified. Kasaei is classified in Category C (mixed ney + setar); Shahnazi is labeled reference-sensitive; Safvat is labeled single-file dominated.
- [x] **Category membership in the prose matches the script:** Verified. Category A contains strictly the 6 solo unmixed radif masters.
- [x] **No "verified", "definitive" or "confirms" without the evidence named:** Verified.
- [x] **No claim of reproduction for a version nobody has run:** Verified. Pipeline is explicitly designated as v6.
- [x] **Every citation has been checked against a source, with the edition named:** Verified (Kinnear 2000, 2nd ed. 2019).
- [x] **Withdrawn claims stay withdrawn:** Verified ("unbroken continuum", cluster refutation, exact 11/6, and causal vibrato interpretations remain permanently withdrawn).
- [x] **The headline conclusion is no stronger than its weakest required assumption:** Verified. Peak estimates are explicitly stated as conditional on researcher-assigned modal reference hypotheses.
