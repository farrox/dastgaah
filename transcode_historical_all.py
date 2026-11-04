import os
import subprocess
from pathlib import Path

dirs = [
    "audio/YouTube Music/Historical Anthologies/Tar - Aqa Hoseyn-Qoli",
    "audio/YouTube Music/Historical Anthologies/The Tar of Qajar Period",
    "audio/YouTube Music/Darvish Khan/Darvish Khan Tar",
    "audio/YouTube Music/Darvish Khan/Collection 16 - Darvish 1906-1914",
    "audio/YouTube Music/Yusef Forutan/Solo Setar - Mahoor",
    "audio/YouTube Music/Yusef Forutan/Shiraz Festival 1967 - Mahoor",
    "audio/YouTube Music/Saeed Hormozi/Tar Solo",
    "audio/YouTube Music/Abolhasan Saba/Abolhasan Saba Setar",
    "audio/YouTube Music/Historical Anthologies/A Century of Tar",
    "audio/YouTube Music/Historical Anthologies/A Century of Setar",
    "audio/YouTube Music/Historical Anthologies/A Century of Santur",
    "audio/YouTube Music/Historical Anthologies/Shahnavaz",
    "audio/Mahoor Demos/Panjgah",
]

total_converted = 0
for d in dirs:
    p = Path(d)
    if not p.exists():
        continue
    for f in sorted(p.iterdir()):
        if f.suffix.lower() in [".m4a", ".mp3", ".opus"]:
            wav = f.with_suffix(".wav")
            if not wav.exists():
                subprocess.run(
                    ["/opt/homebrew/bin/ffmpeg", "-y", "-i", str(f), "-ar", "44100", "-ac", "1", str(wav)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                total_converted += 1

print(f"Transcoded {total_converted} files to 44.1kHz mono WAV.")
