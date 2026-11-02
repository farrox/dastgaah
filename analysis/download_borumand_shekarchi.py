import os
import subprocess
from pathlib import Path

BASE = Path("audio/YouTube Music")
YTDLP = "/opt/homebrew/bin/yt-dlp"

DOWNLOADS = [
    # Aliakbar Shekarchi (Kamancheh - Esfahan Radif)
    ("Aliakbar Shekarchi/Radif Kamancheh - Esfahan", [
        ("6oyWj0IaWE0", "01 - Daramad"),
        ("tj22iOIwcbs", "02 - Jameh Daran"),
        ("p1moQnLS6jk", "03 - Bayat Rajeh"),
        ("_rzJ9UFFDVA", "04 - Naghmeh"),
        ("k-lx1R7yvck", "05 - Souz o Godaz"),
    ]),
    # Nur-Ali Borumand (The Mirza Abdollah Radif - Esfahan & Homayun)
    ("Nur-Ali Borumand/Radif Tar Setar - Esfahan", [
        ("XGhYDRHodDM", "01 - Bayat-e Esfahan Daramad"),
        ("bd6LAjDYBok", "02 - Bayat-e Esfahan Kereshme"),
        ("t7K2Z_oXPKs", "03 - Bayat-e Esfahan Jamedaran"),
        ("yxyYp2N0e5g", "04 - Bayat-e Esfahan Bayat-e Raje"),
        ("SbtlCZiTqks", "05 - Bayat-e Esfahan Suz-o Godaz"),
        ("VbpZ2pRcYHY", "06 - Bayat-e Esfahan Forud"),
    ]),
    ("Nur-Ali Borumand/Radif Tar Setar - Homayun", [
        ("QgvXbKLKJu4", "01 - Homayun Daramad I"),
        ("dU9xQib-fuo", "02 - Homayun Daramad II"),
        ("zkbfdu5f330", "03 - Homayun Chaharmezrab"),
        ("ptnrVV-zDXk", "04 - Homayun Chakavak"),
        ("sCjA8mYf0rU", "05 - Homayun Bidad"),
        ("8akTckz24Yk", "06 - Homayun Bidad-e Kot"),
        ("he3GnOhH9KY", "07 - Homayun Shushtari"),
        ("qw62D6NHtmE", "08 - Homayun Bakhtiyari Ba Moalef"),
        ("BhnCt4Lv1Xs", "09 - Homayun Reng-e Farah"),
    ]),
    # Ali-Akbar Shahnazi (Radif Tar - Esfahan)
    ("Ali-Akbar Shahnazi/Radif Tar - Esfahan", [
        ("CGe_VOnSb1w", "01 - Avaz-e Esfahan Rohab I"),
        ("6HEN-rIx0KM", "02 - Avaz-e Esfahan Rohab II"),
        ("NyvpZIXT9MA", "03 - Avaz-e Esfahan Bayat-e Raje"),
        ("xYlC-dwpT8w", "04 - Avaz-e Esfahan Chaharmezrab"),
        ("SRTAmLq00_g", "05 - Avaz-e Esfahan Oshshaq, Forud"),
        ("PwAQxusLaOg", "06 - Avaz-e Esfahan Gushe-ha-ye Afshari"),
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
