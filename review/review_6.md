# Critical Review Round 5: Response to "Author Response to Review Round 4"

**Document reviewed:** `review/response_5.md`, Part 2 ("Author Response to Review Round 4").
**Reviewed:** 2026-11-04.

**How this round was checked.** Every ratio was recomputed with cents = 1200 · log₂(ratio). I copied `analysis/run_rigorous_modal_audit.py`, the `.npz` files it reads, `shur_consensus.json` and `segah_consensus.json` into a separate sandbox. Running the script there reproduced `re_koron_modal_peak_audit.json` **exactly**. I also read `pitch_dsp.c` to check the stated gates, and I tested how sensitive the peak positions are to tonic estimation. No file in the project was modified.

---

## Summary

The response accepts the Round 4 findings fully and withdraws the right claims: "tight cluster", "+8.8¢ drift" and the Vaziri explanation. Peak-based estimation, bootstrap intervals and a separate category for recordings with no peak are the right direction. The Segāh table is much better.

Four problems remain, and the first two matter most:

1. **The published table doesn't match the script's own output for five performers.** The script marks Darvish Khan, Bagher Khan and Hormozi as having a "Distinct Peak" (at 120.0–121.5¢, the edge of the search range). The table lists all three under "No Distinct Peak". Shahnazi's second peak (143.5¢) doesn't appear in the script output at all. And Hasankhan is moved into the "solo" group, while the script itself labels him "Accompaniment with Vocal". The overrides may well be correct, but they are done by hand and not disclosed.
2. **Kasaei's move into the 13/12 group rests on a tonic estimated from 3 notes.** With the tonic estimated from all octaves (130 notes), his peak is **152.0¢**, not 140.5¢. Shahnazi's peak moves from 128.0¢ to 143.0¢ in the same way. The "two attractors" depend on this choice.
3. **The stated stability gate isn't applied anywhere.** `pitch_dsp.c` computes and stores each strike's drift in ¢/s, but never filters on it. In the Shūr sources, only **7.5–28%** of strikes would pass the stated 15¢/s limit.
4. **The Shahkhatāyī "unambiguous proof of 11/6" is overstated.** The 12-master Segāh consensus puts Shahkhatāyī at 697.6¢ above Īst. That can't distinguish 121/81 (694.8¢) from a pure fifth (702.0¢). Both still put the note near a neutral seventh above Do, so the **qualitative** finding stands on stronger evidence than the response uses.

| Item | Disposition |
|---|---|
| Script and JSON | **Reproduces exactly** |
| Withdrawals (tight cluster, drift, Vaziri) | **Accepted** |
| Peak table vs. script output | **Five rows differ, undisclosed** (§1) |
| Bootstrap "1,000 iterations" | **500** in the code (`n_boot=500`) |
| "Dual attractor" (13/12 vs. 150¢) | **Not supported.** Depends on tonic choice; the largest gap is elsewhere (§2) |
| "Both groups in every era" | **Not supported** for Epoch 1 (§3) |
| Stated DSP gates (15¢/s, ≥80 ms, wobble "range") | **Not implemented as stated** (§4) |
| Segāh table | **Correct ratios.** The empirical column mixes sources (§5) |
| Shahkhatāyī neutral seventh | **Qualitatively supported** by 12 masters, but **not specifically 11/6** (§5) |
| Fret geometry 3.80 mm | **Correct** (one intermediate value is off) |
| Matrix numbers | **Properly withdrawn** |

---

## 1. The published table differs from the script output

Running `run_rigorous_modal_audit.py` (output identical to the committed JSON):

| Performer | Script output | Table in response_5 |
|---|---|---|
| Darvish Khan | **Distinct Peak, 120.5¢ [120.0–158.5]** | "Flat Distribution / No Distinct Peak" |
| Bagher Khan | **Distinct Peak, 120.0¢ [120.0–150.0]** | "Sparse (N=13) / No Distinct Peak" |
| Saeed Hormozi | **Distinct Peak, 121.5¢ [120.0–170.0]** | "Wide Spread / No Distinct Peak" |
| Ali-Akbar Shahnazi | Distinct Peak, 128.0¢ [125.5–130.5] | "Distinct (Bimodal) 128.0¢ / **143.5¢**". The script never reports a second peak |
| Hasankhan | Recording type **"Accompaniment with Vocal"** | "**Santūr Solo**", listed in Category A ("Solo / canonical") |
| Kasaei | Recording type "Solo **Ney & Setar**" | "Solo **Ney**" |
| Talai | Recording type "Solo / Accompaniment" | "Solo Tār" |

The first three overrides look correct to me. A density "peak" at 120.0–121.5¢ is the edge of the 120–175¢ search range, where the side of a lower peak enters the range. It is not a Re-koron peak. But that should be a rule in the code, not a manual edit. For example, reject any maximum within 3¢ of the range edges, and check that it is higher than the density just outside the range. The overrides should also be listed in the text. The Hasankhan relabel matters more: it puts a voice-plus-santūr recording among the solo instruments.

The detector itself is weaker than described. "Not merely a minor shoulder on an overwhelming whole-tone peak" is implemented as `peak ≥ 0.28 × (whole-tone peak)`. A peak at 28% of the neighboring peak's height is still a shoulder. The left-side test (`≥ 22%` above the *minimum* of 85–115¢) passes almost anything with no strong half-step peak.

**Also:** `bootstrap_peak_ci` is called with its default `n_boot=500`, not 1,000. And Borumand (N = 13) gets no interval, because the bootstrap needs N ≥ 15. Say so in the table rather than leaving the interval blank.

**Request:** Publish the table exactly as the script prints it, with the edge rule coded and any manual overrides listed with reasons.

---

## 2. The two "attractors" depend on how the tonic is estimated

For sources taken from `shur_consensus.json`, the script now refines the tonic. It takes the median of the strikes within ±45¢ of the stored tonic, **in that one octave only** (no folding). How many strikes that uses varies a lot:

| Source | Same-octave refinement (script) | All-octave refinement | Script peak | **Peak with all-octave tonic** |
|---|---|---|---:|---:|
| Kasaei | **+11.44¢ from n = 3** | −0.00¢ from n = 130 | 140.5 | **152.0** |
| Shahnazi | −12.50¢ from n = 246 | +0.57¢ from n = 811 | 128.0 | **143.0** |
| Saba (violin) | +4.43¢ from n = 51 | +1.85¢ from n = 428 | 129.0 | 131.5 |
| Karimi | +0.25¢ from n = 217 | +1.00¢ from n = 575 | 138.5 | 138.0 |
| Foroutan | +1.83¢ from n = 680 | +1.83¢ from n = 680 | 149.0 | 149.0 |
| Nariman | +0.72¢ from n = 2,340 | +0.73¢ from n = 2,343 | 138.5 | 138.5 |
| Alizadeh | +1.75¢ from n = 621 | +1.14¢ from n = 808 | 153.0 | 153.5 |

- **Kasaei's tonic rests on 3 strikes.** His other 127 tonic strikes are an octave lower. This is the same octave issue as his 1211¢ octave in Round 3. The choice of octave moves his peak by 11.5¢, from Group 2 to Group 1.
- **Shahnazi's two octaves disagree about the tonic by 13¢.** That is the likely source of his "bimodal" appearance, so his second "peak" may be a tonic artifact rather than two intonations.
- The sources with plenty of tonic strikes in one octave (Foroutan, Nariman, Alizadeh) barely move. So the method is fine when the data support it.

**What this does to the grouping.** Using the response's own peak values, sorted: 129.0, 129.5, 138.5, 138.5, 138.5, 140.5, 145.0, 145.5, 147.5, 149.0, 153.0¢. The largest gap is **9.0¢, between 129.5 and 138.5**. The gap between the two proposed attractors (140.5 → 145.0) is only 4.5¢. With Kasaei at 152.0¢ and Shahnazi at 143.0¢, the values from 138.5¢ upward form an even more continuous run. The data show a **continuum from about 129¢ to 153¢**, with Saba (violin) and Safvat lowest. They don't show two groups centered on 13/12 and 150¢. The response's own section title, "continuum", fits better than "dual attractor".

"Within ±2.0¢ of 13/12" also only fits Nariman, Karimi, Aqa Hoseyn-Qoli and (with the script's tonic) Kasaei. Saba and Safvat are 9.1–9.6¢ below 13/12. Karimi's interval runs 132.5–148.0¢, and Aqa Hoseyn-Qoli's runs 131.0–157.0¢. Those intervals are too wide to place either one in a group.

**Request:** Estimate each recording's tonic from all octaves, using strikes folded to one octave. Report the number of tonic strikes, and flag any source where fewer than about 30 strikes define the tonic. Rerun the peak table, and describe the result as a continuum unless a gap actually appears.

---

## 3. "Both groups appear in every era"

- **Epoch 1:** only Aqa Hoseyn-Qoli (138.5¢, interval 131.0–157.0) and Hasankhan (145.5¢, interval 134.0–156.5) have peaks. **Both intervals cover both proposed groups.** And Hasankhan is a voice-plus-santūr recording (§1). Epoch 1 can't be assigned to either group, so it can't support "both expressions appear in early Qajar recordings".
- **Epoch 3:** only Talai (147.5¢) and Alizadeh (153.0¢) have peaks, and both are in the upper range.

What the data support is narrower: **with two usable performers per end epoch, change over time can be neither shown nor ruled out.** That is a fair summary, and it is close to what §3.3 of the response says. Conclusion 4 in §6 goes further than §3.3 does.

---

## 4. The stated DSP gates aren't the ones implemented

Section 5.2 states that `pitch_dsp.c` enforces `|df/dt| ≤ 15¢/s` and a plateau of at least 80 ms, and that the Python scripts cap "plateau wobble range" at 22¢. Reading `pitch_dsp.c`:

- **Drift:** `drift_c_per_s` is computed (line 628) and written to the output (line 722), but **no gate uses it**. The only gate is line 715, `if (wobble_plat_c > max_wobble_plat_c || conf < min_conf) continue;`.
- **Plateau length:** fixed at **140 ms** (`plat_len = (int)(0.14 * sr)`, line 581). There is no 80 ms minimum. The 0.080 s constants mark where the sustain region and the plateau search begin.
- **Wobble** is a **scaled median absolute deviation** (`1.4826 × MAD`, `mad_cents_arr`), not a range.
- **RMS > −38 dBFS** (from Round 1): no such gate found. The plateau search skips segments below 18% of the strike's peak envelope (line ~643), which is a relative test, not an absolute level.

Because the `.npz` files store `drift_c_per_s`, the stated gate can be applied after the fact. Share of strikes (confidence ≥ 40, wobble ≤ 22) with |drift| ≤ 15¢/s:

| Source | Share passing |
|---|---:|
| Karimi | **7.5%** |
| Saba (violin) | 16.5% |
| Foroutan | 22.0% |
| Shahnazi | 23.9% |
| Kasaei | 24.3% |
| Borumand | 24.4% |
| Alizadeh | 24.6% |
| Nariman | 28.1% |

With the gate applied, most Re-koron peaks stay within about 1.5¢. Karimi's moves from 138.5¢ to **145.0¢**, but on only 25 strikes.

**Request:** Either apply the stated gates in code, or update the methods text to describe the gates that are actually applied: confidence ≥ 40 (on a 0–100 composite score, not the 0.60 stated in Round 1), wobble (1.4826 × MAD) ≤ 22¢, and a fixed 140 ms plateau. Show the main table both ways.

---

## 5. Segāh

### 5.1 The table's ratios are now right

Checked: (9/8) ÷ (27/22) = 11/12 = −150.64¢; 88/81 = 143.50¢; 11/9 = 347.41¢; 4/3 = 498.04¢; 121/81 = 694.82¢; 44/27 = 845.45¢; 27/11 = 1554.55¢. 686.3 + 6.9 = 693.2¢, and 693.2 + 354.55 = 1047.75¢. All correct.

### 5.2 The empirical column mixes sources

The "Empirical (from Īst)" column uses **one performer** (Aqa Hoseyn-Qoli, with Īst re-zeroed by +6.9¢) for every row except Zīr-e Īst, which uses the **12-master consensus** (−147.9¢). The project's `segah_consensus.json` has a 12-master consensus for every row, with Īst already near zero (−0.51¢):

| Degree | Theory (from Īst) | 12-master consensus | Δ | Aqa Hoseyn-Qoli (re-zeroed) | Δ |
|---|---:|---:|---:|---:|---:|
| Zīr-e Īst (Re) | −150.64 (11/12) | −147.89 | +2.8 | −134.1 (N = 1) | +16.5 |
| Zābol (Fa) | +143.50 (88/81) | +141.50 | −2.0 | +148.6 | +5.1 |
| Mūyeh (Sol) | +347.41 (11/9) | +352.17 | +4.8 | +362.7 | +15.3 |
| Hesār (La-koron) | +498.04 (4/3) | +493.47 | −4.6 | +496.9 | −1.1 |
| Shahkhatāyī | +694.82 (121/81) | +697.62 | +2.8 | +693.2 | −1.6 |
| Mokhālef (Do) | +845.45 (44/27) | +850.42 | +5.0 | +857.7 | +12.2 |

The consensus fits the theory within 5¢ on every row. The single performer misses by up to 15¢. Use the consensus column (and show per-master spread), or use Aqa Hoseyn-Qoli throughout, but don't mix them.

The `segah_consensus.json` file's own theory fields are still the old ones: Zābol "154.8 / 13/12", Zīr-e Īst "12/13", Mokhālef "850.0". Update them to match the corrected table.

### 5.3 Shahkhatāyī: neutral seventh yes, "unambiguous 11/6" no

- Per-master Shahkhatāyī, measured from each master's own Īst (12 masters in `segah_consensus.json`): **median 700.5¢, mean 698.6¢, SD 17.9¢, SE 5.2¢**, range 670–732¢. A 95% interval for the mean is roughly **687–710¢**. That covers both **121/81 = 694.8¢** and **3/2 = 702.0¢**, which are only 7.1¢ apart. The consensus file itself labels this degree 3/2.
- Either way, adding Mi-koron (about 354.5¢ above Do) puts the note at about **1049–1057¢ above Do**. That is a neutral seventh (Si-koron), 53–60¢ above a Pythagorean Si-flat (996.1¢). So the **qualitative** conclusion holds, and it rests on 12 masters, not on Aqa Hoseyn-Qoli's 24 strikes. That is a stronger basis than the one the response uses.
- Note that "above Do" is inferred by assuming Mi-koron = 27/22. The measurement is relative to Īst. To claim a specific value above Do, measure Do in the same recordings.

**Suggested wording:** "In Segāh, Shahkhatāyī lies about a fifth above Īst (12-master median 700.5¢, IQR to be reported), placing it near a neutral seventh above Do (about 1050¢), not at the Pythagorean minor seventh (996¢). The data do not distinguish 121/81 from 3/2 above Īst."

---

## 6. Smaller points

- **Fret geometry.** The result, 3.80 mm, is correct. But the intermediate 2^(−139/1200) is **0.922848**, not 0.922756. With 0.922756 the product would be 3.74 mm.
- **Matrix numbers.** Withdrawing 7011r and 7009r and limiting claims to the digital transfers is the right call. On the source: I believe Kinnear's published title is *The Gramophone Company's Persian Recordings, 1906 to 1934* (Bajakhana, 2000), not "*The Persian Gramophone Company Recordings 1906–1912*". Please check the exact title. The engineer attributions (Hampe, Dillnutt) need the same source.
- **"Al-Fārābī introduced the neutral second (13/12)."** This is still a historical attribution of a specific ratio without a citation. Give the text and passage, or say "commonly associated with". (`docs/` contains Ṣafī al-Dīn's *al-Risāla al-Sharafiyya*, not al-Fārābī.)
- **Excluded files.** Compared with Round 4, the script now leaves out Saba's Navā file, Lotfi's kamāncheh "solo" file, the Lotfi–Shajarian "zarbi Hejāz" file, two Safvat files (Razavi Utah, Solo) and Hormozi's Homāyūn file. Dropping Navā and Homāyūn makes sense modally. Give the reason for each exclusion in a comment.
- **Modal function.** Round 4 asked for Re-koron to be defined from annotated Darāmad segments with the Shūr finalis as tonic. The response uses peak detection on whole files instead. That's an improvement, but files with Abu'atā, Hejāz or Dashti material can still have a most-frequent pitch that isn't the Shūr finalis. Segment annotation is still the definitive fix.

---

## 7. What would resolve this round

1. **Make the table equal the script output.** Code the edge rule, list any manual overrides, and fix the recording types (Hasankhan is accompanied).
2. **Estimate the tonic from all octaves**, report the number of tonic strikes per source, and rerun. Expect Kasaei near 152¢ and Shahnazi near 143¢.
3. **Describe the result as a continuum (about 129–153¢)** unless a real gap appears after step 2.
4. **Apply the stated gates in code, or rewrite the methods** to describe what is applied.
5. **Use the 12-master Segāh consensus** for the empirical column, and restate the Shahkhatāyī finding as "a fifth above Īst, a neutral seventh above Do", without choosing 11/6 over 3/2.
6. Fix `n_boot` (or the text), and update the theory fields in `segah_consensus.json`.

### What the data currently support

> Among Shūr/Abu'atā sources with a clear second-degree peak, the peak ranges continuously from about 129¢ (Saba's violin, Safvat) to about 153¢ (Alizadeh). Several sources sit near 13/12 (Nariman, Karimi) and several near 150¢ (Foroutan, Alizadeh, and Kasaei once his tonic is estimated from both octaves). Too few early recordings have a clear peak to say whether this changed over time. In Segāh, twelve masters place Shahkhatāyī about a fifth above Īst, a neutral seventh above Do, not a Pythagorean minor seventh.

The analysis is now close to supporting a clear, honest headline. What remains is mostly making the code, the table and the methods text describe the same procedure.
