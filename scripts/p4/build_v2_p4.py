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
VER = "v0.10"     # 디자인 v1.0 첫 전체 빌드

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
    if key == "dopamine":       # 시안 "podcasts, audiobooks" 가 카드 오른쪽 끝을 넘었다 -> 원고를 줄임 (10-01 사용자)
        return must_replace(page, ">podcasts, audiobooks<", f">{C.DOPAMINE[2][1][1]}<", key)
    return page


# 시안에 박힌 옛 문구 -> 원고의 새 문구 (10-01 사용자, 써 보기 6단계에서 문구 모순·오타). 새 문구는 원고에 있어야 한다
COPY_FIX = [
    (lambda k: k == "flow", "Tap any box to go there.", lambda: C.FLOW["sub"]),
    (lambda k: k == "sprint", "Stop when the last ring is done.", lambda: C.SPRINT[1].split(". ", 1)[1]),
    (lambda k: k == "monthly", "One a month. Any order.", lambda: C.TOOL_PAGES["monthly"][1]),
    (lambda k: k == "daily", "Once a day, one small thing.", lambda: C.TOOL_PAGES["daily"][1]),
    (lambda k: k == "rotation", "Slide it to the next.", lambda: C.WEEKLY_ROTATION_SUB.split("? ", 1)[1]),
    (lambda k: k.startswith("day-"), "PICK THREE AT MOST", lambda: C.DAY_PAGE_CARDS[0][1].upper()),
]


def copy_fix(page, key):
    for when, old, new in COPY_FIX:
        if when(key):
            n = new()
            if n.lower() == old.lower() or n.lower() not in " ".join(t for _, t in C.all_texts()).lower():
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
        names = [r[1] for r in C.ROOMS] + [C.MY_ROOM[1]]
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


def card_overlays(page, key):
    """카드 전체를 누르게 -- 모양은 그대로, 카드 위에 투명한 링크 상자 (10-01 사용자, 써 보기 6단계).
    4쪽 House map 은 부제가 "Tap a room." 인데 작은 "Go →" 만 눌렸다 -- 타일 위쪽(이름 ~ LAST RESET 위)만 덮어
    LAST RESET 쓰는 줄은 쓰다가 넘어가지 않게 둔다. 3쪽 Start here 는 단계 카드 3개 전체"""
    if key not in ("house-map", "start"):
        return page
    cards = list(re.finditer(r'<div style="position:absolute;left:([\d.]+)px;top:([\d.]+)px;width:([\d.]+)px;'
                             r'height:([\d.]+)px;border-radius:16px;background:#FFFFFF;', page))
    over = []
    for i, c in enumerate(cards):
        end = cards[i + 1].start() if i + 1 < len(cards) else len(page)
        go = re.search(r'<a href="#([^"]+)"', page[c.start():end])
        if not go:
            continue
        x, y, w, h = (float(v) for v in c.groups())
        if key == "house-map":
            h = HOUSE_TILE_LINK_H
        over.append(f'<a href="#{go.group(1)}" style="position:absolute;left:{x:g}px;top:{y:g}px;width:{w:g}px;height:{h:g}px"></a>')
    want = 9 if key == "house-map" else 3
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
    t[C.MY_ROOM[1].lower()] = C.MY_ROOM[0]
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
        page = (page[:page.rfind("</div>")] + f'<div style="position:absolute;left:0;top:772px;width:612px;text-align:center;'
                f'font-size:7.5px;font-weight:600;color:#7A7A7A">{num}</div></div>')
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
        page = copy_fix(page, k)
        page = plan_links(page, k)
        if re.fullmatch(r"w\d+", k) and k != "w1":
            page = re.sub(r'src="[^"]*25-week\.jpg"', f'src="{rel_of(last if k == "w52" else mid)}"', page)
        page = norm_rail(page)
        page = linkify(page)
        page = relink(page, k, order)
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
