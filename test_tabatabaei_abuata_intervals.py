import math

# In Daramad Abouata, the base tonic is D4 (~293.5 Hz) or its octave D5 (~587 Hz).
# Let's see the intervals relative to D4 (293.5 Hz):
# 587.9 Hz = D5 (+1200c)
# 830c relative to 587.9 Hz -> actual pitch:
f_830 = 587.9 * (2.0 ** (830.0 / 1200.0))
# Let's inspect all measured pitch peaks relative to 293.5 Hz:
base = 293.5
# In Masnavi and Daramad:
peaks_hz = [293.5, 328.0, 355.0, 392.0, 440.0, 465.0, 523.0, 587.9]

print("Tabatabaei Maktab-e Esfahan - Interval resolution:")
for p in [328.0, 355.0, 392.0, 440.0, 465.0, 523.0, 587.9]:
    c = 1200.0 * math.log2(p / base)
    print(f"  {p:.1f} Hz relative to 293.5 Hz: {c:+6.1f}¢")

