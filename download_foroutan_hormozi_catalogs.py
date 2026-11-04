import subprocess, os
from pathlib import Path

# 1. Yousef Foroutan - Complete Topic Channel (147 tracks)
foroutan_dir = Path("audio/Yusef Foroutan")
foroutan_dir.mkdir(parents=True, exist_ok=True)
foroutan_url = "https://www.youtube.com/playlist?list=UUVNZzWOIZbFb_GVvE9brNbA"

print(f"Downloading complete Yousef Foroutan catalog into {foroutan_dir}...")
cmd_foroutan = [
    "/opt/homebrew/bin/yt-dlp",
    "-x",
    "--audio-format", "m4a",
    "--ignore-errors",
    "--no-overwrites",
    "--continue",
    "-o", f"{foroutan_dir}/%(album,playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s",
    foroutan_url
]
subprocess.Popen(cmd_foroutan)

# 2. Saeed Hormozi - Complete Setar Radif Vol. 1 & Vol. 2 (87 tracks)
hormozi_dir = Path("audio/Saeed Hormozi")
hormozi_dir.mkdir(parents=True, exist_ok=True)
hormozi_playlists = [
    ("Radif Vol 1", "https://www.youtube.com/playlist?list=OLAK5uy_maRfdCPjpjc_Fpxx4HY9rChIELU6lRlgM"),
    ("Radif Vol 2", "https://www.youtube.com/playlist?list=OLAK5uy_nhMTxuNeyR4arh-51xs1aOCoN_WRyG1wU")
]

for title, url in hormozi_playlists:
    print(f"Downloading Saeed Hormozi {title} into {hormozi_dir}...")
    cmd_hormozi = [
        "/opt/homebrew/bin/yt-dlp",
        "-x",
        "--audio-format", "m4a",
        "--ignore-errors",
        "--no-overwrites",
        "--continue",
        "-o", f"{hormozi_dir}/{title}/%(playlist_index)s - %(title)s.%(ext)s",
        url
    ]
    subprocess.Popen(cmd_hormozi)

print("Both background download processes launched!")
