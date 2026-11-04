import subprocess
from pathlib import Path

out_dir = Path("audio/Qajar_Santour_and_Vocal_78RPM_1906_1909")
out_dir.mkdir(parents=True, exist_ok=True)

print("Downloading complete archival album: Music of Qajar - Recorded Works for Santour on 78 RPM LP's in 1906, 1909 (12 tracks)...")

cmd = [
    "/opt/homebrew/bin/yt-dlp",
    "-x",
    "--audio-format", "wav",
    "--postprocessor-args", "ffmpeg:-ar 44100 -ac 1",
    "--no-overwrites",
    "--continue",
    "--ignore-errors",
    "-o", "audio/Qajar_Santour_and_Vocal_78RPM_1906_1909/%(playlist_index)s - %(title)s.%(ext)s",
    "https://www.youtube.com/playlist?list=OLAK5uy_m-A_U5qgFnAHZ6wdzmPy5cqq9lt37eViA"
]

subprocess.run(cmd)
print("Finished downloading Qajar Santour & Vocal 78 RPM album!")
