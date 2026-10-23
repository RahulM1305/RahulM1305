"""Tiny 3D helpers: meshes, rotation, perspective projection, SVG-SMIL emitters."""
import math
from xml.sax.saxutils import escape as _esc

TAU = math.tau


def esc(s):
    return _esc(s, {'"': "&quot;"})


def f1(v):
    s = f"{v:.1f}"
    return "0" if s in ("-0.0", "0.0") else s.rstrip("0").rstrip(".") if "." in s else s


def f2(v):
    return f"{v:.2f}"


# ---------------------------------------------------------------- meshes
def icosahedron():
    p = (1 + 5 ** 0.5) / 2
    v = [(-1, p, 0), (1, p, 0), (-1, -p, 0), (1, -p, 0),
         (0, -1, p), (0, 1, p), (0, -1, -p), (0, 1, -p),
         (p, 0, -1), (p, 0, 1), (-p, 0, -1), (-p, 0, 1)]
    v = [norm(x) for x in v]
    faces = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
             (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
             (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
             (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
    return v, faces


def norm(p):
    l = math.sqrt(sum(c * c for c in p))
    return tuple(c / l for c in p)


def icosphere(sub=1):
    v, faces = icosahedron()
    v = list(v)
    for _ in range(sub):
        cache, nf = {}, []

        def mid(a, b):
            k = (min(a, b), max(a, b))
            if k not in cache:
                cache[k] = len(v)
                v.append(norm(tuple((v[a][i] + v[b][i]) / 2 for i in range(3))))
            return cache[k]
        for a, b, c in faces:
            ab, bc, ca = mid(a, b), mid(b, c), mid(c, a)
            nf += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
        faces = nf
    return v, edges_from_faces(faces)


def edges_from_faces(faces):
    e = set()
    for f in faces:
        for i in range(len(f)):
            a, b = f[i], f[(i + 1) % len(f)]
            e.add((min(a, b), max(a, b)))
    return sorted(e)


def ico_wire():
    v, f = icosahedron()
    return v, edges_from_faces(f)


def torus(R=1.0, r=0.42, nu=14, nv=7):
    v, e = [], []
    for i in range(nu):
        for j in range(nv):
            u, w = TAU * i / nu, TAU * j / nv
            v.append(((R + r * math.cos(w)) * math.cos(u), r * math.sin(w), (R + r * math.cos(w)) * math.sin(u)))
    idx = lambda i, j: (i % nu) * nv + (j % nv)
    for i in range(nu):
        for j in range(nv):
            e.append((idx(i, j), idx(i + 1, j)))
            e.append((idx(i, j), idx(i, j + 1)))
    s = 1 / (R + r)
    return [(a * s, b * s, c * s) for a, b, c in v], e


def octa_cube():
    o = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    oe = [(a, b) for a in range(6) for b in range(a + 1, 6) if sum(x * y for x, y in zip(o[a], o[b])) == 0]
    k = 0.48
    c = [(x * k, y * k, z * k) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    ce = [(a, b) for a in range(8) for b in range(a + 1, 8)
          if sum(1 for i in range(3) if c[a][i] != c[b][i]) == 1]
    return o + c, oe + [(a + 6, b + 6) for a, b in ce]


def tesseract():
    v4 = [(x, y, z, w) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1) for w in (-1, 1)]
    e = [(a, b) for a in range(16) for b in range(a + 1, 16)
         if sum(1 for i in range(4) if v4[a][i] != v4[b][i]) == 1]
    return v4, e


def sphere_rings(n_lat=5, n_lon=8, seg=48):
    """Latitude / longitude polylines on a unit sphere."""
    lines = []
    for i in range(1, n_lat + 1):
        phi = -math.pi / 2 + math.pi * i / (n_lat + 1)
        lines.append([(math.cos(phi) * math.cos(TAU * k / seg), math.sin(phi), math.cos(phi) * math.sin(TAU * k / seg))
                      for k in range(seg + 1)])
    for j in range(n_lon):
        th = math.pi * j / n_lon
        lines.append([(math.cos(-math.pi / 2 + TAU * k / seg) * math.cos(th), math.sin(-math.pi / 2 + TAU * k / seg),
                       math.cos(-math.pi / 2 + TAU * k / seg) * math.sin(th)) for k in range(seg + 1)])
    return lines


# ---------------------------------------------------------------- transforms
def rx(p, a):
    x, y, z = p
    c, s = math.cos(a), math.sin(a)
    return (x, y * c - z * s, y * s + z * c)


def ry(p, a):
    x, y, z = p
    c, s = math.cos(a), math.sin(a)
    return (x * c + z * s, y, -x * s + z * c)


def rz(p, a):
    x, y, z = p
    c, s = math.cos(a), math.sin(a)
    return (x * c - y * s, x * s + y * c, z)


def project(p, cx, cy, R, cam=3.6):
    """Unit-space point -> (sx, sy, depth in [-1,1] where +1 is nearest, scale)."""
    x, y, z = p
    k = cam / (cam + z)
    return cx + x * R * k, cy - y * R * k, -z, k


def tess_frame(v4, t):
    a = TAU * t
    out = []
    for x, y, z, w in v4:
        x, w = x * math.cos(a) - w * math.sin(a), x * math.sin(a) + w * math.cos(a)
        y, z2 = y, z
        z2, w = z2 * math.cos(a) - w * math.sin(a), z2 * math.sin(a) + w * math.cos(a)
        k = 1 / (2.6 - w)
        out.append((x * k * 1.25, y * k * 1.25, z2 * k * 1.25))
    return out


# ---------------------------------------------------------------- SVG emitters
def wire_svg(frames_pts, edges, cx, cy, R, dur, color, width=1.4, op=(0.18, 1.0),
             dots=True, dot_r=2.2, cls="", glow=True):
    """frames_pts: list (N+1, last == first) of vertex lists in unit space.
    Returns SVG markup with per-edge animated path d + opacity."""
    proj = [[project(p, cx, cy, R) for p in pts] for pts in frames_pts]
    lo, hi = op
    out = [f'<g stroke="{color}" stroke-width="{width}" stroke-linecap="round" fill="none"'
           f'{" filter=\"url(#glow)\"" if glow else ""}>']
    for a, b in edges:
        ds, os_ = [], []
        for fr in proj:
            pa, pb = fr[a], fr[b]
            ds.append(f"M{f1(pa[0])} {f1(pa[1])}L{f1(pb[0])} {f1(pb[1])}")
            d = (pa[2] + pb[2]) / 2
            os_.append(f2(lo + (hi - lo) * (d + 1) / 2))
        out.append(f'<path d="{ds[0]}" stroke-opacity="{os_[0]}">'
                   f'<animate attributeName="d" dur="{dur}s" repeatCount="indefinite" values="{";".join(ds)}"/>'
                   f'<animate attributeName="stroke-opacity" dur="{dur}s" repeatCount="indefinite" values="{";".join(os_)}"/>'
                   f'</path>')
    out.append("</g>")
    if dots:
        out.append(f'<g fill="{color}">')
        for i in range(len(frames_pts[0])):
            xs = ";".join(f1(fr[i][0]) for fr in proj)
            ys = ";".join(f1(fr[i][1]) for fr in proj)
            ops = ";".join(f2(0.15 + 0.85 * (fr[i][2] + 1) / 2) for fr in proj)
            rs = ";".join(f2(dot_r * (0.6 + 0.6 * (fr[i][2] + 1) / 2)) for fr in proj)
            p0 = proj[0][i]
            out.append(f'<circle cx="{f1(p0[0])}" cy="{f1(p0[1])}" r="{dot_r}">'
                       f'<animate attributeName="cx" dur="{dur}s" repeatCount="indefinite" values="{xs}"/>'
                       f'<animate attributeName="cy" dur="{dur}s" repeatCount="indefinite" values="{ys}"/>'
                       f'<animate attributeName="r" dur="{dur}s" repeatCount="indefinite" values="{rs}"/>'
                       f'<animate attributeName="opacity" dur="{dur}s" repeatCount="indefinite" values="{ops}"/>'
                       f'</circle>')
        out.append("</g>")
    return "\n".join(out)


def spin_frames(verts, n, tilt_x=0.35, tilt_z=0.0, yturns=1, xwobble=0.0, ztwist=0.0):
    frames = []
    for k in range(n + 1):
        t = k / n
        a = TAU * yturns * t
        pts = []
        for p in verts:
            q = ry(p, a)
            q = rz(q, tilt_z + ztwist * math.sin(TAU * t))
            q = rx(q, tilt_x + xwobble * math.sin(TAU * t))
            pts.append(q)
        frames.append(pts)
    return frames


GLOW = '''<filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
<feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="bigglow" x="-50%" y="-50%" width="200%" height="200%">
<feGaussianBlur stdDeviation="7" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'''

SANS = "'Segoe UI','Inter','Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "'JetBrains Mono','Fira Code','SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"

C = dict(bg0="#05030f", bg1="#0b0820", panel="#0d1117", line="#21262d",
         cyan="#22d3ee", green="#00f5a0", violet="#a855f7", pink="#ff3ea5",
         amber="#fbbf24", blue="#60a5fa", text="#e6edf3", muted="#8b949e")
