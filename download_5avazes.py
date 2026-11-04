import subprocess
import os

tracks = {
    # Borumand Mirza Abdollah Vol 2: Bayat Tork
    "audio/YouTube Music/Nur-Ali Borumand/Bayat Tork/01 - Daramd-e Aval.m4a": "Uo7Tk7UH8Jk",
    "audio/YouTube Music/Nur-Ali Borumand/Bayat Tork/02 - Daramd-e Dovvom.m4a": "s55KSg7bk7g",
    "audio/YouTube Music/Nur-Ali Borumand/Bayat Tork/03 - Dogah.m4a": "5U2fOeJPny0",
    "audio/YouTube Music/Nur-Ali Borumand/Bayat Tork/04 - Ruhol Arvah.m4a": "kVg6PJms8PQ",
    "audio/YouTube Music/Nur-Ali Borumand/Bayat Tork/05 - Jame-daran.m4a": "4CnlursKFOo",
    "audio/YouTube Music/Nur-Ali Borumand/Bayat Tork/06 - Mehrabani.m4a": "FFVwLYMzlC8",
    "audio/YouTube Music/Nur-Ali Borumand/Bayat Tork/07 - Shekaste.m4a": "8EeJG_y2jwo",
    "audio/YouTube Music/Nur-Ali Borumand/Bayat Tork/08 - Feyli.m4a": "Fcmzv6QF9aE",
    "audio/YouTube Music/Nur-Ali Borumand/Bayat Tork/09 - Khosravani.m4a": "vVnOjqRY7OE",

    # Borumand Mirza Abdollah Vol 2: Kord-e Bayat
    "audio/YouTube Music/Nur-Ali Borumand/Kord-e Bayat/01 - Daramd-e Aval.m4a": "LCWnLmM9yNg",
    "audio/YouTube Music/Nur-Ali Borumand/Kord-e Bayat/02 - Daramd-e Dovvom.m4a": "NF_TFCycutg",
    "audio/YouTube Music/Nur-Ali Borumand/Kord-e Bayat/03 - Daramd-e Sevvom.m4a": "WLJ84rEGBxs",
    "audio/YouTube Music/Nur-Ali Borumand/Kord-e Bayat/04 - Daramd-e Chaharom.m4a": "xsobkKQf0e4",
    "audio/YouTube Music/Nur-Ali Borumand/Kord-e Bayat/05 - Haji Hasani.m4a": "iTgGOG6aXWs",
    "audio/YouTube Music/Nur-Ali Borumand/Kord-e Bayat/06 - Baste-negar.m4a": "pXHCXwIpkMM",
    "audio/YouTube Music/Nur-Ali Borumand/Kord-e Bayat/07 - Qatar.m4a": "qjLYGWqMXk8",
    "audio/YouTube Music/Nur-Ali Borumand/Kord-e Bayat/08 - Qarayi.m4a": "h2kKevaljjo",

    # Borumand Mirza Abdollah Vol 2: Afshari
    "audio/YouTube Music/Nur-Ali Borumand/Afshari/01 - Daramd.m4a": "WT0DatQ0rw4",
    "audio/YouTube Music/Nur-Ali Borumand/Afshari/02 - Araq.m4a": "Urm7KZsXyr8",
    "audio/YouTube Music/Nur-Ali Borumand/Afshari/03 - Baste-negar.m4a": "i4xVyw9yZ4A",

    # Karimi Vocal Radif: Abuata
    "audio/YouTube Music/Mahmud Karimi/Abuata/01 - Daramad.m4a": "gYrJOHxdb04",
    "audio/YouTube Music/Mahmud Karimi/Abuata/02 - Sayakhi.m4a": "Uw5NtQYrXuk",
    "audio/YouTube Music/Mahmud Karimi/Abuata/03 - Ramkali I.m4a": "PxHy2sW1L3Q",
    "audio/YouTube Music/Mahmud Karimi/Abuata/04 - Ramkali II.m4a": "u_jWSaJ0hTU",
    "audio/YouTube Music/Mahmud Karimi/Abuata/05 - Gawri.m4a": "qTqTLjKudTs",
    "audio/YouTube Music/Mahmud Karimi/Abuata/06 - Hejaz.m4a": "BgbDRpnV8A4",
    "audio/YouTube Music/Mahmud Karimi/Abuata/07 - Khosrow Shirin.m4a": "T3hUTEyqro8",
    "audio/YouTube Music/Mahmud Karimi/Abuata/08 - Chaharbagh.m4a": "T-s1i4R0PVU",

    # Karimi Vocal Radif: Afshari
    "audio/YouTube Music/Mahmud Karimi/Afshari/01 - Daramad.m4a": "NQzJCgM0ebA",
    "audio/YouTube Music/Mahmud Karimi/Afshari/02 - Jamedaran.m4a": "plaG_k-1tsM",
    "audio/YouTube Music/Mahmud Karimi/Afshari/03 - Hesar.m4a": "o4dM3zUy_9Q",
    "audio/YouTube Music/Mahmud Karimi/Afshari/04 - Sadri.m4a": "9EBOYSHbAJ4",
    "audio/YouTube Music/Mahmud Karimi/Afshari/05 - Qarayi.m4a": "lNrQNGX9ohw",
    "audio/YouTube Music/Mahmud Karimi/Afshari/06 - Rohab.m4a": "emKNSqfPGHU",
    "audio/YouTube Music/Mahmud Karimi/Afshari/07 - Masnavi.m4a": "gflr3FjkyYs",

    # Karimi Vocal Radif: Bayat-e Tork
    "audio/YouTube Music/Mahmud Karimi/Bayat Tork/01 - Daramad I.m4a": "UYhnRsSpzXk",
    "audio/YouTube Music/Mahmud Karimi/Bayat Tork/02 - Dogah.m4a": "Jb3_ZrvKRfk",
    "audio/YouTube Music/Mahmud Karimi/Bayat Tork/03 - Ruhol Arvah.m4a": "rdRYzsNYDbY",
    "audio/YouTube Music/Mahmud Karimi/Bayat Tork/04 - Qatar.m4a": "7oLHcjo7rKw",
    "audio/YouTube Music/Mahmud Karimi/Bayat Tork/05 - Masnavi.m4a": "0C3EOVykrIA",
}

for path, ytid in tracks.items():
    if os.path.exists(path):
        print(f"Already exists: {path}")
        continue
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cmd = [
        "/opt/homebrew/bin/yt-dlp",
        "-f", "ba",
        "-x",
        "-o", path,
        f"https://www.youtube.com/watch?v={ytid}"
    ]
    print(f"Downloading {ytid} -> {path}...")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"Failed to download {ytid}")
    else:
        # Convert to 16kHz mono wav
        wav_path = os.path.splitext(path)[0] + ".wav"
        subprocess.run(["ffmpeg", "-y", "-i", path, "-ar", "16000", "-ac", "1", wav_path], capture_output=True)
        print(f"Converted -> {wav_path}")

print("Done!")
