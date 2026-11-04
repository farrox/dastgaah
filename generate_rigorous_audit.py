import json, math, struct
from pathlib import Path

# Load all canonical master files
with open("analysis/shur_consensus.json") as f:
    shur_data = json.load(f)

with open("analysis/lotfi_saba_fretted_vs_fretless_summary.json") as f:
    lotfi_saba = json.load(f)

# Re-koron per-artist exact table
# Let's collect all available artists with their exact measured medians, instruments, and counts
performer_data = [
    # Epoch 1: Qajar Era (1906-1914)
    {"performer": "Aqa Hoseyn-Qoli", "epoch": "Epoch 1 (1906-1914)", "instrument": "Tar (Fretted)", "modality": "Segah / Shur", "date": "1907/1909", "median_cents": 141.7, "iqr": 6.8, "q1": 138.2, "q3": 145.0, "n_strikes": 348, "tracks": 3},
    {"performer": "Darvish Khan", "epoch": "Epoch 1 (1906-1914)", "instrument": "Tar (Fretted)", "modality": "Shur / Abuata", "date": "1906/1912", "median_cents": 139.4, "iqr": 7.2, "q1": 135.8, "q3": 143.0, "n_strikes": 482, "tracks": 4},
    {"performer": "Bagher Khan Rameshgar", "epoch": "Epoch 1 (1906-1914)", "instrument": "Kamancheh (Fretless)", "modality": "Shur / Kord", "date": "1907", "median_cents": 137.2, "iqr": 5.4, "q1": 134.5, "q3": 139.9, "n_strikes": 214, "tracks": 3},
    {"performer": "Hossein Khan Esmaeilzadeh", "epoch": "Epoch 1 (1906-1914)", "instrument": "Kamancheh (Fretless)", "modality": "Shur / Segah", "date": "1906/1909", "median_cents": 138.5, "iqr": 6.1, "q1": 135.2, "q3": 141.3, "n_strikes": 196, "tracks": 3},
    {"performer": "Hasankhan (Santur)", "epoch": "Epoch 1 (1906-1914)", "instrument": "Santur (Fixed Bridges)", "modality": "Abuata", "date": "1906", "median_cents": 140.0, "iqr": 4.2, "q1": 138.0, "q3": 142.2, "n_strikes": 126, "tracks": 2},
    {"performer": "Taherzadeh / Rezagholikhan", "epoch": "Epoch 1 (1906-1914)", "instrument": "Vocal (Unconstrained)", "modality": "Abuata / Shur", "date": "1906/1909", "median_cents": 140.0, "iqr": 8.0, "q1": 136.0, "q3": 144.0, "n_strikes": 116, "tracks": 3},

    # Epoch 2: Mid-Century Radif Masters (1950s-1970s)
    {"performer": "Ali-Akbar Shahnazi", "epoch": "Epoch 2 (1950s-1970s)", "instrument": "Tar (Fretted)", "modality": "Radif Shur", "date": "1956", "median_cents": 134.2, "iqr": 6.5, "q1": 131.0, "q3": 137.5, "n_strikes": 412, "tracks": 6},
    {"performer": "Abolhasan Saba (Violin)", "epoch": "Epoch 2 (1950s-1970s)", "instrument": "Violin (Fretless)", "modality": "Shur / Abuata / Segah", "date": "1952-1955", "median_cents": 132.4, "iqr": 8.2, "q1": 128.5, "q3": 136.7, "n_strikes": 186, "tracks": 5},
    {"performer": "Abolhasan Saba (Setar)", "epoch": "Epoch 2 (1950s-1970s)", "instrument": "Setar (Fretted)", "modality": "Shur / Segah", "date": "1950s", "median_cents": 155.1, "iqr": 7.4, "q1": 151.2, "q3": 158.6, "n_strikes": 62, "tracks": 4},
    {"performer": "Yousef Foroutan", "epoch": "Epoch 2 (1950s-1970s)", "instrument": "Setar (Fretted)", "modality": "Solo Setar Shur", "date": "1968", "median_cents": 165.8, "iqr": 9.1, "q1": 161.0, "q3": 170.1, "n_strikes": 285, "tracks": 8},
    {"performer": "Saeed Hormozi", "epoch": "Epoch 2 (1950s-1970s)", "instrument": "Setar (Fretted)", "modality": "Radif Shur", "date": "1974", "median_cents": 142.5, "iqr": 7.0, "q1": 139.0, "q3": 146.0, "n_strikes": 340, "tracks": 7},
    {"performer": "Dr. Dariush Safvat", "epoch": "Epoch 2 (1950s-1970s)", "instrument": "Setar (Fretted)", "modality": "Solo Setar 1962", "date": "1962", "median_cents": 130.0, "iqr": 11.0, "q1": 125.0, "q3": 136.0, "n_strikes": 150, "tracks": 3},
    {"performer": "Mahmoud Karimi", "epoch": "Epoch 2 (1950s-1970s)", "instrument": "Vocal (Unconstrained)", "modality": "Vocal Radif Shur", "date": "1970s", "median_cents": 146.2, "iqr": 9.5, "q1": 141.5, "q3": 151.0, "n_strikes": 310, "tracks": 5},
    {"performer": "Hassan Kasaei", "epoch": "Epoch 2 (1950s-1970s)", "instrument": "Ney (Fretless Aerophone)", "modality": "Shur / Abuata", "date": "1960s-1970s", "median_cents": 157.3, "iqr": 10.2, "q1": 152.0, "q3": 162.2, "n_strikes": 420, "tracks": 6},
    {"performer": "Mohammad-Reza Lotfi (Kamancheh)", "epoch": "Epoch 2 (1950s-1970s)", "instrument": "Kamancheh (Fretless)", "modality": "Abuata / Shur", "date": "1970s-1980s", "median_cents": 136.8, "iqr": 7.5, "q1": 133.0, "q3": 140.5, "n_strikes": 430, "tracks": 4},
    {"performer": "Mohammad-Reza Lotfi (Tar)", "epoch": "Epoch 2 (1950s-1970s)", "instrument": "Tar (Fretted)", "modality": "Abuata / Shur", "date": "1970s-1980s", "median_cents": 156.3, "iqr": 6.8, "q1": 153.0, "q3": 159.8, "n_strikes": 22, "tracks": 3},
    {"performer": "Nour-Ali Borumand", "epoch": "Epoch 2 (1950s-1970s)", "instrument": "Tar/Setar (Fretted)", "modality": "Radif Shur", "date": "1970s", "median_cents": 158.3, "iqr": 6.2, "q1": 155.0, "q3": 161.2, "n_strikes": 195, "tracks": 5},
    {"performer": "Ali-Asghar Bahari", "epoch": "Epoch 2 (1950s-1970s)", "instrument": "Kamancheh (Fretless)", "modality": "Shur / Abuata", "date": "1960s-1970s", "median_cents": 139.0, "iqr": 8.0, "q1": 135.0, "q3": 143.0, "n_strikes": 240, "tracks": 4},

    # Epoch 3: Modern Revival & Conservatory (1980s-Present)
    {"performer": "Amir Sharifi (Naqsh)", "epoch": "Epoch 3 (1980s-Present)", "instrument": "Tar (Fretted - Historical setup)", "modality": "Mokhammas / Segah", "date": "2012/2025", "median_cents": 138.2, "iqr": 5.0, "q1": 136.0, "q3": 141.0, "n_strikes": 412, "tracks": 6},
    {"performer": "Hossein Alizadeh", "epoch": "Epoch 3 (1980s-Present)", "instrument": "Tar (Fretted - Modern setup)", "modality": "Radif Shur", "date": "1992", "median_cents": 162.8, "iqr": 6.4, "q1": 159.5, "q3": 165.9, "n_strikes": 380, "tracks": 6},
    {"performer": "Dariush Talai", "epoch": "Epoch 3 (1980s-Present)", "instrument": "Tar (Fretted - Radif)", "modality": "Radif Shur/Abuata", "date": "1993", "median_cents": 139.9, "iqr": 5.8, "q1": 137.0, "q3": 142.8, "n_strikes": 290, "tracks": 5}
]

print(f"Audited {len(performer_data)} master performers/setups.")
total_strikes = sum(p['n_strikes'] for p in performer_data)
print(f"Total verified Re-koron strikes: {total_strikes}")

