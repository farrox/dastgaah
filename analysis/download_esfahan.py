import os
import subprocess
from pathlib import Path

BASE = Path("audio/YouTube Music")

# Group targets by artist directory
DOWNLOADS = [
    # Morteza Neydavud (Tar)
    ("Morteza Neydavud/Radif Tar - Esfahan", [
        ("oKdPWWuqHLM", "01 - Avaz Bayat Esfahan"),
        ("lgW5sPURAYo", "02 - Esfahan, Oshagh"),
        ("6EypOMUNYZk", "03 - Tasnif-o-Reng, Esfahan"),
    ]),
    # Ahmad Ebadi (Setar)
    ("Ahmad Ebadi/Setar Solo - Esfahan", [
        ("Vz4TAxvBXhM", "01 - Bayat-e Esfahan"),
    ]),
    # Jalil Shahnaz (Tar)
    ("Jalil Shahnaz/Tar Solo - Esfahan", [
        ("tqKFHVb72ZQ", "01 - Esfahan"),
        ("iiThP6_hLdU", "02 - Romantic Esfahan"),
        ("ZxKv9rKKaV0", "03 - Improvisation in Bayat Esfahan"),
    ]),
    # Gholam-Hoseyn Bigjekhani (Tar - Tabriz lineage)
    ("Gholamhosein Bigjekhani/Tar - Esfahan", [
        ("Wgew0zGJYHE", "01 - Bayat Esfahan"),
        ("N4-OB_Zj5EA", "02 - Avaz-e Bayat-e Esfahan I"),
    ]),
    # Ali-Asghar Bahari (Kamancheh - Fretless Master)
    ("Ali-Asghar Bahari/Kamancheh - Esfahan", [
        ("hcZV5XTGfrc", "01 - Kamancheh Bayat Esfahan"),
    ]),
    # Mehdi Kamalian (Setar)
    ("Mehdi Kamalian/Setar - Esfahan", [
        ("ZmV57DT3YOU", "01 - Bayate Esfahan"),
    ]),
    # Sa'id Hormozi (Setar)
    ("Saeed Hormozi/Setar - Esfahan", [
        ("W9IkTYrsC-I", "01 - Bayat Esfahan Chaharmezrab, Daramad"),
    ]),
]

def main():
    success = 0
    fail = 0
    for rel_dir, tracks in DOWNLOADS:
        out_dir = BASE / rel_dir
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n=== Target: {out_dir} ===", flush=True)
        for vid, title in tracks:
            out_wav = out_dir / f"{title}.wav"
            if out_wav.exists() and out_wav.stat().st_size > 100000:
                print(f"Already exists: {out_wav.name} ({out_wav.stat().st_size:,} bytes)", flush=True)
                success += 1
                continue
            url = f"https://www.youtube.com/watch?v={vid}"
            cmd = [
                "python3", "-m", "yt_dlp",
                "--extractor-args", "youtube:player_client=android",
                "-x",
                "--audio-format", "wav",
                "--ffmpeg-location", "/opt/homebrew/bin/ffmpeg",
                "-o", str(out_dir / f"{title}.%(ext)s"),
                url
            ]
            print(f"Downloading {vid} -> {out_wav.name}...", flush=True)
            res = subprocess.run(cmd)
            if res.returncode == 0 and out_wav.exists() and out_wav.stat().st_size > 100000:
                print(f"  ✓ Successfully downloaded {title}.wav ({out_wav.stat().st_size:,} bytes)", flush=True)
                success += 1
            else:
                print(f"  ✗ Failed downloading {vid}", flush=True)
                fail += 1

    print(f"\nSummary: {success} succeeded, {fail} failed.")

if __name__ == "__main__":
    main()
