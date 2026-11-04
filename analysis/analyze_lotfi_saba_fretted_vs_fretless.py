import zipfile, struct, math, json
from pathlib import Path
from collections import defaultdict

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

def find_modal_center(f0_list, conf_list, min_c=50.0):
    # filter high conf
    valid = [f for f, c in zip(f0_list, conf_list) if c > min_c and 100 < f < 900]
    if not valid:
        return 300.0
    # histogram with 5-cent bins folded modulo octave or absolute
    # find highest density peak around 200-450 Hz
    bins = defaultdict(float)
    bin_width_c = 10.0
    ref = 220.0
    for f in valid:
        c = 1200.0 * math.log2(f / ref)
        # fold to single octave or keep absolute
        b = round(c / bin_width_c) * bin_width_c
        bins[b] += 1.0
    best_bin = max(bins.items(), key=lambda x: x[1])[0]
    center_hz = ref * (2.0 ** (best_bin / 1200.0))
    return center_hz

datasets = [
    # --- LOTFI ---
    ("Lotfi (Kamancheh - Fretless)", [
        "analysis/strikes_exp_lotfi_kamancheh_abuata_WCpiD15zaYo.npz",
        "analysis/strikes_exp_lotfi_kamancheh_basel_yRB2Hd2nsiU.npz",
        "analysis/strikes_exp_lotfi_kamancheh_solo_xKEM8b2oozU.npz"
    ]),
    ("Lotfi (Tar/Setar - Fretted)", [
        "analysis/strikes_exp_lotfi_shajarian_abuata_pishdaramad_LnsbdhtBFLs.npz",
        "analysis/strikes_exp_lotfi_shajarian_hejaz_cixlq9KvqaA.npz",
        "analysis/strikes_exp_lotfi_shajarian_zarbi_hejaz_J4pb8fpsoB4.npz",
        "analysis/strikes_dashti_lotfi_setar.npz",
        "analysis/strikes_shur_lotfi_solo.npz"
    ]),
    # --- SABA ---
    ("Saba (Violin - Fretless)", [
        "analysis/strikes_shur_saba_violin.npz",
        "analysis/strikes_segah_saba_violin.npz",
        "analysis/strikes_rast_panjgah_saba_violin.npz"
    ]),
    ("Saba (Setar - Fretted)", [
        "analysis/strikes_dashti_saba_setar.npz",
        "analysis/strikes_nava_saba_setar.npz",
        "analysis/strikes_historical_epoch2_mid_saba_setar.npz"
    ])
]

results = {}

for group_name, paths in datasets:
    all_f = []
    all_conf = []
    for p in paths:
        if not Path(p).exists():
            continue
        d = read_npz(p)
        f = d.get('f', d.get('f0', []))
        c = d.get('conf', [60.0]*len(f))
        all_f.extend(f)
        all_conf.extend(c)
    
    valid_f = [f for f, c in zip(all_f, all_conf) if c > 50.0 and 100 < f < 900]
    if not valid_f:
        continue
    
    # Analyze pitch pitch classes modulo 1200 relative to estimated tonic
    # Find tonic: kernel density on pitch class
    # For Abuata / Shur, find the main Ist
    # Let's find prominent cluster peaks
    ref_hz = 220.0
    all_cents = [1200.0 * math.log2(f / ref_hz) for f in valid_f]
    
    # histogram 0..1200 relative to base peak
    # first find dominant base peak (Ist/Tonic)
    pc_bins = defaultdict(int)
    for c in all_cents:
        pc = round((c % 1200.0) / 10.0) * 10.0
        pc_bins[pc] += 1
    
    # Sort top peaks
    sorted_peaks = sorted(pc_bins.items(), key=lambda x: x[1], reverse=True)
    tonic_pc = sorted_peaks[0][0]
    
    # Re-reference all pitches relative to tonic_pc (0 to 1200 cents)
    rel_cents = [((c - tonic_pc) % 1200.0) for c in all_cents]
    
    # Collect degree distributions around canonical intervals:
    # 2nd koron (Re_k / Mi_k relative to local ist): 120-170 cents
    # minor 3rd: 270-320 cents
    # Zalzal neutral 3rd: 330-365 cents
    # 4th: 480-520 cents
    # neutral 5th: 630-670 cents
    # 5th: 690-720 cents
    # neutral 6th (La_k): 800-870 cents
    # minor 7th: 980-1030 cents
    
    deg_windows = {
        "neutral_2nd (Re_k)": (120, 175),
        "minor_3rd (Fa/Sol)": (270, 315),
        "zalzal_neutral_3rd (Mi_k)": (325, 365),
        "fourth": (480, 520),
        "motaghayyer_5th (Sol_k)": (630, 675),
        "pure_fifth": (690, 720),
        "neutral_6th (La_k)": (800, 875),
        "minor_7th": (980, 1030)
    }
    
    deg_stats = {}
    for deg_name, (low, high) in deg_windows.items():
        vals = [c for c in rel_cents if low <= c <= high]
        if len(vals) >= 10:
            vals.sort()
            med = vals[len(vals)//2]
            deg_stats[deg_name] = {
                "median": round(med, 1),
                "count": len(vals)
            }
        else:
            deg_stats[deg_name] = {"median": None, "count": len(vals)}
            
    results[group_name] = {
        "total_valid_strikes": len(valid_f),
        "degrees": deg_stats
    }

print(json.dumps(results, indent=2))
with open('analysis/lotfi_saba_fretted_vs_fretless_summary.json', 'w') as f:
    json.dump(results, f, indent=2)
