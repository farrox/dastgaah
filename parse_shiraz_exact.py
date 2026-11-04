import math

# Notice the prominent peak at 262.0 Hz (Middle C = Do!)
# 262.0 Hz is C4!
# Let's see the pitch degrees with C4 (262.0 Hz) as base tonic:
base_c = 262.0
peaks = [
    (173.4, "F3 (Shahed / Lower 4th)"),
    (231.4, "Bb3 (Subtonic 7th)"),
    (262.0, "C4 (Tonic Do)"),
    (283.3, "D4k (Farabian 13/12 Neutral 2nd)"),
    (308.5, "Eb4 / E4k (Zalzal 27/22 3rd)"),
    (347.7, "F4 (Shahed 4th)"),
    (393.7, "G4 (Acoustic 5th)"),
    (697.4, "F5 (Shahed Octave)")
]

print(f"Shiraz Arts Festival Abuata Concert (Taj Esfahani, Shahnaz, Kasaei) Modal Analysis:")
print(f"Base Tonic C4: {base_c} Hz\n")
for f_val, label in peaks:
    c = 1200.0 * math.log2(f_val / base_c)
    print(f"  {f_val:5.1f} Hz -> {c:+6.1f}¢  |  {label}")

