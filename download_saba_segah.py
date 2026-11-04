import subprocess
from pathlib import Path

out_dir = Path("audio/Abolhasan Saba/Violin_Vol_3")
out_dir.mkdir(parents=True, exist_ok=True)

wav_path = out_dir / "Saba_Dastgah_Segah_Violin_Vol3.wav"
print(f"Downloading Abolhasan Saba - Dastgah Segah (Violin, Vol. 3, 22 mins)...")

cmd = [
    "/opt/homebrew/bin/yt-dlp",
    "-x",
    "--audio-format", "wav",
    "--postprocessor-args", "ffmpeg:-ar 44100 -ac 1",
    "-o", str(out_dir / "Saba_Dastgah_Segah_Violin_Vol3.%(ext)s"),
    "https://www.youtube.com/watch?v=Q410J2BUeHQ"
]
subprocess.run(cmd, check=True)
print(f"Downloaded successfully: {wav_path.name}")
