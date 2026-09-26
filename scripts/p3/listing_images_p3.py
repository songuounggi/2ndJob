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
DRAFT = "draft-v0.13"   # v0.11: 07 만 라벨을 06 처럼 청록 배경 + 흰 글자, 기울이지 않음(사용자). 08 은 그대로 (v0.12 는 08 까지 바꾸다 간격 검사에서 멈춤) / v0.10: 07 BRAIN WEATHER 배지가 REVIEW 배지에 붙었다 -> 배지 글자 22px / v0.9: 07·08 배지가 페이지 어긋남을 따라 높이가 제각각 -> 한 줄로 / v0.8: 07·08 페이지가 작고 아래가 비었다 -> 크게 겹쳐 펼침 / v0.7: 10장으로(사용자: 기존 두 상품 10장) -- 07 한 달, 08 12월, 09 2탭, 10 어디서나 / v0.6: 안전 영역 검사가 06 마지막 배지(오른쪽 1754px)에서 멈춤 -> 배지를 표지 안쪽으로 (v0.6 폴더는 01-05 만 있다) / v0.5: 배지 5도, 안전 영역(글자가 왼쪽 120px 에서 시작 -> 검색 목록에서 잘림) / v0.4: 15도는 너무 기울었다 -> 8도(사용자) / v0.3: 배지 시계방향 15도(사용자) / v0.1: 05 썸네일 3줄이 아래로 잘림, 06 아래가 비었다 / v0.2: 06 표지 네 장이 멀리서 구분 안 됨 -> 배지
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
        "rsd", "budget", "dopamine", "mailbox", "playbook", "mp3", "mr3", "yearreview", "myhol",
        "note1", "note2", "note3", "note4"]
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
.wrap{{position:absolute;inset:0;padding:250px 260px;display:flex;flex-direction:column}}   /* 안전 영역: Etsy 검색은 양옆 ~140px 을 자르고 4:3 자리는 가운데만 -- product2-student.md 목업 안전 영역 */
.k{{font-size:34px;letter-spacing:.14em;text-transform:uppercase;color:{CYAN}}}
h1{{font-size:104px;font-weight:600;line-height:1.02;margin:22px 0 26px;letter-spacing:-.01em}}
p.s{{font-size:42px;font-style:italic;color:{N700};line-height:1.3}}
.row{{flex:1;min-height:0;display:flex;gap:50px;align-items:flex-end;justify-content:center;margin-top:50px}}
.pg{{height:100%;max-height:1000px;max-width:48%;object-fit:contain;box-shadow:0 30px 60px rgba(0,0,0,.18),0 4px 10px rgba(0,0,0,.08)}}
.pg.t{{transform:rotate(-2deg)}} .pg.u{{transform:rotate(1.5deg)}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:30px;margin-top:50px}}
.grid img{{width:100%;box-shadow:0 14px 30px rgba(0,0,0,.15)}}
.list{{font-size:38px;line-height:1.55;margin-top:34px}}
.list b{{color:{CYAN};font-weight:600}}
.pill{{display:inline-block;border:2px solid {N700};border-radius:999px;padding:8px 28px;font-size:34px;margin:0 14px 16px 0}}
.cv{{position:relative}}.cv img{{width:100%;box-shadow:0 14px 30px rgba(0,0,0,.15)}}
.bdg{{position:absolute;top:-22px;right:8px;border-radius:22px;padding:12px 20px 10px;text-align:center;color:#fff;box-shadow:0 8px 18px rgba(0,0,0,.22);transform:rotate(5deg)}}
.bdg b{{display:block;font-size:52px;font-weight:600;line-height:1}}.bdg span{{display:block;font-size:24px;margin-top:6px;letter-spacing:.04em}}
.bdg.mon{{background:{CYAN}}}.bdg.sun{{background:{INK}}}
.trio{{flex:1;min-height:0;display:flex;gap:34px;justify-content:center;align-items:flex-start;margin-top:50px}}
.fig{{flex:1;min-width:0;display:flex;flex-direction:column;align-items:center}}
.fig img{{width:100%;box-shadow:0 14px 30px rgba(0,0,0,.15)}}
.cap{{margin-top:22px;font-size:30px;letter-spacing:.1em;text-transform:uppercase;color:{N700};text-align:center}}
.cap b{{color:{CYAN};font-weight:600}}
.arrow{{flex:none;align-self:center;display:flex;flex-direction:column;align-items:center;gap:14px;color:{CYAN};font-size:30px;letter-spacing:.08em;text-transform:uppercase}}
.steps{{display:flex;gap:22px;margin-top:34px}}.step{{display:flex;align-items:center;gap:16px;font-size:38px}}
.step i{{font-style:normal;width:58px;height:58px;border-radius:50%;background:{CYAN};color:#fff;display:flex;align-items:center;justify-content:center;font-size:32px}}
.fan{{position:relative;flex:1;min-height:0;margin-top:44px}}
.fan .fp{{position:absolute;top:0;box-shadow:-10px 18px 40px rgba(0,0,0,.20)}}
.fan .fp img{{display:block;height:100%}}
.fan .tag{{position:absolute;background:{PAPER};border:2px solid {N700};border-radius:999px;padding:5px 16px;font-size:22px;letter-spacing:.08em;text-transform:uppercase;color:{INK};white-space:nowrap}}
.fan .tag.solid{{background:{CYAN};border:0;border-radius:16px;padding:7px 16px;color:#fff;box-shadow:0 8px 18px rgba(0,0,0,.22)}}
.notes{{display:grid;grid-template-columns:1fr 1fr;gap:26px}}
.foot{{font-size:34px;color:{N700};margin-top:40px;letter-spacing:.04em}}
"""


def img(k, cls="pg"):
    return f'<img class="{cls}" src="_pages/{k}.png">'


def fan(items, h, step, drop, tag=""):
    """페이지를 크게 겹쳐 펼친다 -- 뒤 페이지가 위에 온다. h = 페이지 높이(px), step = 가로 간격, drop = 세로 어긋남"""
    w = round(h * 3 / 4)
    # 배지는 페이지 안이 아니라 펼침 전체 기준으로 -- 모두 같은 높이(첫 페이지 바닥 위 20px)에 둔다
    out = "".join(f'<div class="fp" style="left:{i * step}px;top:{i * drop}px;height:{h}px;width:{w}px;z-index:{i}">'
                  f'<img src="_pages/{k}.png"></div>' for i, (k, c) in enumerate(items))
    out += "".join(f'<span class="tag {tag}" style="left:{i * step + 18}px;top:{h - 72}px;z-index:{len(items) + 1}">{c}</span>'
                   for i, (k, c) in enumerate(items))
    return f'<div class="fan" style="width:{w + step * (len(items) - 1)}px">{out}</div>'


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
    "07_month": f"""<div class="k">Every month · four pages that work together</div>
      <h1>Plan it. Track it.<br>Look back.</h1>
      <p class="s">A calendar, a plan, a brain weather tracker and a review – linked to each other.</p>
      {fan([("m3", "Calendar"), ("mp3", "Plan"), ("bw3", "Brain weather"), ("mr3", "Review")], 900, 268, 18, "solid")}""",
    "08_december": f"""<div class="k">By December</div>
      <h1>A user manual for<br>your own brain.</h1>
      <p class="s">Keep the experiments that worked. Notes you wrote to future you wait in a year-end mailbox.</p>
      {fan([("playbook", "My ADHD playbook"), ("yearreview", "Year review"), ("mailbox", "Year-end mailbox")], 880, 372, 22)}""",
    "09_two_taps": f"""<div class="k">Hyperlinked · ten tabs on every page</div>
      <h1>Any day of the year,<br>two taps away.</h1>
      <div class="steps"><div class="step"><i>1</i>Tap YEAR</div><div class="step"><i>2</i>Tap the date</div></div>
      <div class="trio"><div class="fig">{img("year", "")}<div class="cap">Year at a glance</div></div>
        <div class="arrow"><svg width="150" height="60" viewBox="0 0 150 60"><path d="M4 30H136M112 8l26 22-26 22" fill="none" stroke="currentColor" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></svg><span>tap</span></div>
        <div class="fig">{img("d3-15", "")}<div class="cap">That day's page</div></div></div>""",
    "10_anywhere": f"""<div class="k">Works anywhere</div>
      <h1>No other country's<br>holidays in your way.</h1>
      <p class="s">Only dates shared worldwide are printed. Add your own on the My holidays page.</p>
      <div class="trio"><div class="fig">{img("myhol", "")}<div class="cap">My holidays</div></div>
        <div class="fig"><div class="notes">{"".join(img(k, "") for k in ["note1", "note2", "note3", "note4"])}</div>
        <div class="cap">Dot grid · Ruled · Plain · Grid</div></div></div>""",
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
        out_of = pg.evaluate("""() => [...document.querySelectorAll('.k,h1,p.s,.pill,.list,.foot,.bdg,.cap,.step,.arrow,.tag,.fp')].map(e => {
            const r = e.getBoundingClientRect();
            return (r.left < 260 || r.right > 1740 || r.top < 250 || r.bottom > 1750) ? e.textContent.trim().slice(0, 30) + ' ' + JSON.stringify([r.left|0, r.top|0, r.right|0, r.bottom|0]) : null;
        }).filter(Boolean)""")
        tags = pg.evaluate("""() => [...document.querySelectorAll('.fan .tag')].map(e => { const r = e.getBoundingClientRect(); return [r.left, r.right]; })""")
        close = [i for i in range(1, len(tags)) if tags[i][0] - tags[i - 1][1] < 16]
        if close:
            raise SystemExit(f"{name}: 배지 사이가 16px 보다 좁다 {close}")
        if out_of:
            raise SystemExit(f"{name}: 안전 영역(가로 260-1740, 세로 250-1750) 밖 글자 {out_of}")
        pg.screenshot(path=str(OUT / f"{name}.png"))
        print(OUT / f"{name}.png")
    br.close()
