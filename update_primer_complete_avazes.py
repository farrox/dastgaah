import subprocess
from pathlib import Path

primer_path = Path("analysis/make_theory_primer.py")
content = primer_path.read_text(encoding="utf-8")

# Let's inspect page12 implementation to render the full visual tree layout
new_page12 = '''def page12() -> str:
    o = header(12, "12. The 5 Secondary Āvāzes: Branching Architecture from Dastgāh-e Shūr",
               "Empirical Analysis of 18,632 Note Strikes Across 89 Radif Tracks (Borumand, Karimi, Shahnazi, Hormozi, Alizadeh)")

    # Left Column: The Shur Mother Trunk (x=36, y=100, w=340, h=860)
    card(o, 36, 100, 350, 860, "Trunk: Dastgāh-e Shūr", "Mother Mode (Umm al-Maqāmāt)")
    
    o.append('<text x="56" y="150" font-size="12" font-weight="700" fill="#0F172A">Two Symmetrical Dāng-e Shūr [S + S]:</text>')
    o.append('<text x="56" y="170" font-size="11" class="mono" font-weight="700" fill="#2563EB">Dāng 1: Do(0¢)→Reᵏ(139¢)→Mi♭(294¢)→Fa(498¢)</text>')
    o.append('<text x="56" y="188" font-size="11" class="mono" font-weight="700" fill="#059669">Dāng 2: Sol(702¢)→Laᵏ(841¢)→Si♭(996¢)→Do(1200¢)</text>')

    # Vertical fretboard ruler of Shur
    fret_y = 220
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
    o.append(f'<line x1="80" y1="{fret_y}" x2="80" y2="{fret_y + 350}" stroke="#64748B" stroke-width="4"/>')
    for i, (name, c, col, major) in enumerate(frets):
        fy = fret_y + int(i * 50)
        o.append(f'<line x1="65" y1="{fy}" x2="95" y2="{fy}" stroke="{col}" stroke-width="{2.5 if major else 1.5}"/>')
        o.append(f'<circle cx="80" cy="{fy}" r="{5 if major else 3.5}" fill="{col}"/>')
        o.append(f'<text x="105" y="{fy+4}" font-size="11.5" font-weight="{700 if major else 500}" fill="{col}">{esc(name)} [{c}¢]</text>')

    # Bottom summary box in trunk card
    o.append('<rect x="50" y="640" width="322" height="300" rx="6" fill="#F8FAFC" stroke="#CBD5E1"/>')
    o.append('<text x="65" y="665" font-size="12" font-weight="700" fill="#0F172A">Empirical Strike Corpus (89 Tracks):</text>')
    o.append('<text x="65" y="688" font-size="11" fill="#334155">• <tspan font-weight="700">Abū’atā:</tspan> 3,345 strikes (21 tracks)</text>')
    o.append('<text x="65" y="706" font-size="11" fill="#334155">• <tspan font-weight="700">Bayāt-e Tork:</tspan> 2,034 strikes (16 tracks)</text>')
    o.append('<text x="65" y="724" font-size="11" fill="#334155">• <tspan font-weight="700">Afshārī:</tspan> 4,278 strikes (16 tracks)</text>')
    o.append('<text x="65" y="742" font-size="11" fill="#334155">• <tspan font-weight="700">Dashtī:</tspan> 6,671 strikes (27 tracks)</text>')
    o.append('<text x="65" y="760" font-size="11" fill="#334155">• <tspan font-weight="700">Bayāt-e Kord:</tspan> 2,304 strikes (9 tracks)</text>')
    o.append('<text x="65" y="782" font-size="11.5" font-weight="700" fill="#2563EB">Total: 18,632 Note Strikes</text>')
    o.append('<line x1="65" y1="795" x2="355" y2="795" stroke="#E2E8F0" stroke-width="1"/>')
    o.append('<text x="65" y="818" font-size="11" font-weight="700" fill="#059669">Three Branching Operations:</text>')
    o.append('<text x="65" y="838" font-size="10.5" fill="#475569">1. <tspan font-weight="600">Shāhed Shift:</tspan> Reᵏ (Abū’atā), Laᵏ (Dashtī)</text>')
    o.append('<text x="65" y="856" font-size="10.5" fill="#475569">2. <tspan font-weight="600">Īst Mutation:</tspan> Mi♭ (Bayāt-e Tork), Fa (Afshārī)</text>')
    o.append('<text x="65" y="874" font-size="10.5" fill="#475569">3. <tspan font-weight="600">Motaghayyer:</tspan> Sol ↔ Solᵏ in Afshārī &amp; Dashtī</text>')
    o.append('<text x="65" y="900" font-size="10" font-weight="700" fill="#DC2626">Zero new frets needed on the Setār neck!</text>')

    # Right Branches: 5 Dedicated Cards (x=410, w=954, h=160 each)
    avazes_data = [
        {
            "name": "1. ĀVĀZ-E ABŪ'ATĀ",
            "trans": "Shift: Melodic Focal Center (Shāhed) → 2nd Degree (Re-koron, +139¢)",
            "kernel": "Do (Īst / Pedestal) ↔ Reᵏ (Shāhed / Axis) ↔ Mi♭ (Peak)",
            "desc": "While resting on Do, the entire melodic energy revolves around Re-koron. Movement leaps between Do and Mi♭ through Reᵏ with characteristic undulating motifs (Sayakhi, Ramkali, Hejāz). In Hejāz, the mode climbs to the 5th (Sol) with a dramatic shift to Dāng-e Chahārgāh/Homāyūn flavor.",
            "strikes": "3,345 strikes across 21 tracks (Shahnazi, Karimi, Forutan)",
            "color": "#2563EB", "bg": "#EFF6FF", "border": "#BFDBFE"
        },
        {
            "name": "2. ĀVĀZ-E BAYĀT-E TORK (BAYĀT-E ZAND)",
            "trans": "Shift: Resting Tone (Īst) &amp; Focal Center (Shāhed) → 3rd Degree (Mi-flat, +294¢)",
            "kernel": "Mi♭ (Primary Īst &amp; Shāhed) | Fa (Peak) | Do (Lower Root / Final Foroud)",
            "desc": "By treating Mi♭ as the principal resting tone, Bayāt-e Tork produces a warm, major-like spiritual resonance despite sharing Shūr frets. Famously used in the Iranian Adhān (by Rahim Moazenzadeh) and Sufi cantillation (Masnavi, Rowh al-Arvāh). The lower Do acts as an occasional solemn anchor.",
            "strikes": "2,034 strikes across 16 tracks (Borumand Mirza Abdollah Vol 2, Karimi, Shahnazi)",
            "color": "#059669", "bg": "#F0FDF4", "border": "#BBF7D0"
        },
        {
            "name": "3. ĀVĀZ-E AFSHĀRĪ",
            "trans": "Shift: Tonal Axis → 4th (Fa) &amp; 5th (Sol) with Dynamic Variable Degree (Motaghayyer)",
            "kernel": "Fa (Primary Īst) | Sol ↔ Solᵏ / Fa♯ (Motaghayyer) | Do (Final Foroud)",
            "desc": "Afshārī possesses one of the most poignant emotional signatures. The melody hovers around Fa and Sol, but the 5th degree is motaghayyer: in descending cadences it is pulled flat into Sol-koron (~640¢-660¢), creating an agonizing, unresolved tension before releasing into lower Shūr.",
            "strikes": "4,278 strikes across 16 tracks (Hormozi private setār, Borumand, Karimi, Shahnazi)",
            "color": "#D97706", "bg": "#FFFBEB", "border": "#FDE68A"
        },
        {
            "name": "4. ĀVĀZ-E DASHTĪ",
            "trans": "Shift: Focal Center (Shāhed) → 5th/6th Degree (Sol / La-koron) + Bimodal Motaghayyer",
            "kernel": "Do (Lower Root) | Sol (Pedestal) | Laᵏ (Shāhed / Climax) | Solᵏ (Variable)",
            "desc": "The quintessential mode of Persian pastoral longing ('the crying of the desert'). Melody ascends rapidly through Dāng 1 to obsessively circle La-koron. In Deylamān and Ouj, the 5th degree drops microtonally into Sol-koron, forming an expressive weeping motif unmatched in Mediterranean modal music.",
            "strikes": "6,671 strikes across 27 tracks (Shahnazi, Karimi, Alizadeh, Saba, Lotfi, Ebadi)",
            "color": "#DC2626", "bg": "#FEF2F2", "border": "#FECACA"
        },
        {
            "name": "5. BAYĀT-E KORD",
            "trans": "Shift: Re-anchored to Shūr Tonic (Do) with Prolonged Neutral 2nd Tension (Re-koron)",
            "kernel": "Do (Persistent Īst) | Reᵏ (Dramatic Mordent / Sustained Focus) | Mi♭ (Transient)",
            "desc": "Closely aligned with Dashtī and Shūr, Bayāt-e Kord retains the lower Do as its rigid resting point but treats the neutral second (Reᵏ, 13/12) with intense prolonged emphasis and rapid rhythmic mordents. Melodic lines rarely climb beyond the fourth (Fa), creating an austere, meditative chamber atmosphere.",
            "strikes": "2,304 strikes across 9 tracks (Borumand Mirza Abdollah Vol 2 complete, Alizadeh Ocora)",
            "color": "#7C3AED", "bg": "#F5F3FF", "border": "#DDD6FE"
        }
    ]

    y_branch = 100
    branch_h = 160

    for i, av in enumerate(avazes_data):
        y = y_branch + i * (branch_h + 15)
        mid_y = y + branch_h // 2
        
        # Connector spline from Trunk to branch
        o.append(f'<path d="M 386 {mid_y} C 400 {mid_y}, 400 {mid_y}, 410 {mid_y}" fill="none" stroke="{av["color"]}" stroke-width="2.5" stroke-dasharray="4,3"/>')
        o.append(f'<circle cx="386" cy="{mid_y}" r="3.5" fill="{av["color"]}"/>')
        o.append(f'<circle cx="410" cy="{mid_y}" r="3.5" fill="{av["color"]}"/>')

        # Branch card
        o.append(f'<rect x="410" y="{y}" width="954" height="{branch_h}" rx="8" fill="{av["bg"]}" stroke="{av["border"]}" stroke-width="1.5"/>')
        o.append(f'<text x="430" y="{y+26}" font-size="14.5" font-weight="800" fill="{av["color"]}">{esc(av["name"])}</text>')
        o.append(f'<text x="670" y="{y+26}" font-size="11.5" font-weight="700" fill="#0F172A">{esc(av["trans"])}</text>')
        
        # Kernel box
        o.append(f'<rect x="430" y="{y+38}" width="914" height="26" rx="4" fill="#FFFFFF" stroke="{av["border"]}"/>')
        o.append(f'<text x="440" y="{y+55}" font-size="11.5" font-weight="700" fill="#1E293B">Kernel Formula: <tspan font-weight="600" fill="{av["color"]}">{esc(av["kernel"])}</tspan></text>')

        # Description
        desc_words = av["desc"]
        o.append(f'<text x="430" y="{y+84}" font-size="11.5" fill="#334155">{esc(desc_words[:135])}</text>')
        o.append(f'<text x="430" y="{y+102}" font-size="11.5" fill="#334155">{esc(desc_words[135:270])}</text>')
        if len(desc_words) > 270:
            o.append(f'<text x="430" y="{y+120}" font-size="11.5" fill="#334155">{esc(desc_words[270:])}</text>')

        # Corpus footnote
        o.append(f'<text x="430" y="{y+145}" font-size="11" font-weight="700" fill="#64748B">Empirical Corpus: <tspan font-weight="500">{esc(av["strikes"])}</tspan></text>')

    o.append("</svg>")
    return "\\n".join(o)
'''

start = content.find("def page12()")
end = content.find("def page13()")
updated_content = content[:start] + new_page12 + "\n\n# --------------------------------------------------------------------------- PAGE 13\n" + content[end:]
primer_path.write_text(updated_content, encoding="utf-8")
print("Updated make_theory_primer.py Page 12 with full branching architecture diagram.")
