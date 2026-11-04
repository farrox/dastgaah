# Guide for LLMs working on the dastgaah intonation study

This guide is for any model that writes analysis, author responses or reviews in this repository. It comes from eight rounds of review (`review/review_4.md` to `review_8.md`, plus GPT-6's reviews). Almost every error found in those rounds was one of the patterns below. Read the guide before you write anything, and run through the checklist at the end before you hand anything in.

---

## 1. The core rule: every number must trace to a file

Most problems in past responses were not bad measurements. They were numbers in the prose that no file contains, or numbers that look plausible but came from a different method, frame or subset than the text claims.

- **Generate tables from the JSON.** Don't type them. If a table appears in a response, a script should have written it from `analysis/*.json`. Hand-typed tables are how errors got in: the hardcoded Segāh octave row in `build_response_6.py`, and the literal Re-koron table in `generate_rigorous_audit.py`.
- **No prose-only numbers.** If you want to cite a per-file peak, a sensitivity result or a subset statistic, have the script write it to the JSON first. In Round 7, "Abu'atā 169.3¢" appeared only in prose. The script's own code gives 134.5¢.
- **Check the grid.** The KDE grid in `run_rigorous_modal_audit.py` steps by 0.5¢, so every peak it reports ends in .0 or .5. A value like 169.3 or 146.4 cannot have come from that code.
- **Say which N.** "N = 11,438" (all strikes in the sources) and "8,476" (strikes assigned to the eight displayed degrees) are both true, but they measure different things. Name the one you mean. If you explain the gap between them, the explanation must come from code that classifies those strikes, not from what seems likely.
- **Don't say "verbatim" or "generated directly from"** unless that is literally true.

## 2. Never claim more verification than was done

- **Ran it ≠ checked it.** A script that runs and reproduces its own JSON shows the code is deterministic. It does not show that the tonic is the finalis, or that a note is Re-koron.
- **Version matters.** If a reviewer reproduced v3, nobody has reproduced v4. Say which version was run, by whom, on what inputs.
- **Local paths aren't public.** `file:///Users/ed/...` links are not "open source and reproducible" to an outside reader. Say "reproducible from the local repository" until there is a public commit or bundle.
- **Words to avoid** unless you have the evidence: "verified", "authenticated", "definitive", "firmly establishes", "pristine", "unequivocally", "confirms". Use "conditional on the tonic estimates in Table X", "candidate", "descriptive", "consistent with".
- **Don't credit a reviewer with a finding they didn't make.** In Round 6 a response said GPT-6 "discovered" an octave stretch. GPT-6 had listed it as one of four possibilities, and had not endorsed it.

## 3. Cents arithmetic

Cents = 1200 · log₂(ratio). Check every interval you state. These come up often:

| Ratio | Cents | | Ratio | Cents |
|---|---:|---|---|---:|
| 13/12 | 138.57 | | 3/2 | 701.96 |
| 12/11 | 150.64 | | 121/81 | 694.82 |
| 88/81 | 143.50 | | 44/27 | 845.45 |
| 162/149 | 144.82 | | 18/11 | 852.59 |
| 11/9 | 347.41 | | 16/9 | 996.09 |
| 27/22 | 354.55 | | 11/6 | 1049.36 |
| 4/3 | 498.04 | | 2/1 | 1200.00 |

- **Don't add a theoretical interval to a measured one** and present the sum as a measurement. ("354.5 + 698.2 = 1052.7¢" adds a 44/27-derived value to an empirical mean.) Where both degrees are measured, compute the interval within each source instead. For Segāh, Shahkhatāyī − Mokhālef + 1200 per master gives a median of 1049.4¢ (11 masters).
- **Being near a ratio is not the same as being that ratio.** Report the measured value and its interval. Name a ratio only if the interval excludes its neighbours.

## 4. Reference frames and tonics

This is the most important source of error in the study.

- **Normalize to each source's own tonic.** Per-source values in `shur_consensus.json` and `segah_consensus.json` are measured from `ist_hz`, not from each source's measured Īst. Subtract the source's `ist_tonic` median before comparing sources. In Shūr the offset is +6 to +20¢. In Segāh it is −8.7 to +5.7¢.
- **Apply windows after normalizing, not before.** Selecting a 120–175¢ window in the raw frame and then normalizing truncates the distribution.
- **Use one tonic per recording.** Never pool a performer's recordings and then estimate one tonic. Recordings in different keys make one file's dominant pitch look like another file's Re-koron (Round 6: Lotfi kamāncheh, Hasankhan).
- **Use the same register.** Measure each note against the tonic in its own octave, and report how many tonic strikes define it. Kasaei's "octave stretch" was a 3-strike tonic in the wrong register.
- **The most frequent pitch is a candidate tonic, nothing more.** It can be the shāhed, a drone, or a pitch from a transposed passage. Warning signs: few events in the window relative to the file's 80–220¢ total (Lotfi Abu'atā: 20 of 349), or a peak near the edge of the window.
- **Hand-set tonics are annotations, and must be documented.** Ten performers have a typed `default_ist`. Record each one in an annotation file with its reason, its register, who chose it, and when it changed (for example Kasaei, 544.6 → 272.3 Hz). If a typed tonic is never observed in the recording (Borumand, N_tonic = 0), say so plainly.
- **Keep reference sensitivity visible.** If two defensible tonic choices give different peaks (Shahnazi, 128.0 vs 143.5¢), report both until there's a musical reason to prefer one.
- **Use one frame per table.** Don't mix raw and normalized statistics in the same sentence (for example, a normalized median beside a raw mean and SE).

## 5. Peaks, intervals and categories

- **A local maximum is not a modal peak.** The KDE gate counts all values from 80 to 220¢, so a file can be called "distinct" on one event in the window. Label per-file results as "local maximum", "usable peak" or "insufficient", and report N in the window.
- **Know what the bootstrap measures.** It gives precision conditional on the chosen tonic, window and event selection. It doesn't include uncertainty about the tonic or the note's identity. Notes from one recording aren't independent replications: N_window = 825 from one file is one recording.
- **Name the estimand.** A t-interval is for the mean. Don't print it next to a median as "median (95% CI …)".
- **A missing CI is unstable,** not stable by default.
- **Categories must follow the code.** If the script puts Talai in Category C, Talai can't appear in a "Category A continuum". If you disagree with the code, change the code, and say why.
- **Flag single-file dominance.** If one recording supplies most of a performer's events (Safvat Part 1 supplies 174 of 188; Talai's Shūr Darāmad supplies 119 of 129), present it as a finding about that recording.
- **Account for files whose own peak was rejected.** If such a file still adds events to the pooled performer count, say so, or exclude it.

## 6. Interpretation

- **Seven points can't show a continuum.** 127.5, 128, 129, 138.5, 150.5, 152 and 153.5¢ fit a spread and also fit three clusters. Describe them; don't classify the pattern.
- **Absence of data isn't evidence.** No Epoch 1 source passes the stability gate, so no temporal trend can be tested. Don't present "indeterminate" as a finding about history, and note that a strict gate selects for recording quality.
- **One test doesn't identify a cause.** A peak that moves (or doesn't) under a drift filter says the peak depends (or doesn't) on that filter. It doesn't show what MAD controls, or that vibrato is the cause.
- **Keep repertoire straight.** Rāk, Hejāz, Dashti, Kord-e Bayāt and *Mokhammas* movements aren't Shūr Darāmad. Use a canonical analysis restricted to annotated Shūr-family passages, and keep everything else as exploratory.
- **Mixed sources stay mixed.** Ney + setār (Kasaei), and duets and ensembles, aren't single-instrument evidence until the notes are attributed to an instrument.
- **Summary medians aren't paired notes.** A difference of per-master medians from different gūshehs cancels a fixed offset, but not modulation or retuning.

## 7. Citations

- Cite what the source actually says, and through whom. 13/12 for the rubāb: "Ibn Sīnā, as reported by Barkeshli (1976, 74), via Poorhaydari (2023, n. 15)". *Kitāb al-Shifā'* is not cited there. 162:149 for al-Fārābī: "Poorhaydari (2023, n. 5), crediting During", which is a secondary claim.
- Check titles against a catalog record. Kinnear: *The Gramophone Company's Persian Recordings, 1899 to 1934* (Bajakhana, 2000; ISBN 0957735510; revised 2nd edition 2019). Cite the edition actually consulted. Don't take a title from a reviewer's guess, including Claude's: "1906 to 1934" was a reviewer error.
- Keep citations marked unverified (During and Touma on ney stretch, for example) until someone has checked them.

## 8. Working in the repository

- **Run scripts that write into `analysis/` on copies.** `build_audited_performer_table.py` and `run_rigorous_modal_audit.py` overwrite their outputs.
- **Reviewers change only their own review file.**
- **Keep withdrawals withdrawn.** Don't let a retracted claim (two attractors, exact 11/6, octave stretch, "unbroken continuum") come back in a later summary under new wording.
- **Write less narrative.** Reviewers have asked for exports and checkable calculations. A short response with tables generated from the JSON beats a long one that says everything is fixed.

---

## Checklist before handing in

- [ ] Every number in the text is in a JSON or CSV in `analysis/`, or computed in the text from numbers that are.
- [ ] Every table was written by a script, not typed.
- [ ] Every peak value fits the 0.5¢ grid.
- [ ] Every N says what it counts.
- [ ] Every interval has a stated estimand (mean or median) and a frame (raw or normalized).
- [ ] Every tonic is per recording and in the same register, and every hand-set tonic is documented.
- [ ] Reference-sensitive, single-file and mixed-instrument rows are labeled as such.
- [ ] Category membership in the prose matches the script.
- [ ] No "verified", "definitive" or "confirms" without the evidence named.
- [ ] No claim of reproduction for a version nobody has run.
- [ ] Every citation has been checked against a source, with the edition named.
- [ ] Withdrawn claims stay withdrawn.
- [ ] The headline conclusion is no stronger than its weakest required assumption: tonic identity, which is not yet annotated.
