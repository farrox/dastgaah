import subprocess, os
from pathlib import Path

# 1. Yousef Foroutan - Complete 147 tracks
foroutan_dir = Path("audio/Yusef Foroutan")
foroutan_dir.mkdir(parents=True, exist_ok=True)
cmd_foroutan = [
    "/opt/homebrew/bin/yt-dlp",
    "-x",
    "--audio-format", "m4a",
    "--no-overwrites",
    "--continue",
    "--ignore-errors",
    "-o", "audio/Yusef Foroutan/%(playlist_index)s - %(title)s.%(ext)s",
    "https://www.youtube.com/playlist?list=UUVNZzWOIZbFb_GVvE9brNbA"
]

# 2. Saeed Hormozi - Complete Setar Radif Vol 1 (44 tracks) & Vol 2 (43 tracks)
hormozi_dir = Path("audio/Saeed Hormozi")
hormozi_dir.mkdir(parents=True, exist_ok=True)
cmd_hormozi_1 = [
    "/opt/homebrew/bin/yt-dlp",
    "-x",
    "--audio-format", "m4a",
    "--no-overwrites",
    "--continue",
    "--ignore-errors",
    "-o", "audio/Saeed Hormozi/Radif_Vol_1/%(playlist_index)s - %(title)s.%(ext)s",
    "https://www.youtube.com/playlist?list=OLAK5uy_maRfdCPjpjc_Fpxx4HY9rChIELU6lRlgM"
]

cmd_hormozi_2 = [
    "/opt/homebrew/bin/yt-dlp",
    "-x",
    "--audio-format", "m4a",
    "--no-overwrites",
    "--continue",
    "--ignore-errors",
    "-o", "audio/Saeed Hormozi/Radif_Vol_2/%(playlist_index)s - %(title)s.%(ext)s",
    "https://www.youtube.com/playlist?list=OLAK5uy_nhMTxuNeyR4arh-51xs1aOCoN_WRyG1wU"
]

print("Launching complete download queue...")
subprocess.run(cmd_foroutan)
subprocess.run(cmd_hormozi_1)
subprocess.run(cmd_hormozi_2)
print("Finished downloading all Foroutan and Hormozi albums!")
