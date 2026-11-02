import subprocess
import os

def generate_talai_chart():
    # Width and height of the standalone chart
    w = 1280
    h = 1060

    # Margins and ruler coordinates
    x0 = 140
    x1 = 1140
    span = x1 - x0

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    svg.append("""<defs>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&amp;family=JetBrains+Mono:wght@500;700&amp;display=swap');
  text { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
  .mono { font-family: 'JetBrains Mono', monospace; }
  .title { font-weight: 800; fill: #0F172A; }
  .subtitle { fill: #475569; font-size: 13.5px; }
  .ruler-bg { fill: #F8FAFC; stroke: #CBD5E1; stroke-width: 1.2; rx: 10px; }
  .super-bg { fill: #F0F7FF; stroke: #2563EB; stroke-width: 2; rx: 12px; }
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
    svg.append('<text x="55" y="65" font-size="24" class="title">Dariush Tala\'i\'s Theory of Dāngs &amp; Setār Neck Architecture</text>')
    svg.append('<text x="55" y="90" font-size="13" class="subtitle">The 4 Elemental Tetrachords (Dāngs), Pure Mathematical Ratios, Historical Variants, and String 1 (Do) Superimposition</text>')

    # 4 Dāngs definition
    dangs = [
        (
            "1. Dāng-e Shūr (Root of Shūr, Dashti, Navā, Abū’atā, Afshārī)",
            "Interval Pattern: Neutral 2nd (N) + Neutral 2nd (N) + Whole Tone (T)",
            [
                (0.0, "0¢", "1/1", "Tonic (Do)", "#0F172A"),
                (138.6, "+138.6¢", "13/12 [256/243]", "Reᵏ (Fārābī / Qajar Limma)", "#DC2626"),
                (294.1, "+294.1¢", "32/27 [6/5]", "Mi♭ (Pythagorean / Just)", "#2563EB"),
                (498.0, "+498.0¢", "4/3", "Pure 4th (Fa)", "#16A34A"),
            ],
            "Steps: 13/12 (138.6¢) + 155.5¢ + 9/8 (203.9¢) = 4/3 (498.0¢) · Historical: Limma 256/243 (90.2¢) in early Qajar radifs",
            116, 128
        ),
        (
            "2. Dāng-e Māhūr (Root of Māhūr &amp; Rāst-Panjgāh)",
            "Interval Pattern: Whole Tone (T) + Whole Tone (T) + Semitone (S)",
            [
                (0.0, "0¢", "1/1", "Do (1st)", "#0F172A"),
                (203.9, "+203.9¢", "9/8", "Re (Pythagorean 9/8)", "#2563EB"),
                (407.8, "+407.8¢", "81/64 | 5/4", "Mi (Marāghī 81/64 vs Urmawī 5/4)", "#D97706"),
                (498.0, "+498.0¢", "4/3", "Fa (4/3)", "#16A34A"),
            ],
            "Steps: 9/8 (203.9¢) + 9/8 (203.9¢) + 256/243 (90.2¢) = 4/3 · Measured 13-master consensus: Re = 201.5¢, Mi = 400.8¢",
            258, 128
        ),
        (
            "3. Dāng-e Chahārgāh (Twin Symmetrical Augmented-2nd Dāngs)",
            "Interval Pattern: Neutral 2nd (N) + Augmented 2nd (A) + Semitone (S)",
            [
                (0.0, "0¢", "1/1", "Do / Sol", "#0F172A"),
                (138.6, "+138.6¢", "13/12", "Reᵏ / Laᵏ (13/12)", "#DC2626"),
                (407.8, "+407.8¢", "81/64", "Mi / Si (81/64)", "#D97706"),
                (498.0, "+498.0¢", "4/3", "Fa / Do↑ (4/3)", "#16A34A"),
            ],
            "Steps: 13/12 (~139¢) + Augmented 2nd (~269¢) + Limma (~90¢) = 4/3 · Measured 12-master consensus: Reᵏ = 138.7¢, Mi = 402.3¢",
            400, 128
        ),
        (
            "4. Dāng-e Esfahān / Minor (Kernel of Bayāt-e Esfahān)",
            "Interval Pattern: Whole Tone (T) + Semitone (S) + Whole Tone (T)",
            [
                (0.0, "0¢", "1/1", "Do (1st)", "#0F172A"),
                (203.9, "+203.9¢", "9/8", "Re (9/8)", "#2563EB"),
                (294.1, "+294.1¢", "32/27 | 6/5", "Mi♭ (32/27 Pyth vs 6/5 Just)", "#9333EA"),
                (498.0, "+498.0¢", "4/3", "Fa (4/3)", "#16A34A"),
            ],
            "Steps: 9/8 (203.9¢) + 256/243 (90.2¢) + 9/8 (203.9¢) = 4/3 · Lower dāng of Bayāt-e Esfahān; couples with Upper Chahārgāh at 5th",
            542, 128
        ),
    ]

    for title, subtitle, notes, desc, y, bh in dangs:
        svg.append(f'<rect x="50" y="{y}" width="{w-100}" height="{bh}" class="ruler-bg"/>')
        svg.append(f'<text x="70" y="{y+23}" font-size="13" font-weight="700" fill="#0F172A">{title}</text>')
        svg.append(f'<text x="{w-70}" y="{y+23}" font-size="11" font-weight="500" fill="#64748B" text-anchor="end">{subtitle}</text>')

        ry = y + 66
        svg.append(f'<line x1="{x0}" y1="{ry}" x2="{x1}" y2="{ry}" stroke="#94A3B8" stroke-width="2.5" stroke-linecap="round"/>')

        for c_val, c_str, rat_str, lbl, col in notes:
            xx = x0 + (c_val / 498.0) * span
            svg.append(f'<line x1="{xx:.1f}" y1="{ry-6}" x2="{xx:.1f}" y2="{ry+6}" stroke="{col}" stroke-width="1.8"/>')
            svg.append(f'<circle cx="{xx:.1f}" cy="{ry}" r="6" fill="{col}" stroke="#FFFFFF" stroke-width="1.5"/>')

            # Above ruler: ratio and cents
            svg.append(f'<text x="{xx:.1f}" y="{ry-20}" font-size="11" font-weight="700" fill="{col}" text-anchor="middle">{rat_str}</text>')
            svg.append(f'<text x="{xx:.1f}" y="{ry-8}" font-size="10" font-weight="600" class="mono" fill="{col}" text-anchor="middle">{c_str}</text>')

            # Below ruler: note name
            svg.append(f'<text x="{xx:.1f}" y="{ry+22}" font-size="11" font-weight="600" fill="#1E293B" text-anchor="middle">{lbl}</text>')

        # Explanatory foot text
        svg.append(f'<text x="70" y="{y+114}" font-size="10.5" fill="#475569">{desc}</text>')

    # 5. SUPERIMPOSED RULER ON STRING 1 (Do)
    y5 = 688
    bh5 = 328
    svg.append(f'<rect x="50" y="{y5}" width="{w-100}" height="{bh5}" class="super-bg"/>')
    svg.append(f'<text x="70" y="{y5+28}" font-size="14.5" font-weight="800" fill="#1E3A8A">5. All 4 Dāngs Superimposed on Setār String 1 (Do Fretboard Architecture)</text>')
    svg.append(f'<text x="{w-70}" y="{y5+28}" font-size="12" font-weight="600" fill="#2563EB" text-anchor="end">Pure Ratios, Cents &amp; Physical Frets</text>')

    ry5 = y5 + 132
    svg.append(f'<line x1="{x0}" y1="{ry5}" x2="{x1}" y2="{ry5}" stroke="#1E3A8A" stroke-width="3.5" stroke-linecap="round"/>')

    # Frets definitions with staggered vertical tiers to guarantee zero overlap
    # Re^k (+138.6¢) has top_tier="high", bot_tier="high"
    # Re (+203.9¢) has top_tier="low", bot_tier="low"
    # Mi-flat (+294.1¢) has top_tier="high", bot_tier="high"
    # Mi^k (+342.5¢) is phantom badge
    # Mi (+407.8¢) has top_tier="high", bot_tier="high"
    super_frets = [
        (0.0, "0¢", "1/1", "Open Do (All)", "#0F172A", "low", "low", False),
        (138.6, "+138.6¢", "13/12 [256/243]", "Reᵏ (Shūr / Chahārgāh)", "#DC2626", "high", "high", False),
        (203.9, "+203.9¢", "9/8", "Re (Māhūr / Esfahān)", "#2563EB", "low", "low", False),
        (294.1, "+294.1¢", "32/27 [6/5]", "Mi♭ (Shūr / Esfahān)", "#7C3AED", "high", "high", False),
        (342.5, "+342.5¢", "117/96 [27/22]", "Miᵏ (Phantom Fret from Re-dāng!)", "#E11D48", "low", "low", True),
        (407.8, "+407.8¢", "81/64 [5/4]", "Mi (Māhūr / Chahārgāh)", "#D97706", "high", "high", False),
        (498.0, "+498.0¢", "4/3", "Fa (All 4 Dāngs)", "#16A34A", "low", "low", False),
    ]

    for c_val, c_str, rat_str, lbl, col, top_tier, bot_tier, is_phantom in super_frets:
        xx = x0 + (c_val / 498.0) * span

        # Y positions for top labels
        if top_tier == "high":
            y_rat = ry5 - 54
            y_cnt = ry5 - 40
            svg.append(f'<line x1="{xx:.1f}" y1="{ry5-10}" x2="{xx:.1f}" y2="{ry5-34}" stroke="{col}" stroke-width="1.2" stroke-opacity="0.6"/>')
        else:
            y_rat = ry5 - 24
            y_cnt = ry5 - 10

        # Y positions for bottom labels
        if bot_tier == "high":
            y_lbl = ry5 + 52
            svg.append(f'<line x1="{xx:.1f}" y1="{ry5+10}" x2="{xx:.1f}" y2="{ry5+38}" stroke="{col}" stroke-width="1.2" stroke-opacity="0.6"/>')
        else:
            y_lbl = ry5 + 24

        if is_phantom:
            # Dashed circle and tall highlight guideline
            svg.append(f'<circle cx="{xx:.1f}" cy="{ry5}" r="8.5" fill="#FFF1F2" stroke="{col}" stroke-width="2.5" stroke-dasharray="3,3"/>')
            svg.append(f'<line x1="{xx:.1f}" y1="{ry5-68}" x2="{xx:.1f}" y2="{ry5+80}" stroke="{col}" stroke-width="1.5" stroke-dasharray="3,3" stroke-opacity="0.7"/>')
            
            # Badge for ratio/cents
            bw = 114
            svg.append(f'<rect x="{xx-bw/2:.1f}" y="{y_rat-14}" width="{bw}" height="28" rx="4" fill="#FEE2E2" stroke="#E11D48" stroke-width="1"/>')
            svg.append(f'<text x="{xx:.1f}" y="{y_rat}" font-size="10.5" font-weight="700" fill="{col}" text-anchor="middle">{rat_str}</text>')
            svg.append(f'<text x="{xx:.1f}" y="{y_cnt}" font-size="9.5" font-weight="700" class="mono" fill="{col}" text-anchor="middle">{c_str}</text>')
            svg.append(f'<text x="{xx:.1f}" y="{y_lbl}" font-size="11" font-weight="800" fill="{col}" text-anchor="middle">{lbl}</text>')
        else:
            svg.append(f'<circle cx="{xx:.1f}" cy="{ry5}" r="6.5" fill="{col}" stroke="#FFFFFF" stroke-width="2"/>')
            svg.append(f'<text x="{xx:.1f}" y="{y_rat}" font-size="11" font-weight="700" fill="{col}" text-anchor="middle">{rat_str}</text>')
            svg.append(f'<text x="{xx:.1f}" y="{y_cnt}" font-size="9.5" font-weight="600" class="mono" fill="{col}" text-anchor="middle">{c_str}</text>')
            svg.append(f'<text x="{xx:.1f}" y="{y_lbl}" font-size="11.5" font-weight="700" fill="{col}" text-anchor="middle">{lbl}</text>')

    # Legend / Explanatory notes at bottom of superimposition box
    svg.append(f'<line x1="70" y1="{y5+210}" x2="{w-70}" y2="{y5+210}" stroke="#BFDBFE" stroke-width="1"/>')

    svg.append(f'<text x="70" y="{y5+232}" font-size="11.5" font-weight="700" fill="#1E3A8A">• Dual Historical Variant Ratios [in brackets]:</text>')
    svg.append(f'<text x="90" y="{y5+251}" font-size="11" fill="#334155"><tspan font-weight="600">Neutral 2nd:</tspan> Al-Fārābī superparticular 13/12 (138.6¢) vs Pythagorean limma 256/243 (90.2¢) in old Qajar lineages.</text>')
    svg.append(f'<text x="90" y="{y5+268}" font-size="11" fill="#334155"><tspan font-weight="600">Minor 3rd:</tspan> Marāghī Pythagorean 32/27 (294.1¢) vs Just 6/5 (315.6¢) · <tspan font-weight="600">Major 3rd:</tspan> Marāghī 81/64 (407.8¢) vs Urmawī 5/4 (386.3¢).</text>')

    svg.append(f'<text x="70" y="{y5+294}" font-size="11.5" font-weight="700" fill="#BE123C">• Why is there no Mi-koron (Miᵏ) in any Do-dāng?</text>')
    svg.append(f'<text x="90" y="{y5+311}" font-size="11" fill="#475569">None of the 4 elemental Do-dāngs generate Miᵏ. The physical neck fret at ~343¢ is born ONLY when a dāng is rooted on Re (9/8 &#215; 13/12 = 117/96 = 342.5¢, or ancient Zalzal 27/22 = 354.5¢)!</text>')

    svg.append('</svg>')

    svg_content = "\n".join(svg)
    svg_path = "figures/talai_dangs_architecture.svg"
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Wrote {svg_path}")

    # Convert to PNG at high res (width=2560)
    png_path = "figures/talai_dangs_architecture.png"
    cmd = [
        "/opt/homebrew/bin/rsvg-convert",
        "-f", "png",
        "-w", "2560",
        "-o", png_path,
        svg_path
    ]
    subprocess.run(cmd, check=True)
    print(f"Generated {png_path} ({os.path.getsize(png_path):,} bytes)")

if __name__ == "__main__":
    generate_talai_chart()
