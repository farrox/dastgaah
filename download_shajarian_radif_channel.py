import subprocess
from pathlib import Path

out_dir = Path("audio/Mohammad_Reza_Shajarian_Radif_Avazi")
out_dir.mkdir(parents=True, exist_ok=True)

print("Starting background download of complete Radif-e Avazi Shajarian channel...")

cmd = [
    "/opt/homebrew/bin/yt-dlp",
    "-x",
    "--audio-format", "m4a",
    "--no-overwrites",
    "--continue",
    "--ignore-errors",
    "-o", "audio/Mohammad_Reza_Shajarian_Radif_Avazi/%(playlist_index)s - %(title)s.%(ext)s",
    "https://www.youtube.com/@radife_avazi_shajarian/videos"
]

subprocess.run(cmd)
print("Finished downloading Shajarian Vocal Radif!")
