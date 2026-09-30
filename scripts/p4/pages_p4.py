# -*- coding: utf-8 -*-
"""상품 4 전체 107쪽의 페이지 목록과 페이지 함수 (build_p4.py full 이 부른다).

페이지 순서·수는 product4-content.md 3절 페이지 지도(2026-09-30 변경: 2쪽 순서도, 총 107쪽).
문구는 전부 p4_content 에서 읽는다. 모양 부품은 build_planner(상품 1)와 build_p4 의 것만 쓴다.
"""
import build_p4 as B
import p4_content as C

bp = B.bp
L = C.LABELS
DAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

PAGE_NO = {}      # key -> 쪽 번호 (SPECS 순서에서 채운다)


# ---------------------------------------------------------------- 부품 --
def table(headers, rows, widths=None, box_cols=(), row_h=24):
    """rows: 행마다 칸 문구 목록(모자라면 빈칸). box_cols 는 체크 상자를 넣을 칸 번호"""
    cols = len(headers)
    cg = "".join(f'<col style="width:{w}">' for w in widths) if widths else ""
    th = "".join(f"<th>{h}</th>" for h in headers)
    body = ""
    for r in rows:
        cells = ""
        for i in range(cols):
            v = r[i] if i < len(r) else ""
            if i in box_cols and not v:
                v = '<span class="bx"></span>'
            cells += f'<td class="c">{v}</td>' if i in box_cols else f"<td>{v}</td>"
        body += f'<tr style="height:{row_h}pt">{cells}</tr>'
    return f'<table class="tb"><colgroup>{cg}</colgroup><tr>{th}</tr>{body}</table>'


def card(label, inner, flex="none", hint=None):
    h = f'<div style="font-size:8pt;color:var(--soft);margin:-4pt 0 8pt">{hint}</div>' if hint else ""
    lab = f'<div class="label">{label}</div>' if label else ""
    return f'<div class="card" style="flex:{flex}">{lab}{h}{inner}</div>'


def blank_rows(n):
    return [[] for _ in range(n)]


def link(target, text):
    return f'<a class="tap go" href="#{target}" style="flex:none">{text} {B.ARR_R}</a>'


def title_of(key):
    rooms = {k: n for k, n, *_ in C.ROOMS}
    if key in rooms:
        return rooms[key]
    if key.startswith("notes-"):      # v0.1 은 목록에 "notes-blank-1" 이 그대로 나왔다
        kind, _, n = key[6:].partition("-")
        t, sub = C.PAGE_TEXT["notes-" + kind]
        return f"{t} ({sub.lower()}{' ' + n if n else ''})"
    if key == "routines":
        return C.PAGE_TEXT["routines"][0]
    for src in (C.TOOL_PAGES, C.PAGE_TEXT):
        if key in src:
            return src[key][0]
    return {"cover": C.COVER[0], "flow": C.FLOW["title"], "start": C.START_HERE["title"],
            "rescue": C.RESCUE["title"], "sprint": C.SPRINT[0], "guests": C.GUESTS[0],
            "doom": C.DOOM_PILE[0], "declutter": C.DECLUTTER[0], "dopamine": C.DOPAMINE[0],
            "rotation": C.ROTATION_TITLE, "laundry-loop": C.LOOP_PAGES["laundry-loop"][0],
            "dishes-loop": C.LOOP_PAGES["dishes-loop"][0],
            "day-Low": C.DAY_PAGES["Low"][0], "day-Medium": C.DAY_PAGES["Medium"][0],
            "day-Full": C.DAY_PAGES["Full"][0]}.get(key, key)


def link_list(keys, pad=7):
    rows = "".join(
        f'<a href="#{k}" style="display:flex;justify-content:space-between;padding:{pad}pt 0;'
        f'border-bottom:1px solid var(--line);color:var(--ink);text-decoration:none;font-size:9.5pt">'
        f'<span>{title_of(k)}</span><span style="color:var(--soft)">{PAGE_NO.get(k, "")}</span></a>'
        for k in keys)
    return rows


# --------------------------------------------------------------- HOME --
def p_index():
    t, sub = C.PAGE_TEXT["index"]
    N = C.SECTION_NAMES
    groups = [(N["home"], ["flow", "start", "house-map"]), (N["energy"], ["energy", "day-Low", "day-Medium", "day-Full"]),
              (N["rooms"], ["rooms"] + [r[0] for r in C.ROOMS] + ["myroom"]),
              (N["routines"], ["routines", "daily", "rotation", "monthly", "seasonal", "laundry-loop", "dishes-loop",
                            "who-does-what", "kids-pets"]),
              (N["weeks"], ["weeks"]), (N["tools"], ["tools"] + [k for k in TOOL_KEYS if not k.startswith("notes-")]
                                           + ["notes-ruled"])]
    # v0.1 은 오른쪽(Routines + Tools 18줄)이 페이지 아래로 잘렸다 -> 줄 간격을 줄이고 노트는 한 줄로, 양쪽 줄 수를 맞춘다
    lg, rg = groups[:3] + groups[4:5], groups[3:4] + groups[5:]
    left = "".join(card(g, link_list(k, 3), 1 if i == len(lg) - 1 else "none") for i, (g, k) in enumerate(lg))
    right = "".join(card(g, link_list(k, 3), 1 if i == len(rg) - 1 else "none") for i, (g, k) in enumerate(rg))
    return (bp.head(C.SECTION_NAMES["home"], t, sub) + f'<div class="body"><div class="row">'
            f'<div class="col" style="flex:1">{left}</div><div class="col" style="flex:1">{right}</div>'
            f'</div></div>')


# ------------------------------------------------------------- ENERGY --
def p_day(b):
    t, sub = C.DAY_PAGES[b]
    (l1, h1), (l2, h2), (l3, h3), (l4, h4) = C.DAY_PAGE_CARDS
    today = card(l1, table(["", L["task"]], blank_rows(3), ["22pt", "auto"], box_cols=(0,), row_h=30), hint=h1)
    last = (f'<div class="card" style="flex:none;flex-direction:row;align-items:center;gap:12pt">'
            f'<span class="bx" style="width:16pt;height:16pt"></span><div><div class="st-t">{l4}</div>'
            f'<div class="st-d">{h4}</div></div></div>')
    return (bp.head(C.SECTION_NAMES["energy"], t, sub) + '<div class="body">' + today
            + bp.prompt_card(l2, h2, 3) + bp.prompt_card(l3, h3, 3) + last
            + link("energy", C.TOOL_PAGES["energy"][0]) + '</div>')


# -------------------------------------------------------------- ROOMS --
def p_rooms():
    t, sub = C.PAGE_TEXT["rooms"]
    rooms = [(k, n) for k, n, *_ in C.ROOMS] + [C.MY_ROOM]
    rows = "".join(
        f'<div style="display:flex;align-items:center;padding:9pt 0;border-bottom:1px solid var(--line)">'
        f'<a href="#{k}" style="flex:1;color:var(--ink);text-decoration:none;font-size:11pt;font-weight:700">{n}</a>'
        f'<a href="#deep-{k}" class="chip" style="text-decoration:none">{L["deep_chip"]}</a>'
        f'<span style="width:34pt;text-align:right;color:var(--soft);font-size:9pt">{PAGE_NO.get(k, "")}</span></div>'
        for k, n in rooms)
    return (bp.head(C.SECTION_NAMES["rooms"], t, sub) + f'<div class="body">{card("", rows)}'
            + link("house-map", C.TOOL_PAGES["house-map"][0]) + '</div>')


def p_deep(key):
    if key == "myroom":
        name, deep = C.PAGE_TEXT["myroom"][0], []
    else:
        _, name, _, _, _, deep = next(r for r in C.ROOMS if r[0] == key)
    t, sub = C.PAGE_TEXT["deep"]
    rows = [[d] for d in deep] + blank_rows(16 - len(deep))
    return (bp.head(C.SECTION_NAMES["rooms"], t.format(room=name), sub) + '<div class="body">'
            + card("", table([L["task"], L["last_done"], "", ""], rows, ["52%", "16%", "16%", "16%"], row_h=28))
            + link(key, L["card_link"]) + '</div>')


def p_myroom():
    t, sub = C.PAGE_TEXT["myroom"]
    steps = "".join(f'<div class="chk"><div class="box"></div><span class="num" style="width:18pt;height:18pt;'
                    f'font-size:8pt">{i}</span><div class="field" style="flex:1;height:16pt"></div></div>'
                    for i in range(1, 7))
    dates = "".join('<div class="field" style="flex:1"></div>' for _ in range(5))
    return (bp.head(C.SECTION_NAMES["rooms"], t, sub) + '<div class="body">'
            + bp.field_row(L["room_name"])
            + f'<div class="card" style="flex:1.4"><div class="label">{L["reset"]}</div>'
              f'<div style="flex:1;display:flex;flex-direction:column">{steps}</div></div>'
            + bp.field_row(L["done"])
            + f'<div class="row" style="flex:none">{card(L["need"], "<div class=field></div>", 1)}'
              f'{card(L["last"], f"<div style=display:flex;gap:6pt>{dates}</div>", 1)}</div>'
            + bp.prompt_card(L["hot"], L["hot_hint"], 2)
            + link("deep-myroom", L["deep_link"]) + '</div>')


# ----------------------------------------------------------- ROUTINES --
ROUTINE_KEYS = ["daily", "rotation", "monthly", "seasonal", "laundry-loop", "dishes-loop", "who-does-what", "kids-pets"]


def p_routines():
    t, sub = C.PAGE_TEXT["routines"]
    return bp.head(C.SECTION_NAMES["routines"], t, sub) + f'<div class="body">{card("", link_list(ROUTINE_KEYS, 9))}</div>'


def p_daily():
    t, sub = C.TOOL_PAGES["daily"]
    cards = ""
    for lab, tasks in C.DAILY_RESET.items():
        rows = [[x] for x in tasks] + blank_rows(2)
        cards += card(lab, table([L["task"]] + DAYS, rows, ["37%"] + ["9%"] * 7, box_cols=range(1, 8), row_h=30), 1)
    return bp.head(C.SECTION_NAMES["routines"], t, sub) + f'<div class="body">{cards}</div>'


def p_rotation():
    # 기획서 3-4: 요일 7칸에 방을 하나씩 (2026-09-30 사용자 확정). v0.7 은 방 9줄 x 요일 격자였다
    rows = [[d] for d in DAYS]
    return (bp.head(C.SECTION_NAMES["routines"], C.ROTATION_TITLE, C.WEEKLY_ROTATION_SUB) + '<div class="body">'
            + card("", table(["", L["room"], ""], rows, ["16%", "72%", "12%"], box_cols=(2,), row_h=40))
            + bp.prompt_card(L["slid"], L["slid_hint"], 4) + '</div>')


def p_monthly():
    t, sub = C.TOOL_PAGES["monthly"]
    rows = [[x] for x in C.MONTHLY] + blank_rows(4)
    return (bp.head(C.SECTION_NAMES["routines"], t, sub) + '<div class="body">'
            + card("", table([L["task"], L["month"], ""], rows, ["62%", "26%", "12%"], box_cols=(2,), row_h=28))
            + '</div>')


def p_seasonal():
    t, sub = C.TOOL_PAGES["seasonal"]
    cards = []
    for season, tasks in C.SEASONAL.items():
        rows = [["", x] for x in tasks] + [["", f'<span style="color:var(--soft)">{L["season_extra"]}</span>']]
        cards.append(card(season, table(["", L["task"]], rows, ["22pt", "auto"], box_cols=(0,), row_h=30), 1))
    return (bp.head(C.SECTION_NAMES["routines"], t, sub) + '<div class="body">'
            f'<div class="row">{cards[0]}{cards[1]}</div><div class="row">{cards[2]}{cards[3]}</div></div>')


def p_loop(key, title, stages):
    cells = [(f'<div class="card" style="flex:1"><div style="display:flex;align-items:center;gap:10pt">'
              f'<div class="num">{i}</div><div class="st-t" style="font-size:13pt">{stage}</div>'
              f'<span class="bx" style="margin-left:auto;width:14pt;height:14pt"></span></div>'
              f'<div class="label" style="margin-top:14pt">{L["stuck"]}</div>'
              f'<div style="font-size:10pt">{fix}</div></div>') for i, (stage, fix) in enumerate(stages, 1)]
    title, sub = C.LOOP_PAGES[key]
    return (bp.head(C.SECTION_NAMES["routines"], title, sub) + '<div class="body">'
            f'<div class="row">{cells[0]}{cells[1]}</div><div class="row">{cells[2]}{cells[3]}</div>'
            + bp.prompt_card(L["my_fix"], "", 3) + link("wins", C.TOOL_PAGES["wins"][0]) + '</div>')


def p_who():
    t, sub = C.TOOL_PAGES["who-does-what"]
    return (bp.head(C.SECTION_NAMES["routines"], t, sub) + '<div class="body">'
            + card("", table([L["task"], L["who"], L["how_often"], L["turn"]], blank_rows(17),
                             ["40%", "20%", "20%", "20%"], row_h=28)) + '</div>')


def p_kids():
    t, sub = C.TOOL_PAGES["kids-pets"]
    return (bp.head(C.SECTION_NAMES["routines"], t, sub) + '<div class="body">'
            + card(L["kids"], table([L["task"], L["who"], L["age"]], blank_rows(7), ["60%", "25%", "15%"], row_h=26))
            + card(L["pets"], table([L["task"]] + DAYS, blank_rows(5), ["37%"] + ["9%"] * 7,
                                    box_cols=range(1, 8), row_h=26)) + '</div>')


# -------------------------------------------------------------- WEEKS --
def p_weeks():
    t, sub = C.PAGE_TEXT["weeks"]
    chips = "".join(f'<a href="#w{w}" style="text-align:center;padding:11pt 0;background:var(--chip);'
                    f'color:var(--accent-text);border-radius:10pt;font-size:9.5pt;font-weight:800;'
                    f'text-decoration:none">{w}</a>' for w in range(1, 53))
    return (bp.head(C.SECTION_NAMES["weeks"], t, sub) + '<div class="body"><div class="card" style="flex:1">'
            '<div style="display:grid;grid-template-columns:repeat(5,74pt);gap:11pt;justify-content:center;'
            f'align-content:center;height:100%">{chips}</div></div></div>')


def p_week(n):
    t, sub = C.WEEK_PAGE
    rows = [[d] for d in DAYS]
    # 칸 이름이 House map 으로 간다 (6단계 시나리오 3: 주간에서 방 카드로 갈 길이 없었다)
    rooms_label = f'<a class="tap" href="#house-map">{L["week_rooms"]} {B.ARR_R}</a>'
    # 좁은 칸이라 요일은 한 글자 (v0.1 은 MON TUE 가 칸을 넘쳐 붙었다)
    loops = table([""] + [d[0] for d in DAYS], [[L["laundry"]], [L["dishes"]]], ["30%"] + ["10%"] * 7,
                  box_cols=range(1, 8), row_h=24)
    nav = '<div style="display:flex;justify-content:space-between;flex:none">'
    nav += (f'<a class="tap go" href="#w{n - 1}" style="margin:0">{B.ARR_L}{L["prev"]}</a>' if n > 1 else "<span></span>")
    nav += (f'<a class="tap go" href="#w{n + 1}">{L["next"]} {B.ARR_R}</a>' if n < 52 else "<span></span>")
    nav += "</div>"
    return (bp.head(C.SECTION_NAMES["weeks"], t.format(n=n), sub) + '<div class="body">'
            + f'<div class="row" style="flex:none">'
              f'{card(rooms_label, table(["", L["room"], ""], rows, ["18%", "70%", "12%"], box_cols=(2,), row_h=24), 1.3)}'
              f'<div class="col" style="flex:1">{card(L["week_deep"], "<div class=field></div>")}'
              f'{card(L["week_loops"], loops, 1)}</div></div>'
            + bp.prompt_card(L["week_wins"], "", 3) + bp.prompt_card(L["slid"], L["slid_hint"], 2)
            + nav + '</div>')


# -------------------------------------------------------------- TOOLS --
TOOL_KEYS = ["rescue", "sprint", "guests", "doom", "declutter", "where-things-live", "restock", "dopamine",
             "body-doubling", "wins", "guess-actual", "projects", "big-reset",
             "notes-ruled", "notes-dots", "notes-blank-1", "notes-blank-2"]


def p_tools():
    t, sub = C.PAGE_TEXT["tools"]
    keys = TOOL_KEYS
    half = (len(keys) + 1) // 2
    return (bp.head(C.SECTION_NAMES["tools"], t, sub) + '<div class="body"><div class="row" style="flex:none">'
            f'{card("", link_list(keys[:half]), 1)}{card("", link_list(keys[half:]), 1)}</div></div>')


def p_sprint():
    t, sub = C.SPRINT
    ring = ('<svg width="54pt" height="54pt" viewBox="0 0 54 54"><circle cx="27" cy="27" r="23" fill="none" '
            'stroke="var(--accent)" stroke-width="2.4"/><text x="27" y="31" text-anchor="middle" '
            'font-size="11" font-weight="800" fill="var(--accent-text)">5:00</text></svg>')
    # 카드가 높이를 정하고(stretch) 안쪽 열이 여분 줄을 자른다. v0.3 은 align-items:flex-start 라
    # 안쪽 열이 여분 줄만큼 590px 부풀었다(check_lines 6번, LINES.md 1-4)
    rounds = "".join(
        f'<div class="card" style="flex:1;flex-direction:row;gap:16pt;align-items:stretch;min-height:0">'
        f'<div style="text-align:center;align-self:flex-start">{ring}<div class="st-d">{L["round"]} {i}</div></div>'
        f'<div style="flex:1;display:flex;flex-direction:column;min-height:0;overflow:hidden">'
        f'<div class="label">{L["did"]}</div>{bp.lines(3)}</div></div>' for i in range(1, 4))
    return (bp.head(C.SECTION_NAMES["tools"], t, sub) + f'<div class="body">{rounds}'
            + link("wins", C.TOOL_PAGES["wins"][0]) + '</div>')


def p_guests():
    t, sub, steps = C.GUESTS
    room_of = {n: k for k, n, *_ in C.ROOMS}
    room_of["Entry"] = "entry"

    def linked(s):
        head = s.split(":")[0]
        return f'<a class="tap" href="#{room_of[head]}">{s}</a>' if head in room_of else s
    rows = [["", linked(s)] for s in steps] + blank_rows(2)
    return (bp.head(C.SECTION_NAMES["tools"], t, sub) + '<div class="body">'
            + card("", table(["", L["task"]], rows, ["26pt", "auto"], box_cols=(0,), row_h=40))
            + f'<div class="card" style="flex:none"><div class="st-t">{L["hide"]}</div></div></div>')


def p_doom():
    t, sub, cats = C.DOOM_PILE
    cs = [bp.prompt_card(c, "", 5) for c in cats]
    return (bp.head(C.SECTION_NAMES["tools"], t, sub) + '<div class="body">' + bp.field_row(L["timer"])
            + f'<div class="row">{cs[0]}{cs[1]}</div><div class="row">{cs[2]}{cs[3]}</div></div>')


def p_declutter():
    t, sub, qs = C.DECLUTTER
    q = "".join(f'<div class="step" style="padding:4pt 0"><div class="num" style="width:18pt;height:18pt;'
                f'font-size:8pt">{i}</div><div style="font-size:10pt">{x}</div></div>' for i, x in enumerate(qs, 1))
    return (bp.head(C.SECTION_NAMES["tools"], t, sub) + '<div class="body">' + card("", q)
            + card("", table([L["item"], L["keep"], L["toss"], L["donate"], L["give_back"]], blank_rows(11),
                             ["44%", "14%", "14%", "14%", "14%"], box_cols=(1, 2, 3, 4), row_h=26)) + '</div>')


def simple_table_page(key, headers, widths, n, box_cols=(), row_h=26):
    t, sub = C.TOOL_PAGES[key]
    return (bp.head(C.SECTION_NAMES["tools"], t, sub) + '<div class="body">'
            + card("", table(headers, blank_rows(n), widths, box_cols=box_cols, row_h=row_h)) + '</div>')


def p_big_reset():
    t, sub = C.TOOL_PAGES["big-reset"]
    rows = [["", x] for x in C.BIG_RESET] + blank_rows(19 - len(C.BIG_RESET))
    return (bp.head(C.SECTION_NAMES["tools"], t, sub) + '<div class="body">'
            + card("", table(["", L["task"]], rows, ["26pt", "auto"], box_cols=(0,), row_h=26)) + '</div>')


def p_dopamine():
    t, sub, parts = C.DOPAMINE
    return bp.head(C.SECTION_NAMES["tools"], t, sub) + '<div class="body">' + "".join(bp.prompt_card(a, b, 2) for a, b in parts) + '</div>'


def p_notes(kind):
    t, sub = C.PAGE_TEXT["notes-" + kind]
    if kind == "dots":
        inner = f'<div class="card" style="flex:1;position:relative;overflow:hidden">{bp.dot_svg()}</div>'
    elif kind == "ruled":
        inner = f'<div class="card" style="flex:1">{bp.lines(30)}</div>'
    else:
        inner = '<div class="card" style="flex:1"></div>'
    return bp.head(C.SECTION_NAMES["tools"], t, sub) + f'<div class="body">{inner}</div>'


# -------------------------------------------------------------- 목록 --
def specs():
    """(key, 함수, tab) -- 107쪽 순서"""
    s = [("cover", B.p_cover, "home"), ("flow", B.p_flow, "home"), ("start", B.p_start, "home"),
         ("house-map", B.p_house_map, "home"), ("index", p_index, "home"),
         ("energy", B.p_energy, "energy")]
    s += [(f"day-{b}", (lambda bb: lambda: p_day(bb))(b), "energy") for b in C.BATTERIES]
    s += [("rooms", p_rooms, "rooms")]
    for k, *_ in C.ROOMS:
        s += [(k, (lambda kk: lambda: B.p_room(kk))(k), "rooms"),
              (f"deep-{k}", (lambda kk: lambda: p_deep(kk))(k), "rooms")]
    s += [("myroom", p_myroom, "rooms"), ("deep-myroom", lambda: p_deep("myroom"), "rooms")]
    s += [("routines", p_routines, "routines"), ("daily", p_daily, "routines"), ("rotation", p_rotation, "routines"), ("monthly", p_monthly, "routines"),
          ("seasonal", p_seasonal, "routines"),
          ("laundry-loop", lambda: p_loop("laundry-loop", "Laundry loop", C.LAUNDRY_LOOP), "routines"),
          ("dishes-loop", lambda: p_loop("dishes-loop", "Dishes loop", C.DISHES_LOOP), "routines"),
          ("who-does-what", p_who, "routines"), ("kids-pets", p_kids, "routines")]
    s += [("weeks", p_weeks, "weeks")] + [(f"w{n}", (lambda nn: lambda: p_week(nn))(n), "weeks") for n in range(1, 53)]
    s += [("tools", p_tools, "tools"), ("rescue", B.p_rescue, "tools"), ("sprint", p_sprint, "tools"),
          ("guests", p_guests, "tools"), ("doom", p_doom, "tools"), ("declutter", p_declutter, "tools"),
          ("where-things-live", lambda: simple_table_page("where-things-live", [L["thing"], L["home"]],
                                                          ["45%", "55%"], 19), "tools"),
          ("restock", lambda: simple_table_page("restock", [L["item"], L["full"], L["half"], L["low"], L["buy"]],
                                                ["52%", "12%", "12%", "12%", "12%"], 19, box_cols=(1, 2, 3, 4)), "tools"),
          ("dopamine", p_dopamine, "tools"),
          ("body-doubling", lambda: simple_table_page("body-doubling", [L["date"], L["with"], L["task"], L["how_long"]],
                                                      ["16%", "24%", "42%", "18%"], 19), "tools"),
          ("wins", lambda: simple_table_page("wins", [L["date"], L["did"], L["minutes"]],
                                             ["18%", "64%", "18%"], 19), "tools"),
          ("guess-actual", lambda: simple_table_page("guess-actual", [L["task"], L["guess"], L["actual"]],
                                                     ["60%", "20%", "20%"], 19), "tools"),
          ("projects", lambda: simple_table_page("projects", [L["project"], L["first_step"]],
                                                 ["40%", "60%"], 13, row_h=38), "tools"),
          ("big-reset", p_big_reset, "tools"),
          ("notes-ruled", lambda: p_notes("ruled"), "tools"), ("notes-dots", lambda: p_notes("dots"), "tools"),
          ("notes-blank-1", lambda: p_notes("blank"), "tools"), ("notes-blank-2", lambda: p_notes("blank"), "tools")]
    PAGE_NO.clear()
    PAGE_NO.update({k: i for i, (k, _, _) in enumerate(s, 1)})
    return s
