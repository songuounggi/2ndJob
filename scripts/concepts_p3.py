# -*- coding: utf-8 -*-
"""상품 3 새 콘셉트 4종 시안 (저장소 밖). 일간 + 월간 각 1장."""
import math, os, random, subprocess, calendar, datetime as dt

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "preview", "concepts_p3")
os.makedirs(OUT, exist_ok=True)
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
Y, M, D = 2027, 3, 9
WEEKS = calendar.Calendar(0).monthdayscalendar(Y, M)


def pt(x):
    return f"{x:.2f}"


def polar(cx, cy, r, a):
    a = math.radians(a)
    return cx + r * math.sin(a), cy - r * math.cos(a)


def seg(cx, cy, ri, ro, a0, a1):
    x0, y0 = polar(cx, cy, ro, a0); x1, y1 = polar(cx, cy, ro, a1)
    x2, y2 = polar(cx, cy, ri, a1); x3, y3 = polar(cx, cy, ri, a0)
    return (f"M{pt(x0)} {pt(y0)}A{ro} {ro} 0 0 1 {pt(x1)} {pt(y1)}"
            f"L{pt(x2)} {pt(y2)}A{ri} {ri} 0 0 0 {pt(x3)} {pt(y3)}Z")


def doc(css, fonts, pages):
    body = "".join(f'<section class="pg">{p}</section>' for p in pages)
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?{fonts}&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
@page{{size:612pt 792pt;margin:0}}
.pg{{width:612pt;height:792pt;position:relative;overflow:hidden;page-break-after:always}}
svg{{display:block}}
{css}</style></head><body>{body}</body></html>"""


# =================================================================== A ==
# CLOCKWISE -- 시간맹(time blindness)을 겨냥한 24시간 원형 다이얼
A_CSS = """
body{font-family:'Inter',sans-serif;color:#22303A}
.pg{background:#F6F4EF}
.rail{position:absolute;left:0;top:0;bottom:0;width:40pt;background:#22303A;
  display:flex;flex-direction:column;padding:14pt 0}
.rail a{flex:1;display:flex;align-items:center;justify-content:center}
.rail span{writing-mode:vertical-rl;transform:rotate(180deg);font:600 6.5pt 'Inter';
  letter-spacing:.16em;color:#8FA3B0}
.rail a.on{background:#F6F4EF}.rail a.on span{color:#22303A;font-weight:800}
.mstrip{position:absolute;right:0;top:0;bottom:0;width:26pt;display:flex;flex-direction:column;
  padding:14pt 0;border-left:1pt solid #DDD8CE}
.mstrip a{flex:1;display:flex;align-items:center;justify-content:center;font:700 5.8pt 'Inter';
  color:#9AA3A9;letter-spacing:.08em}
.mstrip a.on{color:#fff;background:#2F8F83}
.c{position:absolute;left:62pt;right:46pt;top:34pt;bottom:30pt;display:flex;flex-direction:column}
.eb{font:700 7.5pt 'Inter';letter-spacing:.18em;color:#2F8F83}
.big{font:700 40pt 'Outfit';letter-spacing:-.02em;line-height:1}
.big small{font:500 16pt 'Outfit';color:#7B868D;margin-left:8pt}
.box{background:#fff;border-radius:10pt;padding:12pt 14pt;border:.6pt solid #E3DED4}
.lab{font:800 7pt 'Inter';letter-spacing:.14em;color:#7B868D;margin-bottom:8pt}
.ln{height:20pt;border-bottom:.8pt solid #E2DDD3}
"""


def a_rail(on):
    tabs = ["INDEX", "YEAR", "MONTH", "WEEK", "FOCUS", "FEEL", "HABITS", "HEALTH", "LIFE", "NOTES"]
    r = "".join(f'<a class="{"on" if t == on else ""}"><span>{t}</span></a>' for t in tabs)
    ms = "".join(f'<a class="{"on" if i == M else ""}">{calendar.month_abbr[i].upper()}</a>'
                 for i in range(1, 13))
    return f'<nav class="rail">{r}</nav><nav class="mstrip">{ms}</nav>'


def a_dial(cx, cy, R):
    out = []
    ro, rm, ri = R, R - 34, R - 68           # 바깥 = 실제, 안 = 계획
    for h in range(24):
        a0, a1 = h * 15, (h + 1) * 15
        night = h < 6 or h >= 22
        out.append(f'<path d="{seg(cx, cy, rm + 2, ro, a0, a1)}" fill="{"#EDEAE3" if night else "#fff"}" stroke="#D5D0C6" stroke-width=".7"/>')
        out.append(f'<path d="{seg(cx, cy, ri, rm - 2, a0, a1)}" fill="{"#E4EFEC" if night else "#fff"}" stroke="#C9DCD7" stroke-width=".7"/>')
    for h in range(24):
        x, y = polar(cx, cy, R + 11, h * 15)
        lab = {0: "12a", 6: "6a", 12: "noon", 18: "6p"}.get(h, str(h % 12 or 12))
        w = "800" if h % 6 == 0 else "500"
        col = "#22303A" if h % 6 == 0 else "#9AA3A9"
        out.append(f'<text x="{pt(x)}" y="{pt(y + 2.5)}" text-anchor="middle" font-family="Inter" '
                   f'font-size="{7 if h % 6 == 0 else 6}" font-weight="{w}" fill="{col}">{lab}</text>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{ri - 6}" fill="#22303A"/>')
    out.append(f'<text x="{cx}" y="{cy - 22}" text-anchor="middle" font-family="Inter" font-size="6.5" '
               f'font-weight="800" letter-spacing="1.4" fill="#7FC4B8">JUST ONE THING</text>')
    for k in range(3):
        out.append(f'<line x1="{cx - 48}" x2="{cx + 48}" y1="{cy - 2 + k * 16}" y2="{cy - 2 + k * 16}" stroke="#4A5A66" stroke-width=".8"/>')
    # 범례 호
    x, y = polar(cx, cy, ro - 17, 97)
    out.append(f'<text x="{pt(x)}" y="{pt(y)}" font-family="Inter" font-size="5.2" font-weight="800" fill="#B0A99C" letter-spacing="1">ACTUAL</text>')
    x, y = polar(cx, cy, rm - 19, 99)
    out.append(f'<text x="{pt(x)}" y="{pt(y)}" font-family="Inter" font-size="5.2" font-weight="800" fill="#2F8F83" letter-spacing="1">PLAN</text>')
    return "".join(out)


def a_daily():
    W = 504
    dial = a_dial(W / 2, 176, 150)
    est = "".join('<div style="display:flex;gap:8pt;height:22pt;border-bottom:.8pt solid #E2DDD3;align-items:end">'
                  '<div style="flex:2"></div><div style="flex:1;border-left:.8pt solid #E2DDD3"></div>'
                  '<div style="flex:1;border-left:.8pt solid #E2DDD3"></div></div>' for _ in range(4))
    batt = "".join(f'<div style="flex:1;height:22pt;border:1.2pt solid #22303A;border-radius:3pt"></div>' for _ in range(5))
    return a_rail("MONTH") + f"""<div class="c">
  <div style="display:flex;align-items:end;justify-content:space-between">
    <div><div class="eb">WEEK 11 &middot; 2027</div><div class="big" style="margin-top:6pt">Tue 9<small>March</small></div></div>
    <div style="font:600 8pt 'Inter';color:#7B868D;text-align:right;line-height:1.5">Plan inside.<br>What happened outside.</div>
  </div>
  <svg viewBox="0 0 {W} 350" width="{W}pt" height="350pt" style="margin-top:4pt">{dial}</svg>
  <div style="display:flex;gap:10pt;flex:1;margin-top:6pt">
    <div class="box" style="flex:1.5"><div class="lab">GUESS vs ACTUAL</div>
      <div style="display:flex;font:700 6pt 'Inter';color:#9AA3A9;letter-spacing:.1em">
        <div style="flex:2">TASK</div><div style="flex:1;padding-left:6pt">GUESS</div><div style="flex:1;padding-left:6pt">TOOK</div></div>{est}</div>
    <div style="flex:1;display:flex;flex-direction:column;gap:10pt">
      <div class="box"><div class="lab">ENERGY</div><div style="display:flex;gap:4pt">{batt}</div></div>
      <div class="box" style="flex:1"><div class="lab">MEDS &middot; WATER</div>
        <div style="display:flex;gap:5pt;flex-wrap:wrap">{''.join('<div style="width:13pt;height:13pt;border-radius:99pt;border:1.2pt solid #2F8F83"></div>' for _ in range(8))}</div></div>
    </div>
  </div></div>"""


def a_month():
    cells = ""
    for w in WEEKS:
        for i, d in enumerate(w):
            if not d:
                cells += '<div></div>'
                continue
            ring = "".join(f'<path d="{seg(20, 20, 11, 17, q * 90 + 2, q * 90 + 88)}" fill="none" stroke="#C9C3B8" stroke-width=".8"/>' for q in range(4))
            cells += (f'<div style="border-top:.8pt solid #DDD8CE;padding-top:5pt">'
                      f'<div style="font:700 9pt Outfit;color:{"#2F8F83" if i >= 5 else "#22303A"}">{d}</div>'
                      f'<svg viewBox="0 0 40 40" width="38pt" height="38pt" style="margin:4pt auto 0">{ring}</svg></div>')
    hd = "".join(f'<div style="font:800 6.5pt Inter;letter-spacing:.14em;color:#9AA3A9">{d}</div>'
                 for d in ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"])
    return a_rail("MONTH") + f"""<div class="c">
  <div class="eb">2027</div><div class="big" style="margin-top:6pt">March</div>
  <div style="font:500 8.5pt Inter;color:#7B868D;margin-top:6pt">Each ring is one day: morning, afternoon, evening, night. Shade how each part went.</div>
  <div style="display:grid;grid-template-columns:repeat(7,1fr);gap:8pt 8pt;margin-top:18pt">{hd}{cells}</div>
  <div style="display:flex;gap:10pt;margin-top:auto">
    <div class="box" style="flex:1"><div class="lab">THIS MONTH, ONE THING</div><div class="ln"></div><div class="ln"></div></div>
    <div class="box" style="flex:1"><div class="lab">WHAT ATE MY TIME</div><div class="ln"></div><div class="ln"></div></div>
  </div></div>"""


# =================================================================== B ==
# QUEST LOG -- 게임화. 할 일 = 퀘스트, 에너지 = HP, 보상 = 전리품
B_CSS = """
body{font-family:'Space Grotesk',sans-serif;color:#2B2A33}
.pg{background:#FBF3E4}
.px{font-family:'Silkscreen',monospace}
.panel{background:#fff;border:2pt solid #2B2A33;border-radius:6pt;position:relative;padding:10pt 12pt}
.sh{position:absolute;inset:0;transform:translate(4pt,4pt);background:#2B2A33;border-radius:6pt;z-index:-1}
.wrap{position:relative;z-index:0}
.tag{display:inline-block;font:700 7pt 'Silkscreen';letter-spacing:.06em;padding:3pt 7pt;
  border:1.6pt solid #2B2A33;border-radius:4pt;background:#F2B233}
.c{position:absolute;left:30pt;right:74pt;top:28pt;bottom:28pt;display:flex;flex-direction:column;gap:14pt}
.menu{position:absolute;right:14pt;top:28pt;bottom:28pt;width:46pt;display:flex;flex-direction:column;gap:6pt}
.menu a{flex:1;border:1.6pt solid #2B2A33;border-radius:5pt;background:#fff;display:flex;
  align-items:center;justify-content:center}
.menu span{writing-mode:vertical-rl;transform:rotate(180deg);font:700 6.5pt 'Silkscreen';letter-spacing:.08em}
.menu a.on{background:#3D7DD8;color:#fff;box-shadow:3pt 3pt 0 #2B2A33}
.row{display:flex;align-items:center;gap:8pt;height:24pt;border-bottom:1.2pt dashed #D8CFBE}
.cb{width:12pt;height:12pt;border:1.6pt solid #2B2A33;border-radius:2pt;flex:none}
.xp{font:700 6.5pt 'Silkscreen';padding:2pt 5pt;border-radius:3pt;flex:none}
"""


def b_menu(on):
    tabs = ["MAP", "YEAR", "MONTH", "WEEK", "QUESTS", "MIND", "HABITS", "HEALTH", "BASE", "NOTES"]
    return '<nav class="menu">' + "".join(
        f'<a class="{"on" if t == on else ""}"><span>{t}</span></a>' for t in tabs) + '</nav>'


def panel(inner, style="", bg="#fff"):
    return (f'<div class="wrap" style="{style}"><div class="sh"></div>'
            f'<div class="panel" style="background:{bg};height:100%">{inner}</div></div>')


HEART = ('<svg viewBox="0 0 16 14" width="15pt" height="13pt"><path d="M8 13 1.6 6.6A3.6 3.6 0 0 1 8 2.4a3.6 3.6 0 0 1 6.4 4.2Z" '
         'fill="{f}" stroke="#2B2A33" stroke-width="1.4"/></svg>')
FLASK = ('<svg viewBox="0 0 14 18" width="13pt" height="17pt"><path d="M5 1h4v5l4 9a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2l4-9Z" '
         'fill="#fff" stroke="#2B2A33" stroke-width="1.4"/><path d="M3 12h8" stroke="#2B2A33" stroke-width="1"/></svg>')
SWORD = ('<svg viewBox="0 0 30 30" width="26pt" height="26pt"><path d="M22 3h5v5L13 22l-5-5Z" fill="#E4574B" stroke="#2B2A33" stroke-width="1.8"/>'
         '<path d="m6 15 9 9M4 26l5-5" stroke="#2B2A33" stroke-width="2.4" stroke-linecap="round"/></svg>')
CHEST = ('<svg viewBox="0 0 30 24" width="26pt" height="21pt"><rect x="2" y="9" width="26" height="13" rx="2" fill="#F2B233" stroke="#2B2A33" stroke-width="1.8"/>'
         '<path d="M2 11V7a5 5 0 0 1 5-5h16a5 5 0 0 1 5 5v4" fill="#E0962A" stroke="#2B2A33" stroke-width="1.8"/>'
         '<rect x="12" y="9" width="6" height="6" fill="#fff" stroke="#2B2A33" stroke-width="1.5"/></svg>')


def b_daily():
    xpbar = "".join(f'<div style="flex:1;height:12pt;border:1.4pt solid #2B2A33;border-radius:2pt;'
                    f'background:{"#3FA66B" if i < 0 else "#fff"}"></div>' for i in range(10))
    hearts = "".join(HEART.format(f="#fff") for _ in range(5))
    xps = [10, 10, 25, 25, 50, 50]
    cols = {10: "#DCEBFA", 25: "#FDE9B8", 50: "#FBD3CE"}
    side = "".join(f'<div class="row"><div class="cb"></div><div style="flex:1"></div>'
                   f'<span class="xp" style="background:{cols[x]}">+{x} XP</span></div>' for x in xps)
    drops = "".join('<svg viewBox="0 0 12 16" width="10pt" height="14pt"><path d="M6 1C4 5 1 8 1 11a5 5 0 0 0 10 0c0-3-3-6-5-10Z" fill="#fff" stroke="#3D7DD8" stroke-width="1.4"/></svg>' for _ in range(8))
    return b_menu("QUESTS") + f"""<div class="c">
  <div style="display:flex;gap:12pt;align-items:stretch">
    {panel(f'<div class="px" style="font-size:7pt">TUESDAY</div><div style="font:700 30pt Space Grotesk;line-height:1">DAY 68</div><div class="px" style="font-size:7pt;color:#7A7465">MAR 9 2027 &middot; WEEK 11</div>', "flex:none;width:150pt", "#F2B233")}
    {panel(f'<div style="display:flex;justify-content:space-between"><span class="px" style="font-size:7pt">XP TODAY</span><span class="px" style="font-size:7pt">LV ___</span></div><div style="display:flex;gap:3pt;margin-top:6pt">{xpbar}</div><div style="display:flex;justify-content:space-between;align-items:center;margin-top:9pt"><span class="px" style="font-size:7pt">HP / ENERGY</span><div style="display:flex;gap:4pt">{hearts}</div></div>', "flex:1")}
  </div>
  {panel(f'<div style="display:flex;align-items:center;gap:10pt">{SWORD}<div><div class="px" style="font-size:9pt">MAIN QUEST</div><div style="font:500 8pt Space Grotesk;color:#7A7465">the one hard thing. beat this and the day counts.</div></div><span class="xp" style="margin-left:auto;background:#FBD3CE;font-size:8pt">+100 XP</span></div><div style="height:26pt;border-bottom:1.6pt solid #2B2A33;margin-top:6pt"></div><div style="display:flex;gap:10pt;margin-top:8pt;font:600 7.5pt Space Grotesk;color:#7A7465"><span>first tiny step:</span><div style="flex:1;border-bottom:1.2pt dashed #D8CFBE"></div></div>', "", "#FFF")}
  {panel(f'<div class="px" style="font-size:8pt;margin-bottom:4pt">SIDE QUESTS</div>{side}', "flex:1")}
  <div style="display:flex;gap:12pt">
    {panel(f'<div class="px" style="font-size:8pt;margin-bottom:8pt">POTIONS</div><div style="display:flex;align-items:center;gap:6pt"><span style="font:700 7pt Space Grotesk;width:34pt">meds</span>{FLASK}{FLASK}</div><div style="display:flex;align-items:center;gap:3pt;margin-top:8pt"><span style="font:700 7pt Space Grotesk;width:37pt">water</span>{drops}</div>', "flex:1")}
    {panel(f'<div style="display:flex;align-items:center;gap:8pt">{CHEST}<div class="px" style="font-size:8pt">LOOT</div></div><div style="font:500 7.5pt Space Grotesk;color:#7A7465;margin:4pt 0 2pt">my reward when the main quest is done</div><div style="height:22pt;border-bottom:1.6pt solid #2B2A33"></div>', "flex:1", "#FFF6DC")}
  </div></div>"""


def b_month():
    # 31일을 뱀 모양 길로. 7일마다 깃발(주간 체크포인트), 끝에 보스 성.
    W, H = 508, 470
    cols, rows = 7, 5
    xs = [40 + i * (W - 80) / (cols - 1) for i in range(cols)]
    ys = [40 + j * (H - 110) / (rows - 1) for j in range(rows)]
    pts = []
    for j in range(rows):
        seq = xs if j % 2 == 0 else xs[::-1]
        for x in seq:
            pts.append((x, ys[j]))
    days = calendar.monthrange(Y, M)[1]
    pts = pts[:days]
    path = "M" + " L".join(f"{pt(x)} {pt(y)}" for x, y in pts)
    g = [f'<path d="{path}" fill="none" stroke="#2B2A33" stroke-width="3" stroke-dasharray="1 7" stroke-linecap="round"/>']
    for i, (x, y) in enumerate(pts):
        d = i + 1
        wd = dt.date(Y, M, d).weekday()
        fill = "#3FA66B" if wd == 6 else ("#FDE9B8" if wd == 5 else "#fff")
        g.append(f'<circle cx="{pt(x + 3)}" cy="{pt(y + 3)}" r="17" fill="#2B2A33"/>')
        g.append(f'<circle cx="{pt(x)}" cy="{pt(y)}" r="17" fill="{fill}" stroke="#2B2A33" stroke-width="2"/>')
        g.append(f'<text x="{pt(x)}" y="{pt(y + 4.5)}" text-anchor="middle" font-family="Space Grotesk" font-weight="700" font-size="12" fill="#2B2A33">{d}</text>')
        if wd == 6:
            g.append(f'<path d="M{pt(x + 12)} {pt(y - 14)}v-18l11 5-11 5" fill="#E4574B" stroke="#2B2A33" stroke-width="1.6"/>')
    bx, by = W / 2, H - 28
    g.append(f'<rect x="{bx - 150}" y="{by - 22}" width="300" height="42" rx="6" fill="#2B2A33"/>')
    g.append(f'<rect x="{bx - 153}" y="{by - 25}" width="300" height="42" rx="6" fill="#E4574B" stroke="#2B2A33" stroke-width="2"/>')
    g.append(f'<text x="{bx - 138}" y="{by + 1}" font-family="Silkscreen" font-size="11" fill="#fff">MONTH BOSS:</text>')
    g.append(f'<line x1="{bx - 40}" x2="{bx + 135}" y1="{by + 4}" y2="{by + 4}" stroke="#fff" stroke-width="1.5"/>')
    return b_menu("MONTH") + f"""<div class="c">
  <div style="display:flex;align-items:end;justify-content:space-between">
    <div><div class="px" style="font-size:8pt;color:#7A7465">WORLD 3 &middot; 2027</div>
    <div style="font:700 34pt Space Grotesk;line-height:1;margin-top:4pt">March</div></div>
    <div style="font:500 8pt Space Grotesk;color:#7A7465;text-align:right;line-height:1.5">Tap a day to play it.<br>Flags are weekly checkpoints.</div>
  </div>
  {panel(f'<svg viewBox="0 0 {W} {H}" width="100%" height="100%">{"".join(g)}</svg>', "flex:1")}
  </div>"""


# =================================================================== C ==
# BOLD -- 네오 브루탈리즘. 굵은 외곽선, 평면 원색, 거대한 숫자, 딱딱한 그림자
C_CSS = """
body{font-family:'Space Grotesk',sans-serif;color:#111}
.pg{background:#F3EFE6}
.blk{border:2.4pt solid #111;border-radius:0;position:relative;padding:10pt 12pt;box-shadow:5pt 5pt 0 #111}
.h{font:400 9pt 'Archivo Black';letter-spacing:.02em;text-transform:uppercase}
.top{position:absolute;left:28pt;right:28pt;top:22pt;height:26pt;display:flex;gap:5pt}
.top a{flex:1;border:2pt solid #111;display:flex;align-items:center;justify-content:center;
  font:400 6.3pt 'Archivo Black';background:#fff}
.top a.on{background:#111;color:#FFD23F}
.c{position:absolute;left:28pt;right:33pt;top:66pt;bottom:30pt;display:flex;flex-direction:column;gap:16pt}
.ln{height:21pt;border-bottom:1.4pt solid #111}
"""


def c_top(on):
    tabs = ["INDEX", "YEAR", "MONTH", "WEEK", "FOCUS", "FEEL", "HABITS", "HEALTH", "LIFE", "NOTES"]
    return '<nav class="top">' + "".join(f'<a class="{"on" if t == on else ""}">{t}</a>' for t in tabs) + '</nav>'


def c_daily():
    hours = ["7", "8", "9", "10", "11", "12", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    sched = "".join(f'<div style="display:flex;align-items:start;height:22.4pt;border-bottom:1.2pt solid #111">'
                    f'<span style="font:400 7pt Archivo Black;background:#111;color:#fff;padding:1pt 4pt;margin-top:3pt">{h}</span></div>'
                    for h in hours)
    top3 = "".join(f'<div style="display:flex;gap:8pt;align-items:center;height:26pt;border-bottom:1.4pt solid #111">'
                   f'<span style="font:400 13pt Archivo Black">{i}</span><div style="flex:1"></div>'
                   f'<div style="width:13pt;height:13pt;border:2pt solid #111;background:#fff"></div></div>' for i in (1, 2, 3))
    mood = "".join(f'<div style="flex:1;height:26pt;border:2pt solid #111;background:{c}"></div>'
                   for c in ["#FF5A36", "#FF9EC7", "#FFD23F", "#3DDC97", "#3A5BFF"])
    return c_top("MONTH") + f"""<div class="c">
  <div style="display:flex;gap:16pt;align-items:stretch">
    <div class="blk" style="background:#3A5BFF;color:#fff;width:196pt;padding:6pt 14pt 10pt">
      <div style="font:400 108pt/1 'Archivo Black';letter-spacing:-.04em;-webkit-text-stroke:2pt #111">09</div>
    </div>
    <div style="flex:1;display:flex;flex-direction:column;gap:14pt">
      <div class="blk" style="background:#FFD23F"><div style="font:400 26pt/1 'Archivo Black'">TUESDAY</div>
        <div class="h" style="margin-top:4pt">March 2027 &nbsp;/&nbsp; Week 11</div></div>
      <div class="blk" style="background:#fff;flex:1"><div class="h" style="margin-bottom:4pt">Today's one thing</div><div class="ln"></div></div>
    </div>
  </div>
  <div style="display:flex;gap:16pt;flex:1;min-height:0">
    <div class="blk" style="background:#fff;flex:1;overflow:hidden"><div class="h" style="margin-bottom:4pt">Schedule</div>{sched}</div>
    <div style="flex:1;display:flex;flex-direction:column;gap:16pt">
      <div class="blk" style="background:#FF9EC7"><div class="h" style="margin-bottom:2pt">Top 3</div>{top3}</div>
      <div class="blk" style="background:#fff"><div class="h" style="margin-bottom:8pt">Mood &mdash; pick a colour</div><div style="display:flex;gap:6pt">{mood}</div></div>
      <div class="blk" style="background:#3DDC97;flex:1"><div class="h">Brain dump</div></div>
    </div>
  </div></div>"""


def c_month():
    hd = "".join(f'<div style="font:400 8pt Archivo Black;padding:5pt 6pt;border-right:2pt solid #111;'
                 f'background:#111;color:{"#FFD23F" if i >= 5 else "#fff"}">{d}</div>'
                 for i, d in enumerate(["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]))
    cells = ""
    for w in WEEKS:
        for i, d in enumerate(w):
            bg = "#3DDC97" if (d and i >= 5) else ("#fff" if d else "#F3EFE6")
            cells += (f'<div style="border-right:2pt solid #111;border-top:2pt solid #111;background:{bg};padding:5pt 6pt">'
                      f'<span style="font:400 13pt Archivo Black">{d or ""}</span></div>')
    return c_top("MONTH") + f"""<div class="c">
  <div style="display:flex;align-items:end;gap:14pt">
    <div style="font:400 92pt/0.8 'Archivo Black';letter-spacing:-.04em;color:#FF5A36;-webkit-text-stroke:2.4pt #111">MAR</div>
    <div class="blk" style="background:#FFD23F;padding:6pt 10pt;margin-bottom:6pt"><div class="h">2027</div></div>
  </div>
  <div class="blk" style="flex:1;padding:0;background:#111;display:grid;grid-template-columns:repeat(7,1fr);grid-template-rows:auto repeat({len(WEEKS)},1fr);border-right:0">{hd}{cells}</div>
  <div class="blk" style="background:#FF9EC7"><div class="h" style="margin-bottom:2pt">This month I will</div><div class="ln"></div></div>
  </div>"""


# =================================================================== D ==
# NOTEBOOK -- 진짜 노트 한 권. 점지 전면, 스프링 구멍, 삐져나온 인덱스 탭, 손글씨 제목, 마스킹 테이프
D_CSS = """
body{font-family:'Nunito',sans-serif;color:#2E2A27}
.pg{background:#FFFDF7}
.hand{font-family:'Caveat',cursive}
.c{position:absolute;left:66pt;right:64pt;top:40pt;bottom:36pt;display:flex;flex-direction:column}
.stk{position:absolute;right:0;width:40pt;height:52pt;display:flex;align-items:center;justify-content:center;
  border-radius:6pt 0 0 6pt}
.stk span{writing-mode:vertical-rl;transform:rotate(180deg);font:700 13pt 'Caveat';color:#2E2A27}
"""


def rnd(seed):
    r = random.Random(seed)
    return lambda a: r.uniform(-a, a)


def wobble_rect(x, y, w, h, seed, stroke="#2E2A27", sw=1.3, fill="none"):
    j = rnd(seed)
    p = [(x + j(1.2), y + j(1.2)), (x + w + j(1.2), y + j(1.2)),
         (x + w + j(1.2), y + h + j(1.2)), (x + j(1.2), y + h + j(1.2))]
    d = f"M{pt(p[0][0])} {pt(p[0][1])}"
    for a, b in zip(p, p[1:] + p[:1]):
        mx, my = (a[0] + b[0]) / 2 + j(1.5), (a[1] + b[1]) / 2 + j(1.5)
        d += f" Q{pt(mx)} {pt(my)} {pt(b[0])} {pt(b[1])}"
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round"/>'


def dots_svg():
    d = "".join(f"M{x - .9:.1f} {y}a.9 .9 0 1 0 1.8 0a.9 .9 0 1 0-1.8 0"
                for y in range(14, 792, 14) for x in range(56, 572, 14))
    return f'<svg width="612pt" height="792pt" viewBox="0 0 612 792" style="position:absolute;inset:0"><path d="{d}" fill="#DCD6CA"/></svg>'


def d_binding():
    holes = "".join(f'<circle cx="22" cy="{50 + i * 58}" r="7.5" fill="#E9E3D8"/>'
                    f'<circle cx="22" cy="{50 + i * 58}" r="4.5" fill="#fff"/>'
                    f'<path d="M4 {50 + i * 58 - 2}h18" stroke="#9B948A" stroke-width="2.6" stroke-linecap="round"/>' for i in range(13))
    return f'<svg width="40pt" height="792pt" viewBox="0 0 40 792" style="position:absolute;left:0;top:0">{holes}</svg>'


def d_tabs(on):
    tabs = [("Index", "#F6D6CF"), ("Year", "#F6D6CF"), ("Month", "#F6D6CF"), ("Week", "#F6D6CF"),
            ("Focus", "#CFE3F2"), ("Feel", "#CFE3F2"), ("Habits", "#D4EBCF"), ("Health", "#D4EBCF"),
            ("Life", "#F7E6B5"), ("Notes", "#F7E6B5")]
    out = ""
    for i, (t, c) in enumerate(tabs):
        w = "48pt" if t == on else "40pt"
        out += (f'<a class="stk" style="top:{40 + i * 71}pt;background:{c};width:{w};'
                f'{"border-left:2pt solid #2E2A27" if t == on else ""}"><span>{t}</span></a>')
    return out


def tape(x, y, w, rot, color):
    j = rnd(int(x + y))
    zig_l = " ".join(f"{pt(x + (2.5 if k % 2 else 0))} {pt(y + k * 3)}" for k in range(6))
    zig_r = " ".join(f"{pt(x + w - (2.5 if k % 2 else 0))} {pt(y + 15 - k * 3)}" for k in range(6))
    return (f'<g transform="rotate({rot} {x + w / 2} {y + 7})"><polygon points="{zig_l} {zig_r}" fill="{color}"/></g>')


def d_daily():
    W, H = 482, 716
    g = []
    g.append(wobble_rect(0, 98, W, 46, 1, sw=1.4))
    g.append(wobble_rect(0, 166, 270, 390, 2))
    g.append(wobble_rect(290, 166, 192, 180, 3))
    g.append(wobble_rect(290, 366, 192, 190, 4))
    g.append(wobble_rect(0, 578, W, 112, 5))
    g.append(f'<path d="M4 64 q60 -8 120 0 t120 -2" fill="none" stroke="#E07A5F" stroke-width="2.2" stroke-linecap="round"/>')
    hours = ["7", "9", "11", "1", "3", "5", "7", "9"]
    for i, h in enumerate(hours):
        yy = 206 + i * 44
        g.append(f'<text x="14" y="{yy}" font-family="Caveat" font-size="15" fill="#9B948A">{h}</text>')
    items = ["•", "•", "•", "○", "○", "–"]
    for i, s in enumerate(items):
        g.append(f'<text x="306" y="{214 + i * 21}" font-family="Nunito" font-weight="800" font-size="12" fill="#2E2A27">{s}</text>')
    for k in range(3):
        g.append(wobble_rect(306 + k * 58, 420, 46, 46, 20 + k, stroke="#5B8DB8", sw=1.2))
    g.append(tape(330, 152, 90, -4, "#F6D6CF"))
    g.append(tape(-12, 570, 80, 5, "#CFE3F2"))
    txt = (f'<text x="16" y="127" font-family="Caveat" font-size="19" font-weight="700" fill="#2E2A27">today, just this one thing:</text>'
           f'<text x="306" y="194" font-family="Caveat" font-size="20" font-weight="700">to do</text>'
           f'<text x="306" y="396" font-family="Caveat" font-size="20" font-weight="700">meds · water · mood</text>'
           f'<text x="16" y="608" font-family="Caveat" font-size="20" font-weight="700">brain dump</text>'
           f'<text x="16" y="190" font-family="Caveat" font-size="20" font-weight="700">the day</text>'
           f'<text x="306" y="338" font-family="Nunito" font-size="7" fill="#9B948A">• to do   ○ event   – note</text>')
    return dots_svg() + d_binding() + d_tabs("Month") + f"""<div class="c">
  <div style="display:flex;align-items:baseline;gap:12pt">
    <div class="hand" style="font-size:44pt;font-weight:700;line-height:1">Tuesday, March 9</div>
    <div style="font:700 8pt Nunito;color:#9B948A;letter-spacing:.1em">2027 &middot; WK 11</div></div>
  <svg viewBox="0 {-20} {W} {H}" width="{W}pt" height="{H}pt" style="position:absolute;top:0;left:0">{''.join(g)}{txt}</svg>
  </div>"""


def d_month():
    W = 482
    g = [f'<path d="M4 64 q60 -8 120 0 t80 -2" fill="none" stroke="#E07A5F" stroke-width="2.2" stroke-linecap="round"/>']
    x0, y0, cw, ch = 0, 116, W / 7, 70
    for i, d in enumerate(["M", "T", "W", "T", "F", "S", "S"]):
        g.append(f'<text x="{pt(x0 + i * cw + cw / 2)}" y="{y0 - 10}" text-anchor="middle" font-family="Caveat" font-size="17" font-weight="700" fill="{"#E07A5F" if i >= 5 else "#2E2A27"}">{d}</text>')
    for r, w in enumerate(WEEKS):
        for i, d in enumerate(w):
            if d:
                g.append(wobble_rect(x0 + i * cw + 2, y0 + r * ch + 2, cw - 4, ch - 4, r * 7 + i, sw=1.1))
                g.append(f'<text x="{pt(x0 + i * cw + 9)}" y="{y0 + r * ch + 20}" font-family="Caveat" font-size="16" font-weight="700">{d}</text>')
    sy = y0 + len(WEEKS) * ch + 26
    g.append(f'<g transform="rotate(-2 120 {sy + 80})"><rect x="6" y="{sy}" width="220" height="150" fill="#FBEBA8"/>'
             f'<text x="22" y="{sy + 30}" font-family="Caveat" font-size="20" font-weight="700">this month</text></g>')
    g.append(tape(70, sy - 8, 90, 3, "#CFE3F2"))
    g.append(f'<g transform="rotate(2 360 {sy + 80})"><rect x="252" y="{sy + 6}" width="220" height="150" fill="#F9D9D0"/>'
             f'<text x="268" y="{sy + 36}" font-family="Caveat" font-size="20" font-weight="700">don\'t forget</text></g>')
    g.append(tape(320, sy - 2, 84, -3, "#D4EBCF"))
    return dots_svg() + d_binding() + d_tabs("Month") + f"""<div class="c">
  <div class="hand" style="font-size:52pt;font-weight:700;line-height:1">March <span style="font-size:22pt;color:#9B948A">2027</span></div>
  <svg viewBox="0 {-20} {W} 716" width="{W}pt" height="716pt" style="position:absolute;top:0;left:0">{''.join(g)}</svg>
  </div>"""


CONCEPTS = {
    "A_clockwise": (A_CSS, "family=Inter:wght@400;500;600;700;800&family=Outfit:wght@500;700", [a_daily(), a_month()]),
    "B_quest": (B_CSS, "family=Space+Grotesk:wght@500;600;700&family=Silkscreen", [b_daily(), b_month()]),
    "C_bold": (C_CSS, "family=Archivo+Black&family=Space+Grotesk:wght@500;700", [c_daily(), c_month()]),
    "D_notebook": (D_CSS, "family=Caveat:wght@500;700&family=Nunito:wght@400;700;800", [d_daily(), d_month()]),
}

if __name__ == "__main__":
    import pypdfium2 as pdfium
    from PIL import Image
    prof = os.path.join(OUT, "prof")
    for name, (css, fonts, pages) in CONCEPTS.items():
        html = os.path.join(OUT, f"{name}.html")
        pdf = os.path.join(OUT, f"{name}.pdf")
        open(html, "w", encoding="utf-8").write(doc(css, fonts, pages))
        if os.path.exists(pdf):
            os.remove(pdf)
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", f"--user-data-dir={prof}",
                        "--no-pdf-header-footer", "--virtual-time-budget=8000",
                        f"--print-to-pdf={pdf}", "file:///" + html.replace("\\", "/")],
                       capture_output=True)
        with open(pdf, "rb") as f:
            d = pdfium.PdfDocument(f.read())
        ims = [d[i].render(scale=1.4).to_pil() for i in range(len(d))]
        d.close()
        w, h = ims[0].size
        sheet = Image.new("RGB", (w * 2 + 60, h + 40), (190, 190, 190))
        for i, im in enumerate(ims[:2]):
            sheet.paste(im, (20 + i * (w + 20), 20))
        sheet.save(os.path.join(OUT, f"{name}.png"))
        print(name, len(ims), "pages")
