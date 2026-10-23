import math, textwrap
from geo import *
from hero import floor as hero_floor  # reuse synthwave floor for footer
import hero
from objects import model_svg

PROJECTS = [
    dict(slug="codechoreo", n="01", title="CodeChoreo", tag="REAL-TIME · COLLABORATION", accent=C["cyan"], shape="laptop",
         desc="Real-time collaborative code editor with live cursors, chat, video calls, a shared whiteboard and AI code suggestions, synced over room-scoped Socket.IO sessions.",
         chips=["React", "Node.js", "Express", "Socket.IO", "WebRTC", "Docker"], foot="live demo on Render"),
    dict(slug="get-me-a-coffee", n="02", title="Get Me A Coffee", tag="CROWDFUNDING · PAYMENTS", accent=C["amber"], shape="cup",
         desc="Patreon-style crowdfunding platform with creator pages, supporter posts, Razorpay one-time and recurring donations, and NextAuth sign-in.",
         chips=["Next.js", "MongoDB", "Razorpay", "NextAuth", "Tailwind"], foot="live demo on Vercel"),
    dict(slug="video-chat-app", n="03", title="Video Chat App", tag="WEBRTC · PEER-TO-PEER", accent=C["pink"], shape="camera",
         desc="Peer-to-peer one-on-one and group video calling with in-call messaging. WebRTC handles media; Socket.IO handles low-latency signalling.",
         chips=["React", "Node.js", "Express", "WebRTC", "Socket.IO"], foot="live demo on Render"),
    dict(slug="gatepass", n="04", title="GatePass", tag="MOBILE · FLUTTER", accent=C["violet"], shape="phone",
         desc="Flutter mobile app that helps gated communities manage visitor entry, backed by Firebase Authentication and Cloud Firestore.",
         chips=["Flutter", "Dart", "Firebase Auth", "Firestore"], foot="source on GitHub"),
]


def shape_markup(kind, cx, cy, R, color, dur=16, n=64):
    if kind == "tess":
        v4, e = tesseract()
        frames = []
        for k in range(n + 1):
            pts = tess_frame(v4, k / n)
            frames.append([rx(ry(p, 0.5), 0.35) for p in pts])
        return wire_svg(frames, e, cx, cy, R, dur, color, width=1.5, dot_r=2.4, op=(0.25, 1))
    if kind == "torus":
        v, e = torus(nu=16, nv=7)
        return wire_svg(spin_frames(v, n, tilt_x=0.75, yturns=1, xwobble=0.15), e, cx, cy, R, dur, color, width=1.2, dots=False, op=(0.12, 1))
    if kind == "ico":
        v, e = icosphere(1)
        return wire_svg(spin_frames(v, n, tilt_x=0.3, yturns=1, tilt_z=0.3), e, cx, cy, R, dur, color, width=1.2, dot_r=1.8)
    if kind == "octa":
        v, e = octa_cube()
        return wire_svg(spin_frames(v, n, tilt_x=0.55, yturns=1, ztwist=0.3), e, cx, cy, R, dur, color, width=1.6, dot_r=2.6, op=(0.25, 1))
    if kind == "cube":
        v = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
        e = [(a, b) for a in range(8) for b in range(a + 1, 8) if sum(1 for i in range(3) if v[a][i] != v[b][i]) == 1]
        v = [(x * .62, y * .62, z * .62) for x, y, z in v]
        return wire_svg(spin_frames(v, n, tilt_x=0.6, yturns=1, tilt_z=0.4), e, cx, cy, R, dur, color, width=1.6, dot_r=1.8, op=(0.3, 1))
    raise ValueError(kind)


def chips(x, y, items, color, size=14, gap=10, maxw=540):
    out, cx, cy = [], x, y
    for it in items:
        w = len(it) * size * 0.62 + 24
        if cx + w > x + maxw:
            cx, cy = x, cy + size + 22
        out.append(f'<g transform="translate({cx:.1f},{cy})"><rect width="{w:.1f}" height="{size + 14}" rx="{(size + 14) / 2:.1f}" fill="{color}" fill-opacity="0.1" stroke="{color}" stroke-opacity="0.45"/>'
                   f'<text x="{w / 2:.1f}" y="{size + 2.5:.1f}" text-anchor="middle" font-family="{MONO}" font-size="{size}" fill="{color}">{esc(it)}</text></g>')
        cx += w + gap
    return "".join(out), cy


def running_border(w, h, r, color, dur=6, delay=0):
    return (f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{r}" fill="none" stroke="{C["line"]}" stroke-width="1.5"/>'
            f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{r}" fill="none" stroke="{color}" stroke-width="2.4" pathLength="1000" '
            f'stroke-dasharray="110 890" stroke-linecap="round" filter="url(#glow)">'
            f'<animate attributeName="stroke-dashoffset" values="0;-1000" dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/></rect>'
            f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{r}" fill="none" stroke="{color}" stroke-width="1.6" pathLength="1000" '
            f'stroke-dasharray="60 940" stroke-dashoffset="-500" stroke-linecap="round" opacity="0.7">'
            f'<animate attributeName="stroke-dashoffset" values="-500;-1500" dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/></rect>')


def project_card(p, idx):
    W, H = 600, 360
    a = p["accent"]
    lines = textwrap.wrap(p["desc"], 60)
    desc = "".join(f'<text x="36" y="{176 + i * 25}" font-family="{SANS}" font-size="16.5" fill="{C["text"]}" fill-opacity="0.86">{esc(l)}</text>'
                   for i, l in enumerate(lines))
    cy0 = 176 + len(lines) * 25 + 10
    chip_svg, last_y = chips(36, cy0, p["chips"], a, size=13, gap=8, maxw=540)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(p["title"])}">
<title>{esc(p["title"])}</title>
<defs>{GLOW}
<linearGradient id="cbg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b1020"/><stop offset="1" stop-color="#140b28"/></linearGradient>
<radialGradient id="spot" cx="0.85" cy="0.22" r="0.5"><stop offset="0" stop-color="{a}" stop-opacity="0.22"/><stop offset="1" stop-color="{a}" stop-opacity="0"/></radialGradient>
<linearGradient id="tg" x1="0" x2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="{a}"/></linearGradient>
<clipPath id="cc"><rect width="{W}" height="{H}" rx="20"/></clipPath>
</defs>
<g clip-path="url(#cc)">
<rect width="{W}" height="{H}" fill="url(#cbg)"/>
<rect width="{W}" height="{H}" fill="url(#spot)"/>
<text x="{W - 24}" y="{H - 22}" text-anchor="end" font-family="{SANS}" font-weight="900" font-size="150" fill="{a}" fill-opacity="0.05">{p["n"]}</text>
<g stroke="{a}" stroke-opacity="0.07">{"".join(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}"/>' for x in range(0, W, 30))}{"".join(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}"/>' for y in range(0, H, 30))}</g>
{model_svg(p["shape"], 498, {"laptop": 90, "cup": 82, "camera": 86, "phone": 86}[p["shape"]], {"laptop": 58, "cup": 70, "camera": 76, "phone": 64}[p["shape"]], a)}
<text x="36" y="56" font-family="{MONO}" font-size="13" letter-spacing="1.5" fill="{a}">{p["n"]} // {esc(p["tag"])}</text>
<text x="36" y="112" font-family="{SANS}" font-weight="800" font-size="38" fill="url(#tg)">{esc(p["title"])}</text>
<rect x="36" y="128" height="3" rx="1.5" fill="{a}" width="0" filter="url(#glow)"><animate attributeName="width" values="0;120;120" keyTimes="0;0.25;1" dur="4s" begin="{idx * 0.3}s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;1;0" keyTimes="0;0.8;1" dur="4s" begin="{idx * 0.3}s" repeatCount="indefinite"/></rect>
{desc}
{chip_svg}
<g transform="translate(36,{H - 30})" font-family="{MONO}" font-size="13">
  <circle cx="5" cy="-4" r="4.5" fill="{C["green"]}"><animate attributeName="opacity" values="1;0.3;1" dur="1.5s" repeatCount="indefinite"/></circle>
  <text x="18" y="0" fill="{C["muted"]}">{esc(p["foot"])}  ·  click card to open repo ↗</text>
</g>
</g>
{running_border(W, H, 20, a, 7, idx * 0.8)}
</svg>'''
    return svg


def lh_ring(cx, cy, label, color, delay):
    r = 34
    circ = 2 * math.pi * r
    return f'''<g transform="translate({cx},{cy})">
<circle r="{r}" fill="none" stroke="{color}" stroke-opacity="0.15" stroke-width="7"/>
<circle r="{r}" fill="none" stroke="{color}" stroke-width="7" stroke-linecap="round" transform="rotate(-90)" stroke-dasharray="{circ:.1f}" stroke-dashoffset="{circ:.1f}" filter="url(#glow)">
<animate attributeName="stroke-dashoffset" values="{circ:.1f};0;0;{circ:.1f}" keyTimes="0;0.3;0.92;1" dur="6s" begin="{delay}s" repeatCount="indefinite"/></circle>
<text y="8" text-anchor="middle" font-family="{SANS}" font-weight="800" font-size="24" fill="{color}">100</text>
<text y="{r + 26}" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{C["muted"]}">{label}</text></g>'''


def devit():
    W, H = 1200, 470
    tiles = [
        ("EDUCATION", "The Cradle Montessori", C["green"], ["Next.js", "Tailwind CSS"],
         "Semantic, responsive and accessible frontend."),
        ("EVENTS", "DSK Convention Hall", C["cyan"], ["Next.js", "SSR", "SSG"],
         "SSR for dynamic pages, SSG for static content."),
        ("HEALTHCARE", "Klinik Mediviron", C["pink"], ["TypeScript", "REST APIs"],
         "Typed request/response contracts over 3rd-party APIs."),
    ]
    tw, th, gap, x0, y0 = 360, 262, 24, 36, 112
    body = []
    for i, (tag, name, col, ch, line) in enumerate(tiles):
        x = x0 + i * (tw + gap)
        chip_svg, _ = chips(22, 82, ch, col, size=12, gap=8, maxw=tw - 40)
        if i == 0:
            vis = lh_ring(110, 186, "SEO", col, 0) + lh_ring(250, 186, "ACCESSIBILITY", col, 0.4)
        elif i == 1:
            # render pipeline: request packets flowing server -> page
            vis = (f'<g font-family="{MONO}" font-size="12" fill="{C["muted"]}">'
                   f'<rect x="22" y="150" width="96" height="56" rx="10" fill="{col}" fill-opacity="0.08" stroke="{col}" stroke-opacity="0.5"/><text x="70" y="183" text-anchor="middle" fill="{col}">server</text>'
                   f'<rect x="240" y="150" width="96" height="56" rx="10" fill="{col}" fill-opacity="0.08" stroke="{col}" stroke-opacity="0.5"/><text x="288" y="183" text-anchor="middle" fill="{col}">page</text>'
                   f'<line x1="122" y1="170" x2="236" y2="170" stroke="{col}" stroke-opacity="0.3" stroke-dasharray="4 5"/>'
                   f'<line x1="122" y1="188" x2="236" y2="188" stroke="{col}" stroke-opacity="0.3" stroke-dasharray="4 5"/>'
                   f'<text x="179" y="162" text-anchor="middle">SSR</text><text x="179" y="206" text-anchor="middle">SSG</text>'
                   f'<circle cy="170" r="4.5" fill="{col}" filter="url(#glow)"><animate attributeName="cx" values="122;236" dur="1.4s" repeatCount="indefinite"/></circle>'
                   f'<circle cy="188" r="4.5" fill="{C["green"]}" filter="url(#glow)"><animate attributeName="cx" values="122;236" dur="2.3s" repeatCount="indefinite"/></circle>'
                   f'<text x="179" y="240" text-anchor="middle" fill="{C["text"]}">fast first load · better SEO</text></g>')
        else:
            code = [("type", " Patient = {", C["violet"]), ("  id", ": string;", C["text"]),
                    ("  name", ": string;", C["text"]), ("  visits", ": Visit[];", C["text"]), ("}", "", C["violet"])]
            vis = [f'<rect x="22" y="138" width="{tw - 44}" height="112" rx="10" fill="#060a14" stroke="{C["line"]}"/>']
            for j, (k, rest, kc) in enumerate(code):
                b = 0.3 + j * 0.35
                vis.append(f'<text x="38" y="{162 + j * 19}" font-family="{MONO}" font-size="13" opacity="0" xml:space="preserve">'
                           f'<tspan fill="{kc}">{esc(k)}</tspan><tspan fill="{C["cyan"] if j and j < 4 else C["text"]}">{esc(rest)}</tspan>'
                           f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{b / 7:.3f};{(b + 0.2) / 7:.3f};0.93;1" dur="7s" repeatCount="indefinite"/></text>')
            vis.append(f'<text x="{tw - 36}" y="240" text-anchor="end" font-family="{MONO}" font-size="12" fill="{C["green"]}">✓ type-safe</text>')
            vis = "".join(vis)
        body.append(f'''<g transform="translate({x},{y0})">
<rect width="{tw}" height="{th}" rx="16" fill="#0a0f1d" stroke="{col}" stroke-opacity="0.28"/>
<text x="22" y="32" font-family="{MONO}" font-size="12" letter-spacing="1.5" fill="{col}">{tag}</text>
<text x="22" y="62" font-family="{SANS}" font-weight="800" font-size="22" fill="{C["text"]}">{esc(name)}</text>
{chip_svg}
{vis}
</g>''')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Experience at DevIt">
<title>Software Engineer at DevIt</title>
<defs>{GLOW}
<linearGradient id="dbg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#080d1a"/><stop offset="1" stop-color="#150b2b"/></linearGradient>
<linearGradient id="dg" x1="0" x2="1"><stop offset="0" stop-color="{C["green"]}"/><stop offset="1" stop-color="{C["cyan"]}"/></linearGradient>
</defs>
<rect width="{W}" height="{H}" rx="22" fill="url(#dbg)"/>
{shape_markup("cube", 1128, 60, 30, C["green"], dur=10, n=48)}
<text x="36" y="58" font-family="{SANS}" font-weight="900" font-size="34" fill="url(#dg)">DevIt</text>
<text x="140" y="58" font-family="{SANS}" font-weight="600" font-size="22" fill="{C["text"]}">Software Engineer</text>
<text x="36" y="88" font-family="{MONO}" font-size="14" fill="{C["muted"]}">Nov 2025 → present  ·  Bengaluru  ·  3 production client sites, shipped end to end</text>
{"".join(body)}
<g transform="translate(36,{H - 52})">
  <rect width="{W - 72}" height="34" rx="10" fill="{C["violet"]}" fill-opacity="0.08" stroke="{C["violet"]}" stroke-opacity="0.35"/>
  {"".join(f'<rect x="{14 + k * 16}" y="10" width="12" height="14" rx="3" fill="{C["violet"]}" opacity="0.25"><animate attributeName="opacity" values="0.2;1;0.2" dur="1.8s" begin="{k * 0.15:.2f}s" repeatCount="indefinite"/></rect>' for k in range(6))}
  <text x="122" y="22" font-family="{MONO}" font-size="13.5" fill="{C["text"]}">Built a reusable Tailwind CSS component library shared across every client build</text>
</g>
{running_border(W, H, 22, C["green"], 9)}
</svg>'''
    return svg


def about():
    W, H = 1200, 470
    K = lambda s: (s, C["cyan"]); S = lambda s: (s, C["green"]); P = lambda s: (s, C["text"]); M = lambda s: (s, C["muted"])
    lines = [
        ("cmd", [("whoami", C["text"])]),
        ("out", [("Rahul Mishra", C["text"]), (" — full-stack developer, Bengaluru, India", C["muted"])]),
        ("cmd", [("cat ", C["text"]), ("rahul.json", C["amber"])]),
        ("out", [P("{")]),
        ("out", [P("  "), K('"role"'), P(": "), S('"Software Engineer @ DevIt"'), P(",")]),
        ("out", [P("  "), K('"stack"'), P(": ["), S('"Next.js"'), P(", "), S('"React"'), P(", "), S('"TypeScript"'), P(", "), S('"Node.js"'), P("],")]),
        ("out", [P("  "), K('"shipped"'), P(": ["), S('"Cradle Montessori"'), P(", "), S('"DSK Convention Hall"'), P(", "), S('"Klinik Mediviron"'), P("],")]),
        ("out", [P("  "), K('"loves"'), P(": ["), S('"real-time systems"'), P(", "), S('"WebRTC"'), P(", "), S('"a11y"'), P(", "), S('"performance"'), P("],")]),
        ("out", [P("  "), K('"education"'), P(": "), S('"B.Tech CSE · MVJ College of Engineering · CGPA 8.60"'), P(",")]),
        ("out", [P("  "), K('"status"'), P(": "), (u'"open to frontend / full-stack roles 🚀"'.replace(" 🚀", ""), C["pink"])]),
        ("out", [P("}")]),
    ]
    CYC = 22.0
    fs, lh, x0, y0 = 16, 30, 40, 96
    cw = fs * 0.6
    t, out = 0.4, []
    for i, (kind, segs) in enumerate(lines):
        y = y0 + i * lh
        txt = "".join(s for s, _ in segs)
        xs = x0 + (24 if kind == "cmd" else 0)
        wfull = len(txt) * cw + 6
        dur = 0.06 * len(txt) if kind == "cmd" else 0.12
        a, b = t / CYC, (t + dur) / CYC
        t += dur + (0.45 if kind == "cmd" else 0.12)
        if kind == "cmd":
            out.append(f'<text x="{x0}" y="{y}" fill="{C["pink"]}" opacity="0">❯<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{a:.4f};{a + 0.001:.4f};0.96;1" dur="{CYC}s" repeatCount="indefinite"/></text>')
        out.append(f'<clipPath id="ab{i}"><rect x="{xs - 2}" y="{y - fs - 2}" height="{fs + 10}" width="0">'
                   f'<animate attributeName="width" values="0;0;{wfull:.0f};{wfull:.0f};0" keyTimes="0;{a:.4f};{b:.4f};0.96;1" dur="{CYC}s" repeatCount="indefinite"/></rect></clipPath>')
        tsp = "".join(f'<tspan fill="{c}">{esc(s)}</tspan>' for s, c in segs)
        out.append(f'<text x="{xs}" y="{y}" clip-path="url(#ab{i})" xml:space="preserve">{tsp}</text>')
    yl = y0 + len(lines) * lh
    a = t / CYC
    out.append(f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{a:.4f};{a + 0.001:.4f};0.96;1" dur="{CYC}s" repeatCount="indefinite"/>'
               f'<text x="{x0}" y="{yl}" fill="{C["pink"]}">❯</text>'
               f'<rect x="{x0 + 24}" y="{yl - fs + 2}" width="{cw:.1f}" height="{fs + 2}" fill="{C["green"]}"><animate attributeName="opacity" values="1;0;1" dur="1s" calcMode="discrete" repeatCount="indefinite"/></rect></g>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="About Rahul">
<title>About Rahul — terminal</title>
<defs>{GLOW}
<linearGradient id="tb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a0f1c"/><stop offset="1" stop-color="#0d0920"/></linearGradient>
</defs>
<rect width="{W}" height="{H}" rx="18" fill="url(#tb)"/>
<rect width="{W}" height="44" rx="18" fill="#111827"/><rect y="26" width="{W}" height="18" fill="#111827"/>
<circle cx="28" cy="22" r="7" fill="#ff5f57"/><circle cx="52" cy="22" r="7" fill="#febc2e"/><circle cx="76" cy="22" r="7" fill="#28c840"/>
<text x="{W / 2}" y="27" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{C["muted"]}">rahul@devit: ~ — zsh</text>
{shape_markup("ico", 1050, 250, 100, C["violet"], dur=26, n=72)}
<g font-family="{MONO}" font-size="{fs}">
{"".join(out)}
</g>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{C["line"]}"/>
</svg>'''
    return svg


def header(num, title, color):
    W, H = 1200, 76
    tw = len(f"{num} // {title}") * 22 * 0.6
    lx = 80 + tw + 24
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(title)}">
<title>{esc(title)}</title>
<defs>{GLOW}
<linearGradient id="hl" x1="0" x2="1"><stop offset="0" stop-color="{color}"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient></defs>
{shape_markup("cube", 34, 38, 26, color, dur=8, n=40)}
<text x="80" y="47" font-family="{MONO}" font-size="22" font-weight="700" fill="{C["text"]}"><tspan fill="{color}">{num}</tspan><tspan fill="{C["muted"]}"> // </tspan>{esc(title)}</text>
<rect x="{lx:.0f}" y="37" width="{W - lx - 10:.0f}" height="2" fill="url(#hl)" opacity="0.6"/>
<circle cy="38" r="3.5" fill="{color}" filter="url(#glow)"><animate attributeName="cx" values="{lx:.0f};{W - 20}" dur="3.5s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;1;0" keyTimes="0;0.7;1" dur="3.5s" repeatCount="indefinite"/></circle>
</svg>'''


THANKS = [("Thank you", "English"), ("ಧನ್ಯವಾದಗಳು", "Kannada"), ("धन्यवाद", "Hindi"), ("आभारी आहे", "Marathi"),
          ("ਧੰਨਵਾਦ", "Punjabi"), ("நன்றி", "Tamil"), ("ధన్యవాదాలు", "Telugu"), ("ধন্যবাদ", "Bengali"),
          ("આભાર", "Gujarati"), ("ありがとう", "Japanese"), ("감사합니다", "Korean"), ("谢谢", "Chinese"),
          ("Gracias", "Spanish"), ("Merci", "French"), ("Danke", "German")]
WORLD = ("'Segoe UI','Nirmala UI','Noto Sans','Noto Sans Kannada','Noto Sans Devanagari','Noto Sans Gurmukhi',"
         "'Noto Sans Tamil','Noto Sans Telugu','Noto Sans Bengali','Noto Sans Gujarati','Kohinoor Devanagari',"
         "'Hiragino Sans','Yu Gothic','Noto Sans CJK JP','Apple SD Gothic Neo','Malgun Gothic','PingFang SC',"
         "'Microsoft YaHei',Helvetica,Arial,sans-serif")


def footer():
    W, H, HOR = 1200, 260, 152
    old = (hero.W, hero.H, hero.HOR)
    hero.H, hero.HOR = H, HOR
    fl = hero.floor()
    hero.W, hero.H, hero.HOR = old
    slot, n = 2.2, len(THANKS)
    cyc = slot * n
    words = []
    for i, (word, lang) in enumerate(THANKS):
        a = i / n
        f = lambda x: f"{a + x / n:.4f}"
        # fade+rise in (0-15% of slot), hold, fade+rise out (85-100%)
        kt = f"0;{f(0)};{f(0.15)};{f(0.85)};{f(1)};1" if i else f"0;{f(0.15)};{f(0.85)};{f(1)};1"
        ov = "0;0;1;1;0;0" if i else "0;1;1;0;0"
        ty = "0 14;0 14;0 0;0 0;0 -14;0 -14" if i else "0 14;0 0;0 0;0 -14;0 -14"
        words.append(f'''<g opacity="0"><animate attributeName="opacity" values="{ov}" keyTimes="{kt}" dur="{cyc:.1f}s" repeatCount="indefinite"/>
<animateTransform attributeName="transform" type="translate" values="{ty}" keyTimes="{kt}" dur="{cyc:.1f}s" repeatCount="indefinite"/>
<text x="{W / 2}" y="84" text-anchor="middle" font-family="{WORLD}" font-weight="800" font-size="48" fill="url(#tg)" filter="url(#glow)">{esc(word)}</text>
</g>''')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Thank you in {n} languages">
<title>Thank you — in {n} languages</title>
<defs>{GLOW}
<linearGradient id="fade" x1="0" y1="{HOR}" x2="0" y2="{H}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.4" stop-color="#fff" stop-opacity="0.8"/><stop offset="1" stop-color="#fff"/></linearGradient>
<mask id="floorMask"><rect x="0" y="{HOR}" width="{W}" height="{H - HOR}" fill="url(#fade)"/></mask>
<linearGradient id="fsky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C["bg0"]}"/><stop offset="1" stop-color="#2a0b45"/></linearGradient>
<linearGradient id="hz" x1="0" x2="1"><stop offset="0" stop-color="{C["pink"]}" stop-opacity="0"/><stop offset="0.5" stop-color="{C["pink"]}"/><stop offset="1" stop-color="{C["pink"]}" stop-opacity="0"/></linearGradient>
<linearGradient id="tg" gradientUnits="userSpaceOnUse" x1="350" y1="0" x2="850" y2="0"><stop offset="0" stop-color="{C["cyan"]}"/><stop offset="0.5" stop-color="{C["green"]}"/><stop offset="1" stop-color="{C["violet"]}"/></linearGradient>
<clipPath id="fc"><rect width="{W}" height="{H}" rx="22"/></clipPath>
</defs>
<g clip-path="url(#fc)">
<rect width="{W}" height="{H}" fill="url(#fsky)"/>
<rect y="{HOR}" width="{W}" height="{H - HOR}" fill="#0a0418"/>
{fl}
<rect y="{HOR - 1}" width="{W}" height="2" fill="url(#hz)" filter="url(#glow)"/>
{"".join(words)}
<text x="{W / 2}" y="126" text-anchor="middle" font-family="{MONO}" font-size="15" fill="{C["muted"]}">let&#8217;s build something great together  ·  $ exit 0</text>
</g>
</svg>'''


if __name__ == "__main__":
    import sys, os
    out = sys.argv[1]
    for i, p in enumerate(PROJECTS):
        open(f"{out}/project-{p['slug']}-v2.svg", "w").write(project_card(p, i))
    open(f"{out}/devit.svg", "w").write(devit())
    open(f"{out}/about.svg", "w").write(about())
    for num, title, col, slug in [("01", "ABOUT ME", C["green"], "about"), ("02", "EXPERIENCE", C["cyan"], "experience"),
                                  ("03", "FEATURED PROJECTS", C["pink"], "projects"), ("04", "TECH STACK", C["violet"], "stack"),
                                  ("05", "GITHUB IN 3D", C["amber"], "github")]:
        open(f"{out}/h-{slug}.svg", "w").write(header(num, title, col))
    open(f"{out}/footer-v3.svg", "w").write(footer())
