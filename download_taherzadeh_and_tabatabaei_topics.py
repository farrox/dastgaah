import subprocess, os
from pathlib import Path

# Channel 1: Seyed Reza Tabatabaei - Topic (UCPZ7mnMIK8WtUfdXdRUwb0g -> UUPZ7mnMIK8WtUfdXdRUwb0g)
# Channel 2: Hossein Ali Khan Taherzadeh - Topic (UClKAnqZH5XHLc5mFVG09ofw -> UUlKAnqZH5XHLc5mFVG09ofw)

out_tabatabaei = Path("audio/Tabatabaei_Maktab_e_Esfahan/Complete_Topic")
out_taherzadeh = Path("audio/Hossein_Ali_Khan_Taherzadeh_Qajar_Shellac")
out_tabatabaei.mkdir(parents=True, exist_ok=True)
out_taherzadeh.mkdir(parents=True, exist_ok=True)

print("Starting background download of Seyed Reza Tabatabaei & Hossein Ali Khan Taherzadeh...")

cmd_tabatabaei = [
    "/opt/homebrew/bin/yt-dlp",
    "-x",
    "--audio-format", "m4a",
    "--no-overwrites",
    "--continue",
    "--ignore-errors",
    "-o", "audio/Tabatabaei_Maktab_e_Esfahan/Complete_Topic/%(playlist_index)s - %(title)s.%(ext)s",
    "https://www.youtube.com/playlist?list=UUPZ7mnMIK8WtUfdXdRUwb0g"
]

cmd_taherzadeh = [
    "/opt/homebrew/bin/yt-dlp",
    "-x",
    "--audio-format", "m4a",
    "--no-overwrites",
    "--continue",
    "--ignore-errors",
    "-o", "audio/Hossein_Ali_Khan_Taherzadeh_Qajar_Shellac/%(playlist_index)s - %(title)s.%(ext)s",
    "https://www.youtube.com/playlist?list=UUlKAnqZH5XHLc5mFVG09ofw"
]

subprocess.run(cmd_tabatabaei)
subprocess.run(cmd_taherzadeh)
print("Finished downloading Tabatabaei & Taherzadeh catalogs!")
