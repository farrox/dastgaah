import subprocess, os, json
from pathlib import Path

out_dir = Path("audio/Amir Sharifi")
out_dir.mkdir(parents=True, exist_ok=True)

# Channel playlist URL
channel_url = "https://www.youtube.com/playlist?list=UU8j4p-yZ45c0R_RvqYYyvgA"

print(f"Starting complete download of Amir Sharifi / Naqsh Ensemble catalog into {out_dir}...")

cmd = [
    "/opt/homebrew/bin/yt-dlp",
    "-x",
    "--audio-format", "m4a",
    "--ignore-errors",
    "--no-overwrites",
    "--continue",
    "-o", f"{out_dir}/%(album,playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s",
    channel_url
]

subprocess.run(cmd)
