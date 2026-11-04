import subprocess
from pathlib import Path

# 1. Gholam-Hoseyn Bigjekhani - Topic (UC-XugAp3HZ49nQhal0Z5vlw -> UU-XugAp3HZ49nQhal0Z5vlw)
dir_bigjekhani = Path("audio/Gholam_Hoseyn_Bigjekhani_Complete")
dir_bigjekhani.mkdir(parents=True, exist_ok=True)

# 2. Taj Esfahani - Topic (UC3qOcAszudj_YzPbFvymOJg -> UU3qOcAszudj_YzPbFvymOJg)
dir_taj = Path("audio/Taj_Esfahani_Complete")
dir_taj.mkdir(parents=True, exist_ok=True)

# 3. Shiraz Arts Festival Iconic Abuata Concert (Taj Esfahani, Shahnaz, Kasaei, Eftetah)
dir_shiraz = Path("audio/Shiraz_Arts_Festival_1970s")
dir_shiraz.mkdir(parents=True, exist_ok=True)

print("Downloading the legendary Shiraz Arts Festival Abuata Concert (Taj, Shahnaz, Kasaei, Eftetah)...")
cmd_shiraz = [
    "/opt/homebrew/bin/yt-dlp",
    "-x",
    "--audio-format", "wav",
    "--postprocessor-args", "ffmpeg:-ar 44100 -ac 1",
    "-o", str(dir_shiraz / "Shiraz_Festival_Abuata_Taj_Shahnaz_Kasaei.%(ext)s"),
    "https://www.youtube.com/watch?v=ClieX3NIuow"
]

cmd_bigjekhani = [
    "/opt/homebrew/bin/yt-dlp",
    "-x",
    "--audio-format", "m4a",
    "--no-overwrites",
    "--continue",
    "--ignore-errors",
    "-o", "audio/Gholam_Hoseyn_Bigjekhani_Complete/%(playlist_index)s - %(title)s.%(ext)s",
    "https://www.youtube.com/playlist?list=UU-XugAp3HZ49nQhal0Z5vlw"
]

cmd_taj = [
    "/opt/homebrew/bin/yt-dlp",
    "-x",
    "--audio-format", "m4a",
    "--no-overwrites",
    "--continue",
    "--ignore-errors",
    "-o", "audio/Taj_Esfahani_Complete/%(playlist_index)s - %(title)s.%(ext)s",
    "https://www.youtube.com/playlist?list=UU3qOcAszudj_YzPbFvymOJg"
]

subprocess.run(cmd_shiraz)
subprocess.run(cmd_bigjekhani)
subprocess.run(cmd_taj)
print("Finished downloading Bigjekhani, Taj, and Shiraz Festival Concert!")
