# -*- coding: utf-8 -*-
"""Pinterest pins for the ADHD planner listing.

Separate from build_mockups.py on purpose. Etsy wants 2000x2000 squares;
Pinterest ranks 2:3 verticals and buries squares, so the two sets do not
share a canvas. Same source art (output/preview/v8_p*.png), same Chrome
--screenshot approach.

A pin is read at thumbnail size in a scrolling feed, so each one carries a
single hook in large type. The link to the Etsy listing is set in Pinterest,
not in the image -- the image only has to earn the click.

    python scripts/build_pinterest.py
"""

import os
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREVIEW = os.path.join(ROOT, "output", "preview")
# 9/22 에 뽑은 핀(494/58 기준)은 output/pinterest/ 에 그대로 둔다.
OUT = os.path.join(ROOT, "output", "pinterest_v815")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

W, H = 1000, 1500          # Pinterest's recommended 2:3

CSS = """
*{box-sizing:border-box;margin:0;padding:0;-webkit-print-color-adjust:exact}
body{width:1000px;height:1500px;font-family:'Nunito',system-ui,sans-serif;
     background:#FBF8F3;color:#3A3A3A;overflow:hidden}
.wrap{width:100%;height:100%;padding:64px 56px;display:flex;
      flex-direction:column;text-align:center}

.kicker{display:inline-block;background:#EAF2F8;color:#3E6E93;font-size:21px;
        font-weight:800;letter-spacing:.08em;padding:10px 24px;border-radius:99px;
        align-self:center}
h1{font-size:76px;font-weight:800;line-height:1.08;margin-top:26px;
   letter-spacing:-.02em}
h1 em{font-style:normal;color:#3E6E93}
.sub{font-size:31px;color:#6E6A64;margin-top:20px;line-height:1.4}

.grow{flex:1;display:flex;align-items:center;justify-content:center;
      min-height:0;margin-top:34px}

/* a plain bezel -- no photo, the page art is the point */
.tab{background:#2B2A33;border-radius:38px;padding:18px;
     box-shadow:0 26px 60px rgba(0,0,0,.17)}
.tab img{display:block;border-radius:22px;height:var(--h,700px);width:auto}

.duo{display:flex;gap:26px;align-items:center}
.duo .tab img{height:560px}

/* constrain the cells by HEIGHT. Sizing them by width blew three rows of
   1224x1584 renders past the canvas and over the heading. */
.grid{display:grid;gap:16px;justify-content:center;align-content:center}
.grid img{height:var(--cell,300px);width:auto;border-radius:11px;
          box-shadow:0 10px 26px rgba(0,0,0,.10);display:block}

.list{text-align:left;width:100%;display:flex;flex-direction:column;gap:20px}
.row{display:flex;gap:16px;align-items:flex-start}
.row i{width:11px;height:11px;border-radius:99px;background:#E08A73;
       flex:none;margin-top:13px}
.row b{font-size:32px;font-weight:800;display:block;line-height:1.25}
.row span{font-size:25px;color:#827D75;display:block;margin-top:3px;
          line-height:1.3}

.foot{font-size:24px;color:#A8A39B;margin-top:30px;letter-spacing:.02em}
.foot b{color:#6E6A64;font-weight:800}
"""


def html(body):
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap"
      rel="stylesheet"><style>{CSS}</style></head><body>{body}</body></html>"""


def img(n):
    # v8.18 렌더를 읽는다. 출시본 소스(v8_p*.png)는 그대로 둔다.
    return "file:///" + os.path.join(
        PREVIEW, f"v815_p{n}.png").replace("\\", "/")


def shoot(name, body):
    os.makedirs(OUT, exist_ok=True)
    src = os.path.join(tempfile.gettempdir(), f"pin_{name}.html")
    with open(src, "w", encoding="utf-8") as f:
        f.write(html(body))
    dest = os.path.join(OUT, f"{name}.png")
    before = os.path.getmtime(dest) if os.path.exists(dest) else 0
    profile = os.path.join(tempfile.gettempdir(), "pinterest-chrome-profile")
    r = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", f"--user-data-dir={profile}",
         "--hide-scrollbars", f"--window-size={W},{H}",
         "--virtual-time-budget=4000",
         f"--screenshot={dest}", "file:///" + src.replace("\\", "/")],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    # Chrome exits 0 without writing when the output file is locked -- the
    # same trap build_planner.to_pdf() guards against.
    if not os.path.exists(dest) or os.path.getmtime(dest) <= before:
        raise RuntimeError(f"Chrome wrote nothing for {name}\n{r.stderr[-400:]}")
    return dest


FOOT = '<div class="foot">Instant download &middot; <b>SongAndParkStudio</b></div>'


# ------------------------------------------------------------------- pins --
def pin_hero():
    return shoot("01_hero", f"""<div class="wrap">
      <span class="kicker">UNDATED &middot; NO-GUILT</span>
      <h1>The ADHD planner<br>with <em>no dates</em><br>to fall behind on</h1>
      <div class="sub">Start any day. Skip a week.<br>Nothing to catch up on.</div>
      <div class="grow"><div class="tab" style="--h:640px">
        <img src="{img(1)}"></div></div>
      {FOOT}
    </div>""")


def pin_tools():
    rows = [("Guess vs actual", "what you thought it would take, what it took"),
            ("Why I am avoiding it", "six reasons, tick the one that fits"),
            ("Stuck on deciding", "you do not need the best one, you need one"),
            ("Rejection sensitivity", "when a small thing lands like a big one"),
            ("Talk to yourself kindly", "answer the inner critic on paper"),
            ("Energy budget", "you have less than the calendar suggests")]
    items = "".join(f'<div class="row"><i></i><div><b>{t}</b>'
                    f'<span>{d}</span></div></div>' for t, d in rows)
    return shoot("02_tools", f"""<div class="wrap">
      <span class="kicker">NOT IN A NORMAL PLANNER</span>
      <h1>Six tools for<br>the hard part</h1>
      <div class="grow"><div class="list">{items}</div></div>
      {FOOT}
    </div>""")


def pin_pages():
    cells = "".join(f'<img src="{img(n)}">' for n in (12, 16, 20, 25, 28, 35))
    return shoot("03_pages", f"""<div class="wrap">
      <span class="kicker">WHAT'S INSIDE</span>
      <h1><em>61</em> pages that<br>are actually different</h1>
      <div class="sub">Not one page copied three hundred times.</div>
      <div class="grow"><div class="grid"
           style="grid-template-columns:repeat(2,auto);--cell:288px">{cells}</div></div>
      {FOOT}
    </div>""")


def pin_nav():
    return shoot("04_navigation", f"""<div class="wrap">
      <span class="kicker">NEVER LOSE YOUR PLACE</span>
      <h1>Ten tabs on<br>every page</h1>
      <div class="sub">The most common complaint about big
        planners is not being able to find anything.</div>
      <div class="grow"><div class="duo">
        <div class="tab"><img src="{img(2)}"></div>
        <div class="tab"><img src="{img(66)}"></div></div></div>
      {FOOT}
    </div>""")


def pin_everyday():
    return shoot("05_everyday", f"""<div class="wrap">
      <span class="kicker">THE PAGES YOU OPEN DAILY</span>
      <h1>A timed day,<br>meds, and a<br>mood row</h1>
      <div class="sub">424 daily and weekly pages.<br>Weeks start on Monday.</div>
      <div class="grow"><div class="duo">
        <div class="tab"><img src="{img(68)}"></div>
        <div class="tab"><img src="{img(452)}"></div></div></div>
      {FOOT}
    </div>""")


def pin_undated():
    rows = [("It never expires", "buy once, use it for years"),
            ("No wall of missed days", "nothing sits there blank and accusing"),
            ("Start in the middle", "March, a Wednesday, whenever")]
    items = "".join(f'<div class="row"><i></i><div><b>{t}</b>'
                    f'<span>{d}</span></div></div>' for t, d in rows)
    return shoot("06_undated", f"""<div class="wrap">
      <span class="kicker">WHY UNDATED MATTERS</span>
      <h1>Not a single<br>date printed<br><em>anywhere</em></h1>
      <div class="grow" style="flex-direction:column;gap:40px">
        <div class="list">{items}</div>
        <div class="tab" style="--h:420px"><img src="{img(69)}"></div>
      </div>
      {FOOT}
    </div>""")


if __name__ == "__main__":
    for fn in (pin_hero, pin_tools, pin_pages, pin_nav, pin_everyday, pin_undated):
        print("saved", os.path.basename(fn()))
