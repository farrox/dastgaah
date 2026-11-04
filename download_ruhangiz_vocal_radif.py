import subprocess
from pathlib import Path

out_dir = Path("audio/Ruhangiz_Vocal_Radif")
out_dir.mkdir(parents=True, exist_ok=True)

print("Downloading complete album: Persian Vocal Music (The Ruhangiz Vocal Radif, 39 tracks, Mahoor Institute)...")

cmd = [
    "/opt/homebrew/bin/yt-dlp",
    "-x",
    "--audio-format", "wav",
    "--postprocessor-args", "ffmpeg:-ar 44100 -ac 1",
    "--no-overwrites",
    "--continue",
    "--ignore-errors",
    "-o", "audio/Ruhangiz_Vocal_Radif/%(playlist_index)s - %(title)s.%(ext)s",
    "https://www.youtube.com/playlist?list=OLAK5uy_mn8Yn4ZhDE7Ug3FYne9YY15XmVMpBoSWc"
]

subprocess.run(cmd)
print("Finished downloading Ruhangiz Vocal Radif!")
