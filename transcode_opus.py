import os
import subprocess

dirs = [
    "audio/YouTube Music/Nur-Ali Borumand/Bayat Tork",
    "audio/YouTube Music/Nur-Ali Borumand/Kord-e Bayat",
    "audio/YouTube Music/Nur-Ali Borumand/Afshari",
    "audio/YouTube Music/Mahmud Karimi/Abuata",
    "audio/YouTube Music/Mahmud Karimi/Afshari",
    "audio/YouTube Music/Mahmud Karimi/Bayat Tork",
]

for d in dirs:
    if not os.path.exists(d):
        continue
    for f in sorted(os.listdir(d)):
        if f.endswith(".opus") or f.endswith(".m4a"):
            src = os.path.join(d, f)
            stem = f.split(".")[0]
            wav = os.path.join(d, stem + ".wav")
            if not os.path.exists(wav):
                print(f"Transcoding {f} -> {wav}...")
                subprocess.run(["ffmpeg", "-y", "-i", src, "-ar", "44100", "-ac", "1", wav], capture_output=True)

print("Transcode opus/m4a complete!")
