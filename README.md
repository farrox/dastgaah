# dastgaah

Empirical pitch and scale-degree latch analysis of *Dastgāh-e Māhur* across **13 canonical recordings** (7 Setar, 3 Tar, 1 Oud, 1 Kemancheh, 1 Voice — **287 tracks, 44,848 stationarity- and confidence-gated note strikes**).

## Latch Fingerprint (v3 — 17 Slots Across 13 Sources)

![Mahur v3 latch fingerprint](output.png)

- **5-Page Empirical Pitch & Historical Theory Report:** [`mahur_pitch_analysis.pdf`](mahur_pitch_analysis.pdf) ([`analysis/mahur_pitch_analysis.pdf`](analysis/mahur_pitch_analysis.pdf))
  - *Page 1:* 17-Slot Cross-Instrument Latch Fingerprint & Absolute `Do` Spectrum (`199.7–441.5 Hz`).
  - *Page 2:* Diatonic vs. *Koron* Pair Discrimination (`La/Laᵏ↓`, `Re/Reᵏ`, `Mi/Miᵏ`, `Si/Siᵏ`) & 44,848-Strike Density.
  - *Page 3:* `13 × 17` Register Coverage Matrix, Rescued Track `Do` Trajectories & Modulating *Gushehs*.
  - *Page 4:* Setar Shared-Fret Couplings (`Reᵏ→Laᵏ↓`, `Re→La↓`, `Miᵏ→Si↓`, `Mi→Siᵏ`) & 22-Row Reference Table.
  - *Page 5:* Historical & Modern Theory Comparison — Testing Ṣafī al-Dīn al-Urmawī (*al-Risālah al-Sharafīyah*), ʿAbd al-Qādir al-Marāghī, Al-Fārābī/Zalzal (`13/12`), Vaziri (`24-TET`), and the Shared-Fret Hybrid model (`3.6¢` RMS error across all 16 non-`Do` slots).
- **2-Page Frequency Extraction DSP Audit & Benchmark:** [`frequency_extraction_audit.pdf`](frequency_extraction_audit.pdf) ([`analysis/frequency_extraction_audit.pdf`](analysis/frequency_extraction_audit.pdf))

---

## v3 4-Stage Frequency Extraction Pipeline (`analysis/pitch_dsp.c`)

Replacing the v1/v2 `PitchHPS + FFT(1st/2nd harmonic) + integer-lag AC` extractor with a native C 4-stage pipeline ([`analysis/pitch_dsp.c`](analysis/pitch_dsp.c), orchestrated by [`analysis/extract_upgraded_strikes.py`](analysis/extract_upgraded_strikes.py)) resolved five physical measurement artifacts:

1. **Stage 1 — Pre-Onset Spectral Drone/Decay Subtraction (`[-110 ms, -10 ms]`) & Parabolic YIN (`CMND`):**
   - Applies a soft Wiener spectral mask against the `100 ms` pre-onset window to suppress ringing previous notes (e.g., `Fa → Sol↓` transitions on oud) and continuous open-string *vākhān* drones (`220.8 Hz` `Fa↓` on setar).
   - Replaces integer-lag autocorrelation (`13–17¢` quantization step) with FFT-accelerated Cumulative Mean Normalized Difference (**YIN-CMND**) + parabolic lag interpolation (`< 0.15¢` precision).
2. **Stage 2 — Multi-Harmonic Least-Squares + Phase-Vocoder Instantaneous Frequency (`HM-LS/PV`):**
   - Replaces uninterpolated `PitchHPS` (`df = 44100/32768 = 1.3458 Hz ≈ 8–12¢` bin-locking and `HPS(½FFT)` subharmonic octave drops) with a joint least-squares fit across harmonics $h = 1 \dots 6$:
     $$\hat{F}_0 = \frac{\sum_{h=1}^{6} w_h \, h \, \hat{f}_h}{\sum_{h=1}^{6} w_h \, h^2}, \qquad w_h = \frac{|X_{\text{enh}}(k_h)|^2}{1 + 0.12\,(h-1)^2}$$
     where $\hat{f}_h$ averages log-magnitude parabolic peak interpolation and two-frame Phase-Vocoder phase-unwrapped instantaneous frequency (`hop = 64` samples), guarded by an odd/even harmonic energy ratio check (`E_odd / E_even < 0.12`) to prevent $F_0/2$ subharmonic locking.
3. **Stage 3 — Harmonic-Locked Narrowband Hilbert Transform (`NB-Hilbert`) & Adaptive `140 ms` Plateau:**
   - Classical **EMD-HHT** sifting mode-mixes harmonics on plucked strings ($\sigma_{\text{IF}} = 133\text{–}173\text{¢}$). Instead, `NB-Hilbert` selects the single harmonic $k^* \in \{1,2,3,4\}$ with highest local signal-to-interference ratio (SIR), applies a zero-phase $\pm 6.5\%$ cosine-tapered analytic filter, and unwraps $\hat{F}_0(t) = \frac{1}{2\pi k^*}\frac{d\phi_{k^*}}{dt}$ ($\sigma_{\text{IF}} = 1.2\text{–}2.5\text{¢}$).
   - Slides a `140 ms` window across `[+60 ms, +480 ms]` to isolate the flattest post-attack plateau (avoiding both the `[0, 55 ms]` *mezrab* pluck-bend transient of `+3¢` to `+25¢` and next-note collisions in fast *chāhārmezrāb* passages).
4. **Stage 4 — Multi-Estimator Arbitration & Modulation/Confidence Gating:**
   - Arbitrates `HM-LS/PV`, `Parabolic YIN`, and `NB-Hilbert` on the selected `140 ms` plateau and gates out ornament/vibrato/*tahrir* frames (`wobble_plat_c > 18.0¢` or composite confidence `conf < 48.0`), reducing within-degree spread $\sigma$ by **17%–48%** across instruments and cutting cross-artist $\sigma$ on `Sol↓/Sol↑` to **`3.8¢`** and `Fa↓/Fa↑` to **`4.4¢`**.

---

## v3 Consensus Tuning Reference (17 Slots Across 13 Sources)

Full CSV table with reference frequencies (`Do = 261.63 Hz`, `326.40 Hz`, `330.00 Hz`): [`analysis/setar_tuning_mahur_best_guess.csv`](analysis/setar_tuning_mahur_best_guess.csv)

| Degree | v3 Consensus (¢ vs Do) | Cross-Artist $\sigma$ | Theory (¢) | Ratio / Fretboard Mechanism | Sources |
|---|---:|---:|---:|---|---:|
| `Re↓` | `−998.5¢` | `9.3¢` | `−996.1¢` | **9/16** (lower-octave Pythagorean `Re`) | **13/13** (folded) |
| `Mi♭↓` | `−798.7¢` | `7.5¢` | `−792.2¢` | **81/128** (native low minor 6th below `Do`) | **9/13** (native) |
| `Fa↓` | `−704.1¢` | `4.4¢` | `−702.0¢` | **2/3** (pure 5th below `Do`) | **13/13** (folded) |
| `Sol↓` | `−497.9¢` | `3.8¢` | `−498.0¢` | **3/4** (open 3rd *Moshtāq* string in `C–G–C–C`) | **13/13** (folded) |
| `Laᵏ↓` | `−355.7¢` | `5.2¢` | `−359.5¢` | **13/16** (`Reᵏ` `+138¢` fret played on `Sol` `−498¢` string) | **7/13** (native) |
| `La↓` | `−300.1¢` | `8.2¢` | `−294.1¢` | **27/32** (`Re` `9/8` fret played on `Sol` `−498¢` string) | **13/13** (folded) |
| `Si↓` | `−211.0¢` | `6.6¢` | `−209.8¢` | `Miᵏ` (`+288¢`) fret played on `Sol` (`−498¢`) string | **13/13** (folded) |
| `Siᵏ` | `−100.3¢` | `12.0¢` | `−98.0¢` | `Mi` (`+400¢`) fret played on `Sol` (`−498¢`) string | **8/13** (native) |
| `Do` | `+0.0¢` | `0.0¢` | `0.0¢` | **1/1** (open melody string / *shāhed*) | **13/13** (native) |
| `Reᵏ` | `+137.5¢` | `6.6¢` | `+138.6¢` | **13/12** / **27/25** (*koron* / neutral 2nd) | **8/13** (native) |
| `Re` | `+201.5¢` | `9.2¢` | `+203.9¢` | **9/8** (Pythagorean major 2nd) | **13/13** (folded) |
| `Miᵏ` | `+288.2¢` | `12.7¢` | `+294.1¢` | *Shekaste* lowered 3rd (**32/27** modern) | **10/13** (native) |
| `Mi` | `+400.8¢` | `16.2¢` | `+400.0¢` | ≈ ET major 3rd (compromise between **5/4** and **81/64**) | **13/13** (native) |
| `Fa↑` | `+495.9¢` | `4.4¢` | `+498.0¢` | **4/3** (pure 4th above `Do`) | **13/13** (folded) |
| `Sol↑` | `+702.1¢` | `3.8¢` | `+702.0¢` | **3/2** (pure 5th above `Do`) | **13/13** (folded) |
| `Laᵏ↑` | `+837.8¢` | `9.5¢` | `+840.5¢` | **13/8** (upper-octave `Laᵏ↓ + 1200¢` in *Delkash*) | **5/13** (native) |
| `La↑` | `+899.9¢` | `8.2¢` | `+905.9¢` | **27/16** (octave of `La↓`) | **13/13** (folded) |

---

## Corpus Summary (13 Sources, 44,848 Gated Strikes)

| SourceKey | Artist & Work | Instrument | Median `Do` (Hz) | `Do` Drift $\sigma$ (¢) | Tracks / Windows Used | Gated Strikes |
|---|---|---|---:|---:|---:|---:|
| `karimi` | Mahmud Karimi — *Vocal Radif Vol. 3* | Voice | `199.7 Hz` | `7.3¢` | `20/20` (`+3` rescued) | `4,530` |
| `forutan` | Yusef Forutan — *Setar Radif III* | Setar | `223.8 Hz` | `6.1¢` | `14/14` (`+4` rescued) | `2,354` |
| `ebadi` | Ahmad Ebadi — *Setar Solo: Mahur* | Setar | `252.5 Hz` | `12.0¢` | `34` windows (`45s/15s`) | `1,206` |
| `nariman` | Mansour Nariman — *Oud Radif: Mahour* | Oud | `265.1 Hz` | `11.1¢` | `20/20` (`+2` rescued) | `5,873` |
| `neydavud` | Morteza Neydavud — *Tar Radif Vol. 4* | Tar | `266.0 Hz` | `14.5¢` | `41/41` (`+24` rescued) | `4,499` |
| `lotfi_mahur` | M. R. Lotfi — *Curated Mahur Playlist* | Setar | `318.4 Hz` | `5.8¢` | `10/10` (`100%` kept) | `1,874` |
| `lotfi` | M. R. Lotfi — *In Memory of Darvish Khan* | Setar | `325.4 Hz` | `10.1¢` | `78` windows (`45s/15s`) | `1,793` |
| `borumand` | Nur-Ali Borumand — *Mirza Abdollah Radif* | Tar / Setar | `326.8 Hz` | `9.8¢` | `44/44` (`+14` rescued) | `6,659` |
| `alizadeh` | Hossein Alizadeh — *Radif Navazi: Mahur* | Setar | `331.4 Hz` | `15.5¢` | `36/36` (`+6` rescued) | `4,034` |
| `kasaei_radif` | Hassan Kasaei — *Radifs 1: Mahoor* | Setar | `369.5 Hz` | `12.0¢` | `43/43` (`+9` rescued) | `3,391` |
| `saba` | Abolhasan Saba — *Setar by Saba: Mahoor* | Setar | `376.5 Hz` | `11.9¢` | `65` windows (`45s/15s`) | `1,232` |
| `shahnazi` | Ali-Akbar Shahnazi — *Advanced Radif III* | Tar | `383.8 Hz` | `13.4¢` | `23/23` (`+4` rescued) | `2,059` |
| `shekarchi` | Aliakbar Shekarchi — *Kemancheh Radif* | Kemancheh | `441.5 Hz` | `13.2¢` | `33/33` (`100%` direct) | `5,511` |

---

## Reproducing From Cache or Audio

- **Re-extract strikes from `.wav` audio (native C 4-stage DSP):**
  ```bash
  clang -O3 -dynamiclib analysis/pitch_dsp.c -o analysis/libpitch_dsp.dylib -lm
  python3 analysis/extract_upgraded_strikes.py
  ```
- **Rebuild `analysis/consensus_template.json` from cached `analysis/strikes_*.npz` (no audio I/O required):**
  ```bash
  python3 analysis/rebuild_consensus_from_cache.py
  ```
- **Interactive Notebook:** [`notebooks/setar_pitch_start.ipynb`](notebooks/setar_pitch_start.ipynb) (`micromamba activate freqs`). Audio files under `audio/` are gitignored.
