import math, random
from geo import *

W, H = 1200, 440
HOR = 318            # horizon y
VPX = 600


def stars(n=110, seed=7):
    rnd = random.Random(seed)
    out = ['<g fill="#ffffff">']
    for _ in range(n):
        x, y = rnd.uniform(0, W), rnd.uniform(0, HOR - 8)
        r = rnd.choice([0.6, 0.8, 1.0, 1.3])
        d = rnd.uniform(2.5, 6)
        b = rnd.uniform(0, 5)
        lo = rnd.uniform(0.1, 0.35)
        out.append(f'<circle cx="{f1(x)}" cy="{f1(y)}" r="{r}" opacity="{f2(lo)}">'
                   f'<animate attributeName="opacity" values="{f2(lo)};0.95;{f2(lo)}" dur="{d:.1f}s" begin="{b:.1f}s" repeatCount="indefinite"/></circle>')
    out.append("</g>")
    return "\n".join(out)


def floor():
    out = ['<g mask="url(#floorMask)" stroke-linecap="round">']
    # converging verticals
    out.append(f'<g stroke="{C["pink"]}" stroke-width="1.1" opacity="0.55">')
    for i in range(-26, 27):
        bx = VPX + i * 70
        # extend line from VP through (bx, H)
        out.append(f'<line x1="{VPX}" y1="{HOR}" x2="{bx}" y2="{H}"/>')
    out.append("</g>")
    # moving horizontals
    fpx, s, K, N, dur = 122, 0.55, 26, 24, 1.6
    out.append(f'<g stroke="{C["cyan"]}" stroke-width="1.2" opacity="0.7">')
    for k in range(K):
        ys = []
        for f in range(N + 1):
            t = f / N
            z = 1 + (k - t) * s
            y = HOR + fpx / z if z > 0.05 else H + 50
            ys.append(f1(min(y, H + 50)))
        v = ";".join(ys)
        out.append(f'<line x1="0" x2="{W}" y1="{ys[0]}" y2="{ys[0]}">'
                   f'<animate attributeName="y1" values="{v}" dur="{dur}s" repeatCount="indefinite"/>'
                   f'<animate attributeName="y2" values="{v}" dur="{dur}s" repeatCount="indefinite"/></line>')
    out.append("</g></g>")
    return "\n".join(out)


def orbit(cx, cy, rx_, ry_, tilt_deg, dur, color, phase=0.0, n=60, r=4):
    """Ellipse ring split into back/front halves + a dot that dims when behind."""
    t = math.radians(tilt_deg)
    def pt(a):
        x, y = rx_ * math.cos(a), ry_ * math.sin(a)
        return cx + x * math.cos(t) - y * math.sin(t), cy + x * math.sin(t) + y * math.cos(t)
    back = "M" + "L".join(f"{f1(pt(math.pi + math.pi * k / 40)[0])} {f1(pt(math.pi + math.pi * k / 40)[1])}" for k in range(41))
    front = "M" + "L".join(f"{f1(pt(math.pi * k / 40)[0])} {f1(pt(math.pi * k / 40)[1])}" for k in range(41))
    xs, ys, os_, rs = [], [], [], []
    for k in range(n + 1):
        a = TAU * (k / n) + phase
        x, y = pt(a)
        depth = math.sin(a)          # >0 = front half (lower part of ellipse)
        xs.append(f1(x)); ys.append(f1(y))
        os_.append(f2(0.25 + 0.75 * (depth + 1) / 2))
        rs.append(f2(r * (0.65 + 0.5 * (depth + 1) / 2)))
    dot = (f'<circle r="{r}" fill="{color}" filter="url(#glow)">'
           f'<animate attributeName="cx" values="{";".join(xs)}" dur="{dur}s" repeatCount="indefinite"/>'
           f'<animate attributeName="cy" values="{";".join(ys)}" dur="{dur}s" repeatCount="indefinite"/>'
           f'<animate attributeName="opacity" values="{";".join(os_)}" dur="{dur}s" repeatCount="indefinite"/>'
           f'<animate attributeName="r" values="{";".join(rs)}" dur="{dur}s" repeatCount="indefinite"/></circle>')
    back_svg = f'<path d="{back}" fill="none" stroke="{color}" stroke-width="1.2" stroke-opacity="0.22"/>'
    front_svg = f'<path d="{front}" fill="none" stroke="{color}" stroke-width="1.6" stroke-opacity="0.75" filter="url(#glow)"/>'
    return back_svg, front_svg, dot


def typing_lines(x, y, phrases, cycle, size=19):
    cw = size * 0.6
    n = len(phrases)
    out = []
    for i, ph in enumerate(phrases):
        a = i / n
        b, c, d = a + 0.09, a + 0.215, a + 0.24
        wfull = len(ph) * cw + 4
        kt = f"0;{a:.3f};{b:.3f};{c:.3f};{d:.3f};1"
        out.append(f'<clipPath id="tc{i}"><rect x="{x}" y="{y - size}" height="{size + 8}" width="0">'
                   f'<animate attributeName="width" values="0;0;{wfull:.0f};{wfull:.0f};0;0" keyTimes="{kt}" dur="{cycle}s" repeatCount="indefinite"/></rect></clipPath>')
        out.append(f'<text x="{x}" y="{y}" clip-path="url(#tc{i})" font-family="{MONO}" font-size="{size}" fill="{C["text"]}">{esc(ph)}</text>')
        out.append(f'<rect y="{y - size + 3}" width="{cw:.1f}" height="{size + 1}" fill="{C["green"]}" x="{x}" opacity="0">'
                   f'<animate attributeName="x" values="{x};{x};{x + wfull:.0f};{x + wfull:.0f};{x};{x}" keyTimes="{kt}" dur="{cycle}s" repeatCount="indefinite"/>'
                   f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{a:.3f};{a + 0.001:.3f};{d - 0.001:.3f};{d:.3f};1" calcMode="discrete" dur="{cycle}s" repeatCount="indefinite"/>'
                   f'</rect>')
    return "\n".join(out)


def build():
    cx, cy, R = 925, 178, 118
    v, e = icosphere(1)
    frames = spin_frames(v, 72, tilt_x=0.42, yturns=1, xwobble=0.12)
    sphere = wire_svg(frames, e, cx, cy, R, 24, C["cyan"], width=1.3, dot_r=2.4)
    # inner counter-rotating icosahedron
    iv, ie = ico_wire()
    iframes = spin_frames(iv, 72, tilt_x=-0.5, yturns=-2, tilt_z=0.4)
    inner = wire_svg(iframes, ie, cx, cy, 52, 24, C["green"], width=1.6, dot_r=2.6, op=(0.3, 1))
    b1, f1_, d1 = orbit(cx, cy, 190, 46, -14, 7, C["pink"])
    b2, f2_, d2 = orbit(cx, cy, 160, 30, 22, 11, C["green"], phase=1.7, r=3.2)

    phrases = ["shipped 3 production client websites",
               "real-time apps on Socket.IO + WebRTC",
               "Lighthouse: 100 SEO / 100 Accessibility",
               "open to frontend / full-stack roles"]
    name_x, name_y = 64, 168

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Rahul Mishra — Full-Stack Developer">
<title>Rahul Mishra — Full-Stack Developer</title>
<defs>
{GLOW}
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{C["bg0"]}"/><stop offset="0.72" stop-color="#140a33"/><stop offset="1" stop-color="#2a0b45"/>
</linearGradient>
<radialGradient id="halo" cx="0.5" cy="0.5" r="0.5">
  <stop offset="0" stop-color="{C["cyan"]}" stop-opacity="0.35"/><stop offset="0.55" stop-color="{C["violet"]}" stop-opacity="0.12"/><stop offset="1" stop-color="{C["violet"]}" stop-opacity="0"/>
</radialGradient>
<linearGradient id="hz" x1="0" x2="1">
  <stop offset="0" stop-color="{C["pink"]}" stop-opacity="0"/><stop offset="0.5" stop-color="{C["pink"]}"/><stop offset="1" stop-color="{C["pink"]}" stop-opacity="0"/>
</linearGradient>
<linearGradient id="fade" x1="0" y1="{HOR}" x2="0" y2="{H}" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.35" stop-color="#fff" stop-opacity="0.8"/><stop offset="1" stop-color="#fff"/>
</linearGradient>
<mask id="floorMask"><rect x="0" y="{HOR}" width="{W}" height="{H - HOR}" fill="url(#fade)"/></mask>
<linearGradient id="nameGrad" gradientUnits="userSpaceOnUse" x1="{name_x}" y1="0" x2="{name_x + 560}" y2="0" spreadMethod="repeat">
  <stop offset="0" stop-color="{C["cyan"]}"/><stop offset="0.33" stop-color="{C["green"]}"/><stop offset="0.66" stop-color="{C["violet"]}"/><stop offset="1" stop-color="{C["cyan"]}"/>
  <animate attributeName="x1" values="{name_x};{name_x + 560}" dur="6s" repeatCount="indefinite"/>
  <animate attributeName="x2" values="{name_x + 560};{name_x + 1120}" dur="6s" repeatCount="indefinite"/>
</linearGradient>
<clipPath id="sliceA"><rect x="0" y="{name_y - 60}" width="{W}" height="22"/></clipPath>
<clipPath id="sliceB"><rect x="0" y="{name_y - 30}" width="{W}" height="18"/></clipPath>
<clipPath id="frame"><rect width="{W}" height="{H}" rx="22"/></clipPath>
</defs>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="url(#sky)"/>
{stars()}
<circle cx="{cx}" cy="{cy}" r="260" fill="url(#halo)"><animate attributeName="r" values="240;275;240" dur="6s" repeatCount="indefinite"/></circle>
<rect x="0" y="{HOR}" width="{W}" height="{H - HOR}" fill="#0a0418"/>
{floor()}
<rect x="0" y="{HOR - 1}" width="{W}" height="2" fill="url(#hz)" filter="url(#glow)"/>
{b1}
{b2}
{inner}
{sphere}
{f1_}
{f2_}
{d1}
{d2}

<!-- text block -->
<g font-family="{MONO}" font-size="17" fill="{C["green"]}">
  <text x="{name_x}" y="{name_y - 78}">&gt; hello world, I&#8217;m</text>
</g>
<g font-family="{SANS}" font-weight="800" font-size="78" letter-spacing="1">
  <text x="{name_x + 3}" y="{name_y}" fill="{C["pink"]}" opacity="0" clip-path="url(#sliceA)">RAHUL MISHRA
    <animate attributeName="opacity" values="0;0;0.9;0;0.9;0;0" keyTimes="0;0.86;0.87;0.89;0.9;0.92;1" dur="5s" repeatCount="indefinite"/>
    <animateTransform attributeName="transform" type="translate" values="0 0;0 0;8 0;-6 0;5 0;0 0;0 0" keyTimes="0;0.86;0.87;0.89;0.9;0.92;1" dur="5s" repeatCount="indefinite"/>
  </text>
  <text x="{name_x - 3}" y="{name_y}" fill="{C["cyan"]}" opacity="0" clip-path="url(#sliceB)">RAHUL MISHRA
    <animate attributeName="opacity" values="0;0;0.9;0;0.9;0;0" keyTimes="0;0.87;0.88;0.9;0.91;0.93;1" dur="5s" repeatCount="indefinite"/>
    <animateTransform attributeName="transform" type="translate" values="0 0;0 0;-9 0;7 0;-4 0;0 0;0 0" keyTimes="0;0.87;0.88;0.9;0.91;0.93;1" dur="5s" repeatCount="indefinite"/>
  </text>
  <text x="{name_x}" y="{name_y}" fill="url(#nameGrad)" filter="url(#glow)">RAHUL MISHRA</text>
</g>
<text x="{name_x}" y="{name_y + 46}" font-family="{SANS}" font-size="28" font-weight="600" fill="{C["text"]}">Full-Stack Developer <tspan fill="{C["muted"]}" font-weight="400">@ DevIt</tspan></text>
<text x="{name_x}" y="{name_y + 78}" font-family="{MONO}" font-size="16" fill="{C["muted"]}">Next.js · React · TypeScript · Node.js · Socket.IO · WebRTC</text>
<g>
  <text x="{name_x}" y="{name_y + 122}" font-family="{MONO}" font-size="19" fill="{C["pink"]}">$</text>
  {typing_lines(name_x + 22, name_y + 122, phrases, 16)}
</g>
<g transform="translate({name_x},{name_y + 146})">
  <rect width="292" height="30" rx="15" fill="#0f2a22" stroke="{C["green"]}" stroke-opacity="0.5"/>
  <circle cx="18" cy="15" r="5" fill="{C["green"]}"><animate attributeName="opacity" values="1;0.25;1" dur="1.6s" repeatCount="indefinite"/></circle>
  <circle cx="18" cy="15" r="5" fill="none" stroke="{C["green"]}"><animate attributeName="r" values="5;12" dur="1.6s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.8;0" dur="1.6s" repeatCount="indefinite"/></circle>
  <text x="34" y="20" font-family="{SANS}" font-size="14" font-weight="600" fill="{C["green"]}">Open to work · Bengaluru, India</text>
</g>
</g>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="22" fill="none" stroke="{C["violet"]}" stroke-opacity="0.35"/>
</svg>'''
    return svg


if __name__ == "__main__":
    import sys
    open(sys.argv[1], "w").write(build())
