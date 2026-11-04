import subprocess, os
from pathlib import Path

# Channel 1: UCYSMb7zCpD8maBLsXdtDFrg -> uploads playlist UUYSMb7zCpD8maBLsXdtDFrg
# Channel 2: UCb7ouWNS-8qEyYbzVi226Bw -> uploads playlist UUb7ouWNS-8qEyYbzVi226Bw

out_dir_1 = Path("audio/Dariush Safvat/Dariush_Safvat_Topic_EN")
out_dir_2 = Path("audio/Dariush Safvat/Dariush_Safvat_Topic_FA")
out_dir_1.mkdir(parents=True, exist_ok=True)
out_dir_2.mkdir(parents=True, exist_ok=True)

print("Starting background download of Dariush Safvat discography from both Topic channels...")

cmd1 = [
    "/opt/homebrew/bin/yt-dlp",
    "-x",
    "--audio-format", "m4a",
    "--no-overwrites",
    "--continue",
    "--ignore-errors",
    "-o", "audio/Dariush Safvat/Dariush_Safvat_Topic_EN/%(playlist_index)s - %(title)s.%(ext)s",
    "https://www.youtube.com/playlist?list=UUYSMb7zCpD8maBLsXdtDFrg"
]

cmd2 = [
    "/opt/homebrew/bin/yt-dlp",
    "-x",
    "--audio-format", "m4a",
    "--no-overwrites",
    "--continue",
    "--ignore-errors",
    "-o", "audio/Dariush Safvat/Dariush_Safvat_Topic_FA/%(playlist_index)s - %(title)s.%(ext)s",
    "https://www.youtube.com/playlist?list=UUb7ouWNS-8qEyYbzVi226Bw"
]

subprocess.run(cmd1)
subprocess.run(cmd2)
print("Finished downloading Dariush Safvat Topic catalogs!")
