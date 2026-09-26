# -*- coding: utf-8 -*-
"""상품 3 설치 안내서 (Goodnotes 중심) -- 구매자에게 가는 글. Prod 3 방 소유.

    python scripts/p3/guide_p3.py      # -> output/prod3/guide/<DRAFT>/Setup-Guide.pdf + 미리보기 PNG

문장은 공식 도움말에서 확인된 것만(2026-09-26 조사, 출처는 product3-dated.md "설치 안내서 근거").
미확인(Notability 링크, 투명 PNG 유지, Etsy 모바일 정확한 탭 경로)은 약속하지 않는다.
이미 있는 폴더면 멈춘다(덮어쓰지 않는다).
"""
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "p3"))
DRAFT = "draft-v0.1"
OUT = ROOT / "output" / "prod3" / "guide" / DRAFT
if OUT.exists():
    raise SystemExit(f"{OUT} 는 이미 있다. 덮어쓰지 않는다 -- DRAFT 를 올릴 것.")
OUT.mkdir(parents=True)

PAPER, INK, N300, N400, N700, CYAN, CYAN7 = "#f8f4f4", "#201e1d", "#d7d3d3", "#bab6b6", "#605d5d", "#0088b0", "#006786"
PLATE = "2.5px 2px 0 rgba(214,0,108,.45)"

CSS = f"""
@page{{size:768px 1024px;margin:0}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Source Serif 4',Georgia,serif;color:{INK};background:{PAPER}}}
section{{width:768px;height:1024px;padding:78px 76px 60px;display:flex;flex-direction:column;page-break-after:always;background:{PAPER}}}
.eb{{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:{N700}}}
h1{{font-size:46px;font-weight:600;line-height:1.05;margin:10px 0 8px}}
h1.big{{font-size:78px;text-shadow:{PLATE}}}
.sub{{font-size:18px;font-style:italic;color:{N700};margin-bottom:30px}}
.step{{display:flex;gap:18px;padding:16px 0;border-bottom:1px solid {N300}}}
.n{{flex:none;width:40px;height:40px;border-radius:50%;background:{CYAN7};color:#fff;font-size:20px;font-weight:600;
  display:flex;align-items:center;justify-content:center;text-shadow:{PLATE}}}
.step p{{font-size:17px;line-height:1.5}} .step b{{font-weight:600}}
.ui{{display:inline-block;border:1px solid {N400};border-radius:999px;padding:0 10px;font-size:14px;line-height:22px;margin:0 1px;white-space:nowrap}}
.tip{{margin-top:22px;border-left:3px solid {CYAN};padding:10px 16px;font-size:16px;line-height:1.5;background:#eef6f9}}
.warn{{margin-top:22px;border-left:3px solid #d6006c;padding:10px 16px;font-size:16px;line-height:1.5;background:#fbeef3}}
.lab{{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:{CYAN7};margin:24px 0 8px}}
table{{border-collapse:collapse;width:100%;font-size:16px}} td{{padding:10px 8px;border-bottom:1px solid {N300}}}
td.k{{width:40%;color:{N700}}}
.foot{{margin-top:auto;font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:{N700};display:flex;justify-content:space-between}}
"""


def ui(t):
    return f'<span class="ui">{t}</span>'


def step(n, html):
    return f'<div class="step"><div class="n">{n}</div><p>{html}</p></div>'


def sec(eb, title, body, page, sub="", big=False):
    return (f'<section><div class="eb">{eb}</div><h1{" class=big" if big else ""}>{title}</h1>'
            f'{f"<div class=sub>{sub}</div>" if sub else ""}{body}'
            f'<div class="foot"><span>The ADHD Year · Setup guide</span><span>{page}</span></div></section>')


PAGES = [
    sec("Start here", "The ADHD<br>Year", """
      <div class="lab">In your download</div>
      <table>
        <tr><td class="k">4 planners</td><td>2026 and 2027, each in a Monday-start and a Sunday-start version. Pick the one that matches your week.</td></tr>
        <tr><td class="k">Sticker kit</td><td>A ZIP of transparent PNG stickers made for the planner's own pages.</td></tr>
        <tr><td class="k">This guide</td><td>Four short steps. About five minutes.</td></tr>
      </table>
      <div class="lab">The four steps</div>
      """ + step(1, "<b>Download</b> the files from Etsy in Safari.")
        + step(2, "<b>Open</b> your planner in Goodnotes.")
        + step(3, "<b>Tap</b> the tabs and links to move around.")
        + step(4, "<b>Add</b> the stickers to Goodnotes."),
        "1 / 5", "Setup guide for Goodnotes on iPad.", big=True),
    sec("Step 1", "Download from Etsy", step(1, f"On your iPad, open <b>Safari</b> and sign in at etsy.com. <i>The Etsy app can't download digital files.</i>")
        + step(2, f"Go to {ui('Your account')} → {ui('Purchases')}, then tap {ui('Download Files')} next to this order.")
        + step(3, "Save the files. The sticker kit arrives as a <b>ZIP</b>.")
        + step(4, f"To open the ZIP, go to the <b>Files</b> app and tap the ZIP. A folder with the stickers appears next to it.")
        + '<div class="tip">No limit on downloads — you can come back to Purchases and download again any time.</div>',
        "2 / 5", "Your files are on the order's download page."),
    sec("Step 2", "Open it in Goodnotes", '<div class="lab">From the Files app</div>'
        + step(1, f"Find the planner PDF, tap {ui('Share')} and choose {ui('Open in Goodnotes')}.")
        + step(2, f"Choose the {ui('New Document')} tab, pick a folder, then tap {ui('Import to…')}")
        + '<div class="lab">Or from inside Goodnotes</div>'
        + step(1, f"In the Documents tab, tap {ui('+ New')} → {ui('Import')}.")
        + step(2, f"Select the planner PDF and tap {ui('Open')}.")
        + '<div class="warn"><b>Goodnotes free plan:</b> it imports files up to 5 MB, and each planner is about 7.7 MB. '
          'You need a Goodnotes subscription, or another PDF note app.</div>',
        "3 / 5", "Each planner becomes one notebook."),
    sec("Step 3", "Tap to move around", step(1, "<b>Ten tabs</b> run down the right side of every page: Index, SOS, Year, Month, Week, Focus, Feel, Body, Life, Notes. Tap one to jump there.")
        + step(2, f"<b>Any day in two taps:</b> tap {ui('Year')}, then tap the date.")
        + step(3, f"On a daily page, {ui('Tomorrow →')} and {ui('From yesterday ←')} walk you through the days. A note to future you links to the day it arrives.")
        + step(4, f"Stuck? Tap {ui('SOS')} and pick what is happening.")
        + '<div class="tip"><b>If a tap draws a line instead of opening the link,</b> switch to <b>Read Only Mode</b> '
          '(the icon in the Nav Bar), or touch and hold the link and choose <b>Open Link</b>. Switch back to write.</div>',
        "4 / 5", "Every link is a real PDF link."),
    sec("Step 4", "Add the stickers", step(1, f"In a notebook, choose {ui('Elements')} from the toolbar.")
        + step(2, "Scroll to the end of the collection list and tap the <b>+</b>.")
        + step(3, f"Give the collection a name, then choose {ui('Import from…')} and select the sticker PNGs from the unzipped folder.")
        + step(4, f"Tap {ui('Create')}. Now tap a sticker, or drag it onto the page.")
        + '<div class="lab">Need help?</div>'
          '<p style="font-size:17px;line-height:1.5">Message me on Etsy. If anything is wrong with a file, I will fix it.</p>'
        + '<p style="font-size:13px;color:#605d5d;margin-top:18px;line-height:1.5">Using Notability or another app? Import the PDF the same way '
          '(in Notability: +New → Import). This planner is a set of writing prompts, not medical advice.</p>',
        "5 / 5", "Your stickers, in your own collection."),
]

html = OUT / "guide.html"
html.write_text('<!DOCTYPE html><html><head><meta charset="utf-8">'
                '<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=block" rel="stylesheet">'
                f'<style>{CSS}</style></head><body>{"".join(PAGES)}</body></html>', encoding="utf-8")

import editions_build as E  # noqa: E402  (정적 폰트 UA -- 가변 폰트가 Type3 로 들어가지 않게)
from playwright.sync_api import sync_playwright  # noqa: E402
import pypdfium2 as pdfium  # noqa: E402

pdf = OUT / "ADHD-Year-Planner-Setup-Guide.pdf"
with sync_playwright() as p:
    br = p.chromium.launch(channel="chrome")
    pg = br.new_context(user_agent=E.STATIC_FONT_UA).new_page()
    pg.goto(html.as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(800)
    pg.pdf(path=str(pdf), width="768px", height="1024px", print_background=True, prefer_css_page_size=True)
    br.close()
with open(pdf, "rb") as fh:
    d = pdfium.PdfDocument(fh.read())
for i in range(len(d)):
    d[i].render(scale=1.3).to_pil().save(OUT / f"page_{i + 1}.png")
print(pdf, len(d), "pages", pdf.stat().st_size, "B")
d.close()
