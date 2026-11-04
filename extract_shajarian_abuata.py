import subprocess, sys, os
from pathlib import Path
sys.path.insert(0, 'analysis')
from extract_upgraded_strikes import extract_single_wav, ensure_dylib, save_npz_pure

ensure_dylib()

# Find Abuata tracks in Shajarian folder
in_dir = Path("audio/Mohammad_Reza_Shajarian_Radif_Avazi")
tmp_wav_dir = Path("audio/Mohammad_Reza_Shajarian_Radif_Avazi/wav")
tmp_wav_dir.mkdir(exist_ok=True)

abuata_m4as = sorted([p for p in in_dir.glob("*.m4a") if "ابوعطا" in p.name])
print(f"Found {len(abuata_m4as)} Shajarian Abuata master tracks:")
for m in abuata_m4as:
    print(f"  - {m.name}")

for m in abuata_m4as:
    stem = m.stem
    wav_path = tmp_wav_dir / f"{stem}.wav"
    if not wav_path.exists():
        subprocess.run(["ffmpeg", "-y", "-i", str(m), "-ar", "44100", "-ac", "1", str(wav_path)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    npz_path = Path(f"analysis/strikes_shajarian_{stem}.npz")
    if npz_path.exists():
        print(f"Exists: {npz_path.name}")
        continue
    print(f"Extracting {stem}...")
    res = extract_single_wav(str(wav_path), stem, 110.0, 750.0)
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

print("All Shajarian Abuata tracks extracted!")
