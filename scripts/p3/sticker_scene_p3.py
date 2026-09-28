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

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from devices_p3 import ALU, CAM, GLASS, IPAD_SHADOW, SHEEN, pencil_png  # noqa: E402
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[2]
DRAFT = "draft-v0.11"   # v0.11 = iPad·펜슬 그림자·반사 옅게, devices_p3 의 값을 그대로 씀(사용자: 과해서 그림판 같다) / v0.10 = full 배치 KEEP 스티커를 펜슬 길 위로(800 -> 690) -- 펜슬이 반쯤 덮어 "…P" 만 보였다 / v0.9 = 펜슬·iPad 를 devices_p3.py 로(3D 음영 펜슬, 알루미늄 테두리 + 유리 베젤) -- 리스팅 01 과 같은 소품 (사용자: SVG 펜슬이 구리다) / v0.8 = full 배치 배경 투명 -- 리스팅 07 의 리소 원이 장면 네모에 잘렸다 / v0.7 v0.7 = 플래너 v0.23 페이지(모서리 하이라이트 고침) / v0.6 v0.6 = full 배치 그림자가 아래에서 잘려 리스팅에 경계선 -> iPad 조금 작게, 그림자 짧게 / v0.5 (v0.4 폴더는 INK 정의 빠져 멈춘 빈 폴더)  v0.4 = 리스팅용 full 배치 추가 -- iPad 세로 통째로(사용자: 잘라 넣어 가로 모드로 보였다)
# v0.3   # v0.3 = 손글씨 대조: 금요일 "keep it for March" -> 분기 흐름대로 "keeper → Q1 review", Brain dump "2-min rule next wk"(7주차) -> 13주차 실제 실험 "decide once", 책상 위 NOT FOR ME -> IN MY PLAYBOOK (광고에 부정어 X)
# v0.2   # v0.2 = 형광펜을 "due Fri!" 위로, Top 3 글자가 체크에 가리지 않게, 연필이 Brain dump 를 덜 덮게, 수요일 글 왼쪽으로
PLANNER, STICKERS = "v0.23", "draft-v0.8"
OUT = ROOT / "output/prod3/preview/sticker_scene" / DRAFT
if OUT.exists():
    raise SystemExit(f"{OUT} 는 이미 있다. 덮어쓰지 않는다 -- DRAFT 를 올릴 것.")
OUT.mkdir(parents=True)
ST = (ROOT / f"output/prod3/stickers/{STICKERS}/png").as_uri()

html = (ROOT / f"src/prod3/planner/{PLANNER}/ADHD-Year-Planner-2027-mon.html").read_text(encoding="utf-8")
ids = re.findall(r'<section class="pg" id="([^"]+)"', html)
pg = pymupdf.open(ROOT / f"output/prod3/planner/{PLANNER}/ADHD-Year-Planner-2027-mon.pdf")[ids.index("w12")]

INK = "#1d2740"
# 두 가지 배치. full = 리스팅 11번 자리(가로 1480 x 세로 1110) -- iPad 가 세로로 통째로 보인다 (사용자: 잘라 넣으니 가로 모드로 착각할 수 있다)
LAYOUTS = {
    "sticker_scene": dict(CW=2000, CH=2000, SW=1700, BZ=34, Y0=170, R=78, SR=46,
                          bg="radial-gradient(ellipse 90% 70% at 50% 35%,#f1eee8 0%,#e6e2da 70%,#ddd8cf 100%)",
                          loose=[("Experiments/in-my-playbook_deep.png", 30, 70, 100, -12), ("Energy/recharge_deep.png", 1380, 36, 96, 9),
                                 ("Experiments/sort-of_stone.png", 1720, 110, 170, 12)],
                          pencil=(1380, 1922, 760, 24)),   # 펜촉 끝 (x, y), 길이, 반시계 각도
    "sticker_scene_full": dict(CW=1480, CH=1110, SW=716, BZ=20, Y0=24, R=46, SR=26, bg="transparent",   # 리스팅 배경과 같은 색
                               loose=[("Experiments/in-my-playbook_deep.png", 20, 110, 62, -12), ("Energy/recharge_deep.png", 70, 470, 58, 8),
                                      ("Brain-weather/great_ink.png", 130, 760, 150, -6), ("Experiments/sort-of_stone.png", 1195, 90, 165, 12),
                                      ("Small-wins/tiny-step_blush.png", 1200, 500, 54, -8), ("Experiments/keep_mist.png", 1230, 690, 64, 6)],
                               pencil=(985, 1045, 500, 38)),
}
with sync_playwright() as p:
    br = p.chromium.launch(channel="chrome")
    for name, L in LAYOUTS.items():
        SW, BZ = L["SW"], L["BZ"]
        K = SW / pg.rect.width                                       # pt -> px (손글씨·스티커 좌표가 이걸 따른다)
        pm = pg.get_pixmap(matrix=pymupdf.Matrix(K, K))
        pm.save(str(OUT / f"_page_{name}.png"))
        SH = pm.height
        X0 = (L["CW"] - SW - 2 * BZ) // 2


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
            hand(64, 536, "keeper → Q1 review", 11, -1),
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
            hand(443, 379, "next wk: decide once", 10, -1),
            hand(443, 405, "new phone charger", 10, -1),
        ])
        px, py, plen, pang = L["pencil"]
        pen, (tx, ty) = pencil_png(plen, pang)
        pen.save(OUT / f"_pencil_{name}.png")
        loose = "".join(f'<img class="loose" src="{ST}/{rel}" style="left:{x}px;top:{y}px;height:{h}px;transform:rotate({r}deg)">'
                        for rel, x, y, h, r in L["loose"])
        page_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@500;600&display=block" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{L["CW"]}px;height:{L["CH"]}px;overflow:hidden;position:relative;background:{L["bg"]}}}
.ipad{{position:absolute;left:{X0}px;top:{L["Y0"]}px;width:{SW + 2 * BZ}px;height:{SH + 2 * BZ}px;border-radius:{L["R"]}px;padding:{BZ}px;
  background:{ALU};box-shadow:{IPAD_SHADOW}}}
.glass{{position:absolute;inset:{max(4, round(SW * .011))}px;border-radius:{L["R"] - max(4, round(SW * .011))}px;background:{GLASS};box-shadow:inset 0 0 0 1px rgba(255,255,255,.06)}}
.cam{{position:absolute;left:{(SW + 2 * BZ) / 2 - 5:.0f}px;top:{BZ / 2 - 3:.0f}px;width:10px;height:10px;border-radius:50%;background:{CAM}}}
.screen::after{{content:"";position:absolute;inset:0;pointer-events:none;background:{SHEEN}}}
.screen{{position:relative;width:{SW}px;height:{SH}px;border-radius:{L["SR"]}px;overflow:hidden;background:url('_page_{name}.png')}}
.h{{position:absolute;font-family:'Caveat',cursive;font-weight:500;color:{INK};white-space:nowrap;transform-origin:left center;line-height:1}}
.s{{position:absolute;transform-origin:center;filter:drop-shadow(0 2px 3px rgba(0,0,0,.12))}}
.pen{{position:absolute}}
.hl{{position:absolute;background:rgba(237,187,0,.38);border-radius:3px;transform:rotate(-1deg)}}
.loose{{position:absolute;filter:drop-shadow(0 14px 18px rgba(40,30,20,.25))}}
.pencil{{position:absolute;left:{px - tx:.0f}px;top:{py - ty:.0f}px}}
</style></head><body>
<div class="ipad"><div class="glass"></div><div class="cam"></div><div class="screen">{on_page}</div></div>
{loose}
<img class="pencil" src="_pencil_{name}.png">
</body></html>"""
        f = OUT / f"{name}.html"
        f.write_text(page_html, encoding="utf-8")
        b = br.new_page(viewport={"width": L["CW"], "height": L["CH"]})
        b.goto(f.as_uri()); b.evaluate("document.fonts.ready"); b.wait_for_timeout(1200)
        b.screenshot(path=str(OUT / f"{name}.png"), omit_background=L["bg"] == "transparent")
        b.close()
        print(OUT / f"{name}.png")
    br.close()
