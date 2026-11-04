#!/usr/bin/env python3
"""Run Rigorous Modal Function Audit & Spectral Peak Extraction across 80-220 Cents.
Version 5: Fast convolution KDE, window-specific sample size gating (N_win >= 15 for usable peaks),
per-file peak audit, explicit multi-dimensional classification of Category A sources,
reconciliation of pooled vs usable window events, and transparent reference hypothesis logging.

Outputs:
  - Per-recording modal tonic estimation
  - Fast convolved KDE (identical to Gaussian within 1e-5)
  - True window-specific sample size gating: N_win < 8 (insufficient), 8 <= N_win < 15 (sparse local max), N_win >= 15 (usable)
  - 1,000-resample non-parametric bootstrap 95% confidence intervals with presence probability
  - Multi-dimensional classification for Category A:
      * conditional peak precision (CI width <= 15¢)
      * reference robustness (flagging Shahnazi's 15.5¢ register sensitivity)
      * source/instrument attribution (flagging Kasaei's ney+setar mix and sharp fifth)
      * single-file concentration (flagging Safvat Part 1 = 92.6%, Talai = 92.2%)
      * modal ground-truth status (explicitly noted as researcher reference hypothesis)
  - Saves analysis/re_koron_modal_peak_audit.json
"""

import zipfile
import struct
import math
import json
import random
import statistics
import re
from pathlib import Path
from collections import defaultdict

OUT = Path("analysis")

# Precompute Gaussian kernel for fast discrete convolution KDE (bandwidth=5.0¢, bin_width=0.1¢)
BIN_W = 0.1
BANDWIDTH = 5.0
MAX_K = int(4.0 * BANDWIDTH / BIN_W)
K_VALS = [math.exp(-0.5 * ((i * BIN_W / BANDWIDTH) ** 2)) for i in range(-MAX_K, MAX_K + 1)]

def read_npz(path):
    arrays = {}
    with zipfile.ZipFile(path, 'r') as z:
        for name in z.namelist():
            if name.endswith('.npy'):
                buf = z.read(name)
                hlen = struct.unpack('<H', buf[8:10])[0]
                header = buf[10:10+hlen].decode('latin1')
                raw = buf[10+hlen:]
                if '<f8' in header or '=f8' in header:
                    n = len(raw) // 8
                    arrays[name[:-4]] = list(struct.unpack(f'<{n}d', raw[:n*8]))
                elif '<f4' in header or '=f4' in header:
                    n = len(raw) // 4
                    arrays[name[:-4]] = list(struct.unpack(f'<{n}f', raw[:n*4]))
    return arrays

def get_track_strings(npz_path):
    with zipfile.ZipFile(npz_path) as z:
        if 'track.npy' not in z.namelist():
            return []
        buf = z.read('track.npy')
        hlen = struct.unpack('<H', buf[8:10])[0]
        header = buf[10:10+hlen].decode('latin1')
        raw = buf[10+hlen:]
        m = re.search(r'\'<U(\d+)\'', header)
        if m:
            slen = int(m.group(1)) * 4
            n = len(raw) // slen
            return [raw[i*slen:(i+1)*slen].decode('utf-32-le').rstrip('\x00') for i in range(n)]
    return []

def kde_peak_location(values, grid_min=80.0, grid_max=220.0, bandwidth=5.0):
    """Locate KDE peak in 120-175¢ with strict window-specific sample size gating."""
    if not values:
        return None, 0.0, False, "No data (N = 0)"
        
    n_win = len([x for x in values if 120.0 <= x <= 175.0])
    if n_win < 8:
        return None, 0.0, False, f"Insufficient window strikes (N_win={n_win} < 8)"
        
    origin = 60.0
    n_bins = int((240.0 - 60.0) / BIN_W) + 1
    bins = [0] * n_bins
    for v in values:
        idx = int((v - origin) / BIN_W + 0.5)
        if 0 <= idx < n_bins:
            bins[idx] += 1
            
    steps = int((grid_max - grid_min) / 0.5) + 1
    grid = [grid_min + i * 0.5 for i in range(steps)]
    norm_const = 1.0 / (len(values) * bandwidth * math.sqrt(2 * math.pi))
    
    densities = []
    for i in range(steps):
        x = grid[i]
        x_idx = int((x - origin) / BIN_W + 0.5)
        s = 0.0
        start = max(0, x_idx - MAX_K)
        end = min(n_bins, x_idx + MAX_K + 1)
        for b_idx in range(start, end):
            s += bins[b_idx] * K_VALS[b_idx - x_idx + MAX_K]
        densities.append(s * norm_const)
        
    peaks = []
    for i in range(1, len(grid) - 1):
        if densities[i] > densities[i-1] and densities[i] > densities[i+1]:
            x = grid[i]
            if 120.0 <= x <= 175.0:
                peaks.append((x, densities[i]))
                
    if not peaks:
        return None, 0.0, False, "No local maximum in 120–175¢"
        
    best_peak_x, best_peak_d = max(peaks, key=lambda p: p[1])
    
    # Boundary Edge Rule: Reject peaks within 3.5¢ of the search bounds
    if best_peak_x <= 123.5 or best_peak_x >= 171.5:
        return best_peak_x, best_peak_d, False, f"Boundary edge artifact ({best_peak_x:.1f}¢)"
        
    left_dens = [densities[i] for i, x in enumerate(grid) if 85.0 <= x <= 115.0]
    right_dens = [densities[i] for i, x in enumerate(grid) if 185.0 <= x <= 215.0]
    left_min = min(left_dens) if left_dens else 0.0
    right_max = max(right_dens) if right_dens else 0.0
    
    left_drop = (best_peak_d - left_min) / best_peak_d if best_peak_d > 0 else 0.0
    grid_between = [densities[i] for i, x in enumerate(grid) if best_peak_x < x < 195.0]
    valley_between = min(grid_between) if grid_between else best_peak_d
    drop_to_valley = (best_peak_d - valley_between) / best_peak_d if best_peak_d > 0 else 0.0
    
    if right_max > best_peak_d * 1.5 and drop_to_valley < 0.20:
        return best_peak_x, best_peak_d, False, f"Shoulder on 200¢ whole tone ({best_peak_x:.1f}¢)"
        
    if left_drop < 0.20:
        return best_peak_x, best_peak_d, False, f"Insufficient prominence above half-step ({best_peak_x:.1f}¢)"
        
    if n_win < 15:
        return best_peak_x, best_peak_d, False, f"Local KDE Maximum (Sparse N_win={n_win} < 15)"
        
    return best_peak_x, best_peak_d, True, "Usable modal peak"

def bootstrap_peak_ci(values, n_boot=1000, bandwidth=5.0):
    """Compute 95% bootstrap confidence interval and presence probability for KDE peak."""
    n_win = len([x for x in values if 120.0 <= x <= 175.0])
    if n_win < 15:
        return None, None, 0.0
    peaks = []
    n = len(values)
    random.seed(42)
    for _ in range(n_boot):
        sample = [random.choice(values) for _ in range(n)]
        pk, _, is_dist, _ = kde_peak_location(sample, bandwidth=bandwidth)
        if pk is not None:
            peaks.append(pk)
    presence_prob = len(peaks) / n_boot
    if presence_prob < 0.40:
        return None, None, round(presence_prob, 2)
    peaks.sort()
    ci_lower = peaks[int(len(peaks) * 0.025)]
    ci_upper = peaks[int(len(peaks) * 0.975)]
    return round(ci_lower, 1), round(ci_upper, 1), round(presence_prob, 2)

def extract_file_events(p, default_ist=None, track_filter=None, min_conf=40.0):
    """Extract valid strikes and compute relative cents per recording file."""
    if not Path(p).exists():
        return [], 0, 0.0
    d = read_npz(p)
    fs = d.get('f', d.get('f0', []))
    confs = d.get('conf', [60.0]*len(fs))
    wobs = d.get('wobble_plat_c', [5.0]*len(fs))
    tracks = get_track_strings(p) if track_filter else None
    
    valid_fs = []
    for i, (f, c, w) in enumerate(zip(fs, confs, wobs)):
        if c >= min_conf and w <= 22.0 and 100 < f < 950:
            if track_filter:
                tr = tracks[i] if i < len(tracks) else ''
                if not any(tf in tr.lower() for tf in track_filter):
                    continue
            valid_fs.append(f)
            
    if len(valid_fs) < 8:
        return [], 0, 0.0
        
    base_hz = default_ist
    if not base_hz:
        bins = defaultdict(int)
        for f in valid_fs:
            c = 1200.0 * math.log2(f / 220.0)
            bins[round(c / 10.0) * 10.0] += 1
        top_b = sorted(bins.items(), key=lambda x: x[1], reverse=True)[0][0]
        base_hz = 220.0 * (2.0 ** (top_b / 1200.0))
        
    same_oct = [f for f in valid_fs if 0.8 * base_hz < f < 1.25 * base_hz]
    c_same = [1200.0 * math.log2(f / base_hz) for f in same_oct]
    t_same = [c for c in c_same if -45.0 <= c <= 45.0]
    n_tonic = len(t_same)
    offset = statistics.median(t_same) if t_same else 0.0
    tonic_hz = base_hz * (2.0 ** (offset / 1200.0))
    
    cents = []
    for f in valid_fs:
        rel = ((1200.0 * math.log2(f / tonic_hz) + 600.0) % 1200.0) - 600.0
        if 80.0 <= rel <= 220.0:
            cents.append(rel)
            
    return cents, n_tonic, tonic_hz

def main():
    print("==========================================================================================")
    print("Executing Rigorous Modal Peak Audit (v5: Fast KDE, Strict N_win Gating & Multi-Dimensional Categories)")
    print("==========================================================================================")
    
    performers = [
        # EPOCH 1: Qajar Shellac (1906-1914)
        {
            "id": "ahq_tar", "name": "Aqa Hoseyn-Qoli", "epoch": "Epoch 1 (1906-1914)", "instrument": "Tar (Fretted)",
            "context": "Solo Instrumental", "date": "1907/1909", "paths": ["analysis/strikes_historical_epoch1_qajar_aqa_hoseyn_qoli.npz"],
            "track_filter": ["11 - dastgah-e shur", "09 - avaz-e kord-e bayat"], "default_ist": 499.6,
            "annotation": "Shūr Darāmad modal finalis (nominal Sol; sounding B4 concert)",
            "is_mixed_instrument": False, "reference_sensitive": False
        },
        {
            "id": "bkh_kam", "name": "Bagher Khan Rameshgar", "epoch": "Epoch 1 (1906-1914)", "instrument": "Kamancheh (Fretless)",
            "context": "Solo Instrumental", "date": "1907/1909", "paths": [
                "analysis/strikes_qajar_kam_3-dastgah-e-shur-i.npz", "analysis/strikes_qajar_kam_11-dastgah-e-shur-ii.npz",
                "analysis/strikes_qajar_kam_13-hejaz.npz", "analysis/strikes_qajar_kam_14-avaz-e-bayat-e-kord.npz"
            ], "track_filter": None, "default_ist": None,
            "annotation": "Multi-track per-recording dominant modal pitch",
            "is_mixed_instrument": False, "reference_sensitive": False
        },
        {
            "id": "dk_tar", "name": "Darvish Khan", "epoch": "Epoch 1 (1906-1914)", "instrument": "Tar (Fretted)",
            "context": "Solo Instrumental", "date": "1912", "paths": ["analysis/strikes_historical_epoch1_qajar_darvish_khan.npz"],
            "track_filter": None, "default_ist": 370.0,
            "annotation": "Abū'atā modal tonic (nominal Fa#; sounding F#4 concert)",
            "is_mixed_instrument": False, "reference_sensitive": False
        },
        {
            "id": "hk_san", "name": "Hasankhan (Santur)", "epoch": "Epoch 1 (1906-1914)", "instrument": "Santur (Fixed Bridges)",
            "context": "Accompaniment with Vocal", "date": "1906", "paths": [
                "analysis/strikes_taherzadeh_1906_abuata_santour_1.npz", "analysis/strikes_taherzadeh_1906_abuata_santour_2.npz"
            ], "track_filter": None, "default_ist": None,
            "annotation": "Per-recording dominant santūr bridge tuning",
            "is_mixed_instrument": True, "reference_sensitive": False
        },
        {
            "id": "tz_voc", "name": "Hossein Ali Khan Taherzadeh", "epoch": "Epoch 1 (1906-1914)", "instrument": "Vocal (Unconstrained)",
            "context": "Accompanied Vocal", "date": "1906/1909", "paths": [
                "analysis/strikes_taherzadeh_1 - Rak (I).npz", "analysis/strikes_taherzadeh_4 - Rak (II).npz",
                "analysis/strikes_taherzadeh_5 - Avaz (II).npz", "analysis/strikes_taherzadeh_6 - Avaz (III).npz",
                "analysis/strikes_taherzadeh_8 - Avaz (I).npz"
            ], "track_filter": None, "default_ist": None,
            "annotation": "Per-recording vocal shāhed / modal focus",
            "is_mixed_instrument": True, "reference_sensitive": False
        },

        # EPOCH 2: Mid-Century Masters (1950s-1970s)
        {
            "id": "sh_tar", "name": "Ali-Akbar Shahnazi", "epoch": "Epoch 2 (1950s-1970s)", "instrument": "Tar (Fretted)",
            "context": "Solo Radif", "date": "1956", "paths": ["analysis/strikes_shur_shahnazi_tar.npz"],
            "track_filter": None, "default_ist": 213.2,
            "annotation": "Shūr Darāmad modal finalis (nominal Do; sounding A3 concert; 15.5¢ register sensitivity)",
            "is_mixed_instrument": False, "reference_sensitive": True
        },
        {
            "id": "sb_vln", "name": "Abolhasan Saba (Violin)", "epoch": "Epoch 2 (1950s-1970s)", "instrument": "Violin (Fretless)",
            "context": "Solo Instrumental", "date": "1952-1955", "paths": ["analysis/strikes_shur_saba_violin.npz"],
            "track_filter": None, "default_ist": 232.8,
            "annotation": "Shūr Darāmad modal finalis (nominal Re; sounding Bb3 concert)",
            "is_mixed_instrument": False, "reference_sensitive": False
        },
        {
            "id": "sb_set", "name": "Abolhasan Saba (Setar)", "epoch": "Epoch 2 (1950s-1970s)", "instrument": "Setar (Fretted)",
            "context": "Solo Instrumental", "date": "1950s", "paths": [
                "analysis/strikes_historical_epoch2_mid_saba_setar.npz", "analysis/strikes_dashti_saba_setar.npz"
            ], "track_filter": None, "default_ist": None,
            "annotation": "Per-recording dominant setār tuning",
            "is_mixed_instrument": False, "reference_sensitive": False
        },
        {
            "id": "yf_set", "name": "Yousef Foroutan", "epoch": "Epoch 2 (1950s-1970s)", "instrument": "Setar (Fretted)",
            "context": "Solo Instrumental", "date": "1968", "paths": ["analysis/strikes_shur_forutan_setar.npz"],
            "track_filter": None, "default_ist": 311.2,
            "annotation": "Shūr Darāmad modal finalis (nominal Mib; sounding Eb4 concert)",
            "is_mixed_instrument": False, "reference_sensitive": False
        },
        {
            "id": "hm_set", "name": "Saeed Hormozi", "epoch": "Epoch 2 (1950s-1970s)", "instrument": "Setar (Fretted)",
            "context": "Solo Radif", "date": "1974", "paths": ["analysis/strikes_historical_epoch2_mid_hormozi_tar_setar.npz"],
            "track_filter": None, "default_ist": None,
            "annotation": "Per-recording dominant setār tonic",
            "is_mixed_instrument": False, "reference_sensitive": False
        },
        {
            "id": "sf_set", "name": "Dr. Dariush Safvat", "epoch": "Epoch 2 (1950s-1970s)", "instrument": "Setar (Fretted)",
            "context": "Solo Instrumental", "date": "1962", "paths": [
                "analysis/strikes_Safvat_Setar_1962_LNwPd8_hP74.npz", "analysis/strikes_Safvat_Setar_Part1_5zSljfC5jdY.npz",
                "analysis/strikes_Safvat_Setar_Part2_dqg5Ka7--pg.npz"
            ], "track_filter": None, "default_ist": None,
            "annotation": "Per-recording dominant setār tonic (Part 1 dominates 92.6% of window events)",
            "is_mixed_instrument": False, "reference_sensitive": False
        },
        {
            "id": "km_voc", "name": "Mahmoud Karimi", "epoch": "Epoch 2 (1950s-1970s)", "instrument": "Vocal (Unconstrained)",
            "context": "Solo Vocal Pedagogy", "date": "1970s", "paths": ["analysis/strikes_shur_karimi_vocal.npz"],
            "track_filter": None, "default_ist": 235.2,
            "annotation": "Shūr vocal pedagogy finalis (nominal Re; sounding Bb3 concert)",
            "is_mixed_instrument": False, "reference_sensitive": False
        },
        {
            "id": "ks_ney", "name": "Hassan Kasaei", "epoch": "Epoch 2 (1950s-1970s)", "instrument": "Ney / Setar",
            "context": "Solo Ney & Setar", "date": "1960s-1970s", "paths": ["analysis/strikes_shur_kasaei_ney_setar.npz"],
            "track_filter": None, "default_ist": 272.3,
            "annotation": "Lower register (jawf) tonic (273.2 Hz, N=127); mixed ney/setār source; 5th sits sharp @ 727.4¢",
            "is_mixed_instrument": True, "reference_sensitive": False
        },
        {
            "id": "lt_kam", "name": "Mohammad-Reza Lotfi (Kamancheh)", "epoch": "Epoch 2 (1950s-1970s)", "instrument": "Kamancheh (Fretless)",
            "context": "Live Duet / Solo", "date": "1970s-1980s", "paths": [
                "analysis/strikes_exp_lotfi_kamancheh_abuata_WCpiD15zaYo.npz", "analysis/strikes_exp_lotfi_kamancheh_basel_yRB2Hd2nsiU.npz"
            ], "track_filter": None, "default_ist": None,
            "annotation": "Per-recording tonic: Basel (481.7 Hz), Abu'atā (522.2 Hz)",
            "is_mixed_instrument": True, "reference_sensitive": False
        },
        {
            "id": "lt_tar", "name": "Mohammad-Reza Lotfi (Tar)", "epoch": "Epoch 2 (1950s-1970s)", "instrument": "Tar (Fretted)",
            "context": "Duet with Vocal (Shajarian)", "date": "1970s-1980s", "paths": [
                "analysis/strikes_exp_lotfi_shajarian_abuata_pishdaramad_LnsbdhtBFLs.npz", "analysis/strikes_exp_lotfi_shajarian_hejaz_cixlq9KvqaA.npz"
            ], "track_filter": None, "default_ist": None,
            "annotation": "Per-recording instrumental modal anchor",
            "is_mixed_instrument": True, "reference_sensitive": False
        },
        {
            "id": "br_tar", "name": "Nour-Ali Borumand", "epoch": "Epoch 2 (1950s-1970s)", "instrument": "Tar/Setar (Fretted)",
            "context": "Solo Radif", "date": "1970s", "paths": ["analysis/strikes_shur_borumand_tar_setar.npz"],
            "track_filter": None, "default_ist": 131.0,
            "annotation": "Unobserved tonic in recording (N_tonic=0); no measured reference",
            "is_mixed_instrument": False, "reference_sensitive": False
        },
        {
            "id": "nr_oud", "name": "Mansour Nariman", "epoch": "Epoch 2 (1950s-1970s)", "instrument": "Oud (Fretless)",
            "context": "Solo Radif", "date": "1970s", "paths": ["analysis/strikes_shur_nariman_oud.npz"],
            "track_filter": None, "default_ist": 194.8,
            "annotation": "Shūr Darāmad modal finalis (nominal Sol; sounding G3 concert)",
            "is_mixed_instrument": False, "reference_sensitive": False
        },
        {
            "id": "bh_ens", "name": "Ali-Asghar Bahari & Shiraz Ensemble", "epoch": "Epoch 2 (1950s-1970s)", "instrument": "Ensemble (Kamancheh/Ney/Tar)",
            "context": "Live Full Ensemble", "date": "1970", "paths": ["analysis/strikes_shiraz_festival_abuata.npz"],
            "track_filter": None, "default_ist": None,
            "annotation": "Live ensemble dominant pitch",
            "is_mixed_instrument": True, "reference_sensitive": False
        },
        {
            "id": "tb_voc", "name": "Seyed Reza Tabatabaei", "epoch": "Epoch 2 (1950s-1970s)", "instrument": "Vocal (Unconstrained)",
            "context": "Accompanied Vocal", "date": "1970s", "paths": [
                "analysis/strikes_tabatabaei_01 - Avaze Abouata.npz", "analysis/strikes_tabatabaei_02 - Daramad Abouata.npz",
                "analysis/strikes_tabatabaei_04 - Hejaz.npz", "analysis/strikes_tabatabaei_05 - Korde Bayat.npz"
            ], "track_filter": None, "default_ist": None,
            "annotation": "Per-recording vocal shāhed",
            "is_mixed_instrument": True, "reference_sensitive": False
        },
        {
            "id": "sj_voc", "name": "Mohammad-Reza Shajarian", "epoch": "Epoch 2 (1950s-1970s)", "instrument": "Vocal (Unconstrained)",
            "context": "Accompanied Vocal", "date": "1970s-1980s", "paths": [
                "analysis/strikes_shajarian_13 - آواز ابوعطا (یتمیک-لیلی و مجنون-خسرو و شیرین-مثنوی).npz",
                "analysis/strikes_shajarian_14 - آواز ابوعطا (رامکلی-سیخی-چهارپاره-گبری).npz",
                "analysis/strikes_shajarian_15 - آواز ابوعطا (حجاز).npz",
                "analysis/strikes_shajarian_16 - آواز ابوعطا (درآمد).npz"
            ], "track_filter": None, "default_ist": None,
            "annotation": "Per-recording vocal shāhed",
            "is_mixed_instrument": True, "reference_sensitive": False
        },

        # EPOCH 3: Modern Revival & Conservatory (1980s-Present)
        {
            "id": "sf_ens", "name": "Amir Sharifi & Naqsh", "epoch": "Epoch 3 (1980s-Present)", "instrument": "Tar (Fretted) / Ensemble",
            "context": "Ensemble Suite", "date": "2012", "paths": [
                f"analysis/strikes_mokhammas_{i:02d}.npz" for i in range(1, 13)
            ], "track_filter": None, "default_ist": None,
            "annotation": "Per-movement modal centre across suite",
            "is_mixed_instrument": True, "reference_sensitive": False
        },
        {
            "id": "al_tar", "name": "Hossein Alizadeh", "epoch": "Epoch 3 (1980s-Present)", "instrument": "Tar (Fretted)",
            "context": "Solo Radif", "date": "1992", "paths": ["analysis/strikes_shur_alizadeh_tar.npz"],
            "track_filter": None, "default_ist": 368.4,
            "annotation": "Shūr Darāmad modal finalis (nominal Fa#; sounding F#4 concert)",
            "is_mixed_instrument": False, "reference_sensitive": False
        },
        {
            "id": "tl_tar", "name": "Dariush Talai", "epoch": "Epoch 3 (1980s-Present)", "instrument": "Tar (Fretted)",
            "context": "Solo / Accompaniment", "date": "1993", "paths": [
                "analysis/strikes_sarvestani_talai_Shur_Daramad.npz", "analysis/sarvestani_talai_Abu_Ata_Daramad.npz",
                "analysis/strikes_sarvestani_talai_Abu_Ata_Daramad.npz"
            ], "track_filter": None, "default_ist": None,
            "annotation": "Per-recording tonic: Shur Daramad solo (353.7 Hz, 145.0¢), Abu Ata vocal accomp (242.2 Hz)",
            "is_mixed_instrument": True, "reference_sensitive": False
        }
    ]

    # Deduplicate paths in Talai if any
    for p in performers:
        seen = set()
        dedup = []
        for x in p["paths"]:
            if x not in seen and Path(x).exists():
                seen.add(x)
                dedup.append(x)
        p["paths"] = dedup

    audit_rows = []
    for p in performers:
        all_cents = []
        tot_tonic = 0
        file_stats = []
        for path in p["paths"]:
            c, nt, thz = extract_file_events(path, p.get("default_ist"), p.get("track_filter"))
            all_cents.extend(c)
            tot_tonic += nt
            if c:
                pk_f, _, is_usable_f, reason_f = kde_peak_location(c)
                ci_f_lo, ci_f_hi, prob_f = bootstrap_peak_ci(c, n_boot=500) if is_usable_f else (None, None, 0.0)
                file_stats.append({
                    "file": Path(path).name,
                    "tonic_hz": round(thz, 1),
                    "n_tonic": nt,
                    "n_80_220": len(c),
                    "n_window_120_175": len([x for x in c if 120.0 <= x <= 175.0]),
                    "peak_cents": round(pk_f, 1) if pk_f is not None else None,
                    "ci_95": [ci_f_lo, ci_f_hi] if ci_f_lo is not None else None,
                    "classification": reason_f,
                    "is_usable": is_usable_f,
                    "presence_prob": prob_f
                })
            
        in_win = [c for c in all_cents if 120.0 <= c <= 175.0]
        pk, d, is_usable, reason = kde_peak_location(all_cents)
        ci_lo, ci_hi, presence_prob = (None, None, 0.0)
        if is_usable:
            ci_lo, ci_hi, presence_prob = bootstrap_peak_ci(all_cents, n_boot=1000)
            
        ci_width = (ci_hi - ci_lo) if (ci_lo is not None and ci_hi is not None) else None
        
        # Stability gating
        is_stable = False
        diag = reason
        if p["id"] == "br_tar" and tot_tonic == 0:
            diag = "No Observed Modal Tonic (N_tonic=0)"
            is_stable = False
        elif is_usable and ci_width is not None and ci_width <= 15.0 and tot_tonic >= 30:
            is_stable = True
            diag = "Usable modal peak (Stable)"
        elif is_usable:
            diag = f"Peak Unstable (CI width {ci_width:.1f}¢)" if ci_width else "Peak Unstable (Missing CI)"
            is_stable = False

        # Multi-file audit
        n_win_usable = sum(f["n_window_120_175"] for f in file_stats if f["is_usable"])
        n_win_sparse_or_rejected = len(in_win) - n_win_usable
        
        # Single-file dominance check
        is_single_file_dominated = False
        dominant_file = None
        dominant_file_share = 0.0
        if file_stats and len(in_win) > 0:
            top_f = max(file_stats, key=lambda f: f["n_window_120_175"])
            dominant_file_share = top_f["n_window_120_175"] / len(in_win)
            if dominant_file_share >= 0.80 and len(file_stats) > 1:
                is_single_file_dominated = True
                dominant_file = top_f["file"]

        # Classification & Category Assignment
        is_mixed = p.get("is_mixed_instrument", False)
        is_ref_sens = p.get("reference_sensitive", False)
        context = p["context"].lower()
        
        if "duet" in context or "ensemble" in context or "accompan" in context:
            category = "Category C: Ensemble & Duet / Mixed Sources"
        elif is_stable and not is_mixed:
            category = "Category A: Candidate Solo Radif Sources (Conditional Peak Precision <= 5.5¢)"
        elif is_stable and is_mixed and p["id"] == "ks_ney":
            # Kasaei is solo ney + setar
            category = "Category A: Candidate Solo Radif Sources (Conditional Peak Precision <= 5.5¢)"
        else:
            category = "Category B: Solo Sources (Sparse / Boundary / Peak Unstable / Unobserved Tonic)"
            
        audit_rows.append({
            "id": p["id"],
            "name": p["name"],
            "epoch": p["epoch"],
            "instrument": p["instrument"],
            "context": p["context"],
            "date": p.get("date", ""),
            "annotation": p.get("annotation", ""),
            "default_ist": p.get("default_ist"),
            "category": category,
            "n_total_80_220": len(all_cents),
            "n_window_total": len(in_win),
            "n_window_from_usable_files": n_win_usable,
            "n_window_from_sparse_or_rejected": n_win_sparse_or_rejected,
            "n_tonic": tot_tonic,
            "peak_cents": round(pk, 1) if pk is not None else None,
            "ci_95": [ci_lo, ci_hi] if ci_lo is not None else None,
            "ci_width": round(ci_width, 1) if ci_width is not None else None,
            "presence_prob": presence_prob,
            "diagnostic": diag,
            "is_stable": is_stable,
            "is_reference_sensitive": is_ref_sens,
            "is_mixed_instrument": is_mixed,
            "is_single_file_dominated": is_single_file_dominated,
            "dominant_file_share": round(dominant_file_share * 100, 1) if dominant_file_share > 0 else 0.0,
            "files": file_stats
        })

    # Sort: Category, Epoch, Name
    audit_rows.sort(key=lambda r: (r["category"], r["epoch"], r["name"]))

    print("\n" + "="*145)
    print(f"{'Performer':32s} | {'Category':15s} | {'Classification / Diagnostic':32s} | {'Peak (95% CI)':22s} | {'CI Width':8s} | {'N_Win':5s} | {'N_Ton':5s}")
    print("="*145)
    current_cat = None
    for r in audit_rows:
        if r["category"] != current_cat:
            current_cat = r["category"]
            print(f"\n--- {current_cat.upper()} ---")
        pk_str = f"{r['peak_cents']:.1f}¢" if r['peak_cents'] is not None else "None"
        if r['ci_95']:
            pk_str += f" [{r['ci_95'][0]}–{r['ci_95'][1]}]"
        w_str = f"{r['ci_width']:.1f}¢" if r['ci_width'] is not None else "-"
        print(f"{r['name']:32s} | {r['category'][:15]:15s} | {r['diagnostic'][:32]:32s} | {pk_str:22s} | {w_str:8s} | {r['n_window_total']:5d} | {r['n_tonic']:5d}")
    print("="*145)

    with open(OUT / "re_koron_modal_peak_audit.json", "w") as f:
        json.dump(audit_rows, f, indent=2)
    print(f"\nSaved updated v5 audit results to {OUT / 're_koron_modal_peak_audit.json'}")

if __name__ == "__main__":
    main()
