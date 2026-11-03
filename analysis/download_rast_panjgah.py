#!/usr/bin/env python3
"""Download the Grand Dastgah-e Rast-Panjgah Corpus across 12 canonical masters
for cross-instrument modal pitch and dāng transition analysis."""

import os
import subprocess
from pathlib import Path

BASE = Path("audio/YouTube Music")
YTDLP = "/opt/homebrew/bin/yt-dlp"

DOWNLOADS = [
    # 1. Nur-Ali Borumand (Tar & Setar - The Mirza Abdollah Radif Vol. 7)
    ("Nur-Ali Borumand/Radif Mirza Abdollah - Rast-Panjgah", [
        ("iqplw8fBU08", "01 - Rast-Panjgah Daramad I-Rast"),
        ("pXQnbr3zivQ", "02 - Rast-Panjgah Panjgah"),
        ("K4zKOeCxc8A", "03 - Rast-Panjgah Naghme"),
        ("X7cY9wn1yQ8", "04 - Rast-Panjgah Khosravani"),
        ("SYXf9haVw1c", "05 - Rast-Panjgah Mobarqa"),
        ("7wY1RBy5lF8", "06 - Rast-Panjgah Oshshaq"),
        ("oCuor8jC2bA", "07 - Rast-Panjgah Neyriz"),
        ("jwmOxdqbr20", "08 - Rast-Panjgah Sepehr"),
    ]),

    # 2. Ali-Akbar Shahnazi (Tar - The Aqa Hoseyn-Qoli Radif Vol. 6)
    ("Ali-Akbar Shahnazi/Radif Tar - Rast-Panjgah", [
        ("pVt2rXMZiFY", "01 - Rast-Panjgah Daramad"),
        ("1ulAM2udbIM", "02 - Rast-Panjgah Panjgah"),
        ("lgtxhri1WXg", "03 - Rast-Panjgah Naghme"),
        ("ltPmgQ7kKcA", "04 - Rast-Panjgah Mobarqa"),
        ("YhzY6Bs9D6M", "05 - Rast-Panjgah Oshshaq"),
        ("hEnxMe3Igec", "06 - Rast-Panjgah Neyriz Saghir"),
        ("PfUwmF7Dy-g", "07 - Rast-Panjgah Sepehr"),
    ]),

    # 3. Mahmud Karimi (Vocal - The Karimi Vocal Radif Vol. 3)
    ("Mahmud Karimi/Vocal Radif - Rast-Panjgah", [
        ("tO39rYV8gf8", "01 - Rast-Panjgah Daramad"),
        ("U_XnZySpPFA", "02 - Rast-Panjgah Panjgah Sepehr"),
        ("A_rCCMkcMJc", "03 - Rast-Panjgah Naghme"),
        ("OzSgwkZOPvs", "04 - Rast-Panjgah Ruhafza"),
        ("I62CiU2r-VQ", "05 - Rast-Panjgah Oshshaq"),
        ("TBZqQI1Sayw", "06 - Rast-Panjgah Neyriz"),
    ]),

    # 4. Hossein Alizadeh (Tar & Setar Radif Navazi)
    ("Hossein Alizadeh/Radif Navazi - Rast-Panjgah", [
        ("StMjZ2wqzGU", "01 - Rast-Panjgah Daramad"),
        ("Wt9WcDX6ZAE", "02 - Rast-Panjgah Panjgah"),
        ("iBd2MW4M5hQ", "03 - Rast-Panjgah Naghmeh"),
        ("iyfA_B6xc_8", "04 - Rast-Panjgah Oshagh"),
        ("zO-YALmWVj8", "05 - Rast-Panjgah Neyriz"),
        ("3XNYUJqcyPQ", "06 - Rast-Panjgah Khosravani"),
    ]),

    # 5. Mansour Nariman (Oud Radif - Dastgahe Rastpanjgah)
    ("Mansour Nariman/Radif Oud - Rast-Panjgah", [
        ("TKhSLYDInv4", "01 - Moghadame"),
        ("lcu5msKajdA", "02 - Panjgah"),
        ("eID88iFiZg4", "03 - Oshagh"),
        ("yOZPVQuznuw", "04 - Neyriz"),
        ("dcZXVaJWsF8", "05 - Sepehr"),
    ]),

    # 6. Morteza Neydavud (Tar Radif)
    ("Morteza Neydavud/Radif Tar - Rast-Panjgah", [
        ("kBa5UcOZX5k", "01 - Panjgah"),
        ("Q5bCYvzfw5s", "02 - Naghme"),
        ("zjb8P2mjoCs", "03 - Oshshaq"),
        ("v_GazJaXbyw", "04 - Neyriz"),
        ("DY_r2PYau9U", "05 - Mobarqa and Sepehr"),
    ]),

    # 7. Aliakbar Shekarchi (Kamancheh Radif)
    ("Aliakbar Shekarchi/Radif Kamancheh - Rast-Panjgah", [
        ("gIIyPGkRP98", "01 - Daramad Pt 1 Rast"),
        ("XgGaHfMM2A4", "02 - Panj Gah"),
        ("qanQNvjTABA", "03 - Naghmeh"),
        ("SogbEGbKWCU", "04 - Oshagh Froud"),
        ("wOnUG5qVnn4", "05 - Neyriz"),
        ("XuVD6f4ScQw", "06 - Sepehr"),
    ]),

    # 8. Hassan Kasaei (Ney)
    ("Hassan Kasaei/Ney - Rast-Panjgah", [
        ("f6bTZCzshu0", "01 - Daramad"),
        ("Vmp0BgCJmyQ", "02 - Feyli 5Gaah"),
        ("2irnFIOB238", "03 - Khosravani"),
        ("WzZulfyqhpo", "04 - Neyriz"),
        ("lkwPlBm8CRs", "05 - Leili o Majnoon"),
    ]),

    # 9. Jalil Shahnaz (Tar)
    ("Jalil Shahnaz/Tar Solo - Rast-Panjgah", [
        ("V7aRDm_wTsg", "01 - Daramad Naghmeh"),
        ("24ZhRrHYHko", "02 - Panjgah Sepehr"),
        ("iy1XzhDdaFA", "03 - Neyriz"),
        ("GCESp7d1j2k", "04 - Zarbi-Ye Zanguleh Naghmeh"),
    ]),

    # 10. Ahmad Ebadi (Setar)
    ("Ahmad Ebadi/Setar Solo - Rast-Panjgah", [
        ("tE8c_jDYdFk", "01 - Rastpanjgah Solo Setar"),
    ]),

    # 11. Abolhasan Saba (Violin)
    ("Abolhasan Saba/Violin - Rast-Panjgah", [
        ("YEt3prm3N0M", "01 - Dastgah Rast-Panjgah"),
    ]),

    # 12. Mohammad Reza Lotfi (Tar)
    ("Mohammad Reza Lotfi/Tar - Rast-Panjgah", [
        ("1YyLTGuk8n4", "01 - Rast Panjgah chahar mezrab"),
    ]),
]

def download_track(out_dir: Path, ytid: str, title: str):
    out_dir.mkdir(parents=True, exist_ok=True)
    m4a_path = out_dir / f"{title}.m4a"
    wav_path = out_dir / f"{title}.wav"
    
    if wav_path.exists():
        print(f"  [OK] Exists: {wav_path.name}")
        return
        
    print(f"  [DL] Downloading {title} ({ytid})...")
    url = f"https://www.youtube.com/watch?v={ytid}"
    cmd = [
        YTDLP,
        "-x",
        "--audio-format", "m4a",
        "-o", str(m4a_path),
        url
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"  [ERR] Failed to download {ytid}: {res.stderr[:200]}")
        return

    # Convert to standard 44.1 kHz WAV
    print(f"  [WAV] Converting to {wav_path.name}...")
    conv_cmd = [
        "ffmpeg", "-y", "-i", str(m4a_path),
        "-ar", "44100", "-ac", "1",
        str(wav_path)
    ]
    subprocess.run(conv_cmd, capture_output=True, check=True)
    print(f"  [DONE] {wav_path.name}")

def main():
    print(f"=== Starting Grand Dastgah-e Rast-Panjgah Corpus Download ===")
    total = sum(len(tracks) for _, tracks in DOWNLOADS)
    print(f"Target: {len(DOWNLOADS)} masters, {total} canonical tracks/gushehs.\n")
    
    count = 0
    for folder_rel, tracks in DOWNLOADS:
        out_dir = BASE / folder_rel
        print(f"\nMaster: {folder_rel}")
        for ytid, title in tracks:
            count += 1
            print(f"[{count}/{total}]", end=" ")
            download_track(out_dir, ytid, title)

if __name__ == "__main__":
    main()
