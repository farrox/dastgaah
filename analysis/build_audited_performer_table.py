#!/usr/bin/env python3
"""Build Audited Performer Table and Event-Level CSV for Persian Microtonal Intonation.

Reads per-event strike .npz files, normalizes each recording to its own verified modal
tonic (Ist = 0.0 cents), extracts the neutral second (Re-koron) degree, computes
authentic quantiles (Q1, Median, Q3, IQR) per performer and across pooled subgroups,
fits statistical equivalence tests (TOST), and exports:
  - analysis/re_koron_performer_audit_sample.csv
  - analysis/audited_re_koron_performer_summary.json
"""

import zipfile
import struct
import math
import json
import statistics
from pathlib import Path
from collections import defaultdict

OUT = Path("analysis")

def read_npz(path):
    """Read numpy arrays from an npz file using pure Python."""
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
    """Extract string track names from track.npy if present."""
    with zipfile.ZipFile(npz_path) as z:
        if 'track.npy' not in z.namelist():
            return []
        buf = z.read('track.npy')
        hlen = struct.unpack('<H', buf[8:10])[0]
        header = buf[10:10+hlen].decode('latin1')
        raw = buf[10+hlen:]
        import re
        m = re.search(r'\'<U(\d+)\'', header)
        if m:
            slen = int(m.group(1)) * 4
            n = len(raw) // slen
            return [raw[i*slen:(i+1)*slen].decode('utf-32-le').rstrip('\x00') for i in range(n)]
    return []

# --------------------------------------------------------------------------
# Performer Extraction Specifications
# --------------------------------------------------------------------------

def extract_from_shur_consensus_source(source_name, meta):
    """Extract events from shur_consensus.json and its matching npz file."""
    with open(OUT / "shur_consensus.json") as f:
        shur = json.load(f)
    s = shur["sources"][source_name]
    ist_cents = s["slots"]["ist_tonic"]["median_cents"]
    ist_hz = s["ist_hz"] * (2.0 ** (ist_cents / 1200.0))
    
    npz_path = OUT / f"strikes_shur_{source_name}.npz"
    d = read_npz(npz_path)
    fs = d.get('f', d.get('f0', []))
    confs = d.get('conf', [60.0]*len(fs))
    wobs = d.get('wobble_plat_c', [5.0]*len(fs))
    
    events = []
    # Window 120 to 175 cents (for Shahnazi use 125 to 175 to avoid passing half-step)
    min_w = 125.0 if "shahnazi" in source_name else 120.0
    max_w = 175.0
    
    for f, c, w in zip(fs, confs, wobs):
        if c >= 40.0 and w <= 22.0 and 100 < f < 950:
            rel = (1200.0 * math.log2(f / ist_hz) + 200.0) % 1200.0 - 200.0
            if min_w <= rel <= max_w:
                events.append({
                    "performer": meta["performer"],
                    "epoch": meta["epoch"],
                    "instrument": meta["instrument"],
                    "instrument_type": meta["instrument_type"],
                    "modality": meta["modality"],
                    "date": meta["date"],
                    "cents": round(rel, 2),
                    "conf": round(c, 1),
                    "f0_hz": round(f, 2)
                })
    return events

def extract_qajar_tar_events(npz_path, track_filter, meta, tonic_hint_hz):
    """Extract events from Qajar shellac tar files (Aqa Hoseyn-Qoli, Darvish Khan)."""
    d = read_npz(npz_path)
    tracks = get_track_strings(npz_path)
    fs = d['f']
    confs = d['conf']
    wobs = d['wobble_plat_c']
    
    events = []
    # Group by track to normalize tonic per track
    track_indices = defaultdict(list)
    for i, tr in enumerate(tracks):
        if any(f_name in tr.lower() for f_name in track_filter):
            track_indices[tr].append(i)
            
    for tr, idxs in track_indices.items():
        t_fs = [fs[i] for i in idxs if confs[i] >= 38.0 and wobs[i] <= 22.0 and 100 < fs[i] < 950]
        if len(t_fs) < 15:
            continue
        # Find local tonic
        bins = defaultdict(int)
        for f in t_fs:
            c = 1200.0 * math.log2(f / 220.0)
            bins[round(c / 10.0) * 10.0] += 1
        top_bin = sorted(bins.items(), key=lambda x: x[1], reverse=True)[0][0]
        thz = 220.0 * (2.0 ** (top_bin / 1200.0))
        # Refine tonic peak within +/- 45 cents
        rc = [((1200.0 * math.log2(f / thz) + 600.0) % 1200.0) - 600.0 for f in t_fs]
        t_vals = [c for c in rc if -45.0 <= c <= 45.0]
        if not t_vals:
            continue
        t_offset = statistics.median(t_vals)
        thz_refined = thz * (2.0 ** (t_offset / 1200.0))
        
        for i in idxs:
            f = fs[i]
            c = confs[i]
            w = wobs[i]
            if c >= 38.0 and w <= 22.0 and 100 < f < 950:
                rel = ((1200.0 * math.log2(f / thz_refined) + 600.0) % 1200.0) - 600.0
                if 120.0 <= rel <= 175.0:
                    events.append({
                        "performer": meta["performer"],
                        "epoch": meta["epoch"],
                        "instrument": meta["instrument"],
                        "instrument_type": meta["instrument_type"],
                        "modality": meta["modality"],
                        "date": meta["date"],
                        "cents": round(rel, 2),
                        "conf": round(c, 1),
                        "f0_hz": round(f, 2)
                    })
    return events

def extract_generic_npz_events(paths, meta, min_conf=40.0, max_wob=22.0):
    """Extract events from a list of npz files with automated tonic detection."""
    events = []
    for p in paths:
        if not Path(p).exists():
            continue
        d = read_npz(p)
        fs = d.get('f', d.get('f0', []))
        confs = d.get('conf', [60.0]*len(fs))
        wobs = d.get('wobble_plat_c', [5.0]*len(fs))
        valid = [f for f, c, w in zip(fs, confs, wobs) if c >= min_conf and w <= max_wob and 100 < f < 950]
        if len(valid) < 10:
            continue
        # Find dominant pitch (Ist)
        bins = defaultdict(int)
        for f in valid:
            c = 1200.0 * math.log2(f / 220.0)
            bins[round(c / 10.0) * 10.0] += 1
        top_bin = sorted(bins.items(), key=lambda x: x[1], reverse=True)[0][0]
        thz = 220.0 * (2.0 ** (top_bin / 1200.0))
        rc = [((1200.0 * math.log2(f / thz) + 600.0) % 1200.0) - 600.0 for f in valid]
        t_vals = [c for c in rc if -40.0 <= c <= 40.0]
        if not t_vals:
            continue
        thz_refined = thz * (2.0 ** (statistics.median(t_vals) / 1200.0))
        
        for f, c, w in zip(fs, confs, wobs):
            if c >= min_conf and w <= max_wob and 100 < f < 950:
                rel = ((1200.0 * math.log2(f / thz_refined) + 600.0) % 1200.0) - 600.0
                if 120.0 <= rel <= 175.0:
                    events.append({
                        "performer": meta["performer"],
                        "epoch": meta["epoch"],
                        "instrument": meta["instrument"],
                        "instrument_type": meta["instrument_type"],
                        "modality": meta["modality"],
                        "date": meta["date"],
                        "cents": round(rel, 2),
                        "conf": round(c, 1),
                        "f0_hz": round(f, 2)
                    })
    return events


def main():
    print("=====================================================================")
    print("Extracting Audited Performer Re-koron Events from Disk .npz Files...")
    print("=====================================================================")
    
    all_events = []
    
    # -----------------------------------------------------------------------
    # EPOCH 1: Early Qajar Era (1906-1914)
    # -----------------------------------------------------------------------
    # 1. Aqa Hoseyn-Qoli (Tar) - Shur and Kord-e Bayat tracks
    p_ahq = {
        "performer": "Aqa Hoseyn-Qoli",
        "epoch": "Epoch 1 (1906-1914)",
        "instrument": "Tar (Fretted)",
        "instrument_type": "Fretted",
        "modality": "Shur / Kord-e Bayat",
        "date": "1907/1909"
    }
    ev_ahq = extract_qajar_tar_events(
        "analysis/strikes_historical_epoch1_qajar_aqa_hoseyn_qoli.npz",
        ["11 - dastgah-e shur", "09 - avaz-e kord-e bayat"],
        p_ahq, 499.6
    )
    all_events.extend(ev_ahq)
    print(f"1. Aqa Hoseyn-Qoli (Tar): {len(ev_ahq)} strikes")

    # 2. Darvish Khan (Tar) - Abuata, Hejaz, Kord-e Bayat, Dashti
    p_dk = {
        "performer": "Darvish Khan",
        "epoch": "Epoch 1 (1906-1914)",
        "instrument": "Tar (Fretted)",
        "instrument_type": "Fretted",
        "modality": "Abuata / Hejaz / Kord / Dashti",
        "date": "1909/1912"
    }
    ev_dk = extract_qajar_tar_events(
        "analysis/strikes_historical_epoch1_qajar_darvish_khan.npz",
        ["abu’atâ", "abuata", "hejâz", "hejaz", "kord", "dashti"],
        p_dk, 370.0
    )
    all_events.extend(ev_dk)
    print(f"2. Darvish Khan (Tar): {len(ev_dk)} strikes")

    # 3. Bagher Khan Rameshgar (Kamancheh) - Shur / Hejaz / Kord
    p_bk = {
        "performer": "Bagher Khan Rameshgar",
        "epoch": "Epoch 1 (1906-1914)",
        "instrument": "Kamancheh (Fretless)",
        "instrument_type": "Fretless/Vocal",
        "modality": "Shur / Hejaz / Bayat-e Kord",
        "date": "1907"
    }
    ev_bk = extract_generic_npz_events([
        "analysis/strikes_qajar_kam_3-dastgah-e-shur-i.npz",
        "analysis/strikes_qajar_kam_11-dastgah-e-shur-ii.npz",
        "analysis/strikes_qajar_kam_13-hejaz.npz",
        "analysis/strikes_qajar_kam_14-avaz-e-bayat-e-kord.npz"
    ], p_bk, min_conf=38.0)
    all_events.extend(ev_bk)
    print(f"3. Bagher Khan Rameshgar (Kamancheh): {len(ev_bk)} strikes")

    # 4. Hasankhan (Santur) - Fixed Bridges Abu'ata (1906 Paris)
    p_hk = {
        "performer": "Hasankhan (Santur)",
        "epoch": "Epoch 1 (1906-1914)",
        "instrument": "Santur (Fixed Bridges)",
        "instrument_type": "Santur",
        "modality": "Abuata (1906)",
        "date": "1906"
    }
    ev_hk = extract_generic_npz_events([
        "analysis/strikes_taherzadeh_1906_abuata_santour_1.npz",
        "analysis/strikes_taherzadeh_1906_abuata_santour_2.npz"
    ], p_hk, min_conf=40.0)
    all_events.extend(ev_hk)
    print(f"4. Hasankhan (Santur): {len(ev_hk)} strikes")

    # 5. Taherzadeh (Vocal) - 1906-1909 Shellac
    p_tz = {
        "performer": "Hossein Ali Khan Taherzadeh",
        "epoch": "Epoch 1 (1906-1914)",
        "instrument": "Vocal (Unconstrained)",
        "instrument_type": "Fretless/Vocal",
        "modality": "Abuata / Shur (1906-1909)",
        "date": "1906/1909"
    }
    ev_tz = extract_generic_npz_events([
        "analysis/strikes_taherzadeh_1 - Rak (I).npz",
        "analysis/strikes_taherzadeh_4 - Rak (II).npz",
        "analysis/strikes_taherzadeh_5 - Avaz (II).npz",
        "analysis/strikes_taherzadeh_6 - Avaz (III).npz",
        "analysis/strikes_taherzadeh_8 - Avaz (I).npz"
    ], p_tz, min_conf=38.0)
    all_events.extend(ev_tz)
    print(f"5. Taherzadeh (Vocal): {len(ev_tz)} strikes")

    # -----------------------------------------------------------------------
    # EPOCH 2: Mid-Century Radif Masters (1950s-1970s)
    # -----------------------------------------------------------------------
    # 6. Ali-Akbar Shahnazi (Tar)
    p_sh = {
        "performer": "Ali-Akbar Shahnazi",
        "epoch": "Epoch 2 (1950s-1970s)",
        "instrument": "Tar (Fretted)",
        "instrument_type": "Fretted",
        "modality": "Radif Shur",
        "date": "1956"
    }
    ev_sh = extract_from_shur_consensus_source("shahnazi_tar", p_sh)
    all_events.extend(ev_sh)
    print(f"6. Ali-Akbar Shahnazi (Tar): {len(ev_sh)} strikes")

    # 7. Abolhasan Saba (Violin)
    p_sb_v = {
        "performer": "Abolhasan Saba (Violin)",
        "epoch": "Epoch 2 (1950s-1970s)",
        "instrument": "Violin (Fretless)",
        "instrument_type": "Fretless/Vocal",
        "modality": "Shur / Segah",
        "date": "1952-1955"
    }
    ev_sb_v = extract_from_shur_consensus_source("saba_violin", p_sb_v)
    all_events.extend(ev_sb_v)
    print(f"7. Abolhasan Saba (Violin): {len(ev_sb_v)} strikes")

    # 8. Abolhasan Saba (Setar)
    p_sb_s = {
        "performer": "Abolhasan Saba (Setar)",
        "epoch": "Epoch 2 (1950s-1970s)",
        "instrument": "Setar (Fretted)",
        "instrument_type": "Fretted",
        "modality": "Shur / Dashti / Nava",
        "date": "1950s"
    }
    ev_sb_s = extract_generic_npz_events([
        "analysis/strikes_historical_epoch2_mid_saba_setar.npz",
        "analysis/strikes_dashti_saba_setar.npz",
        "analysis/strikes_nava_saba_setar.npz"
    ], p_sb_s, min_conf=45.0)
    all_events.extend(ev_sb_s)
    print(f"8. Abolhasan Saba (Setar): {len(ev_sb_s)} strikes")

    # 9. Yousef Foroutan (Setar)
    p_yf = {
        "performer": "Yousef Foroutan",
        "epoch": "Epoch 2 (1950s-1970s)",
        "instrument": "Setar (Fretted)",
        "instrument_type": "Fretted",
        "modality": "Solo Setar Shur",
        "date": "1968"
    }
    ev_yf = extract_from_shur_consensus_source("forutan_setar", p_yf)
    all_events.extend(ev_yf)
    print(f"9. Yousef Foroutan (Setar): {len(ev_yf)} strikes")

    # 10. Saeed Hormozi (Setar)
    p_hm = {
        "performer": "Saeed Hormozi",
        "epoch": "Epoch 2 (1950s-1970s)",
        "instrument": "Setar (Fretted)",
        "instrument_type": "Fretted",
        "modality": "Radif Shur / Homayun / Esfahan",
        "date": "1974"
    }
    ev_hm = extract_generic_npz_events([
        "analysis/strikes_historical_epoch2_mid_hormozi_tar_setar.npz",
        "analysis/strikes_homayun_hormozi_setar.npz"
    ], p_hm, min_conf=45.0)
    all_events.extend(ev_hm)
    print(f"10. Saeed Hormozi (Setar): {len(ev_hm)} strikes")

    # 11. Dr. Dariush Safvat (Setar)
    p_sf = {
        "performer": "Dr. Dariush Safvat",
        "epoch": "Epoch 2 (1950s-1970s)",
        "instrument": "Setar (Fretted)",
        "instrument_type": "Fretted",
        "modality": "Solo Setar 1962 / Utah",
        "date": "1962"
    }
    ev_sf = extract_generic_npz_events([
        "analysis/strikes_Safvat_Setar_1962_LNwPd8_hP74.npz",
        "analysis/strikes_Safvat_Setar_Part1_5zSljfC5jdY.npz",
        "analysis/strikes_Safvat_Setar_Part2_dqg5Ka7--pg.npz",
        "analysis/strikes_Safvat_Setar_Razavi_Utah_yvZh-u4C6jY.npz",
        "analysis/strikes_Safvat_Setar_Solo_BSPDwyzNV6w.npz"
    ], p_sf, min_conf=45.0)
    all_events.extend(ev_sf)
    print(f"11. Dr. Dariush Safvat (Setar): {len(ev_sf)} strikes")

    # 12. Mahmoud Karimi (Vocal)
    p_km = {
        "performer": "Mahmoud Karimi",
        "epoch": "Epoch 2 (1950s-1970s)",
        "instrument": "Vocal (Unconstrained)",
        "instrument_type": "Fretless/Vocal",
        "modality": "Vocal Radif Shur",
        "date": "1970s"
    }
    ev_km = extract_from_shur_consensus_source("karimi_vocal", p_km)
    all_events.extend(ev_km)
    print(f"12. Mahmoud Karimi (Vocal): {len(ev_km)} strikes")

    # 13. Hassan Kasaei (Ney)
    p_ks = {
        "performer": "Hassan Kasaei",
        "epoch": "Epoch 2 (1950s-1970s)",
        "instrument": "Ney (Fretless Aerophone)",
        "instrument_type": "Fretless/Vocal",
        "modality": "Shur / Abuata",
        "date": "1960s-1970s"
    }
    ev_ks = extract_from_shur_consensus_source("kasaei_ney_setar", p_ks)
    all_events.extend(ev_ks)
    print(f"13. Hassan Kasaei (Ney): {len(ev_ks)} strikes")

    # 14. Mohammad-Reza Lotfi (Kamancheh)
    p_lt_k = {
        "performer": "Mohammad-Reza Lotfi (Kamancheh)",
        "epoch": "Epoch 2 (1950s-1970s)",
        "instrument": "Kamancheh (Fretless)",
        "instrument_type": "Fretless/Vocal",
        "modality": "Abuata / Shur",
        "date": "1970s-1980s"
    }
    ev_lt_k = extract_generic_npz_events([
        "analysis/strikes_exp_lotfi_kamancheh_abuata_WCpiD15zaYo.npz",
        "analysis/strikes_exp_lotfi_kamancheh_basel_yRB2Hd2nsiU.npz",
        "analysis/strikes_exp_lotfi_kamancheh_solo_xKEM8b2oozU.npz"
    ], p_lt_k, min_conf=48.0)
    all_events.extend(ev_lt_k)
    print(f"14. Mohammad-Reza Lotfi (Kamancheh): {len(ev_lt_k)} strikes")

    # 15. Mohammad-Reza Lotfi (Tar)
    p_lt_t = {
        "performer": "Mohammad-Reza Lotfi (Tar)",
        "epoch": "Epoch 2 (1950s-1970s)",
        "instrument": "Tar (Fretted)",
        "instrument_type": "Fretted",
        "modality": "Abuata / Shur",
        "date": "1970s-1980s"
    }
    ev_lt_t = extract_generic_npz_events([
        "analysis/strikes_exp_lotfi_shajarian_abuata_pishdaramad_LnsbdhtBFLs.npz",
        "analysis/strikes_exp_lotfi_shajarian_hejaz_cixlq9KvqaA.npz",
        "analysis/strikes_exp_lotfi_shajarian_zarbi_hejaz_J4pb8fpsoB4.npz"
    ], p_lt_t, min_conf=48.0)
    all_events.extend(ev_lt_t)
    print(f"15. Mohammad-Reza Lotfi (Tar): {len(ev_lt_t)} strikes")

    # 16. Nour-Ali Borumand (Tar/Setar)
    p_br = {
        "performer": "Nour-Ali Borumand",
        "epoch": "Epoch 2 (1950s-1970s)",
        "instrument": "Tar/Setar (Fretted)",
        "instrument_type": "Fretted",
        "modality": "Radif Shur",
        "date": "1970s"
    }
    ev_br = extract_from_shur_consensus_source("borumand_tar_setar", p_br)
    all_events.extend(ev_br)
    print(f"16. Nour-Ali Borumand (Tar/Setar): {len(ev_br)} strikes")

    # 17. Mansour Nariman (Oud)
    p_nr = {
        "performer": "Mansour Nariman",
        "epoch": "Epoch 2 (1950s-1970s)",
        "instrument": "Oud (Fretless Lute)",
        "instrument_type": "Fretless/Vocal",
        "modality": "Radif Shur",
        "date": "1970s"
    }
    ev_nr = extract_from_shur_consensus_source("nariman_oud", p_nr)
    all_events.extend(ev_nr)
    print(f"17. Mansour Nariman (Oud): {len(ev_nr)} strikes")

    # 18. Ali-Asghar Bahari / Shiraz Festival 1970
    p_bh = {
        "performer": "Ali-Asghar Bahari & Shiraz Ensemble",
        "epoch": "Epoch 2 (1950s-1970s)",
        "instrument": "Kamancheh / Ney / Tar",
        "instrument_type": "Fretless/Vocal",
        "modality": "Abuata Live 1970",
        "date": "1970"
    }
    ev_bh = extract_generic_npz_events(["analysis/strikes_shiraz_festival_abuata.npz"], p_bh, min_conf=48.0)
    all_events.extend(ev_bh)
    print(f"18. Shiraz 1970 Abuata (Bahari/Kasaei/Shahnaz): {len(ev_bh)} strikes")

    # 19. Seyed Reza Tabatabaei (Vocal) - Maktab-e Esfahan Abuata
    p_tb = {
        "performer": "Seyed Reza Tabatabaei",
        "epoch": "Epoch 2 (1950s-1970s)",
        "instrument": "Vocal (Unconstrained)",
        "instrument_type": "Fretless/Vocal",
        "modality": "Maktab-e Esfahan Abuata",
        "date": "1970s"
    }
    ev_tb = extract_generic_npz_events([
        "analysis/strikes_tabatabaei_01 - Avaze Abouata.npz",
        "analysis/strikes_tabatabaei_02 - Daramad Abouata.npz",
        "analysis/strikes_tabatabaei_04 - Hejaz.npz",
        "analysis/strikes_tabatabaei_05 - Korde Bayat.npz"
    ], p_tb, min_conf=45.0)
    all_events.extend(ev_tb)
    print(f"19. Seyed Reza Tabatabaei (Vocal): {len(ev_tb)} strikes")

    # 20. Mohammad-Reza Shajarian (Vocal) - Vocal Radif Abuata
    p_sj = {
        "performer": "Mohammad-Reza Shajarian",
        "epoch": "Epoch 2 (1950s-1970s)",
        "instrument": "Vocal (Unconstrained)",
        "instrument_type": "Fretless/Vocal",
        "modality": "Vocal Radif Abuata",
        "date": "1970s-1980s"
    }
    ev_sj = extract_generic_npz_events([
        "analysis/strikes_shajarian_13 - آواز ابوعطا (یتمیک-لیلی و مجنون-خسرو و شیرین-مثنوی).npz",
        "analysis/strikes_shajarian_14 - آواز ابوعطا (رامکلی-سیخی-چهارپاره-گبری).npz",
        "analysis/strikes_shajarian_15 - آواز ابوعطا (حجاز).npz",
        "analysis/strikes_shajarian_16 - آواز ابوعطا (درآمد).npz"
    ], p_sj, min_conf=48.0)
    all_events.extend(ev_sj)
    print(f"20. Mohammad-Reza Shajarian (Vocal): {len(ev_sj)} strikes")

    # -----------------------------------------------------------------------
    # EPOCH 3: Modern Revival & Conservatory (1980s-Present)
    # -----------------------------------------------------------------------
    # 21. Amir Sharifi / Ensemble Naqsh (Tar) - Mokhammas Album
    p_sf3 = {
        "performer": "Amir Sharifi & Naqsh",
        "epoch": "Epoch 3 (1980s-Present)",
        "instrument": "Tar (Fretted - Historical setup)",
        "instrument_type": "Fretted",
        "modality": "Mokhammas Suite",
        "date": "2012"
    }
    ev_sf3 = extract_generic_npz_events([
        f"analysis/strikes_mokhammas_{i:02d}.npz" for i in range(1, 13)
    ], p_sf3, min_conf=50.0)
    all_events.extend(ev_sf3)
    print(f"21. Amir Sharifi / Naqsh (Tar): {len(ev_sf3)} strikes")

    # 22. Hossein Alizadeh (Tar)
    p_al = {
        "performer": "Hossein Alizadeh",
        "epoch": "Epoch 3 (1980s-Present)",
        "instrument": "Tar (Fretted - Modern setup)",
        "instrument_type": "Fretted",
        "modality": "Radif Shur",
        "date": "1992"
    }
    ev_al = extract_from_shur_consensus_source("alizadeh_tar", p_al)
    all_events.extend(ev_al)
    print(f"22. Hossein Alizadeh (Tar): {len(ev_al)} strikes")

    # 23. Dariush Talai (Tar) - Sarvestani & Radif Shur / Abuata
    p_tl = {
        "performer": "Dariush Talai",
        "epoch": "Epoch 3 (1980s-Present)",
        "instrument": "Tar (Fretted - Radif)",
        "instrument_type": "Fretted",
        "modality": "Radif Shur / Abuata",
        "date": "1993"
    }
    ev_tl = extract_generic_npz_events([
        "analysis/strikes_sarvestani_talai_Shur_Daramad.npz",
        "analysis/strikes_sarvestani_talai_Abu_Ata_Daramad.npz"
    ], p_tl, min_conf=48.0)
    all_events.extend(ev_tl)
    print(f"23. Dariush Talai (Tar): {len(ev_tl)} strikes")

    # -----------------------------------------------------------------------
    # Export CSV
    # -----------------------------------------------------------------------
    csv_path = OUT / "re_koron_performer_audit_sample.csv"
    with open(csv_path, "w") as f:
        f.write("performer,epoch,instrument,instrument_type,modality,date,cents,conf,f0_hz\n")
        for ev in all_events:
            f.write(f'"{ev["performer"]}","{ev["epoch"]}","{ev["instrument"]}","{ev["instrument_type"]}","{ev["modality"]}","{ev["date"]}",{ev["cents"]},{ev["conf"]},{ev["f0_hz"]}\n')
    print(f"\nSuccessfully wrote {len(all_events)} per-event strikes to {csv_path}")

    # -----------------------------------------------------------------------
    # Compute Exact Per-Performer Summary Table
    # -----------------------------------------------------------------------
    perf_groups = defaultdict(list)
    for ev in all_events:
        perf_groups[ev["performer"]].append(ev)
        
    summary_rows = []
    for perf, evs in perf_groups.items():
        cents = [e["cents"] for e in evs]
        cents.sort()
        n = len(cents)
        q1 = cents[n // 4]
        med = statistics.median(cents)
        q3 = cents[(n * 3) // 4]
        iqr = q3 - q1
        mean = statistics.mean(cents)
        stdev = statistics.stdev(cents) if n > 1 else 0.0
        meta = evs[0]
        
        # Proximity to 13/12 (138.57 cents)
        prox_13_12 = med - 138.57
        
        summary_rows.append({
            "performer": perf,
            "epoch": meta["epoch"],
            "instrument": meta["instrument"],
            "instrument_type": meta["instrument_type"],
            "modality": meta["modality"],
            "date": meta["date"],
            "n_strikes": n,
            "q1": round(q1, 2),
            "median_cents": round(med, 2),
            "q3": round(q3, 2),
            "iqr": round(iqr, 2),
            "mean": round(mean, 2),
            "stdev": round(stdev, 2),
            "prox_13_12": round(prox_13_12, 2)
        })

    # Sort summary rows by Epoch then Performer
    summary_rows.sort(key=lambda r: (r["epoch"], r["performer"]))

    print("\n" + "="*110)
    print(f"{'Performer':35s} | {'Epoch':18s} | {'N':4s} | {'Q1':5s} | {'Median':6s} | {'Q3':5s} | {'IQR':5s} | {'Δ(13/12)':8s}")
    print("="*110)
    for r in summary_rows:
        print(f"{r['performer']:35s} | {r['epoch']:18s} | {r['n_strikes']:4d} | {r['q1']:5.1f} | {r['median_cents']:6.1f} | {r['q3']:5.1f} | {r['iqr']:5.1f} | {r['prox_13_12']:+7.1f}¢")
    print("="*110)

    # -----------------------------------------------------------------------
    # Pooled & Subgroup Statistics
    # -----------------------------------------------------------------------
    all_cents = sorted([e["cents"] for e in all_events])
    total_n = len(all_cents)
    p_q1 = all_cents[total_n // 4]
    p_med = statistics.median(all_cents)
    p_q3 = all_cents[(total_n * 3) // 4]
    p_iqr = p_q3 - p_q1
    p_mean = statistics.mean(all_cents)
    p_sd = statistics.stdev(all_cents)
    
    print("\n================== AUTHENTIC POOLED QUANTILIC STATISTICS ==================")
    print(f"Total Verified Re-koron Strikes: N = {total_n}")
    print(f"Pooled Q1:     {p_q1:.2f}¢")
    print(f"Pooled Median: {p_med:.2f}¢")
    print(f"Pooled Q3:     {p_q3:.2f}¢")
    print(f"Pooled IQR:    {p_iqr:.2f}¢")
    print(f"Pooled Mean:   {p_mean:.2f}¢ (SD = {p_sd:.2f}¢)")
    print(f"Distance to Al-Farabi 13/12 (138.57¢): {p_med - 138.57:+.2f}¢")
    print(f"Distance to 24-TET (150.00¢):           {p_med - 150.00:+.2f}¢")

    # Epoch breakdowns
    epoch_cents = defaultdict(list)
    for e in all_events:
        epoch_cents[e["epoch"]].append(e["cents"])
        
    print("\n================== HISTORICAL EPOCH BREAKDOWNS ==================")
    epoch_stats = {}
    for ep in sorted(epoch_cents.keys()):
        c_list = sorted(epoch_cents[ep])
        en = len(c_list)
        eq1 = c_list[en // 4]
        emed = statistics.median(c_list)
        eq3 = c_list[(en * 3) // 4]
        eiqr = eq3 - eq1
        emean = statistics.mean(c_list)
        esd = statistics.stdev(c_list)
        epoch_stats[ep] = {
            "n": en, "q1": round(eq1, 2), "median": round(emed, 2),
            "q3": round(eq3, 2), "iqr": round(eiqr, 2), "mean": round(emean, 2), "sd": round(esd, 2)
        }
        print(f"{ep:25s} | N={en:4d} | Q1={eq1:5.1f} | Med={emed:5.1f} | Q3={eq3:5.1f} | IQR={eiqr:5.1f} | Mean={emean:5.1f} (SD={esd:4.1f})")

    # Instrument Type breakdowns
    inst_cents = defaultdict(list)
    for e in all_events:
        inst_cents[e["instrument_type"]].append(e["cents"])
        
    print("\n================== INSTRUMENT TYPE BREAKDOWNS ==================")
    inst_stats = {}
    for it in sorted(inst_cents.keys()):
        c_list = sorted(inst_cents[it])
        it_n = len(c_list)
        it_q1 = c_list[it_n // 4]
        it_med = statistics.median(c_list)
        it_q3 = c_list[(it_n * 3) // 4]
        it_iqr = it_q3 - it_q1
        it_mean = statistics.mean(c_list)
        it_sd = statistics.stdev(c_list)
        inst_stats[it] = {
            "n": it_n, "q1": round(it_q1, 2), "median": round(it_med, 2),
            "q3": round(it_q3, 2), "iqr": round(it_iqr, 2), "mean": round(it_mean, 2), "sd": round(it_sd, 2)
        }
        print(f"{it:25s} | N={it_n:4d} | Q1={it_q1:5.1f} | Med={it_med:5.1f} | Q3={it_q3:5.1f} | IQR={it_iqr:5.1f} | Mean={it_mean:5.1f} (SD={it_sd:4.1f})")

    # -----------------------------------------------------------------------
    # Statistical Equivalence Testing (TOST)
    # Testing Epoch 1 (Qajar) vs Epoch 3 (Modern)
    # Using Performer-Level Medians to Avoid Pseudoreplication
    # -----------------------------------------------------------------------
    ep1_perfs = [r["median_cents"] for r in summary_rows if "Epoch 1" in r["epoch"]]
    ep3_perfs = [r["median_cents"] for r in summary_rows if "Epoch 3" in r["epoch"]]
    
    n1 = len(ep1_perfs)
    n3 = len(ep3_perfs)
    m1 = statistics.mean(ep1_perfs)
    m3 = statistics.mean(ep3_perfs)
    s1 = statistics.stdev(ep1_perfs) if n1 > 1 else 0.0
    s3 = statistics.stdev(ep3_perfs) if n3 > 1 else 0.0
    diff = m3 - m1
    
    # Pooled variance
    df = n1 + n3 - 2
    sp2 = (((n1 - 1) * (s1 ** 2)) + ((n3 - 1) * (s3 ** 2))) / df
    se_diff = math.sqrt(sp2 * (1.0 / n1 + 1.0 / n3))
    
    # TOST for equivalence margin Delta = 5.0 cents
    # H0: |diff| >= 5.0 cents vs H1: -5.0 < diff < +5.0
    delta = 5.0
    t_lower = (diff - (-delta)) / se_diff
    t_upper = (diff - delta) / se_diff
    
    # Approximate two-tailed Student-t p-values or normal approximation
    # For df = 6, t(0.05) ~ 1.943
    print("\n================== STATISTICAL EQUIVALENCE TEST (TOST) ==================")
    print(f"Performer-Level Analysis (Degrees of Freedom df = {df}):")
    print(f"Epoch 1 Performer Medians: {ep1_perfs} -> Mean = {m1:.2f}¢ (SD = {s1:.2f}¢)")
    print(f"Epoch 3 Performer Medians: {ep3_perfs} -> Mean = {m3:.2f}¢ (SD = {s3:.2f}¢)")
    print(f"Empirical Difference (Epoch 3 - Epoch 1): {diff:+.2f}¢ (SE = {se_diff:.2f}¢)")
    print(f"90% Confidence Interval: [{diff - 1.943*se_diff:.2f}¢, {diff + 1.943*se_diff:.2f}¢]")
    print(f"Equivalence Margin: ±{delta:.1f}¢")
    print(f"TOST t-statistics: t_lower = {t_lower:.3f}, t_upper = {t_upper:.3f}")

    # Export complete JSON summary
    export_data = {
        "dataset_metadata": {
            "total_verified_strikes": total_n,
            "total_performers": len(summary_rows),
            "csv_path": "analysis/re_koron_performer_audit_sample.csv"
        },
        "pooled_quantiles": {
            "q1": round(p_q1, 2),
            "median": round(p_med, 2),
            "q3": round(p_q3, 2),
            "iqr": round(p_iqr, 2),
            "mean": round(p_mean, 2),
            "stdev": round(p_sd, 2)
        },
        "epoch_breakdowns": epoch_stats,
        "instrument_breakdowns": inst_stats,
        "equivalence_test": {
            "epoch_1_performers_n": n1,
            "epoch_3_performers_n": n3,
            "degrees_of_freedom": df,
            "epoch_1_mean": round(m1, 2),
            "epoch_3_mean": round(m3, 2),
            "difference_cents": round(diff, 2),
            "se_cents": round(se_diff, 2),
            "margin_delta": delta,
            "t_lower": round(t_lower, 3),
            "t_upper": round(t_upper, 3)
        },
        "performers": summary_rows
    }
    
    with open(OUT / "audited_re_koron_performer_summary.json", "w") as f:
        json.dump(export_data, f, indent=2)
    print(f"Successfully saved audited summary to {OUT / 'audited_re_koron_performer_summary.json'}")

if __name__ == "__main__":
    main()

