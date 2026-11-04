import subprocess
from pathlib import Path

out_dir = Path("audio/Tabatabaei_Maktab_e_Esfahan/Abouata")
out_dir.mkdir(parents=True, exist_ok=True)

print("Downloading complete album: Radif Avazi Maktab-e Esfahan - Abouata (Seyed Reza Tabatabaei, 13 tracks)...")

cmd = [
    "/opt/homebrew/bin/yt-dlp",
    "-x",
    "--audio-format", "wav",
    "--postprocessor-args", "ffmpeg:-ar 44100 -ac 1",
    "--no-overwrites",
    "--continue",
    "--ignore-errors",
    "-o", "audio/Tabatabaei_Maktab_e_Esfahan/Abouata/%(playlist_index)s - %(title)s.%(ext)s",
    "https://www.youtube.com/playlist?list=OLAK5uy_nvR0ggDu3x3fEyKjY4H31elCk6yBTvbtM"
]

subprocess.run(cmd)
print("Finished downloading Tabatabaei Abouata album!")
