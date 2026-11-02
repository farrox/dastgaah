import os
import subprocess
from pathlib import Path

BASE = Path("audio/YouTube Music")
YTDLP = "/opt/homebrew/bin/yt-dlp"

NEW_DOWNLOADS = [
    # Hossein Alizadeh (Setar - Radif Navazi Bayat-e Esfahan)
    ("Hossein Alizadeh/Radif Navazi - Esfahan", [
        ("NTPnadiaxw0", "01 - Bayat Esfahan Daramad"),
        ("iEIMOfWJYgk", "02 - Bayat Esfahan Jamehdaran"),
        ("Y5oKEDIASY0", "03 - Bayat Esfahan Bayat Raje Pt 1"),
        ("U47bkfFcWTc", "04 - Bayat Esfahan Suz-o Godaz"),
        ("rDmnUoB3g5w", "05 - Bayat Esfahan Forud"),
    ]),
    # Yousef Foroutan (Setar - Radif Bayat-e Esfahan)
    ("Yusef Forutan/Radif Setar - Esfahan", [
        ("gWPzOuIqG4c", "01 - Pishdaramad-e Bayat-e Esfahan"),
        ("Ay_Viyy8Tp4", "02 - Bayat Esfahan Bayat-e Raje"),
        ("zkpgqcfmLEs", "03 - Bayat Esfahan Oshshaq Busalik Chaharmezrab"),
        ("KKKuh7H8Ipk", "04 - Bayat Esfahan Sufiname"),
        ("IUC9RCz9HWU", "05 - Reng-e Bayat-e Esfahan"),
    ]),
    # Abolhasan Saba (Setar / Violin - Bayat-e Esfahan)
    ("Abolhasan Saba/Radif - Esfahan", [
        ("GzHWnxS9Y_Y", "01 - Bayat-e-Esfahan"),
        ("Y-d5jQmL-xw", "02 - Avaz Bayat Esfahan"),
        ("H8UpxYNouHg", "03 - Avaz Bayat Esfahan ft Tehrani"),
        ("kb5WphlDLj8", "04 - Zang-e-Esfahan"),
    ]),
    # Dariush Tala'i (Tar / Setar - Radif Bayat-e Esfahan)
    ("Dariush Talai/Radif - Esfahan", [
        ("Cb7jtQvzmfU", "01 - Avaz-e Bayat-e Esfahan"),
        ("InVGmE11XOs", "02 - Improvisation in Bayat-e Esfahan"),
    ]),
    # Mohammad Reza Lotfi (Setar & Tar - Bayat-e Esfahan)
    ("Mohammad Reza Lotfi/Solo - Esfahan", [
        ("flH7sOhVuYY", "01 - Tar Solo Bayat Esfahan"),
        ("EcnNU7Zhyo8", "02 - Setar Solo Bayate Esfahan"),
    ]),
    # Hassan Kasaei (Ney / Setar - Bayat-e Esfahan)
    ("Hassan Kasaei/Solo - Esfahan", [
        ("3LlYAhml4Io", "01 - Bayat Esfahan Part 1"),
        ("_KkijdPsYog", "02 - Bayat Esfahan Oshagh"),
        ("nhgI4UCiKbI", "03 - Bayat Esfahan Naghmeh"),
    ]),
    # Mansour Nariman (Oud - Radif Oud Esfahan)
    ("Mansour Nariman/Radif Oud - Esfahan", [
        ("8fT4ZzX4B-U", "01 - Avaze Esfahan Moghadame"),
        ("_jGFPfosPB4", "02 - Daramade Aval Esfahan"),
        ("NMqNpOr6ErY", "03 - Chaharmezrabe Esfahan"),
        ("lOr7_XAUBkk", "04 - Goosheye Oshagh Esfahan"),
        ("_ADMw7nKunA", "05 - Forood Esfahan"),
    ]),
    # Mahmoud Karimi (Vocal - Radif Esfahan)
    ("Mahmud Karimi/Vocal Radif - Esfahan", [
        ("0gibwoPWYKQ", "01 - Bayat-e Esfahan Naghme"),
        ("6FhyLUJqKnk", "02 - Vocal Radif Bayat Esfahan Complete"),
    ]),
]

def main():
    success = 0
    fail = 0
    for rel_dir, tracks in NEW_DOWNLOADS:
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
                YTDLP,
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

