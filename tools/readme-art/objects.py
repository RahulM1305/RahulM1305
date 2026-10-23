"""3D wireframe models for the project cards: laptop, coffee cup, movie camera, phone."""
import math
from geo import TAU, rx, ry, rz, project, f1, f2


# ---------------------------------------------------------------- primitives
def circle(c, r, axis="y", n=20, a0=0.0, a1=TAU):
    cx, cy, cz = c
    pts = []
    for k in range(n + 1):
        a = a0 + (a1 - a0) * k / n
        u, v = r * math.cos(a), r * math.sin(a)
        pts.append({"y": (cx + u, cy, cz + v), "x": (cx, cy + u, cz + v), "z": (cx + u, cy + v, cz)}[axis])
    return pts


def box(x0, x1, y0, y1, z0, z1):
    P = lambda x, y, z: (x, y, z)
    lines = []
    for z in (z0, z1):
        lines.append([P(x0, y0, z), P(x1, y0, z), P(x1, y1, z), P(x0, y1, z), P(x0, y0, z)])
    for x in (x0, x1):
        for y in (y0, y1):
            lines.append([P(x, y, z0), P(x, y, z1)])
    return lines


def rrect(cx, cy, w, h, r, z, n=5):
    """Rounded rectangle in the xy-plane at depth z."""
    pts = []
    corners = [(cx + w / 2 - r, cy + h / 2 - r, 0), (cx - w / 2 + r, cy + h / 2 - r, math.pi / 2),
               (cx - w / 2 + r, cy - h / 2 + r, math.pi), (cx + w / 2 - r, cy - h / 2 + r, 3 * math.pi / 2)]
    for ox, oy, a0 in corners:
        for k in range(n + 1):
            a = a0 + (math.pi / 2) * k / n
            pts.append((ox + r * math.cos(a), oy + r * math.sin(a), z))
    pts.append(pts[0])
    return pts


def shift(lines, dx=0, dy=0, dz=0, s=1.0):
    return [[((x + dx) * s, (y + dy) * s, (z + dz) * s) for x, y, z in l] for l in lines]


# ---------------------------------------------------------------- models
def laptop():
    L = []
    w, d, t = 1.7, 1.12, 0.07
    yb = -0.42
    L += box(-w / 2, w / 2, yb - t, yb, -d / 2, d / 2)                       # base slab
    # keyboard rows + trackpad on top face
    for i in range(4):
        z = -d / 2 + 0.16 + i * 0.12
        L.append([(-w / 2 + 0.16, yb + .001, z), (w / 2 - 0.16, yb + .001, z)])
    for i in range(7):
        x = -w / 2 + 0.16 + i * (w - 0.32) / 6
        L.append([(x, yb + .001, -d / 2 + 0.16), (x, yb + .001, -d / 2 + 0.52)])
    L.append([(-0.3, yb, 0.2), (0.3, yb, 0.2), (0.3, yb, 0.47), (-0.3, yb, 0.47), (-0.3, yb, 0.2)])
    # screen, hinged at the back edge, tilted back 14 deg
    a = math.radians(14)
    hinge = (0, yb, -d / 2)
    up, nrm = (0, math.cos(a), -math.sin(a)), (0, math.sin(a), math.cos(a))
    H = 1.08

    def S(u, v, off=0.0):
        return (u, hinge[1] + up[1] * v + nrm[1] * off, hinge[2] + up[2] * v + nrm[2] * off)
    for off in (0.0, -0.05):
        L.append([S(-w / 2, 0, off), S(w / 2, 0, off), S(w / 2, H, off), S(-w / 2, H, off), S(-w / 2, 0, off)])
    for u in (-w / 2, w / 2):
        L.append([S(u, H, 0), S(u, H, -0.05)])
    b = 0.08
    L.append([S(-w / 2 + b, b, .002), S(w / 2 - b, b, .002), S(w / 2 - b, H - b, .002), S(-w / 2 + b, H - b, .002), S(-w / 2 + b, b, .002)])
    # "code" on screen
    lines = [(0.0, 0.55), (0.12, 0.9), (0.12, 0.6), (0.24, 0.75), (0.12, 0.45), (0.0, 0.3)]
    for i, (indent, ln) in enumerate(lines):
        v = H - b - 0.14 - i * 0.13
        x0 = -w / 2 + b + 0.12 + indent
        L.append([S(x0, v, .003), S(x0 + ln, v, .003)])
    L.append([S(-0.05, H - b / 2, .002), S(0.05, H - b / 2, .002)])        # webcam
    return shift(L, dy=-0.05, dz=0.12, s=1.0)


def cup():
    L = []
    y0, y1, r0, r1 = -0.42, 0.38, 0.38, 0.52
    for k in range(5):
        t = k / 4
        L.append(circle((0, y0 + (y1 - y0) * t, 0), r0 + (r1 - r0) * t, "y", 24))
    for j in range(12):
        a = TAU * j / 12
        L.append([(r0 * math.cos(a), y0, r0 * math.sin(a)), (r1 * math.cos(a), y1, r1 * math.sin(a))])
    L.append(circle((0, y1 - 0.05, 0), r1 - 0.06, "y", 24))                  # coffee surface
    # handle: two C-curves in the xy-plane
    for z in (-0.06, 0.06):
        pts = []
        for k in range(15):
            th = -math.pi / 2 + math.pi * k / 14
            pts.append((0.47 + 0.28 * math.cos(th), -0.04 + 0.23 * math.sin(th), z))
        L.append(pts)
    for k in (0, 7, 14):
        th = -math.pi / 2 + math.pi * k / 14
        p = (0.47 + 0.28 * math.cos(th), -0.04 + 0.23 * math.sin(th))
        L.append([(p[0], p[1], -0.06), (p[0], p[1], 0.06)])
    # saucer
    L.append(circle((0, y0 - 0.02, 0), 0.88, "y", 32))
    L.append(circle((0, y0 - 0.06, 0), 0.62, "y", 28))
    L.append(circle((0, y0, 0), 0.45, "y", 24))
    # steam
    for i, x in enumerate((-0.18, 0.04, 0.24)):
        pts = []
        for k in range(13):
            v = k / 12
            pts.append((x + 0.07 * math.sin(v * TAU * 1.2 + i), y1 + 0.1 + v * 0.5, 0.05 * math.cos(v * TAU + i)))
        L.append(pts)
    return shift(L, dy=-0.12)


def camera():
    L = []
    L += box(-0.6, 0.3, -0.38, 0.22, -0.3, 0.3)                              # body
    # lens barrel pointing +x
    for x, r in ((0.3, 0.2), (0.48, 0.24), (0.66, 0.3), (0.72, 0.3)):
        L.append(circle((x, -0.08, 0), r, "x", 18))
    L.append(circle((0.72, -0.08, 0), 0.17, "x", 16))
    for j in range(8):
        a = TAU * j / 8
        L.append([(0.3, -0.08 + 0.2 * math.cos(a), 0.2 * math.sin(a)), (0.66, -0.08 + 0.3 * math.cos(a), 0.3 * math.sin(a))])
    # two film reels on top
    for cx, cy, r in ((-0.38, 0.5, 0.27), (0.12, 0.47, 0.23)):
        for z in (-0.06, 0.06):
            L.append(circle((cx, cy, z), r, "z", 22))
            L.append(circle((cx, cy, z), 0.06, "z", 10))
        for j in range(5):
            a = TAU * j / 5 + 0.3
            L.append([(cx + 0.06 * math.cos(a), cy + 0.06 * math.sin(a), 0.06), (cx + r * math.cos(a), cy + r * math.sin(a), 0.06)])
        L.append([(cx, cy - r, -0.06), (cx, cy - r, 0.06)])
    L.append([(-0.38, 0.23, 0), (-0.38, 0.22, 0)])
    # handle underneath
    L += box(-0.42, -0.2, -0.62, -0.38, -0.07, 0.07)
    return shift(L, dx=0.0, dy=0.04)


def camera_rec_light():
    return (-0.5, 0.12, 0.301)


def phone():
    L = []
    w, h, r = 0.92, 1.86, 0.15
    for z in (-0.05, 0.05):
        L.append(rrect(0, 0, w, h, r, z, 5))
    for x, y in ((w / 2, h / 2 - r), (-w / 2, h / 2 - r), (w / 2, -h / 2 + r), (-w / 2, -h / 2 + r)):
        L.append([(x, y, -0.05), (x, y, 0.05)])
    zf = 0.052
    L.append(rrect(0, 0, w - 0.1, h - 0.1, r - 0.05, zf, 4))                   # screen
    L.append(rrect(0, h / 2 - 0.12, 0.26, 0.07, 0.035, zf + .001, 3))         # notch / island
    L.append([(-0.14, -h / 2 + 0.1, zf), (0.14, -h / 2 + 0.1, zf)])           # home bar
    # visitor pass UI: avatar, two text lines, QR code
    L.append(circle((0, 0.52, zf), 0.13, "z", 18))
    L.append([(-0.24, 0.3, zf), (0.24, 0.3, zf)])
    L.append([(-0.16, 0.22, zf), (0.16, 0.22, zf)])
    q, qy = 0.42, -0.18
    L.append([(-q / 2, qy - q / 2, zf), (q / 2, qy - q / 2, zf), (q / 2, qy + q / 2, zf), (-q / 2, qy + q / 2, zf), (-q / 2, qy - q / 2, zf)])
    for fx, fy in ((-1, 1), (1, 1), (-1, -1)):
        cx, cy, s = fx * (q / 2 - 0.08), qy + fy * (q / 2 - 0.08), 0.06
        L.append([(cx - s, cy - s, zf), (cx + s, cy - s, zf), (cx + s, cy + s, zf), (cx - s, cy + s, zf), (cx - s, cy - s, zf)])
    L.append([(0.03, qy - 0.06, zf), (0.12, qy - 0.06, zf), (0.12, qy - 0.15, zf)])
    L.append([(-0.04, qy - 0.02, zf), (-0.04, qy - 0.12, zf)])
    # "approved" pill
    L.append(rrect(0, -0.62, 0.5, 0.13, 0.065, zf, 3))
    L.append([(-0.06, -0.62, zf), (-0.02, -0.66, zf), (0.06, -0.58, zf)])
    return L


# ---------------------------------------------------------------- animation
def pose_frames(lines, n, mode, tilt=0.3, amp=0.85, base=0.0):
    out = []
    for k in range(n + 1):
        t = k / n
        yaw = TAU * t if mode == "spin" else base + amp * math.sin(TAU * t)
        out.append([[rx(ry(p, yaw), tilt + 0.06 * math.sin(TAU * t)) for p in l] for l in lines])
    return out


def poly_svg(frames, cx, cy, R, dur, color, width=1.4, op=(0.18, 1.0)):
    lo, hi = op
    n_lines = len(frames[0])
    out = [f'<g stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" fill="none" filter="url(#glow)">']
    for i in range(n_lines):
        ds, ops = [], []
        for fr in frames:
            pts = [project(p, cx, cy, R) for p in fr[i]]
            ds.append("M" + "L".join(f"{f1(x)} {f1(y)}" for x, y, _, _ in pts))
            d = sum(p[2] for p in pts) / len(pts)
            ops.append(f2(lo + (hi - lo) * (d + 1) / 2))
        out.append(f'<path d="{ds[0]}" stroke-opacity="{ops[0]}">'
                   f'<animate attributeName="d" dur="{dur}s" repeatCount="indefinite" values="{";".join(ds)}"/>'
                   f'<animate attributeName="stroke-opacity" dur="{dur}s" repeatCount="indefinite" values="{";".join(ops)}"/></path>')
    out.append("</g>")
    return "\n".join(out)


def point_svg(p, n, mode, cx, cy, R, dur, color, r=4.5, **kw):
    fr = pose_frames([[p]], n, mode, **kw)
    pts = [project(f[0][0], cx, cy, R) for f in fr]
    xs = ";".join(f1(q[0]) for q in pts)
    ys = ";".join(f1(q[1]) for q in pts)
    vis = ";".join(f2(max(0.0, min(1.0, (q[2] + 0.2) * 2))) for q in pts)   # hide when facing away
    return (f'<g opacity="{vis.split(";")[0]}"><animate attributeName="opacity" dur="{dur}s" repeatCount="indefinite" values="{vis}"/>'
            f'<circle r="{r}" fill="{color}" filter="url(#glow)" cx="{xs.split(";")[0]}" cy="{ys.split(";")[0]}">'
            f'<animate attributeName="cx" dur="{dur}s" repeatCount="indefinite" values="{xs}"/>'
            f'<animate attributeName="cy" dur="{dur}s" repeatCount="indefinite" values="{ys}"/>'
            f'<animate attributeName="r" values="{r};{r * 0.55};{r}" dur="1.2s" repeatCount="indefinite"/></circle></g>')


def model_svg(kind, cx, cy, R, color, dur=14, n=72):
    if kind == "laptop":
        return poly_svg(pose_frames(laptop(), n, "sway", tilt=0.42, amp=0.8, base=-0.35), cx, cy, R, dur, color, op=(0.3, 1))
    if kind == "cup":
        return poly_svg(pose_frames(cup(), n, "spin", tilt=0.38), cx, cy, R, dur, color, width=1.3, op=(0.22, 1))
    if kind == "camera":
        kw = dict(tilt=0.3, amp=0.9, base=-0.6)
        body = poly_svg(pose_frames(camera(), n, "sway", **kw), cx, cy, R, dur, color, op=(0.25, 1))
        return body + point_svg(camera_rec_light(), n, "sway", cx, cy, R, dur, "#ff3b3b", r=4, **kw)
    if kind == "phone":
        return poly_svg(pose_frames(phone(), n, "sway", tilt=0.18, amp=0.75, base=-0.25), cx, cy, R, dur, color, op=(0.3, 1))
    raise ValueError(kind)
