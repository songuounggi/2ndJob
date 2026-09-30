# -*- coding: utf-8 -*-
"""상품 4 The ADHD Home Reset -- 빌드 (PROCESS.md 4단계).

모양은 상품 1(v8.20) 그대로: build_planner.py 를 **읽기 전용으로 import** 해서 CSS·head()·lines()·
prompt_card()·그림자 PNG·snap 을 쓴다(공유 파일이라 고치지 않는다 -- CLAUDE.md "방이 여럿").
색은 섹션마다 한 색(product4-content.md 색 확정표): 페이지 <section> 의 style 에 --bg 등을 덮어쓴다.
문구는 전부 scripts/p4/p4_content.py 에서 읽는다(5-1 기획서 대조가 원고와 PDF 를 1:1 로 본다).

    python scripts/p4/build_p4.py sample     # 표본 7쪽 -> output/prod4/sample/<VER>/
    (전체 빌드는 표본 확인 뒤에 붙인다)

Chrome 은 chrome_auto 로 켠다(계정 잠김, CLAUDE.md).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
os.environ["PLANNER_VERSION"] = "v8.20-undated"     # 상품 1 판매본 모양
import build_planner as bp                          # noqa: E402  (읽기 전용)
import color_candidates_p4 as cc                    # noqa: E402
import p4_content as C                              # noqa: E402
from chrome_auto import CHROME, chrome_args         # noqa: E402

VER = "sample-v0.1"
OUT_DIR = os.path.join(ROOT, "output", "prod4", "sample", VER)
SRC = os.path.join(ROOT, "src", f"p4_home-reset_{VER}.html")    # src/ 에 둬야 '../assets/' 가 맞는다

# ------------------------------------------------------------------ 색 --
CAND = {c["key"]: c for c in cc.CANDIDATES}
SECTION_OF_TAB = {"home": "A", "energy": "A", "rooms": "B", "routines": "C", "weeks": "C", "tools": "D"}
TABS = [("home", "HOME"), ("energy", "ENERGY"), ("rooms", "ROOMS"),
        ("routines", "ROUTINES"), ("weeks", "WEEKS"), ("tools", "TOOLS")]
ROOM_KEYS = {r[0] for r in C.ROOMS} | {C.MY_ROOM[0]}
TAB_OF_PAGE = {"cover": "home", "start": "home", "house-map": "home", "index": "home",
               "energy": "energy", "rescue": "tools"}


def tab_of(key):
    if key in TAB_OF_PAGE:
        return TAB_OF_PAGE[key]
    if key in ROOM_KEYS or key.startswith("deep-") or key == "rooms":
        return "rooms"
    return "tools"


def accent(k):
    """(장식, 틴트, 글자용) -- 후보의 1번 강조색. 탭 레일은 전 페이지 이 네 색"""
    return cc.palette(CAND[k])[0]


GRAY = dict(bg="#FFFFFF", ink="#2B2B2B", mid="#555555", soft="#6B6B6B", line="#CFCFCF", field="#F2F2F2")
GRAY_ACC = ("#8A8A8A", "#EDEDED", "#3F3F3F")


def bloom_file(k):
    name = f"p4_bloom_{k}_{VER}.png"
    path = os.path.join(ROOT, "assets", name)
    if not os.path.exists(path):
        cc.bake_bloom(CAND[k], path)
    return name


def rail(active, bw=False):
    out = []
    for k, lab in TABS:
        a, _, tx = GRAY_ACC if bw else accent(SECTION_OF_TAB[k])
        out.append(f'<a class="{"on" if k == active else ""}" href="#{k}" style="--acc:{a};--acc-text:{tx}">'
                   f'<i style="background:{a}"></i><span>{lab}</span></a>')
    return f'<nav class="rail">{"".join(out)}</nav>'


SOS = ('<a href="#rescue" class="sos">SOS</a>')


def page(key, body, bw=False, sos=True, pid=None):
    t = tab_of(key)
    k = SECTION_OF_TAB[t]
    c = GRAY if bw else CAND[k]
    a, ti, tx = GRAY_ACC if bw else accent(k)
    style = (f"--bg:{c['bg']};--ink:{c['ink']};--mid:{c['mid']};--soft:{c['soft']};--line:{c['line']};"
             f"--field:{c['field']};--accent:{a};--chip:{ti};--accent-text:{tx}")
    layer = "" if bw else (f'<div class="bg-bloom" style="background-image:url(\'../assets/{bloom_file(k)}\');'
                           f'opacity:1"></div>')
    return (f'<section class="page" id="{pid or key}" style="{style}">{layer}{rail(t, bw)}'
            f'<div class="content">{body}</div>{SOS if sos else ""}</section>')


P4_CSS = """
.sos{position:absolute;right:28pt;top:30pt;font-size:7.5pt;font-weight:800;letter-spacing:.08em;
     color:var(--accent-text);background:var(--chip);border-radius:99pt;padding:4pt 9pt;text-decoration:none}
a.tap{color:inherit;text-decoration:none}
.step{display:flex;align-items:center;gap:14pt}
.num{width:22pt;height:22pt;border-radius:99pt;background:var(--chip);color:var(--accent-text);
     font-weight:800;font-size:10pt;display:flex;align-items:center;justify-content:center;flex:none}
.st-t{font-size:11pt;font-weight:800}
.st-d{font-size:9pt;color:var(--mid);margin-top:2pt}
.go{margin-left:auto;font-size:8pt;font-weight:800;color:var(--accent-text)}
.em{border-collapse:separate;border-spacing:6pt;width:100%;table-layout:fixed;margin:-6pt}
.em th{font-size:7.5pt;font-weight:800;color:var(--soft);text-align:left;padding:0 4pt}
.em td{background:var(--card);border-radius:10pt;vertical-align:top;padding:8pt 8pt 6pt;
       border:0.4pt solid var(--line)}
.em .bat{background:none;border:none;font-size:10pt;font-weight:800;width:52pt;vertical-align:middle;padding:0}
.em a{display:flex;gap:5pt;align-items:flex-start;color:var(--ink);text-decoration:none;
      font-size:8pt;line-height:1.3;margin-bottom:6pt}
.em a .dot{margin-top:3pt}
.em .blank{height:13pt;border-bottom:1px solid var(--line)}
.tiles{display:grid;grid-template-columns:repeat(3,1fr);gap:12pt;flex:1}
.tile{background:var(--card);border-radius:var(--radius);border:0.4pt solid rgba(0,0,0,.10);
      padding:14pt;display:flex;flex-direction:column;justify-content:space-between;
      color:var(--ink);text-decoration:none;position:relative}
.tile b{font-size:12pt}
.tile small{font-size:7.5pt;color:var(--soft)}
.chk{display:flex;align-items:center;gap:10pt;flex:1;border-bottom:1px solid var(--line);font-size:10pt}
.chk:last-child{border-bottom:none}
"""


# --------------------------------------------------------------- 페이지 --
def p_cover():
    items = [("energy", "Energy menu", "pick by battery and time", "4"),
             ("rooms", "Rooms", "nine rooms, ten-minute resets", "19"),
             ("routines", "Routines &amp; weeks", "daily, weekly, the loops", "61"),
             ("tools", "Tools", "rescue, sprint, declutter", "18")]
    rows = "".join(
        f'<div style="display:flex;align-items:center;gap:12pt;padding:11pt 0;'
        f'{"" if i == len(items) - 1 else "border-bottom:1px solid var(--line)"}">'
        f'<div class="dot" style="background:{accent(SECTION_OF_TAB[k])[0]}"></div>'
        f'<div style="flex:1"><div style="font-size:10pt;font-weight:700">{t}</div>'
        f'<div style="font-size:8.5pt;color:var(--soft);margin-top:2pt">{d}</div></div>'
        f'<span class="chip">{n}</span></div>' for i, (k, t, d, n) in enumerate(items))
    title, sub = C.COVER
    return (f'<div class="head" style="flex:1;display:flex;flex-direction:column;align-items:center;'
            f'justify-content:center;text-align:center"><div class="coverrule"></div>'
            f'<span class="chip">UNDATED &middot; NO-GUILT</span>'
            f'<div style="font-size:31pt;font-weight:700;line-height:1.18;margin-top:20pt;letter-spacing:-.02em">'
            f'{title.replace("ADHD ", "ADHD<br>")}</div>'
            f'<div style="color:var(--mid);font-size:11pt;margin-top:12pt">{sub.capitalize()}.</div></div>'
            f'<div class="card" style="flex:none;padding:6pt 22pt;margin-bottom:40pt">{rows}</div>')


def p_start():
    s = C.START_HERE
    steps = "".join(
        f'<a class="card tap" href="#{target}" style="flex:none;padding:18pt 20pt">'
        f'<div class="step"><div class="num">{i}</div><div><div class="st-t">{t}</div>'
        f'<div class="st-d">{d}</div></div><div class="go">Go &rarr;</div></div></a>'
        for i, (t, d, target) in enumerate(s["steps"], 1))
    return (bp.head("Home", s["title"], s["sub"])
            + f'<div class="body">{steps}'
            + f'<div class="card" style="flex:none;padding:14pt 20pt"><div style="font-size:9pt;color:var(--mid)">'
              f'{s["note"]}</div></div>'
            + bp.prompt_card("The room that bugs me most", "start there next time", 4)
            + '</div>')


def p_energy():
    title, sub = C.TOOL_PAGES["energy"]
    head_row = '<tr><th></th>' + "".join(f"<th>{m} MIN</th>" for m in C.MINUTES) + "</tr>"
    rows = ""
    for b in C.BATTERIES:
        cells = ""
        for m in C.MINUTES:
            items = "".join(f'<a href="#{t}"><span class="dot sm"></span><span>{txt}</span></a>'
                            for txt, t in C.ENERGY[(b, m)])
            cells += f'<td>{items}<div class="blank"></div></td>'
        rows += f'<tr><td class="bat">{b}</td>{cells}</tr>'
    return (bp.head("Energy", title, sub)
            + f'<div class="body"><table class="em">{head_row}{rows}</table>'
            + bp.prompt_card("Today's pick", "one is enough", 3)
            + '</div>')


def p_house_map():
    title, sub = C.TOOL_PAGES["house-map"]
    rooms = [(k, n) for k, n, *_ in C.ROOMS] + [C.MY_ROOM]
    tiles = "".join(
        f'<a class="tile" href="#{k}"><b>{n}</b><div><small>Last reset</small>'
        f'<div class="field" style="margin-top:4pt"></div></div></a>' for k, n in rooms)
    return bp.head("Home", title, sub) + f'<div class="body"><div class="tiles">{tiles}</div></div>'


def p_room(key):
    key, name, steps, done, tools, deep = next(r for r in C.ROOMS if r[0] == key)
    chk = "".join(f'<div class="chk"><div class="box"></div><span class="num" style="width:18pt;height:18pt;'
                  f'font-size:8pt">{i}</span>{s}</div>' for i, s in enumerate(steps, 1))
    tool_chips = " ".join(f'<span class="chip" style="margin:0 4pt 4pt 0">{t}</span>' for t in tools)
    dates = "".join('<div class="field" style="flex:1"></div>' for _ in range(5))
    return (bp.head("Rooms", name, "Ten minutes, top to bottom. Then stop.")
            + '<div class="body">'
            + f'<div class="card" style="flex:1.4"><div class="label">10-minute reset</div>'
              f'<div style="flex:1;display:flex;flex-direction:column">{chk}</div></div>'
            + f'<div class="card" style="flex:none"><div class="label">Done enough</div>'
              f'<div style="font-size:11pt;font-weight:700">{done}</div></div>'
            + '<div class="row" style="flex:none">'
            + f'<div class="card" style="flex:1"><div class="label">You\'ll need</div><div>{tool_chips}</div></div>'
            + f'<div class="card" style="flex:1"><div class="label">Last reset</div>'
              f'<div style="display:flex;gap:6pt">{dates}</div></div></div>'
            + bp.prompt_card("Hotspots", "where it always piles up", 3)
            + f'<a class="tap go" href="#deep-{key}" style="flex:none">Deep clean list &rarr;</a>'
            + '</div>')


def p_rescue():
    r = C.RESCUE
    steps = "".join(
        f'<a class="card tap" href="#{t}" style="flex:1;padding:12pt 18pt;justify-content:center">'
        f'<div class="step"><div class="num">{i}</div><div><div class="st-t">{a}</div>'
        f'<div class="st-d">{b}</div></div></div></a>' for i, (a, b, t) in enumerate(r["steps"], 1))
    return (bp.head("Tools", r["title"], r["sub"])
            + f'<div class="body">{steps}'
            + f'<a class="card tap" href="#wins" style="flex:none;padding:14pt 18pt">'
              f'<div class="step"><div class="st-t">{r["after"]}</div><div class="go">Wins log &rarr;</div></div></a>'
            + '</div>')


SAMPLE = [("cover", p_cover, {"sos": False}), ("start", p_start, {}), ("energy", p_energy, {}),
          ("house-map", p_house_map, {}), ("kitchen", lambda: p_room("kitchen"), {}),
          ("rescue", p_rescue, {}),
          ("kitchen", lambda: p_room("kitchen"), {"bw": True, "pid": "kitchen-bw"})]


def build_html(specs):
    pages = [page(k, fn(), **kw) for k, fn, kw in specs]
    css = bp.CSS + P4_CSS
    html = (f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>{C.COVER[0]}</title>'
            f'<link rel="preconnect" href="https://fonts.googleapis.com">'
            f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            f'<link href="{bp.font_url()}" rel="stylesheet"><style>{css}</style></head>'
            f'<body>{"".join(pages)}</body></html>')
    os.makedirs(os.path.dirname(SRC), exist_ok=True)
    open(SRC, "w", encoding="utf-8").write(html)
    cc.check_urls(html.replace("'../assets/", "'" + cc.ASSETS_URI), OUT_DIR)
    return SRC


def to_pdf(out):
    """상품 1 to_pdf 와 같은 가드: 새 PDF 가 안 써지면 멈춘다(CLAUDE.md 조용한 실패 1)"""
    before = os.path.getmtime(out) if os.path.exists(out) else 0
    r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", *chrome_args(), "--no-pdf-header-footer",
                        f"--print-to-pdf={out}", "file:///" + SRC.replace(os.sep, "/")],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if not os.path.exists(out) or os.path.getmtime(out) <= before:
        raise RuntimeError(f"Chrome 이 새 PDF 를 쓰지 않았다\n{r.stderr[-400:]}")
    return out


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "sample"
    if mode != "sample":
        raise SystemExit("지금은 sample 만 -- 전체 빌드는 표본 확인 뒤 (PROCESS.md 4단계)")
    os.makedirs(OUT_DIR, exist_ok=True)
    shadow = os.path.join(ROOT, "assets", "shadow_v8.20-undated.png")
    if not os.path.exists(shadow):
        bp.shadow_png(shadow)
    build_html(SAMPLE)
    bp.SRC = SRC                                      # snap_cards 는 bp.SRC 를 고친다
    for n in range(1, 8):
        k = bp.snap_cards()
        print(f"snap pass {n}: pinned {k}")
        if not k:
            break
    out = to_pdf(os.path.join(OUT_DIR, f"home-reset_{VER}.pdf"))
    print("->", out)


if __name__ == "__main__":
    main()
