#!/usr/bin/env python3
"""Fetch LeetCode stats and render assets/leetcode.svg in the profile's neon-3D style.

Standard library only, so it runs on a bare GitHub Actions runner.

  python3 leetcode_card.py <username> <out.svg>            # live data
  python3 leetcode_card.py <username> <out.svg> --sample   # random demo data (no network)
  python3 leetcode_card.py <username> <out.svg> --placeholder
"""
import datetime as dt
import json
import math
import random
import sys
import urllib.request
from xml.sax.saxutils import escape

W, H = 1200, 460
SANS = "'Segoe UI','Inter','Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "'JetBrains Mono','Fira Code','SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"
ORANGE, EASY, MED, HARD = "#ffa116", "#00b8a3", "#ffc01e", "#ef4743"
TEXT, MUTED, LINE = "#e6edf3", "#8b949e", "#21262d"
LOGO = ("M13.483 0a1.374 1.374 0 0 0-.961.438L7.116 6.226l-3.854 4.126a5.266 5.266 0 0 0-1.209 2.104 5.35 5.35 0 0 0-.125.513 "
        "5.527 5.527 0 0 0 .062 2.362 5.83 5.83 0 0 0 .349 1.017 5.938 5.938 0 0 0 1.271 1.818l4.277 4.193.039.038c2.248 2.165 "
        "5.852 2.133 8.063-.074l2.396-2.392c.54-.54.54-1.414.003-1.955a1.378 1.378 0 0 0-1.951-.003l-2.396 2.392a3.021 3.021 0 0 "
        "1-4.205.038l-.02-.019-4.276-4.193c-.652-.64-.972-1.469-.948-2.263a2.68 2.68 0 0 1 .066-.523 2.545 2.545 0 0 1 .619-1.164L9.13 "
        "8.114c1.058-1.134 3.204-1.27 4.43-.278l3.501 2.831c.593.48 1.461.387 1.94-.207a1.384 1.384 0 0 0-.207-1.943l-3.5-2.831c-.8-.647"
        "-1.766-1.045-2.774-1.202l2.015-2.158A1.384 1.384 0 0 0 13.483 0zm-2.866 12.815a1.38 1.38 0 0 0-1.38 1.382 1.38 1.38 0 0 0 1.38 "
        "1.382H20.79a1.38 1.38 0 0 0 1.38-1.382 1.38 1.38 0 0 0-1.38-1.382z")
WEEKS = 20

QUERY = """query($username: String!) {
  allQuestionsCount { difficulty count }
  matchedUser(username: $username) {
    profile { ranking }
    submitStats { acSubmissionNum { difficulty count } }
    userCalendar { streak totalActiveDays submissionCalendar }
  }
  userContestRanking(username: $username) { rating attendedContestsCount topPercentage }
}"""


# ------------------------------------------------------------------ data
def fetch(username):
    req = urllib.request.Request(
        "https://leetcode.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"username": username}}).encode(),
        headers={"Content-Type": "application/json", "Referer": f"https://leetcode.com/u/{username}/",
                 "User-Agent": "Mozilla/5.0 (profile-readme-card)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    d = body.get("data") or {}
    u = d.get("matchedUser")
    if not u:
        raise SystemExit(f"LeetCode returned no user for {username!r}: {body.get('errors')}")
    tot = {x["difficulty"]: x["count"] for x in d["allQuestionsCount"]}
    ac = {x["difficulty"]: x["count"] for x in u["submitStats"]["acSubmissionNum"]}
    cal = u.get("userCalendar") or {}
    sub = {int(k): v for k, v in json.loads(cal.get("submissionCalendar") or "{}").items()}
    cr = d.get("userContestRanking") or {}
    return dict(total=tot, solved=ac, ranking=(u.get("profile") or {}).get("ranking"),
                streak=cal.get("streak"), active=cal.get("totalActiveDays"), calendar=sub,
                rating=cr.get("rating"), contests=cr.get("attendedContestsCount"), top=cr.get("topPercentage"))


def sample():
    rnd = random.Random(4)
    today = dt.datetime.now(dt.timezone.utc).date()
    cal = {}
    for k in range(WEEKS * 7):
        if rnd.random() < 0.45:
            day = today - dt.timedelta(days=k)
            ts = int(dt.datetime(day.year, day.month, day.day, tzinfo=dt.timezone.utc).timestamp())
            cal[ts] = rnd.choice([1, 1, 2, 3, 4, 6, 9])
    return dict(total={"All": 3420, "Easy": 860, "Medium": 1790, "Hard": 770},
                solved={"All": 214, "Easy": 102, "Medium": 96, "Hard": 16},
                ranking=412345, streak=17, active=96, calendar=cal, rating=1544.3, contests=6, top=31.2)


def placeholder():
    return dict(total={"All": 0, "Easy": 0, "Medium": 0, "Hard": 0}, solved={"All": 0, "Easy": 0, "Medium": 0, "Hard": 0},
                ranking=None, streak=None, active=None, calendar={}, rating=None, contests=None, top=None)


# ------------------------------------------------------------------ render helpers
def fmt(n):
    return "—" if n is None else f"{int(round(n)):,}"


def ring(cx, cy, r, s):
    """Full ring split by difficulty share of solved problems."""
    circ = 2 * math.pi * r
    solved = sum(s.get(k, 0) for k in ("Easy", "Medium", "Hard"))
    out = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{TEXT}" stroke-opacity="0.08" stroke-width="12"/>']
    start, gap = 0.0, 6.0
    for key, col in (("Easy", EASY), ("Medium", MED), ("Hard", HARD)):
        seg = (s.get(key, 0) / solved * circ) if solved else 0
        if seg <= 0:
            continue
        L = max(seg - gap, 0.5)
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" stroke-width="12" stroke-linecap="round" '
                   f'transform="rotate({-90 + (start + gap / 2) * 360 / circ:.2f} {cx} {cy})" stroke-dasharray="0 {circ:.1f}" filter="url(#glow)">'
                   f'<animate attributeName="stroke-dasharray" values="0 {circ:.1f};{L:.1f} {circ:.1f};{L:.1f} {circ:.1f};0 {circ:.1f}" '
                   f'keyTimes="0;0.18;0.9;1" dur="8s" repeatCount="indefinite"/></circle>')
        start += seg
    return "".join(out)


def orbit(cx, cy, rx_, ry_, tilt, dur, col):
    t = math.radians(tilt)
    pt = lambda a: (cx + rx_ * math.cos(a) * math.cos(t) - ry_ * math.sin(a) * math.sin(t),
                    cy + rx_ * math.cos(a) * math.sin(t) + ry_ * math.sin(a) * math.cos(t))
    back = "M" + "L".join("%.1f %.1f" % pt(math.pi + math.pi * k / 40) for k in range(41))
    front = "M" + "L".join("%.1f %.1f" % pt(math.pi * k / 40) for k in range(41))
    n = 60
    xs, ys, op = [], [], []
    for k in range(n + 1):
        a = 2 * math.pi * k / n
        x, y = pt(a)
        xs.append(f"{x:.1f}"); ys.append(f"{y:.1f}"); op.append(f"{0.25 + 0.75 * (math.sin(a) + 1) / 2:.2f}")
    return (f'<path d="{back}" fill="none" stroke="{col}" stroke-opacity="0.2"/>',
            f'<path d="{front}" fill="none" stroke="{col}" stroke-opacity="0.65" stroke-width="1.5" filter="url(#glow)"/>'
            f'<circle r="4.5" fill="{col}" filter="url(#glow)"><animate attributeName="cx" values="{";".join(xs)}" dur="{dur}s" repeatCount="indefinite"/>'
            f'<animate attributeName="cy" values="{";".join(ys)}" dur="{dur}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="{";".join(op)}" dur="{dur}s" repeatCount="indefinite"/></circle>')


def bar(x, y, w, label, col, solved, total, delay):
    pct = (solved / total) if total else 0
    fw = max(pct * w, 0 if not solved else 6)
    return (f'<text x="{x}" y="{y}" font-family="{SANS}" font-size="17" font-weight="700" fill="{col}">{label}</text>'
            f'<text x="{x + w}" y="{y}" text-anchor="end" font-family="{MONO}" font-size="15" fill="{TEXT}">{fmt(solved)}'
            f'<tspan fill="{MUTED}"> / {fmt(total)}</tspan></text>'
            f'<rect x="{x}" y="{y + 12}" width="{w}" height="10" rx="5" fill="{col}" fill-opacity="0.15"/>'
            f'<rect x="{x}" y="{y + 12}" height="10" rx="5" fill="{col}" width="0" filter="url(#glow)">'
            f'<animate attributeName="width" values="0;{fw:.1f};{fw:.1f};0" keyTimes="0;0.18;0.9;1" dur="8s" begin="{delay}s" repeatCount="indefinite"/></rect>')


def tile(x, y, w, label, value, sub=""):
    return (f'<g transform="translate({x},{y})"><rect width="{w}" height="62" rx="12" fill="#0a0f1d" stroke="{ORANGE}" stroke-opacity="0.25"/>'
            f'<text x="16" y="24" font-family="{MONO}" font-size="12" letter-spacing="1" fill="{MUTED}">{escape(label)}</text>'
            f'<text x="16" y="50" font-family="{SANS}" font-size="22" font-weight="800" fill="{TEXT}">{escape(value)}'
            f'<tspan font-size="13" font-weight="500" fill="{MUTED}">{escape(sub)}</tspan></text></g>')


def iso_heatmap(cal, ox, oy, c=15):
    today = dt.datetime.now(dt.timezone.utc).date()
    end = today + dt.timedelta(days=(5 - today.weekday()) % 7)        # Saturday of this week
    start = end - dt.timedelta(days=WEEKS * 7 - 1)                     # a Sunday
    by_day = {}
    for ts, n in cal.items():
        by_day[dt.datetime.fromtimestamp(ts, dt.timezone.utc).date()] = by_day.get(
            dt.datetime.fromtimestamp(ts, dt.timezone.utc).date(), 0) + n
    days = [(start + dt.timedelta(days=k)) for k in range(WEEKS * 7)]
    mx = max([by_day.get(d, 0) for d in days] + [1])
    nz = sorted(by_day.get(d, 0) for d in days if by_day.get(d, 0) > 0)
    qs = [nz[int(len(nz) * q)] for q in (0.25, 0.5, 0.75)] if nz else [1, 2, 3]
    cs, sn = c * math.cos(math.radians(30)), c * 0.5
    P = lambda i, j, h=0: (ox + (i - j) * cs, oy + (i + j) * sn - h)
    shades = [("#1b2333", "#141a27", "#10151f"), ("#7a4a0f", "#5a360a", "#462a08"), ("#b8680f", "#8a4e0b", "#6b3c08"),
              ("#f08c12", "#b4690d", "#8c510a"), ("#ffc04d", "#ff9a1a", "#d07a0c")]
    cells = []
    for k, d in enumerate(days):
        i, j = k // 7, k % 7
        n = by_day.get(d, 0) if d <= today else 0
        lvl = 0 if n == 0 else 1 + sum(1 for q in qs if n > q)   # quartiles of active days
        cells.append((i + j, i, j, lvl, d > today))
    cells.sort()
    out = []
    for _, i, j, lvl, future in cells:
        top, left, right = shades[lvl]
        if future:
            continue
        hmax = 3 if lvl == 0 else 5 + lvl * 8
        hmin = 3

        def faces(h):
            a, b, cc, dd = P(i, j, h), P(i + 1, j, h), P(i + 1, j + 1, h), P(i, j + 1, h)
            b0, cc0, dd0 = P(i + 1, j), P(i + 1, j + 1), P(i, j + 1)
            f = lambda pts: " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
            return f([a, b, cc, dd]), f([dd, cc, cc0, dd0]), f([b, cc, cc0, b0])
        if lvl == 0:
            t, l, r = faces(hmax)
            out.append(f'<polygon points="{t}" fill="{top}"/><polygon points="{l}" fill="{left}"/><polygon points="{r}" fill="{right}"/>')
            continue
        lo, hi = faces(hmin), faces(hmax)
        t0 = ((i + j) / (WEEKS + 6)) * 0.3
        kt = f"0;{t0:.3f};{t0 + 0.15:.3f};0.88;0.96;1"
        polys = []
        for idx, col in enumerate((top, left, right)):
            v = f"{lo[idx]};{lo[idx]};{hi[idx]};{hi[idx]};{lo[idx]};{lo[idx]}"
            polys.append(f'<polygon points="{lo[idx]}" fill="{col}"><animate attributeName="points" values="{v}" keyTimes="{kt}" '
                         f'dur="9s" repeatCount="indefinite"/></polygon>')
        # draw order inside a bar: sides first, top last
        out.append(polys[1] + polys[2] + polys[0])
    return "".join(out), mx


# ------------------------------------------------------------------ card
def render(username, d):
    tot, s = d["total"], d["solved"]
    total_all, solved_all = tot.get("All", 0), s.get("All", 0)
    cx, cy = 200, 262
    ob, of = orbit(cx, cy, 150, 36, -12, 6, ORANGE)
    heat, mx = iso_heatmap(d["calendar"], 890, 200, c=14)
    rating = fmt(d["rating"])
    top = f'  top {d["top"]:.1f}%' if d.get("top") else ""
    updated = dt.datetime.now(dt.timezone.utc).strftime("%d %b %Y")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="LeetCode stats for {escape(username)}">
<title>LeetCode — {solved_all} problems solved</title>
<defs>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<linearGradient id="lbg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b0f1c"/><stop offset="1" stop-color="#1a0f24"/></linearGradient>
<radialGradient id="lspot" cx="0.17" cy="0.55" r="0.35"><stop offset="0" stop-color="{ORANGE}" stop-opacity="0.18"/><stop offset="1" stop-color="{ORANGE}" stop-opacity="0"/></radialGradient>
<clipPath id="lc"><rect width="{W}" height="{H}" rx="22"/></clipPath>
</defs>
<g clip-path="url(#lc)">
<rect width="{W}" height="{H}" fill="url(#lbg)"/><rect width="{W}" height="{H}" fill="url(#lspot)"/>
<path d="{LOGO}" fill="{ORANGE}" transform="translate(36,26) scale(1.3)"/>
<text x="76" y="52" font-family="{SANS}" font-size="28" font-weight="800" fill="{TEXT}">LeetCode</text>
<text x="226" y="52" font-family="{MONO}" font-size="15" fill="{MUTED}">@{escape(username)}</text>
<text x="{W - 36}" y="52" text-anchor="end" font-family="{MONO}" font-size="12" fill="{MUTED}">updated {updated}</text>
{ob}
{ring(cx, cy, 100, s)}
{of}
<text x="{cx}" y="{cy + 8}" text-anchor="middle" font-family="{SANS}" font-size="50" font-weight="900" fill="{TEXT}">{fmt(solved_all)}</text>
<text x="{cx}" y="{cy + 34}" text-anchor="middle" font-family="{MONO}" font-size="14" fill="{MUTED}">solved of {fmt(total_all)}</text>
{bar(410, 128, 360, "Easy", EASY, s.get("Easy", 0), tot.get("Easy", 0), 0)}
{bar(410, 186, 360, "Medium", MED, s.get("Medium", 0), tot.get("Medium", 0), 0.15)}
{bar(410, 244, 360, "Hard", HARD, s.get("Hard", 0), tot.get("Hard", 0), 0.3)}
{tile(410, 300, 174, "GLOBAL RANK", "#" + fmt(d["ranking"]) if d["ranking"] else "—")}
{tile(596, 300, 174, "CONTEST RATING", rating, top) if d["rating"] else tile(596, 300, 174, "SUBMISSIONS · 1Y", fmt(sum(d["calendar"].values())))}
{tile(410, 374, 174, "BEST STREAK", fmt(d["streak"]), " days" if d["streak"] is not None else "")}
{tile(596, 374, 174, "ACTIVE DAYS", fmt(d["active"]), " this year" if d["active"] is not None else "")}
<text x="1004" y="116" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{MUTED}">submissions · last {WEEKS} weeks</text>
{heat}
<g transform="translate(930,428)" font-family="{MONO}" font-size="11" fill="{MUTED}"><text x="0" y="0">less</text>
{"".join(f'<rect x="{34 + k * 16}" y="-10" width="12" height="12" rx="2" fill="{c}"/>' for k, c in enumerate(["#1b2333", "#7a4a0f", "#b8680f", "#f08c12", "#ffc04d"]))}
<text x="{34 + 5 * 16 + 4}" y="0">more</text></g>
</g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="none" stroke="{LINE}" stroke-width="1.5"/>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="none" stroke="{ORANGE}" stroke-width="2.4" pathLength="1000" stroke-dasharray="110 890" stroke-linecap="round" filter="url(#glow)"><animate attributeName="stroke-dashoffset" values="0;-1000" dur="9s" repeatCount="indefinite"/></rect>
</svg>'''


if __name__ == "__main__":
    user, out = sys.argv[1], sys.argv[2]
    mode = sys.argv[3] if len(sys.argv) > 3 else ""
    data = sample() if mode == "--sample" else placeholder() if mode == "--placeholder" else fetch(user)
    open(out, "w").write(render(user, data))
    print(f"wrote {out}: {data['solved'].get('All', 0)} solved")
