import math
from geo import *

W, H = 1200, 520
CATS = [
    ("Languages", C["cyan"], ["TypeScript", "JavaScript", "C++", "Python", "SQL"]),
    ("Frontend", C["green"], ["Next.js", "React", "Redux", "Tailwind CSS", "Framer Motion", "HTML5", "CSS3"]),
    ("Backend & Real-time", C["violet"], ["Node.js", "Express", "Socket.IO", "WebRTC", "REST APIs", "NextAuth.js", "Mongoose"]),
    ("Databases", C["amber"], ["MongoDB", "PostgreSQL", "MySQL", "Firebase"]),
    ("Tools & Mobile", C["pink"], ["Docker", "Git", "GitHub", "Postman", "Vercel", "Render", "Flutter", "Dart"]),
]


def fib(n):
    g = math.pi * (3 - 5 ** 0.5)
    out = []
    for i in range(n):
        y = 1 - 2 * (i + 0.5) / n
        r = math.sqrt(1 - y * y)
        out.append((math.cos(g * i) * r, y, math.sin(g * i) * r))
    return out


def build():
    cx, cy, R = 400, 276, 192
    N, DUR = 72, 30
    labels = [(name, col) for _, col, items in CATS for name in items]
    # interleave categories so colours spread over the sphere
    labels = labels[0::3] + labels[1::3] + labels[2::3]
    pos = fib(len(labels))
    tilt = 0.32

    def rot(p, t):
        q = ry(p, TAU * t)
        return rx(rz(q, 0.18), tilt)

    parts = []
    # wire rings
    rings = sphere_rings(4, 6, 32)
    for line in rings:
        ds, ops = [], []
        for k in range(N + 1):
            t = k / N
            pts = [project(rot(p, t), cx, cy, R * 0.93, cam=4) for p in line]
            ds.append("M" + "L".join(f"{f1(x)} {f1(y)}" for x, y, _, _ in pts))
        parts.append(f'<path d="{ds[0]}"><animate attributeName="d" dur="{DUR}s" repeatCount="indefinite" values="{";".join(ds)}"/></path>')
    wire = f'<g fill="none" stroke="{C["blue"]}" stroke-opacity="0.13" stroke-width="1">' + "".join(parts) + "</g>"

    texts = []
    for (name, col), p in zip(labels, pos):
        xs, ys, fs, os_ = [], [], [], []
        for k in range(N + 1):
            t = k / N
            x, y, d, s = project(rot(p, t), cx, cy, R, cam=4)
            dn = (d + 1) / 2
            xs.append(f1(x)); ys.append(f1(y + 5))
            fs.append(f1(11 + 12 * dn))
            os_.append(f2(0.16 + 0.84 * dn ** 1.4))
        texts.append(
            f'<text x="{xs[0]}" y="{ys[0]}" font-size="{fs[0]}" opacity="{os_[0]}" fill="{col}">{esc(name)}'
            f'<animate attributeName="x" dur="{DUR}s" repeatCount="indefinite" values="{";".join(xs)}"/>'
            f'<animate attributeName="y" dur="{DUR}s" repeatCount="indefinite" values="{";".join(ys)}"/>'
            f'<animate attributeName="font-size" dur="{DUR}s" repeatCount="indefinite" values="{";".join(fs)}"/>'
            f'<animate attributeName="opacity" dur="{DUR}s" repeatCount="indefinite" values="{";".join(os_)}"/></text>')

    # legend panel
    lx, ly = 752, 36
    leg = [f'<g transform="translate({lx},{ly})">']
    leg.append(f'<rect width="408" height="{H - 2 * ly + 8}" rx="16" fill="#0b1220" fill-opacity="0.75" stroke="{C["line"]}"/>')
    yy = 44
    for i, (cat, col, items) in enumerate(CATS):
        leg.append('<g>')
        leg.append(f'<circle cx="28" cy="{yy - 5}" r="5" fill="{col}" filter="url(#glow)"/>'
                   f'<circle cx="28" cy="{yy - 5}" r="5" fill="none" stroke="{col}"><animate attributeName="r" values="5;11" dur="2.5s" begin="{i * 0.5:.1f}s" repeatCount="indefinite"/>'
                   f'<animate attributeName="opacity" values="0.8;0" dur="2.5s" begin="{i * 0.5:.1f}s" repeatCount="indefinite"/></circle>')
        leg.append(f'<text x="44" y="{yy}" font-family="{SANS}" font-size="16" font-weight="700" fill="{col}">{esc(cat)}</text>')
        # wrap items
        line, lines = "", []
        for it in items:
            cand = (line + "  ·  " + it) if line else it
            if len(cand) > 44:
                lines.append(line); line = it
            else:
                line = cand
        lines.append(line)
        for j, ln in enumerate(lines):
            leg.append(f'<text x="44" y="{yy + 24 + j * 20}" font-family="{MONO}" font-size="13" fill="{C["text"]}" fill-opacity="0.82">{esc(ln)}</text>')
        leg.append("</g>")
        yy += 26 + 20 * len(lines) + 18
    leg.append("</g>")

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Tech stack">
<title>Tech stack — rotating 3D sphere</title>
<defs>{GLOW}
<radialGradient id="core" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{C["violet"]}" stop-opacity="0.32"/><stop offset="0.6" stop-color="{C["blue"]}" stop-opacity="0.08"/><stop offset="1" stop-color="{C["blue"]}" stop-opacity="0"/></radialGradient>
<linearGradient id="bgp" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#070b16"/><stop offset="1" stop-color="#120a26"/></linearGradient>
</defs>
<rect width="{W}" height="{H}" rx="22" fill="url(#bgp)"/>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="22" fill="none" stroke="{C["violet"]}" stroke-opacity="0.3"/>
<circle cx="{cx}" cy="{cy}" r="230" fill="url(#core)"><animate attributeName="r" values="215;245;215" dur="5s" repeatCount="indefinite"/></circle>
{wire}
<g font-family="{SANS}" font-weight="700" text-anchor="middle">
{"".join(texts)}
</g>
<text x="40" y="44" font-family="{MONO}" font-size="14" fill="{C["muted"]}">// tech_stack.sphere — {len(labels)} tools in orbit</text>
{"".join(leg)}
</svg>'''
    return svg


if __name__ == "__main__":
    import sys
    open(sys.argv[1], "w").write(build())
