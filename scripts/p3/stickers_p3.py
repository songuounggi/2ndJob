# -*- coding: utf-8 -*-
"""상품 3 스티커 -- "리소 인쇄 스탬프". 표지 "52" 의 청록·마젠타 판 어긋남을 시각 언어로. Prod 3 방 소유.

    python scripts/p3/stickers_p3.py            # -> output/prod3/stickers/<DRAFT>/sample_sheet.png (시안)

디자인은 사용자 확정 전 시안. 색은 핸드오프(종이·잉크·청록·마젠타 판), 글꼴 Source Serif 4.
내용은 플래너 장치에 맞춘다: 실험 판정, KEEP/DROP, Brain weather 5단계, 배터리, 시간맹, 시간 링크, 작은 승리, 공휴일 빈칸.
이미 있는 시안 폴더면 멈춘다(덮어쓰지 않는다).
"""
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[2]
DRAFT = "draft-v0.3"   # v0.2: 색 조합 CSS 중괄호가 두 겹이라 통째로 무시됐다 / v0.1: 바탕이 종이색 하나 -> 핸드오프 색 전부로 색 조합(사용자)
OUT = ROOT / "output" / "prod3" / "stickers" / DRAFT
if OUT.exists():
    raise SystemExit(f"{OUT} 는 이미 있다. 덮어쓰지 않는다 -- DRAFT 를 올릴 것.")
OUT.mkdir(parents=True)

PAPER, INK, N700, CYAN, CYAN7 = "#f8f4f4", "#201e1d", "#605d5d", "#0088b0", "#006786"
MAG = "rgba(214,0,108,.55)"
PLATE = "2.5px 2px 0 var(--plate)"
# 색 조합: 핸드오프 팔레트만 (종이·잉크·청록 3단·마젠타 판·회색). 이름 -> (바탕, 글자, 어긋난 판)
WAYS = {
    "paper":   ("#f8f4f4", "#201e1d", "rgba(214,0,108,.55)"),
    "cyan":    ("#0088b0", "#f8f4f4", "rgba(32,30,29,.55)"),
    "deep":    ("#006786", "#f8f4f4", "rgba(214,0,108,.75)"),
    "mist":    ("#95c9d9", "#201e1d", "rgba(214,0,108,.55)"),
    "ink":     ("#201e1d", "#f8f4f4", "rgba(0,136,176,.9)"),
    "blush":   ("#efc9d7", "#201e1d", "rgba(0,136,176,.6)"),     # 마젠타 판을 종이 위에 옅게 -- 표지 판색
    "stone":   ("#d7d3d3", "#201e1d", "rgba(214,0,108,.55)"),
}


def plate_svg(inner, w, h, off=3):
    """같은 도형을 마젠타로 한 번, 잉크/청록으로 한 번 -- 판이 어긋난 인쇄"""
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">'
            f'<g transform="translate({off},{off * .7})" style="opacity:.6;stroke:var(--plate);color:var(--plate)" '
            f'fill="none">{inner}</g>'
            f'<g stroke="currentColor" fill="none">{inner}</g></svg>')


# ---- 아이콘 (선 굵기 6, 둥근 끝) ----
CHECK = '<path d="M14 34l13 13 27-30" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>'
TILDE = '<path d="M12 36c8-12 16-12 24 0s16 12 24 0" stroke-width="7" stroke-linecap="round"/>'
CROSS = '<path d="M18 18l32 32M50 18l-32 32" stroke-width="7" stroke-linecap="round"/>'
SUN = ('<circle cx="40" cy="40" r="14" stroke-width="6"/>' +
       "".join(f'<path d="M40 {40-26}v-8" stroke-width="6" stroke-linecap="round" transform="rotate({a} 40 40)"/>' for a in range(0, 360, 45)))
CLOUD = '<path d="M22 56h36a13 13 0 0 0 0-26 18 18 0 0 0-34-4 14 14 0 0 0-2 30z" stroke-width="6" stroke-linejoin="round"/>'
PART = ('<circle cx="30" cy="28" r="11" stroke-width="6"/>'
        '<path d="M26 60h32a11 11 0 0 0 0-22 16 16 0 0 0-30-3 12 12 0 0 0-2 25z" stroke-width="6" stroke-linejoin="round" fill="#f8f4f4"/>')
RAIN = CLOUD.replace("56h36", "46h36").replace("0-2 30z", "0-2 30z") + ''.join(
    f'<path d="M{x} 62l-4 10" stroke-width="5" stroke-linecap="round"/>' for x in (30, 44, 58))
STORM = RAIN + '<path d="M42 58l-8 12h10l-6 10" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'


def battery(n):
    bars = "".join(f'<rect x="{12 + i * 11}" y="22" width="7" height="24" rx="1.5" fill="currentColor" stroke="none"/>' for i in range(n))
    return f'<rect x="6" y="16" width="62" height="36" rx="7" stroke-width="5"/><path d="M72 28v12" stroke-width="6" stroke-linecap="round"/>{bars}'


ENVELOPE = ('<rect x="8" y="16" width="72" height="48" rx="5" stroke-width="5"/>'
            '<path d="M10 20l34 26 34-26" stroke-width="5" stroke-linejoin="round"/>')
CLOCK = ('<circle cx="40" cy="40" r="28" stroke-width="6"/>'
         '<path d="M40 24v16l11 8" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>')

CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=block');
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:2000px;height:2000px;background:#e6e2de;font-family:'Source Serif 4',Georgia,serif;color:{INK};
  padding:110px 120px;overflow:hidden}}
h1{{font-size:64px;font-weight:600}} .sub{{font-size:30px;font-style:italic;color:{N700};margin:8px 0 46px}}
.grid{{display:flex;flex-wrap:wrap;gap:40px 44px;align-items:center}}
.st{{background:var(--bg);--bg:{PAPER};--plate:rgba(214,0,108,.55);border-radius:26px;padding:20px 28px;display:inline-flex;align-items:center;gap:16px;
  box-shadow:0 0 0 10px #fff,0 14px 24px rgba(0,0,0,.18);color:var(--fg,{INK})}}
.st.round{{border-radius:50%;width:210px;height:210px;flex-direction:column;justify-content:center;gap:4px;padding:0}}
.st.cy{{--fg:{CYAN7}}} .st.mg{{--fg:#b0005a}}
"""
CSS += "".join(f".w-{k}{{--bg:{b};--fg:{f}!important;--plate:{pl}}}" for k, (b, f, pl) in WAYS.items())
CSS += f"""
.t{{font-size:34px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;text-shadow:{PLATE}}}
.t.sm{{font-size:24px}} .it{{font-style:italic;font-size:26px;color:{N700};text-transform:none;letter-spacing:0;text-shadow:none}}
.blank{{display:inline-block;width:120px;border-bottom:3px solid currentColor;height:30px;vertical-align:bottom}}
.tag{{border-radius:12px;clip-path:polygon(22px 0,100% 0,100% 100%,22px 100%,0 50%);padding-left:40px}}
.wx{{flex-direction:column;gap:2px;padding:18px 22px}}
.sec{{width:100%;font-size:24px;letter-spacing:.14em;text-transform:uppercase;color:{CYAN7};margin:18px 0 -14px}}
"""


def st(icon, text, cls="", size=(80, 80), small=False):
    ic = plate_svg(icon, *size) if icon else ""
    return f'<div class="st {cls}">{ic}<span class="t{" sm" if small else ""}">{text}</span></div>'


WX = [(STORM, "Rough"), (RAIN, "Low"), (CLOUD, "Okay"), (PART, "Good"), (SUN, "Great")]
BODY = f"""
<h1>The ADHD Year · Sticker kit</h1><div class="sub">Riso-stamp stickers made for the planner's own pages.</div>
<div class="grid">
  <div class="sec">Friday verdicts · 52 experiments</div>
  <div class="st round cy">{plate_svg(CHECK, 68, 68)}<span class="t sm">Helped</span></div>
  <div class="st round">{plate_svg(TILDE, 68, 68)}<span class="t sm">Sort of</span></div>
  <div class="st round mg">{plate_svg(CROSS, 68, 68)}<span class="t sm">Not for me</span></div>
  <div class="st tag cy"><span class="t">Keep</span></div>
  <div class="st tag mg"><span class="t">Drop</span></div>
  <div class="sec">Brain weather</div>
  {"".join(f'<div class="st wx">{plate_svg(i, 80, 80)}<span class="t sm">{t}</span></div>' for i, t in WX)}
  <div class="sec">Energy · time · time links</div>
  {"".join(f'<div class="st cy" style="padding:14px 18px">{plate_svg(battery(n), 80, 68)}</div>' for n in (1, 3, 5))}
  {st(CLOCK, "+15 buffer", "cy", small=True)}
  <div class="st"><span class="t sm">Leave at <span class="blank"></span></span></div>
  {st(ENVELOPE, "To future me", "", (88, 80), small=True)}
  <div class="st round mg" style="width:190px;height:190px"><span class="t sm">Arrived</span><span class="it">from past you</span></div>
  <div class="sec">Small wins · works anywhere</div>
  <div class="st cy"><span class="t">Did the thing</span></div>
  <div class="st"><span class="t">Started counts</span></div>
  <div class="st"><span class="t sm">Public holiday <span class="blank"></span></span></div>
  <div class="st"><span class="t sm">Day off</span></div>
</div>"""

PICK = [
    lambda w: f'<div class="st round w-{w}">{plate_svg(CHECK, 68, 68)}<span class="t sm">Helped</span></div>',
    lambda w: f'<div class="st wx w-{w}">{plate_svg(SUN, 80, 80)}<span class="t sm">Great</span></div>',
    lambda w: f'<div class="st w-{w}" style="padding:14px 18px">{plate_svg(battery(3), 80, 68)}</div>',
    lambda w: f'<div class="st w-{w}">{plate_svg(ENVELOPE, 88, 80)}<span class="t sm">To future me</span></div>',
    lambda w: f'<div class="st w-{w}"><span class="t">Did the thing</span></div>',
    lambda w: f'<div class="st tag w-{w}"><span class="t">Keep</span></div>',
]
BODY = (f'<h1>Sticker colorways</h1><div class="sub">Every color comes from the planner itself: paper, ink, three cyans, the magenta plate, stone.</div>'
        + "".join(f'<div class="sec">{k}</div><div class="grid">' + "".join(f(k) for f in PICK) + "</div>" for k in WAYS))
CSS += ".sec{margin:18px 0 14px!important}.grid{gap:26px 30px;zoom:.78}h1{font-size:54px}.sub{margin-bottom:20px}"

from playwright.sync_api import sync_playwright  # noqa: E402

html = OUT / "sample_sheet.html"
html.write_text(f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{BODY}</body></html>',
                encoding="utf-8")
with sync_playwright() as p:
    br = p.chromium.launch(channel="chrome")
    pg = br.new_page(viewport={"width": 2000, "height": 2000})
    pg.goto(html.as_uri())
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(500)
    pg.screenshot(path=str(OUT / "sample_sheet.png"))
    br.close()
print(OUT / "sample_sheet.png")
