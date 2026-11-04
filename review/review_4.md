# Critical Review Round 3: Response to "Author Response to Review Round 2"

**Document reviewed:** `review/response_3.md`, Part 4 ("Author Response to Review Round 2").
**Reviewed:** 2026-11-03.

**How this round was checked.** Every interval, ratio and frequency in Part 4 was recomputed with cents = 1200 · log₂(ratio). Unlike earlier rounds, this round also cross-checked the numbers against the files in the project folder, because the response points to them (`analysis/`, `generate_rigorous_audit.py`). The files read were `analysis/shur_consensus.json`, `analysis/lotfi_saba_fretted_vs_fretless_summary.json`, `analysis/aqa_hoseyn_qoli_segah_scale_degrees.json`, `analysis/qajar_kamancheh_degrees_summary.json`, `analysis/segah_consensus.json`, `analysis/historical_masters_interval_summary.json` and `generate_rigorous_audit.py`. No file was modified.

The earlier rounds deliberately accepted the author's measurements as provisionally accurate. That stays the stance here. But several numbers in Part 4 differ from the project's own extraction output, and in those cases the extraction output is treated as the evidence.

---

## Summary

The response resolves the 15,663 / 14,663 question correctly and corrects several theory labels. However, three problems are serious enough that the main Round 2 conclusions cannot stand as written:

1. **The 21-performer table is hand-entered, not computed.** Its values are typed as literals into `generate_rigorous_audit.py` (last modified 13 minutes before `response_3.md`). For most performers, no extraction file in the project contains the listed median, Q1, Q3 or N. The quantile, mixed-model and TOST results have no code in the project, and the promised CSV does not exist.
2. **The "Modern Conservatory High-Koron Lineage" is mostly the tonic-offset artifact flagged in the README review (§1.1).** In `shur_consensus.json`, each source's tonic slot sits 6–20¢ above zero. Alizadeh's 162.8¢, Foroutan's 165.8¢, Borumand's 158.3¢ and Karimi's 146.2¢ are raw values. Measured from each performer's own tonic, they become 142.7¢, 147.5¢, 145.1¢ and 139.8¢.
3. **The pooled quantiles do not follow from the two subgroups or from the table.** Given the stated subgroups, the pooled median would be about 142.5¢, not 139.8¢. Computed from the table itself, the pooled Q3 would be about 146.5¢ and the IQR about 11¢, not 156.4¢ and 21.2¢.

| Item | Disposition |
|---|---|
| 15,663 = all degrees in the Lotfi/Saba sub-study | **Confirmed** from `lotfi_saba_fretted_vs_fretless_summary.json` |
| N = 5,616 | Arithmetic **correct** (sum of the table), but the per-performer N values don't match the extraction files |
| Per-performer IQR and "ratio proximity" columns | Arithmetic **correct** in all 21 rows |
| Bimodal split, 3,842 / 1,774 | **Inconsistent** with the table (944 or 1,254 above 146¢) |
| Pooled Q1 / median / Q3 / IQR | **Inconsistent** with the subgroups and the table |
| High-koron fretted "lineage" | **Largely an artifact** of un-normalized tonic |
| Mixed model and TOST | **Requires data.** No code or output in the project, and the Epoch 1 vs 3 result depends on dropping Alizadeh |
| Shafiei reconciliation | Subtraction **correct**. One of 206 / 210 / 347 is wrong, and Karimi's table value (146.2¢) contradicts the 140.2¢ claim |
| Segāh coordinate systems | **Two wrong ratio labels**, two frequency errors, and a frame that conflicts with the project's own Segāh file |
| La-koron "septimal minor third" | **Wrong.** 315.6¢ is 6/5, and 4/3 × 6/5 = 8/5 (813.7¢) |
| Seventh at 11/6 | Cents **correct**. "Superparticular" and "inversion of 11/9" are **wrong**, and no Shūr source in the project shows it |
| Fret-pressure explanation | **Unsupported** and partly physically impossible as stated |
| Wow/flutter validation | **Inconsistent with the stated stability gate** |
| Provenance | Dates in the table **contradict** Section 8 of the same response |

---

## 1. What checks out

These were recomputed and are correct:

- **15,663.** The four `total_valid_strikes` values in `lotfi_saba_fretted_vs_fretless_summary.json` are 4,204 + 3,114 + 2,668 + 5,677 = **15,663**. The response's explanation is confirmed. The four Re-koron counts in that file (430, 22, 186, 62) and medians (136.8, 156.3, 132.4, 155.1¢) also match the table rows for Lotfi and Saba.
- **5,616** is the sum of the table's N column.
- **IQR column:** Q3 − Q1 matches the listed IQR in all 21 rows.
- **"Acoustic Ratio Proximity" column:** median − 138.57¢ (or − 150¢ where 24-TET is named) matches in all rows.
- **13/8 = 3/2 × 13/12:** 701.96 + 138.57 = **840.53¢**. Correct, and the "13/12 above the fourth" phrase is now gone, as requested.
- **11/6 = 1049.36¢.** Correct.
- **Mi-koron to La-koron:** 852.59 − 354.55 = **498.04¢** = 4/3. Correct.
- **Fa and Sol frequencies:** 261.6 × 4/3 = 348.8 Hz and 261.6 × 3/2 = 392.4 Hz. Correct.
- **Constant speed error cancels exactly** in an interval ratio. Correct, as noted in Round 1.

---

## 2. The 21-performer table is not traceable to extraction output

`generate_rigorous_audit.py` contains the entire table as a hand-typed Python list (`performer_data = [...]`), with each performer's `median_cents`, `q1`, `q3`, `iqr`, `n_strikes` and `tracks` written as literals. The script loads `shur_consensus.json` and `lotfi_saba_fretted_vs_fretless_summary.json` but never reads values from them. It only prints the number of rows and the sum of N.

Comparing the table with the extraction files that exist:

| Performer | Table: median / N | Extraction file: median / N | File |
|---|---|---|---|
| Lotfi (kamāncheh, tār), Saba (violin, setār) | 136.8 / 430, 156.3 / 22, 132.4 / 186, 155.1 / 62 | **Same** | `lotfi_saba_…summary.json` |
| Alizadeh | 162.8 / 380 | 162.77 raw / **337**, SD 20.8 | `shur_consensus.json` |
| Foroutan | 165.8 / 285 | 165.8 raw / **154**, SD 19.0 | `shur_consensus.json` |
| Borumand | 158.3 / 195 | 158.3 raw / **13**, SD 5.0 | `shur_consensus.json` |
| Karimi | 146.2 / 310 | 146.2 raw / **435**, SD 17.5 | `shur_consensus.json` |
| Shahnazi | 134.2 / 412 | 134.2 raw / **271**, SD 21.1 | `shur_consensus.json` |
| Kasaei | **135.3** / 420 | 157.3 raw / **94** | `shur_consensus.json`; the script itself says **157.3** |
| Aqa Hoseyn-Qoli | 141.7 / 348, "Shūr & Segāh" | 141.7 / **16**, and it is **Segāh Zābol (Fa above Mi-koron)**, not a Shūr Re-koron | `aqa_hoseyn_qoli_segah_scale_degrees.json` |
| Bagher Khan | 137.2 / 214, "Shūr & Kord" | The only 137.2 in the Qajar kamāncheh file is **Chahārgāh**, N = 16. That file's Shūr/Hejāz/Kord Re-koron is **143.1¢**, N = 46 | `qajar_kamancheh_degrees_summary.json` |
| Darvish Khan, Hossein Khan, Hasankhan, Taherzadeh, Hormozi, Safvat, Bahari, Sharifi, Talai | various | **No matching value found** in any `analysis/*.json` file | — |

Further points:

- **The IQRs are too small for the source spreads.** For a roughly normal distribution, IQR ≈ 1.35 × SD. Alizadeh's SD of 20.8¢ implies an IQR of about 28¢, not 6.4¢. Foroutan's 19.0¢ implies about 26¢, not 9.1¢.
- **Kasaei changed by about 22¢ between the script and the response** (157.3 → 135.3; Q1 152.0 → 131.0; Q3 162.2 → 141.2). No reason is given. Moving Kasaei from 157.3 to 135.3 also moves him from the high group to the low group, which affects the subgroup split and the equivalence test.
- **No code in the project fits a mixed model or runs a TOST** (searched for TOST, mixedlm, equivalence). The pooled quantiles (135.2 / 139.8 / 156.4) and the subgroup quantiles are not computed anywhere in the project either.
- **`analysis/re_koron_performer_audit_sample.csv` does not exist.**

**Request:** Regenerate the table directly from per-event extraction output (the `.npz` strike files), with a script that reads the events, applies the stated gates, normalizes to each recording's tonic, and computes N, Q1, median, Q3 and IQR. Publish that script with the CSV. Until then, the table cannot be treated as measured data.

---

## 3. The "high-koron" subgroup is mostly the un-normalized tonic

The README review (§1.1) showed that the Shūr consensus is offset by the tonic: the Ist slot sits at +14.5¢ instead of 0. The same holds for **every source** in `shur_consensus.json`. Subtracting each source's own tonic median from its other degrees puts every octave within 1.4¢ of 1200¢ (Kasaei, at 1211.4¢, is the one exception). That confirms the normalization is the right correction.

| Source (shur_consensus.json) | Tonic slot | Re-koron raw | **Re-koron from own tonic** | Octave from own tonic |
|---|---:|---:|---:|---:|
| Alizadeh, tār | +20.1 | 162.8 | **142.7** | 1199.7 |
| Foroutan, setār | +18.3 | 165.8 | **147.5** | 1199.6 |
| Borumand, tār/setār | +13.2 | 158.3 | **145.1** (N = 13) | 1199.9 |
| Karimi, voice | +6.4 | 146.2 | **139.8** | 1200.7 |
| Shekarchi, kamāncheh | +17.2 | 159.4 | **142.2** | 1198.6 |
| Nariman, oud | +10.6 | 152.2 | **141.6** | 1199.4 |
| Saba, violin | +17.5 | 151.7 | **134.2** | 1199.1 |
| Kasaei, ney/setār | +6.2 | 157.3 | **151.1** | 1211.4 |
| Shahnazi, tār | +15.7 | 134.2 | **118.5** | 1199.4 |
| Lotfi, tār/setār | +9.6 | 101.7 | **92.1** (N = 36) | 1199.9 |

What this changes:

- Alizadeh, Foroutan and Borumand, three of the five performers defining the "Modern Conservatory High-Koron Fretted Lineage", fall to 142.7–147.5¢. They sit 4–9¢ above 13/12, not 20–27¢.
- **Karimi measured from his own tonic is 139.8¢.** That agrees with the response's own claim of +140.2¢ for Karimi (Part 2 §3 and Part 4 §4) and contradicts the table's 146.2¢.
- Shahnazi drops to 118.5¢ and Lotfi's Shūr tār to 92.1¢. These are implausible as Re-koron and suggest that slot assignment or tonic detection failed for those sources. They should be inspected, not averaged in.
- The only high values left are Saba's setār (155.1¢, N = 62) and Lotfi's tār (156.3¢, N = 22), both from the Lotfi/Saba file. That is 84 events. It would be worth confirming that file is normalized the same way; its fifths (696–707¢) suggest it is.

**Revised reading:** with normalization, the project's own data point to a single broad Re-koron cluster around 140–148¢. A few fretted setups sit higher. That is not a 31.6% stratum at 158¢. Interestingly, it is closer to the Round 1 claim than the Round 2 response is.

**One genuinely strong comparison deserves to be kept.** Saba (violin 132.4¢ vs setār 155.1¢) and Lotfi (kamāncheh 136.8¢ vs tār 156.3¢) each differ by about 20¢ between instruments within one performer. A within-performer instrument contrast is the cleanest test of fret effects in the corpus, because it holds lineage, era and musician constant. Even so, the fretted sides rest on only 62 and 22 events.

---

## 4. Count reconciliation still fails

- **Epoch totals in the new table:** 1,482 / 3,052 / 1,082. Epoch 1 is **exactly** the Round 1 count (1,482). Part 4 §1A describes the Round 1 counts as pre-filter candidates. If so, the stationary-plateau filter removed 0% of Epoch 1 (shellac) events, 66% of Epoch 2 (8,924 → 3,052) and 75% of Epoch 3 (4,257 → 1,082). Noisy 1906–1912 shellac should lose the most events, not none.
- **Subgroup sizes:** in the table, performers with a median above 150¢ total **944** events (Saba setār, Foroutan, Lotfi tār, Borumand, Alizadeh). Adding Karimi (146.2¢) gives 1,254. Neither is **1,774**. 3,842 + 1,774 = 5,616 is correct, but the split doesn't come from the table.
- **Tracks:** the Track Count column sums to **95**, not the "89 distinct recorded suites" stated. If a suite can span several tracks, say so.

---

## 5. The pooled quantiles are inconsistent with the subgroups

The response gives pooled Q1 / median / Q3 = 135.2 / 139.8 / 156.4¢. It gives the low group (68.4%) as 135.0 / 139.1 / 142.8¢ and the high group (31.6%) as 154.2 / 158.4 / 163.5¢.

**Pooled median.** For the pooled median to be 139.8¢, half of all events must lie at or below 139.8¢. At most 25% of the high group lies below its Q1 (154.2¢), so the high group contributes at most 0.316 × 0.25 = 7.9% of the total below 139.8. The low group must then supply at least 42.1%, which means at least 0.421 / 0.684 = **61.5% of the low group** must lie at or below 139.8¢. But that is only 0.7¢ above the low group's median, so 11.5% of the low group would have to be packed into a 0.7¢ window. With any ordinary shape (two-piece normal fitted to the stated quartiles), the pooled median comes out at about **142.5¢**.

**Pooled Q3.** For 156.4¢ to be the pooled Q3, at most 75% of events can lie at or below it. Fitting the high group's quartiles, about 37% of the high group lies below 156.4¢. That contributes 11.8% of the total. So at most 63.2% of the total can come from the low group, which means at least **7.6% of the low group** must lie above 156.4¢. That is 13.6¢ above the low group's Q3 and past its 1.5 × IQR fence (154.5¢). A normal shape would put about 0.08% there.

**Computed from the table instead.** Simulating each performer as a two-piece normal from their Q1, median, Q3 and N, then pooling, gives approximately **135.4 / 140.0 / 146.5¢ (IQR ≈ 11¢)**. That is far from 21.2¢. The table and the pooled summary cannot both be right.

**Request:** Compute pooled and subgroup quantiles from the event-level data with code, and publish that code with the output.

---

## 6. Contradictions with the Round 1 response

Part 4 §1B says the Round 1 ranges were "ranges of per-performer medians". The new table doesn't support that for two of the three epochs:

| Epoch | Round 1 range | Range of per-performer medians in the new table |
|---|---|---|
| 1 | 137.2–141.7¢ | 137.2–141.7¢ ✓ |
| 2 | 138.0–142.5¢ | **130.0–165.8¢** |
| 3 | 138.2–140.1¢ | **138.2–162.8¢** (no performer is at 140.1¢) |

Other conflicts:

- **Round 1 conclusion 1** said Re-koron "consistently clusters in a tight unimodal distribution between +137.2 and +142.5¢" and that "no statistically significant cluster was observed at +150.0¢". Part 4 now reports a 31.6% subpopulation centered at 158.4¢. Both can't be true of the same data. As §3 shows, the normalized project data actually favor the Round 1 picture more than the Round 2 one.
- **Round 1 IQR of 5.2¢** versus Round 2 IQRs of 7.8¢ (low group) and 21.2¢ (pooled). The 5.2¢ figure is not reconciled.
- **Round 1 conclusion 4** ("vocal lineages disregard conservatory fretboard simplifications") sits awkwardly beside the table, where Karimi's vocal 146.2¢ is the closest non-fretted performer to 150¢. After normalization (139.8¢) the conclusion is fine again, which is one more reason to use normalized values.

---

## 7. Mixed model and equivalence test

There is no code or output for these in the project, so they can only be checked for internal consistency:

- **Epoch 1 vs Epoch 3, all performers:** the Epoch 1 mean of performer medians is 139.5¢. Epoch 3 (Sharifi, Alizadeh, Talai) is 147.0¢. The difference is **+7.5¢**, which is **outside** the ±5¢ margin. The reported −0.84¢ matches only the "revival" subset (Sharifi and Talai, −0.42¢ unweighted), which drops Alizadeh.
- **Circularity:** the subgroups were defined by their Re-koron values (above or below about 150¢). Testing equivalence of Re-koron within the low group is circular, because the selection already ensures similarity. Groups for an equivalence test must be defined before looking at the outcome, for example by instrument type, fret setup measured independently, or lineage documented from sources.
- **p-value:** the CI [−3.12, +1.44] gives a standard error of 1.39¢ (z) and a TOST p of 0.0013 (normal), or about 0.003 with roughly 15 degrees of freedom. The stated 0.0031 is plausible for that. With only 8 performers, artist-level degrees of freedom would be about 6, giving p ≈ 0.006. That doesn't change the conclusion, but report the df.
- **Labels:** Saba's setār (1950s) and Foroutan (1968) are Epoch 2 performers, so "Modern Conservatory" is a misleading name for a group that contains them.

---

## 8. Shafiei (2021)

- 347 − 210 = **137¢**. Correct.
- But Round 2 quoted Shafiei as C→D = **206¢**, D→E-koron = 137¢ and E-koron = 347¢ above C. Since 206 + 137 = 343, not 347, **one of 206, 210 and 347 is misquoted**. Part 4 uses 210. Please check the paper and quote the exact figures.
- The response says its own plateau-extracted Karimi value is +140.2¢, but the table lists Karimi at **146.2¢**. Normalized project data give 139.8¢ (§3). Use the normalized value in the table. Then the Shafiei comparison (137 vs about 140) holds at about 3¢.

---

## 9. Segāh coordinate systems

### 9.1 Arithmetic and ratio errors

| Item in Part 4 §5 | Stated | Correct |
|---|---|---|
| Mi-koron at 27/22 above C₄ = 261.6 Hz | 320.0 Hz | **321.1 Hz** |
| La-koron at 18/11 above C₄ | 427.8 Hz | **428.1 Hz** |
| Re-koron below shahed: "ratio 22/27" | −215.9¢ | 22/27 is **−354.5¢** (that is Do). The ratio for −216.0¢ is (13/12) ÷ (27/22) = **143/162** |
| Fa above shahed: "88/81 ≈ 13/12" | +143.5¢ | 88/81 = 143.5¢ is correct, but it is **4.9¢** from 13/12, so "≈" is loose |
| Sol above shahed: "81/64 ≈ 27/22" | +347.5¢ | (3/2) ÷ (27/22) = **11/9 = 347.4¢**. 81/64 is **407.8¢**. Also, 11/9 is 7.1¢ from 27/22 |

### 9.2 The frame conflicts with the project's own Segāh file

In `aqa_hoseyn_qoli_segah_scale_degrees.json`, Īst is Mi-koron (0¢), **Mūyeh is Sol at +355.8¢** and **Mokhālef is Do at +850.8¢**, both measured from Mi-koron. The README's Segāh table uses the same frame (see the triad review, §1.5).

Part 4's System A instead names **Fa (+498¢ above Do)** as Mūyeh and **La-koron (+852.6¢ above Do)** as Mokhālef's shahed. Those are different notes. In the project's own frame, Mokhālef is Do above Mi-koron, whose theory value is 1200 − 354.55 = **845.5¢ (44/27)**, not 852.6¢.

Note also that the same JSON has Īst itself at **−6.9¢** (N = 107), so it has the same kind of unnormalized offset. Measured from Īst, Zābol becomes 148.6¢, Mūyeh 362.7¢ and Mokhālef 857.7¢.

### 9.3 Zābol is still assigned two identities

- Round 1 response: Hoseyn-Qoli's Zābol 141.7¢ is "Re-koron / Fa".
- Part 4 System B: Re-koron is the "Zābol lower pivot" at **−215.9¢** from the shahed, and Fa is a separate degree at **+143.5¢**.
- Project file: "Zabol (Fa)" = 141.7¢.

So the 141.7¢ value is **Fa above Mi-koron**, whose theory value is **88/81 = 143.5¢, not 13/12**. That also means it is not a Re-koron observation and should not appear in the Re-koron table (§2).

Foroutan's "Zābol = 350¢" is then Sol above Mi-koron (Mūyeh's note), which supports the triad review's suspicion (§1.1) of a copied value. "The shahed of Segāh itself" would be 0¢ in this frame.

**Request:** For every Segāh value, state the frame (from Do or from Īst) and the note, and keep the two frames in separate columns.

---

## 10. La-koron

- **"Septimal minor third" is wrong.** 315.6¢ is the 5-limit minor third **6/5 = 315.64¢**. The septimal minor third, 7/6, is 266.87¢. And 4/3 × 6/5 = **8/5 = 813.69¢**, the just minor sixth. That deserves care: 8/5 is the sixth degree of a just minor scale, so this derivation sits uncomfortably beside the decision to withdraw the "Western minor chords" explanation.
- **The project's data don't show a fretted-versus-fretless split.** Measured from each source's own tonic:

| Source | Type | La-koron |
|---|---|---:|
| Borumand, tār/setār | fretted | 849.9 |
| Lotfi, tār/setār (Shūr) | fretted | 849.0 |
| Saba, setār (Lotfi/Saba file) | fretted | 845.1 |
| Lotfi, tār (Lotfi/Saba file) | fretted | 830.7 |
| Shahnazi, tār | fretted | 801.3 |
| Foroutan, setār | fretted | 798.4 |
| Alizadeh, tār | fretted | 789.1 |
| Saba, violin | fretless | 845.5–851.9 |
| Nariman, oud | fretless | 844.2 |
| Karimi, voice | fretless | 839.5 |
| Lotfi, kamāncheh | fretless | 829.3 |
| Shekarchi, kamāncheh | fretless | 805.1 |
| Kasaei, ney/setār | fretless | 801.6 |

Values near 849¢ appear on frets, and values near 802–805¢ appear on fretless instruments. The data support a wide La-koron range of about 790–852¢ that varies by performer. They don't support a mechanical split by instrument type. The README review's normalized consensus (819.6¢, about 21¢ below 13/8) is the fairer summary.

---

## 11. The seventh at about 1049¢

- **11/6 is not superparticular.** Superparticular ratios have the form (n+1)/n, like 12/11 or 13/12.
- **It is not the inversion of 11/9 or 27/22.** The inversion of 11/9 is 18/11 = 852.6¢, a sixth. The text's own arithmetic, 1200 − 150.6, uses **12/11 = 150.64¢**. So 11/6 is the inversion of the neutral **second** 12/11, as the subtraction shows.
- **Naming.** A note about 1049¢ above Do is a **Si-koron**, not a Si-flat. Si-flat is nominally about 1000¢, and the README's normalized Shūr Razavi is 994.6¢.
- **No Shūr source in the project shows it.** Measured from each source's own tonic, the Shūr seventh is 988.0–1003.5¢ in every source except Foroutan (957.8¢). The Lotfi/Saba file gives 994.4–1002.9¢. If the 1049¢ note comes from Segāh Mokhālef or Dashti Ghamangiz, as Part 4 says, identify the file, the frame and N. In the Segāh frame from Īst, "1049¢ above tonic" would be a different note again.

---

## 12. Fret placement versus sounding pitch

- **Pressure can only raise pitch.** Pressing harder on a fret raises tension and pitch. Light pressure can't make a fret tied at 150¢ sound at 139¢. To sound 11¢ lower, the vibrating length must increase, which means the fret has moved.
- **"Angling the fret toward the nut" is moving the fret.** For scale length L, the fret's distance from the nut is L · (1 − 2^(−c/1200)). Between 139¢ and 150¢ the difference is L × 0.00585. On a 650 mm scale that is about **3.8 mm**. Between 150¢ and 160¢ it is about **3.4 mm**. Both are easily measurable with a ruler.
- **An 8–13¢ rise from pressure alone** on a tied gut fret is large and needs a measurement.

**Request:** Measure the fret positions directly on the instruments, or from video or photographs of the recordings where available. Otherwise state the fret positions as unknown. The sounding pitch is the measurement. The fret position is a separate question.

---

## 13. The wow and flutter validation conflicts with the stability gate

The pipeline keeps only plateaus where pitch changes by less than **15¢/s** for at least **80 ms** (Part 2 §1).

| Simulated condition | Peak pitch deviation | Peak slope | Share of time below 15¢/s | Longest window below 15¢/s |
|---|---:|---:|---:|---:|
| 0.55 Hz, ±1.5% | ±25.8¢ | 89¢/s | 10.8% | about 98 ms, **only at the extremes** (±25.8¢) |
| 1.30 Hz, ±3.0% | ±51.2¢ | 418¢/s | 2.3% | about **8.8 ms** |

- At 1.30 Hz with ±3%, no 80 ms plateau can pass the gate. The pipeline as described would return **no events**, not 139.11¢.
- At 0.55 Hz with ±1.5%, the plateaus that do pass sit at the peaks and troughs of the wow, about ±25.8¢ from the true pitch. Against a 20-second running-KDE tonic, that would give a bimodal error, not +0.25¢.
- The results in the table are only possible with a **simultaneously sounding reference** (the "dual-peak tracker" mentioned in §9). That is a different method from the 20-second KDE tonic in Part 2 §2. Say which method produced the event data, and for which recordings a simultaneous drone actually exists.
- **0.55 Hz is 33⅓ rpm.** That is irrelevant to 1906–1912 shellac at 78 rpm, unless the audio came via LP reissues. If so, say so, because that transfer chain matters.

---

## 14. Provenance

Part 4 contradicts itself:

| Performer | Table (§2) | Section 8 |
|---|---|---|
| Aqa Hoseyn-Qoli | "Paris 1907 / 1909" | Paris 1907, **London** 1909 |
| Taherzadeh | 1906 / 1909 | **1907** Paris / 1909 London |
| Darvish Khan | Paris 1906 / London **1912** | London **1909** (with Taherzadeh) |
| Epoch 1 span | 1906–1914 | — (and `historical_diachronic_evolution.json` says **1906–1920**) |

- The matrix numbers are given as round ranges (7000r–7150r, 10000e–10150e). Give the **matrix and catalog number of each track** actually analyzed. A range doesn't identify a recording.
- The Khaleqi (*Nazari beh Musiqi*, vol. 2, p. 114) and Maroufi (*Radif*, p. 7) citations could not be verified here. Please quote the passages in the original and in translation. A page-7 citation in a radif collection would usually fall in the front matter, so confirm the page.
- *Mokhammas*: the 2012 / 2014 / 2025 breakdown is helpful. The table should use the recording date (2012), not "2012/2025" as in the script.

---

## 15. What would resolve this round

In order of priority:

1. **One script from events to table.** Read the per-event `.npz` files, apply the stated gates, subtract each recording's tonic, assign degrees by mode and frame, and write the per-performer table and the CSV. Commit both. This resolves §2, §4 and §5 at once.
2. **Re-run the Re-koron comparison on normalized values** and drop the non-Re-koron entries (Hoseyn-Qoli's Segāh Zābol, any Chahārgāh values). Expect the "high-koron lineage" to shrink to Saba's setār and Lotfi's tār (§3).
3. **Inspect the outliers:** Shahnazi 118.5¢, Lotfi's Shūr tār 92.1¢, Kasaei's octave at 1211¢. These look like slot-assignment or tonic failures.
4. **Define comparison groups before looking at Re-koron** (instrument, documented lineage, measured fret), and then run the equivalence test with code. Report artist-level degrees of freedom.
5. **Correct the theory labels:** 143/162 (not 22/27), 11/9 (not 81/64), 6/5 and 8/5 (not septimal), 11/6 (not superparticular, and the inversion of 12/11).
6. **Rebuild the wow/flutter validation** with the actual stability gate and the actual tonic method.
7. **Reconcile the dates** in the table with Section 8, and give per-track matrices.

### The conclusion the data currently support

> Measured from each recording's own tonic, Shūr Re-koron in the project's sources clusters broadly at about 134–148¢, near 13/12 (138.6¢) and below 24-TET's 150¢. Two fretted setups (Saba's setār and Lotfi's tār, 84 events in all) sit at about 155¢, roughly 20¢ above the same players on bowed instruments. The evidence doesn't yet establish a separate conservatory stratum, an instrument-type split for La-koron, or a neutral seventh in Shūr.

This is a weaker headline than "invariance", but every part of it can be traced to a file in the project.
