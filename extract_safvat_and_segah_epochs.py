import sys, glob, json, math, os, subprocess
from pathlib import Path
sys.path.insert(0, 'analysis')
from extract_upgraded_strikes import extract_single_wav, ensure_dylib, save_npz_pure

ensure_dylib()

# 1. Process downloaded Safvat & Sarvestani tracks
safvat_dir = Path("audio/Safvat_and_Sarvestani_Rare")
safvat_wavs = sorted(safvat_dir.glob("*.wav"))
print(f"--- Extracting {len(safvat_wavs)} Safvat & Sarvestani tracks ---")
for w in safvat_wavs:
    stem = w.stem
    npz_path = Path(f"analysis/strikes_{stem}.npz")
    if npz_path.exists():
        print(f"Exists: {npz_path.name}")
        continue
    print(f"Extracting {stem}...")
    res = extract_single_wav(str(w), stem, 100.0, 950.0)
    print(f"  Strikes: {len(res['f'])}")
    npz_data = {
        "t": (res["t"], "f8"),
        "f": (res["f"], "f8"),
        "conf": (res["conf"], "f8"),
        "wobble_plat_c": (res["wobble_plat_c"], "f8"),
        "wobble_sus_c": (res["wobble_sus_c"], "f8"),
        "drift_c_per_s": (res["drift_c_per_s"], "f8"),
        "attack_bend_c": (res["attack_bend_c"], "f8"),
    }
    save_npz_pure(npz_path, npz_data)

# 2. Select key Segah tracks from Yousef Foroutan and Saeed Hormozi
segah_targets = [
    # Yousef Foroutan
    ("audio/Yusef Foroutan/053 - Segah： Zabol, Zarbi.m4a", "foroutan_segah_zabol"),
    ("audio/Yusef Foroutan/045 - Segah： Muyeh.m4a", "foroutan_segah_muye"),
    ("audio/Yusef Foroutan/035 - Segah： Mokhalef, Hazin, Masnavi-ye Mokhalef.m4a", "foroutan_segah_mokhalef"),
    # Saeed Hormozi
    ("audio/Saeed Hormozi/Radif_Vol_1/34 - Segah： Zabol.m4a", "hormozi_segah_zabol"),
    ("audio/Saeed Hormozi/Radif_Vol_1/35 - Segah： Muye.m4a", "hormozi_segah_muye"),
    ("audio/Saeed Hormozi/Radif_Vol_1/36 - Segah： Mokhalef & Chaharmezrab Mokhalef, Maghlub & Naghmeye Maghlub.m4a", "hormozi_segah_mokhalef")
]

tmp_dir = Path("tmp_segah_wavs")
tmp_dir.mkdir(exist_ok=True)

print(f"\n--- Extracting {len(segah_targets)} Diachronic Segah tracks (Foroutan & Hormozi) ---")
for in_m4a, tag in segah_targets:
    p = Path(in_m4a)
    if not p.exists():
        print(f"File missing: {in_m4a}")
        continue
    npz_path = Path(f"analysis/strikes_{tag}.npz")
    if npz_path.exists():
        print(f"Exists: {npz_path.name}")
        continue
    wav_path = tmp_dir / f"{tag}.wav"
    if not wav_path.exists():
        subprocess.run(["ffmpeg", "-y", "-i", str(p), "-ar", "44100", "-ac", "1", str(wav_path)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"Extracting {tag}...")
    res = extract_single_wav(str(wav_path), tag, 100.0, 950.0)
    print(f"  Strikes: {len(res['f'])}")
    npz_data = {
        "t": (res["t"], "f8"),
        "f": (res["f"], "f8"),
        "conf": (res["conf"], "f8"),
        "wobble_plat_c": (res["wobble_plat_c"], "f8"),
        "wobble_sus_c": (res["wobble_sus_c"], "f8"),
        "drift_c_per_s": (res["drift_c_per_s"], "f8"),
        "attack_bend_c": (res["attack_bend_c"], "f8"),
    }
    save_npz_pure(npz_path, npz_data)

print("\nAll extractions complete!")
