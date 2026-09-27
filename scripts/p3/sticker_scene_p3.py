# -*- coding: utf-8 -*-
"""상품 3 스티커 실사용 장면 -- iPad 위 주간 페이지를 손글씨로 채우고 스티커를 붙인 모습 (리스팅 이미지 후보). Prod 3 방 소유.

    python scripts/p3/sticker_scene_p3.py     # -> output/prod3/preview/sticker_scene/<DRAFT>/sticker_scene.png (2000x2000)

2026-09-27 사용자: 앱 화면 흉내 목업(sticker_mockup_p3.py)은 "그리 이쁘지 않다" -- 빈 페이지·싸 보이는 가짜 앱 화면·너무 먼 거리.
그래서 앱 화면 없이 기기 틀만, 페이지를 크게, 손글씨(Caveat, Google Fonts OFL)로 한 주를 채우고 스티커는 뜻 있는 자리에 붙인다.
좌표는 PDF 의 글자·괘선 위치(pt) 기준 -- 2027 월요일판 458쪽 Week 12 (Named alarms).
"""
import pathlib
import re
import sys

import pymupdf
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[2]
DRAFT = "draft-v0.2"   # v0.2 = 형광펜을 "due Fri!" 위로, Top 3 글자가 체크에 가리지 않게, 연필이 Brain dump 를 덜 덮게, 수요일 글 왼쪽으로
PLANNER, STICKERS = "v0.22", "draft-v0.8"
OUT = ROOT / "output/prod3/preview/sticker_scene" / DRAFT
if OUT.exists():
    raise SystemExit(f"{OUT} 는 이미 있다. 덮어쓰지 않는다 -- DRAFT 를 올릴 것.")
OUT.mkdir(parents=True)
ST = (ROOT / f"output/prod3/stickers/{STICKERS}/png").as_uri()

html = (ROOT / f"src/prod3/planner/{PLANNER}/ADHD-Year-Planner-2027-mon.html").read_text(encoding="utf-8")
ids = re.findall(r'<section class="pg" id="([^"]+)"', html)
pg = pymupdf.open(ROOT / f"output/prod3/planner/{PLANNER}/ADHD-Year-Planner-2027-mon.pdf")[ids.index("w12")]
SW = 1700                                   # 화면 속 페이지 폭(px)
K = SW / pg.rect.width                      # pt -> px
pm = pg.get_pixmap(matrix=pymupdf.Matrix(K, K))
pm.save(str(OUT / "_page.png"))
SH = pm.height
BZ, X0, Y0 = 34, (2000 - SW) // 2 - 34, 170      # 기기 틀 두께, 위치
INK = "#1d2740"


def at(x, y):
    return f"left:{x * K:.0f}px;top:{y * K:.0f}px"


def hand(x, y, text, size=11, rot=0, extra=""):
    return f'<div class="h" style="{at(x, y)};font-size:{size * K:.0f}px;transform:rotate({rot}deg);{extra}">{text}</div>'


def stk(rel, x, y, h, rot=0):
    return f'<img class="s" src="{ST}/{rel}" style="{at(x, y)};height:{h * K:.0f}px;transform:rotate({rot}deg)">'


on_page = "".join([
    # 금요일 판정: "helped" 에 펜으로 동그라미 + HELPED 스티커
    f'<svg class="pen" style="left:{156 * K:.0f}px;top:{178 * K:.0f}px;width:{48 * K:.0f}px;height:{26 * K:.0f}px" viewBox="0 0 48 26">'
    f'<path d="M30 4C18 1 5 4 3 12s10 12 24 11 19-6 17-12S33 2 22 4" fill="none" stroke="{INK}" stroke-width="1.3" stroke-linecap="round"/></svg>',
    stk("Experiments/helped_cyan.png", 322, 156, 54, -8),
    # MON
    hand(64, 248, "✓ labeled the 7:40 alarm “Leave now”", 11, -1),
    hand(64, 266, "✓ dentist call (finally!)", 11, -0.5),
    stk("Small-wins/did-the-thing_paper.png", 290, 262, 22, 5),
    # TUE
    hand(64, 316, "groceries + pharmacy pickup", 11, -1),
    hand(64, 334, '<span style="text-decoration:line-through;text-decoration-thickness:2px">reply to Sam</span>  ✓', 11, 0),
    # WED
    stk("Energy/low-battery-day_blush.png", 64, 380, 21, -3),
    hand(190, 384, "basics only. nap at 3 :)", 11, -1),
    # THU
    '<div class="hl" style="' + at(123, 449) + f';width:{35 * K:.0f}px;height:{10 * K:.0f}px"></div>',
    hand(64, 448, "pay phone bill — due Fri!", 11, -0.5),
    hand(64, 466, "laundry, round 2", 11, -1),
    # FRI
    hand(64, 518, "named alarms actually worked.", 11, -1),
    hand(64, 536, "keep it for March →", 11, -1),
    stk("Brain-weather/good_mist.png", 330, 506, 42, 6),
    # SAT
    hand(64, 585, "farmers market w/ Jo", 11, -1),
    # TOP 3
    hand(443, 229, "Q1 report", 10, -1),
    hand(443, 255, "book flights", 10, -1),
    hand(443, 280, "call Grandma", 10, -1),
    stk("Mini/check_mist.png", 486, 227, 15, 4),
    stk("Mini/check_mist.png", 486, 253, 15, -3),
    # BRAIN DUMP
    hand(443, 328, "gift for Jo's bday?", 10, -1),
    hand(443, 354, "renew passport (May)", 10, -1),
    hand(443, 379, "2-min rule next wk", 10, -1),
    hand(443, 405, "new phone charger", 10, -1),
])

loose = "".join(f'<img class="loose" src="{ST}/{rel}" style="left:{x}px;top:{y}px;height:{h}px;transform:rotate({r}deg)">'
                for rel, x, y, h, r in [("Experiments/not-for-me_ink.png", 40, 40, 190, -14),
                                        ("Energy/recharge_deep.png", 1380, 36, 96, 9),
                                        ("Experiments/sort-of_stone.png", 1720, 110, 170, 12)])

page_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@500;600&display=block" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:2000px;height:2000px;overflow:hidden;position:relative;
  background:radial-gradient(ellipse 90% 70% at 50% 35%,#f1eee8 0%,#e6e2da 70%,#ddd8cf 100%)}}
.ipad{{position:absolute;left:{X0}px;top:{Y0}px;width:{SW + 2 * BZ}px;height:{SH + 2 * BZ}px;border-radius:78px;
  background:#1c1c1e;padding:{BZ}px;box-shadow:0 40px 80px rgba(40,30,20,.28),0 10px 24px rgba(40,30,20,.18),inset 0 0 0 3px #3a3a3c}}
.screen{{position:relative;width:{SW}px;height:{SH}px;border-radius:46px;overflow:hidden;background:url('_page.png')}}
.h{{position:absolute;font-family:'Caveat',cursive;font-weight:500;color:{INK};white-space:nowrap;transform-origin:left center;line-height:1}}
.s{{position:absolute;transform-origin:center;filter:drop-shadow(0 2px 3px rgba(0,0,0,.12))}}
.pen{{position:absolute}}
.hl{{position:absolute;background:rgba(237,187,0,.38);border-radius:3px;transform:rotate(-1deg)}}
.loose{{position:absolute;filter:drop-shadow(0 14px 18px rgba(40,30,20,.25))}}
.pencil{{position:absolute;left:1380px;top:1900px;width:760px;height:44px;transform:rotate(-24deg);transform-origin:left center;
  filter:drop-shadow(0 18px 16px rgba(40,30,20,.3))}}
</style></head><body>
<div class="ipad"><div class="screen">{on_page}</div></div>
{loose}
<svg class="pencil" viewBox="0 0 760 44"><defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#ffffff"/><stop offset=".55" stop-color="#f2f2f0"/><stop offset="1" stop-color="#d9d8d4"/></linearGradient></defs>
<path d="M60 4H740a18 18 0 0 1 0 36H60L4 22z" fill="url(#g)"/><path d="M4 22L60 4v36z" fill="#e9e8e4"/><path d="M4 22l18-6v12z" fill="#2b2b2d"/>
<rect x="700" y="4" width="3" height="36" fill="#cfcfcb"/></svg>
</body></html>"""
f = OUT / "scene.html"
f.write_text(page_html, encoding="utf-8")
with sync_playwright() as p:
    br = p.chromium.launch(channel="chrome")
    b = br.new_page(viewport={"width": 2000, "height": 2000})
    b.goto(f.as_uri()); b.evaluate("document.fonts.ready"); b.wait_for_timeout(1200)
    b.screenshot(path=str(OUT / "sticker_scene.png"))
    br.close()
print(OUT / "sticker_scene.png")
