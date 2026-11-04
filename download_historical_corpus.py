import subprocess
import os
import sys

# Master playlists and key tracks to download
items = [
    # 1. Yousef Foroutan solo videos & uploads
    ("https://www.youtube.com/watch?v=QIm5ELmtZkY", "audio/YouTube Music/Yusef Forutan/Solo Setar - Mahoor/01 - Foroutan Mahoor Solo.m4a"),
    ("https://www.youtube.com/watch?v=CHKlzlhY3ZE", "audio/YouTube Music/Yusef Forutan/Shiraz Festival 1967 - Mahoor/01 - Foroutan Shiraz 1967 Mahoor.m4a"),
    
    # 2. Saeed Hormozi playing Tar
    ("https://www.youtube.com/watch?v=aEOkpszEx1o", "audio/YouTube Music/Saeed Hormozi/Tar Solo/01 - Saeed Hormozi Tar Solo.m4a"),

    # 3. Abolhasan Saba Setar album (OLAK5uy_kMfEA987L8sAF0xoaXdY3sABGnlEvoGa8)
    ("https://www.youtube.com/playlist?list=OLAK5uy_kMfEA987L8sAF0xoaXdY3sABGnlEvoGa8", "audio/YouTube Music/Abolhasan Saba/Abolhasan Saba Setar/%(playlist_index)02d - %(title)s.%(ext)s"),

    # 4. Darvish Khan Tar album (OLAK5uy_nHdJ2HDbEzD3s7_ZZzCutogsefb21myPQ)
    ("https://www.youtube.com/playlist?list=OLAK5uy_nHdJ2HDbEzD3s7_ZZzCutogsefb21myPQ", "audio/YouTube Music/Darvish Khan/Darvish Khan Tar/%(playlist_index)02d - %(title)s.%(ext)s"),

    # 5. Gholamhossein Darvish 1906-1914 Collection 16 (OLAK5uy_k0nmY0H6_NOH-z7LtL5QPnkd--QfqVY8g)
    ("https://www.youtube.com/playlist?list=OLAK5uy_k0nmY0H6_NOH-z7LtL5QPnkd--QfqVY8g", "audio/YouTube Music/Darvish Khan/Collection 16 - Darvish 1906-1914/%(playlist_index)02d - %(title)s.%(ext)s"),

    # 6. A Century of Tar Music (OLAK5uy_mtNC16T1dEm-wX4ULx7LmG8i2eO2g9mvo)
    ("https://music.youtube.com/playlist?list=OLAK5uy_mtNC16T1dEm-wX4ULx7LmG8i2eO2g9mvo", "audio/YouTube Music/Historical Anthologies/A Century of Tar/%(playlist_index)02d - %(title)s.%(ext)s"),

    # 7. A Century of Setar Music (OLAK5uy_maSTOhgZmFLGBfPET-iRHsdQHedQPFjfQ)
    ("https://music.youtube.com/playlist?list=OLAK5uy_maSTOhgZmFLGBfPET-iRHsdQHedQPFjfQ", "audio/YouTube Music/Historical Anthologies/A Century of Setar/%(playlist_index)02d - %(title)s.%(ext)s"),

    # 8. A Century of Santur (OLAK5uy_lQ_FBb7oZJ_1R5ktmKjrZcSluCJCf68mI)
    ("https://music.youtube.com/playlist?list=OLAK5uy_lQ_FBb7oZJ_1R5ktmKjrZcSluCJCf68mI", "audio/YouTube Music/Historical Anthologies/A Century of Santur/%(playlist_index)02d - %(title)s.%(ext)s"),

    # 9. A Century of Avaz (OLAK5uy_ll9nA7Nl8QyG4V0Y2qxyzZ2338Kfhwvqw)
    ("https://music.youtube.com/playlist?list=OLAK5uy_ll9nA7Nl8QyG4V0Y2qxyzZ2338Kfhwvqw", "audio/YouTube Music/Historical Anthologies/A Century of Avaz/%(playlist_index)02d - %(title)s.%(ext)s"),
]

for url, out_tmpl in items:
    print(f"\n=======================================================")
    print(f"Downloading: {url} -> {out_tmpl}")
    print(f"=======================================================")
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

print("\nAll downloads initiated/completed!")
