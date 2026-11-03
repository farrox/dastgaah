#!/usr/bin/env python3
"""Download the 6 user-provided Rast-Panjgah recordings/playlists:
1. Hassan Kasaei - Iranian Classical Music Radifs 5 (Ney Rast-Panjgah complete set)
2. Mohammadreza Shajarian & Mohammad Reza Lotfi - Cheshmeye Noush (Live Rast-Panjgah album)
3. Sanam Gharacheh - Historical 1927-1929 Rast-Panjgah (Collection of Iranian Music 18)
4. Seyed Ahmadkhan - Historical 1907-1912 Shellac Rast-Panjgah (Collection of Iranian Music 13)
5. Morteza Neydavud - Complete Tar Radif Rast-Panjgah (Radif on Tar, Vol. 5)
6. Abolhasan Saba - Dastgah Rast-Panjgah (Violin, Vol. 3)
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

BASE = Path("audio/YouTube Music")
YTDLP = "/opt/homebrew/bin/yt-dlp"

DOWNLOAD_SETS = [
    # 1. Hassan Kasaei - Radifs 5 (All 19 Rast-Panjgah Ney Tracks)
    ("Hassan Kasaei/Iranian Classical Music Radifs 5 - Rast Panjgah", [
        ("0ecw6QR7qYU", "01 - Rast Panjgah"),
        ("f6bTZCzshu0", "02 - Rast Panjgah Daramad"),
        ("6vZPlYFBF90", "03 - Rast Panjgah Parvaneh"),
        ("WzZulfyqhpo", "04 - Rast Panjgah Neyriz"),
        ("INNTTwupIs4", "05 - Rast Panjgah Majles Afrooz"),
        ("hp_aj5KxN40", "06 - Rast Panjgah Zang-e Shotor"),
        ("5D3yuLX6gus", "07 - Rast Panjgah Goshayesh"),
        ("2irnFIOB238", "08 - Rast Panjgah Khosravani"),
        ("Vmp0BgCJmyQ", "09 - Rast Panjgah Feyli 5Gaah"),
        ("Q_KnITkQyIw", "10 - Rast Panjgah Naghmeh"),
        ("GIt4WVgd_NY", "11 - Rast Panjgah Rak Hendi"),
        ("v8b70whWJ30", "12 - Rast Panjgah Safir-e Rak"),
        ("iaK0Ukdj9CM", "13 - Rast Panjgah Zangooleh"),
        ("Yhf6EXPtpxk", "14 - Rast Panjgah Eshareh be Shushtari"),
        ("PctK3uzzLtw", "15 - Rast Panjgah Masnavi Shushtari Rak Forud"),
        ("lkwPlBm8CRs", "16 - Rast Panjgah Leili o Majnoon"),
        ("vjmZf7M5MjQ", "17 - Rast Panjgah Eshareh be Bidad"),
        ("p5YoJlO7f5Y", "18 - Rast Panjgah Masnavi"),
        ("gqAztIWhjTo", "19 - Rast Panjgah Forud"),
    ]),

    # 2. Shajarian & Mohammad Reza Lotfi - Cheshmeye Noush (Masterpiece Concert in Rast-Panjgah)
    ("Mohammad Reza Lotfi & Shajarian/Cheshmeye Noush - Rast Panjgah", [
        ("S1cbsNTOZl0", "01 - Pishdaramade Rast"),
        ("0WR_dTjJq6U", "02 - Chaharmezrab Rast"),
        ("xPQOZf_WTTo", "03 - Saz Va Avaz Pt 1"),
        ("LRYVMkdHWPQ", "04 - Tasnife Ghadimye Nava"),
        ("CuvEYPfV9R0", "05 - Avaz Va Chaharmezrab"),
        ("7I08qDoYcN0", "06 - Ghateye Zarbiye Tar"),
        ("DNJbjTKygUM", "07 - Saz Va Avaz Pt 2"),
        ("x9CGMfZW5Hg", "08 - Ghateh Zarbi Naghme Esfahan Sarkhoshan"),
    ]),

    # 3. Sanam Gharacheh (Historical 1927-1929 Recording)
    ("Historical Masters/1927-1929 Sanam Gharacheh - Rast Panjgah", [
        ("dBiXDDDiz7w", "01 - Rast Panjgah Sanam Gharacheh 1927-1929"),
    ]),

    # 4. Seyed Ahmadkhan (Early Qajar 1907-1912 Shellac Recording)
    ("Historical Masters/1907-1912 Seyed Ahmadkhan - Rast Panjgah", [
        ("XFuYqoOAHWI", "01 - Rast Panjgah Seyed Ahmadkhan Shellac"),
    ]),

    # 5. Morteza Neydavud - Complete Radif Vol. 5 (Tar)
    ("Morteza Neydavud/Radif on Tar Vol 5 - Rast-Panjgah", [
        ("BmHfyDnOQPU", "01 - Rast-Panjgah Daramad I"),
        ("DUulIn_YDQM", "02 - Rast-Panjgah Avaz"),
        ("KqmKxRnH2DI", "03 - Rast-Panjgah Chaharmezrab"),
        ("JwuKsWk-3aE", "04 - Rast-Panjgah Zang-e Shotor"),
        ("Q5bCYvzfw5s", "05 - Rast-Panjgah Naghme"),
        ("Gik4cD2Py_o", "06 - Rast-Panjgah Ruhafza"),
        ("KPTYoBjSPpI", "07 - Rast-Panjgah Parvane I"),
        ("kBa5UcOZX5k", "08 - Rast-Panjgah Panjgah"),
        ("TctBvHvM0cE", "09 - Rast-Panjgah Parvane II"),
        ("zjb8P2mjoCs", "10 - Rast-Panjgah Oshshaq"),
        ("zGVFcYtVgUc", "11 - Rast-Panjgah Bayat-e Ajam"),
        ("znJYshanCKo", "12 - Rast-Panjgah Zabol"),
        ("4ygE5-50k90", "13 - Rast-Panjgah Qarache"),
        ("hlo-d7wYw1U", "14 - Rast-Panjgah Bahr-e Nur"),
        ("DY_r2PYau9U", "15 - Rast-Panjgah Mobarqa and Sepehr"),
        ("v_GazJaXbyw", "16 - Rast-Panjgah Neyriz"),
        ("8NX2jWj8TnE", "17 - Rast-Panjgah Nowruz-e Khara"),
        ("0OSapX5q_Jw", "18 - Rast-Panjgah Nowruz-e Saba"),
        ("3xqL1_AGOsU", "19 - Rast-Panjgah Nowruz-e Arab"),
        ("7Nt1j8ojYjw", "20 - Rast-Panjgah Tarz"),
        ("LBjg6yGrVEg", "21 - Rast-Panjgah Hazin"),
    ]),

    # 6. Abolhasan Saba - Dastgah Rast-Panjgah (Violin, Vol. 3)
    ("Abolhasan Saba/Violin Vol 3 - Rast-Panjgah", [
        ("YEt3prm3N0M", "01 - Dastgah Rast-Panjgah Saba Violin"),
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

def main():
    print(f"=== Downloading User-Provided Grand Rast-Panjgah Collections ===")
    total = sum(len(tracks) for _, tracks in DOWNLOAD_SETS)
    print(f"Target: {len(DOWNLOAD_SETS)} collections, {total} canonical tracks/gushehs.\n")
    
    count = 0
    for folder_rel, tracks in DOWNLOAD_SETS:
        out_dir = BASE / folder_rel
        print(f"\nCollection: {folder_rel}")
        for ytid, title in tracks:
            count += 1
            print(f"[{count}/{total}]", end=" ")
            download_track(out_dir, ytid, title)

if __name__ == "__main__":
    main()
