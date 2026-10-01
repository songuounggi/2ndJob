# -*- coding: utf-8 -*-
"""상품 4 Pinterest 핀 **시안** -- 1000x1500(2:3), 판매 PDF 쪽을 렌더해 배치 (PROCESS.md 10단계 준비).

    python scripts/p4/pinterest_p4.py        # -> output/prod4/pinterest/draft-v0.1/01_guests.png ~ 06_undated.png

pinterest.md 규칙: 핀은 피드에서 썸네일 크기로 읽힌다 -- 한 장에 한마디를 큰 글씨로. 핀마다 다른 것은 그림과 제목뿐이라
(설명은 Etsy 설명이 뜬다) 여섯 장의 각도를 서로 다르게: 손님맞이(11~12월 시즌) · 기운 없는 날 · 엉망일 때 · 10분 방 ·
인쇄 · 날짜 없음. 그림 속 문구는 listing-p4.md · p4_content 에 있는 말만. 숫자는 판에서 센다.
안전 영역: 글자 가로 70-930 · 세로 60-1440, 그림은 캔버스 안, 라벨-그림 겹침 0 -- 넘으면 멈춘다.
이미 있는 시안 폴더면 멈춘다(덮어쓰지 않는다).
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import listing_images_p4 as L  # noqa: E402  -- 쪽 렌더 · 섹션 색 · 숫자는 리스팅 사진과 같은 것을 쓴다
import p4_content as C  # noqa: E402

DRAFT = "draft-v0.2"   # v0.2: 패드 키움(470 -> 560, 뒤 380 -> 380 위치 조정), 01 부제가 제목과 같은 말 -> "Everything else into one box." / v0.1: 첫 시안 6장
OUT = os.path.join(ROOT, "output", "prod4", "pinterest", DRAFT)
L.OUT = OUT            # 쪽 그림을 이 폴더 _pages 에


def pin(sec, kicker, h1, sub, visual):
    d, t, w1, w2 = L.SEC[sec]
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
html,body{{margin:0;padding:0}}
body{{width:1000px;height:1500px;overflow:hidden;position:relative;font-family:'Nunito',sans-serif;color:#2C3631;
  background:radial-gradient(ellipse 70% 40% at 10% 92%, {w2}cc, transparent 70%),
             radial-gradient(ellipse 60% 35% at 95% 60%, {w1}aa, transparent 70%), #FBF8F3}}
.top{{position:absolute;left:70px;right:70px;top:70px;text-align:center}}
.k{{display:inline-block;padding:12px 28px;border-radius:999px;background:{t};color:{d};font-size:26px;font-weight:800;letter-spacing:.08em}}
h1{{margin:24px 0 0;font-size:84px;font-weight:800;letter-spacing:-.025em;line-height:1.05;text-wrap:balance}}
.s{{margin:20px 0 0;font-size:34px;color:#5F6B65;line-height:1.3;text-wrap:balance}}
.vis{{position:absolute;left:0;top:0;width:1000px;transform-origin:50% 0}}
.pad,.paper{{position:absolute}}
.pad{{background:#2B2A33;border-radius:40px;padding:18px;box-shadow:0 36px 70px -24px rgba(40,40,60,.45)}}
.pad img{{display:block;border-radius:10px}}
.paper img{{display:block;box-shadow:0 24px 50px -18px rgba(40,40,60,.35);border-radius:3px}}
</style></head><body>
<div class="top"><span class="k">{kicker}</span><h1>{h1}</h1>{f'<p class="s">{sub}</p>' if sub else ''}</div>
<div class="vis">{visual}</div>
</body></html>"""


def pins():
    P = lambda k: L.page_png("color", k, 1.8)
    B = lambda k: L.page_png("BW", k)
    two = lambda back, front: L.pad(P(back), 560, 130, 380, 1) + L.pad(P(front), 80, 40, 560, 2)
    return [
        ("01_guests", pin("aqua", "GUESTS IN 2 HOURS", "Company coming? Clean only what they’ll see.", C.GUESTS[2][4],
                          two("entry", "guests"))),
        ("02_energy", pin("mint", "ENERGY MENU", "Low battery? Pick a 2-minute task.",
                          f"{L.N_TASKS} tasks sorted by battery and time", two("day-Low", "energy"))),
        ("03_rescue", pin("aqua", "RESCUE MODE", "For when it is all too much", "Five steps, then stop.",
                          two("w7", "rescue"))),
        ("04_rooms", pin("lemon", "ROOM RESET CARDS", "Ten minutes, then stop.", "A “done enough” line for every room",
                         two("deep-kitchen", "kitchen"))),
        ("05_print", pin("lavender", "PRINTABLE", "A home reset checklist you can print",
                         "Black &amp; white, easy on ink. US Letter.",
                         L.paper(B("w1"), 470, 120, 470, 1, 4) + L.paper(B("kitchen"), 70, 40, 520, 2, -3))),
        ("06_undated", pin("lavender", "UNDATED", "Skip a week. Nothing to catch up on.",
                           f"{L.N_WEEKS} reset weeks. Start on any week.", two("weeks", "w1"))),
    ]


LAYOUT_JS = L.LAYOUT_JS.replace("1790", "1440")
SAFE_JS = (L.SAFE_JS.replace("r.left < 260 || r.right > 1740 || r.top < 250 || r.bottom > 1750", "r.left < 70 || r.right > 930 || r.top < 60 || r.bottom > 1440")
           .replace("r.left < 200 || r.right > 1800 || r.bottom > 1850", "r.left < 20 || r.right > 980 || r.bottom > 1480"))


def main():
    if os.path.exists(OUT):
        raise SystemExit(f"{OUT} 는 이미 있다. 덮어쓰지 않는다 -- DRAFT 를 올릴 것.")
    os.makedirs(os.path.join(OUT, "_pages"))
    assert SAFE_JS != L.SAFE_JS and "1440" in LAYOUT_JS, "안전 영역 치환이 안 됐다"
    from chrome_auto import launch
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = launch(p)
        pg = br.new_page(viewport={"width": 1000, "height": 1500})
        for name, doc in pins():
            src = os.path.join(OUT, "_pages", f"_{name}.html")
            open(src, "w", encoding="utf-8").write(doc)
            pg.goto("file:///" + src.replace(os.sep, "/"))
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(400)
            if not pg.evaluate("document.fonts.check('800 84px Nunito')"):
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
