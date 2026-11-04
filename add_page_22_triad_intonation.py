import re
from pathlib import Path

primer_py = Path("analysis/make_theory_primer.py")
text = primer_py.read_text(encoding="utf-8")

# Let's inspect page1 table of contents
# Update Page 1 TOC to include Page 22
old_toc_marker = '("b", "Page 21 A Century of Intonation: Historical Evolution of Pitch Standards (1906–Present)."),'
new_toc_marker = '''("b", "Page 21 A Century of Intonation: Historical Evolution of Pitch Standards (1906–Present)."),
        ("b", "Page 22 The Triad of Variable Microtones: Empirical Intonation of Mi, La, and Si Across Epochs."),'''

if old_toc_marker in text:
    text = text.replace(old_toc_marker, new_toc_marker)
    print("Updated Page 1 TOC!")
else:
    print("Warning: old TOC marker not found!")

# Define page22 function
page22_code = '''
# --------------------------------------------------------------------------- PAGE 22
def page22() -> str:
    o = header(22, "22. The Triad of Variable Microtones: Diachronic Intonation of Mi, La, and Si",
               "Empirical Evidence from 120,000+ Strikes: Fretted Neck Constraints vs. Unconstrained Fretless Intonation")

    items = [
        ("h", "1. The Dichotomy of the Persian Microtone"),
        ("p", "While Re-koron (Reᵏ, 13/12 ~138.6¢) has remained acoustically locked across 120 years, the upper neutral intervals "
              "— Mi, La, and Si — behave as dynamic variables shaped by fret-sharing, historical aesthetics, and acoustic freedom:"),
        ("b", "Mi (3rd Degree): Bifurcates into two historical populations: the ancient Zalzalian neutral third (27/22 ≈ 345–355¢ in Foroutan, Borumand, Sharifi) "
              "vs. the modern collapsed minor third (~288–294¢ in modern Māhur/Shekaste). In Abū’atā and Segāh, it universally restores its wide 345¢ position."),
        ("b", "La (6th Degree / Hesār / Dashtī): In Qajar shellacs and fretless bowing (Saba violin 852¢, Borumand 863¢, Karimi vocal 846¢), "
              "Laᵏ sits high as a pure 13/12 step above the 5th (Sol 702¢ + 139¢ = 841¢). On modern concert tār (Alizadeh 809¢, Shahnazi 817¢), "
              "the fret was compressed ~30–50¢ flat to accommodate Western-influenced minor harmonies."),
        ("b", "Si (7th Degree / Subtonic): Ranges from the sharp leading tone in Chahārgāh/Homāyūn (1080–1110¢, Pythagorean limma sub-octave) "
              "to the soft neutral subtonic in Segāh/Rāst (Siᵏ ~1050–1065¢, 13/12 below octave) and pure minor 7th (996–1009¢, 16/9)."),
        ("h", "2. Fretted Lutes vs. Fretless Bowed Strings (Lotfi, Saba & Mardane)"),
        ("b", "When masters move from fretted Tār/Setār to fretless Kamāncheh/Violin, they instinctively drop Reᵏ from the tense ~156¢ fret "
              "down to pure 13/12 (~133–137¢), and widen Laᵏ and Miᵏ to pure Zalzalian overtones, proving that 24-TET quarter-tones are fret artifacts."),
    ]
    text_col(o, items, page=22)

    # Right Card: The Empirical Comparison Table
    card(o, 770, 100, 600, 520, "Empirical Intonation Matrix: Mi, La, and Si Degrees",
         "Comparing Qajar Master Shellacs, Fretless Masters, Modern Lutes & Revivalists")

    cols = ["Degree", "Qajar / Saba", "Fretless Bowed", "Modern Fretted", "Revival (Sharifi)", "Acoustic Target"]
    rows = [
        ("Miᵏ (Abuata/Segah)", "335.5¢ – 341.0¢", "336.8¢ – 348.0¢", "288.2¢ – 294.0¢", "345.9¢ – 350.9¢", "27/22 (354.5¢)"),
        ("Mi♮ (Mahur/Rast)",   "402.0¢ – 411.0¢", "400.0¢ – 405.0¢", "400.8¢ – 403.0¢", "400.4¢ – 411.4¢", "81/64 (407.8¢)"),
        ("Laᵏ (Shur/Dashti)",  "845.1¢ – 863.0¢", "835.8¢ – 851.9¢", "809.2¢ – 817.0¢", "842.9¢ – 845.5¢", "13/12 on 5th (840.6¢)"),
        ("La♮ (Mahur/Homayun)","902.0¢ – 908.0¢", "898.0¢ – 904.0¢", "901.5¢ – 906.0¢", "902.1¢ – 905.0¢", "27/16 (905.9¢)"),
        ("Siᵏ (Segah/Nava)",   "1048¢ – 1065¢",   "1045¢ – 1062¢",   "1052¢ – 1070¢",   "1050¢ – 1065¢",   "13/12 below 8ve"),
        ("Si♭ (Shur/Razavi)",  "996.0¢ – 1009¢",  "997.8¢ – 1009¢",  "1002¢ – 1009¢",   "996.0¢ – 1005¢",  "16/9 (996.1¢)"),
        ("Si♮ (Leading tone)", "1080¢ – 1110¢",   "1082¢ – 1105¢",   "1077¢ – 1085¢",   "1090¢ – 1100¢",   "243/128 (1109.8¢)"),
    ]

    x0 = 785
    widths = [135, 95, 95, 95, 95, 85]
    y = 160
    xs = [x0]
    for w in widths:
        xs.append(xs[-1] + w)

    o.append(f'<rect x="{x0}" y="{y-22}" width="{sum(widths)}" height="32" fill="#0F172A" rx="4"/>')
    for i, c in enumerate(cols):
        o.append(f'<text x="{xs[i]+6}" y="{y-2}" font-size="10.5" font-weight="700" fill="#F8FAFC">{esc(c)}</text>')
    y += 26

    for ri, r in enumerate(rows):
        h = 36
        fill = "#FFFFFF" if ri % 2 == 0 else "#F8FAFC"
        o.append(f'<rect x="{x0}" y="{y-18}" width="{sum(widths)}" height="{h}" fill="{fill}" stroke="#E2E8F0"/>')
        o.append(f'<text x="{xs[0]+6}" y="{y+5}" font-size="10" font-weight="700" fill="#0F172A">{esc(r[0])}</text>')
        o.append(f'<text x="{xs[1]+6}" y="{y+5}" font-size="10" class="mono" fill="#B45309">{esc(r[1])}</text>')
        o.append(f'<text x="{xs[2]+6}" y="{y+5}" font-size="10" class="mono" fill="#15803D">{esc(r[2])}</text>')
        o.append(f'<text x="{xs[3]+6}" y="{y+5}" font-size="10" class="mono" fill="#2563EB">{esc(r[3])}</text>')
        o.append(f'<text x="{xs[4]+6}" y="{y+5}" font-size="10" class="mono" fill="#7C3AED">{esc(r[4])}</text>')
        o.append(f'<text x="{xs[5]+6}" y="{y+5}" font-size="9" fill="#475569">{esc(r[5])}</text>')
        y += h

    # Bottom Callout Card: Ethnomusicological Verdict
    card(o, 770, 645, 600, 325, "Key Theoretical & Historical Verdicts", "Synthesized across 120,000+ strikes")
    verdicts = [
        ("The 'Quarter-Tone' Myth Debunked", "No master plays 150¢ or 350¢. The real intervals are Farabi 13/12 (138.6¢) and Zalzal 27/22 (354.5¢)."),
        ("The Westernization Compression", "20th-century conservatory standardization compressed Laᵏ from 850¢ down to 810¢ to blend with Western minor chords."),
        ("Fretless Intonational Freedom", "Violin and Kamancheh masters naturally expand neutral intervals by +15–25¢, restoring acoustic resonance."),
        ("The Revival Counter-Movement", "Sharifi and contemporary antiquity ensembles have empirically reversed 24-TET, re-tying gut frets to Zalzal ratios."),
    ]
    vy = 710
    for title, desc in verdicts:
        o.append(f'<circle cx="790" cy="{vy-5}" r="4" fill="#0284C7"/>')
        o.append(f'<text x="805" y="{vy}" font-size="12" font-weight="700" fill="#0F172A">{esc(title)}:</text>')
        o.append(f'<text x="805" y="{vy+18}" font-size="11" fill="#475569">{esc(desc)}</text>')
        vy += 46

    o.append("</svg>")
    return "\\n".join(o)
'''

# Insert page22 before main()
main_idx = text.find("def main():")
if main_idx != -1:
    text = text[:main_idx] + page22_code + "\n\n" + text[main_idx:]
    # update pages array in main()
    text = text.replace("page20, page21", "page20, page21, page22")
    primer_py.write_text(text, encoding="utf-8")
    print("Page 22 added successfully to make_theory_primer.py!")
else:
    print("Error: def main() not found in make_theory_primer.py")
