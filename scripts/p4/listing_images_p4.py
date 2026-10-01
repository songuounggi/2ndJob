# -*- coding: utf-8 -*-
"""상품 4 Etsy 리스팅 사진 **시안** -- 실제 판매 PDF 쪽을 렌더해 2000x2000 정사각형에 배치한다 (PROCESS.md 8단계).

    python scripts/p4/listing_images_p4.py          # -> output/prod4/listing/draft-v0.1/01_hero.png ~ 10_files.png

상품 1·3 에서 얻은 규칙 (shop.md 리스팅 이미지 · listing-p3.md):
  - 상품 1 대표 사진과 같은 틀: 크림 바탕 · 맨 위 배지 · 큰 제목 · 숫자 알약 · 단순한 패드(#2B2A33, 회색 띠·반사 없음)
  - 폰 Etsy 앱에서 읽히게 제목 150px 이상(01 은 170) -- 상품 3 은 다 만든 뒤 제목이 작아 다시 했다
  - 바탕을 비워 두지 않는다 -- 섹션 색 번짐(디자인 시안 w1·w2)을 옅게 (상품 3: "경쟁작보다 썰렁하다")
  - 안전 영역: 글자는 가로 260-1740 · 세로 250-1750, 기기는 가로 200-1800 (폰 4:5 · PC 4:3 검색 자르기) -- 넘으면 멈춘다
  - 그림 속 문구는 listing-p4.md 설명 · p4_content 원고에 있는 말만. 숫자(쪽 수 · 할 일 · 방 · 주)는 판에서 센다
  - 이미 있는 시안 폴더면 멈춘다(덮어쓰지 않는다) -- 고치면 DRAFT 를 올린다
"""
import os
import re
import sys

import pymupdf

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import p4_content as C  # noqa: E402
import pages_p4  # noqa: E402

VER = "v0.11"
DRAFT = "draft-v0.5"   # v0.5: 그림 묶음이 남는 공간보다 작으면 위아래 가운데로(06·09 아래가 비었다) / v0.4: 10 라벨이 패드 뒤에 가렸다 -> 패드·종이 줄임 + 라벨-그림 겹침 검사, 09 두 줄 사이 440 -> 320, 06 패드 키워 부채꼴 / v0.3: 10 오른쪽 라벨 상자 1060 -> 1040(안전 영역 1740 을 20px 넘었다, v0.2 는 09 까지만) / v0.2: 그림 묶음을 글자 블록 아래 50px 부터, 넘치면 비율대로 줄임(v0.1 은 01 에서 멈춤 -- 제목 두 줄이 그림과 붙었다) / v0.1: 첫 시안
OUT = os.path.join(ROOT, "output", "prod4", "listing", DRAFT)
PDF = {t: os.path.join(ROOT, "output", "prod4", "planner", VER, f"home-reset_{VER}_{t}-FINAL.pdf") for t in ("color", "BW")}

KEYS = [k for k, _, _ in pages_p4.specs()]
N_PAGES = len(KEYS)
N_TASKS = sum(len(v) for v in C.ENERGY.values())
N_ROOMS = len(C.ROOMS) + len(C.MY_ROOMS)
N_WEEKS = len([k for k in KEYS if re.fullmatch(r"w\d+", k)])
WORD = {10: "Ten", 52: "52"}

# 섹션 색 (README §4) -- d 진한(글자) · t 옅은(배지) · w1/w2 번짐
SEC = {"mint": ("#537364", "#E4F0EA", "#CFE4EE", "#C4E6D0"), "lemon": ("#7D6A28", "#F8F0D0", "#D6E7EE", "#F8ECB8"),
       "lavender": ("#6E6490", "#ECE8F8", "#F1D3E5", "#DFD8F4"), "aqua": ("#237581", "#DAF1F4", "#F6DCCB", "#C9ECF2")}


def page_png(tag, key, scale=2.2):
    n = KEYS.index(key)
    path = os.path.join(OUT, "_pages", f"{tag}_{n + 1:03d}_{key}.png")
    if not os.path.exists(path):
        with open(PDF[tag], "rb") as fh:
            doc = pymupdf.open(stream=fh.read(), filetype="pdf")
        doc[n].get_pixmap(matrix=pymupdf.Matrix(scale, scale)).save(path)
    return "file:///" + path.replace(os.sep, "/")


def pad(src, x, y, w, z=1, cls="pad"):
    """상품 1 패드: 단색 테두리, 화면 = 쪽 그림 (가로 w, 세로는 쪽 비율)"""
    return (f'<div class="{cls}" style="left:{x}px;top:{y}px;z-index:{z}"><img src="{src}" style="width:{w}px"></div>')


def paper(src, x, y, w, z=1, rot=0):
    return (f'<div class="paper" style="left:{x}px;top:{y}px;z-index:{z};transform:rotate({rot}deg)">'
            f'<img src="{src}" style="width:{w}px"></div>')


def chip_row(chips, col):
    return "".join(f'<span class="chip" style="color:{col}">{c}</span>' for c in chips)


def html(sec, kicker, h1, sub, chips, visual, hero=False):
    d, t, w1, w2 = SEC[sec]
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
html,body{{margin:0;padding:0}}
body{{width:2000px;height:2000px;overflow:hidden;position:relative;font-family:'Nunito',sans-serif;color:#2C3631;
  background:radial-gradient(ellipse 60% 45% at 12% 88%, {w2}cc, transparent 70%),
             radial-gradient(ellipse 55% 40% at 92% 70%, {w1}aa, transparent 70%),
             radial-gradient(ellipse 50% 30% at 80% 8%, {w2}66, transparent 70%), #FBF8F3}}
.top{{position:absolute;left:260px;right:260px;top:{250 if hero else 270}px;text-align:center}}
.k{{display:inline-block;padding:16px 40px;border-radius:999px;background:{t};color:{d};font-size:42px;font-weight:800;letter-spacing:.08em}}
h1{{margin:34px 0 0;font-size:{170 if hero else 150}px;font-weight:800;letter-spacing:-.025em;line-height:1.04;text-wrap:balance}}
.s{{margin:30px 0 0;font-size:52px;color:#5F6B65;line-height:1.3;text-wrap:balance}}
.chips{{margin-top:40px;display:flex;justify-content:center;gap:24px;flex-wrap:wrap}}
.chip{{background:#fff;border-radius:999px;padding:16px 40px;font-size:46px;font-weight:800;box-shadow:0 10px 30px -12px rgba(40,50,45,.25)}}
.vis{{position:absolute;left:0;top:0;width:2000px;height:1100px;transform-origin:50% 0}}
.pad,.paper{{position:absolute}}
.pad{{background:#2B2A33;border-radius:60px;padding:28px;box-shadow:0 50px 90px -30px rgba(40,40,60,.45)}}
.pad img{{display:block;border-radius:14px}}
.paper img{{display:block;box-shadow:0 30px 60px -20px rgba(40,40,60,.35);border-radius:4px}}
.lab{{position:absolute;font-size:40px;font-weight:800;color:{d};text-align:center}}
</style></head><body>
<div class="top"><span class="k">{kicker}</span><h1>{h1}</h1>{f'<p class="s">{sub}</p>' if sub else ''}
{f'<div class="chips">{chip_row(chips, d)}</div>' if chips else ''}</div>
<div class="vis">{visual}</div>
</body></html>"""


def images():
    P = lambda k, s=2.2: page_png("color", k, s)
    B = lambda k: page_png("BW", k)
    out = []
    # 01 대표 -- 표지 + 순서도
    out.append(("01_hero", html("mint", "UNDATED · NO-GUILT", C.COVER[0], C.COVER[1][0].upper() + C.COVER[1][1:] + ".",
                                [f"{N_PAGES} pages", "Hyperlinked", "Printable B&amp;W"],
                                pad(P("flow"), 1050, 960, 560, 1) + pad(P("cover"), 390, 860, 660, 2), hero=True)))
    # 02 Energy menu
    out.append(("02_energy", html("mint", "ENERGY MENU", "Pick by battery, not by day",
                                  f"{N_TASKS} tasks · low, medium, full · 2 to 20 minutes", [],
                                  pad(P("day-Low"), 1060, 900, 560, 1) + pad(P("energy"), 380, 800, 680, 2))))
    # 03 방 카드
    out.append(("03_rooms", html("lemon", "ROOM RESET CARDS", "Ten minutes, then stop",
                                 f"{WORD.get(N_ROOMS, N_ROOMS)} rooms · six steps · a “done enough” line", [],
                                 pad(P("deep-kitchen"), 1060, 900, 560, 1) + pad(P("kitchen"), 380, 800, 680, 2))))
    # 04 Rescue
    out.append(("04_rescue", html("aqua", "RESCUE MODE", "For when it is all too much",
                                  "Tap SOS on any page after the cover. Five steps, then stop.", [],
                                  pad(P("w7"), 1060, 900, 560, 1) + pad(P("rescue"), 380, 800, 680, 2))))
    # 05 순서도
    out.append(("05_flow", html("mint", "HOW IT FLOWS", "One page shows the whole system", C.FLOW["sub"], [],
                                pad(P("flow"), 620, 760, 700, 2))))
    # 06 탭 여섯
    tabs = ["index", "rooms", "routines", "tools"]
    out.append(("06_tabs", html("lavender", "SIX TABS", "Every page is one tap away",
                                " · ".join(["Home", "Energy", "Rooms", "Routines", "Weeks", "Tools"]), [],
                                "".join(pad(P(k, 1.8), 250 + i * 350, 860 + (i % 2) * 60, 380, 2 + i, "pad sm") for i, k in enumerate(tabs)))))
    # 07 흑백 인쇄판
    out.append(("07_print", html("lavender", "PRINTABLE", "Black &amp; white for paper",
                                 f"The same {N_PAGES} pages in grayscale, easy on ink. US Letter.", [],
                                 paper(B("w1"), 1010, 880, 620, 1, 4) + paper(B("kitchen"), 380, 820, 640, 2, -3))))
    # 08 52주
    out.append(("08_weeks", html("lavender", f"{N_WEEKS} RESET WEEKS", "Skip a week. Nothing to catch up on.",
                                 C.PAGE_TEXT["weeks"][1], [],
                                 pad(P("weeks"), 1060, 900, 560, 1) + pad(P("w1"), 380, 800, 680, 2))))
    # 09 안에 든 것
    grid = ["energy", "day-Low", "kitchen", "deep-kitchen", "house-map", "daily",
            "rotation", "laundry-loop", "rescue", "guests", "wins", "dopamine"]
    cells = "".join(paper(P(k, 1.2), 280 + (i % 6) * 245, 820 + (i // 6) * 320, 215, 2) for i, k in enumerate(grid))
    out.append(("09_inside", html("aqua", "WHAT'S INSIDE", f"{N_PAGES} pages, six sections",
                                  "Home · Energy · Rooms · Routines · Weeks · Tools", [], cells)))
    # 10 파일 둘
    files = (pad(P("cover"), 320, 900, 520, 2) + paper(B("cover"), 1120, 930, 540, 2)
             + '<div class="lab" style="left:260px;top:1660px;width:700px">Hyperlinked PDF</div>'
             + '<div class="lab" style="left:1040px;top:1660px;width:700px">Printable B&amp;W PDF</div>')
    out.append(("10_files", html("mint", "WHAT YOU GET", "2 files", "Goodnotes, Notability, and other PDF note apps", [], files)))
    return out


LAYOUT_JS = """() => {
  // 그림 묶음 = 글자 블록 아래 50px 부터, 아래 1790 까지 -- 넘치면 비율대로 줄인다(가운데 기준)
  const vis = document.querySelector('.vis');
  const items = [...vis.children];
  const minY = Math.min(...items.map(e => e.offsetTop));
  const maxY = Math.max(...items.map(e => e.offsetTop + e.offsetHeight));
  const top = document.querySelector('.top').getBoundingClientRect().bottom + 50;
  const sc = Math.min(1, (1790 - top) / (maxY - minY));
  vis.style.transform = `scale(${sc})`;
  const spare = (1790 - top) - (maxY - minY) * sc;              // 남는 공간 -- 위아래 가운데로 (06·09 아래가 비었다)
  vis.style.top = (top + Math.max(0, spare) / 2 - minY * sc) + 'px';
  return Math.round(sc * 100) / 100;
}"""

SAFE_JS = """() => {
  const bad = [];
  document.querySelectorAll('.top *, .lab').forEach(e => {
    if (!e.textContent.trim() || e.children.length && !e.classList.contains('lab')) return;
    const r = e.getBoundingClientRect();
    if (r.width && (r.left < 260 || r.right > 1740 || r.top < 250 || r.bottom > 1750)) bad.push(['글자', e.textContent.trim().slice(0, 30), r.left|0, r.top|0, r.right|0, r.bottom|0]);
  });
  document.querySelectorAll('.pad, .paper').forEach(e => {
    const r = e.getBoundingClientRect();
    if (r.left < 200 || r.right > 1800 || r.bottom > 1850) bad.push(['그림', e.className, r.left|0, r.top|0, r.right|0, r.bottom|0]);
  });
  // 라벨이 그림에 가리지 않는다 (v0.3 의 10 "Hyperlinked PDF" 가 패드 뒤로 숨었다)
  const pics = [...document.querySelectorAll('.pad, .paper')].map(e => e.getBoundingClientRect());
  document.querySelectorAll('.lab').forEach(e => {
    const r = e.getBoundingClientRect();
    if (pics.some(q => r.left < q.right && r.right > q.left && r.top < q.bottom && r.bottom > q.top)) bad.push(['라벨이 그림과 겹침', e.textContent.trim()]);
  });
  const top = document.querySelector('.top').getBoundingClientRect().bottom;
  const vis = [...document.querySelectorAll('.pad, .paper')].map(e => e.getBoundingClientRect().top);
  if (vis.length && Math.min(...vis) < top + 30) bad.push(['겹침', '제목 아래 30px 안에 그림', top|0, Math.min(...vis)|0]);
  return bad;
}"""


def main():
    if os.path.exists(OUT):
        raise SystemExit(f"{OUT} 는 이미 있다. 덮어쓰지 않는다 -- DRAFT 를 올릴 것.")
    os.makedirs(os.path.join(OUT, "_pages"))
    from chrome_auto import launch
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = launch(p)
        pg = br.new_page(viewport={"width": 2000, "height": 2000})
        for name, doc in images():
            src = os.path.join(OUT, "_pages", f"_{name}.html")
            open(src, "w", encoding="utf-8").write(doc)
            pg.goto("file:///" + src.replace(os.sep, "/"))
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(400)
            if not pg.evaluate("document.fonts.check('800 150px Nunito')"):
                raise SystemExit(f"{name}: Nunito 를 못 불러왔다")
            sc = pg.evaluate(LAYOUT_JS)
            pg.wait_for_timeout(100)
            bad = pg.evaluate(SAFE_JS)
            if bad:
                raise SystemExit(f"{name}: 안전 영역·겹침 {bad}")
            pg.screenshot(path=os.path.join(OUT, f"{name}.png"))
            print("  ", name, f"그림 묶음 비율 {sc}")
        br.close()
    print("->", OUT)


if __name__ == "__main__":
    main()
