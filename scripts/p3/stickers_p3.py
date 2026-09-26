# -*- coding: utf-8 -*-
"""상품 3 스티커 키트 -- "리소 인쇄 스탬프". 표지 "52" 의 청록·마젠타 판 어긋남을 시각 언어로. Prod 3 방 소유.

    python scripts/p3/stickers_p3.py        # -> output/prod3/stickers/<DRAFT>/  (sheets/*.png, png/<묶음>/*.png)

사용자 확정(2026-09-26): 리소 스탬프 방향, 두 색 겹친 글자, 바탕은 핸드오프 팔레트 7색 전부, 개수는 많을수록(200+),
종류를 넓게. 내용은 플래너 장치·도구에 붙는 것만. 이미 있는 폴더면 멈춘다(덮어쓰지 않는다) -- 고치면 DRAFT 를 올린다.
draft-v0.1~0.3 은 시안 한 장씩(샘플 시트, 커밋 e87bbf3 / adee9d2 의 이 파일).
"""
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[2]
DRAFT = "draft-v0.4"   # 전체 키트 첫 판 (고유 약 130종)
OUT = ROOT / "output" / "prod3" / "stickers" / DRAFT
if OUT.exists():
    raise SystemExit(f"{OUT} 는 이미 있다. 덮어쓰지 않는다 -- DRAFT 를 올릴 것.")
(OUT / "sheets").mkdir(parents=True)

PAPER, INK, N700, CYAN, CYAN7 = "#f8f4f4", "#201e1d", "#605d5d", "#0088b0", "#006786"
# 색 조합: 핸드오프 팔레트만. 이름 -> (바탕, 글자, 어긋난 판)
WAYS = {
    "paper": ("#f8f4f4", "#201e1d", "rgba(214,0,108,.55)"),
    "cyan":  ("#0088b0", "#f8f4f4", "rgba(32,30,29,.55)"),
    "deep":  ("#006786", "#f8f4f4", "rgba(214,0,108,.75)"),
    "mist":  ("#95c9d9", "#201e1d", "rgba(214,0,108,.55)"),
    "ink":   ("#201e1d", "#f8f4f4", "rgba(0,136,176,.9)"),
    "blush": ("#efc9d7", "#201e1d", "rgba(0,136,176,.6)"),
    "stone": ("#d7d3d3", "#201e1d", "rgba(214,0,108,.55)"),
}
WK = list(WAYS)


# ------------------------------------------------------------------ icons --
def P(d, w=6):
    return f'<path d="{d}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'


def battery(n):
    bars = "".join(f'<rect x="{12 + i * 11}" y="22" width="7" height="24" rx="1.5" fill="currentColor" stroke="none"/>' for i in range(n))
    return f'<rect x="6" y="16" width="62" height="36" rx="7" stroke-width="5"/>{P("M72 28v12")}{bars}'


ICON = {
    "check": P("M14 34l13 13 27-30", 7), "tilde": P("M12 36c8-12 16-12 24 0s16 12 24 0", 7),
    "cross": P("M18 18l32 32M50 18l-32 32", 7),
    "sun": '<circle cx="40" cy="40" r="13" stroke-width="6"/>' + "".join(
        f'<path d="M40 16v-8" stroke-width="6" stroke-linecap="round" transform="rotate({a} 40 40)"/>' for a in range(0, 360, 45)),
    "cloud": P("M22 56h36a13 13 0 0 0 0-26 18 18 0 0 0-34-4 14 14 0 0 0-2 30z"),
    "part": '<circle cx="30" cy="28" r="11" stroke-width="6"/>' + P("M26 60h32a11 11 0 0 0 0-22 16 16 0 0 0-30-3 12 12 0 0 0-2 25z"),
    "rain": P("M22 48h36a13 13 0 0 0 0-26 18 18 0 0 0-34-4 14 14 0 0 0-2 30z") + P("M30 60l-4 10M44 60l-4 10M58 60l-4 10", 5),
    "storm": P("M22 44h36a13 13 0 0 0 0-26 18 18 0 0 0-34-4 14 14 0 0 0-2 30z") + P("M44 50l-9 13h11l-7 12", 5),
    "fog": P("M12 30h56M18 42h50M12 54h44", 6),
    "clock": '<circle cx="40" cy="40" r="28" stroke-width="6"/>' + P("M40 24v16l11 8"),
    "timer": '<circle cx="40" cy="44" r="25" stroke-width="6"/>' + P("M40 44V30M33 12h14M40 12v7"),
    "envelope": '<rect x="8" y="18" width="64" height="44" rx="5" stroke-width="5"/>' + P("M10 22l30 22 30-22", 5),
    "mailbox": P("M14 64V36a16 16 0 0 1 32 0v28zM46 36h22v28H46M30 50h6M58 20v16", 5),
    "arrow": P("M10 40h54M46 22l18 18-18 18", 7), "back": P("M70 40H16M34 22L16 40l18 18", 7),
    "star": P("M40 10l9 19 21 3-15 15 4 21-19-10-19 10 4-21-15-15 21-3z", 5),
    "flag": P("M18 70V12M18 14h40l-8 12 8 12H18", 5),
    "pin": P("M40 72s22-22 22-38a22 22 0 0 0-44 0c0 16 22 38 22 38z", 5) + '<circle cx="40" cy="34" r="7" stroke-width="5"/>',
    "bolt": P("M44 8L20 44h18l-4 28 26-38H42z", 5),
    "spark": P("M40 10v18M40 52v18M10 40h18M52 40h18M20 20l12 12M48 48l12 12M60 20L48 32M32 48L20 60", 5),
    "heart": P("M40 66S12 48 12 30a14 14 0 0 1 28-6 14 14 0 0 1 28 6c0 18-28 36-28 36z", 5),
    "drop": P("M40 10s22 26 22 40a22 22 0 0 1-44 0c0-14 22-40 22-40z", 5),
    "pill": '<rect x="10" y="28" width="60" height="26" rx="13" stroke-width="5" transform="rotate(-30 40 41)"/>' + P("M33 25l14 24", 5),
    "moon": P("M52 12a28 28 0 1 0 16 44A24 24 0 0 1 52 12z", 5),
    "shoe": P("M10 54l4-24 18 6 10 8 22 4a6 6 0 0 1 4 6v2H10z", 5),
    "steth": P("M22 10v22a14 14 0 0 0 28 0V10M36 46v8a14 14 0 0 0 28 0v-6", 5) + '<circle cx="64" cy="42" r="6" stroke-width="5"/>',
    "chat": P("M12 16h56v36H36l-14 12V52H12z", 5),
    "bill": P("M18 8h44v64l-8-6-7 6-7-6-7 6-7-6-8 6z", 5) + P("M28 26h24M28 38h24M28 50h14", 4),
    "coin": '<circle cx="40" cy="40" r="28" stroke-width="6"/>' + P("M48 30c-2-4-6-6-10-6-6 0-10 3-10 8 0 11 20 6 20 16 0 5-4 8-10 8-4 0-8-2-10-6M38 18v44", 5),
    "cart": P("M8 14h10l8 36h36l6-24H22", 5) + '<circle cx="32" cy="62" r="5" stroke-width="5"/><circle cx="56" cy="62" r="5" stroke-width="5"/>',
    "box": P("M10 28l30-14 30 14v30L40 72 10 58zM10 28l30 14 30-14M40 42v30", 5),
    "phone": '<rect x="24" y="8" width="32" height="64" rx="6" stroke-width="5"/>' + P("M36 62h8", 5),
    "people": '<circle cx="28" cy="26" r="9" stroke-width="5"/><circle cx="54" cy="26" r="9" stroke-width="5"/>' + P("M12 64c0-12 7-20 16-20s16 8 16 20M38 64c0-12 7-20 16-20s16 8 16 20", 5),
    "brain": P("M40 16c-6-6-18-4-20 6-8 2-10 12-4 18-4 8 2 18 12 16 4 8 12 8 12 0V16zM40 16c6-6 18-4 20 6 8 2 10 12 4 18 4 8-2 18-12 16-4 8-12 8-12 0", 5),
    "pause": P("M30 18v44M50 18v44", 8),
    "leaf": P("M16 64C16 32 36 14 66 14c0 30-18 50-50 50zM16 64l30-30", 5),
    "gift": '<rect x="12" y="30" width="56" height="36" rx="3" stroke-width="5"/>' + P("M8 30h64M40 30v36M40 30c-6-14-20-14-18-4M40 30c6-14 20-14 18-4", 5),
    "cake": '<rect x="14" y="38" width="52" height="28" rx="4" stroke-width="5"/>' + P("M14 50c8 6 18 6 26 0s18-6 26 0M40 38V26M40 14v4", 5),
    "plane": P("M8 44l64-26-20 50-12-18zM40 50l-8 18", 5),
    "cal": '<rect x="12" y="16" width="56" height="52" rx="5" stroke-width="5"/>' + P("M12 32h56M28 10v12M52 10v12", 5),
    "bookmark": P("M22 10h36v60L40 56 22 70z", 5),
    "target": '<circle cx="40" cy="40" r="28" stroke-width="5"/><circle cx="40" cy="40" r="15" stroke-width="5"/><circle cx="40" cy="40" r="3" stroke-width="5"/>',
}
for _n in range(1, 6):
    ICON[f"bat{_n}"] = battery(_n)


def plate_svg(inner, off=3):
    """같은 도형을 어긋난 판 색으로 한 번, 글자 색으로 한 번 -- 판이 어긋난 인쇄"""
    return (f'<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
            f'<g transform="translate({off},{off * .7})" style="opacity:.6;stroke:var(--plate);color:var(--plate)" fill="none">{inner}</g>'
            f'<g stroke="currentColor" fill="none">{inner}</g></svg>')


# ------------------------------------------------------------ the kit --
# (글자, 아이콘, 모양)  모양: pill / round / tag / blank / icon / ticket / tab / wx
KIT = {
    "Experiments": [("Helped", "check", "round"), ("Sort of", "tilde", "round"), ("Not for me", "cross", "round"),
                    ("Keep", None, "tag"), ("Drop", None, "tag"), ("Try again", "back", "pill"), ("Bonus week", "star", "pill"),
                    ("In my playbook", "bookmark", "pill"), ("Experiment #", None, "blank"), ("New strategy", "spark", "pill")],
    "Brain weather": [("Rough", "storm", "wx"), ("Low", "rain", "wx"), ("Okay", "cloud", "wx"), ("Good", "part", "wx"),
                      ("Great", "sun", "wx"), ("Foggy", "fog", "wx"), ("Scattered", "spark", "pill"), ("Wired", "bolt", "pill"),
                      ("Flat", None, "pill"), ("Calm", "leaf", "pill")],
    "Energy": [("", "bat1", "icon"), ("", "bat2", "icon"), ("", "bat3", "icon"), ("", "bat4", "icon"), ("", "bat5", "icon"),
               ("Low battery day", "bat1", "pill"), ("Recharge", "bolt", "pill")],
    "Time": [("+15 buffer", "clock", "pill"), ("Leave at", None, "blank"), ("Timer on", "timer", "pill"), ("Hard stop", "pause", "pill"),
             ("Due", None, "blank"), ("Later than you think", "clock", "pill"), ("5-minute start", "timer", "pill"),
             ("Two-minute rule", None, "pill"), ("Alarm set", "bolt", "pill"), ("Waiting mode", "clock", "pill")],
    "Time links": [("To future me", "envelope", "pill"), ("Arrived", None, "round"), ("From yesterday", "back", "pill"),
                   ("Tomorrow starts with", "arrow", "pill"), ("Note to self", "envelope", "pill"), ("Year-end mailbox", "mailbox", "pill")],
    "Focus": [("Body doubling", "people", "pill"), ("One thing", "target", "pill"), ("Brain dump", "brain", "pill"),
              ("Phone away", "phone", "pill"), ("Single tab", None, "pill"), ("Deep work", "target", "pill"),
              ("Hyperfocus zone", "bolt", "pill"), ("Break time", "pause", "pill")],
    "Small wins": [("Did the thing", "check", "pill"), ("Started counts", "arrow", "pill"), ("Tiny step", None, "pill"),
                   ("Showed up", "star", "pill"), ("Good enough", "check", "pill"), ("Done is good", None, "pill"),
                   ("Rest counts", "moon", "pill"), ("Asked for help", "chat", "pill"), ("Proud of this", "heart", "pill"), ("Win", "star", "round")],
    "Feelings": [("Be kind", "heart", "pill"), ("Not a failure", None, "pill"), ("Pause", "pause", "pill"),
                 ("Stop · Think · Act", None, "pill"), ("It's okay", None, "pill"), ("Overwhelmed", "storm", "pill"),
                 ("Needs rest", "moon", "pill"), ("Breathe", "leaf", "pill")],
    "Body": [("Meds", "pill", "pill"), ("Water", "drop", "pill"), ("Moved", "shoe", "pill"), ("Slept", "moon", "pill"),
             ("Doctor", "steth", "pill"), ("Therapy", "chat", "pill"), ("Ate a real meal", None, "pill"), ("Outside", "sun", "pill")],
    "Life admin": [("ADHD tax $", "coin", "blank"), ("Bill due", "bill", "pill"), ("Renewal", "back", "pill"), ("Payday", "coin", "pill"),
                   ("Cancel it", "cross", "pill"), ("Doom pile cleared", "box", "pill"), ("Laundry", None, "pill"),
                   ("Groceries", "cart", "pill"), ("Clear one zone", "box", "pill"), ("Where I put it", "pin", "pill")],
    "Dopamine menu": [("Starter", None, "ticket"), ("Main", None, "ticket"), ("Side", None, "ticket"),
                      ("Dessert", None, "ticket"), ("Special", None, "ticket")],
    "Status": [("Today", "flag", "pill"), ("This week", "cal", "pill"), ("Someday", None, "pill"), ("Waiting on", "clock", "pill"),
               ("In progress", "arrow", "pill"), ("Done", "check", "pill"), ("Skipped, no shame", None, "pill"), ("Urgent", "bolt", "pill")],
    "Anywhere": [("Public holiday", None, "blank"), ("Day off", "sun", "pill"), ("School break", None, "pill"),
                 ("Birthday", "cake", "blank"), ("Appointment", "cal", "blank"), ("Trip", "plane", "pill"),
                 ("Celebrate", "gift", "pill"), ("Deadline", "flag", "pill")],
    "Days & months": [(d, None, "tab") for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun",
                                                 "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]],
    "Icons": [("", k, "icon") for k in ["star", "flag", "pin", "bolt", "check", "arrow", "heart", "spark", "bookmark", "target"]],
}


def colorways(group, i, shape):
    """디자인마다 색 조합 -- 판정 도장은 뜻 있는 색을 고정, 탭은 한 가지, 나머지는 돌려 가며 두 가지"""
    if group == "Experiments" and shape == "round":
        return [["cyan", "paper"], ["stone", "paper"], ["ink", "blush"]][i]
    if shape == "tab":
        return [WK[i % len(WK)]]
    return [WK[i % len(WK)], WK[(i + 3) % len(WK)]]


def sticker(text, icon, shape):
    ic = plate_svg(ICON[icon]) if icon else ""
    small = shape in ("round", "wx")
    t = f'<span class="t{" sm" if small else ""}">{text}</span>' if text else ""
    if shape == "round":
        return f'<div class="st round">{ic}{t}</div>'
    if shape == "wx":
        return f'<div class="st wx">{ic}{t}</div>'
    if shape == "tag":
        return f'<div class="tagw"><div class="st tag">{t}</div></div>'
    if shape == "blank":
        return f'<div class="st">{ic}<span class="t">{text} <span class="blank"></span></span></div>'
    if shape == "icon":
        return f'<div class="st ico">{ic}</div>'
    if shape == "ticket":
        return f'<div class="st ticket"><span class="t sm2">Dopamine</span><span class="t">{text}</span></div>'
    if shape == "tab":
        return f'<div class="st tab"><span class="t">{text}</span></div>'
    return f'<div class="st">{ic}{t}</div>'


CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=block');
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:2000px;background:#e6e2de;font-family:'Source Serif 4',Georgia,serif;color:{INK};padding:100px 110px}}
body.cut{{background:transparent}}
h1{{font-size:56px;font-weight:600}} .sub{{font-size:28px;font-style:italic;color:{N700};margin:6px 0 30px}}
.sec{{font-size:24px;letter-spacing:.14em;text-transform:uppercase;color:{CYAN7};margin:30px 0 20px}}
.grid{{display:flex;flex-wrap:wrap;gap:30px 30px;align-items:center}}
.cell{{padding:14px;display:inline-block}}
.st{{background:var(--bg);color:var(--fg);border-radius:24px;padding:16px 24px;display:inline-flex;align-items:center;gap:14px;
  box-shadow:0 0 0 9px #fff;white-space:nowrap}}
.sheet .st{{box-shadow:0 0 0 9px #fff,0 12px 22px rgba(0,0,0,.16)}}
.st svg{{width:60px;height:60px;flex:none}}
.st.round{{border-radius:50%;width:180px;height:180px;flex-direction:column;justify-content:center;gap:2px;padding:0}}
.st.round svg{{width:62px;height:62px}}
.st.wx{{flex-direction:column;gap:2px;padding:16px 20px}} .st.wx svg{{width:70px;height:70px}}
.st.ico{{padding:16px}} .st.ico svg{{width:76px;height:76px}}
.st.tab{{border-radius:14px;padding:10px 20px}}
.st.ticket{{flex-direction:column;gap:0;padding:14px 30px;border-radius:14px}}
.tagw{{display:inline-block;background:#fff;padding:9px;clip-path:polygon(22px 0,100% 0,100% 100%,22px 100%,0 50%);border-radius:0 18px 18px 0}}
.sheet .tagw{{filter:drop-shadow(0 10px 10px rgba(0,0,0,.14))}}
.st.tag{{border-radius:0 12px 12px 0;box-shadow:none;clip-path:polygon(18px 0,100% 0,100% 100%,18px 100%,0 50%);padding:14px 26px 14px 38px}}
.t{{font-size:30px;font-weight:600;letter-spacing:.07em;text-transform:uppercase;text-shadow:2.5px 2px 0 var(--plate)}}
.t.sm{{font-size:22px}} .t.sm2{{font-size:16px;letter-spacing:.2em;opacity:.8}}
.blank{{display:inline-block;width:110px;border-bottom:3px solid currentColor;height:28px;vertical-align:bottom}}
""" + "".join(f".w-{k}{{--bg:{b};--fg:{f};--plate:{pl}}}" for k, (b, f, pl) in WAYS.items())

items = []   # (group, name, way, html)
for g, lst in KIT.items():
    for i, (text, icon, shape) in enumerate(lst):
        for w in colorways(g, i, shape):
            name = re.sub(r"[^a-z0-9]+", "-", (text or icon).lower()).strip("-")
            items.append((g, name, w, f'<div class="cell w-{w}">{sticker(text, icon, shape)}</div>'))
uniq = sum(len(v) for v in KIT.values())
print(f"unique designs {uniq}, stickers {len(items)}")

from playwright.sync_api import sync_playwright  # noqa: E402


def page(body, cls):
    return f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body class="{cls}">{body}</body></html>'


with sync_playwright() as p:
    br = p.chromium.launch(channel="chrome")
    pg = br.new_page(viewport={"width": 2000, "height": 1000})
    # 1) 시트 -- 묶음 세 개씩 한 장 (미리보기·리스팅용)
    groups = list(KIT)
    for si in range(0, len(groups), 3):
        gs = groups[si:si + 3]
        body = (f'<h1>The ADHD Year · Sticker kit</h1><div class="sub">Riso-stamp stickers made for the planner\'s own pages.</div>'
                + "".join(f'<div class="sec">{g}</div><div class="grid">' + "".join(h for gg, _, _, h in items if gg == g) + "</div>" for g in gs))
        f = OUT / "sheets" / f"sheet_{si // 3 + 1:02d}.html"
        f.write_text(page(body, "sheet"), encoding="utf-8")
        pg.goto(f.as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(400)
        pg.screenshot(path=str(f.with_suffix(".png")), full_page=True)
    # 2) 낱장 투명 PNG -- 흰 테두리까지, 배경 없이
    f = OUT / "_cut.html"
    f.write_text(page('<div class="grid">' + "".join(h for *_, h in items) + "</div>", "cut"), encoding="utf-8")
    pg.goto(f.as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(600)
    cells = pg.locator(".cell")
    for k, (g, name, w, _) in enumerate(items):
        d = OUT / "png" / re.sub(r"[^A-Za-z0-9]+", "-", g).strip("-")
        d.mkdir(parents=True, exist_ok=True)
        out = d / f"{name}_{w}.png"
        n = 2
        while out.exists():
            out = d / f"{name}-{n}_{w}.png"
            n += 1
        cells.nth(k).screenshot(path=str(out), omit_background=True)
    br.close()
print(OUT)
