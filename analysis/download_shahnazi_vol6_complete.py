#!/usr/bin/env python3
"""Download all 36 canonical Rast-Panjgah tracks from Ali-Akbar Shahnazi's
definitive album: 'The Aqa Hoseyn-Qoli Radif, Vol. 6'."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

BASE = Path("audio/YouTube Music/Ali-Akbar Shahnazi/The Aqa Hoseyn-Qoli Radif, Vol. 6 - Rast-Panjgah")
YTDLP = "/opt/homebrew/bin/yt-dlp"

TRACKS = [
    ("pVt2rXMZiFY", "01 - Rast-Panjgah Daramad"),
    ("XcLjvWeY-0w", "02 - Rast-Panjgah Chaharmezrab"),
    ("l3Ql-9xggKA", "03 - Rast-Panjgah Zang Shotor or Naqus"),
    ("lgtxhri1WXg", "04 - Rast-Panjgah Naghme"),
    ("V50sZ59TDQM", "05 - Rast-Panjgah Ruhafza"),
    ("5CBkATx5MNc", "06 - Rast-Panjgah Parvane"),
    ("1ulAM2udbIM", "07 - Rast-Panjgah Panjgah"),
    ("YhzY6Bs9D6M", "08 - Rast-Panjgah Oshshaq"),
    ("IEl3wpkxuaQ", "09 - Rast-Panjgah Zabol"),
    ("_w9UB9s5VRI", "10 - Rast-Panjgah Bayat Ajam"),
    ("9M-vP8KZqWI", "11 - Rast-Panjgah Bahre Nur"),
    ("e1Z25108q6s", "12 - Rast-Panjgah Mansuri"),
    ("ltPmgQ7kKcA", "13 - Rast-Panjgah Mobarqa"),
    ("PfUwmF7Dy-g", "14 - Rast-Panjgah Sepehr"),
    ("fm0lJNUrIxk", "15 - Rast-Panjgah Araq"),
    ("W4A_1wfLqRQ", "16 - Rast-Panjgah Mohayyer"),
    ("HD1a24D4Zv4", "17 - Rast-Panjgah Ashuravand"),
    ("_LMwMPd28j4", "18 - Rast-Panjgah Esfahanak"),
    ("C3yI7h8rbr0", "19 - Rast-Panjgah Hazin"),
    ("-Mx2aIf_v_M", "20 - Rast-Panjgah Zangule"),
    ("kLYvNNnAJOo", "21 - Rast-Panjgah Nowruz Arab"),
    ("xgIo31vuLdc", "22 - Rast-Panjgah Nowruz Saba"),
    ("Y1DlRfPFvCM", "23 - Rast-Panjgah Nowruz Khara"),
    ("9WQrLXCbr-A", "24 - Rast-Panjgah Nafir"),
    ("ZLGOcQ1Y-UE", "25 - Rast-Panjgah Abolchap"),
    ("804DD5u5JSY", "26 - Rast-Panjgah Ravandi"),
    ("2TEDOanGpIU", "27 - Rast-Panjgah Leyli-O Majnun"),
    ("fHekBE6pmPk", "28 - Rast-Panjgah Tarz"),
    ("gz7PhDHrKTY", "29 - Rast-Panjgah Parvane I"),
    ("qfAI0hS8p2U", "30 - Rast-Panjgah Mavara-on-Nahr"),
    ("F34xweT1CLE", "31 - Rast-Panjgah Rak Abdollah"),
    ("-jHza93HJGI", "32 - Rast-Panjgah Rak Hendi"),
    ("kT4BCFv13x0", "33 - Rast-Panjgah Parvane II"),
    ("hEnxMe3Igec", "34 - Rast-Panjgah Neyriz Saghir"),
    ("tHUdPmVcOpA", "35 - Rast-Panjgah Neyriz Kabir"),
    ("kRU22eS5OuE", "36 - Rast-Panjgah Parvane III"),
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

    print(f"  [WAV] Converting to {wav_path.name}...")
    conv_cmd = [
        "/opt/homebrew/bin/ffmpeg", "-y", "-i", str(m4a_path),
        "-ar", "44100", "-ac", "1",
        str(wav_path)
    ]
    subprocess.run(conv_cmd, capture_output=True, check=True)
    print(f"  [DONE] {wav_path.name}")

def main():
    print(f"=== Downloading Ali-Akbar Shahnazi Complete Radif Vol. 6 (Rast-Panjgah) ===")
    print(f"Target: {len(TRACKS)} canonical gūshehs.\n")
    for idx, (ytid, title) in enumerate(TRACKS, 1):
        print(f"[{idx}/{len(TRACKS)}]", end=" ")
        download_track(BASE, ytid, title)

if __name__ == "__main__":
    main()
