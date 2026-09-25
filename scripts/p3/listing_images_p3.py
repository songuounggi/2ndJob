# -*- coding: utf-8 -*-
"""상품 3 Etsy 리스팅 이미지 **시안** -- 실제 판매 파일 페이지를 렌더해 2000x2000 정사각형에 배치한다. Prod 3 방 소유.

    python scripts/p3/listing_images_p3.py            # -> output/prod3/listing/draft-v0.1/

디자인은 사용자 것(Lifted Paper 핸드오프). 여기서는 핸드오프의 종이색·잉크·청록·Source Serif 4 만 쓴다.
이미지 속 문구는 listing-p3.md 에서 check_listing_p3.py 를 통과한 주장만 쓴다(구매자 글 규칙).
이미 있는 시안 폴더면 멈춘다(덮어쓰지 않는다) -- 고치면 DRAFT 를 올린다.
"""
import pathlib
import re
import sys

import pypdfium2 as pdfium

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[2]
VER = "v0.7"
DRAFT = "draft-v0.3"   # v0.1: 05 썸네일 3줄이 아래로 잘림, 06 아래가 비었다 / v0.2: 06 표지 네 장이 멀리서 구분 안 됨 -> 배지
PDF = ROOT / "output" / "prod3" / "planner" / VER / "ADHD-Year-Planner-2027-mon.pdf"
HTML = ROOT / "src" / "prod3" / "planner" / VER / "ADHD-Year-Planner-2027-mon.html"
OUT = ROOT / "output" / "prod3" / "listing" / DRAFT
if OUT.exists():
    raise SystemExit(f"{OUT} 는 이미 있다. 덮어쓰지 않는다 -- DRAFT 를 올릴 것.")
OUT.mkdir(parents=True)
PAGES = OUT / "_pages"
PAGES.mkdir()

ids = re.findall(r'<section class="pg" id="([^"]+)"', HTML.read_text(encoding="utf-8"))
WANT = ["cover", "sos", "year", "experiments", "m3", "d3-15", "d3-16", "w12", "q1", "bw3", "admin",
        "rsd", "budget", "dopamine", "mailbox", "playbook"]
with open(PDF, "rb") as fh:
    doc = pdfium.PdfDocument(fh.read())
for k in WANT:
    doc[ids.index(k)].render(scale=2.2).to_pil().save(PAGES / f"{k}.png")
doc.close()
# 06 에 네 판 표지 -- 월/일 시작, 연도가 표지에 찍혀 있다
for y in ("2026", "2027"):
    for w in ("mon", "sun"):
        with open(ROOT / "output" / "prod3" / "planner" / VER / f"ADHD-Year-Planner-{y}-{w}.pdf", "rb") as fh:
            d = pdfium.PdfDocument(fh.read())
        d[0].render(scale=1.4).to_pil().save(PAGES / f"cover-{y}-{w}.png")
        d.close()

PAPER, INK, N700, CYAN = "#f8f4f4", "#201e1d", "#605d5d", "#006786"
CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=block');
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:2000px;height:2000px;overflow:hidden;background:#e9e6e3;color:{INK};font-family:'Source Serif 4',Georgia,serif}}
.wrap{{position:absolute;inset:0;padding:120px;display:flex;flex-direction:column}}
.k{{font-size:34px;letter-spacing:.14em;text-transform:uppercase;color:{CYAN}}}
h1{{font-size:118px;font-weight:600;line-height:1.02;margin:22px 0 26px;letter-spacing:-.01em}}
p.s{{font-size:46px;font-style:italic;color:{N700};line-height:1.3;max-width:1500px}}
.row{{flex:1;display:flex;gap:60px;align-items:flex-end;justify-content:center;margin-top:60px}}
.pg{{height:100%;max-height:1180px;box-shadow:0 30px 60px rgba(0,0,0,.18),0 4px 10px rgba(0,0,0,.08)}}
.pg.t{{transform:rotate(-2deg)}} .pg.u{{transform:rotate(1.5deg)}}
.grid{{flex:1;display:grid;grid-template-columns:repeat(4,1fr);gap:36px;margin-top:60px}}
.grid img{{width:100%;box-shadow:0 14px 30px rgba(0,0,0,.15)}}
.list{{font-size:44px;line-height:1.55;margin-top:40px}}
.list b{{color:{CYAN};font-weight:600}}
.pill{{display:inline-block;border:2px solid {N700};border-radius:999px;padding:10px 34px;font-size:40px;margin:0 16px 20px 0}}
.cv{{position:relative}}.cv img{{width:100%;box-shadow:0 14px 30px rgba(0,0,0,.15)}}
.bdg{{position:absolute;top:-26px;right:-18px;border-radius:26px;padding:16px 26px 14px;text-align:center;color:#fff;box-shadow:0 8px 18px rgba(0,0,0,.22)}}
.bdg b{{display:block;font-size:64px;font-weight:600;line-height:1}}.bdg span{{display:block;font-size:30px;margin-top:6px;letter-spacing:.04em}}
.bdg.mon{{background:{CYAN}}}.bdg.sun{{background:{INK}}}
.foot{{font-size:34px;color:{N700};margin-top:40px;letter-spacing:.04em}}
"""


def img(k, cls="pg"):
    return f'<img class="{cls}" src="_pages/{k}.png">'


SHOTS = {
    "01_hero": f"""<div class="k">Dated ADHD planner · 2026 &amp; 2027</div>
      <h1>The ADHD Year</h1>
      <p class="s">One small experiment a week. By December, a user manual for your own brain.</p>
      <div class="row">{img("cover", "pg t")}{img("d3-15", "pg u")}</div>""",
    "02_experiments": f"""<div class="k">52 experiments</div>
      <h1>One strategy a week.<br>Keep what works.</h1>
      <p class="s">Printed on that week's page. Mark it on Friday. Keep or drop it each quarter.</p>
      <div class="row">{img("experiments")}{img("w12")}</div>""",
    "03_time_links": f"""<div class="k">Time links</div>
      <h1>Today links to tomorrow.</h1>
      <p class="s">Write a note to future you – it links to the day it arrives, 30 days later.</p>
      <div class="row">{img("d3-15", "pg t")}{img("d3-16", "pg u")}</div>""",
    "04_sos": f"""<div class="k">SOS page</div>
      <h1>Pick what is happening.<br>Tap straight to the tool.</h1>
      <p class="s">"I can't start" · "I'm overwhelmed" · "Someone's words stung"</p>
      <div class="row">{img("sos")}{img("rsd")}</div>""",
    "05_inside": f"""<div class="k">What's inside · 598 pages a year</div>
      <h1>Year, months, weeks, every day – and 45 tools.</h1>
      <div class="grid">{"".join(img(k, "") for k in ["year", "m3", "w12", "d3-15", "admin", "rsd", "budget", "dopamine"])}</div>""",
    "06_files": f"""<div class="k">What you get</div>
      <h1>4 PDFs. Pick your start day.</h1>
      <div class="list"><span class="pill">2026 · Monday start</span><span class="pill">2026 · Sunday start</span><br>
        <span class="pill">2027 · Monday start</span><span class="pill">2027 · Sunday start</span></div>
      <div class="list"><b>Ten tabs</b> on every page · every day <b>two taps</b> away<br>
        For GoodNotes, Notability and other PDF note apps · shaped for a tablet (3:4)</div>
      <div class="grid" style="margin-top:70px;gap:56px">{"".join(
          f'<div class="cv">{img(f"cover-{y}-{w}", "")}<div class="bdg {w}"><b>{y}</b><span>{"Monday" if w == "mon" else "Sunday"} start</span></div></div>'
          for y in ("2026", "2027") for w in ("mon", "sun"))}</div>
      <div class="foot">Digital download – nothing is shipped.</div>""",
}

from playwright.sync_api import sync_playwright  # noqa: E402

with sync_playwright() as p:
    br = p.chromium.launch(channel="chrome")
    pg = br.new_page(viewport={"width": 2000, "height": 2000})
    for name, body in SHOTS.items():
        f = OUT / f"{name}.html"
        f.write_text(f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head>'
                     f'<body><div class="wrap">{body}</div></body></html>', encoding="utf-8")
        pg.goto(f.as_uri())
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(500)
        pg.screenshot(path=str(OUT / f"{name}.png"))
        print(OUT / f"{name}.png")
    br.close()
