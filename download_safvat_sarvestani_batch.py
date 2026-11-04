import subprocess
from pathlib import Path

out_dir = Path("audio/Safvat_and_Sarvestani_Rare")
out_dir.mkdir(parents=True, exist_ok=True)

targets = [
    ("Safvat_Setar_Solo_BSPDwyzNV6w", "https://www.youtube.com/watch?v=BSPDwyzNV6w"),
    ("Safvat_Setar_1962_LNwPd8_hP74", "https://www.youtube.com/watch?v=LNwPd8_hP74"),
    ("Safvat_Setar_Part2_dqg5Ka7--pg", "https://www.youtube.com/watch?v=dqg5Ka7--pg"),
    ("Safvat_Setar_Part1_5zSljfC5jdY", "https://www.youtube.com/watch?v=5zSljfC5jdY"),
    ("Safvat_Setar_Razavi_Utah_yvZh-u4C6jY", "https://www.youtube.com/watch?v=yvZh-u4C6jY"),
    ("Sarvestani_Masnavi_Mokhalef_Chahargah_YJUeciRfLSc", "https://www.youtube.com/watch?v=YJUeciRfLSc"),
]

print(f"Downloading {len(targets)} rare archival master recordings (Dr. Dariush Safvat & Razavi Sarvestani)...")

for name, url in targets:
    wav_path = out_dir / f"{name}.wav"
    if wav_path.exists():
        print(f"  Exists: {wav_path.name}")
        continue
    print(f"  Downloading {name}...")
    cmd = [
        "/opt/homebrew/bin/yt-dlp",
        "-x",
        "--audio-format", "wav",
        "--postprocessor-args", "ffmpeg:-ar 44100 -ac 1",
        "-o", str(out_dir / f"{name}.%(ext)s"),
        url
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    print(f"  Done: {wav_path.name}")

print("All Safvat & Sarvestani tracks downloaded!")
