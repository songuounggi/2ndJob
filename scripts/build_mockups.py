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
def hero():
    body = f"""<div class="wrap">
      <span class="kicker">UNDATED &middot; NO-GUILT</span>
      <h1>ADHD &amp; Wellness<br>Digital Planner</h1>
      <div class="sub">Start any day. Skip a week.<br>Nothing to catch up on.</div>
      <div class="grow"><div class="tab"><img src="{img(1)}"></div></div>
    </div>"""
    return shoot("01_hero", body)


def templates():
    pages = [12, 16, 20, 25, 28, 35, 38, 50]
    cells = "".join(f'<img src="{img(n)}">' for n in pages)
    body = f"""<div class="wrap">
      <span class="kicker">WHAT'S INSIDE</span>
      <h1>58 unique pages</h1>
      <div class="sub">Not the same page copied 300 times.</div>
      <div class="grow"><div class="grid"
           style="grid-template-columns:repeat(4,1fr);--cell:545px">{cells}</div></div>
    </div>"""
    return shoot("02_templates", body)


def navigation():
    body = f"""<div class="wrap">
      <span class="kicker">NEVER LOSE YOUR PLACE</span>
      <h1>Tabs on every page</h1>
      <div class="sub">The most common complaint about big planners is
        not being able to find anything. This one is built around that.</div>
      <div class="grow" style="gap:50px">
        <div class="tab"><img src="{img(2)}"></div>
        <div class="tab"><img src="{img(58)}"></div>
      </div>
    </div>"""
    return shoot("03_navigation", body)


def tools(name, kicker, title, sub, pages):
    cells = "".join(f'<img src="{img(n)}">' for n in pages)
    body = f"""<div class="wrap">
      <span class="kicker">{kicker}</span>
      <h1>{title}</h1>
      <div class="sub">{sub}</div>
      <div class="grow"><div class="grid"
           style="grid-template-columns:repeat(3,1fr);--cell:700px">{cells}</div></div>
    </div>"""
    return shoot(name, body)


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


def howto():
    steps = [("1", "Buy &amp; download", "One PDF, instantly"),
             ("2", "Open in your app", "GoodNotes, Notability, Xodo&hellip;"),
             ("3", "Write with a stylus", "Tap the side tabs to move around")]
    cells = "".join(
        f'<div class="chip"><b>{n}. {t}</b><span>{d}</span></div>'
        for n, t, d in steps)
    body = f"""<div class="wrap">
      <span class="kicker">HOW IT WORKS</span>
      <h1>No app to install</h1>
      <div class="sub">It is a hyperlinked PDF. It opens in the note app
        you already use.</div>
      <div class="grow"><div style="display:flex;flex-direction:column;
           gap:34px;width:100%">{cells}</div></div>
      <div class="foot">Digital download &middot; nothing is posted to you</div>
    </div>"""
    return shoot("08_howto", body)


if __name__ == "__main__":
    made = [
        hero(), templates(), navigation(),
        tools("04_focus", "WHEN STARTING IS HARD", "Focus tools",
              "Break it down, dump it out, work backwards from the date.",
              [12, 13, 14, 16, 20, 21]),
        tools("05_feelings", "FOR THE HEAVIER DAYS", "Feelings tools",
              "Rejection sensitivity, the worry loop, the inner critic.",
              [24, 25, 26, 27, 28, 31]),
        tools("06_life", "THE ADMIN THAT EATS THE WEEK", "Health &amp; life",
              "Medication, sleep, meals, money, the things that slip.",
              [38, 39, 47, 50, 51, 54]),
        everyday(), numbers(), howto(),
    ]
    for m in made:
        print("saved", os.path.basename(m))
