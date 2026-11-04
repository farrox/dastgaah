import math

base = 181.8 # Tonic C
peaks = [181.8, 197.1, 215.0, 242.7, 272.4, 396.5, 432.4, 485.4]
labels = ["Tonic (Do)", "Rek (138c)", "Mib (294c) / Mik (336c)", "Fa (498c Shahed)", "Sol (702c)", "Lak (835c)", "Sib (1017c)", "Do (1200c)"]

print(f"Base tonic: {base} Hz")
for p in peaks:
    c = 1200.0 * math.log2(p / base)
    oct_c = c % 1200
    print(f"  {p:.1f} Hz -> {c:+6.1f}¢ (mod 1200: {oct_c:6.1f}¢)")

