import math

# In Track 11 (Taherzadeh & Santour Abuata II):
# Tonic Peak sits at 702.0 Hz (F5 in vocal, or high octave Shahed / Do).
# Let's inspect the intervals relative to 702.0 Hz and relative to Middle C / F:
# Peak 1: 702.0 Hz (0.0c)
# Peak 2: +150.0c -> 765.7 Hz
# Peak 3: +360.0c -> 864.6 Hz

# In Track 12 (Rezagholikhan & Santour Abuata):
# Tonic Peak sits at 352.0 Hz (F4 - standard Abuata Shahed!).
base_f4 = 352.0
# Peak 1: 352.0 Hz (0.0c = Shahed F4)
# Peak 2: +110.0c -> 375.0 Hz
# Peak 3: +140.0c -> 381.5 Hz (Al-Farabi 13/12 above Shahed!)

print("1906 Qajar Santour & Vocal Pitch Audit:")
print(f"Rezagholikhan Shahed Base: {base_f4:.1f} Hz (F4)")
for c in [0.0, 110.0, 140.0]:
    f = base_f4 * (2.0 ** (c / 1200.0))
    print(f"  Cent: {c:+6.1f}¢ -> {f:.1f} Hz")

