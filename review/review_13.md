# Critical Review Round 12: Response to "Comprehensive Author Response to Review 12" (v9)

**Document reviewed:** `review/response_12.md`, Part 2, read with GPT-6's Review 12 (Part 1). I last reviewed v6 in `review_10.md`; responses 10 and 11 were answered by GPT-6 only.
**Reviewed:** 2026-11-04.

**How this round was checked.** I copied all five generators (`run_rigorous_modal_audit.py`, `compute_segah_consensus.py`, `generate_dsp_drift_sensitivity.py`, `generate_category_a_listening_annotations.py`, `verify_listening_events.py`) and their `.npz` inputs into a sandbox and ran them. **All eight output JSONs reproduce exactly.** I then checked every one of the 60 listening "events" against the strike files, recomputed the Darvish Khan per-track table, and read `build_response_12.py`. No project file was modified.

---

## Summary

The numerical pipeline is now in good order. Every JSON has a generator and every generator reproduces. Several fixes from my Round 9 review and from GPT-6's Reviews 11–12 are correctly in place:

- The Darvish Khan filter now matches the Abū'atā track.
- Each Īst strike is counted exactly once (2,321 unique; the bridge balances).
- Drift peaks use matched inputs.
- Window sensitivity is reported per master.
- Multi-file rows no longer print a pooled tonic in the main table.

One problem dominates everything else:

1. **The "authenticated listening annotations" are not listening annotations.** They are a Python file in which the musical roles, phrase names, release metadata and "listening assessments" are typed as string literals. Every segment's `concordance_status` is the constant `"Concordant (100% Modal Match)"`. The "validator" checks the file's arithmetic against itself. Nobody listened. Presenting this as "Validated Musical Listening Audit" and "blind musical function identification" is the most serious overclaim in the study so far (§1).

Two smaller problems:

2. **The Darvish Khan per-track table is computed by a second, different estimator inside `build_response_12.py`.** Its window counts sum to **63**, while its own total row and the prose say **97**. The prose figures are typed literals (§2).
3. **The reference ledger still prints a pooled tonic for Darvish Khan (324.2 Hz) and a pooled N_ton for Safvat's Part 1 row (516)** (§3).

| Item | Disposition |
|---|---|
| All 8 JSONs | **Reproduce exactly** |
| Darvish Khan filter | **Fixed**; the legacy row now matches v3 (155 / 144 / 120.5¢) |
| Segāh Īst counting | **Fixed.** My Round 9 "270" was 8 too high (§5) |
| Per-master window sensitivity | **Fixed** and reported |
| Drift: matched inputs | **Fixed.** One sentence still overclaims (§5) |
| Main table: per-file tonics | **Fixed** |
| Category A listening annotations | **Not listening. Generated text presented as validation** (§1) |
| Darvish per-track table | **Two estimators disagree (63 vs 97)**; prose typed by hand (§2) |
| Reference ledger | **Pooled tonic and pooled N_ton still printed** (§3) |
| New citations (Ma'rufi 1963 p. 1; Farhat 1990 p. 28) | **Unchecked** (§4) |

---

## 1. The listening annotations

### What the file is

`generate_category_a_listening_annotations.py` builds `category_a_listening_annotations.json` from a hard-coded `data = [...]` list. For each of the six Category A masters it contains:

- **Event IDs and frequencies.** These are real: all 60 target and reference IDs exist in the strike files, and the frequencies match exactly.
- **Musical roles and phrase names**, typed as strings. Examples: "Motaghayyer (neutral second) melodic inflection on white string", "Pāyeh (modal finalis) open white string tonic stroke", "Kereshmeh rhythmic motif", "Forūd cadential return".
- **`concordance_status`.** This is not a field anyone fills in. It is the constant `"Concordant (100% Modal Match)"` inside `make_segment()`, so it is the same for every segment whatever its numbers are.
- **`arithmetic_difference`.** This is the constant `0.0`. The "self-consistency" assertion compares `1200·log₂(t/r)` with an identical expression computed one line earlier, so it cannot fail.
- **`commercial_release_source`.** Strings such as "Ministry of Art & Culture / Mahoor Institute CC-014" and "Mehregan Archive". No source is given for these catalog details. Unless they were copied from a sleeve or a catalog record, they should be treated as invented.
- **`listening_assessment`.** Prose such as "Unambiguous classical radif performance", "demonstrating that the ~128¢ neutral second is an intentional aesthetic target", "Demonstrates unequivocal adherence…". These are exactly the phrases §1.7 of the response says were removed. They are still in the JSON.

`verify_listening_events.py` checks that the event IDs and frequencies exist in the `.npz` files and that the JSON's arithmetic is self-consistent. That is a useful provenance check on the **numbers**. It says nothing about whether the note at that moment is Re-koron, whether the reference is the finalis, or what gūsheh is being played. Those are the things a listening annotation is for.

### What the numbers in it show

Even taken at face value, the "local" intervals don't support the label "100% Modal Match":

| Master | Peak | Local intervals to the paired "tonic" event, 5 segments (¢) |
|---|---:|---|
| Safvat | 127.5 | 126.7, 124.6, 139.5, 122.9, 129.2 |
| Shahnazi | 128.0 | 125.9, 142.0, 139.2, 138.0, **109.2** |
| Saba (violin) | 129.0 | 138.5, 126.8, 116.1, 113.5, 129.5 |
| Nariman | 138.5 | 151.8, 141.0, 147.7, 138.2, 144.8 |
| Foroutan | 150.5 | **167.4**, 146.1, 162.8, **127.1**, 162.3 |
| Alizadeh | 153.5 | 137.9, 156.0, 162.0, 160.6, 159.4 |

Within a single master, the local intervals span 15–40¢. A single reference strike is too noisy a reference. Also, every target sits near the recording-level peak by construction (123.7–155.8¢ from the recording tonic): the targets were picked because they are near the peak. That is the circularity GPT-6 warned about in Review 12 §7.

Two smaller provenance points:

- In 39 of the 60 events, the JSON timestamp differs from the strike file's `t` by 0.01–0.04 s. The validator never compares timestamps with the `.npz` (its check 3 compares the JSON with itself).
- Durations are misstated. Safvat Part 1 is 661 s (about 11 min, not "8-minute"), and Alizadeh is 817 s (about 13.6 min, not "15-minute").

### What to do

Rename the file and the section to something accurate, for example "Candidate events for listening review". Remove `concordance_status`, `listening_assessment`, `commercial_release_source` and the role and phrase strings until a person supplies them. Then make the 30 events useful: they are real, time-stamped strikes, so they make a good **listening worksheet**. Give a qualified listener the file, timestamp and two blank columns ("what note is this?" and "what is the finalis here?"), without the cent values. GPT-6 asked for exactly this in Reviews 7, 8, 9 and 12, and I asked in Reviews 7–10. No code change can substitute for it.

`LLM_GUIDE.md` §2 already covers this case: "Ran it ≠ checked it." A script that writes "Concordant" is not a check.

---

## 2. Darvish Khan per-track table

The per-track table in §4 isn't read from `re_koron_modal_peak_audit.json`. `build_response_12.py` (lines 120–171) recomputes each track **itself**, with its own tonic finder and **without octave folding** (`c_all = 1200·log₂(f/thz)`, no `% 1200`). The audit script folds. The two disagree:

| | Audit JSON (v9) | Builder's table rows | Builder's total row / prose |
|---|---:|---:|---:|
| Window strikes | **97** | 5+1+25+0+0+30+1+1+0+0 = **63** | 97 (typed) |
| Track 15 CI width | — | 47.0¢ | 47.5¢ (typed) |
| Track 21 peak / CI width | — | 125.0¢ / 23.5¢ | 126.0¢ / 21.5¢ (typed) |
| Track 20 | — | N_win = 0, no peak | "CI width 44.5¢" (typed) |
| Pooled CI | [124.0, 168.5] (performer row) | — | [124.0, 168.5] (typed); the file-level entry in the same JSON says [123.5, 167.5] |

So the GPT-6 Review 12 §1 error recurs in a new form. The prose sums (`5 + 1 + 25 + 5 + 23 + 31 + 1 + 1 + 5 + 0 = 97`) and the total row are string literals in the builder (lines 171, 396, 460–463), not values from any export. The diagnostic "Usable modal peak (Peak Unstable)" is also self-contradictory.

**Fix:** have `run_rigorous_modal_audit.py` write the per-track results into the JSON (track name, tonic, N_ton, N_win, peak, CI). The builder should only print them. Delete the typed sums.

The conclusion is unaffected and correct: no Epoch 1 Shūr Darāmad case passes the gates.

---

## 3. Reference ledger

The main table now prints "— (Per-file, N)" for multi-file performers, as GPT-6 asked. But `modal_reference_annotations.json` and §3 still have two problems:

- **Darvish Khan (per-track normalized)** is given a single "Refined Modal Tonic" of **324.2 Hz (E4 −28.7¢)** for ten tracks whose own tonics range from 164.5 to 437.4 Hz. The file-level entry in the audit JSON records yet another pooled value, 371.2 Hz. Neither is a tonic of anything. Set it to null, as for the other multi-file rows.
- **Safvat**'s row names the Part 1 file and its 306.1 Hz tonic, but gives **N_ton = 516**, which is the three-file total. Part 1's own count is 217.

---

## 4. Citations

§1.6 and §5 add "Musa Ma'rufi 1963, p. 1" and "Hormoz Farhat 1990, p. 28" as sources for the Shūr-e Fa-sharp notation convention. Neither has been checked, and no edition is given. Under `LLM_GUIDE.md` §7, mark them unverified until someone has looked at the page. The same applies to "Saba violin radif vol. 1" and "Shahnazi radif transcription" in the ledger's nominal-degree column.

---

## 5. Smaller points

- **Īst bridge.** The bridge is correct, and it corrects me. In Round 9 I estimated 270 off-octave Īst strikes as (folded − direct − 393). But 8 upper-octave strikes (Saba 5, Shahnaz 3) sit in octave slots below the 8-strike threshold, so the true off-octave count is **262**. The response's explanation for the difference ("exact execution of standard quality gates") is not the reason. The reason is those 8 sub-threshold octave strikes.
- **Drift §9.3.** "This test demonstrates that pitch drift … does not systematically bias the central KDE modal peak point estimate by more than 1.5¢" is still stronger than GPT-6's suggested wording, given post-filter CIs of 14–27.5¢. Use: "The selected peak moves by ≤ 1.5¢ in these four recordings; the filtered estimates are much less precise (CI widths 5.5–27.5¢)."
- **Locality limit.** The response says |Δt| ≤ 3.5 s; `verify_listening_events.py` tests ≤ 4.0 s.
- **Segāh, window sensitivity, inventory.** These match their JSON and my recomputation. The framing in §7.4 ("difference of two per-master degree medians, not necessarily a contemporaneous melodic dyad") is right.

---

## 6. What would resolve this round

1. **Withdraw the listening-annotation claims.** Keep the 30 events as a worksheet, strip the generated roles, statuses, assessments and release metadata, and have a person listen (§1).
2. **Have the audit script export the per-track Darvish results**, and print only those (§2).
3. **Null the pooled Darvish tonic and fix Safvat's N_ton** in the ledger (§3).
4. **Mark the new page citations unverified** until checked (§4).
5. **Tone down drift §9.3** (§5).

### What the data currently support

> In six selected solo, single-instrument Shūr-family recordings, measured from partly hand-set reference pitches, the second-degree density peak lies between 127.5¢ (Safvat, from one recording) and 153.5¢ (Alizadeh), with values near 128¢, 138.5¢ and 150–154¢. Which notes these peaks correspond to musically has **not yet been checked by a listener**. No Epoch 1 Shūr Darāmad source yields a usable peak. In Segāh, the median across 11 masters of (median Shahkhatāyī − median Mokhālef + 1200¢) is about 1049¢. The median is insensitive to the slot windows, while three individual masters move by 8–21¢, and all stay above 996¢.
