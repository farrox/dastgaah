import subprocess, os, sys
from pathlib import Path
sys.path.insert(0, 'analysis')
from extract_upgraded_strikes import extract_single_wav, ensure_dylib, save_npz_pure

ensure_dylib()

in_dir = Path("audio/Hossein_Ali_Khan_Taherzadeh_Qajar_Shellac")
wav_dir = Path("audio/Hossein_Ali_Khan_Taherzadeh_Qajar_Shellac/wav")
wav_dir.mkdir(exist_ok=True)

m4as = sorted(in_dir.glob("*.m4a"))
print(f"Transcoding & extracting {len(m4as)} Taherzadeh 1907-1909 Qajar Shellac tracks...")

for m4a in m4as:
    stem = m4a.stem
    wav_path = wav_dir / f"{stem}.wav"
    if not wav_path.exists():
        subprocess.run(["ffmpeg", "-y", "-i", str(m4a), "-ar", "44100", "-ac", "1", str(wav_path)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    npz_path = Path(f"analysis/strikes_taherzadeh_{stem}.npz")
    if npz_path.exists():
        print(f"Exists: {npz_path.name}")
        continue
        
    print(f"Extracting {stem}...")
    res = extract_single_wav(str(wav_path), stem, 110.0, 800.0)
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

print("All Taherzadeh Shellac tracks extracted!")
