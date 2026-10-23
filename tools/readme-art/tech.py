import math, json, os
from geo import *

W, H = 1200, 720
HERE = os.path.dirname(os.path.abspath(__file__))
ICONS = json.load(open(os.path.join(HERE, "icons.json")))

# (label, icon slug)
CATS = [
    ("Languages", C["cyan"], [("TypeScript", "typescript"), ("JavaScript", "javascript"), ("C++", "cplusplus"),
                              ("Python", "python"), ("SQL", "x-sql")]),
    ("Frontend", C["green"], [("Next.js", "nextdotjs"), ("React", "react"), ("Redux", "redux"), ("Tailwind CSS", "tailwindcss"),
                              ("Framer Motion", "framer"), ("HTML5", "html5"), ("CSS3", "css")]),
    ("Backend & Real-time", C["violet"], [("Node.js", "nodedotjs"), ("Express", "express"), ("Socket.IO", "socketdotio"),
                                         ("WebRTC", "webrtc"), ("REST APIs", "x-rest"), ("NextAuth.js", "x-auth"), ("Mongoose", "mongoose")]),
    ("Databases", C["amber"], [("MongoDB", "mongodb"), ("PostgreSQL", "postgresql"), ("MySQL", "mysql"), ("Firebase", "firebase")]),
    ("Tools & Mobile", C["pink"], [("Docker", "docker"), ("Git", "git"), ("GitHub", "github"), ("Postman", "postman"),
                                   ("Vercel", "vercel"), ("Render", "render"), ("Flutter", "flutter"), ("Dart", "dart")]),
]

CUSTOM = {
    "x-sql": '<g fill="none" stroke-width="2" stroke-linecap="round"><ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5"/><path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/></g>',
    "x-rest": '<g fill="none" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3c-2 0-3 1-3 3v3c0 1.5-1 2.5-2.5 3C4 12.5 5 13.5 5 15v3c0 2 1 3 3 3"/><path d="M16 3c2 0 3 1 3 3v3c0 1.5 1 2.5 2.5 3-1.5.5-2.5 1.5-2.5 3v3c0 2-1 3-3 3"/><circle cx="12" cy="12" r="1.3" fill="currentColor"/></g>',
    "x-auth": '<g fill="none" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"><path d="M12 2l8 3v6c0 5-3.4 9-8 11-4.6-2-8-6-8-11V5z"/><path d="M8.5 12l2.5 2.5 4.5-5"/></g>',
}
CUSTOM_COL = {"x-sql": "#7dd3fc", "x-rest": "#c4b5fd", "x-auth": "#c084fc"}


def lum(h):
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def icon_color(slug):
    if slug in CUSTOM_COL:
        return CUSTOM_COL[slug]
    h = ICONS[slug]["hex"]
    L = lum(h)
    if L < 0.12:
        return "#f0f6fc"
    if L < 0.3:   # lift dark brand colours so they read on a dark background
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
        r, g, b = (int(c + (255 - c) * 0.45) for c in (r, g, b))
        return f"#{r:02x}{g:02x}{b:02x}"
    return "#" + h


def icon_defs():
    out = []
    for slug in {s for _, _, items in CATS for _, s in items}:
        if slug in CUSTOM:
            out.append(f'<g id="ic-{slug}">{CUSTOM[slug]}</g>')
        else:
            out.append(f'<path id="ic-{slug}" d="{ICONS[slug]["d"]}"/>')
    return "".join(out)


def use_icon(slug, x, y, size):
    s = size / 24
    col = icon_color(slug)
    return (f'<use href="#ic-{slug}" xlink:href="#ic-{slug}" fill="{col}" stroke="{col}" color="{col}" '
            f'transform="translate({f1(x)},{f1(y)}) scale({s:.3f})"/>' if slug in CUSTOM else
            f'<use href="#ic-{slug}" xlink:href="#ic-{slug}" fill="{col}" transform="translate({f1(x)},{f1(y)}) scale({s:.3f})"/>')


def fib(n):
    g = math.pi * (3 - 5 ** 0.5)
    out = []
    for i in range(n):
        y = 1 - 2 * (i + 0.5) / n
        r = math.sqrt(1 - y * y)
        out.append((math.cos(g * i) * r, y, math.sin(g * i) * r))
    return out


def build():
    cx, cy, R = 366, 378, 252
    N, DUR = 72, 36
    items = [(name, slug, col) for _, col, its in CATS for name, slug in its]
    items = items[0::3] + items[1::3] + items[2::3]       # spread categories over the sphere
    pos = fib(len(items))

    def rot(p, t):
        return rx(rz(ry(p, TAU * t), 0.18), 0.32)

    # faint wire globe
    parts = []
    for line in sphere_rings(4, 6, 32):
        ds = []
        for k in range(N + 1):
            pts = [project(rot(p, k / N), cx, cy, R * 0.9, cam=4) for p in line]
            ds.append("M" + "L".join(f"{f1(x)} {f1(y)}" for x, y, _, _ in pts))
        parts.append(f'<path d="{ds[0]}"><animate attributeName="d" dur="{DUR}s" repeatCount="indefinite" values="{";".join(ds)}"/></path>')
    wire = f'<g fill="none" stroke="{C["blue"]}" stroke-opacity="0.13" stroke-width="1">' + "".join(parts) + "</g>"

    FS, IS = 19, 26                     # label font size / icon size at scale 1
    nodes = []
    for (name, slug, col), p in zip(items, pos):
        tr, sc, op = [], [], []
        for k in range(N + 1):
            x, y, d, _ = project(rot(p, k / N), cx, cy, R, cam=4)
            dn = (d + 1) / 2
            tr.append(f"{f1(x)} {f1(y)}")
            sc.append(f2(0.55 + 0.75 * dn))
            op.append(f2(0.14 + 0.86 * dn ** 1.5))
        tw = len(name) * FS * 0.56
        total = IS + 7 + tw
        x0 = -total / 2
        nodes.append(
            f'<g transform="translate({tr[0].replace(" ", ",")})" opacity="{op[0]}">'
            f'<animateTransform attributeName="transform" type="translate" dur="{DUR}s" repeatCount="indefinite" values="{";".join(tr)}"/>'
            f'<animate attributeName="opacity" dur="{DUR}s" repeatCount="indefinite" values="{";".join(op)}"/>'
            f'<g transform="scale({sc[0]})"><animateTransform attributeName="transform" type="scale" dur="{DUR}s" repeatCount="indefinite" values="{";".join(sc)}"/>'
            f'{use_icon(slug, x0, -IS / 2, IS)}'
            f'<text x="{f1(x0 + IS + 7)}" y="{FS * 0.36:.1f}" fill="{col}">{esc(name)}</text>'
            f'</g></g>')

    # legend panel with icons
    lx, ly, lw = 738, 30, 434
    leg = [f'<g transform="translate({lx},{ly})">',
           f'<rect width="{lw}" height="{H - 2 * ly}" rx="16" fill="#0b1220" fill-opacity="0.8" stroke="{C["line"]}"/>']
    yy, colw = 40, (lw - 36) / 3
    for i, (cat, col, its) in enumerate(CATS):
        leg.append(f'<circle cx="26" cy="{yy - 6}" r="5.5" fill="{col}" filter="url(#glow)"/>'
                   f'<circle cx="26" cy="{yy - 6}" r="5.5" fill="none" stroke="{col}"><animate attributeName="r" values="5.5;12" dur="2.5s" begin="{i * 0.5:.1f}s" repeatCount="indefinite"/>'
                   f'<animate attributeName="opacity" values="0.8;0" dur="2.5s" begin="{i * 0.5:.1f}s" repeatCount="indefinite"/></circle>'
                   f'<text x="42" y="{yy}" font-family="{SANS}" font-size="18" font-weight="800" fill="{col}">{esc(cat)}</text>')
        yy += 16
        for j, (name, slug) in enumerate(its):
            r_, c_ = divmod(j, 3)
            x = 18 + c_ * colw
            y = yy + r_ * 31
            leg.append(use_icon(slug, x, y, 20) +
                       f'<text x="{f1(x + 27)}" y="{y + 15}" font-family="{SANS}" font-size="14" font-weight="600" fill="{C["text"]}">{esc(name)}</text>')
        yy += math.ceil(len(its) / 3) * 31 + 30
    leg.append("</g>")

    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Tech stack">
<title>Tech stack — rotating 3D sphere</title>
<defs>{GLOW}{icon_defs()}
<radialGradient id="core" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{C["violet"]}" stop-opacity="0.32"/><stop offset="0.6" stop-color="{C["blue"]}" stop-opacity="0.08"/><stop offset="1" stop-color="{C["blue"]}" stop-opacity="0"/></radialGradient>
<linearGradient id="bgp" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#070b16"/><stop offset="1" stop-color="#120a26"/></linearGradient>
</defs>
<rect width="{W}" height="{H}" rx="22" fill="url(#bgp)"/>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="22" fill="none" stroke="{C["violet"]}" stroke-opacity="0.3"/>
<circle cx="{cx}" cy="{cy}" r="270" fill="url(#core)"><animate attributeName="r" values="250;285;250" dur="5s" repeatCount="indefinite"/></circle>
{wire}
<g font-family="{SANS}" font-weight="800" font-size="{FS}">
{"".join(nodes)}
</g>
<text x="36" y="46" font-family="{MONO}" font-size="16" fill="{C["muted"]}">// tech_stack.sphere — {len(items)} tools in orbit</text>
{"".join(leg)}
</svg>'''


if __name__ == "__main__":
    import sys
    open(sys.argv[1], "w").write(build())
