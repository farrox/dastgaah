#!/usr/bin/env python3
"""Download the newly provided gems:
1. Saeed Hormozi - Setar in Shur (N7tUktKwlfo)
2. Saeed Hormozi - Setar in Afshari (tNtl9tQrYHA)
3. Saeed Hormozi - Setar in Rast-Panjgah (min 27 extracted, D3yw9TIAYVI)
4. Saeed Hormozi - Setar in Bayat-e Esfahan (00ZN3XAOzfU)
5. Hossein Alizadeh - The Art of Improvisation in Rast-Panjgah (Complete 15-track Radio France album)
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

BASE = Path("audio/YouTube Music")
YTDLP = "/opt/homebrew/bin/yt-dlp"

DOWNLOAD_SETS = [
    # 1. Saeed Hormozi - Solo Setar Curated Gems
    ("Saeed Hormozi/Setar - Shur Solo", [
        ("N7tUktKwlfo", "01 - Saeed Hormozi Setar Shur"),
    ]),
    ("Saeed Hormozi/Setar - Afshari Solo", [
        ("tNtl9tQrYHA", "01 - Saeed Hormozi Setar Afshari"),
    ]),
    ("Saeed Hormozi/Setar - Rast Panjgah", [
        ("D3yw9TIAYVI", "01 - Saeed Hormozi Setar Rast Panjgah"),
    ]),
    ("Saeed Hormozi/Setar - Esfahan Solo", [
        ("00ZN3XAOzfU", "01 - Saeed Hormozi Setar Esfahan Recital"),
    ]),

    # 2. Hossein Alizadeh - The Art of Improvisation (Rast-Panjgah, Radio France Ocora 1993)
    ("Hossein Alizadeh/The Art Of Improvisation - Rast-Panjgah", [
        ("E2d2WavgQc8", "01 - Daramad"),
        ("0dyga44pl-A", "02 - Parvaneh"),
        ("4G3OG8LBjhk", "03 - Nahmeh"),
        ("uOzKwuEG7AE", "04 - Ruh Afza"),
        ("Bao5goQhBF4", "05 - Khosravani"),
        ("0mYr8S4afUo", "06 - Eraq"),
        ("OYdScwAvUXg", "07 - Zarbi-E Eraq Neyshaburak"),
        ("eED_wVNhgRs", "08 - Hazin Nahib Mohayyer Ashuraband"),
        ("9-2RlPjGFII", "09 - Suz-O-Godaz"),
        ("EgUZ0EqHQdg", "10 - Leyli-O-Majnun"),
        ("VfW66U7p2-o", "11 - Zarbi-E Shushtari Esfahan"),
        ("RHWC8qamFcY", "12 - Odj Abou-Ata"),
        ("FQ4pDX52vEU", "13 - Tchaharmezrab"),
        ("gJo7BRvR808", "14 - Forud Sepehr Parvaneh"),
        ("U-sg-uIbDo4", "15 - Avaz-E Bayat-E Kord"),
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

    print(f"  [WAV] Converting to {wav_path.name}...")
    conv_cmd = [
        "/opt/homebrew/bin/ffmpeg", "-y", "-i", str(m4a_path),
        "-ar", "44100", "-ac", "1",
        str(wav_path)
    ]
    subprocess.run(conv_cmd, capture_output=True, check=True)
    print(f"  [DONE] {wav_path.name}")

    # Special handling for Hormozi Rast-Panjgah which starts around min 27 (1620s)
    if "Rast Panjgah" in title and ytid == "D3yw9TIAYVI":
        trimmed_wav = out_dir / "01 - Saeed Hormozi Setar Rast Panjgah (Min 27 Onwards).wav"
        print(f"  [TRIM] Slicing Rast-Panjgah section from min 27...")
        trim_cmd = [
            "/opt/homebrew/bin/ffmpeg", "-y", "-ss", "00:27:00", "-i", str(wav_path),
            "-ar", "44100", "-ac", "1", str(trimmed_wav)
        ]
        subprocess.run(trim_cmd, capture_output=True, check=True)
        print(f"  [DONE] Created: {trimmed_wav.name}")

def main():
    print(f"=== Downloading Saeed Hormozi Masteries & Alizadeh Rast-Panjgah ===")
    total = sum(len(tracks) for _, tracks in DOWNLOAD_SETS)
    print(f"Target: {len(DOWNLOAD_SETS)} sets, {total} canonical tracks.\n")
    
    count = 0
    for folder_rel, tracks in DOWNLOAD_SETS:
        out_dir = BASE / folder_rel
        print(f"\nTarget: {folder_rel}")
        for ytid, title in tracks:
            count += 1
            print(f"[{count}/{total}]", end=" ")
            download_track(out_dir, ytid, title)

if __name__ == "__main__":
    main()
