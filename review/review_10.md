# Critical Review Round 9: Response to "Comprehensive Author Response to Review 9" (v6)

**Document reviewed:** `review/response_9.md`, Part 2.
**Reviewed:** 2026-11-04.

**How this round was checked.** I copied the three generator scripts (`run_rigorous_modal_audit.py` = `run_rigorous_modal_audit_v6.py`, `compute_segah_consensus.py`, `generate_dsp_drift_sensitivity.py`), all Shūr and Segāh `.npz` inputs, and the six output JSONs into a sandbox. I ran every generator there. **All six outputs reproduce exactly**, and all six output hashes and three spot-checked input hashes match the manifest. I then recomputed the Darvish Khan row, the Īst counts and the window-sensitivity test independently. No project file was modified.

---

## Summary

This is the best round so far. Every output now has a generator, every table in the response matches its JSON, and most of the Round 8 requests are implemented correctly:

- concert-pitch offsets computed in code
- the CI gate applied per file (Sharifi now 37)
- the drift table computed from the strike files (it matches my figures)
- id-keyed exceptions replaced by general rules (Kasaei → Category C)
- missing files raise an error
- the dominant file is named
- per-master Īst normalization implemented

Three new problems, all introduced while fixing Round 8 items:

1. **The Darvish Khan filter was "restored" with the wrong apostrophe.** That drops the only Abū'atā track. The row is still labeled "Āvāz-e Abū'atā" but contains no Abū'atā material (§1).
2. **The Segāh fix overcorrects.** Unfolding `ist_tonic` removed 663 Īst strikes, but only 393 were double counts. The other **270 are genuine Īst strikes in other octaves**, now counted as "outside slot windows". The response's 8,083 figure is not produced by any v6 code (§2).
3. **The window-sensitivity test reports only the median.** Individual masters move by up to **20.6¢** when the windows widen. The text's "virtually zero impact" and "every master ≥ 15¢ above 996¢" don't survive the per-master view (§3).

| Item | Disposition |
|---|---|
| All 6 JSONs | **Reproduce exactly** |
| Manifest | **Output hashes match.** `generate_dsp_drift_sensitivity.py` has changed since (§6) |
| Concert-pitch ledger | **Fixed**, computed in code |
| Per-file CI gate | **Fixed** |
| Kasaei / Borumand rules | **Fixed**, by general rule |
| Darvish Khan filter | **Wrong apostrophe**; the Abū'atā track is excluded (§1) |
| Segāh double count | **Fixed**, but 270 off-octave Īst strikes are now dropped (§2) |
| Inventory figures in prose | **8,083 isn't computed**; v6 gives 7,832 / 7,813 (§2) |
| Per-master normalization | **Implemented correctly**, on the direct-register Īst only (§2) |
| Window sensitivity | **Median-only.** Per-master shifts of −20.6 to +11.5¢ (§3) |
| Drift table | **Counts reproduce.** The filtered and unfiltered peaks use different inputs (§4) |
| Wording | **Three overclaims** have crept back (§5) |
| Listening annotation | **Not attempted.** Still the main gap (§7) |

---

## 1. Darvish Khan: the restored filter misses Abū'atā

v6's filter is `["abu'atâ", "abuata", "hejâz", "hejaz", "kord", "dashti"]`, with an ASCII apostrophe. The track name in the strike file is **`34 - Tasnif–e Abu’atâ`**, with a typographic apostrophe (U+2019), which is what v3 used. "abuata" doesn't match it either. Running v6's own `extract_file_events` with each spelling:

| Filter | Tracks selected | N_ton | N_win | Result |
|---|---|---:|---:|---|
| v6 (ASCII ') | 9: Dashti ×3, Hejāz ×4, Kord-e Bayāt ×2 | 116 | 148 | 121.5¢, boundary artifact |
| v3 (’) | the same 9 + **`34 - Tasnif–e Abu’atâ`** | 144 | 155 | 120.5¢, boundary artifact |

So the v6 row has **no Abū'atā track at all**, while `modal_reference_annotations.json` labels it "Āvāz-e Abū'atā". The response's 148 / 116 / 121.5 are reproducible, but they aren't what the response says they are ("restored").

Two further points. First, the selected tracks span Dashti, Hejāz and Kord-e Bayāt, and the only Abū'atā item is a *tasnif* (a composed song), not āvāz. Second, all of them are still measured against one typed tonic of 370.0 Hz. As in Round 8 §5, each track should get its own tonic.

**Fix:** match on normalized names: fold apostrophes and diacritics before comparing, or list tracks by number. Write the selected track names into the JSON so a reader can see which ones went in.

---

## 2. Segāh: the double count is fixed, but too much was removed

`compute_segah_consensus.py` now matches `ist_tonic` only in its own register (|c| ≤ 35¢), and matches `octave_ist` separately. That ends the double count. But it also drops Īst strikes in **every other octave**, for example the lower Īst at −1200¢, which no slot catches:

| | Folded Īst (old) | Direct Īst (v6) | Removed | Of which were octave double counts | **Genuine off-octave Īst now unassigned** |
|---|---:|---:|---:|---:|---:|
| Corpus | 2,721 | 2,058 | 663 | 393 | **270** |

(One strike differs from the old 2,722 because the v6 histogram tonic is rounded slightly differently.)

The largest effects are Borumand (322 → 174), Payvar (342 → 208), Kasaei (310 → 212) and Lotfi (244 → 163). For Borumand, Īst is now estimated from fewer than half its earlier strikes. Since every normalized degree is `degree − ist`, that changes his whole normalized row.

**Fix:** keep the folded Īst match but exclude strikes already matched as `octave_ist`. Alternatively, fold everything except the upper octave. Either way, every Īst strike is counted exactly once.

**Inventory numbers.** v6 produces two totals:

- **7,832** = strikes inside any slot window (`assigned_indices`), which includes slots that end up below the 8-strike threshold
- **7,813** = sum of `n` over displayed slots, written to `segah_consensus.json` as `total_assigned_no_double_count`

The response's §1.2 and §7.2 also state **"exactly 8,083 strikes fall in the 8 canonical window slots (8,476 − 393)"**. That was my Round 8 arithmetic for the old folded scheme. **No v6 code computes it**, and under v6's slot definitions it isn't true. §7.2 also has the two v6 definitions the wrong way round: 7,832 is the window count, and 7,813 is the thresholded one. Use the two numbers the code produces, each with its definition.

**Per-master normalization.** The new column is computed correctly (`median_i(degree_i − ist_i)`), and the Shahkhatāyī value of 700.38¢ follows from it. It inherits the direct-Īst issue above, so it will move once the fix is in.

---

## 3. Window sensitivity: the median hides large per-master changes

The test widens Shahkhatāyī to ±55¢ and Mokhālef to ±65¢. I reproduced its median, 1049.40¢ (−0.04¢). Per master, using the same code path:

| Master | Base (¢) | Wider windows (¢) | Change |
|---|---:|---:|---:|
| **Saba (violin)** | 1029.1 | 1008.4 | **−20.6** |
| **Kasaei (ney)** | 1031.3 | 1042.9 | **+11.5** |
| **Shahnaz (tar)** | 1036.0 | 1044.5 | **+8.5** |
| Nariman | 1063.2 | 1067.4 | +4.2 |
| Alizadeh | 1054.9 | 1051.9 | −3.1 |
| Payvar | 1011.5 | 1009.1 | −2.3 |
| Karimi | 1081.8 | 1083.7 | +1.9 |
| Others (4) | — | — | ≤ 0.5 |

With wider windows the mean is 1047.2¢, the SD is 22.4¢ (up from 19.4¢), and the 95% CI for the mean is 1032.1–1062.2¢. The minimum is **1008.4¢ (Saba), 12.3¢ above 996.09¢**.

So:

- The **median** (about 1049¢) is robust. That part of the response is right.
- **Individual masters are not.** Three move by 8–21¢. That's exactly what you would expect for masters whose slot medians sit near a window edge, which is what Round 8 flagged.
- "Every master is ≥ 15¢ above 996¢" depends on the window choice. With wider windows, two masters fall below 15¢ (Saba 12.3¢, Payvar 13.0¢). Reword it as "all 11 masters are above 996¢ under both window choices (minimum 12.3¢ above it)", or drop the threshold.
- The JSON's `conclusion` string says "by only 0.05c", while the computed delta is −0.04. That's a hand-typed sentence in a generated file. Generate it from the number, or remove it.

**Fix:** report the per-master wide-window values alongside the base values in `segah_shahkhatayi_pairs.json`, and mark the masters with |Δ| > 5¢ as window-sensitive.

---

## 4. Drift table

The counts and pass rates now reproduce from the strike files: Karimi 384 → 25 (6.5%), instruments 16.5–26.8%. The causal language is gone. Two remaining issues:

- **The two peaks use different inputs.** In `generate_dsp_drift_sensitivity.py`, the **unfiltered** peak is the KDE of all 80–220¢ values, but the **filtered** peak is the KDE of **window values only** (120–175¢). Truncating at the window boundary changes the density near the edges, so part of each "shift" comes from changing the input rather than from the filter. Filter the same 80–220¢ set. (With matched inputs, Shahnazi's filtered peak is 129.0¢, not 129.5¢.)
- **The documented command fails.** `python3 analysis/generate_dsp_drift_sensitivity.py` fails with `ModuleNotFoundError: No module named 'analysis'`. It only runs with `PYTHONPATH=.` or as `python3 -m analysis.generate_dsp_drift_sensitivity`. Put the working command in the manifest.

"Instrumental peaks are drift-invariant" (§8.1) is too strong for four sources, one of which (Saba) keeps only 15 window strikes, exactly the minimum. Say "shift by ≤ 1.5¢ in these four sources".

---

## 5. Wording

`LLM_GUIDE.md` §2 asks for "consistent with" rather than "confirms" or "proves". Three places slipped:

- §1.2: "**proving** robust stability against window boundary truncation". Per §3, this holds only for the median.
- §6: "This **confirms** that boundary truncation has virtually zero impact on the observed consensus neutral seventh."
- §6: "**Proximity to 11/6** … within +0.08¢". The exact-11/6 claim was withdrawn in Round 5, and the guide says to name a ratio only when the interval excludes its neighbours. The CI (1034–1060¢) does not exclude them. Report the median and leave out the ratio.

In §2, every Category C row carries the note "Mixed instrument source (ney + setar / ensemble)", including Hasankhan (santur with voice) and Taherzadeh (voice). That is a fixed string in `build_response_9.py` line 59. Print the actual instrument field instead.

The §10 compliance checklist marks every item "Verified". Because of §1–§3 above, three items don't hold yet:

- "every N says what it counts" fails on the 8,083 figure
- "category membership matches" fails on the Darvish label
- "no 'confirms' without the evidence named" fails on the wording above

A checklist is more useful when it reports what was actually checked than when it ticks every box.

---

## 6. Manifest

All six output hashes match the files on disk. Three spot-checked input `.npz` hashes match. One script hash does not: **`generate_dsp_drift_sensitivity.py` is now `0417f478…`; the manifest says `bca65db4…`**. The file was edited after the response was built, though its output is unchanged. `run_rigorous_modal_audit.py` and `compute_segah_consensus.py` are also newer on disk than their outputs, but their hashes still match. Rebuild the manifest as the last step, after every edit.

---

## 7. What is still missing

None of the Round 6–8 requests for **musical annotation** have been taken up: finalis, passage and target note, time-stamped, by a listener who can't see the cent values. GPT-6 has asked for the same thing in Reviews 7, 8 and 9. The pipeline is now reproducible enough that its remaining uncertainty is mostly about **what** is being measured, not **how**. One more round of code fixes won't change that. A one-page annotation table for the six Category A recordings would.

---

## 8. What would resolve this round

1. **Fix the Darvish Khan filter** (normalize apostrophes), write the selected track names to the JSON, and give each track its own tonic (§1).
2. **Count each Īst strike exactly once** (folded, minus the octave slot). Regenerate, and drop the 8,083 figure in favour of the two v6 definitions (§2).
3. **Report per-master window sensitivity**, mark window-sensitive masters, and reword the "≥ 15¢" claim (§3).
4. **Use the same input set for filtered and unfiltered drift peaks**, and fix the run command (§4).
5. **Remove "proving", "confirms" and the 11/6 proximity line.** Print real instrument labels (§5).
6. **Regenerate the manifest last** (§6).
7. **Do the listening annotation** for the six Category A recordings (§7).

### What the data currently support

> In six selected solo, single-instrument Shūr-family recordings, measured from partly hand-set reference pitches, the second-degree density peak lies between 127.5¢ (Safvat, from one recording) and 153.5¢ (Alizadeh), with values near 128¢, 138.5¢ and 150–154¢. No Epoch 1 source yields a usable peak. In Segāh, the median across 11 masters of (median Shahkhatāyī − median Mokhālef + 1200¢) is about 1049¢, and this median is insensitive to the slot windows. Individual masters' values move by up to 21¢ with the windows, and all stay above the Pythagorean minor seventh (996¢).
