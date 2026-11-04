import math

# In Daramad Abuata, Shajarian's fundamental rests at 269.7 Hz (C#4/D4).
# Notice the prominent peaks:
# 269.7 Hz (Tonic = 0c)
# +150c = Neutral second (Farabian/Vaziri transition: 138-150c)
# +360c = Zalzalian Neutral Third! (354.5c = 27/22)
# +390c = Major third ornamental inflection (5/4 = 386c)
# Let's inspect the exact frequencies:
base = 269.7
for c in [0.0, 150.0, 360.0, 390.0]:
    f = base * (2.0 ** (c / 1200.0))
    print(f"  Cent: {c:+6.1f}¢ -> {f:.1f} Hz")

