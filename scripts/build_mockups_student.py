# -*- coding: utf-8 -*-
"""상품 2(학생용)의 Etsy 리스팅 이미지 9장.

    PLANNER_VERSION=student-v0.1 python scripts/build_planner.py
    python scripts/build_mockups_student.py

상품 1의 `build_mockups.py` 를 건드리지 않고 따로 둔다. 톤이 다르고
(크림/블루 vs 다크 오로라/유리) 파는 이야기도 다르기 때문이다.

Etsy 는 리스팅 이미지를 정사각으로 보여준다. 2000x2000 으로 짜고
헤드리스 Chrome 으로 찍는다. 원본은 build 가 만든 페이지 PNG 다.

> **검색 결과에서는 440px 폭으로 줄어든다.** 2000px 에서 40px 인 글자는
>   거기서 9px 이 되어 안 읽힌다. 첫 장의 핵심 문구는 최소 70px 로 둘 것.
>   (상품 1 에서 한 번 갈아엎은 이유다)
"""
import os
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "output", "preview", "listing_src")
OUT = os.path.join(ROOT, "output", "listing_student")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SIZE = 2000

# 상품의 색 그대로. 표지 오로라에서 뽑았다.
INK = "#17133E"
VIOLET = "#7C4DFF"
PINK = "#F45D9B"
ORANGE = "#FF8A3D"
CYAN = "#22D3EE"
PAPER = "#F7F4FD"

CSS = """
*{box-sizing:border-box;margin:0;padding:0;-webkit-print-color-adjust:exact}
body{width:2000px;height:2000px;overflow:hidden;color:#241E3A;
     font-family:'Nunito',system-ui,sans-serif;background:%(PAPER)s}
.wrap{width:100%%;height:100%%;padding:120px;display:flex;
      flex-direction:column}
/* 오로라 위에 불투명 배경을 깔면 오로라가 통째로 가려진다.
   다크 장면은 색만 바꾸고 배경은 <img> 가 맡는다. */
.dark{color:#F4F1FF}
.aurora{position:absolute;inset:0;z-index:0}
.aurora img{width:100%%;height:100%%;object-fit:cover}
.on{position:relative;z-index:1;width:100%%;height:100%%;display:flex;
    flex-direction:column;padding:120px}

.kicker{display:inline-block;font-size:34px;font-weight:800;
        letter-spacing:.14em;padding:16px 34px;border-radius:99px;
        align-self:flex-start;background:rgba(255,255,255,.14);
        color:rgba(244,241,255,.92)}
.kicker.lt{background:#E9E3FB;color:#5A3FB8}
h1{font-size:118px;font-weight:800;line-height:1.06;margin-top:40px;
   letter-spacing:-.02em}
h2{font-size:86px;font-weight:800;line-height:1.1;letter-spacing:-.02em}
.sub{font-size:44px;line-height:1.4;margin-top:28px;opacity:.72}
.grow{flex:1;display:flex;align-items:center;justify-content:center;
      min-height:0;gap:40px;overflow:hidden}
.foot{font-size:34px;text-align:center;margin-top:34px;opacity:.55}

/* 기기 틀 -- 사진 없이 깔끔한 베젤 */
.tab{background:#221E33;border-radius:60px;padding:28px;
     box-shadow:0 50px 110px rgba(20,10,60,.40)}
.tab img{display:block;border-radius:34px;height:var(--tab,1120px);
         width:auto}

.grid{display:grid;gap:28px;width:100%%;justify-items:center}
.grid img{height:var(--cell,420px);width:auto;border-radius:16px;
          box-shadow:0 18px 44px rgba(40,28,90,.18);display:block}

.card{background:#FFF;border-radius:32px;padding:44px 48px;flex:1;
      box-shadow:0 18px 44px rgba(40,28,90,.12)}
.card b{display:block;font-size:50px;font-weight:800}
.card span{display:block;font-size:31px;color:#6B6480;margin-top:12px;
           line-height:1.35}
.row{display:flex;gap:34px;align-items:stretch;width:100%%}
.big{font-size:176px;font-weight:800;line-height:1}
.dot{width:26px;height:26px;border-radius:99px;flex:none}
""" % {"PAPER": PAPER, "INK": INK}


def html(body, extra=""):
    return ("""<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap"
      rel="stylesheet"><style>%s%s</style></head><body>%s</body></html>"""
            % (CSS, extra, body))


def img(name):
    p = os.path.join(SRC, name + ".png")
    if not os.path.exists(p):
        raise SystemExit("페이지 PNG 가 없다: %s\n"
                         "  먼저 빌드하고 listing_src 를 렌더할 것" % p)
    return "file:///" + p.replace("\\", "/")


def shoot(name, body, extra=""):
    os.makedirs(OUT, exist_ok=True)
    src = os.path.join(tempfile.gettempdir(), "mockst_%s.html" % name)
    with open(src, "w", encoding="utf-8") as f:
        f.write(html(body, extra))
    dest = os.path.join(OUT, "%s.png" % name)
    before = os.path.getmtime(dest) if os.path.exists(dest) else 0
    profile = os.path.join(tempfile.gettempdir(), "mockup-chrome-profile")
    r = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu",
         "--user-data-dir=%s" % profile, "--hide-scrollbars",
         "--window-size=%d,%d" % (SIZE, SIZE), "--virtual-time-budget=5000",
         "--screenshot=%s" % dest, "file:///" + src.replace("\\", "/")],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    if not os.path.exists(dest) or os.path.getmtime(dest) <= before:
        raise RuntimeError("Chrome 이 %s 를 쓰지 않았다\n%s"
                           % (name, (r.stderr or "")[-400:]))
    return dest


def dark(body):
    """표지 오로라를 배경으로 깐 다크 장면."""
    return ('<div class="aurora"><img src="%s"></div>'
            '<div class="on dark">%s</div>'
            % (img("cover_bg"), body))


# --------------------------------------------------------------- 9장 --
def s1_hero():
    """검색 결과에서 보이는 단 한 장. 440px 로 줄어도 읽혀야 한다."""
    return dark(
        '<div class="kicker">UNDATED &middot; GOODNOTES READY</div>'
        '<h1 style="font-size:150px">ADHD Student<br>Planner</h1>'
        '<div class="sub" style="font-size:52px">Syllabus, assignments and '
        'exams &mdash;<br>broken into pieces you can actually start.</div>'
        '<div class="grow" style="--tab:880px;align-items:flex-end;'
        'overflow:hidden"><div class="tab"><img src="%s"></div></div>'
        '<div class="foot" style="font-size:40px">428 pages &nbsp;&middot;&nbsp; '
        '33 unique templates &nbsp;&middot;&nbsp; four years</div>'
        % img("d1"))


def s2_syllabus():
    """핵심 셀링 포인트 한 장. 이 상품을 사는 이유다."""
    return ('<div class="wrap"><div class="kicker lt">THE ONE THAT MATTERS'
            '</div><h1>One handout,<br>broken into dates.</h1>'
            '<div class="sub">The syllabus arrives, you skim it, and nothing '
            'moves to your calendar. This page does that in one sitting.</div>'
            '<div class="grow"><img src="%s" style="height:940px;'
            'border-radius:20px;box-shadow:0 30px 70px rgba(40,28,90,.22)">'
            '</div></div>' % img("syllabus"))


def s3_templates():
    cells = ["syllabus", "assignments", "exam", "cornell", "grades", "reading",
             "timetable", "c1", "backwards", "group", "braindump", "energy"]
    g = "".join('<img src="%s">' % img(c) for c in cells)
    return ('<div class="wrap"><div class="kicker lt">33 UNIQUE TEMPLATES</div>'
            '<h2 style="margin-top:34px">Not the same page<br>printed 400 times.'
            '</h2>'
            '<div class="grow"><div class="grid" '
            'style="grid-template-columns:repeat(4,1fr);--cell:380px">%s</div>'
            '</div></div>' % g)


def s4_navigation():
    return ('<div class="wrap"><div class="kicker lt">TAP, DO NOT SCROLL</div>'
            '<h2 style="margin-top:34px">Ten tabs down the side.<br>'
            'Every page is one tap away.</h2>'
            '<div class="sub">The tab you are on lights up, so you always know '
            'where you are. 4,700 working links inside.</div>'
            '<div class="grow"><img src="%s" style="height:820px;'
            'border-radius:20px;box-shadow:0 30px 70px rgba(40,28,90,.22)">'
            '<img src="%s" style="height:820px;border-radius:20px;'
            'box-shadow:0 30px 70px rgba(40,28,90,.22)"></div></div>'
            % (img("index"), img("work")))


def s5_structure():
    cards = [("8 terms", "four years of study, one file", VIOLET),
             ("16 weeks each", "a week page for every week", PINK),
             ("31 day pages a term", "for the days you need one", ORANGE)]
    row = "".join(
        '<div class="card"><div class="dot" style="background:%s"></div>'
        '<b style="margin-top:22px">%s</b><span>%s</span></div>'
        % (c, t, d) for t, d, c in cards)
    return ('<div class="wrap"><div class="kicker lt">UNDATED</div>'
            '<h2 style="margin-top:34px">Start any week.<br>Skip a week.</h2>'
            '<div class="sub">Nothing is dated, so a gap costs you nothing. '
            'The page is not keeping score.</div>'
            '<div class="grow"><img src="%s" style="height:760px;'
            'border-radius:20px;box-shadow:0 30px 70px rgba(40,28,90,.22)">'
            '</div><div class="row">%s</div></div>' % (img("t1"), row))


def s6_work():
    return ('<div class="wrap"><div class="kicker lt">WORK</div>'
            '<h2 style="margin-top:34px">From the deadline,<br>'
            'not from today.</h2>'
            '<div class="sub">Working backwards, assignment tracking, and '
            'group projects where your part is written down.</div>'
            '<div class="grow"><div class="grid" '
            'style="grid-template-columns:repeat(3,1fr);--cell:680px">'
            '<img src="%s"><img src="%s"><img src="%s"></div></div>'
            % (img("backwards"), img("assignments"), img("group")))


def s7_study():
    return ('<div class="wrap"><div class="kicker lt">STUDY</div>'
            '<h2 style="margin-top:34px">Split the scope first.<br>'
            'Then give each piece a day.</h2>'
            '<div class="sub">Exam plans, Cornell notes, and a grade tracker '
            'that shows what each piece is actually worth.</div>'
            '<div class="grow"><div class="grid" '
            'style="grid-template-columns:repeat(3,1fr);--cell:680px">'
            '<img src="%s"><img src="%s"><img src="%s"></div></div>'
            % (img("exam"), img("cornell"), img("grades")))


def s8_focus():
    return ('<div class="wrap"><div class="kicker lt">FOR THE HARD PART</div>'
            '<h2 style="margin-top:34px">Starting is the problem.<br>'
            'These pages are for that.</h2>'
            '<div class="sub">Brain dump, focus sessions, stuck on deciding, '
            'why I am avoiding it, energy budget.</div>'
            '<div class="grow"><div class="grid" '
            'style="grid-template-columns:repeat(3,1fr);--cell:680px">'
            '<img src="%s"><img src="%s"><img src="%s"></div></div>'
            % (img("braindump"), img("avoiding"), img("energy")))


def s9_howto():
    steps = [("1", "Buy and download", "one PDF, instantly"),
             ("2", "Open in GoodNotes", "or Notability, or any PDF app"),
             ("3", "Tap the side tabs", "no scrolling through 400 pages")]
    row = "".join(
        '<div class="card"><div class="big" style="font-size:96px;color:%s">'
        '%s</div><b style="margin-top:18px">%s</b><span>%s</span></div>'
        % (c, n, t, d)
        for (n, t, d), c in zip(steps, (VIOLET, PINK, CYAN)))
    return ('<div class="wrap"><div class="kicker lt">HOW IT WORKS</div>'
            '<h2 style="margin-top:34px">iPad, Android tablet,<br>'
            'or print it.</h2>'
            '<div class="sub">A digital file &mdash; nothing is shipped. '
            'Works with any app that opens a PDF.</div>'
            '<div class="grow"><img src="%s" style="height:700px;'
            'border-radius:20px;box-shadow:0 30px 70px rgba(40,28,90,.22)">'
            '</div><div class="row">%s</div></div>' % (img("timetable"), row))


SHOTS = [
    ("1_hero", s1_hero),
    ("2_syllabus", s2_syllabus),
    ("3_templates", s3_templates),
    ("4_navigation", s4_navigation),
    ("5_structure", s5_structure),
    ("6_work", s6_work),
    ("7_study", s7_study),
    ("8_focus", s8_focus),
    ("9_howto", s9_howto),
]


def make_cover_bg():
    """표지에서 레일과 글자를 뺀 배경. 다크 장면의 바닥으로 쓴다."""
    from PIL import Image
    src = os.path.join(ROOT, "assets", "app_cover_student-v0.1.png")
    dst = os.path.join(SRC, "cover_bg.png")
    Image.open(src).convert("RGB").resize((SIZE, SIZE),
                                          Image.LANCZOS).save(dst)
    return dst


if __name__ == "__main__":
    make_cover_bg()
    for name, fn in SHOTS:
        print("찍음:", shoot(name, fn()))
