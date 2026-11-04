import subprocess
from pathlib import Path

out_dir = Path("audio/Abdollah_Davami_Vocal_Radif/Vol_1")
out_dir.mkdir(parents=True, exist_ok=True)

print("Downloading complete album: The Davami Vocal Radif, Vol. 1 (Abdollah Davami, 36 tracks, Mahoor Institute)...")

cmd = [
    "/opt/homebrew/bin/yt-dlp",
    "-x",
    "--audio-format", "wav",
    "--postprocessor-args", "ffmpeg:-ar 44100 -ac 1",
    "--no-overwrites",
    "--continue",
    "--ignore-errors",
    "-o", "audio/Abdollah_Davami_Vocal_Radif/Vol_1/%(playlist_index)s - %(title)s.%(ext)s",
    "https://www.youtube.com/playlist?list=OLAK5uy_kPSI_ML90VCamQf_CK3jZAVz6zJ9PclsM"
]

subprocess.run(cmd)
print("Finished downloading Davami Vocal Radif Vol. 1!")
