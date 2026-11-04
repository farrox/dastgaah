import subprocess

additions = [
    ("https://music.youtube.com/playlist?list=OLAK5uy_kZj_7z7oG62AYe2HeBCVDdTJ7IRapUrLE", "audio/YouTube Music/Historical Anthologies/Tar - Aqa Hoseyn-Qoli/%(playlist_index)02d - %(title)s.%(ext)s"),
    ("https://music.youtube.com/playlist?list=OLAK5uy_nJBLjtMEYImu9lSkJrxKFt0gKNSCanPMk", "audio/YouTube Music/Historical Anthologies/The Tar of Qajar Period/%(playlist_index)02d - %(title)s.%(ext)s"),
]

for url, out_tmpl in additions:
    print(f"\nDownloading {url} -> {out_tmpl}")
    cmd = [
        "/opt/homebrew/bin/yt-dlp",
        "-f", "ba",
        "--extract-audio",
        "--audio-format", "m4a",
        "--yes-playlist",
        "-o", out_tmpl,
        url
    ]
    subprocess.run(cmd)

print("Qajar additions download complete!")
