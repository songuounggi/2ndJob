# -*- coding: utf-8 -*-
"""Generate the ADHD/wellness planner as HTML, then print it to PDF with Chrome.

Pipeline per CLAUDE.md: HTML/CSS -> headless Chrome print-to-PDF, which keeps
internal `#anchor` links as PDF named destinations.
"""

import calendar
import os
import tempfile
import urllib.parse
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
YEAR = 2026

TABS = [
    ("index",  "INDEX"),
    ("year",   "YEAR"),
    ("month",  "MONTH"),
    ("week",   "WEEK"),
    ("day",    "DAY"),
    ("tasks",  "TASKS"),
    ("habits", "HABITS"),
    ("meds",   "MEDS"),
    ("notes",  "NOTES"),
]

# --------------------------------------------------------------- themes --
# v2 follows the researched "adult ADHD self" palette: warm paper instead of
# white, and four category colours (the ceiling before colour coding starts
# hurting recall) mapped onto the section groups.
THEMES = {
    "v1-admin": {
        "font": "Inter", "weights": "400;600;700", "display": None,
        "radius": "10pt", "tab_dots": False,
        "bg": "#F4F6F5", "card": "#FFFFFF", "ink": "#22262B",
        "mid": "#5A616B", "soft": "#7C8087", "line": "#E4E7E6",
        "field": "#F3F5F4",
        "sections": {k: ("#12855C", "#E7F2EC", "#0F6E4C") for k, _ in TABS},
    },
    "v2-warm": {
        "font": "Nunito", "weights": "400;600;700;800", "display": "Caveat",
        "radius": "14pt", "tab_dots": True,
        "bg": "#FBF8F3", "card": "#FFFFFF", "ink": "#3A3A3A",
        "mid": "#6E6A64", "soft": "#827D75", "line": "#EAE4DA",
        "field": "#F6F2EA",
        # section -> (decorative accent, tint, text tone).
        # The pastel reads well as a bar/dot/fill but only hits ~2.5:1 as text,
        # so every coloured *word* uses the darker tone (>=4.8:1 on white).
        "sections": {
            "index":  ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "year":   ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "month":  ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "week":   ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "day":    ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "tasks":  ("#E08A73", "#FBEDE8", "#B4543A"),
            "habits": ("#E08A73", "#FBEDE8", "#B4543A"),
            "meds":   ("#7FA37C", "#ECF3EB", "#4A7248"),
            "notes":  ("#D9A441", "#FBF1DC", "#8A6415"),
        },
    },
    # v2 with the user's own sky photo washed into the page background.
    # Cards stay fully opaque so writing areas keep their contrast; only the
    # paper behind them carries the image.
    "v5-sky": {
        "font": "Nunito", "weights": "400;600;700;800", "display": "Caveat",
        "radius": "14pt", "tab_dots": True,
        "bg": "#FBF8F3", "card": "#FFFFFF", "ink": "#3A3A3A",
        "mid": "#6E6A64", "soft": "#827D75", "line": "#EAE4DA",
        "field": "#F6F2EA",
        "photo": "../assets/sky.jpg",
        "photo_cover": 0.20,   # showcase page, the photo is the point
        "photo_page": 0.0,     # working pages get the bloom only -- a photo
                               # behind handwriting is visual noise
        "bloom_cover": 0.42,
        "bloom_page": 0.55,
        # one faint cool stop, as first shipped
        "bloom_cool": [(-100, -12, 124, 92, "#B3C6D6", .26)],
        "sections": {
            "index":  ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "year":   ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "month":  ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "week":   ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "day":    ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "tasks":  ("#E08A73", "#FBEDE8", "#B4543A"),
            "habits": ("#E08A73", "#FBEDE8", "#B4543A"),
            "meds":   ("#7FA37C", "#ECF3EB", "#4A7248"),
            "notes":  ("#D9A441", "#FBF1DC", "#8A6415"),
        },
    },
    # v5 with the cool side of the bloom carried further left: the sky blue
    # builds over three stops and thins out toward the page edge.
    "v6-skyblue": {
        "font": "Nunito", "weights": "400;600;700;800", "display": "Caveat",
        "radius": "14pt", "tab_dots": True,
        "bg": "#FBF8F3", "card": "#FFFFFF", "ink": "#3A3A3A",
        "mid": "#6E6A64", "soft": "#827D75", "line": "#EAE4DA",
        "field": "#F6F2EA",
        "photo": "../assets/sky.jpg",
        "photo_cover": 0.20,
        "photo_page": 0.0,
        "bloom_cover": 0.42,
        "bloom_page": 0.55,
        "bloom_cool": [
            (-104, -14, 138, 100, "#AFC9DF", .34),  # sky blue picks up
            (-152, -22, 158, 108, "#A3C4E2", .30),  # wider, airier
            (-206, -30, 172, 112, "#B6D2EC", .22),  # fades out to the edge
        ],
        "sections": {
            "index":  ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "year":   ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "month":  ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "week":   ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "day":    ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "tasks":  ("#E08A73", "#FBEDE8", "#B4543A"),
            "habits": ("#E08A73", "#FBEDE8", "#B4543A"),
            "meds":   ("#7FA37C", "#ECF3EB", "#4A7248"),
            "notes":  ("#D9A441", "#FBF1DC", "#8A6415"),
        },
    },
    # Palette B from the research: parents + teens. Sunset range, higher
    # saturation, rounder type -- reads as "made for me", not clinical.
    "v3-sunset": {
        "font": "Quicksand", "weights": "400;600;700", "display": None,
        "radius": "16pt", "tab_dots": True,
        "bg": "#FFF4E8", "card": "#FFFFFF", "ink": "#3B3335",
        "mid": "#6F625F", "soft": "#9A8C88", "line": "#F0E2D4",
        "field": "#FDF3E9",
        "sections": {
            "index":  ("#FF8A65", "#FFE8E0", "#B84A25"),
            "year":   ("#FF8A65", "#FFE8E0", "#B84A25"),
            "month":  ("#FF8A65", "#FFE8E0", "#B84A25"),
            "week":   ("#FF8A65", "#FFE8E0", "#B84A25"),
            "day":    ("#FF8A65", "#FFE8E0", "#B84A25"),
            "tasks":  ("#F06292", "#FDE4EC", "#A82A60"),
            "habits": ("#F06292", "#FDE4EC", "#A82A60"),
            "meds":   ("#4CAF7D", "#E3F4EA", "#2A6E4A"),
            "notes":  ("#9575CD", "#EDE7F8", "#5F429B"),
        },
    },
}

VERSION = os.environ.get("PLANNER_VERSION", "v2-warm")
T = THEMES[VERSION]
SRC = os.path.join(ROOT, "src", f"planner_{VERSION}.html")
OUT = os.path.join(ROOT, "output", f"planner_{VERSION}.pdf")

ROOT_VARS = f""":root{{
  --bg:{T['bg']}; --card:{T['card']}; --ink:{T['ink']}; --mid:{T['mid']};
  --soft:{T['soft']}; --line:{T['line']}; --field:{T['field']};
  --radius:{T['radius']}; --font:'{T['font']}';
  --accent:#12855C; --chip:#E7F2EC; --accent-text:#0F6E4C;
}}"""

BASE_CSS = """
*{box-sizing:border-box;-webkit-print-color-adjust:exact;print-color-adjust:exact}
@page{size:612pt 792pt;margin:0}
body{margin:0;font-family:var(--font),system-ui,sans-serif;color:var(--ink);
     -webkit-font-smoothing:antialiased}

.page{width:612pt;height:792pt;background:var(--bg);position:relative;
      page-break-after:always;overflow:hidden}
.page:last-child{page-break-after:auto}
/* Background wash layers. They sit under everything and never under a card's
   own white, so writing areas keep full contrast. */
.bg-photo,.bg-bloom{position:absolute;inset:0;background-size:cover;
      background-position:center;pointer-events:none}
.bg-bloom{background-repeat:no-repeat}

/* ---------- tab rail ---------- */
.rail{position:absolute;left:0;top:0;width:58pt;height:792pt;
      border-right:1px solid var(--line);display:flex;flex-direction:column;
      padding:4pt}
.rail a{flex:1;display:flex;align-items:center;justify-content:center;
        position:relative;margin:2pt 0;border-radius:var(--radius);
        text-decoration:none}
.rail a span{writing-mode:vertical-rl;transform:rotate(180deg);font-size:7pt;
        font-weight:700;letter-spacing:.06em;color:var(--soft)}
.rail a i{position:absolute;left:50%;margin-left:-2.5pt;top:calc(50% - 27pt);
        width:5pt;height:5pt;border-radius:99pt;opacity:.55}
.rail a.on{background:var(--card);
        box-shadow:0 0 2pt rgba(0,0,0,.05), 0 0 6pt rgba(0,0,0,.035)}
.rail a.on i{opacity:1}
.rail a.on span{color:var(--acc-text);font-weight:800}
.rail a.on::before{content:"";position:absolute;left:5pt;top:50%;
        transform:translateY(-50%);width:2.4pt;height:24pt;
        background:var(--acc);border-radius:2pt}
/* The active tab is a raised card too, so it gets the same directional
   shadow as .card -- without this it reads as an evenly lit box and breaks
   the light source the rest of the page establishes. */
.rail a.on::after{content:"";position:absolute;left:8%;right:8%;top:100%;
        height:11pt;background:radial-gradient(ellipse 62% 100% at 50% 0%,
        rgba(0,0,0,.07), rgba(0,0,0,0) 72%);pointer-events:none}

/* ---------- page skeleton ---------- */
.content{position:absolute;left:84pt;right:28pt;top:0;bottom:0;
         display:flex;flex-direction:column;padding:42pt 0 34pt}
.head{flex:none}
.body{flex:1;display:flex;flex-direction:column;gap:12pt;margin-top:20pt;
      min-height:0}

.eyebrow{display:flex;align-items:center;gap:8pt;font-size:9.5pt;font-weight:700;
         color:var(--mid)}
.eyebrow::before{content:"";width:2.6pt;height:11pt;background:var(--accent);
         border-radius:1pt}
h1{font-size:23pt;font-weight:800;margin:11pt 0 0;letter-spacing:-.01em}
.sub{color:var(--soft);font-size:9.5pt;margin-top:5pt}
.titlerow{display:flex;align-items:center;gap:16pt}

/* ---------- pieces ---------- */
/* Elevation is ONE continuous falloff, not two stacked shadows.
   - box-shadow: tight and un-offset, so it only defines the edge.
   - ::after: the drop shadow proper. It starts exactly at the card's bottom
     edge (top:100%) and its gradient centre sits at its own top-centre, so
     density peaks right under the card and fades both downward and sideways.
   Offsetting the box-shadow instead put its peak below the edge, which left a
   bright gap between the two and read as two separate lines. */
.card{background:var(--card);border-radius:var(--radius);
      box-shadow:0 0 2pt rgba(0,0,0,.05), 0 0 6pt rgba(0,0,0,.035);
      padding:16pt;display:flex;flex-direction:column;min-height:0;
      position:relative}
/* `top` must be exactly 100% -- no offset. Pushing the pool even 1pt below the
   edge leaves a seam that subpixel rounding exposes on some cards and not
   others (the Focus card on the index page showed a 5-level bright row while
   its neighbours did not), which reads as the "two lines" defect on that card
   alone. At 100% every card measures identically. */
.card::after{content:"";position:absolute;left:4%;right:4%;top:100%;height:13pt;
      background:radial-gradient(ellipse 62% 100% at 50% 0%, rgba(0,0,0,.07),
      rgba(0,0,0,0) 72%);pointer-events:none}
.label{display:flex;align-items:center;gap:7pt;font-size:9pt;font-weight:800;
       color:var(--ink);margin-bottom:10pt;flex:none}
.label::before{content:"";width:2.6pt;height:10pt;background:var(--accent);
       border-radius:1pt;flex:none}
.chip{display:inline-block;background:var(--chip);color:var(--accent-text);
      font-size:7.5pt;font-weight:800;padding:3pt 9pt;border-radius:99pt;
      letter-spacing:.03em}
.field{background:var(--field);border-radius:6pt;height:19pt;flex:none}
.box{width:12pt;height:12pt;border:1.2px solid var(--line);border-radius:3pt;
     flex:none}

.lines{flex:1;display:flex;flex-direction:column;min-height:0}
.lines>div{flex:1;border-bottom:1px solid var(--line);min-height:16pt}

.row{display:flex;gap:12pt;flex:1;min-height:0}
.col{display:flex;flex-direction:column;gap:12pt;min-height:0}

/* ---------- grids ---------- */
.cal{border-collapse:collapse;width:100%;height:100%;table-layout:fixed}
.cal td{border:1px solid var(--line);vertical-align:top;padding:5pt 6pt;
        font-size:8.5pt;font-weight:700}
.cal th{font-size:7.5pt;color:var(--soft);font-weight:800;padding-bottom:7pt;
        letter-spacing:.05em;height:18pt}
.cal .we{color:var(--accent-text)}

.mini{width:100%;border-collapse:collapse}
.mini td,.mini th{text-align:center;font-size:5.6pt;padding:1.3pt 0;line-height:1}
.mini th{color:var(--soft);font-weight:800;font-size:5.2pt}
.mini .we{color:var(--accent-text)}

.trk{border-collapse:collapse;width:100%;height:100%;table-layout:fixed}
.trk td{border:1px solid var(--line)}
.trk .nm{border:none;border-bottom:1px solid var(--line);text-align:left;
         font-size:8.5pt;padding:0 8pt 0 2pt;white-space:nowrap;width:104pt}
.trk .dh{border:none;font-size:5.4pt;color:var(--soft);font-weight:800;
         height:13pt;vertical-align:bottom;padding-bottom:3pt;text-align:center}
.trk .dh.we{color:var(--accent-text)}
.trk tr:first-child .nm{border-bottom:none}

.dots{background-image:radial-gradient(var(--line) 1.1px, transparent 1.1px);
      background-size:14pt 14pt;background-position:8pt 8pt}
"""

CSS = ROOT_VARS + BASE_CSS


def bloom_svg(cx=306, cy=250):
    """Iridescent bloom traced from the user's sky photo.

    Measured hues in the photo run 34-49 deg only -- pure amber to yellow, no
    green or blue at any usable saturation. What reads as a spectrum is
    simultaneous contrast: the #FFFBE8 core looks cool against the warm
    surround. So the warm stops below are the photo's real sampled values, and
    the cool ones are held very faint and placed on the left, where the eye
    already reads them.
    """
    stops = [
        # dx,  dy,  rx,  ry,  colour,    alpha   (dx/dy are offsets from cx,cy)
        (0,    0, 118, 92, "#FFFBE8", .95),   # core, sampled #FFFFE8
        (24,   8, 150, 108, "#F5DC97", .80),  # amber, sampled #F1D790
        (60,  18, 165, 112, "#E9B87E", .62),  # orange, sampled #EFCA8B
        (104, 28, 150, 104, "#E3A492", .40),  # pink edge
        (-56, -6, 132, 96, "#C6D2AC", .30),   # faint green, left
    ] + T.get("bloom_cool", [])
    stops = [(cx + dx, cy + dy, rx, ry, c, a) for dx, dy, rx, ry, c, a in stops]
    ell = "".join(
        f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{c}" '
        f'opacity="{a}"/>' for x, y, rx, ry, c, a in stops)
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="612" height="792" '
        'viewBox="0 0 612 792">'
        '<defs><filter id="b" x="-40%" y="-40%" width="180%" height="180%">'
        '<feGaussianBlur stdDeviation="52"/></filter></defs>'
        f'<g filter="url(#b)">{ell}</g></svg>')
    # Percent-encode the whole payload: the SVG contains quotes, spaces and
    # parentheses (url(#b)), any of which would terminate the style attribute
    # or the url() token if passed through raw.
    return "data:image/svg+xml," + urllib.parse.quote(svg, safe="")


def bloom_png(path, cx=306, cy=250, scale=0.5, blur=52):
    """Bake the bloom to a PNG so all pages share one image resource.

    Inlining the SVG re-rasterises it per page; a single file is referenced
    once. The bloom is heavily blurred, so storing it at half size costs
    nothing visible and cuts the file substantially.
    """
    from PIL import Image, ImageDraw, ImageFilter
    W, H = 612, 792
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    stops = [
        (0, 0, 118, 92, "#FFFBE8", .95),
        (24, 8, 150, 108, "#F5DC97", .80),
        (60, 18, 165, 112, "#E9B87E", .62),
        (104, 28, 150, 104, "#E3A492", .40),
        (-56, -6, 132, 96, "#C6D2AC", .30),
    ] + T.get("bloom_cool", [])
    for dx, dy, rx, ry, col, a in stops:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        r, g, b = (int(col[i:i + 2], 16) for i in (1, 3, 5))
        ex, ey = cx + dx, cy + dy
        ImageDraw.Draw(layer).ellipse(
            [ex - rx, ey - ry, ex + rx, ey + ry], fill=(r, g, b, int(a * 255)))
        base = Image.alpha_composite(base, layer)
    # Blur with premultiplied alpha. Blurring straight RGBA mixes the RGB of
    # fully transparent pixels -- which is black -- into the visible edge and
    # darkens the whole bloom (measured ~7 grey levels against the SVG).
    import numpy as np
    a = np.asarray(base).astype(np.float64)
    al = a[..., 3:4] / 255.0
    a[..., :3] *= al
    blurred = np.asarray(
        Image.fromarray(a.astype(np.uint8), "RGBA")
        .filter(ImageFilter.GaussianBlur(blur))).astype(np.float64)
    out_a = blurred[..., 3:4]
    rgb = np.divide(blurred[..., :3] * 255.0, np.maximum(out_a, 1e-6))
    base = Image.fromarray(
        np.concatenate([np.clip(rgb, 0, 255), out_a], axis=2).astype(np.uint8),
        "RGBA")
    if scale != 1.0:
        base = base.resize((int(W * scale), int(H * scale)), Image.LANCZOS)
    base.save(path, optimize=True)
    return path


# ---------------------------------------------------------------- helpers --
def section_colors(key):
    """(decorative accent, tint, text tone) for a section."""
    return T["sections"].get(key, next(iter(T["sections"].values())))


def rail(active):
    out = []
    for k, lb in TABS:
        acc, _, txt = section_colors(k)
        dot = f'<i style="background:{acc}"></i>' if T["tab_dots"] else ""
        out.append(f'<a class="{"on" if k == active else ""}" href="#{k}" '
                   f'style="--acc:{acc};--acc-text:{txt}">{dot}<span>{lb}</span></a>')
    return f'<nav class="rail">{"".join(out)}</nav>'


def page(key, body):
    acc, tint, txt = section_colors(key)
    style = f"--accent:{acc};--chip:{tint};--accent-text:{txt}"
    layers = ""
    if T.get("photo"):
        cover = key == "cover"
        po = T["photo_cover"] if cover else T["photo_page"]
        bo = T["bloom_cover"] if cover else T["bloom_page"]
        if po:
            layers += (f'<div class="bg-photo" style="background-image:'
                       f'url(\'{T["photo"]}\');opacity:{po}"></div>')
        # On working pages the cards cover the middle, so the bloom is moved
        # up behind the header where background is actually visible.
        # One baked PNG per position, shared by every page that uses it.
        name = "bloom_cover" if cover else "bloom_page"
        layers += (f'<div class="bg-bloom" style="background-image:'
                   f"url('../assets/{name}_{VERSION}.png');opacity:{bo}\"></div>")
    return (f'<section class="page" id="{key}" style="{style}">{layers}'
            f'{rail(key)}<div class="content">{body}</div></section>')


def head(eyebrow, title, sub="", field_after=False):
    t = f"<h1>{title}</h1>"
    if field_after:
        t = (f'<div class="titlerow"><h1>{title}</h1>'
             f'<div class="field" style="flex:1;max-width:210pt;height:22pt"></div></div>')
    s = f'<div class="sub">{sub}</div>' if sub else ""
    return f'<div class="head"><div class="eyebrow">{eyebrow}</div>{t}{s}</div>'


def lines(n):
    return '<div class="lines">' + "<div></div>" * n + "</div>"


def checkrow(field_flex=1):
    return ('<div style="display:flex;align-items:center;gap:9pt">'
            f'<div class="box"></div><div class="field" style="flex:{field_flex}"></div></div>')


# ------------------------------------------------------------------ pages --
def p_cover():
    items = [
        ("Index &amp; year view", "see everything, jump anywhere", "2"),
        ("Monthly / weekly / daily", "the three you'll use every day", "3"),
        ("Task breakdown", "make the big thing smaller", "1"),
        ("Habit &amp; medication log", "31-day grid, no streak guilt", "2"),
        ("Notes", "dot grid, yours to fill", "1"),
    ]
    rows = "".join(
        f'<div style="display:flex;align-items:center;gap:12pt;padding:11pt 0;'
        f'{"" if i == len(items) - 1 else "border-bottom:1px solid var(--line)"}">'
        f'<div style="width:5pt;height:5pt;border-radius:99pt;background:var(--accent);'
        f'flex:none"></div>'
        f'<div style="flex:1"><div style="font-size:10pt;font-weight:700">{t}</div>'
        f'<div style="font-size:8.5pt;color:var(--soft);margin-top:2pt">{d}</div></div>'
        f'<span class="chip">{c}</span></div>'
        for i, (t, d, c) in enumerate(items))
    return f"""
    <div class="head" style="flex:1;display:flex;flex-direction:column;
         align-items:center;justify-content:center;text-align:center">
      <div style="width:28pt;height:2.6pt;background:var(--accent);margin-bottom:18pt"></div>
      <span class="chip">UNDATED &middot; NO-GUILT</span>
      <div style="font-size:31pt;font-weight:700;line-height:1.18;margin-top:20pt;
                  letter-spacing:-.02em">{YEAR} ADHD &amp;<br>Wellness Planner</div>
      <div style="color:var(--mid);font-size:11pt;margin-top:12pt">
        Start any day. Skip a week. Nothing to catch up on.</div>
    </div>
    <div class="card" style="flex:none;padding:18pt 22pt;margin-bottom:6pt">
      <div class="label">What's inside</div>{rows}
    </div>"""


def p_index():
    groups = [
        ("Plan", [("year", "Year at a glance"), ("month", "Monthly overview"),
                  ("week", "Weekly spread"), ("day", "Daily page")]),
        ("Focus", [("tasks", "Task breakdown"), ("habits", "Habit tracker")]),
        ("Health", [("meds", "Medication log")]),
        ("Free", [("notes", "Notes")]),
    ]
    cards = []
    for title, links in groups:
        rows = "".join(
            f'<a href="#{k}" style="display:flex;align-items:center;gap:10pt;flex:1;'
            f'text-decoration:none;color:var(--ink);'
            f'{"" if i == len(links) - 1 else "border-bottom:1px solid var(--line)"}">'
            f'<div style="width:4pt;height:4pt;border-radius:99pt;'
            f'background:{section_colors(k)[0]}"></div>'
            f'<div style="flex:1;font-size:10pt;font-weight:600">{n}</div>'
            f'<div style="color:var(--soft);font-size:11pt">&rsaquo;</div></a>'
            for i, (k, n) in enumerate(links))
        # the group's own colour, so the header bar, the row dots and the tab
        # rail all say the same thing
        cards.append(f'<div class="card" style="flex:{len(links)};'
                     f'--accent:{section_colors(links[0][0])[0]}">'
                     f'<div class="label">{title}</div>{rows}</div>')
    return (head("Index", "Where to?", "Use the side tabs, or pick from here")
            + f'<div class="body">{"".join(cards)}</div>')


def mini_month(m):
    weeks = calendar.Calendar(firstweekday=0).monthdayscalendar(YEAR, m)
    th = "".join(f'<th class="{"we" if i >= 5 else ""}">{d}</th>'
                 for i, d in enumerate("MTWTFSS"))
    rows = "".join(
        "<tr>" + "".join(f'<td class="{"we" if i >= 5 else ""}">{d or ""}</td>'
                         for i, d in enumerate(w)) + "</tr>" for w in weeks)
    return (f'<div><div style="font-size:8pt;font-weight:700;'
            f'margin-bottom:5pt">{calendar.month_name[m]}</div>'
            f'<table class="mini"><tr>{th}</tr>{rows}</table></div>')


def p_year():
    months = "".join(mini_month(m) for m in range(1, 13))
    return (head("Year at a glance", str(YEAR))
            + f"""<div class="body">
      <div class="card" style="flex:none;padding:18pt">
        <div style="display:grid;grid-template-columns:repeat(4,1fr);
             gap:22pt 14pt">{months}</div>
      </div>
      <div class="card" style="flex:1">
        <div class="label">Three things that matter this year</div>
        <div style="flex:1;display:flex;flex-direction:column;gap:12pt">
          {''.join('<div style="display:flex;align-items:stretch;gap:10pt;flex:1">'
                   '<div class="box" style="margin-top:10pt"></div>'
                   '<div class="field" style="flex:1;height:auto"></div></div>'
                   for _ in range(3))}
        </div>
      </div></div>""")


def p_month():
    weeks = calendar.Calendar(firstweekday=0).monthdayscalendar(YEAR, 1)
    th = "".join(f'<th class="{"we" if i >= 5 else ""}">{d}</th>' for i, d in
                 enumerate(["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]))
    rows = "".join(
        "<tr>" + "".join(f'<td class="{"we" if i >= 5 else ""}">{d or ""}</td>'
                         for i, d in enumerate(w)) + "</tr>" for w in weeks)
    return (head("Monthly overview", f"January {YEAR}")
            + f"""<div class="body">
      <div class="card" style="flex:1;padding:16pt 18pt">
        <table class="cal"><tr>{th}</tr>{rows}</table></div>
      <div class="card" style="flex:none;flex-direction:row;align-items:center;gap:14pt">
        <div class="label" style="margin:0;white-space:nowrap">This month's focus</div>
        <div class="field" style="flex:1"></div></div></div>""")


def p_week():
    days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    rows = "".join(
        f'<div style="flex:1;display:flex;align-items:flex-start;padding-top:8pt;'
        f'{"" if i == 6 else "border-bottom:1px solid var(--line)"}">'
        f'<span class="chip" style="{"" if i < 5 else "background:var(--field);color:var(--mid)"}">{d}</span>'
        f'</div>' for i, d in enumerate(days))
    return (head("Weekly spread", "Week of", field_after=True)
            + f"""<div class="body"><div class="row">
      <div class="card" style="flex:1.45">{rows}</div>
      <div class="col" style="flex:1">
        <div class="card" style="flex:1.6">
          <div class="label">Brain dump</div>{lines(8)}</div>
        <div class="card" style="flex:1">
          <div class="label">Top 3 priorities</div>
          <div style="flex:1;display:flex;flex-direction:column;
               justify-content:space-around">{checkrow() * 3}</div></div>
        <div class="card" style="flex:none">
          <div class="label">Energy</div>
          <div style="display:flex;justify-content:space-between;padding:0 4pt">
            {'<div class="box" style="width:14pt;height:14pt"></div>' * 5}</div>
          <div style="display:flex;justify-content:space-between;font-size:7pt;
               color:var(--soft);margin-top:6pt;padding:0 2pt">
            <span>low</span><span>high</span></div></div>
      </div></div></div>""")


def p_day():
    hours = ["7 AM", "9 AM", "11 AM", "1 PM", "3 PM", "5 PM", "7 PM", "9 PM"]
    blocks = "".join(
        f'<div style="flex:1;display:flex;align-items:center;'
        f'{"" if i == len(hours) - 1 else "border-bottom:1px solid var(--line)"}">'
        f'<span style="font-size:7.5pt;font-weight:700;color:var(--soft);'
        f'width:34pt">{h}</span></div>' for i, h in enumerate(hours))
    mood = "".join(
        f'<div><div class="box" style="width:14pt;height:14pt;margin:0 auto"></div>'
        f'<div style="font-size:7pt;color:var(--soft);margin-top:5pt">{m}</div></div>'
        for m in ["Low", "OK", "Good", "Great"])
    return (head("Daily page", "Today", field_after=True)
            + f"""<div class="body">
      <div class="card" style="flex:none;flex-direction:row;align-items:center;
           gap:14pt;padding:13pt 16pt">
        <div class="label" style="margin:0;white-space:nowrap">Just one thing today</div>
        <div class="field" style="flex:1"></div></div>
      <div class="row">
        <div class="card" style="flex:1.3">{blocks}</div>
        <div class="col" style="flex:1">
          <div class="card" style="flex:none">
            <div class="label">Meds / water</div>
            <div style="display:flex;align-items:center;gap:8pt;margin-bottom:11pt">
              <span style="font-size:7.5pt;color:var(--soft);width:30pt">Meds</span>
              {'<div class="box" style="width:13pt;height:13pt"></div>' * 2}</div>
            <div style="display:flex;align-items:center;gap:5pt">
              <span style="font-size:7.5pt;color:var(--soft);width:30pt">Water</span>
              {'<div class="box" style="width:11pt;height:11pt"></div>' * 8}</div></div>
          <div class="card" style="flex:none">
            <div class="label">Mood</div>
            <div style="display:flex;justify-content:space-between;text-align:center">
              {mood}</div></div>
          <div class="card" style="flex:1">
            <div class="label">Brain dump</div>{lines(8)}</div>
        </div></div></div>""")


def p_tasks():
    chunks = "".join(
        f'<div style="display:flex;align-items:center;gap:9pt">'
        f'<span style="font-size:8pt;color:var(--soft);width:12pt;font-weight:700">{i}</span>'
        f'<div class="box"></div><div class="field" style="flex:1"></div></div>'
        for i in range(1, 9))
    quads = [
        f'<div style="background:var(--field);border-radius:7pt;padding:10pt;flex:1">'
        f'<div style="font-size:7.5pt;font-weight:700;color:{c}">{t}</div></div>'
        for t, c in [("Now &middot; Important", "var(--accent-text)"),
                     ("Later &middot; Important", "var(--mid)"),
                     ("Now &middot; Less important", "var(--mid)"),
                     ("Doesn't need doing", "var(--soft)")]]
    return (head("Task breakdown", "Make it smaller", "One piece at a time")
            + f"""<div class="body">
      <div class="card" style="flex:none;flex-direction:row;align-items:center;gap:14pt">
        <div class="label" style="margin:0;white-space:nowrap">The big thing</div>
        <div class="field" style="flex:1"></div></div>
      <div class="row">
        <div class="card" style="flex:1.25">
          <div class="label">Broken into pieces</div>
          <div style="flex:1;display:flex;flex-direction:column;
               justify-content:space-around">{chunks}</div></div>
        <div class="col" style="flex:1">
          <div class="card" style="flex:1.6">
            <div class="label">Sort it out</div>
            <div style="flex:1;display:flex;flex-direction:column;gap:8pt">
              <div style="display:flex;gap:8pt;flex:1">{quads[0]}{quads[1]}</div>
              <div style="display:flex;gap:8pt;flex:1">{quads[2]}{quads[3]}</div>
            </div></div>
          <div class="card" style="flex:1">
            <div class="label">The first five minutes</div>
            <div style="font-size:8pt;color:var(--soft);margin-bottom:8pt">
              Just start. You don't have to finish.</div>
            <div class="field" style="flex:1;height:auto"></div></div>
        </div></div></div>""")


def tracker(names, blanks=0):
    dh = "".join(f'<td class="dh {"we" if (d % 7) in (6, 0) else ""}">{d}</td>'
                 for d in range(1, 32))
    body = "".join(f'<tr><td class="nm">{n}</td>' + "<td></td>" * 31 + "</tr>"
                   for n in names)
    body += "".join('<tr><td class="nm">&nbsp;</td>' + "<td></td>" * 31 + "</tr>"
                    for _ in range(blanks))
    return f'<table class="trk"><tr><td class="nm"></td>{dh}</tr>{body}</table>'


def p_habits():
    names = ["Water", "Meds", "Movement", "Sleep 7h+", "Journal",
             "Tidy 10 min", "Outside", "Screen cutoff"]
    return (head("Habit tracker", f"January {YEAR}")
            + f"""<div class="body">
      <div class="card" style="flex:2.2;padding:16pt 18pt">{tracker(names, 2)}</div>
      <div class="row" style="flex:1">
        <div class="card" style="flex:1"><div class="label">What worked</div>{lines(5)}</div>
        <div class="card" style="flex:1"><div class="label">What to change</div>{lines(5)}</div>
      </div></div>""")


def p_meds():
    return (head("Medication log", f"January {YEAR}", "Track the dose and how it felt")
            + f"""<div class="body">
      <div class="card" style="flex:2;padding:16pt 18pt">{tracker([], 9)}</div>
      <div class="card" style="flex:1">
        <div class="label">Side effects &middot; how you felt</div>{lines(6)}</div>
      </div>""")


def p_notes():
    return (head("Notes", "Blank space")
            + '<div class="body"><div class="card dots" style="flex:1"></div></div>')


# ------------------------------------------------------------------ build --
def font_url():
    fams = [f"family={T['font']}:wght@{T['weights']}"]
    if T["display"]:
        fams.append(f"family={T['display']}:wght@600;700")
    return "https://fonts.googleapis.com/css2?" + "&".join(fams) + "&display=swap"


def build_bloom_assets():
    """Bake the two bloom positions once per theme."""
    if not T.get("photo"):
        return
    d = os.path.join(ROOT, "assets")
    os.makedirs(d, exist_ok=True)
    bloom_png(os.path.join(d, f"bloom_cover_{VERSION}.png"), 306, 250, scale=0.5)
    bloom_png(os.path.join(d, f"bloom_page_{VERSION}.png"), 330, 92, scale=0.5)


def build_html():
    pages = [page(k, fn()) for k, fn in [
        ("cover", p_cover), ("index", p_index), ("year", p_year),
        ("month", p_month), ("week", p_week), ("day", p_day),
        ("tasks", p_tasks), ("habits", p_habits), ("meds", p_meds),
        ("notes", p_notes),
    ]]
    font_url_v = font_url()
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>{YEAR} ADHD &amp; Wellness Planner</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{font_url_v}" rel="stylesheet">
<style>{CSS}</style></head>
<body>{"".join(pages)}</body></html>"""
    os.makedirs(os.path.dirname(SRC), exist_ok=True)
    with open(SRC, "w", encoding="utf-8") as f:
        f.write(html)
    return SRC


def to_pdf():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    before = os.path.getmtime(OUT) if os.path.exists(OUT) else 0

    # A dedicated profile dir is required: with the default one, a Chrome the
    # user already has open holds the lock, and the headless call exits 0
    # without ever writing the PDF.
    profile = os.path.join(tempfile.gettempdir(), "planner-chrome-profile")
    r = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", f"--user-data-dir={profile}",
         "--no-pdf-header-footer", f"--print-to-pdf={OUT}",
         "file:///" + SRC.replace("\\", "/")],
        capture_output=True, text=True, encoding="utf-8", errors="replace")

    if not os.path.exists(OUT) or os.path.getmtime(OUT) <= before:
        raise RuntimeError(
            "Chrome exited without writing a new PDF.\n"
            f"returncode={r.returncode}\nstdout={r.stdout}\nstderr={r.stderr}")
    return OUT


if __name__ == "__main__":
    build_bloom_assets()
    build_html()
    to_pdf()
    print("Saved:", OUT)
