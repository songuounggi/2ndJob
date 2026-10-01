# -*- coding: utf-8 -*-
"""상품 4 v0.10~ -- 디자인 시안(claude.ai/design, TURN 25)을 틀로 108쪽을 만든다 (PROCESS.md 4단계).

디자인 인수인계: design/prod4/the-adhd-home-reset-design-v1.0.zip 의 README.md (반드시 먼저 읽을 것).
  - pages_turn25.html: 대표 38쪽. 쪽마다 612x792 상자, 배경 JPG(번짐·유리 탭·그림자·배너 번짐을 구움) 위에
    글자·선·체크 상자를 pt 절대 좌표로 올린 정적 HTML (스크립트·그라데이션·그림자 CSS 없음)
  - 이 스크립트는 대표 쪽 HTML 을 **그대로 틀로 쓰고**, 108쪽마다 내용(방·할 일·주 번호)과 링크만 갈아 끼운다.
    수치를 다시 옮겨 적지 않으므로 디자인과 어긋날 수 없다
  - 문구 원본은 여전히 p4_content.py. 페이지 순서·key 는 pages_p4.specs() 그대로(108쪽)

    python scripts/p4/build_v2_p4.py sample     # 표본 몇 쪽
    python scripts/p4/build_v2_p4.py full       # 컬러 + 흑백 108쪽

결정 (2026-10-01 사용자): Reset week 에 "← Previous week" 알약 추가 / 39쪽 힌트는 원고대로 "no penalty, just the next slot" /
흑백판 = 배경 없이 + 카드에 연한 회색 테두리. README 미결 4건은 기획서로 판단(product4-content.md 인계 절).
"""
import html as H
import os
import re
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
os.environ.setdefault("PLANNER_VERSION", "v8.20-undated")
import p4_content as C                         # noqa: E402
import pages_p4                                # noqa: E402
from chrome_auto import CHROME, chrome_args    # noqa: E402

DESIGN_ZIP = os.path.join(ROOT, "design", "prod4", "the-adhd-home-reset-design-v1.0.zip")
DESIGN_DIR = os.path.join(ROOT, "src", "p4_design_v1.0")          # src/ 는 git 밖 -- 빌드 때 압축을 푼다
DH = "design_handoff_adhd_home_reset"
VER = "v0.10"

# 쪽 key -> 대표 쪽 번호 (README §9, reference/틀_목록.md)
TEMPLATE = {"cover": 1, "flow": 2, "start": 3, "house-map": 4, "index": 5, "energy": 6, "rooms": 10, "myroom": 27,
            "routines": 29, "daily": 30, "rotation": 31, "monthly": 32, "seasonal": 33, "laundry-loop": 34,
            "dishes-loop": 34, "who-does-what": 36, "kids-pets": 37, "weeks": 38, "tools": 91, "rescue": 92,
            "sprint": 93, "guests": 94, "doom": 95, "declutter": 96, "where-things-live": 97, "restock": 98,
            "dopamine": 99, "body-doubling": 100, "wins": 101, "guess-actual": 102, "projects": 103,
            "big-reset": 104, "notes-ruled": 105, "notes-dots": 106, "notes-blank-1": 107, "notes-blank-2": 107}
TAB_TARGET = {"HOME": "index", "ENERGY": "energy", "ROOMS": "rooms", "ROUTINES": "routines",
              "WEEKS": "weeks", "TOOLS": "tools"}


def template_of(key):
    if key in TEMPLATE:
        return TEMPLATE[key]
    if key.startswith("day-"):
        return 7
    if key.startswith("deep-"):
        return 12
    if re.fullmatch(r"w\d+", key):
        return 39
    if key in {r[0] for r in C.ROOMS}:
        return 11
    raise KeyError(key)


# ------------------------------------------------------------- 디자인 읽기 --
def unpack():
    if not os.path.exists(os.path.join(DESIGN_DIR, DH, "pages_turn25.html")):
        z = zipfile.ZipFile(DESIGN_ZIP)
        for i in z.infolist():
            name = i.filename if i.flag_bits & 0x800 else i.filename.encode("cp437").decode("utf-8", "replace")
            p = os.path.join(DESIGN_DIR, name)
            if name.endswith("/"):
                os.makedirs(p, exist_ok=True)
                continue
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "wb").write(z.read(i))
    return os.path.join(DESIGN_DIR, DH)


def element_at(h, start):
    """h[start] 의 <div ...> 부터 짝이 맞는 </div> 까지"""
    depth, i = 0, start
    for m in re.finditer(r"<(/?)div\b[^>]*>", h[start:]):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return h[start:start + m.end()]
    raise ValueError("div 짝이 안 맞는다")


def templates(design):
    h = open(os.path.join(design, "pages_turn25.html"), encoding="utf-8").read()
    out = {}
    for m in re.finditer(r'<div data-screen-label="25 · (\d+)쪽', h):
        out[int(m.group(1))] = element_at(h, m.start())
    if len(out) != 38:
        raise SystemExit(f"대표 쪽 {len(out)} != 38")
    return out


# ------------------------------------------------------------- 갈아 끼우기 --
def text_of(fragment):
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", fragment))).replace("→", "").replace("←", "").strip()


def must_replace(page, old, new, key, count=1):
    if old not in page:
        raise SystemExit(f"[{key}] 틀에서 못 찾음: {old[:60]}")
    return page.replace(old, new, count)


ROOM_OF = {r[0]: r for r in C.ROOMS}
KITCHEN = ROOM_OF["kitchen"]


def fill_room(page, key):
    k, name, steps, done, tools, deep = ROOM_OF[key]
    page = must_replace(page, f">{KITCHEN[1]}<", f">{H.escape(name)}<", key)
    for old, new in zip(KITCHEN[2], steps):
        page = must_replace(page, f">{old}<", f">{H.escape(new)}<", key)
    page = must_replace(page, f">{KITCHEN[3]}<", f">{H.escape(done)}<", key)
    # 준비물 칩: 칩 줄(flex-wrap) 안을 이 방 것으로 -- 칩 모양은 첫 칩 그대로
    chip = re.search(r'(<span style="height:26px;[^"]*">)' + re.escape(KITCHEN[4][0]) + "</span>", page)
    if not chip:
        raise SystemExit(f"[{key}] 준비물 칩을 못 찾음")
    chips_old = "".join(chip.group(1) + t + "</span>" for t in KITCHEN[4])
    page = must_replace(page, chips_old, "".join(chip.group(1) + H.escape(t) + "</span>" for t in tools), key)
    return page


def fill_deep(page, key):
    room = key[5:]
    if room == "myroom":
        name, tasks = C.MY_ROOM[1], [""] * 8
    else:
        name, tasks = ROOM_OF[room][1], ROOM_OF[room][5]
    page = must_replace(page, f">{KITCHEN[1]}: deep clean<", f">{H.escape(name)}: deep clean<", key)
    for old, new in zip(KITCHEN[5], tasks):
        page = must_replace(page, f">{old}<", f">{H.escape(new)}<", key)
    return page


def fill_day(page, key):
    b = key[4:]
    t0, s0 = C.DAY_PAGES["Low"]
    t, s = C.DAY_PAGES[b]
    page = must_replace(page, f">{t0}<", f">{t}<", key)
    return must_replace(page, f">{s0}<", f">{s}<", key)


def fill_loop(page, key):
    if key == "laundry-loop":
        return page
    lt, ls = C.LOOP_PAGES["laundry-loop"]
    dt, ds = C.LOOP_PAGES["dishes-loop"]
    page = must_replace(page, f">{lt}<", f">{dt}<", key)
    page = must_replace(page, f">{H.escape(ls)}<" if H.escape(ls) in page else f">{ls}<", f">{H.escape(ds)}<", key)
    for (a0, b0), (a1, b1) in zip(C.LAUNDRY_LOOP, C.DISHES_LOOP):
        page = must_replace(page, f">{a0}<", f">{a1}<", key)
        page = must_replace(page, f">{b0}<", f">{H.escape(b1)}<", key)
    return page


PILL_NEXT = re.compile(r'(<a href="[^"]*" style="position:absolute;left:)([\d.]+)(px;top:754px;[^"]*">)(.*?)(</a>)', re.S)


def fill_week(page, key):
    n = int(key[1:])
    page = must_replace(page, ">Reset week 1<", f">Reset week {n}<", key)
    # 힌트: 원고대로 (사용자 10-01) -- 시안은 "next slot"
    page = must_replace(page, ">next slot<", f">{C.LABELS['slid_hint']}<", key)
    m = PILL_NEXT.search(page)
    if not m:
        raise SystemExit(f"[{key}] Next week 알약을 못 찾음")
    pill = m.group(0)
    if n == 52:
        page = page.replace(pill, "")
    if n > 1:
        # 왼쪽 알약 = 같은 모양, x84 · 폭 PREV_W (사용자 10-01). 흰 알약과 그림자는 배경에 굽는다(week_bg)
        prev = (m.group(1) + "84" + m.group(3)
                + f'<span style="margin-right:4px">←</span>{C.LABELS["prev"]}' + m.group(5))
        prev = re.sub(r"width:[\d.]+px", f"width:{PREV_W}px", prev, count=1)
        page = page[:page.rfind("</div>")] + prev + "</div>"
    return page


PREV_W = 120      # "← Previous week" 9pt 800 + 여백. Next 알약(100)과 같은 모양


def week_bg(design, tpl):
    """Reset week 배경 변형: 2~51주(Previous + Next), 52주(Previous 만). 디자인 굽기 코드로 같은 방식"""
    import bake_bg_p4 as K
    gen = os.path.join(DESIGN_DIR, "generated")
    mid, last = os.path.join(gen, "p4-week-mid.jpg"), os.path.join(gen, "p4-week-last.jpg")
    if not (os.path.exists(mid) and os.path.exists(last)):
        rects = K.rects_of(tpl[39])
        nxt = [r for r in rects if r["y"] == 754.0]
        body = [r for r in rects if r["y"] != 754.0]
        prev = dict(x=84.0, y=754.0, w=float(PREV_W), h=24.0, r=12.0, ban=False)
        K.bake([(mid, K.COLORS["lavender"], 4, body + nxt + [prev]), (last, K.COLORS["lavender"], 4, body + [prev])])
    return mid, last


def fill(page, key):
    if key in ROOM_OF and key != "kitchen":
        return fill_room(page, key)
    if key.startswith("deep-") and key != "deep-kitchen":
        return fill_deep(page, key)
    if key.startswith("day-"):
        return fill_day(page, key)
    if key == "dishes-loop":
        return fill_loop(page, key)
    if re.fullmatch(r"w\d+", key):
        return fill_week(page, key)
    return page


# ------------------------------------------------------------------ 링크 --
def link_targets():
    """글자 -> 페이지 key (쪽 제목·방 이름·할 일·단계 이름)"""
    t = {}
    for k, _, _ in pages_p4.specs():
        try:
            t[pages_p4.title_of(k).lower()] = k
        except Exception:
            pass
    for v in C.ENERGY.values():
        for txt, tg in v:
            t[txt.lower()] = tg
    for a, _, tg in C.RESCUE["steps"]:
        t[a.lower()] = tg
    for a, _, tg in C.FLOW["boxes"].values():
        t[a.lower()] = tg
    for k, n, *_ in C.ROOMS:
        t[n.lower()] = k
    t[C.MY_ROOM[1].lower()] = C.MY_ROOM[0]
    t["index"] = "index"
    return t


def relink(page, key, order):
    """시안의 href 를 전부 우리 페이지 key 로. 못 정하면 멈춘다(죽은 링크 0)"""
    T = link_targets()
    seq = {"start": ["energy", "house-map", "rescue"],
           "house-map": [r[0] for r in C.ROOMS] + ["myroom"],
           "cover": ["energy", "rooms", "routines", "tools"]}
    used = {k: 0 for k in seq}
    out, pos, bad = [], 0, []
    room_row = iter([r[0] for r in C.ROOMS] + ["myroom"])
    for m in re.finditer(r'<a href="([^"]*)"', page):
        a_end = page.index("</a>", m.end())
        txt = text_of(page[page.index(">", m.end()) + 1:a_end])      # 여는 태그의 속성은 빼고 글자만
        low = txt.lower()
        tgt = None
        if txt in TAB_TARGET:
            tgt = TAB_TARGET[txt]
        elif txt == C.SOS_LABEL:
            tgt = "rescue"
        elif key in seq and (low.startswith("go") or key == "cover" and used[key] < 4 and low not in T):
            tgt = seq[key][used[key]]
            used[key] += 1
        elif key == "rooms" and low == C.LABELS["deep_chip"]:
            tgt = "deep-" + next(room_row)
        elif low.startswith(C.LABELS["next"].lower()):
            tgt = f"w{int(key[1:]) + 1}"
        elif low.startswith(C.LABELS["prev"].lower()):
            tgt = f"w{int(key[1:]) - 1}"
        elif low.startswith(C.LABELS["deep_link"].lower()):
            tgt = f"deep-{key}"
        elif low.startswith(C.LABELS["card_link"].lower()):
            tgt = key[5:]
        elif key == "weeks" and re.fullmatch(r"(week )?\d+", low):
            tgt = "w" + re.search(r"\d+", low).group(0)
        elif key.startswith("day-") is False and low in ("low", "medium", "full") and key == "energy":
            tgt = "day-" + txt.capitalize()
        elif low.startswith(C.LABELS["week_rooms"].lower()):
            tgt = "house-map"
        elif ":" in txt and txt.split(":")[0].lower() in T:            # Guests 줄 "Entry: ..." -> 방
            head = txt.split(":")[0].lower()
            tgt = "entry" if head == "entry" else T[head]
        else:
            for cand in (low, re.sub(r"\s+\d+$", "", low)):
                if cand in T:
                    tgt = T[cand]
                    break
            if not tgt:      # "제목 + 한 줄 설명" 상자(순서도·목차 줄): 아는 제목 중 가장 긴 것으로 시작하면 그 쪽
                pref = [n for n in T if low.startswith(n + " ") or low == n]
                if pref:
                    tgt = T[max(pref, key=len)]
        if not tgt or tgt not in order:
            bad.append(txt or "(글자 없음)")
            tgt = "BROKEN"
        out.append(page[pos:m.start()] + f'<a href="#{tgt}"')
        pos = m.end()
    out.append(page[pos:])
    if bad:
        raise SystemExit(f"[{key}] 링크를 정하지 못함: {bad}")
    return "".join(out)


# ------------------------------------------------------------- 화살표 --
# → ← 는 Nunito 에 없어 PC 마다 다른 대체 글꼴로 찍힌다(v0.6: 맑은 고딕). 글자 크기를 따라가는 벡터로 바꾼다
ARR = ('<svg class="ar" viewBox="0 0 12 10" aria-hidden="true"><path d="M1 5h9.7M7.4 2l3.3 3-3.3 3" fill="none" '
       'stroke="currentColor" stroke-width="1.15" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def arrows(page):
    # 화살표를 앞 단어와 한 덩어리로: 넘치면 "battery →" 가 함께 다음 줄로 (README §7-2, 2쪽 시안). svg 는 그 앞에서
    # 줄이 바뀔 수 있어 화살표만 혼자 떨어졌다
    # flex 상자 안에서는 묶지 않는다 -- 글자 조각이 따로따로 flex 항목이 되어 앞 공백이 사라졌다("Open theplanner").
    # flex 한 줄 안에서는 화살표가 떨어질 일도 없다. 글자가 감싸는 상자(순서도 칸 등)에서만 묶는다
    page = re.sub(r'(<(?:span|div|a)\b[^>]*style="(?![^"]*display:flex)[^"]*"[^>]*>)([^<]*?)([^\s<>]+)(<span[^>]*>)→(</span>)',
                  r'\1\2<span style="white-space:nowrap">\3\4→\5</span>', page)
    page = page.replace("→", ARR)
    return page.replace("←", ARR.replace('class="ar"', 'class="ar l"'))


# ----------------------------------------------------------------- 흑백 --
def gray(hexcol):
    r, g, b = (int(hexcol[i:i + 2], 16) for i in (1, 3, 5))
    y = round(0.2126 * r + 0.7152 * g + 0.0722 * b)
    return "#%02X%02X%02X" % (y, y, y)


def to_bw(page):
    page = re.sub(r'<img src="[^"]*25-[^"]*"[^>]*>', "", page)                     # 배경 JPG 빼기
    page = re.sub(r"#[0-9A-Fa-f]{6}\b", lambda m: gray(m.group(0)), page)
    page = re.sub(r"rgba\((\d+),(\d+),(\d+),", lambda m: "rgba(%d,%d,%d," % ((round(
        0.2126 * int(m.group(1)) + 0.7152 * int(m.group(2)) + 0.0722 * int(m.group(3))),) * 3), page)
    # 카드·배너에 연한 회색 테두리 (사용자 10-01: 배경 없이 + 카드 테두리). 그림자가 없으니 경계가 필요하다
    page = re.sub(r"(border-radius:16px;background:(?:#FFFFFF|transparent);box-sizing:border-box;)",
                  r"\1border:0.6px solid #C9C9C9;", page)
    return page.replace("background:#F3F7F4", "background:#FFFFFF")


# ----------------------------------------------------------------- 조립 --
# 디자인은 1 CSS px = 1pt 로 그렸다(README). Chrome 인쇄는 px 를 0.75pt 로 바꾸므로 쪽을 4/3 배로 키워 612x792pt(US Letter)로.
# (v0.10 첫 표본은 이걸 빠뜨려 쪽이 459x594pt 로 나왔다 -- check_v2 가 쪽 크기를 잰다)
CSS = """@page{size:612pt 792pt;margin:0}
section.page{zoom:1.3333333}
html,body{margin:0;padding:0}
body{font-family:'Nunito',sans-serif;color:#2C3631;-webkit-print-color-adjust:exact;print-color-adjust:exact}
a{color:inherit;text-decoration:none}
section.page{width:612px;height:792px;position:relative;overflow:hidden;page-break-after:always}
section.page:last-child{page-break-after:auto}
section.page>div{margin:0}
.ar{width:1.06em;height:.88em;vertical-align:-.08em;display:inline-block}
.ar.l{transform:scaleX(-1)}
"""


def build(keys=None, bw=False):
    design = unpack()
    tpl = templates(design)
    specs = pages_p4.specs()
    order = [k for k, _, _ in specs]
    if len(order) != 108:
        raise SystemExit(f"쪽 수 {len(order)} != 108")
    pages = []
    rel = os.path.relpath(os.path.join(design, "assets"), os.path.join(ROOT, "src")).replace(os.sep, "/")
    mid, last = week_bg(design, tpl)
    rel_of = lambda f: os.path.relpath(f, os.path.join(ROOT, "src")).replace(os.sep, "/")
    for k in (keys or order):
        page = tpl[template_of(k)]
        page = re.sub(r' data-screen-label="[^"]*"', "", page, count=1)
        page = page.replace('src="assets/', f'src="{rel}/')
        page = fill(page, k)
        if re.fullmatch(r"w\d+", k) and k != "w1":
            page = re.sub(r'src="[^"]*25-week\.jpg"', f'src="{rel_of(last if k == "w52" else mid)}"', page)
        page = relink(page, k, order)
        page = arrows(page)
        if bw:
            page = to_bw(page)
        pages.append(f'<section class="page" id="{k}">{page}</section>')
    return ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>The ADHD Home Reset</title>'
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">'
            f"<style>{CSS}</style></head><body>{''.join(pages)}</body></html>")


def to_pdf(src, out):
    before = os.path.getmtime(out) if os.path.exists(out) else 0
    r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", *chrome_args(), "--no-pdf-header-footer",
                        "--virtual-time-budget=20000", f"--print-to-pdf={out}", "file:///" + src.replace(os.sep, "/")],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if not os.path.exists(out) or os.path.getmtime(out) <= before:
        raise RuntimeError(f"Chrome 이 새 PDF 를 쓰지 않았다\n{r.stderr[-400:]}")
    return out


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "sample"
    if mode == "sample":
        keys = ["cover", "flow", "start", "energy", "day-Medium", "bathroom", "deep-bathroom", "w2", "rescue",
                "declutter", "w52"]
        out_dir = os.path.join(ROOT, "output", "prod4", "sample", f"sample-{VER}")
        jobs = [("color", False), ("BW", True)]
    elif mode == "full":
        keys = None
        out_dir = os.path.join(ROOT, "output", "prod4", "planner", VER)
        jobs = [("color", False), ("BW", True)]
    else:
        raise SystemExit("mode = sample | full")
    os.makedirs(out_dir, exist_ok=True)
    for tag, bw in jobs:
        src = os.path.join(ROOT, "src", f"p4_home-reset_{VER}_{mode}_{tag}.html")
        open(src, "w", encoding="utf-8").write(build(keys, bw))
        out = to_pdf(src, os.path.join(out_dir, f"home-reset_{VER}_{tag}.pdf"))
        if mode == "full":
            final = out[:-4] + "-FINAL.pdf"
            subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "dedupe_pdf.py"), out, final], check=True)
            out = final
        print(tag, "->", out, os.path.getsize(out), "B")


if __name__ == "__main__":
    main()
