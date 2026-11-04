import subprocess
from pathlib import Path

# Create dedicated SVG diagram for the 5 Secondary Avazes
W, H = 1400, 980
svg = []
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
svg.append(f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>')

# Title banner
svg.append('<rect x="36" y="24" width="1328" height="70" rx="8" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1.5"/>')
svg.append('<text x="56" y="52" font-size="22" font-weight="800" fill="#0F172A">The 5 Secondary Āvāzes: Branching Architecture from Dastgāh-e Shūr</text>')
svg.append('<text x="56" y="76" font-size="13" fill="#64748B">Empirical Analysis Across 18,632 Note Strikes &amp; Modal Mechanics (Īst, Shāhed, Motaghayyer Shifts)</text>')

# Left Trunk: Mother Mode Shur
svg.append('<rect x="36" y="115" width="380" height="825" rx="10" fill="#F1F5F9" stroke="#94A3B8" stroke-width="2"/>')
svg.append('<rect x="46" y="125" width="360" height="42" rx="6" fill="#1E293B"/>')
svg.append('<text x="226" y="152" font-size="16" font-weight="800" fill="#FFFFFF" text-anchor="middle">TRUNK: DASTGĀH-E SHŪR</text>')

# Shur explanation
svg.append('<text x="56" y="195" font-size="13" font-weight="700" fill="#0F172A">The Mother System (Umm al-Maqāmāt):</text>')
svg.append('<text x="56" y="215" font-size="12" fill="#475569">Two symmetrical Dāng-e Shūr [S + S] joined by 9/8 tone:</text>')
svg.append('<text x="56" y="235" font-size="11.5" class="mono" font-weight="700" fill="#2563EB">Dāng 1: Do(0¢) → Reᵏ(+139¢) → Mi♭(+294¢) → Fa(+498¢)</text>')
svg.append('<text x="56" y="255" font-size="11.5" class="mono" font-weight="700" fill="#059669">Dāng 2: Sol(702¢) → Laᵏ(841¢) → Si♭(996¢) → Do(1200¢)</text>')

# Fretboard schematic of Shur
fret_y = 280
frets = [
    ("Do (Tonic / Īst)", 0, "#0F172A", True),
    ("Re-koron (Attr)", 139, "#D97706", True),
    ("Mi-flat", 294, "#2563EB", False),
    ("Fa (Top Dāng 1)", 498, "#059669", True),
    ("Sol (Panjgāh)", 702, "#0F172A", True),
    ("La-koron (Qaracheh)", 841, "#D97706", True),
    ("Si-flat (Razavi)", 996, "#2563EB", False),
    ("Do (Octave)", 1200, "#0F172A", True),
]

svg.append(f'<line x1="80" y1="{fret_y}" x2="80" y2="{fret_y + 360}" stroke="#475569" stroke-width="6"/>')
for i, (name, c, col, major) in enumerate(frets):
    fy = fret_y + int(i * 50)
    svg.append(f'<line x1="60" y1="{fy}" x2="100" y2="{fy}" stroke="{col}" stroke-width="{3 if major else 1.5}"/>')
    svg.append(f'<circle cx="80" cy="{fy}" r="{6 if major else 4}" fill="{col}"/>')
    svg.append(f'<text x="110" y="{fy+4}" font-size="12" font-weight="{700 if major else 500}" fill="{col}">{name} [{c}¢]</text>')

svg.append('<rect x="50" y="700" width="352" height="225" rx="6" fill="#FFFFFF" stroke="#CBD5E1"/>')
svg.append('<text x="65" y="725" font-size="13" font-weight="700" fill="#0F172A">Empirical Strike Corpus (5 Āvāzes):</text>')
svg.append('<text x="65" y="750" font-size="12" fill="#334155">• <tspan font-weight="700">Total Analyzed Strikes:</tspan> 18,632 strikes</text>')
svg.append('<text x="65" y="770" font-size="12" fill="#334155">• <tspan font-weight="700">Canonical Radif Tracks:</tspan> 89 tracks</text>')
svg.append('<text x="65" y="790" font-size="12" fill="#334155">• <tspan font-weight="700">Masters:</tspan> Borumand, Karimi, Shahnazi,</text>')
svg.append('<text x="75" y="810" font-size="12" fill="#334155">Hormozi, Alizadeh, Saba, Ebadi, Kasaei</text>')
svg.append('<text x="65" y="835" font-size="12" fill="#059669" font-weight="700">Branching Mechanism:</text>')
svg.append('<text x="65" y="855" font-size="11.5" fill="#475569">Each Āvāz preserves the core fretboard of</text>')
svg.append('<text x="65" y="873" font-size="11.5" fill="#475569">Shūr, but completely reorganizes its musical</text>')
svg.append('<text x="65" y="891" font-size="11.5" fill="#475569">hierarchy via Īst, Shāhed, or Motaghayyer.</text>')

# 5 Branches on the Right
avazes_data = [
    {
        "name": "1. ĀVĀZ-E ABŪ'ATĀ",
        "trans": "Shift: Melodic Focal Center (Shāhed) → 2nd Degree (Re-koron, +139¢)",
        "kernel": "Do (Īst / Pedestal) ↔ Reᵏ (Shāhed / Axis) ↔ Mi♭ (Peak)",
        "desc": "While resting on Do, the entire melodic energy revolves around Re-koron. Movement leaps between Do and Mi♭ through Reᵏ with characteristic undulating motifs (Sayakhi, Ramkali, Hejāz). In Hejāz, the mode climbs to the 5th (Sol) with a dramatic shift to Dāng-e Chahārgāh/Homāyūn flavor.",
        "strikes": "3,345 strikes across 21 tracks (Shahnazi, Karimi, Forutan)",
        "color": "#2563EB",
        "bg": "#EFF6FF",
        "border": "#BFDBFE"
    },
    {
        "name": "2. ĀVĀZ-E BAYĀT-E TORK (BAYĀT-E ZAND)",
        "trans": "Shift: Resting Tone (Īst) &amp; Focal Center (Shāhed) → 3rd Degree (Mi-flat, +294¢)",
        "kernel": "Mi♭ (Primary Īst &amp; Shāhed) | Fa (Peak) | Do (Lower Root / Final Foroud)",
        "desc": "By treating Mi♭ as the principal resting tone, Bayāt-e Tork produces a warm, major-like spiritual resonance despite sharing Shūr frets. Famously used in the Iranian Adhān (by Rahim Moazenzadeh) and Sufi cantillation (Masnavi, Rowh al-Arvāh). The lower Do acts as an occasional solemn anchor.",
        "strikes": "2,034 strikes across 16 tracks (Borumand Mirza Abdollah Vol 2, Karimi, Shahnazi)",
        "color": "#059669",
        "bg": "#F0FDF4",
        "border": "#BBF7D0"
    },
    {
        "name": "3. ĀVĀZ-E AFSHĀRĪ",
        "trans": "Shift: Tonal Axis → 4th (Fa) &amp; 5th (Sol) with Dynamic Variable Degree (Motaghayyer)",
        "kernel": "Fa (Primary Īst) | Sol ↔ Solᵏ / Fa♯ (Motaghayyer) | Do (Final Foroud)",
        "desc": "Afshārī possesses one of the most poignant emotional signatures. The melody hovers around Fa and Sol, but the 5th degree is motaghayyer: in descending cadences it is pulled flat into Sol-koron (~640¢-660¢), creating an agonizing, unresolved tension before releasing into lower Shūr.",
        "strikes": "4,278 strikes across 16 tracks (Hormozi private setār, Borumand, Karimi, Shahnazi)",
        "color": "#D97706",
        "bg": "#FFFBEB",
        "border": "#FDE68A"
    },
    {
        "name": "4. ĀVĀZ-E DASHTĪ",
        "trans": "Shift: Focal Center (Shāhed) → 5th/6th Degree (Sol / La-koron) + Bimodal Motaghayyer",
        "kernel": "Do (Lower Root) | Sol (Pedestal) | Laᵏ (Shāhed / Climax) | Solᵏ (Variable)",
        "desc": "The quintessential mode of Persian pastoral longing ('the crying of the desert'). Melody ascends rapidly through Dāng 1 to obsessively circle La-koron. In Deylamān and Ouj, the 5th degree drops microtonally into Sol-koron, forming an expressive weeping motif unmatched in Mediterranean modal music.",
        "strikes": "6,671 strikes across 27 tracks (Shahnazi, Karimi, Alizadeh, Saba, Lotfi, Ebadi)",
        "color": "#DC2626",
        "bg": "#FEF2F2",
        "border": "#FECACA"
    },
    {
        "name": "5. BAYĀT-E KORD",
        "trans": "Shift: Re-anchored to Shūr Tonic (Do) with Prolonged Neutral 2nd Tension (Re-koron)",
        "kernel": "Do (Persistent Īst) | Reᵏ (Dramatic Mordent / Sustained Focus) | Mi♭ (Transient)",
        "desc": "Closely aligned with Dashtī and Shūr, Bayāt-e Kord retains the lower Do as its rigid resting point but treats the neutral second (Reᵏ, 13/12) with intense prolonged emphasis and rapid rhythmic mordents. Melodic lines rarely climb beyond the fourth (Fa), creating an austere, meditative chamber atmosphere.",
        "strikes": "2,304 strikes across 9 tracks (Borumand Mirza Abdollah Vol 2 complete, Alizadeh Ocora)",
        "color": "#7C3AED",
        "bg": "#F5F3FF",
        "border": "#DDD6FE"
    }
]

y_branch = 115
branch_h = 153

for i, av in enumerate(avazes_data):
    y = y_branch + i * (branch_h + 15)
    mid_y = y + branch_h // 2
    svg.append(f'<path d="M 416 {mid_y} C 445 {mid_y}, 445 {mid_y}, 460 {mid_y}" fill="none" stroke="{av["color"]}" stroke-width="2.5" stroke-dasharray="4,3"/>')
    svg.append(f'<circle cx="416" cy="{mid_y}" r="4" fill="{av["color"]}"/>')
    svg.append(f'<circle cx="460" cy="{mid_y}" r="4" fill="{av["color"]}"/>')

    svg.append(f'<rect x="460" y="{y}" width="904" height="{branch_h}" rx="8" fill="{av["bg"]}" stroke="{av["border"]}" stroke-width="1.5"/>')
    svg.append(f'<text x="480" y="{y+26}" font-size="15" font-weight="800" fill="{av["color"]}">{av["name"]}</text>')
    svg.append(f'<text x="700" y="{y+26}" font-size="12" font-weight="700" fill="#0F172A">{av["trans"]}</text>')
    
    svg.append(f'<rect x="480" y="{y+38}" width="864" height="26" rx="4" fill="#FFFFFF" stroke="{av["border"]}"/>')
    svg.append(f'<text x="490" y="{y+55}" font-size="12" font-weight="700" fill="#1E293B">Kernel Formula: <tspan font-weight="600" fill="{av["color"]}">{av["kernel"]}</tspan></text>')

    desc_words = av["desc"]
    svg.append(f'<text x="480" y="{y+84}" font-size="12" fill="#334155">{desc_words[:120]}</text>')
    svg.append(f'<text x="480" y="{y+102}" font-size="12" fill="#334155">{desc_words[120:240]}</text>')
    if len(desc_words) > 240:
        svg.append(f'<text x="480" y="{y+120}" font-size="12" fill="#334155">{desc_words[240:]}</text>')

    svg.append(f'<text x="480" y="{y+140}" font-size="11" font-weight="700" fill="#64748B">Empirical Corpus: <tspan font-weight="500">{av["strikes"]}</tspan></text>')

svg.append("</svg>")

out_svg = Path("figures/five_secondary_avazes_branching_tree.svg")
out_svg.write_text("\n".join(svg), encoding="utf-8")
print(f"Wrote {out_svg}")

# Convert to PNG
out_png = Path("figures/five_secondary_avazes_branching_tree.png")
subprocess.run(["/opt/homebrew/bin/rsvg-convert", "-f", "png", "-w", "2800", "-o", str(out_png), str(out_svg)], check=True)
print(f"Rendered PNG -> {out_png}")
