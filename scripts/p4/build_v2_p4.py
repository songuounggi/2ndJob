# -*- coding: utf-8 -*-
"""상품 4 v0.10~ -- 디자인 시안(claude.ai/design, TURN 25)을 틀로 109쪽(v0.10 108 · v0.11 110)을 만든다 (PROCESS.md 4단계).

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
VER = "v0.15"     # v0.15: L11 -- 빈 표 도구 쪽 5장 미리 채움, 3쪽 아래 "Set up once" (10-02) / v0.14: 2쪽 = design 순서도 시안 v1.0(34e, 10-02) / v0.10: 디자인 v1.0 첫 전체 빌드(108쪽) / v0.11: 빈 방 카드 둘째로 110쪽 / v0.12: 노트 세 종류 한 장씩 109쪽 (10-01 사용자) / v0.13: 구조 논리 S1~S4 -- 2쪽 갈림 순서도(design 시안 전 임시 배치), 3쪽 번호 뺌, Wins log 알약 (10-02 사용자)

# 쪽 key -> 대표 쪽 번호 (README §9, reference/틀_목록.md)
TEMPLATE = {"cover": 1, "flow": 2, "start": 3, "house-map": 4, "index": 5, "energy": 6, "rooms": 10, "myroom": 27, "myroom-2": 27,
            "routines": 29, "daily": 30, "rotation": 31, "monthly": 32, "seasonal": 33, "laundry-loop": 34,
            "dishes-loop": 34, "who-does-what": 36, "kids-pets": 37, "weeks": 38, "tools": 91, "rescue": 92,
            "sprint": 93, "guests": 94, "doom": 95, "declutter": 96, "where-things-live": 97, "restock": 98,
            "dopamine": 99, "body-doubling": 100, "wins": 101, "guess-actual": 102, "projects": 103,
            "big-reset": 104, "notes-ruled": 105, "notes-dots": 106, "notes-blank": 107}
TAB_OF = {"home": 0, "energy": 1, "rooms": 2, "routines": 3, "weeks": 4, "tools": 5}
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
    my = dict(C.MY_ROOMS)
    if room in my:
        name, tasks = my[room], [""] * 8
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
    # 힌트: 시안 "next slot" -> 원고 짧은 꼴 "no penalty" (10-01 사용자 -- 원고 전체 문구는 반쪽 카드 끝을 넘었다)
    page = must_replace(page, ">next slot<", f">{C.LABELS['slid_hint_short']}<", key)
    m = PILL_NEXT.search(page)
    if not m:
        raise SystemExit(f"[{key}] Next week 알약을 못 찾음")
    pill = m.group(0)
    if n == 52:
        page = page.replace(pill, "")
    if n > 1:
        # 왼쪽 알약 = 같은 모양, x84 · 폭 PREV_W (사용자 10-01). 흰 알약과 그림자는 배경에 굽는다(week_bg)
        # ← 색 = Next 알약 → 와 같은 섹션 진한색 (README §7-2). v0.10 첫 빌드는 색을 빠뜨려 글자색이었다(check_design F)
        arrow_col = re.search(r'margin-left:4px;color:(#[0-9A-Fa-f]{6})', m.group(4)).group(1)
        prev = (m.group(1) + "84" + m.group(3)
                + f'<span style="margin-right:4px;color:{arrow_col}">←</span>{C.LABELS["prev"]}' + m.group(5))
        prev = re.sub(r"width:[\d.]+px", f"width:{PREV_W}px", prev, count=1)
        page = page[:page.rfind("</div>")] + prev + "</div>"
    return page


PREV_W = 120      # "← Previous week" 9pt 800 + 여백. Next 알약(100)과 같은 모양


def week_bg(design, tpl):
    """(v0.10 에서만 썼다 -- v0.11 부터 variant_bg 가 그림자 자리가 바뀐 모든 쪽을 같은 방식으로 굽고 원본과 대조한다)
    Reset week 배경 변형: 2~51주(Previous + Next), 52주(Previous 만). 디자인 굽기 코드로 같은 방식"""
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


# 2쪽 = design 회신 "순서도 시안 v1.0"(TURN 34 · 34e, 10-02 사용자 승인) -- 인수인계서 v0.4 의 갈림 순서도. 다른 37쪽은 v1.0 그대로.
# 그림자는 design 이 배경 JPG 에 구워 보냈다(page2-bg.jpg) -- variant_bg 로 다시 굽지 않는다. v0.13 의 임시 배치(fill_flow · flow_bg)는 뺐다
FLOW_ZIP = os.path.join(ROOT, "design", "prod4", "the-adhd-home-reset-flow-v0.4-design-v1.0.zip")
FLOW_DIR = os.path.join(ROOT, "src", "p4_flow_design_v1.0")
FLOW_DH = "design_handoff_flow_v0.4"


def fill_flow(page):
    """시안 2쪽(page2_34e.html)의 <div data-page="2"> 덩어리를 그대로 쓴다. 그림 경로만 src/ 기준으로"""
    html_path = os.path.join(FLOW_DIR, FLOW_DH, "page2_34e.html")
    if not os.path.exists(html_path):
        z = zipfile.ZipFile(FLOW_ZIP)
        for i in z.infolist():
            name = i.filename if i.flag_bits & 0x800 else i.filename.encode("cp437").decode("utf-8", "replace")
            if name.endswith("/"):
                continue
            out = os.path.join(FLOW_DIR, name)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            open(out, "wb").write(z.read(i))
    h = open(html_path, encoding="utf-8").read()
    i = h.index('<div data-page="2"')
    div = element_at(h, i).replace(' data-page="2"', "", 1)
    rel = os.path.relpath(os.path.join(FLOW_DIR, FLOW_DH, "assets"), os.path.join(ROOT, "src")).replace(os.sep, "/")
    if div.count('src="assets/') != 2:
        raise SystemExit("[flow] 시안 2쪽 그림이 배경 + Open 그림자 둘이 아니다")
    return div.replace('src="assets/', f'src="{rel}/')


START_ICON = {   # 3쪽 번호(1 · 2 · 3) 자리 그림 -- 28pt 원 안 14pt, 선 1.4, 섹션 진한색 (10-02 구조 논리 S1)
    "energy": '<rect x="1.5" y="4" width="10" height="6.5" rx="1.5"/><path d="M13 6v2.5"/><path d="M3.5 6.2v2.2M5.7 6.2v2.2"/>',
    "house-map": '<path d="M2 7.2 7 2.8l5 4.4V12H2z"/><path d="M5.8 12V9h2.4v3"/>',
    "rescue": '<circle cx="7" cy="7" r="5.2"/><circle cx="7" cy="7" r="2.2"/><path d="M3.3 3.3 5.4 5.4M10.7 3.3 8.6 5.4M3.3 10.7l2.1-2.1M10.7 10.7 8.6 8.6"/>',
}


def fill_start(page):
    """3쪽: 번호 원 안의 숫자를 그림으로, 카드 제목을 원고로, 첫 두 카드 위에 "Doable today? Pick one way in." 라벨.
    카드 자리·모양은 시안 그대로라 배경을 다시 굽지 않는다"""
    S = C.START_HERE
    old = [("Check your battery", "energy"), ("Pick one room", "house-map"), ("All too much?", "rescue")]
    for i, ((t0, tg), (t, _, tg2)) in enumerate(zip(old, S["steps"])):
        if tg != tg2:
            raise SystemExit(f"[start] 카드 {i + 1} 목적지가 원고와 다름: {tg} / {tg2}")
        svg = (f'<svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.4" '
               f'stroke-linecap="round" stroke-linejoin="round">{START_ICON[tg]}</svg>')
        page = must_replace(page, f'justify-content:center">{i + 1}</span>', f'justify-content:center">{svg}</span>', "start")
        page = must_replace(page, f'>{t0}</span>', f'>{H.escape(t)}</span>', "start")
    label = (f'<div style="position:absolute;left:84px;top:119px;height:14px;line-height:14px;{LABEL_CSS}">'
             f'{H.escape(S["pick"]).upper()}</div>')
    page = start_setup(page)
    return page[:page.rfind("</div>")] + label + "</div>"


def start_setup(page):
    """3쪽 아래 카드: 옛 "The room that bugs me most" + 9줄 -> "Set up once" (10-02 사용자, L11). 카드 자리·크기는 시안 그대로.
    쓰는 칸 둘(줄 하나씩) + 다른 쪽으로 가는 줄 둘 -- 빈 방 이름(27, 29쪽 Room name)과 짝 나누기(38쪽)는 그 쪽에 쓴다(L5 같은 기록 두 곳 금지)"""
    title, hint, fields, links = C.START_HERE["setup"]
    old = re.search(r'<div style="position:absolute;left:108px;top:496px;display:flex;gap:10px;align-items:baseline">'
                    r'<span style="font-size:12px;font-weight:800">' + re.escape(C.START_PROMPT[0]) + r'</span>.*?</div>'
                    r'<div style="position:absolute;left:108px;top:516px;width:452px">(?:<div [^>]*></div>){9}</div>', page)
    if not old:
        raise SystemExit("[start] 아래 카드(The room that bugs me most + 9줄)를 못 찾음")
    head = lambda y, a, b, extra="": (f'<div style="position:absolute;left:108px;top:{y}px;width:452px;display:flex;gap:10px;'
                                      f'align-items:baseline"><span style="font-size:10.5px;font-weight:800">{H.escape(a)}</span>'
                                      f'<span style="font-size:8.5px;color:#66716B">{H.escape(b)}</span>{extra}</div>')
    line = lambda y: (f'<div style="position:absolute;left:108px;top:{y}px;width:452px;box-sizing:border-box;height:26px;'
                      f'border-bottom:0.6px solid #E3E9E5"></div>')
    go = lambda k, t: f'<a href="#{k}">{H.escape(t)}<span style="margin-left:4px;color:#537364">→</span></a>'
    rooms = "".join(go(k, f'{C.LABELS["room"]} {n[-1]}') for k, n in C.MY_ROOMS)
    right = lambda inner: f'<span style="margin-left:auto;display:flex;gap:14px;font-size:9px;font-weight:800">{inner}</span>'
    new = (f'<div style="position:absolute;left:108px;top:496px;display:flex;gap:10px;align-items:baseline">'
           f'<span style="font-size:12px;font-weight:800">{H.escape(title)}</span><span style="font-size:8.5px;color:#66716B">{H.escape(hint)}</span></div>'
           + head(526, *fields[0]) + line(538)
           + head(588, *fields[1]) + line(600)
           + head(660, *links[0], right(rooms))
           + head(700, *links[1], right(go("who-does-what", pages_p4.title_of("who-does-what")))))
    return page[:old.start()] + new + page[old.end():]


def fill(page, key):
    if key == "flow":
        return fill_flow(page)
    if key == "start":
        return fill_start(page)
    if key in dict(C.MY_ROOMS):          # 시안 27쪽 제목 "My room" -> "My room 1" / "My room 2" (v0.11)
        return must_replace(page, ">My room<", f">{dict(C.MY_ROOMS)[key]}<", key)
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
    if key == "dopamine":       # 시안 "podcasts, audiobooks" 가 카드 오른쪽 끝을 넘었다 -> 원고를 줄임 (10-01 사용자)
        page = must_replace(page, ">podcasts, audiobooks<", f">{C.DOPAMINE[2][1][1]}<", key)
        return prefill_cards(page, key)
    if key in C.PREFILL:
        return prefill_table(page, key)
    return page


ROW_CSS = "height:26px;display:flex;align-items:center;justify-content:flex-start;font-size:10px;font-weight:400;color:#2C3631"   # = 106쪽 Moving 줄


def prefill_table(page, key):
    """빈 표 첫 칸에 원고 PREFILL 을 위에서부터 (10-02 사용자, L11 빈 쪽 시험). 줄 = 시안 표 줄(머리 아래 26pt 간격), 글자 = 106쪽 Moving 줄.
    첫 칸 폭은 머리 라벨 폭 - 8(다음 칸과 떼기)"""
    m = re.search(r'<div style="position:absolute;left:([\d.]+)px;top:([\d.]+)px;width:([\d.]+)px;height:22px;[^"]*'
                  r'letter-spacing:0\.12em[^"]*">(ITEM|THING|TASK)</div>', page)
    if not m:
        raise SystemExit(f"[{key}] 표 머리를 못 찾음")
    x, y, w = float(m.group(1)), float(m.group(2)) + 22, float(m.group(3)) - 8
    rows = "".join(f'<div style="position:absolute;left:{x:g}px;top:{y + 26 * i:g}px;width:{w:g}px;{ROW_CSS}">{H.escape(t)}</div>'
                   for i, t in enumerate(C.PREFILL[key]))
    return page[:page.rfind("</div>")] + rows + "</div>"


def prefill_cards(page, key):
    """101쪽 카드 5장: 카드마다 줄 3개 중 위 두 줄에 예시, 셋째 줄은 빈 줄"""
    empty = '<div style="box-sizing:border-box;height:26px;border-bottom:0.6px solid #E3E9E5"></div>'
    blocks = list(re.finditer(r'(<div style="position:absolute;left:[\d.]+px;top:[\d.]+px;width:[\d.]+px">)((?:' + re.escape(empty) + r'){3})</div>', page))
    if len(blocks) != len(C.PREFILL[key]):
        raise SystemExit(f"[{key}] 카드 줄 묶음 {len(blocks)} != {len(C.PREFILL[key])}")
    out, pos = [], 0
    for b, ex in zip(blocks, C.PREFILL[key]):
        rows = "".join(empty.replace('"></div>', f';display:flex;align-items:center;font-size:9.5px;color:#2C3631">{H.escape(t)}</div>')
                       for t in ex) + empty
        out.append(page[pos:b.start()] + b.group(1) + rows + "</div>")
        pos = b.end()
    return "".join(out) + page[pos:]


# 시안에 박힌 옛 문구 -> 원고의 새 문구 (10-01 사용자, 써 보기 6단계에서 문구 모순·오타). 새 문구는 원고에 있어야 한다
COPY_FIX = [
    (lambda k: k == "sprint", "Stop when the last ring is done.", lambda: C.SPRINT[1].split(". ", 1)[1]),
    (lambda k: k == "monthly", "One a month. Any order.", lambda: C.TOOL_PAGES["monthly"][1]),
    (lambda k: k == "daily", "Once a day, one small thing.", lambda: C.TOOL_PAGES["daily"][1]),
    (lambda k: k == "rotation", "Slide it to the next.", lambda: C.WEEKLY_ROTATION_SUB.split("? ", 1)[1]),
    (lambda k: k.startswith("day-"), "PICK THREE AT MOST", lambda: C.DAY_PAGE_CARDS[0][1].upper()),
    (lambda k: k == "cover", "nine rooms, ten-minute resets", lambda: C.COVER_ITEMS[1][1]),     # v0.11 빈 방 둘째로 열 방
    # 할 일이 눌린다는 안내 (v0.11 재시험: "목록인 줄 알고 지나친다" 3명)
    (lambda k: k == "energy", "Pick by battery and time, not by day.", lambda: C.TOOL_PAGES["energy"][1]),
    # "Vacuum one room" 은 아무 방인데 거실 카드로 갔다 -> 원고 "Vacuum the living room" (10-02 사용자, 구조 논리 S3).
    # 7~9쪽 목록은 원고에서 만들어 이미 바뀌고, 6쪽 칸은 시안 글자라 여기서 (check_plan 1 이 v0.13 첫 빌드에서 잡음)
    (lambda k: k == "energy", ">Vacuum one room<",
     lambda: ">" + [t for t, _ in C.ENERGY[("Medium", 10)] if t.startswith("Vacuum")][0] + "<"),
]


LABEL_CSS = "font-size:7.5px;font-weight:800;letter-spacing:0.12em;color:#66716B"     # 시안 칸 라벨(TODAY I'LL DO 등)
HINT_CSS = "font-size:8.5px;color:#66716B"                                             # 시안 제목 옆 작은 글씨(no penalty)
DAY_MENU_CARD = dict(x=84, y=628.6, w=500, h=114)   # 하루 쪽 마지막 카드(538+74.6=612.6) 아래 16 · 알약(754) 위


def additions(page, key):
    """6단계 써 보기 뒤 사용자 결정(10-01)으로 시안에 더한 것. 모양은 시안에 이미 있는 요소를 그대로 쓴다.
    - 39~90쪽: Wins 제목 옆 "this week"(= Slid 의 "no penalty" 모양) · 제목 오른쪽 "WEEK OF ____" 날짜 칸
    - 7~9쪽: 마지막 카드 아래 "FROM THE ENERGY MENU" 카드 -- 그 배터리의 할 일을 분 별로(누르면 그 일이 있는 쪽)
    - 11~29쪽 방 카드: 아래 왼쪽 "← Energy menu" 알약(= 7~9쪽 알약, 폭 100)
    - 11~29쪽 방 카드 · 7~9쪽: "Wins log →" 알약 (10-02, 구조 논리 S2)
    그림자를 받는 카드·알약은 variant_bg 가 디자인 굽기 코드로 배경을 다시 굽는다"""
    if re.fullmatch(r"w\d+", key):
        page = must_replace(page, '<span style="font-size:12px;font-weight:800">Wins</span>',
                            f'<span style="font-size:12px;font-weight:800">Wins</span><span style="{HINT_CSS}">'
                            f'{C.LABELS["wins_hint"]}</span>', key)
        # 날짜 칸은 "This week's rooms" 카드 안, 제목과 같은 줄 오른쪽(148~170, 표 머리 176 위). 처음엔 카드 밖 바탕(라벤더)에
        # 두었더니 쓰는 줄이 안 보였다 -- 시안의 쓰는 줄은 늘 흰 카드 안이다
        field = (f'<div style="position:absolute;left:392px;top:148px;width:168px;height:22px;display:flex;align-items:flex-end;'
                 f'gap:8px"><span style="{LABEL_CSS};padding-bottom:3px">{C.LABELS["week_of"].upper()}</span>'
                 f'<div style="flex:1;box-sizing:border-box;height:22px;border-bottom:0.6px solid #E3E9E5"></div></div>')
        page = page[:page.rfind("</div>")] + field + "</div>"
    elif key.startswith("day-"):
        b = key[4:]
        c = DAY_MENU_CARD
        rows = []
        for i, m in enumerate(C.MINUTES):
            tasks = C.ENERGY.get((b, m), [])
            links = " · ".join(f'<a href="#{tg}">{H.escape(t)}</a>' for t, tg in tasks)
            rows.append(f'<div style="position:absolute;left:{c["x"] + 24}px;top:{c["y"] + 40 + 14 * i:g}px;width:{c["w"] - 48}px;'
                        f'height:14px;display:flex;gap:8px;font-size:8.5px;line-height:14px;white-space:nowrap">'
                        f'<span style="flex:none;width:38px;{LABEL_CSS}">{m} MIN</span><span>{links}</span></div>')
        card = (f'<div style="position:absolute;left:{c["x"]}px;top:{c["y"]:g}px;width:{c["w"]}px;height:{c["h"]}px;'
                f'border-radius:16px;background:#FFFFFF;box-sizing:border-box;"></div>'
                f'<div style="position:absolute;left:{c["x"] + 24}px;top:{c["y"] + 18:g}px;width:{c["w"] - 48}px;height:22px;'
                f'display:flex;align-items:center;justify-content:flex-start;{LABEL_CSS}">{C.LABELS["from_menu"].upper()} · '
                f'{C.LABELS["tap_one"].upper()}</div>'
                + "".join(rows))
        page = page[:page.rfind("</div>")] + card + wins_pill(374, "#537364") + "</div>"
    elif key == "house-map":
        # 9번째 타일 = 빈 방 둘 (v0.11, 10-01 사용자) -- 타일 모양 그대로, 이름 "My rooms", Go 자리에 "Room 1 →" "Room 2 →"
        page = must_replace(page, '<span style="font-size:12.5px;font-weight:800">My room</span>',
                            f'<span style="font-size:12.5px;font-weight:800">{C.LABELS["my_rooms"]}</span>', key)
        i = page.index(f'>{C.LABELS["my_rooms"]}<')
        go = re.search(r'<span style="align-self:flex-end;margin-top:10px;font-size:9px;font-weight:800">Go'
                       r'(<span style="margin-left:4px;color:#7D6A28">→</span>)</span>', page[i:])    # 시안은 글자(linkify 가 링크로)
        if not go:
            raise SystemExit("[house-map] My rooms 타일의 Go 를 못 찾음")
        two = ('<div style="align-self:flex-end;margin-top:10px;display:flex;gap:12px;font-size:9px;font-weight:800">'
               + "".join(f'<a href="#{k}">{C.LABELS["room"]} {n[-1]}{go.group(1)}</a>' for k, n in C.MY_ROOMS) + '</div>')
        page = page[:i + go.start()] + two + page[i + go.end():]
    elif key == "rooms":
        # 10쪽 표에 My room 2 줄 (v0.11): 줄 26 그대로 아래로 하나 -- 가로선 하나 · 세로선 26 · 카드 292 -> 318(아래 18 유지)
        row = re.search(r'(<div style="position:absolute;left:108px;top:386px;[^"]*">)My room(</div>)'
                        r'(<div style="position:absolute;left:410px;top:386px;[^"]*">.*?</div>)'
                        r'(<div style="position:absolute;left:510px;top:386px;[^"]*">)27(</div>)', page, re.S)
        if not row:
            raise SystemExit("[rooms] My room 줄을 못 찾음")
        n1, n2 = (n for _, n in C.MY_ROOMS)
        first = row.group(1) + n1 + row.group(2) + row.group(3) + row.group(4) + "27" + row.group(5)
        second = (first.replace("top:386px", "top:412px").replace(f">{n1}<", f">{n2}<")
                  .replace(">27<", ">29<"))       # 쪽 번호는 renumber 가 실제 쪽으로 다시 쓴다
        page = page[:row.start()] + first + second + page[row.end():]
        page = must_replace(page, "M108,412 H560 ", "M108,412 H560 M108,438 H560 ", key)
        page = must_replace(page, "M410,182 V408 M510,182 V408 ", "M410,182 V434 M510,182 V434 ", key)
        page = must_replace(page, "left:84px;top:138px;width:500px;height:292px;",
                            "left:84px;top:138px;width:500px;height:318px;", key)
    elif key == "index":
        # 5쪽 목차 Rooms 칸에 My room 2 줄 (v0.11). 왼쪽 카드(628)는 위에서 흘러 채우는 구조라 줄 하나(20)가 들어간다
        row = re.search(r'(<a href="#" style="display:flex;justify-content:space-between;align-items:center;height:20px;'
                        r'padding-left:13px;font-size:9.5px"><span>)My room(<span[^>]*>→</span></span>'
                        r'<span[^>]*>)27(</span></a>)', page)
        if not row:
            raise SystemExit("[index] My room 줄을 못 찾음")
        n1, n2 = (n for _, n in C.MY_ROOMS)
        page = (page[:row.start()] + row.group(1) + n1 + row.group(2) + "27" + row.group(3)
                + row.group(1) + n2 + row.group(2) + "29" + row.group(3) + page[row.end():])
        page = notes_one(page, key)
    elif key == "tools":
        page = notes_one(page, key)
    elif key in ROOM_OF or key in dict(C.MY_ROOMS):
        pill = (f'<a href="#energy" style="position:absolute;left:84px;top:754px;width:100px;height:24px;border-radius:12px;'
                f'display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:800">'
                f'<span style="margin-right:4px;color:#7D6A28">←</span>{H.escape(pages_p4.title_of("energy"))}</a>')
        page = page[:page.rfind("</div>")] + pill + wins_pill(364, "#7D6A28") + "</div>"
    return page


def wins_pill(left, arrow_col):
    """"Wins log →" 알약 (10-02 사용자, 구조 논리 S2): 순서도가 "10분 하고 멈춤 → Wins log" 인데 방 카드·배터리 날 쪽에 길이 없었다.
    모양 = 시안 루프 쪽(34쪽)의 Wins log 알약(아래 754 · 높이 24 · 모서리 12), 폭은 옆 알약과 같은 100. 그림자는 variant_bg 가 굽는다"""
    return (f'<a href="#wins" style="position:absolute;left:{left}px;top:754px;width:100px;height:24px;border-radius:12px;'
            f'display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:800">'
            f'{H.escape(pages_p4.title_of("wins"))}<span style="margin-left:4px;color:{arrow_col}">→</span></a>')


def variant_bg(page, key, rel_of, tpl_html):
    """additions 로 그림자 자리가 바뀐 쪽의 배경을 디자인 굽기 코드로 다시 굽는다.
    파일 이름에 그림자 자리 지문을 붙여 낡은 배경을 다시 쓰지 않는다. 새로 넣은 자리 밖은 원본 시안 배경과 같아야 한다 --
    다르면 빌드를 멈춘다(10-01 사용자: "타협한 것들이 오류를 만들어서는 안 된다")"""
    import hashlib
    import json
    import bake_bg_p4 as K
    rects = K.rects_of(page)
    base = K.rects_of(tpl_html)
    if rects == base:                    # 시안 원본과 그림자 자리가 같으면 원본 배경 그대로
        return page
    tab = TAB_OF[[t for kk, _, t in pages_p4.specs() if kk == key][0]]
    col = {0: "mint", 1: "mint", 2: "lemon", 3: "lavender", 4: "lavender", 5: "aqua"}[tab]
    m = re.search(r'src="([^"]*/assets/(25-[\w-]+)\.jpg)"', page)
    if not m:
        raise SystemExit(f"[{key}] 원본 배경을 못 찾음")
    orig = os.path.join(DESIGN_DIR, "design_handoff_adhd_home_reset", "assets", m.group(2) + ".jpg")
    sig = hashlib.md5(json.dumps([col, tab, rects], sort_keys=True).encode()).hexdigest()[:8]
    out = os.path.join(DESIGN_DIR, "generated", f"p4-{m.group(2)[3:]}-{sig}.jpg")
    if not os.path.exists(out):
        K.bake([(out, K.COLORS[col], tab, rects)])
        changed = [r for r in rects if r not in base] + [r for r in base if r not in rects]     # 새로 넣거나 바뀐 자리
        d = K.masked_diff(orig, out, changed, pad=34)
        print(f"   배경 다시 굽기 {key}: {os.path.basename(out)} -- 새 자리 밖 원본과 차이 {d:.3f}")
        if d > 1.0:
            os.remove(out)
            raise SystemExit(f"[{key}] 다시 구운 배경이 새 자리 밖에서 원본과 다르다({d:.3f}) -- 그림자 자리를 확인")
    return page.replace(m.group(1), rel_of(out))


def copy_fix(page, key):
    for when, old, new in COPY_FIX:
        if when(key):
            n = new()
            if n.lower() == old.lower() or n.strip("<>").lower() not in " ".join(t for _, t in C.all_texts()).lower():
                raise SystemExit(f"[{key}] 새 문구가 옛 문구와 같거나 원고에 없음: {n}")
            page = must_replace(page, old, n, key)
    if key == "cover":
        # 표지 목차 알약 = 그 섹션 첫 쪽 번호 (10-01 사용자: 쪽 수 4·19·62·18 이 쪽 번호로 읽혔다 -- 다른 목차와 같은 뜻으로)
        keys = [k for k, _, _ in pages_p4.specs()]
        firsts = iter(str(keys.index(s) + 1) for s in ("energy", "rooms", "routines", "tools"))
        page, n = re.subn(r'(border-radius:9px;[^"]*">)(\d+)(</span></a>)', lambda m: m.group(1) + next(firsts) + m.group(3), page)
        if n != 4:
            raise SystemExit(f"[cover] 목차 알약 {n} != 4")
    return page


# ------------------------------------------------------------------ 링크 --
SECTION_D = {"energy": "#537364", "rooms": "#7D6A28"}


def plan_links(page, key):
    """시안에 화살표가 없지만 기획서(product4-content.md 페이지 표·3-7)가 링크로 정한 곳 (10-01 사용자)
    - 보이는 링크(→ 추가): 6쪽 배터리 Low/Medium/Full -> 7~9쪽, 10쪽 방 이름 -> 방 카드. 7~9쪽은 Index 말고 길이 없었다
    - 보이지 않는 링크(모양은 시안 그대로, 글자 위에만): 1쪽 제목 -> 2쪽, 6쪽 할 일 -> 그 일이 있는 쪽, 39~90쪽
      This week's rooms -> House map
    - 글자 끝 → 만 링크(10-01 사용자, 써 보기 6단계): 94쪽 방 이름 줄 -> 방 카드, 92쪽 2·3단계 -> 설거지·빨래 루프.
      글자 전체를 링크로 두었더니 94쪽은 체크 상자와 4pt 라 체크하다 넘어갔다. → 는 체크 상자와 멀고 링크인 게 보인다
    목적지는 relink 가 글자로 정한다(→ 만 링크인 곳은 목적지를 직접 적는다). 링크 상자는 글자 크기만큼"""
    T = link_targets()
    wrap = lambda m: f'{m.group(1)}<a href="#">{m.group(2)}</a>{m.group(3)}'
    if key == "energy":
        # 배터리 이름 칸(폭 56) -- 안쪽 span 하나로 감싸 → 가 칸을 넘으면 두 줄로 (README §7-2 "칸 폭·글자 크기 그대로")
        page, n = re.subn(r'<div (style="position:absolute;left:84px;top:\d+px;width:56px;[^"]*")>(Low|Medium|Full)</div>',
                          lambda m: f'<a href="#" {m.group(1)}><span>{m.group(2)}<span style="margin-left:4px;'
                                    f'color:{SECTION_D["energy"]}">→</span></span></a>', page)
        if n != 3:
            raise SystemExit(f"[energy] 배터리 이름 {n} != 3")
        page, n = re.subn(r'(flex:none"></span><span>)([^<]+)(</span>)',
                          lambda m: wrap(m) if H.unescape(m.group(2)).lower() in T else m.group(0), page)
    elif key == "rooms":
        names = [r[1] for r in C.ROOMS] + [n for _, n in C.MY_ROOMS]
        for nm in names:       # 시안은 & 를 그대로 쓴다(Entry & hallway)
            nm = nm if f">{nm}</div>" in page else H.escape(nm)
            page = must_replace(page, f">{nm}</div>",
                                f'>{nm}<span style="margin-left:4px;color:{SECTION_D["rooms"]}">→</span></div>', key)
    elif key == "cover":
        page = must_replace(page, ">The ADHD<br>Home Reset<", '><a href="#">The ADHD<br>Home Reset</a><', key)
    elif re.fullmatch(r"w\d+", key):
        lab = H.escape(C.LABELS["week_rooms"], quote=False)
        page = must_replace(page, f">{lab}<", f'><a href="#">{lab}</a><', key)
    elif key == "rescue":
        for a, _, tg in C.RESCUE["steps"]:
            if tg in C.RESCUE["linked"]:
                page = must_replace(page, f">{H.escape(a)}<", f">{H.escape(a)}{arrow_link(tg, TOOLS_D)}<", key)
    elif key == "guests":
        def row(m):
            head = m.group(2).split(":")[0].lower()
            tgt = "entry" if head == "entry" else T.get(head)     # "Entry" 는 방 이름이 "Entry & hallway" 라 T 에 없다
            return m.group(0) if not tgt else m.group(1) + m.group(2) + arrow_link(tgt, TOOLS_D) + m.group(3)
        page = re.sub(r'(<div style="position:absolute;left:132px;[^"]*">)([^<:]+:[^<]*)(</div>)', row, page)
    return page


TOOLS_D = "#237581"


def arrow_link(tgt, col):
    """글자 끝 → 만 누르는 링크. 손끝 여유 6pt(padding)를 주되 음수 margin 으로 배치는 그대로"""
    return (f'<a href="#{tgt}" style="padding:6px 6px 6px 0;margin:-6px -6px -6px 0">'
            f'<span style="margin-left:4px;color:{col}">→</span></a>')


def notes_one(page, key):
    """노트 세 종류 한 장씩 (v0.12, 10-01 사용자): 목차의 "Notes (blank 1)" -> "Notes (blank)", "Notes (blank 2)" 줄은 뺀다.
    5쪽은 흘러가는 목록이라 줄만 뺀다. 93쪽은 좌표 표라 마지막 줄을 빼면서 가로선 하나 · 세로선 26 · 카드 500 -> 474(아래 18 유지)"""
    blank = C.PAGE_TEXT["notes-blank"][0] + " (" + C.PAGE_TEXT["notes-blank"][1].lower() + ")"
    if key == "index":
        row2 = re.search(r'<a href="#" style="display:flex;justify-content:space-between;align-items:center;height:20px;'
                         r'padding-left:13px;font-size:9.5px"><span>Notes \(blank 2\)<span[^>]*>→</span></span><span[^>]*>108</span></a>', page)
        if not row2:
            raise SystemExit("[index] Notes (blank 2) 줄을 못 찾음")
        page = page[:row2.start()] + page[row2.end():]
        return must_replace(page, ">Notes (blank 1)<", f">{blank}<", key)
    row2 = re.search(r'<div style="position:absolute;left:108px;top:594px;[^"]*">Notes \(blank 2\)<span[^>]*>→</span></div>'
                     r'<div style="position:absolute;left:500px;top:594px;[^"]*">108</div>', page)
    if not row2:
        raise SystemExit("[tools] Notes (blank 2) 줄을 못 찾음")
    page = page[:row2.start()] + page[row2.end():]
    page = must_replace(page, ">Notes (blank 1)<", f">{blank}<", key)
    page = must_replace(page, " M108,620 H560 ", " ", key)
    page = must_replace(page, "M500,182 V616 ", "M500,182 V590 ", key)
    return must_replace(page, "left:84px;top:138px;width:500px;height:500px;", "left:84px;top:138px;width:500px;height:474px;", key)


def renumber(page, key, order):
    """인쇄된 쪽 번호 = 그 줄 링크가 실제로 가는 쪽. 시안의 숫자는 108쪽 기준이라 v0.11(110쪽)에서 29쪽 뒤가 2씩 틀린다.
    (1) 링크 안의 숫자(5쪽 목차 · 1쪽 표지 알약) (2) 표 줄의 숫자 칸(10 · 29 · 91쪽) -- 같은 높이의 링크(깊은 청소 제외).
    38쪽 Weeks 칸("WEEK n")은 주 번호라 건드리지 않는다. check_plan_p4 4 가 결과를 잰다.
    목차 쪽에만 -- 다른 쪽의 단계 번호가 우연히 링크와 같은 높이에 있어도 바뀌지 않게"""
    if key not in ("cover", "index", "rooms", "routines", "tools"):
        return page

    def in_link(m):
        dest, inner = m.group(1), m.group(2)
        if "WEEK" in inner or dest not in order:
            return m.group(0)
        return (f'<a href="#{dest}"' + re.sub(r'(<span style="[^"]*">)(\d{1,3})(</span>)',
                                                 lambda x: x.group(1) + str(order.index(dest) + 1) + x.group(3), inner) + "</a>")
    page = re.sub(r'<a href="#([^"]+)"(.*?)</a>', in_link, page, flags=re.S)
    tops = {}
    for dest, top in re.findall(r'<a href="#([^"]+)" style="position:absolute;left:[\d.]+px;top:([\d.]+)px', page):
        if not dest.startswith("deep-") and dest in order:
            tops.setdefault(top, dest)
    return re.sub(r'(<div style="position:absolute;left:[\d.]+px;top:([\d.]+)px;[^"]*">)(\d{1,3})(</div>)',
                  lambda m: m.group(1) + str(order.index(tops[m.group(2)]) + 1) + m.group(4) if m.group(2) in tops else m.group(0),
                  page)


def card_overlays(page, key):
    """카드 전체를 누르게 -- 모양은 그대로, 카드 위에 투명한 링크 상자 (10-01 사용자, 써 보기 6단계).
    4쪽 House map 은 부제가 "Tap a room." 인데 작은 "Go →" 만 눌렸다 -- 타일 위쪽(이름 ~ LAST RESET 위)만 덮어
    LAST RESET 쓰는 줄은 쓰다가 넘어가지 않게 둔다. 3쪽 Start here 는 단계 카드 3개 전체.
    Rescue 2·3단계 카드도 전체(v0.11 재시험: "→ 하나만 눌린다" 구매자 4명 -- 카드에 체크 상자가 없어 넓혀도 안전하다).
    Rescue 아래 배너 "Log it in Wins. Rescue counts. Wins log →" 도 전체(10-01 사용자 질문: 흰 카드만 덮어 배너는 글자·→ 만 눌렸다).
    흰 카드는 빈 상자 옆에 내용이 따로 놓이고(다음 카드까지가 그 카드), 배너는 상자 안에 글자·링크가 들어 있다(첫 </div> 까지)"""
    if key not in ("house-map", "start", "rescue"):
        return page
    cards = list(re.finditer(r'<div style="position:absolute;left:([\d.]+)px;top:([\d.]+)px;width:([\d.]+)px;'
                             r'height:([\d.]+)px;border-radius:16px;background:(#FFFFFF|transparent);', page))
    over = []
    for i, c in enumerate(cards):
        banner = c.group(5) == "transparent"
        end = page.index("</div>", c.start()) if banner else (cards[i + 1].start() if i + 1 < len(cards) else len(page))
        hrefs = set(re.findall(r'<a href="#([^"]+)"', page[c.start():end]))
        go = re.search(r'<a href="#([^"]+)"', page[c.start():end])
        if not go or len(hrefs) > 1:              # 목적지가 둘인 타일(4쪽 My rooms -- v0.11)은 덮지 않는다
            continue
        x, y, w, h = (float(v) for v in c.groups()[:4])
        if key == "house-map":
            h = HOUSE_TILE_LINK_H
        over.append(f'<a href="#{go.group(1)}" style="position:absolute;left:{x:g}px;top:{y:g}px;width:{w:g}px;height:{h:g}px"></a>')
    want = {"house-map": 8, "start": 3, "rescue": len(C.RESCUE["linked"]) + 1}[key]     # rescue: 단계 카드 + 아래 배너
    if len(over) != want:
        raise SystemExit(f"[{key}] 카드 링크 상자 {len(over)} != {want}")
    return page[:page.rfind("</div>")] + "".join(over) + "</div>"


HOUSE_TILE_LINK_H = 98    # 타일 176 중 위 98 -- LAST RESET 라벨(타일 위에서 약 103)보다 위. check_design 이 겹침을 잰다


def norm_rail(page):
    """왼쪽 탭 6개 = 12 + 128 x 순서 (켜진 탭 배경도 이 자리에 굽는다 -- bake_bg_p4). 시안 원본은 3쪽 WEEKS·TOOLS 4pt,
    92쪽 TOOLS 2pt, 94쪽 TOOLS 4pt 아래라 넘길 때 튀었다(써 보기 6단계, 10-01 사용자 결정으로 맞춤)"""
    n = iter(range(6))
    out, k = re.subn(r'(<a href="[^"]*" style="position:absolute;left:10px;top:)([\d.]+)(px;width:40px;height:128px;)',
                     lambda m: f"{m.group(1)}{12 + 128 * next(n)}{m.group(3)}", page)
    if k != 6:
        raise SystemExit(f"왼쪽 탭 {k} != 6")
    return out
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
    for k, n in C.MY_ROOMS:
        t[n.lower()] = k
    t["index"] = "index"
    return t


def outside_links(page):
    """<a>...</a> 밖인 구간인지 판정하는 함수"""
    spans = [(m.start(), page.index("</a>", m.start())) for m in re.finditer(r"<a\b", page)]
    return lambda i: not any(s0 <= i <= s1 for s0, s1 in spans)


def linkify(page):
    """시안이 링크로 의도했는데 <a> 가 안 걸린 곳을 <a href="#"> 로 바꾼다 -- relink 가 글자로 목적지를 정한다.
    (1) 화살표(→)가 붙은 글자 요소 (README §7-2 "링크가 걸린 곳은 →")
    (2) 38쪽 Weeks 칸 52개 (README §8 "링크 칸" 예외 -- 화살표 없이 링크)
    v0.10 첫 빌드에서 시안의 <a> 가 일부에만 있어 v0.9 보다 링크 62쪽이 빠졌다(dogfood·링크 대조로 찾음)"""
    out = page
    pat = re.compile(r'<(div|span) (style="[^"]*")>([^<]*)(<span style="margin-left:4px;color:[^"]*">→</span>)</\1>')
    ok = outside_links(out)
    out = "".join(_sub_outside(out, pat, ok, lambda m: f'<a href="#" {m.group(2)}>{m.group(3)}{m.group(4)}</a>'))
    pat = re.compile(r'<div (style="position:absolute;[^"]*")>(<span [^>]*>WEEK</span><span [^>]*>\d+</span>)</div>')
    ok = outside_links(out)
    out = "".join(_sub_outside(out, pat, ok, lambda m: f'<a href="#" {m.group(1)}>{m.group(2)}</a>'))
    return out


def _sub_outside(text, pat, ok, fn):
    pos = 0
    for m in pat.finditer(text):
        if not ok(m.start()):
            continue
        yield text[pos:m.start()]
        yield fn(m)
        pos = m.end()
    yield text[pos:]


def relink(page, key, order):
    """시안의 href 를 전부 우리 페이지 key 로. 못 정하면 멈춘다(죽은 링크 0)"""
    T = link_targets()
    seq = {"start": ["energy", "house-map", "rescue"],
           "house-map": [r[0] for r in C.ROOMS],      # 9번째 타일 My rooms 는 목적지를 직접 적은 두 링크 (v0.11)
           "cover": ["energy", "rooms", "routines", "tools"]}
    used = {k: 0 for k in seq}
    out, pos, bad = [], 0, []
    room_row = iter([r[0] for r in C.ROOMS] + [k for k, _ in C.MY_ROOMS])
    for m in re.finditer(r'<a href="([^"]*)"', page):
        a_end = page.index("</a>", m.end())
        txt = text_of(page[page.index(">", m.end()) + 1:a_end])      # 여는 태그의 속성은 빼고 글자만
        low = txt.lower()
        tgt = None
        if m.group(1)[1:] in order:                  # 목적지를 직접 적은 링크(글자 끝 → 등)
            tgt = m.group(1)[1:]
        elif txt in TAB_TARGET:
            tgt = TAB_TARGET[txt]
        elif txt == C.SOS_LABEL:
            tgt = "rescue"
        elif key == "cover" and low.startswith("the adhd"):       # 표지 제목 -> 2쪽 순서도 (기획서 페이지 표 1행)
            tgt = "flow"
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
        elif ":" in txt and txt.split(":")[0].lower() in set(T) | {"entry"}:            # Guests 줄 "Entry: ..." -> 방
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


BW_PAGE_NO_TOP = 35
BW_LINES = {"#D3DBD6": "#B4B4B4", "#E3E9E5": "#C2C2C2", "#ECF0ED": "#CCCCCC", "#E9EEEB": "#CCCCCC"}


def bw_cell(m):
    """쓰는 칸(체크 상자·동그라미 14, Last reset 칸): 흰 바탕 + 회색 테두리 -- 연회색 면은 인쇄하면 사라진다"""
    st = m.group(1)
    if re.search(r"width:14px;height:14px;border-radius:(4\.5px|50%)", st) or re.search(r"^height:26px;border-radius:8px;", st):
        st = re.sub(r"background:#[0-9A-Fa-f]{6}", "background:#FFFFFF;border:0.6px solid #9A9A9A;box-sizing:border-box", st)
    return f'style="{st}"'


def to_bw(page, num):
    # 그림은 전부 뺀다(배경 JPG·구운 Reset week 배경·2쪽 그림자 PNG) -- 흑백판 = 배경 없이 + 카드 테두리 (10-01 사용자).
    # v0.10 첫 빌드는 시안 배경(25-*)만 골라 빼서 구운 주간 배경 51장이 흑백판 40~90쪽에 컬러로 남았다(써 보기 6단계에서 찾음)
    page = re.sub(r"<img\b[^>]*>", "", page)
    # 쪽 바탕(섹션 paper 4색)은 흰 종이로 -- 회색으로 바꾸면 245 로 쪽 전체를 칠해 잉크를 쓴다. v0.10 첫 빌드는 Home 민트만
    # 바꿔 나머지 99쪽 바탕이 회색이었다(써 보기 6단계, 리뷰어·인쇄파 구매자 역할이 찾음)
    for paper in ("#F3F7F4", "#F9F8F0", "#F7F6FA", "#F2F7F8"):
        page = page.replace(f"background:{paper}", "background:#FFFFFF")
    # 인쇄용 (10-01 사용자, 써 보기 6단계 인쇄파): 선 한 단계 진하게 / 쓰는 칸 테두리 / 쪽 번호(표지 빼고)
    for a, b in BW_LINES.items():
        page = page.replace(f"solid {a}", f"solid {b}").replace(f'stroke="{a}"', f'stroke="{b}"')
    page = re.sub(r'style="([^"]*)"', bw_cell, page)
    if num > 1:
        # 쪽 번호 자리 = 위쪽 가운데, 이동 경로·SOS 와 같은 줄(top 35). v0.11 첫 판은 아래 772 라 종이 끝에서 4~6mm --
        # 가정용 프린터의 인쇄 안 되는 아래 여백(3~6mm)에 걸릴 수 있었다(써 보기 재시험, 인쇄파 구매자). 아래로 올리면(760)
        # 목차·표 카드(766 까지)와 2쪽 순서도 글자에 겹쳤다. check_v2 8 이 끝에서 18pt 이상·겹침 0·카드 밖을 잰다
        page = (page[:page.rfind("</div>")] + f'<div style="position:absolute;left:0;top:{BW_PAGE_NO_TOP}px;width:612px;text-align:center;'
                f'font-size:7.5px;font-weight:600;color:#7A7A7A">{num}</div></div>')
    # 종이에서 길 찾기 (10-01 사용자, 재시험 인쇄파): SOS 옆에 Rescue 쪽 번호 / 10쪽 · 40쪽에 쪽 번호 규칙 한 줄.
    # 번호는 쪽 목록에서 계산한다 -- 규칙 자체가 맞는지는 check_v2 8 이 잰다
    keys = [k for k, _, _ in pages_p4.specs()]
    key = keys[num - 1]
    add = ""
    if key != "cover":
        add += (f'<div style="position:absolute;left:470px;top:30px;width:72px;height:18px;display:flex;align-items:center;'
                f'justify-content:flex-end;font-size:7.5px;font-weight:600;color:#7A7A7A">'
                f'{C.LABELS["page_short"]}{keys.index("rescue") + 1}</div>')
    rule = {"rooms": C.LABELS["deep_next"], "weeks": C.LABELS["week_page"].format(p=keys.index("weeks") + 1)}.get(key)
    if rule:
        add += f'<div style="position:absolute;left:84px;top:116px;{HINT_CSS}">{rule}</div>'
    if add:
        page = page[:page.rfind("</div>")] + add + "</div>"
    page = re.sub(r"#[0-9A-Fa-f]{6}\b", lambda m: gray(m.group(0)), page)
    page = re.sub(r"rgba\((\d+),(\d+),(\d+),", lambda m: "rgba(%d,%d,%d," % ((round(
        0.2126 * int(m.group(1)) + 0.7152 * int(m.group(2)) + 0.0722 * int(m.group(3))),) * 3), page)
    # 카드·배너에 연한 회색 테두리 (사용자 10-01: 배경 없이 + 카드 테두리). 그림자가 없으니 경계가 필요하다
    page = re.sub(r"(border-radius:16px;background:(?:#FFFFFF|transparent);box-sizing:border-box;)",
                  r"\1border:0.6px solid #C9C9C9;", page)
    return page


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
    if len(order) != 109:
        raise SystemExit(f"쪽 수 {len(order)} != 109")
    pages = []
    rel = os.path.relpath(os.path.join(design, "assets"), os.path.join(ROOT, "src")).replace(os.sep, "/")
    rel_of = lambda f: os.path.relpath(f, os.path.join(ROOT, "src")).replace(os.sep, "/")
    for k in (keys or order):
        page = tpl[template_of(k)]
        page = re.sub(r' data-screen-label="[^"]*"', "", page, count=1)
        page = page.replace('src="assets/', f'src="{rel}/')
        page = fill(page, k)
        page = copy_fix(page, k)
        page = additions(page, k)
        if k != "flow":                       # 2쪽은 design 이 그림자를 구운 배경을 보냈다
            page = variant_bg(page, k, rel_of, tpl[template_of(k)])
        page = plan_links(page, k)
        page = norm_rail(page)
        page = linkify(page)
        page = relink(page, k, order)
        page = renumber(page, k, order)
        page = card_overlays(page, k)
        page = arrows(page)
        if bw:
            page = to_bw(page, order.index(k) + 1)
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
