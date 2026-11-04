import subprocess
import os

def generate_talai_chart():
    # Width and height of the standalone chart
    w = 1320
    h = 1140

    # Margins and ruler coordinates
    x0 = 140
    x1 = 1180
    span = x1 - x0

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    svg.append("""<defs>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&amp;family=JetBrains+Mono:wght@500;600;700&amp;display=swap');
  text { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
  .mono { font-family: 'JetBrains Mono', monospace; }
  .title { font-weight: 800; fill: #0F172A; }
  .subtitle { fill: #475569; font-size: 13.5px; }
  .ruler-bg { fill: #F8FAFC; stroke: #CBD5E1; stroke-width: 1.2; rx: 10px; }
  .super-bg { fill: #F0F7FF; stroke: #2563EB; stroke-width: 2; rx: 12px; }
  .layer-tag { font-size: 9.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
</style>
<filter id="shadow" x="-3%" y="-2%" width="106%" height="105%" filterUnits="userSpaceOnUse">
  <feDropShadow dx="0" dy="4" stdDeviation="8" flood-opacity="0.08"/>
</filter>
</defs>""")

    # Canvas Background
    svg.append(f'<rect width="{w}" height="{h}" fill="#F1F5F9"/>')

    # Main Card Container
    svg.append(f'<rect x="25" y="25" width="{w-50}" height="{h-50}" rx="16" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5" filter="url(#shadow)"/>')

    # Header
    svg.append('<text x="55" y="62" font-size="23" class="title">Dariush Talā\'ī\'s Theory of Dāngs: 3-Layer Decoupled Architecture</text>')
    svg.append('<text x="55" y="86" font-size="12.5" class="subtitle">Decoupling Source Heuristics (~20¢ Grid) · Pure Rational Models (498.05¢ Pure 4th) · Empirical Master Consensus</text>')

    # 4 Dāngs definition with 3-layer annotations
    dangs = [
        (
            "1. Dāng-e Shūr (Root of Shūr, Dashti, Navā, Abū’atā, Afshārī)",
            "Pattern: Neutral 2nd (N) + Neutral 2nd (N) + Greater Whole Tone (T+)",
            [
                (0.0, "0¢", "1/1", "Tonic (Do)", "#0F172A"),
                (138.6, "+138.6¢", "13/12 [256/243]", "Reᵏ (Fārābī / Limma)", "#DC2626"),
                (294.1, "+294.1¢", "32/27 [6/5]", "Mi♭ (Pythagorean / Just)", "#2563EB"),
                (498.0, "+498.0¢", "4/3", "Pure 4th (Fa)", "#16A34A"),
            ],
            "L1 (Source): 140 + 140 + 220 = 500¢ (~20¢ grid, aesthetic judgment)  ·  L2 (Rational): 13/12 (138.6¢) + 128/117 (155.6¢) + 9/8 (203.9¢) = 498.0¢",
            "L3 (Empirical): 12-master consensus Reᵏ = +138.7¢ [Cat A: Saba 129.0¢, Shahnazi 128.0¢, Safvat 127.5¢; Qajar Borumand Navā limma = 90.2¢]",
            106, 134
        ),
        (
            "2. Dāng-e Māhūr (Root of Māhūr &amp; Rāst-Panjgāh)",
            "Pattern: Whole Tone (T) + Whole Tone (T) + Semitone (S) · Conjunct do-dāngi (G-A-B-C + C-D-E-F)",
            [
                (0.0, "0¢", "1/1", "Do (1st)", "#0F172A"),
                (203.9, "+203.9¢", "9/8", "Re (Pythagorean 9/8)", "#2563EB"),
                (407.8, "+407.8¢", "81/64 | 5/4", "Mi (Marāghī 81/64 vs Urmawī 5/4)", "#D97706"),
                (498.0, "+498.0¢", "4/3", "Fa (4/3)", "#16A34A"),
            ],
            "L1 (Source): 200 + 180 + 120 = 500¢ (~20¢ grid)  ·  L2 (Rational): 9/8 (203.9¢) + 9/8 (203.9¢) + 256/243 (90.2¢) = 498.0¢  [Just 5:4 = 386.3¢]",
            "L3 (Empirical): 13-master consensus Re = +201.5¢, Mi = +400.8¢ (individual range 386.6–414.7¢; 6 masters cluster near 81/64: Borumand 414.7¢, Ebadi 412.0¢)",
            250, 134
        ),
        (
            "3. Dāng-e Chahārgāh (Twin Symmetrical Augmented-2nd Dāngs)",
            "Pattern: Neutral 2nd (N) + Augmented 2nd (A) + Semitone (S) · Symmetrical pairs on Do and Sol",
            [
                (0.0, "0¢", "1/1", "Do / Sol", "#0F172A"),
                (138.6, "+138.6¢", "13/12", "Reᵏ / Laᵏ (13/12)", "#DC2626"),
                (407.8, "+407.8¢", "81/64 [5/4]", "Mi / Si (81/64)", "#D97706"),
                (498.0, "+498.0¢", "4/3", "Fa / Do' (4/3)", "#16A34A"),
            ],
            "L1 (Source): 140 + 240 + 120 = 500¢ (~20¢ grid)  ·  L2 (Rational): 13/12 (138.6¢) + 243/208 (269.2¢) + 256/243 (90.2¢) = 498.0¢  [Mofakham 15/13 = 247.7¢]",
            "L3 (Empirical): 12-master consensus Reᵏ = +138.7¢, Mi = +402.3¢, Fa = +497.1¢ · Aug 2nd span = 263.6¢",
            394, 134
        ),
        (
            "4. Dāng-e Esfahān / Minor (Kernel of Bayāt-e Esfahān) &amp; Dāng-e Navā",
            "Pattern: Whole Tone (T) + Semitone (S) + Whole Tone (T) · In S2 p. 92, Talā'ī lists 4th dāng as Navā (200+80+220¢)",
            [
                (0.0, "0¢", "1/1", "Do (1st)", "#0F172A"),
                (203.9, "+203.9¢", "9/8", "Re (9/8)", "#2563EB"),
                (294.1, "+294.1¢", "32/27 | 6/5", "Mi♭ (32/27 Pyth vs 6/5 Just)", "#9333EA"),
                (498.0, "+498.0¢", "4/3", "Fa (4/3)", "#16A34A"),
            ],
            "L1 (Source): Navā (S2 p. 92) = 200 + 80 + 220 = 500¢; Minor (Esfahān lower dāng) = 200 + 100 + 200 = 500¢  ·  L2 (Rational): 9/8 + 256/243 + 9/8 = 498.0¢",
            "L3 (Empirical): Measured in Bayāt-e Esfahān: Re = +201.2¢, Mi♭ = +294.5¢, Fa = +497.8¢ · Coupled with Upper Chahārgāh on Sol",
            538, 134
        ),
    ]

    for title, subtitle, notes, l1_l2, l3, y, bh in dangs:
        svg.append(f'<rect x="50" y="{y}" width="{w-100}" height="{bh}" class="ruler-bg"/>')
        svg.append(f'<text x="70" y="{y+21}" font-size="12.5" font-weight="700" fill="#0F172A">{title}</text>')
        svg.append(f'<text x="{w-70}" y="{y+21}" font-size="11" font-weight="500" fill="#64748B" text-anchor="end">{subtitle}</text>')

        ry = y + 62
        svg.append(f'<line x1="{x0}" y1="{ry}" x2="{x1}" y2="{ry}" stroke="#94A3B8" stroke-width="2.5" stroke-linecap="round"/>')

        for c_val, c_str, rat_str, lbl, col in notes:
            xx = x0 + (c_val / 498.0) * span
            svg.append(f'<line x1="{xx:.1f}" y1="{ry-6}" x2="{xx:.1f}" y2="{ry+6}" stroke="{col}" stroke-width="1.8"/>')
            svg.append(f'<circle cx="{xx:.1f}" cy="{ry}" r="5.5" fill="{col}" stroke="#FFFFFF" stroke-width="1.5"/>')

            # Above ruler: ratio and cents
            svg.append(f'<text x="{xx:.1f}" y="{ry-18}" font-size="10.5" font-weight="700" fill="{col}" text-anchor="middle">{rat_str}</text>')
            svg.append(f'<text x="{xx:.1f}" y="{ry-7}" font-size="9.5" font-weight="600" class="mono" fill="{col}" text-anchor="middle">{c_str}</text>')

            # Below ruler: note name
            svg.append(f'<text x="{xx:.1f}" y="{ry+20}" font-size="10.5" font-weight="600" fill="#1E293B" text-anchor="middle">{lbl}</text>')

        # Explanatory 3-layer text lines
        svg.append(f'<text x="70" y="{y+104}" font-size="10" fill="#334155"><tspan class="mono" font-weight="700" fill="#1E40AF">• </tspan>{l1_l2}</text>')
        svg.append(f'<text x="70" y="{y+121}" font-size="10" fill="#475569"><tspan class="mono" font-weight="700" fill="#047857">• </tspan>{l3}</text>')

    # 5. SUPERIMPOSED RULER ON STRING 1 (Do) WITH RESOLVED PHANTOM FRET SPLITTING
    y5 = 684
    bh5 = 412
    svg.append(f'<rect x="50" y="{y5}" width="{w-100}" height="{bh5}" class="super-bg"/>')
    svg.append(f'<text x="70" y="{y5+26}" font-size="14.5" font-weight="800" fill="#1E3A8A">5. Superimposed Setār String 1 Architecture: Splitting the "Phantom Fret" into 39/32 vs 27/22</text>')
    svg.append(f'<text x="{w-70}" y="{y5+26}" font-size="12" font-weight="600" fill="#2563EB" text-anchor="end">Fretboard Coordinates &amp; Mathematical Resolution</text>')

    ry5 = y5 + 138
    svg.append(f'<line x1="{x0}" y1="{ry5}" x2="{x1}" y2="{ry5}" stroke="#1E3A8A" stroke-width="3.5" stroke-linecap="round"/>')

    # Frets definition:
    # Notice the explicit separation of 342.5¢ (39/32) and 354.5¢ (27/22)!
    # 342.5¢ is placed on TOP tier with rose badge.
    # 354.5¢ is placed on BOTTOM tier with purple badge.
    # This guarantees ZERO visual overlap and highlights their 12.06¢ mathematical distinction!
    super_frets = [
        # (c_val, c_str, rat_str, lbl, col, top_tier, bot_tier, style_mode)
        (0.0, "0¢", "1/1", "Open Do (All Dāngs)", "#0F172A", "low", "low", "normal"),
        (138.6, "+138.6¢", "13/12 [256/243]", "Reᵏ (Shūr / Chahārgāh)", "#DC2626", "high", "high", "normal"),
        (203.9, "+203.9¢", "9/8", "Re (Māhūr / Esfahān)", "#2563EB", "low", "low", "normal"),
        (294.1, "+294.1¢", "32/27 [6/5]", "Mi♭ (Shūr / Esfahān)", "#2563EB", "high", "high", "normal"),
        # Fret A: Literal Shūr-on-Re transposition
        (342.5, "+342.5¢", "39/32", "Miᵏ (Literal Shūr on Re)", "#E11D48", "high_box", "none", "shur_re"),
        # Fret B: Historical Zalzal Fret / Segāh Mūyeh
        (354.5, "+354.5¢", "27/22", "Miᵏ (Zalzal / Segāh Mūyeh)", "#7C3AED", "none", "bot_box", "zalzal"),
        (407.8, "+407.8¢", "81/64 [5/4]", "Mi (Māhūr / Chahārgāh)", "#D97706", "high", "high", "normal"),
        (498.0, "+498.0¢", "4/3", "Fa (All 4 Dāngs)", "#16A34A", "low", "low", "normal"),
    ]

    for c_val, c_str, rat_str, lbl, col, top_tier, bot_tier, style_mode in super_frets:
        xx = x0 + (c_val / 498.0) * span

        if style_mode == "normal":
            # Y positions for top labels
            if top_tier == "high":
                y_rat = ry5 - 54
                y_cnt = ry5 - 40
                svg.append(f'<line x1="{xx:.1f}" y1="{ry5-8}" x2="{xx:.1f}" y2="{ry5-34}" stroke="{col}" stroke-width="1.2" stroke-opacity="0.6"/>')
            else:
                y_rat = ry5 - 24
                y_cnt = ry5 - 10

            # Y positions for bottom labels
            if bot_tier == "high":
                y_lbl = ry5 + 50
                svg.append(f'<line x1="{xx:.1f}" y1="{ry5+8}" x2="{xx:.1f}" y2="{ry5+36}" stroke="{col}" stroke-width="1.2" stroke-opacity="0.6"/>')
            else:
                y_lbl = ry5 + 24

            svg.append(f'<circle cx="{xx:.1f}" cy="{ry5}" r="6.5" fill="{col}" stroke="#FFFFFF" stroke-width="2"/>')
            svg.append(f'<text x="{xx:.1f}" y="{y_rat}" font-size="11" font-weight="700" fill="{col}" text-anchor="middle">{rat_str}</text>')
            svg.append(f'<text x="{xx:.1f}" y="{y_cnt}" font-size="9.5" font-weight="600" class="mono" fill="{col}" text-anchor="middle">{c_str}</text>')
            svg.append(f'<text x="{xx:.1f}" y="{y_lbl}" font-size="11" font-weight="700" fill="{col}" text-anchor="middle">{lbl}</text>')

        elif style_mode == "shur_re":
            # 342.5¢: Leader line extends UPWARD to top badge
            svg.append(f'<circle cx="{xx:.1f}" cy="{ry5}" r="7" fill="#FFF1F2" stroke="{col}" stroke-width="2.5" stroke-dasharray="2.5,2.5"/>')
            svg.append(f'<line x1="{xx:.1f}" y1="{ry5-8}" x2="{xx:.1f}" y2="{ry5-74}" stroke="{col}" stroke-width="1.5" stroke-dasharray="3,3"/>')
            
            # Top Callout Box
            bw = 146
            bh = 46
            bx = xx - bw/2 - 16  # shift slightly left to keep clear of 354.5
            by = ry5 - 76 - bh
            svg.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw}" height="{bh}" rx="5" fill="#FFF1F2" stroke="{col}" stroke-width="1.4"/>')
            svg.append(f'<text x="{bx+bw/2:.1f}" y="{by+15}" font-size="10.5" font-weight="800" fill="{col}" text-anchor="middle">39/32 = 342.5¢</text>')
            svg.append(f'<text x="{bx+bw/2:.1f}" y="{by+28}" font-size="9.5" font-weight="700" fill="{col}" text-anchor="middle">Literal Shūr on Re</text>')
            svg.append(f'<text x="{bx+bw/2:.1f}" y="{by+40}" font-size="8.5" fill="#9F1239" text-anchor="middle">9/8 &#215; 13/12 · Transposition</text>')

        elif style_mode == "zalzal":
            # 354.5¢: Leader line extends DOWNWARD to bottom badge
            svg.append(f'<circle cx="{xx:.1f}" cy="{ry5}" r="7" fill="#F5F3FF" stroke="{col}" stroke-width="2.5"/>')
            svg.append(f'<line x1="{xx:.1f}" y1="{ry5+8}" x2="{xx:.1f}" y2="{ry5+74}" stroke="{col}" stroke-width="1.8"/>')
            
            # Bottom Callout Box
            bw = 154
            bh = 46
            bx = xx - bw/2 + 18  # shift slightly right to keep clear of 342.5
            by = ry5 + 74
            svg.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw}" height="{bh}" rx="5" fill="#F5F3FF" stroke="{col}" stroke-width="1.5"/>')
            svg.append(f'<text x="{bx+bw/2:.1f}" y="{by+15}" font-size="10.5" font-weight="800" fill="{col}" text-anchor="middle">27/22 = 354.5¢ (Zalzal)</text>')
            svg.append(f'<text x="{bx+bw/2:.1f}" y="{by+28}" font-size="9.5" font-weight="700" fill="{col}" text-anchor="middle">Physical Setār Fret (Mūyeh)</text>')
            svg.append(f'<text x="{bx+bw/2:.1f}" y="{by+40}" font-size="8.5" font-weight="600" fill="#5B21B6" text-anchor="middle">Empirical Consensus = +352.7¢</text>')

    # Bracket showing the 12.06¢ difference between the two frets
    x_342 = x0 + (342.48 / 498.0) * span
    x_354 = x0 + (354.55 / 498.0) * span
    svg.append(f'<line x1="{x_342:.1f}" y1="{ry5+16}" x2="{x_354:.1f}" y2="{ry5+16}" stroke="#0F172A" stroke-width="1.2"/>')
    svg.append(f'<line x1="{x_342:.1f}" y1="{ry5+13}" x2="{x_342:.1f}" y2="{ry5+19}" stroke="#0F172A" stroke-width="1.2"/>')
    svg.append(f'<line x1="{x_354:.1f}" y1="{ry5+13}" x2="{x_354:.1f}" y2="{ry5+19}" stroke="#0F172A" stroke-width="1.2"/>')
    svg.append(f'<text x="{(x_342+x_354)/2:.1f}" y="{ry5+29}" font-size="9" font-weight="700" fill="#0F172A" text-anchor="middle">&#916; = 12.06¢</text>')

    # Legend / Explanatory notes at bottom of superimposition box
    svg.append(f'<line x1="70" y1="{y5+282}" x2="{w-70}" y2="{y5+282}" stroke="#BFDBFE" stroke-width="1"/>')

    svg.append(f'<text x="70" y="{y5+302}" font-size="11.5" font-weight="700" fill="#1E3A8A">• Mathematical &amp; Organological Resolution of the "Phantom Fret" Conundrum:</text>')
    svg.append(f'<text x="90" y="{y5+320}" font-size="10.8" fill="#334155"><tspan font-weight="700" fill="#E11D48">1. Transposition Model (39/32 = 342.5¢):</tspan> If the Shūr dāng [1, 13/12, 32/27, 4/3] is shifted literally to Re (9/8), the 2nd degree falls at 9/8 &#215; 13/12 = 39/32 (342.5¢).</text>')
    svg.append(f'<text x="90" y="{y5+337}" font-size="10.8" fill="#334155"><tspan font-weight="700" fill="#7C3AED">2. Physical Neck Fret (27/22 = 354.5¢):</tspan> Ancient Wosṭā-Zalzal fret (9/8 &#215; 12/11 = 27/22) preserved on the Setār neck since Al-Fārābī (c. 950).</text>')
    svg.append(f'<text x="90" y="{y5+354}" font-size="10.8" fill="#334155"><tspan font-weight="700" fill="#047857">3. Empirical Proof from 1,282 Audio Strikes:</tspan> Measured Segāh Mūyeh sits at <tspan font-weight="700">+352.7¢</tspan> — within <tspan font-weight="700">1.85¢ of Zalzal (27/22)</tspan>, and 10.22¢ away from 39/32! Iranian masters retune this fret to Zalzal rather than playing a literal transposition.</text>')

    svg.append(f'<text x="70" y="{y5+380}" font-size="11.5" font-weight="700" fill="#1E3A8A">• Decoupled 3-Layer Epistemology:</text>')
    svg.append(f'<text x="90" y="{y5+398}" font-size="10.8" fill="#475569"><tspan font-weight="600" fill="#1E40AF">Layer 1 (Source):</tspan> Talā\'ī\'s ~20¢ grid (500¢ sum) captures pedagogical morphology  ·  <tspan font-weight="600" fill="#B45309">Layer 2 (Rational):</tspan> Pure mathematical ratios span exact pure 4th (498.05¢)  ·  <tspan font-weight="600" fill="#047857">Layer 3 (Empirical):</tspan> Acoustic pitch peaks confirm physical fretting traditions.</text>')

    svg.append('</svg>')

    svg_content = "\n".join(svg)
    svg_path = "figures/talai_dangs_architecture.svg"
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Wrote {svg_path}")

    # Convert to PNG at high res (width=2640)
    png_path = "figures/talai_dangs_architecture.png"
    cmd = [
        "/opt/homebrew/bin/rsvg-convert",
        "-f", "png",
        "-w", "2640",
        "-o", png_path,
        svg_path
    ]
    subprocess.run(cmd, check=True)
    print(f"Generated {png_path} ({os.path.getsize(png_path):,} bytes)")

if __name__ == "__main__":
    generate_talai_chart()
