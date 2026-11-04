import os
import subprocess

shahnazi_dir = "audio/YouTube Music/Ali-Akbar Shahnazi/The Advanced Shahnazi Radif I"
for f in sorted(os.listdir(shahnazi_dir)):
    if "Abuata" in f or "Tork" in f:
        src = os.path.join(shahnazi_dir, f)
        wav = os.path.splitext(src)[0] + ".wav"
        if not os.path.exists(wav):
            print(f"Converting {f} -> wav...")
            subprocess.run(["ffmpeg", "-y", "-i", src, "-ar", "16000", "-ac", "1", wav], capture_output=True)
print("Shahnazi conversion complete.")
