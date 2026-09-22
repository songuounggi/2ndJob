# -*- coding: utf-8 -*-
"""Generate Etsy listing images from the rendered planner pages.

Etsy shows listing images as squares, so everything is composed at
2000x2000 and shot with headless Chrome. Source art is the page PNGs the
build already produces in output/preview/.
"""

import os
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREVIEW = os.path.join(ROOT, "output", "preview")
OUT = os.path.join(ROOT, "output", "listing")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SIZE = 2000

CSS = """
*{box-sizing:border-box;margin:0;padding:0;-webkit-print-color-adjust:exact}
body{width:2000px;height:2000px;font-family:'Nunito',system-ui,sans-serif;
     background:#FBF8F3;color:#3A3A3A;overflow:hidden}
.wrap{width:100%;height:100%;padding:110px;display:flex;flex-direction:column}
.kicker{display:inline-block;background:#EAF2F8;color:#3E6E93;font-size:30px;
        font-weight:800;letter-spacing:.06em;padding:12px 30px;border-radius:99px;
        align-self:flex-start}
h1{font-size:104px;font-weight:800;line-height:1.1;margin-top:38px;
   letter-spacing:-.02em}
.sub{font-size:40px;color:#6E6A64;margin-top:26px;line-height:1.45}
.grow{flex:1;display:flex;align-items:center;justify-content:center;min-height:0}
.foot{font-size:30px;color:#A8A39B;text-align:center;margin-top:30px}

/* a plain device frame -- no photo, just a clean bezel */
.tab{background:#2B2A33;border-radius:56px;padding:26px;
     box-shadow:0 40px 90px rgba(0,0,0,.18)}
.tab img{display:block;border-radius:30px;height:1180px;width:auto}

.grid{display:grid;gap:26px;width:100%;justify-items:center}
.grid img{height:var(--cell,430px);width:auto;border-radius:14px;
          box-shadow:0 14px 34px rgba(0,0,0,.10);display:block}

.row{display:flex;gap:34px;align-items:center}
.chip{background:#FFF;border-radius:26px;padding:34px 40px;flex:1;
      box-shadow:0 14px 34px rgba(0,0,0,.08)}
.chip b{display:block;font-size:44px;font-weight:800}
.chip span{display:block;font-size:28px;color:#827D75;margin-top:10px}
.big{font-size:150px;font-weight:800;color:#3E6E93;line-height:1}
"""


def html(body, extra=""):
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap"
      rel="stylesheet"><style>{CSS}{extra}</style></head><body>{body}</body></html>"""


def img(n):
    return "file:///" + os.path.join(PREVIEW, f"v8_p{n}.png").replace("\\", "/")


def shoot(name, body, extra=""):
    os.makedirs(OUT, exist_ok=True)
    src = os.path.join(tempfile.gettempdir(), f"mock_{name}.html")
    with open(src, "w", encoding="utf-8") as f:
        f.write(html(body, extra))
    dest = os.path.join(OUT, f"{name}.png")
    before = os.path.getmtime(dest) if os.path.exists(dest) else 0
    profile = os.path.join(tempfile.gettempdir(), "mockup-chrome-profile")
    r = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", f"--user-data-dir={profile}",
         "--hide-scrollbars", f"--window-size={SIZE},{SIZE}",
         "--virtual-time-budget=4000",
         f"--screenshot={dest}", "file:///" + src.replace("\\", "/")],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    if not os.path.exists(dest) or os.path.getmtime(dest) <= before:
        raise RuntimeError(f"Chrome wrote nothing for {name}\n{r.stderr[-400:]}")
    return dest


# ------------------------------------------------------------------ shots --
# Etsy crops the square listing image to a narrower box for the search grid,
# taking roughly 140px off each side of a 2000px image. The first hero had
# left-aligned text starting at x=112, so the grid thumbnail read
# "DHD & Wellness / igital Planner" -- the first letter of every line was
# eaten. Keep everything that must survive inside SAFE on both sides.
SAFE = 260

HERO_CSS = """
.hero{width:100%;height:100%;padding:96px SAFEpx;display:flex;
      flex-direction:column;align-items:center;text-align:center}
/* the shared .kicker pins itself left; override it or it sits off-axis
   while everything else is centred */
.hero .kicker{align-self:center}
.hero h1{font-size:112px;font-weight:800;line-height:1.06;margin-top:30px;
         letter-spacing:-.025em}
.hero .sub{font-size:42px;color:#6E6A64;margin-top:22px;line-height:1.35}
.hero .stats{display:flex;gap:16px;margin-top:30px;flex-wrap:wrap;
             justify-content:center}
.hero .stats b{background:#FFF;border-radius:99px;padding:14px 30px;
               font-size:30px;font-weight:800;color:#3E6E93;
               box-shadow:0 8px 22px rgba(0,0,0,.07)}
/* two devices, the back one peeking out so the inside is visible at
   thumbnail size -- a single centred tablet read as empty next to the
   competition, which all show three or four screens */
.hero .stage{flex:1;display:flex;align-items:center;justify-content:center;
             min-height:0;position:relative;margin-top:16px}
.hero .stage .tab{position:absolute}
.hero .stage .back{transform:translateX(188px) scale(.87);z-index:1;
                   opacity:.97}
.hero .stage .front{transform:translateX(-150px);z-index:2}
.hero .stage img{height:960px}
""".replace("SAFEpx", f"{SAFE}px")


def hero():
    body = f"""<div class="hero">
      <span class="kicker">UNDATED &middot; NO-GUILT</span>
      <h1>ADHD &amp; Wellness<br>Digital Planner</h1>
      <div class="sub">Start any day. Skip a week. Nothing to catch up on.</div>
      <div class="stats"><b>494 pages</b><b>58 unique</b><b>10 tabs</b></div>
      <div class="stage">
        <div class="tab back"><img src="{img(60)}"></div>
        <div class="tab front"><img src="{img(1)}"></div>
      </div>
    </div>"""
    return shoot("01_hero", body, HERO_CSS)


# Eight thumbnails at 440px were eight pale rectangles -- the claim "58
# genuinely different pages" was argued with evidence nobody could read.
# Four, bigger, chosen because their STRUCTURE differs at a glance: a
# radial map, a dense 31-column grid, a calendar, a row of rating scales.
# Text is not legible at this size and does not need to be -- 10_closeup
# does that job.
TMPL_CSS = """
.tm{width:100%;height:100%;padding:88px 92px;display:flex;
    flex-direction:column;align-items:center;text-align:center}
.tm .kicker{align-self:center}
.tm h1{font-size:100px;font-weight:800;line-height:1.06;margin-top:26px;
       letter-spacing:-.025em}
.tm h1 em{font-style:normal;color:#3E6E93}
.tm .sub{font-size:34px;color:#6E6A64;margin-top:16px}
.tm .grid{flex:1;min-height:0;margin-top:34px;display:grid;
          grid-template-columns:1fr 1fr;gap:30px 44px;align-content:center;
          justify-items:center}
.tm .cell{display:flex;flex-direction:column;align-items:center;gap:12px}
.tm .cell img{height:var(--cell,560px);width:auto;border-radius:12px;
              box-shadow:0 12px 30px rgba(0,0,0,.11);display:block}
.tm .cell b{font-size:29px;font-weight:800;color:#3A3A3A}
"""

TMPL_PICKS = [
    (17, "Mind map"),
    (35, "31-day habit tracker"),
    (58, "Monthly grid"),
    (48, "Wheel of life"),
]


def templates():
    cells = "".join(
        f'<div class="cell"><img src="{img(n)}"><b>{label}</b></div>'
        for n, label in TMPL_PICKS)
    body = f"""<div class="tm">
      <span class="kicker">WHAT'S INSIDE</span>
      <h1><em>58</em> pages that are<br>actually different</h1>
      <div class="sub">Not one page copied three hundred times.</div>
      <div class="grid">{cells}</div>
    </div>"""
    return shoot("02_templates", body, TMPL_CSS)


# The old version showed two whole tablets. The subject -- ten tabs -- was
# a sliver a few pixels wide on each one, so the image argued for navigation
# while making navigation invisible. This pairs the real rail (proof it is
# in the file) with the ten names at a size that reads at 440px.
NAV_CSS = """
.nav{width:100%;height:100%;padding:90px 96px;display:flex;
     flex-direction:column}
.nav .kicker{align-self:flex-start}
.nav h1{font-size:96px;font-weight:800;line-height:1.06;margin-top:26px;
        letter-spacing:-.025em}
.nav .sub{font-size:34px;color:#6E6A64;margin-top:16px;line-height:1.35}
.nav .body{flex:1;min-height:0;display:flex;gap:56px;margin-top:38px;
           align-items:stretch}
.nav .rail{flex:none;width:250px;border-radius:20px;overflow:hidden;
           background:#F7F4EE;box-shadow:0 14px 34px rgba(0,0,0,.10);
           position:relative}
.nav .rail img{position:absolute;top:50%;left:50%;
               transform:translate(-50%,-50%);width:100%;display:block}
/* the strip is far taller than the frame, so it has to be cut. Fade both
   ends or the cut reads as a mistake rather than "it continues". */
.nav .rail::before,.nav .rail::after{content:"";position:absolute;left:0;
    right:0;height:120px;z-index:2;pointer-events:none}
.nav .rail::before{top:0;background:linear-gradient(#F7F4EE,rgba(247,244,238,0))}
.nav .rail::after{bottom:0;background:linear-gradient(rgba(247,244,238,0),#F7F4EE)}
.nav .list{flex:1;display:flex;flex-direction:column;justify-content:center;
           gap:5px}
.nav .t{display:flex;align-items:baseline;gap:18px;padding:11px 0;
        border-bottom:1px solid #EFEAE1}
.nav .t:last-child{border-bottom:0}
.nav .t i{width:16px;height:16px;border-radius:99px;flex:none;
          align-self:center}
.nav .t b{font-size:34px;font-weight:800;letter-spacing:.04em;
          width:210px;flex:none}
.nav .t span{font-size:29px;color:#827D75}
"""

TABS_10 = [
    ("INDEX", "#7FA8C9", "everything, one tap away"),
    ("YEAR", "#7FA8C9", "quarterly, goals, vision"),
    ("MONTH", "#7FA8C9", "twelve grids, 372 days"),
    ("WEEK", "#7FA8C9", "fifty-two spreads"),
    ("FOCUS", "#E08A73", "when starting is the hard part"),
    ("FEELINGS", "#7FA37C", "the loop, the sting, the critic"),
    ("HABITS", "#7FA37C", "31-day tracker, routines"),
    ("HEALTH", "#7FA37C", "meds, sleep, symptoms"),
    ("LIFE", "#D9A441", "meals, money, the admin"),
    ("NOTES", "#D9A441", "dot grid"),
]


def navigation():
    rail = "file:///" + os.path.join(
        PREVIEW, "rail_strip.png").replace("\\", "/")
    rows = "".join(
        f'<div class="t"><i style="background:{c}"></i><b>{n}</b>'
        f'<span>{d}</span></div>' for n, c, d in TABS_10)
    body = f"""<div class="nav">
      <span class="kicker">NEVER LOSE YOUR PLACE</span>
      <h1>Ten tabs, down<br>every single page</h1>
      <div class="sub">All 494 of them. The most common complaint about big
        planners is not being able to find anything.</div>
      <div class="body">
        <div class="rail"><img src="{rail}"></div>
        <div class="list">{rows}</div>
      </div>
    </div>"""
    return shoot("03_navigation", body, NAV_CSS)


# 04/05/06 used to be three 3x2 grids of six pages each. At 440px they were
# three near-identical walls of pale rectangles -- a buyer scrolling the
# gallery saw the same image three times. Now each shows THREE pages with
# the tool's name under it, so the three images differ by their words even
# when the art reads small.
TOOLS_CSS = """
.tl{width:100%;height:100%;padding:88px 92px;display:flex;
    flex-direction:column}
.tl .kicker{align-self:flex-start}
.tl h1{font-size:100px;font-weight:800;line-height:1.06;margin-top:26px;
       letter-spacing:-.025em}
.tl .sub{font-size:34px;color:#6E6A64;margin-top:16px;line-height:1.35}
.tl .row{flex:1;min-height:0;margin-top:40px;display:flex;gap:34px;
         align-items:center;justify-content:center}
.tl .cell{display:flex;flex-direction:column;align-items:center;gap:14px;
          flex:1}
/* three cells across 1824px of content: 560px each after the gaps, so a
   page at aspect 0.773 can be at most ~724px tall. 880 overflowed and the
   outer two got clipped. */
.tl .cell img{height:var(--cell,712px);width:auto;border-radius:12px;
              box-shadow:0 14px 34px rgba(0,0,0,.11);display:block}
.tl .cell b{font-size:31px;font-weight:800;color:#3A3A3A;text-align:center}
.tl .cell span{font-size:26px;color:#827D75;text-align:center;
               line-height:1.3;margin-top:-6px}
"""


def tools(name, kicker, title, sub, picks):
    """picks: [(page, label, note), ...] -- three of them."""
    cells = "".join(
        f'<div class="cell"><img src="{img(n)}"><b>{lab}</b>'
        f'<span>{note}</span></div>' for n, lab, note in picks)
    body = f"""<div class="tl">
      <span class="kicker">{kicker}</span>
      <h1>{title}</h1>
      <div class="sub">{sub}</div>
      <div class="row">{cells}</div>
    </div>"""
    return shoot(name, body, TOOLS_CSS)


def everyday():
    body = f"""<div class="wrap">
      <span class="kicker">THE PAGES YOU OPEN EVERY DAY</span>
      <h1>424 daily &amp; weekly pages</h1>
      <div class="sub">A timed day from 7am, meds and water, a mood row.
        Weeks start on Monday.</div>
      <div class="grow" style="gap:50px">
        <div class="tab"><img src="{img(60)}"></div>
        <div class="tab"><img src="{img(444)}"></div>
      </div>
    </div>"""
    return shoot("09_everyday", body)


# At the size Etsy actually shows these (440x440 on the listing page) a
# grid of six page thumbnails is six pale rectangles -- the buyer cannot
# read a single word of the product whose whole value is what the pages
# say. This one shows ONE page big enough to read, cropped to the part
# that carries the idea.
CLOSEUP_CSS = """
.close{width:100%;height:100%;padding:86px 90px;display:flex;
       flex-direction:column;align-items:center;text-align:center}
.close .kicker{align-self:center}
.close h1{font-size:92px;font-weight:800;line-height:1.08;margin-top:26px;
          letter-spacing:-.025em}
.close .sub{font-size:36px;color:#6E6A64;margin-top:18px;line-height:1.35}
.close .frame{flex:1;min-height:0;margin-top:34px;width:100%;
              border-radius:26px;overflow:hidden;background:#FFF;
              box-shadow:0 22px 54px rgba(0,0,0,.13);position:relative}
.close .frame img{position:absolute;left:50%;top:var(--top,-8%);
                  transform:translateX(-50%);width:var(--w,150%);
                  max-width:none;display:block}
"""


def closeup():
    """A readable crop of Guess vs actual -- the page that names the problem
    ADHD buyers search for (time blindness) in words they recognise."""
    src = "file:///" + os.path.join(
        PREVIEW, "big_p20.png").replace("\\", "/")
    body = f"""<div class="close">
      <span class="kicker">INSIDE ONE PAGE</span>
      <h1>Guess first.<br>Then check.</h1>
      <div class="sub">You thought it would take an hour. It took three.
        Do that ten times and you know your multiplier.</div>
      <div class="frame" style="--w:132%;--top:-4%">
        <img src="{src}">
      </div>
    </div>"""
    return shoot("10_closeup", body, CLOSEUP_CSS)


def numbers():
    stats = [("58", "unique page designs", "not one page copied 300 times"),
             ("494", "pages in total", "12 months, 52 weeks, 372 days"),
             ("493", "linked pages", "every page is a tap away"),
             ("0", "dates printed", "start on any day of any year")]
    cells = "".join(
        f'<div class="chip" style="display:flex;flex-direction:column;'
        f'justify-content:center;padding:56px 60px"><div class="big">{n}</div>'
        f'<span style="font-size:38px;color:#3A3A3A;font-weight:700;'
        f'margin-top:18px">{l}</span>'
        f'<span style="font-size:28px;margin-top:8px">{d}</span></div>'
        for n, l, d in stats)
    body = f"""<div class="wrap">
      <span class="kicker">AT A GLANCE</span>
      <h1>Built to be used,<br>not admired</h1>
      <div class="grow"><div style="display:grid;width:100%;
           grid-template-columns:1fr 1fr;grid-auto-rows:520px;gap:34px">{cells}</div></div>
      <div class="foot">Works in GoodNotes, Notability, Noteful, Xodo &middot;
        iPad, Android tablet, or print at home</div>
    </div>"""
    return shoot("07_numbers", body)


# Three thin rows left the bottom half of the square empty. The steps now
# sit beside a device so the image carries a picture as well as words, and
# the apps are named as chips -- "does it work in MY app" is the question
# this image exists to answer.
HOWTO_CSS = """
.hw{width:100%;height:100%;padding:90px 96px;display:flex;
    flex-direction:column}
.hw .kicker{align-self:flex-start}
.hw h1{font-size:100px;font-weight:800;line-height:1.06;margin-top:26px;
       letter-spacing:-.025em}
.hw .sub{font-size:34px;color:#6E6A64;margin-top:16px;line-height:1.35}
.hw .body{flex:1;min-height:0;display:flex;gap:56px;margin-top:40px;
          align-items:center}
.hw .steps{flex:1;display:flex;flex-direction:column;gap:26px}
.hw .st{display:flex;gap:22px;align-items:flex-start}
.hw .st i{width:60px;height:60px;border-radius:99px;background:#EAF2F8;
          color:#3E6E93;font-size:32px;font-weight:800;flex:none;
          display:flex;align-items:center;justify-content:center}
.hw .st b{font-size:38px;font-weight:800;display:block;line-height:1.2}
.hw .st span{font-size:29px;color:#827D75;display:block;margin-top:6px;
             line-height:1.3}
.hw .apps{display:flex;flex-wrap:wrap;gap:12px;margin-top:8px;
          margin-left:82px}
.hw .apps u{text-decoration:none;background:#FFF;border-radius:99px;
            padding:11px 24px;font-size:26px;font-weight:700;color:#6E6A64;
            box-shadow:0 6px 18px rgba(0,0,0,.06)}
.hw .shot{flex:none}
.hw .shot .tab{background:#2B2A33;border-radius:44px;padding:20px;
               box-shadow:0 30px 70px rgba(0,0,0,.18)}
.hw .shot img{display:block;border-radius:26px;height:1010px;width:auto}
.hw .foot{font-size:30px;color:#A8A39B;text-align:center;margin-top:34px}
"""


def howto():
    steps = [("1", "Buy and download",
              "One PDF, instantly. Nothing is shipped to you."),
             ("2", "Open it in your note app", None),
             ("3", "Write on it with a stylus",
              "Tap the side tabs to move around, or print the pages you want.")]
    apps = ["GoodNotes", "Notability", "Noteful", "Xodo", "Acrobat"]
    rows = ""
    for n, t, d in steps:
        rows += f'<div class="st"><i>{n}</i><div><b>{t}</b>'
        rows += f'<span>{d}</span>' if d else ""
        rows += "</div></div>"
        if n == "2":
            rows += ('<div class="apps">'
                     + "".join(f"<u>{a}</u>" for a in apps) + "</div>")
    body = f"""<div class="hw">
      <span class="kicker">HOW IT WORKS</span>
      <h1>No app to install</h1>
      <div class="sub">It is a hyperlinked PDF. It opens in the note app
        you already use.</div>
      <div class="body">
        <div class="steps">{rows}</div>
        <div class="shot"><div class="tab"><img src="{img(2)}"></div></div>
      </div>
      <div class="foot">iPad &middot; Android tablet &middot; Windows
        &middot; or print it at home</div>
    </div>"""
    return shoot("08_howto", body, HOWTO_CSS)


if __name__ == "__main__":
    made = [
        hero(), templates(), navigation(),
        tools("04_focus", "WHEN STARTING IS HARD", "Focus tools",
              "Break it down, guess the time, name what is stopping you.",
              [(12, "Make it smaller", "one piece at a time"),
               (20, "Guess vs actual", "time blindness, measured"),
               (21, "Why I am avoiding it", "six reasons, tick one")]),
        tools("05_feelings", "FOR THE HEAVIER DAYS", "Feelings tools",
              "Rejection sensitivity, the worry loop, the inner critic.",
              [(26, "Rejection sensitivity", "when a small thing lands big"),
               (25, "Cycle of worry", "break the loop"),
               (27, "Talk to yourself kindly", "answer the critic on paper")]),
        tools("06_life", "THE ADMIN THAT EATS THE WEEK", "Health &amp; life",
              "Medication, sleep, money, the things that slip.",
              [(38, "Medication log", "dose, and how it felt"),
               (50, "Monthly budget", "in, out, what is left"),
               (51, "Before you buy it", "the ten-minute check")]),
        everyday(), closeup(), numbers(), howto(),
    ]
    for m in made:
        print("saved", os.path.basename(m))
