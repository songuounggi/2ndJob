# -*- coding: utf-8 -*-
"""상품 2(학생용)의 Etsy 리스팅 이미지 9장.

    PLANNER_VERSION=<버전> python scripts/build_planner.py
    python scripts/build_mockups_student.py <버전>      # 기본 student-v0.8

페이지 그림(output/preview/listing_src/)은 스크립트가 그 버전 PDF 에서 직접
뽑는다(render_src). 전에는 뽑는 방법이 기록에 없어 다른 PC 에서 재현이 안 됐다.

상품 1의 `build_mockups.py` 는 건드리지 않는다. 톤도 파는 이야기도 다르다.
다만 그 방에서 얻은 교훈은 그대로 가져온다:

  1. **검색 결과에서는 위아래가 잘린다.** 카드가 정사각을 가로로 길게
     크롭하기 때문에, 맨 위에 둔 제목은 잘려 나간다. 핵심 문구는
     세로 가운데 4:3 띠(y 250~1750) 안에 둔다. -> SAFE
  2. **리스팅 페이지에서는 440x440 으로 줄어든다.** 2000px 기준 40px 글자는
     거기서 9px 이라 안 읽힌다. 핵심 문구는 최소 70px.
  3. **원칙은 "적게, 크게".** 경쟁자가 화면 4개씩 넣는 건 색이 강해서다.
     우리 파스텔은 작아지면 전부 같은 색이 된다.
  4. **아홉 장이 서로 달라 보여야 한다.** 상품 1 에서 3x2 격자 세 장이
     갤러리에서 같은 이미지 세 번으로 보였다. 다크/라이트, 기기/평면,
     클로즈업/전체를 번갈아 쓴다.
  5. **썰렁하면 싸구려로 보인다.** 빈 자리에는 숫자 칩·라벨·기기 그림자를
     넣어 밀도를 올린다.
"""
import os
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "output", "preview", "listing_src")
OUT = os.path.join(ROOT, "output", "listing_student")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SIZE = 2000
SAFE = 250          # 위아래 이만큼은 검색 결과에서 잘린다고 보고 비운다
# 좌우. Etsy 검색 격자는 정사각을 양옆 약 140px 씩 잘라 간다. 상품 1 첫 대표
# 이미지가 x=112 에서 시작해 "DHD & Wellness / igital Planner" 로 첫 글자가
# 잘렸다(scripts/build_mockups.py). 읽혀야 하는 것은 양옆 260px 안쪽에.
# 학생용은 130 이었다(사용자 지적 2026-09-24).
SAFE_X = 260

VIOLET = "#7C4DFF"
PINK = "#F45D9B"
ORANGE = "#FF8A3D"
CYAN = "#22D3EE"
GREEN = "#3FBF7F"
PAPER = "#F6F3FD"
INKC = "#241E3A"

CSS = """
*{box-sizing:border-box;margin:0;padding:0;-webkit-print-color-adjust:exact}
body{width:2000px;height:2000px;overflow:hidden;color:%(INKC)s;
     font-family:'Nunito',system-ui,sans-serif;background:%(PAPER)s}

/* 검색 결과가 잘라 가는 띠. 핵심 문구는 이 안에 둔다. */
.wrap{width:100%%;height:100%%;padding:%(SAFE)spx %(SAFE_X)spx;display:flex;
      flex-direction:column;position:relative;z-index:1}
.aurora{position:absolute;inset:0;z-index:0}
.aurora img{width:100%%;height:100%%;object-fit:cover}
.dark{color:#F4F1FF}

.kicker{display:inline-block;font-size:36px;font-weight:800;
        letter-spacing:.14em;padding:18px 36px;border-radius:99px;
        align-self:flex-start;background:#E9E3FB;color:#5A3FB8}
.dark .kicker{background:rgba(255,255,255,.16);color:#FFF}
h1{font-size:132px;font-weight:800;line-height:1.04;margin-top:36px;
   letter-spacing:-.025em}
h2{font-size:92px;font-weight:800;line-height:1.08;margin-top:36px;
   letter-spacing:-.022em}
.sub{font-size:46px;line-height:1.38;margin-top:26px;opacity:.74;
     text-wrap:balance}   /* 끝 단어 하나만 다음 줄로 떨어지지 않게(1번 start., 5번 score.) */
.grow{flex:1;display:flex;align-items:center;justify-content:center;
      min-height:0;gap:40px;position:relative}
/* overflow:hidden 을 두면 태블릿 그림자가 칸 아래에서 칼같이 잘려
   회색 띠가 된다(2·7번). 크기는 shelf() 와 고정 높이로 막는다. */
.foot{font-size:36px;text-align:center;margin-top:28px;opacity:.6}

.tab{background:#1C1830;border-radius:54px;padding:24px;position:relative;
     box-shadow:0 36px 80px rgba(20,10,60,.38)}
.tab img{display:block;border-radius:32px;height:var(--tab,860px);width:auto}

.chips{display:flex;gap:22px;margin-top:34px;flex-wrap:wrap}
.chip{background:#FFF;border-radius:99px;padding:20px 40px;font-size:42px;
      font-weight:800;box-shadow:0 12px 30px rgba(40,28,90,.12)}
.chip i{font-style:normal;font-weight:700;font-size:32px;opacity:.55;
        margin-left:12px}
.dark .chip{background:rgba(255,255,255,.14);color:#FFF;box-shadow:none}
.dark .pg b{color:#FFF}
.dark .pg span{color:rgba(255,255,255,.72);opacity:1}
.dark .note span{opacity:.75}

.shelf{display:flex;gap:32px;align-items:flex-end;justify-content:center;
       width:100%%}
.pg{display:flex;flex-direction:column;align-items:center;gap:20px}
.pg img{border-radius:18px;box-shadow:0 24px 56px rgba(40,28,90,.20);
        display:block;height:var(--cell,700px);width:auto}
.pg b{font-size:38px;font-weight:800}
.pg span{font-size:28px;opacity:.6;text-align:center;line-height:1.3}

.tags{display:flex;flex-wrap:wrap;gap:18px;max-width:780px}
.tag{border-radius:99px;padding:16px 32px;font-size:34px;font-weight:800;
     background:rgba(255,255,255,.14);color:#FFF}

.note{display:flex;gap:22px;align-items:flex-start;margin-top:26px}
.note .dot{width:22px;height:22px;border-radius:99px;flex:none;margin-top:14px}
/* 일부만 보여 주는 그림은 잘린 쪽을 페이드로 마감한다.
   그냥 자르면 "실수로 잘렸다"로 보인다. */
.cut{display:block;border-radius:26px}
.cut.r{-webkit-mask-image:linear-gradient(to right,#000 68%%,transparent 99%%)}
.cut.rb{-webkit-mask-image:linear-gradient(to right,#000 72%%,transparent 99%%),
        linear-gradient(to bottom,#000 80%%,transparent 99%%);
        -webkit-mask-composite:source-in}
.note b{font-size:42px;font-weight:800;display:block}
.note span{font-size:30px;opacity:.62;display:block;margin-top:6px}
""" % {"PAPER": PAPER, "INKC": INKC, "SAFE": SAFE, "SAFE_X": SAFE_X}


def html(body, extra=""):
    return ("""<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap"
      rel="stylesheet"><style>%s%s</style></head><body>%s</body></html>"""
            % (CSS, extra, body))


def img(name):
    p = os.path.join(SRC, name + ".png")
    if not os.path.exists(p):
        raise SystemExit("페이지 PNG 가 없다: %s" % p)
    return "file:///" + p.replace("\\", "/")


MIN_GAP = 24     # 세로로 쌓인 덩어리 사이 최소 간격(px)
# 글꼴(Nunito)이 다 오기 전에 재면 줄바꿈이 촬영본과 달라진다 -- 5번 "score."
# 가 검사에서는 윗줄에 붙어 있었다. fonts.ready 뒤에 잰다.
SAFE_JS = """
document.fonts.ready.then(() => {
const bad = [];
document.querySelectorAll('h1,h2,.kicker,.sub,.chip,.tag,.pg b,.pg span,.note b,.note span,.foot').forEach(e => {
  const r = e.getBoundingClientRect();
  if (!r.width || !r.height) return;
  if (r.left < %d - 0.5 || r.right > 2000 - %d + 0.5 || r.top < %d - 0.5 || r.bottom > 2000 - %d + 0.5)
    bad.push((e.textContent || '').trim().slice(0, 30) + ' @' + [r.left, r.top, r.right, r.bottom].map(Math.round).join(','));
});
// 세로로 쌓인 덩어리끼리 붙어 있으면 안 된다 -- 5번에서 숫자 칩 줄과 학기
// 카드 줄이 0px 로 붙어 있었다(사용자 2026-09-24). 세로 흐름(.wrap, 세로 .grow)의
// 이웃한 자식 사이 간격이 MIN_GAP 미만이면 잡는다.
// .grow 는 칸이 크고 내용을 가운데 둔다 -- 칸이 아니라 보이는 내용의 범위를 잰다.
const ink = k => {
  if (!k.classList.contains('grow')) return k.getBoundingClientRect();
  const rs = [...k.children].map(c => ink(c)).filter(r => r.height > 0);
  if (!rs.length) return k.getBoundingClientRect();
  const t = Math.min(...rs.map(r => r.top)), b = Math.max(...rs.map(r => r.bottom));
  return {top: t, bottom: b, height: b - t};
};
document.querySelectorAll('.wrap, .grow').forEach(box => {
  if (getComputedStyle(box).flexDirection !== 'column') return;
  const kids = [...box.children].map(k => [k, ink(k)])
    .filter(([k, r]) => r.height > 0).sort((x, y) => x[1].top - y[1].top);
  for (let i = 1; i < kids.length; i++) {
    const gap = kids[i][1].top - kids[i-1][1].bottom;
    if (gap < %d) bad.push('붙음 ' + Math.round(gap) + 'px: ' +
      (kids[i-1][0].textContent || kids[i-1][0].className).trim().slice(0, 20) + ' / ' +
      (kids[i][0].textContent || kids[i][0].className).trim().slice(0, 20));
  }
});
// 마지막 줄에 단어 하나만 남는 줄바꿈(5번 "score."). <br> 로 일부러 나눈
// 줄(1번 "ADHD / Student / Planner")은 제외 -- 마지막 <br> 뒤 단어만 본다.
document.querySelectorAll('h1,h2,.sub,.foot').forEach(e => {
  let words = [];
  const walk = n => [...n.childNodes].forEach(c => {
    if (c.nodeType === 3) c.textContent.split(/(\s+)/).forEach(w => {
      if (!w) return;
      const s = document.createElement('span'); s.textContent = w;
      c.parentNode.insertBefore(s, c); if (w.trim()) words.push(s);
    }), c.remove();
    else if (c.nodeName === 'BR') words = [];
    else walk(c);
  });
  walk(e);
  if (words.length < 3) return;
  const tops = words.map(w => Math.round(w.getBoundingClientRect().top));
  const last = tops[tops.length - 1];
  if (tops.filter(t => t === last).length === 1 && tops[0] !== last)
    bad.push('외톨이 단어: ' + words[words.length - 1].textContent);
});
document.body.setAttribute('data-safe', JSON.stringify(bad));
});
""" % (SAFE_X, SAFE_X, SAFE, SAFE, MIN_GAP)


def check_safe(name, body, extra=""):
    """글자가 안전 영역 밖이면 멈춘다 -- Etsy 검색·가로 배치에서 잘린다."""
    import json, re
    src = os.path.join(tempfile.gettempdir(), "mockst_safe_%s.html" % name)
    with open(src, "w", encoding="utf-8") as f:
        f.write(html(body, extra).replace("</body>", "<script>%s</script></body>" % SAFE_JS))
    r = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu",
         "--user-data-dir=%s" % os.path.join(tempfile.gettempdir(), "mockup-safe-profile"),
         "--window-size=%d,%d" % (SIZE, SIZE), "--virtual-time-budget=6000",
         "--dump-dom", "file:///" + src.replace(chr(92), "/")],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.search(r'data-safe="([^"]*)"', r.stdout or "")
    bad = json.loads(m.group(1).replace("&quot;", '"')) if m else ["(측정 실패)"]
    if bad:
        raise SystemExit("%s: 안전 영역·간격·줄바꿈 %s" % (name, bad[:4]))


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
         "--window-size=%d,%d" % (SIZE, SIZE), "--virtual-time-budget=6000",
         "--screenshot=%s" % dest, "file:///" + src.replace("\\", "/")],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    if not os.path.exists(dest) or os.path.getmtime(dest) <= before:
        raise RuntimeError("Chrome 이 %s 를 쓰지 않았다\n%s"
                           % (name, (r.stderr or "")[-400:]))
    return dest


def dark(body):
    return ('<div class="aurora"><img src="%s"></div>'
            '<div class="wrap dark">%s</div>' % (img("cover_bg"), body))


# 밝은 장의 바탕. 거의 흰 단색(PAPER)은 "흰 바탕은 아니다"(사용자 2026-09-24).
# pastel = 제품 내지 바닥과 같은 연한 오로라, dark = 표지 오로라(dark() 와 같게).
LIGHT_BG = os.environ.get("MOCK_LIGHT", "dark")


def light(body):
    if LIGHT_BG == "dark":
        return dark(body)
    if LIGHT_BG == "pastel":
        return ('<div class="aurora"><img src="%s"></div>'
                '<div class="wrap">%s</div>' % (img("light_bg"), body))
    return '<div class="wrap">%s</div>' % body


def page(name, label, note, cell=700):
    return ('<div class="pg" style="--cell:%dpx"><img src="%s">'
            '<b>%s</b><span>%s</span></div>' % (cell, img(name), label, note))


SHELF_W = 2000 - 2 * SAFE_X     # 목업 폭 - 좌우 안전 여백
PAGE_RATIO = 612 / 792.0


def shelf(cells, cell):
    """페이지 카드 한 줄. 폭을 넘치면 양 끝이 잘려 나간다 -- 찍기 전에 막는다
    (2026-09-24: 4장 x 640, 3장 x 780 이 넘쳐 "ss schedule" 이 나갔다)."""
    need = len(cells) * cell * PAGE_RATIO + (len(cells) - 1) * 32
    if need > SHELF_W:
        raise SystemExit("카드 %d장 x 높이 %dpx = 폭 %dpx > %dpx. 높이를 줄일 것"
                         % (len(cells), cell, need, SHELF_W))
    return "".join(page(k, t, d, cell) for k, t, d in cells)


def chips(items, dark_=False):
    return '<div class="chips">%s</div>' % "".join(
        '<div class="chip">%s<i>%s</i></div>' % (a, b) for a, b in items)


# ------------------------------------------------------------------ 9장 --
# 문구의 근거 (2026-09-24, student-v0.8 실측. product2-student.md "F" 절 표):
#   437 pages     = PDF 페이지 수
#   32 templates  = 쓰는 페이지 디자인 수(목차·탭 페이지 제외, 노트 3종 포함)
#   Eight terms   = TERMS 8, 반복 세트는 학기마다 한 벌
#   two taps      = 모든 페이지 쌍의 최단 탭 수 최대값 (링크 그래프 BFS)
#   4,900 links   = PDF 링크 주석 4,933
#   112 day pages = DAYS_PER_TERM 14 x 8
#   12 / 20       = 학기마다 반복되는 디자인 12종 / 그 밖 20종 (32종, 3번)
#   Five pages    = FOCUS 탭 아래 5장 (8번. 전에는 세 탭에서 모은 "Eleven")
#   Nine notes    = 노트 3종 x 3장 (10번)
#   print 는 뺐다 -- 괘선 대비 1.14:1 이라 인쇄하면 거의 안 보인다(G)
# 페이지 구성을 바꾸면 이 숫자들을 다시 잰다.
def s1_hero():
    """검색 결과에서 보이는 단 한 장.

    자리 계산을 먼저 한다. 폭 2000 - 좌우 패딩 260 - 글 단 700 - 간격 60
    = 980px 이 기기 몫이다. 태블릿 한 대(높이 1100 -> 폭 약 900)는 들어가고
    두 대는 안 들어간다. 안 맞는 걸 억지로 넣으면 글자를 덮거나 잘린다.
    """
    return dark(
        '<div style="flex:1;display:flex;align-items:center;gap:60px;'
        'min-height:0">'
        '<div style="flex:0 0 700px">'
        '<div class="kicker">UNDATED &middot; ADHD STUDENT</div>'
        '<h1 style="font-size:96px">ADHD<br>Student<br>Planner</h1>'
        '<div class="sub" style="font-size:42px">Syllabus, assignments and '
        'exams &mdash; broken into pieces you can actually start.</div>'
        + chips([("437", "pages"), ("32", "designs")])
        + chips([("4", "years"), ("10", "tabs")])
        + '</div>'
          '<div style="flex:1;display:flex;justify-content:center;'
          'min-width:0">'
          '<div class="tab" style="--tab:1000px;transform:rotate(2deg)">'
          '<img src="%s"></div></div></div>' % img("syllabus"))


def s2_syllabus():
    """이 상품을 사는 이유 한 장."""
    notes = [("Assignments", "what is due, and when", VIOLET),
             ("Exams &amp; quizzes", "the dates you keep forgetting", PINK),
             ("Reading", "what has to be read before class", CYAN)]
    n = "".join('<div class="note"><div class="dot" style="background:%s">'
                '</div><div><b>%s</b><span>%s</span></div></div>'
                % (c, t, d) for t, d, c in notes)
    return light(
        '<div class="kicker">THE PAGE YOU BUY THIS FOR</div>'
        '<h2>One handout,<br>broken into dates.</h2>'
        '<div class="grow" style="gap:90px">'
        '<div style="flex:none;max-width:640px">%s</div>'
        '<div class="tab" style="--tab:1000px"><img src="%s"></div></div>' %
        (n, img("syllabus")))


def s3_templates():
    """구조가 한눈에 다른 것만 고른다. 글자는 이 크기에서 안 읽힌다."""
    cells = [("timetable", "Class schedule", "the week, hour by hour"),
             ("cornell", "Lecture notes", "cue &middot; notes &middot; summary"),
             ("grades", "Grade tracker", "what each piece is worth"),
             ("braindump", "Brain dump", "no order, no rules")]
    return light(
        '<div class="kicker">32 PAGE DESIGNS</div>'
        '<h2>12 for every term.<br>20 for whenever you need them.</h2>'
        '<div class="grow"><div class="shelf">%s</div></div>'
        % shelf(cells, 440))
    # 카드 높이: 폭 2000 - 좌우 패딩 260 = 1740px 안에 들어가야 한다. 페이지
    # 비율 0.773 -> 4장이면 높이 <= 532, 3장이면 <= 722. 640/780 으로 두었을
    # 때 양 끝 카드가 잘려 "ss schedule", 탭 레일 없는 페이지가 나갔다.


def s4_navigation():
    """'탭 10개'가 핵심인데 그림에서 실오라기면 주장과 그림이 따로 논다."""
    tabs = ["INDEX", "SEMESTER", "WEEKS", "DAYS", "CLASSES",
            "WORK", "STUDY", "FOCUS", "LIFE", "NOTES"]
    t = "".join('<div class="tag">%s</div>' % x for x in tabs)
    return dark(
        '<div class="kicker">TAP, DO NOT SCROLL</div>'
        '<h2>Ten tabs down the side.<br>Any page in two taps.</h2>'
        '<div class="grow" style="gap:70px">'
        '<div class="tab" style="--tab:960px;flex:none"><img src="%s"></div>'
        '<div style="flex:none;max-width:600px"><div class="tags">%s</div>'
        '<div class="sub" style="font-size:40px;margin-top:34px">'
        'Over 4,900 working links inside. The tab you are on lights up, so you '
        'never lose your place.</div></div></div>'
        % (img("d1"), t))
    # 전에는 레일만 잘라 오른쪽을 흐리게 지웠다(cut r). 7번과 같은 흐림이라
    # 함께 뺐다(2026-09-24). 페이지 전체를 태블릿에 넣고 탭 이름은 옆에.


def s5_structure():
    cards = "".join(
        '<div style="flex:1;background:#FFF;border-radius:24px;padding:22px 6px;'
        'text-align:center;box-shadow:0 16px 40px rgba(40,28,90,.10)">'
        '<div style="font-size:26px;font-weight:800;letter-spacing:.06em;white-space:nowrap;'
        'color:%s">TERM %d</div>'
        '<div style="font-size:24px;color:#8A8499;margin-top:8px">16 weeks'
        '</div></div>' % (c, i + 1)
        for i, c in enumerate([VIOLET, VIOLET, PINK, PINK,
                               ORANGE, ORANGE, CYAN, CYAN]))
    return light(
        '<div class="kicker">UNDATED &middot; FOUR YEARS</div>'
        '<h2>Start any week.<br>Skip a week.</h2>'
        '<div class="sub">Nothing is dated, so a gap costs you nothing. '
        'The page is not keeping score.</div>'
        + chips([("8", "terms"), ("128", "week pages"), ("112", "day pages")])
        + '<div class="grow" style="flex-direction:column;gap:34px;margin-top:44px">'
          '<div style="display:flex;gap:18px;width:100%%">%s</div>'
          '<img src="%s" style="flex:1;min-height:0;height:0;width:auto;border-radius:20px;'
          'box-shadow:0 30px 70px rgba(40,28,90,.22)"></div>'
          % (cards, img("t1")))


def s6_work():
    cells = [("backwards", "Working backwards", "from the deadline"),
             ("assignments", "Assignment tracker", "what is due, and what is done"),
             ("group", "Group project", "who does what, by when")]
    return light(
        '<div class="kicker">WORK</div>'
        '<h2>From the deadline,<br>not from today.</h2>'
        '<div class="grow"><div class="shelf">%s</div></div>'
        % shelf(cells, 600))


def s7_study():
    """클로즈업 한 장. 다른 장들이 전신 샷이라 여기서 결을 보여 준다."""
    return dark(
        '<div class="kicker">STUDY</div>'
        '<h2>Split the scope first.<br>Then give each piece a day.</h2>'
        '<div class="grow" style="gap:50px">'
        '<div class="tab" style="--tab:880px"><img src="%s"></div>'
        '<div style="display:flex;flex-direction:column;gap:30px">'
        '<img src="%s" style="height:360px;border-radius:18px;'
        'box-shadow:0 30px 70px rgba(10,5,40,.45)">'
        '<img src="%s" style="height:360px;border-radius:18px;'
        'box-shadow:0 30px 70px rgba(10,5,40,.45)"></div></div>'
        '<div class="foot" style="font-size:38px">Exam study plans &middot; '
        'Lecture notes &middot; Reading log<br>Grade tracker &middot; '
        'Study session log &middot; Office hours</div>'
        % (img("exam"), img("cornell"), img("grades")))
    # 전에는 시험 계획을 잘라 확대하고 오른쪽·아래를 흐리게 지웠다(cut rb).
    # 흰 얼룩처럼 보였다 -- "이 그라데이션은 최악"(사용자). 페이지 전체를
    # 2번처럼 태블릿 프레임에 넣는다.


def s8_focus():
    cells = [("braindump", "Brain dump", "empty your head onto the page"),
             ("avoiding", "Why I am avoiding it", "name it and it gets smaller"),
             ("energy", "Energy budget", "what you actually have today")]
    return light(
        '<div class="kicker">WHEN STARTING IS THE HARD PART</div>'
        '<h2>Five pages for the<br>part nobody sells you.</h2>'
        '<div class="grow"><div class="shelf">%s</div></div>'
        % shelf(cells, 600))


def s9_howto():
    apps = ["GoodNotes", "Notability", "Xodo", "Adobe Acrobat"]
    tags = "".join('<div class="tag">%s</div>' % a for a in apps)
    steps = [("1", "Buy and download", "one PDF, instantly"),
             ("2", "Open in your notes app", "iPad or Android tablet"),
             ("3", "Tap the side tabs", "no scrolling through 437 pages")]
    st = "".join(
        '<div class="note"><div class="dot" style="background:%s;width:44px;'
        'height:44px;margin-top:6px;color:#FFF;font-size:26px;'
        'font-weight:800;display:flex;align-items:center;'
        'justify-content:center">%s</div>'
        '<div><b>%s</b><span>%s</span></div></div>'
        % (c, n, t, d) for (n, t, d), c in zip(steps, (VIOLET, PINK, CYAN)))
    return dark(
        '<div class="kicker">HOW IT WORKS</div>'
        '<h2>Works in the app<br>you already use.</h2>'
        '<div class="grow" style="justify-content:space-between;gap:60px">'
        '<div style="flex:none;max-width:820px">%s'
        '<div class="tags" style="margin-top:44px">%s</div></div>'
        '<div class="tab" style="--tab:760px"><img src="%s"></div></div>'
        '<div class="foot">A digital download &mdash; nothing is shipped.</div>'
        % (st, tags, img("timetable")))


def s10_notes():
    """10번째 장 (2026-09-24, 사용자: 9장이 아니라 10장). 노트 9장은 기존 9장을
    만든 뒤에 들어온 기능이라 어디에도 안 보였다. 리스팅은 "nine note pages"."""
    cells = [("ruled", "Ruled", "lined, top to bottom"),
             ("dots", "Dot grid", "lists, sketches, and diagrams"),
             ("plain", "Plain", "nothing printed on it")]
    return light(
        '<div class="kicker">NOTES</div>'
        '<h2>Nine note pages.<br>Three kinds of paper.</h2>'
        '<div class="grow"><div class="shelf">%s</div></div>'
        % shelf(cells, 600))


SHOTS = [("1_hero", s1_hero), ("2_syllabus", s2_syllabus),
         ("3_templates", s3_templates), ("4_navigation", s4_navigation),
         ("5_structure", s5_structure), ("6_work", s6_work),
         ("7_study", s7_study), ("8_focus", s8_focus), ("9_howto", s9_howto),
         ("10_notes", s10_notes)]


# 목업에 쓰는 페이지 그림: 이름 -> 페이지 id (scale 2 로 뽑는다)
SRC_PAGES = {"syllabus": "s1", "timetable": "h1", "grades": "g1",
             "assignments": "a1", "exam": "e1", "t1": "t1", "d1": "d1",
             "cornell": "cornell", "braindump": "braindump",
             "backwards": "backwards", "group": "group",
             "avoiding": "avoiding", "energy": "energy",
             "ruled": "n1", "dots": "n4", "plain": "n7"}


def render_src(version):
    """listing_src 의 페이지 그림을 그 버전의 FINAL PDF 에서 뽑는다."""
    import re
    import pypdfium2 as pdfium
    html = open(os.path.join(ROOT, "src", "planner_%s.html" % version),
                encoding="utf-8").read()
    ids = re.findall(r'<section class="page[^"]*" id="([^"]+)"', html)
    pdf = os.path.join(ROOT, "output", "planner_%s-FINAL.pdf" % version)
    with open(pdf, "rb") as fh:
        doc = pdfium.PdfDocument(fh.read())
    os.makedirs(SRC, exist_ok=True)
    for name, pid in SRC_PAGES.items():
        doc[ids.index(pid)].render(scale=2).to_pil().save(
            os.path.join(SRC, name + ".png"))
    doc.close()


def prep():
    """합성에 필요한 원본 몇 장을 만든다."""
    from PIL import Image
    # 다크 장면 바닥이 될 오로라
    cov = Image.open(os.path.join(ROOT, "assets",
                                  "app_cover_student-v0.1.png")).convert("RGB")
    cov.resize((SIZE, SIZE), Image.LANCZOS).save(
        os.path.join(SRC, "cover_bg.png"))
    # 밝은 장 바탕 -- 제품 내지 바닥(sheet)과 같은 오로라
    sheet = os.path.join(ROOT, "assets", "app_sheet_%s.png" % VERSION)
    if os.path.exists(sheet):
        Image.open(sheet).convert("RGB").resize((SIZE, SIZE), Image.LANCZOS).save(
            os.path.join(SRC, "light_bg.png"))
    # 레일 클로즈업 -- '탭 10개'를 실제로 보이게
    d1 = Image.open(os.path.join(SRC, "d1.png")).convert("RGB")
    w, h = d1.size
    d1.crop((0, 0, int(w * 0.34), h)).save(os.path.join(SRC, "rail_zoom.png"))
    # 시험 계획 표 클로즈업 -- 결을 보여 주는 한 장
    ex = Image.open(os.path.join(SRC, "exam.png")).convert("RGB")
    w, h = ex.size
    ex.crop((int(w * 0.05), int(h * 0.20), w, int(h * 0.72))).save(
        os.path.join(SRC, "exam_zoom.png"))


if __name__ == "__main__":
    import sys
    VERSION = sys.argv[1] if len(sys.argv) > 1 else "student-v1.1"
    render_src(VERSION)
    prep()
    for name, fn in SHOTS:
        check_safe(name, fn())
        print("찍음:", shoot(name, fn()))
