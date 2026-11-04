import subprocess, os
from pathlib import Path

out_dir = Path("audio/Abolhasan Saba/Abolhasan_Saba_Topic_Complete")
out_dir.mkdir(parents=True, exist_ok=True)

print("Starting background download of complete Abolhasan Saba Topic channel discography...")

cmd = [
    "/opt/homebrew/bin/yt-dlp",
    "-x",
    "--audio-format", "m4a",
    "--no-overwrites",
    "--continue",
    "--ignore-errors",
    "-o", "audio/Abolhasan Saba/Abolhasan_Saba_Topic_Complete/%(playlist_index)s - %(title)s.%(ext)s",
    "https://www.youtube.com/playlist?list=UUbzXl-z5lGDv2l40JqwubKw"
]

subprocess.run(cmd)
print("Finished downloading complete Abolhasan Saba Topic catalog!")
