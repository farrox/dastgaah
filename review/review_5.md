# Critical Review Round 4: Response to "Author Response to Review Round 3"

**Document reviewed:** `review/response_4.md`, Part 2 ("Author Response to Review Round 3").
**Reviewed:** 2026-11-04.

**How this round was checked.** Every interval and ratio was recomputed with cents = 1200 · log₂(ratio). I also copied `analysis/build_audited_performer_table.py`, the 60 `.npz` strike files it reads and `shur_consensus.json` into a separate sandbox and ran the script there. That run reproduced `re_koron_performer_audit_sample.csv` **byte for byte** and matched every number in `audited_re_koron_performer_summary.json`. I then ran a modified copy that keeps every event from 60¢ to 240¢, so I could see what lies just outside the script's window. No file in the project was modified.

---

## Summary

This round is a real step forward. The table is now computed from the event files, the CSV exists, the result reproduces exactly, and nearly every theory correction from Round 3 has been applied correctly. The new equivalence test is honest: it reports that equivalence fails.

The main problem has moved, though. It used to be in the bookkeeping. Now it is in **how a strike gets counted as Re-koron.** The script treats as Re-koron any note that falls 120–175¢ above the most frequent pitch in a file. It doesn't check the note's modal role, and it doesn't check whether there is actually a peak in that window. When I look past the window edges, about half the performers show **no distinct peak between 120 and 175¢**. For them, the window cuts into the sides of neighboring peaks, most often a large peak near 200¢. Their medians then depend on where the window edges are, not on how they played. That undermines three of the new conclusions:

1. **The "+8.8¢ modern drift"** ranges from **+4.0¢ to +14.4¢** when the window edges are moved by 5–20¢. Among performers with a clear peak in the window, only two remain in Epoch 1 and two in Epoch 3, which is too few for any test.
2. **"Clusters tightly at 134–148¢"** doesn't hold. Epoch 1's event-level spread (SD 15.3¢, IQR 25.2¢) is almost the spread of a flat distribution over the window (SD 15.9¢, IQR 27.5¢).
3. **The fretted vs. fretless comparison (Δ = 1.2¢)** mixes in ensemble and duet recordings, so it isn't a clean instrument comparison.

I also need to correct two things I said in Round 3 (§2 below).

| Item | Disposition |
|---|---|
| Script, CSV and summary JSON | **Confirmed.** Reproduces exactly |
| Pooled, epoch and instrument statistics | **Arithmetic correct** for the events selected |
| TOST arithmetic (SE 2.61, CI [3.75, 13.90], t = 5.29 and 1.46, df = 6) | **Correct.** One-sided p = 0.0009 and 0.097 |
| "+8.8¢ drift toward 24-TET, from Vaziri's influence" | **Not supported.** Depends on window placement, and the cause is asserted without evidence |
| "Re-koron clusters tightly at 134–148¢" | **Contradicted** by the response's own quantiles |
| Fretted ≈ fretless (Δ 1.2¢) | **Partly supported.** Confounded by mixed recordings |
| Tonic-offset concession | **Accepted**, with my own correction (§2) |
| Shahnazi fix | **Partly supported.** The 125¢ edge is used for one performer only |
| Kasaei ney octave stretch | **Requires data.** The source mixes ney and setār |
| Segāh dual-frame table | **Mostly correct.** Shahkhatāyī's ratio label is wrong, and Zīr-e Īst's "empirical" value is from Navā |
| La-koron and seventh corrections | **Correct** |
| Fret displacement 4.1 mm | **Minor error.** It is 3.8 mm at that fret position |
| Wow/flutter | **Correct as far as it goes**, but the Re-koron table doesn't use the dual-peak tracker |
| Matrix numbers | **Requires a source.** The claimed matrix suffixes equal the digital track numbers |

---

## 1. What checks out

- **Reproducibility.** The script runs cleanly on copies of the event files and writes exactly the published CSV (3,255 rows) and summary JSON. This resolves the main Round 3 request.
- **Pooled statistics** (Q1 133.93, median 143.98, Q3 154.56, IQR 20.63, mean 144.75, SD 13.29), the epoch breakdowns and the instrument breakdowns all match the CSV. 1,776 + 1,415 + 64 = 3,255. 1,776 + 1,415 = 3,191.
- **TOST.** Performer medians {142.49, 136.37, 140.09, 146.01, 136.56} have mean 140.30 and SD 4.09. Medians {150.16, 146.57, 150.65} have mean 149.13 and SD 2.23. Pooled SD = 3.58, SE = 2.61, 90% CI = [3.75, 13.90], t = 5.290 and 1.463. With df = 6, the one-sided p-values are 0.0009 and **0.097**. All correct.
- **Theory corrections, all correct:** 143/162 = −215.98¢; 11/9 = 347.41¢; 88/81 = 143.50¢; 6/5 = 315.64¢; 7/6 = 266.87¢; 8/5 = 813.69¢; 11/6 = 1049.36¢, the inversion of 12/11 = 150.64¢; 44/27 = 845.45¢; 18/11 = 852.59¢; 27/11 = 1554.55¢. The frequencies are now right too: 321.1 Hz and 428.1 Hz.
- **The 1.30 Hz gate calculation** (8.8 ms window) is correct, and 78 rpm ÷ 60 = 1.30 Hz.
- **Lotfi's solo Shūr file** (a peak near 81¢, nothing between 130 and 170¢) is correctly dropped as not a Re-koron source.

---

## 2. Corrections to my Round 3 review

**My "normalized" Re-koron values were window-truncated.** In Round 3, I subtracted each source's tonic from its `neutral_2nd_koron` median in `shur_consensus.json`. But that slot's window (95–180¢, line 38 of `shur_consensus.py`) appears to have been applied *before* removing the tonic offset. In each performer's own frame, the window is therefore shifted down by the offset. For Alizadeh it runs about 75–160¢, which cuts off his peak near 155¢. That is why Round 3 gave 142.7¢ for Alizadeh, while the new script gives 150.7¢ and his density peak is at about 154.5¢. Foroutan (147.5 → 150.1) and Karimi (139.8 → 142.7) were understated in the same way. The tonic-offset point itself stands, because every octave lands within 1.4¢ of 1200¢ once the offset is removed. But the specific Round 3 values that `response_4.md` adopts in §1.2 and §3 should be replaced by the script's values.

**The within-performer instrument contrast I highlighted is not robust.** In Round 3 I called Saba (violin 132.4 vs setār 155.1¢) and Lotfi (kamāncheh 136.8 vs tār 156.3¢) the cleanest fret test in the corpus. With different files and the new tonic method, the contrast shrinks for Saba (135.5 vs 140.7¢) and **reverses** for Lotfi (kamāncheh 150.5 vs tār 137.7¢). The same performer on the same instrument moves 13.7¢ (Lotfi's kamāncheh, 136.8 → 150.5¢) just from file selection and the tonic method. That size of change exceeds the claimed epoch drift. Please drop my Round 3 framing of this contrast as a strong result.

---

## 3. The selection window, not the performers, drives several medians

### 3.1 How the script defines Re-koron

For non-Shūr-consensus sources (`extract_generic_npz_events`, `extract_qajar_tar_events`):

1. The tonic is the **most-populated 10¢ bin of all notes in the file**, refined to within ±40–45¢.
2. Every note in any octave that lands 120–175¢ above that pitch counts as Re-koron.

Problems with this:

- **The most frequent pitch is often not the Shūr finalis.** In Abu'atā, Hejāz, Dashti and Rāk tracks, and in a mixed suite like *Mokhammas*, the most-sung or most-played pitch is usually the āvāz's focal note (shāhed), not the Shūr finalis. A note 120–175¢ above it need not be Re-koron at all. Rāk, in particular, is usually classed as a gusheh of Māhur, which has no Re-koron in the Shūr sense.
- **No check for a peak.** A window always returns events, even if it only cuts into the side of a neighboring peak.
- **The window is asymmetric around 13/12.** 120–175¢ extends 18.6¢ below 138.57¢ but 36.4¢ above it. Any event spread that isn't a sharp peak (and any spillover from the side of a ~200¢ peak) pulls the median toward the window's center at 147.5¢.

### 3.2 What lies just outside the window

Counts per 10¢ bin, using the script's own tonic, gates and files, but keeping events from 80 to 220¢. **The script's window covers the bins from 120–130 to 170–180 (the window ends at 175¢).**

| Performer | 80 | 90 | 100 | 110 | **120** | **130** | **140** | **150** | **160** | **170** | 180 | 190 | 200 | 210 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Saba (violin) | 0 | 0 | 0 | 5 | **25** | **43** | **13** | **6** | **7** | **0** | 1 | 0 | 0 | 2 |
| Foroutan | 3 | 8 | 8 | 4 | **1** | **19** | **50** | **57** | **15** | **1** | 0 | 0 | 0 | 1 |
| Nariman | 0 | 0 | 3 | 10 | **70** | **282** | **272** | **120** | **72** | **18** | 22 | 162 | 154 | 58 |
| Darvish Khan | 20 | 22 | 27 | 15 | **28** | **21** | **11** | **11** | **17** | **17** | 19 | 23 | 18 | 10 |
| Taherzadeh | 36 | 23 | 11 | 2 | **3** | **6** | **2** | **0** | **3** | **3** | 9 | 40 | 27 | 12 |
| Saba (setār) | 9 | 10 | 7 | 18 | **20** | **13** | **12** | **8** | **8** | **16** | 86 | 201 | 180 | 121 |
| Lotfi (kamāncheh) | 2 | 8 | 8 | 18 | **13** | **15** | **19** | **16** | **13** | **62** | 219 | 199 | 138 | 76 |
| Tabatabaei | 1 | 0 | 2 | 0 | **1** | **0** | **3** | **4** | **15** | **14** | 48 | 58 | 108 | 80 |
| Sharifi & Naqsh | 5 | 3 | 6 | 8 | **14** | **37** | **47** | **53** | **30** | **39** | 43 | 97 | 167 | 77 |

The first three rows have a clear peak inside the window. Those medians are meaningful. The next five don't. Darvish Khan is flat across the whole range. Taherzadeh has almost nothing in the window and large peaks near 90¢ and 200¢. Saba's setār, Lotfi's kamāncheh and Tabatabaei sit on the lower side of a large peak at 180–210¢, which is the whole-tone region (Re natural or its equivalent). Sharifi has a modest bump near 150¢ on the side of a larger peak at 200¢. For these performers, the "Re-koron median" mostly reports where the window ends.

A rough screen (a smoothed peak between 125 and 165¢ that is clearly higher than both 100–120¢ and 180–200¢) finds a distinct peak for only **11 of 23** performers. They are Aqa Hoseyn-Qoli, Hasankhan, Saba (violin), Kasaei, Karimi, Nariman, Borumand, Foroutan, Talai, Alizadeh and, more weakly, Safvat and Bahari. Safvat and Bahari have a second peak of similar height near 200¢. The screen is a heuristic, but the histograms above speak for themselves.

### 3.3 Spread close to a flat distribution

A flat distribution over 120–175¢ has SD 15.9¢ and IQR 27.5¢. Compare:

- **Epoch 1 pooled:** SD 15.3¢, IQR 25.2¢.
- **Individual performers at or above the flat SD:** Lotfi's tār (18.9), Taherzadeh (18.2), Hormozi (17.6), Darvish Khan (16.7), Lotfi's kamāncheh (16.4). Darvish Khan, Taherzadeh, Hormozi and Lotfi's tār also have IQRs above 27.5¢.

Spread at or above a flat distribution means the events are not clustered in the window. That contradicts §5's statement that Qajar masters "adhered tightly" to 13/12, and §12's "clusters tightly at 134–148¢". The pooled interquartile range in the response itself runs from 133.9 to 154.6¢.

### 3.4 Moving the window edges

Same events, tonic and files, with only the window edges changed (the same rule for every performer, including Shahnazi):

| Window (¢) | N | Pooled median | Epoch 1 mean of performer medians | Epoch 3 mean | **Epoch 3 − Epoch 1** |
|---|---:|---:|---:|---:|---:|
| 120–175 (as published, but with Shahnazi at 120) | 3,275 | 143.8 | 140.3 | 149.1 | **+8.8** |
| 110–167 (symmetric about 13/12) | 3,346 | 141.3 | 135.3 | 147.6 | **+12.4** |
| 100–180 | 3,870 | 142.3 | 133.9 | 148.3 | **+14.4** |
| 125–160 | 2,602 | 142.4 | 139.8 | 147.8 | **+8.0** |
| 120–160 | 2,804 | 141.2 | 137.3 | 146.6 | **+9.3** |
| 130–175 | 2,778 | 146.9 | 146.5 | 150.5 | **+4.0** |

Individual performers move a lot with the window. Darvish Khan ranges from 131.9 to 152.3¢. Hormozi ranges from 134.5 to 155.4¢. Lotfi's kamāncheh ranges from 139.5 to 155.1¢. Saba's setār ranges from 130.5 to 148.8¢. Performers with a real peak barely move. Foroutan stays within 149.0–150.1¢, Kasaei within 150.8–151.4¢ and Alizadeh within 148.1–152.1¢.

Epoch 3 comes out higher in every window, so the direction is consistent. The size is not: it ranges from 4 to 14¢. Most of the instability comes from Epoch 1, where three of the five performers (Darvish Khan, Taherzadeh, Bagher Khan) don't show a clear peak.

### 3.5 What the equivalence test can and can't say

- Failing TOST means **equivalence was not shown**. It does not by itself show a drift. A direct two-sample t-test on the same numbers gives t = 3.38, df = 6, two-sided p = 0.015. So the response could report a detected difference. But with 5 and 3 performers, and a window sensitivity of about ±5¢, the effect size isn't established.
- With only performers that have a clear peak, the comparison is Epoch 1 = {Aqa Hoseyn-Qoli ≈ 132.5, Hasankhan ≈ 154.5} against Epoch 3 = {Talai ≈ 147.0, Alizadeh ≈ 154.5} (smoothed peak positions). Two against two can't support any test. Moreover, the two Epoch 1 values lie 22¢ apart, on opposite sides of 13/12.
- **Labels:** Epoch 3 includes Sharifi's "historical setup" and Talai, a radif traditionalist. Calling the group "Modern Conservatory performers" doesn't fit them.
- **"The assimilative influence of Vaziri's 24-TET framework"** is a causal claim with no evidence offered. Round 1 asked for this kind of claim to be dropped unless documented. A higher Re-koron in two or three modern tār players is compatible with many explanations.

**Request:** Define Re-koron by modal function rather than by a fixed window. For example, use only tracks or time segments annotated as Darāmad-e Shūr (or the matching Abu'atā segment) with the Shūr finalis annotated as tonic, and locate the second-degree peak with a smoothed density. Report each performer's peak position with a bootstrap interval. Performers or tracks with no distinct peak should be reported as "no peak" rather than as a median.

---

## 4. Attribution: ensemble and duet recordings

| Table row | Files read | Issue |
|---|---|---|
| Lotfi (tār) | `strikes_exp_lotfi_shajarian_*` | Duets with Shajarian's voice. The tracker can't separate tār from voice |
| Hasankhan (santūr) | `strikes_taherzadeh_1906_abuata_santour_*` | Taherzadeh singing with santūr |
| Bahari & Shiraz Ensemble | `strikes_shiraz_festival_abuata.npz` | The script's instrument field says "Kamancheh / Ney / Tar", but the row is classed as **Fretless/Vocal** |
| Sharifi & Naqsh | `strikes_mokhammas_01…12` | All 12 tracks of an ensemble suite, with mode unspecified per track |
| Kasaei | `strikes_shur_kasaei_ney_setar.npz` | Ney and setār together |

Because of these, the fretted-versus-fretless figures (144.7¢ vs 143.5¢) don't compare instruments cleanly. Restrict that comparison to solo recordings, or label the mixed rows separately.

---

## 5. Smaller points on the table and script

- **Shahnazi.** The 125¢ lower edge is applied to Shahnazi only, after the result was seen. With the 120¢ edge used for everyone else, his median is **140.4¢**, not 144.3¢. Use one rule for everyone and report Shahnazi's ~115¢ peak as a separate finding. A strong peak at 110–120¢ in a Shūr radif is itself interesting.
- **Gates.** The table script keeps events with confidence ≥ 38–50, a threshold that **varies by performer**, and plateau wobble ≤ 22¢. In the CSV, **980 of 3,255 events (30.1%)** have confidence below 60, while Round 1 stated the gate as confidence > 0.60. Wobble ≤ 22¢ is a limit on pitch range within the plateau, not the stated 15¢/s slope limit. If the slope, RMS and 80 ms gates were applied when the `.npz` files were made, say where in the code. Otherwise, update the stated method.
- **Dates and epochs.** Shajarian and Lotfi are listed under Epoch 2 with dates of "1970s–1980s", which overlaps Epoch 3's "1980s–Present". Give each track's recording year and assign epochs by that.

---

## 6. Kasaei's octave

The response attributes Kasaei's 1211.4¢ octave to ney acoustics and cites During (1984) and Touma (1996). I couldn't verify these citations or the "jawf/ghayb" register terms. Two practical problems:

- The source is labeled **ney and setār**. A stretched octave on the ney can't be inferred from mixed events. Repeat the octave measurement on ney-only passages.
- If register stretch is real, the octave pairs in other degrees (Fa↓/Fa, Sol↓/Sol) of the same source should show a similar stretch. Check them. Then quote the page in During or Touma that gives the 8–15¢ figure.

---

## 7. Segāh dual-frame table

Most rows are now right, and the dual frame is a clear improvement. Remaining issues:

| Row | Issue |
|---|---|
| **Shahkhatāyī (Si♭)** | (16/9) ÷ (27/22) = **352/243 = 641.54¢**, not 32/27, which is 294.13¢. The cents value is right but the ratio label is wrong. |
| **Shahkhatāyī, measured** | 686.3¢ is **44.8¢** above the Si♭ theory value, and the table doesn't comment. From Īst (686.3 + 6.9 = 693.2¢), it matches **121/81 = 694.82¢** within 1.6¢. That is 11/6 above Do, a **Si-koron**. This may be the source of the ~1049¢ seventh discussed in Rounds 1–3: 694.8 + 354.5 = 1049.4¢. If so, name the note Si-koron here, and cite this as the corpus evidence for the neutral seventh. |
| **Zīr-e Īst, "empirical −218.4¢"** | This value is **Saba's setār Zīr-e Īst in Navā** (`nava_consensus.json`, `saba_setar`). It is not a Segāh measurement. The project's own Segāh values are −141.0¢ (N = 1, `aqa_hoseyn_qoli_segah_scale_degrees.json`) and −147.9¢ (README Segāh consensus). Those fit **Re natural, 12/11 below Mi-koron (−150.6¢)**, not Re-koron (−216.0¢). Either the theory row should be Re, or the measurement should be replaced. |
| **Mūyeh** | Measured 355.8¢ (362.7¢ from Īst) against 11/9 = 347.4¢, a gap of +8.4 to +15.3¢. Worth a sentence, because it is the Segāh "neutral third" question in another form. |
| **Mokhālef** | Measured 850.8¢ (857.7¢ from Īst) against 44/27 = 845.5¢, a gap of +5.3 to +12.3¢. |
| **Īst offset** | The Segāh JSON still has Īst at −6.9¢. Either normalize the "Empirical (System B)" column or state that it isn't normalized. |

---

## 8. Other checks

- **Fret displacement.** 650 × (1 − 2^(−11/1200)) = 4.12 mm is the shift for 11¢ at the **nut**. Between frets at 139¢ and 150¢, the correct shift is 650 × (2^(−139/1200) − 2^(−150/1200)) = **3.80 mm**. The point stands either way.
- **Shafiei.** The response now gives C→D = 210¢ and calls D the "subtonic". D is the second degree above C, not a subtonic. I can't verify 206 vs 210 from here. Quote the table or page so the next reader can check.
- **Wow and flutter.** The <0.15% figure for transfers is undocumented. Even at 0.15%, 1.30 Hz flutter gives peak slopes of 21.2¢/s, above the 15¢/s gate. More importantly, the Re-koron table script doesn't use the dual-peak tracker. It uses one pitch per strike and a per-file tonic. So the robustness case that matters for the table is the single-pitch one, and that hasn't been tested.
- **Matrix numbers.** The script selects Aqa Hoseyn-Qoli's tracks by the digital album's track names, "11 - dastgah-e shur" and "09 - avaz-e kord-e bayat". The response gives their matrices as **7011r and 7009r**, the same digits. That may be coincidence, but it needs a primary source: label scans, or a published Gramophone Company discography with page numbers. The contiguous ranges (10000e–10030e, then 10031e–10080e) need the same.
- **§12 wording.** "Rooted in the classical Zalzalian neutral second": the interval associated with Zalzal is the neutral **third** (wusṭā Zalzal). "Clusters tightly at 134–148¢" conflicts with §3.3 above.

---

## 9. What would resolve this round

1. **Define Re-koron by modal function.** Use annotated Darāmad-e Shūr or Abu'atā segments with the Shūr finalis as tonic, and drop Rāk, Dashti, Navā and Hejāz material from this table.
2. **Use a peak estimator with bootstrap intervals**, and report "no distinct peak" where there isn't one. Publish the 80–220¢ histogram for each performer next to the table.
3. **Use solo recordings for instrument comparisons.** Mark duet and ensemble rows separately.
4. **Apply one window rule to everyone**, Shahnazi included, and show results under at least two other windows.
5. **Drop or support the Vaziri explanation.**
6. **Fix the Segāh rows:** the Shahkhatāyī ratio (352/243), the Shahkhatāyī note name (likely Si-koron), and the source of the Zīr-e Īst value.
7. **Document the gates actually applied**, or update the stated method.

### What the data currently support

> In performers whose Shūr/Abu'atā material shows a distinct second-degree peak, that peak lies between about 132¢ and 155¢. Some peaks sit near 13/12 (Saba's violin, Nariman, Karimi) and some near 150¢ (Foroutan, Kasaei, Alizadeh). This is a genuine spread across performers, not a single tight cluster. Whether it changed over time can't be judged yet: in the Qajar recordings, only two performers show a distinct peak, and those two peaks are 22¢ apart. Segāh's Shahkhatāyī note may be the corpus's evidence for a neutral seventh near 11/6.

The project now has what it needs to answer the Re-koron question properly. A reproducible script and event-level data are the hard part, and they are done. What remains is choosing which events count as Re-koron.
