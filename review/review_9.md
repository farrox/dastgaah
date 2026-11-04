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
