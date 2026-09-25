# -*- coding: utf-8 -*-
"""상품 3 -- 날짜형(dated) ADHD & Wellness Planner. Prod 3 방 소유.

build_planner.py 가 테마에 `dated` 가 있으면 이 모듈을 import 한다
(student_pages 와 같은 방식). 상품 1(v8.20)의 템플릿·모양을 그대로 쓰고
갈아 끼우는 것은 넷뿐이다:

  표지            연도·주 시작을 적고, 칸 수를 실제 페이지 수로 센다
  month          열두 달 목차 대신 "한 해 한 장" -- 날짜마다 링크
  m{월}           실제 요일에 맞춘 월 달력. 날짜 -> 일간, 주 번호 -> 주간
  w{n} / d{월}-{일} 날짜가 박힌 주간·일간

키 모양은 undated 와 같다(m / d / w). 그래서 rail_key() 와 탭 하이라이트
규칙을 손대지 않고 그대로 탄다.

주는 그 해에 걸친 주 전부다: 1월 1일이 든 주부터 12월 31일이 든 주까지.
해 밖의 날(앞뒤 해)은 날짜를 흐리게 적고 링크를 걸지 않는다 -- 다른
PDF 에 있는 날이라 목적지가 없다(CLAUDE.md 500p 절 3: 목적지 없는 링크는
Chrome 이 조용히 버린다).
"""

import calendar
import datetime as dt

bp = None           # build_planner 모듈
YEAR = None
WS = 0              # 주 시작: 0 = 월요일, 6 = 일요일 (datetime.weekday 기준)
WEEKS = []          # [(n, 첫날), ...]
WEEK_OF = {}        # date -> 주 번호

DAY_ABBR = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]


def init(module):
    global bp, YEAR, WS
    bp = module
    YEAR = bp.T["year"]
    WS = bp.T["week_start"]
    bp.YEAR = YEAR              # 표지·연간 등 bp 쪽 {YEAR} 도 이 해로
    jan1, dec31 = dt.date(YEAR, 1, 1), dt.date(YEAR, 12, 31)
    start = jan1 - dt.timedelta(days=(jan1.weekday() - WS) % 7)
    n = 1
    while start <= dec31:
        WEEKS.append((n, start))
        for i in range(7):
            WEEK_OF[start + dt.timedelta(days=i)] = n
        start += dt.timedelta(days=7)
        n += 1
    # 연간 그룹 목록의 설명. undated 문구("write the month in yourself")가
    # 날짜형에서는 거짓말이 된다.
    grp = bp.GROUPS["year"]
    for i, item in enumerate(grp):
        if item[0] == "month":
            grp[i] = ("month", "Year at a glance", "every date, one tap away")


# ------------------------------------------------------------- helpers --
def days_in(m):
    return calendar.monthrange(YEAR, m)[1]


def all_days():
    d = dt.date(YEAR, 1, 1)
    while d.year == YEAR:
        yield d
        d += dt.timedelta(days=1)


def dkey(d):
    return f"d{d.month}-{d.day}"


def weekday_order():
    return [(WS + i) % 7 for i in range(7)]


def is_weekend(wd):
    return wd >= 5


def link_chip(href, text):
    return (f'<a href="#{href}" class="chip" style="text-decoration:none">'
            f'{text}</a>')


def dhead(eyebrow, title, sub="", chips=""):
    """날짜형 머리. undated 의 적는 칸(field_after) 대신 이동 칩을 둔다 --
    날짜가 이미 박혀 있으니 적을 것이 없다."""
    s = f'<div class="sub">{sub}</div>' if sub else ""
    return (f'<div class="head"><div class="eyebrow">{eyebrow}</div>'
            f'<div class="titlerow"><h1>{title}</h1>'
            f'<div style="flex:1"></div>{chips}</div>{s}</div>')


def md(d):
    return f"{calendar.month_abbr[d.month]} {d.day}"


def week_range(first):
    last = first + dt.timedelta(days=6)
    if first.month == last.month:
        return f"{calendar.month_abbr[first.month]} {first.day} &ndash; {last.day}"
    return f"{md(first)} &ndash; {md(last)}"


# --------------------------------------------------------------- pages --
def p_cover():
    """표지는 리스팅 대표 이미지다 -- 칸 수는 실제 페이지 수로 센다."""
    G = bp.GROUPS
    cal_pages = 1 + 12 + 1 + len(WEEKS) + sum(days_in(m) for m in range(1, 13))
    items = [
        ("Months, weeks &amp; days",
         f"every date of {YEAR}, all linked", str(cal_pages)),
        ("Focus tools", "for when starting is the hard part", str(len(G["focus"]))),
        ("Feelings tools", "the loop, the sting, the inner critic", str(len(G["feel"]))),
        ("Health &amp; habits", "medication, sleep, routines",
         str(len(G["health"]) + len(G["habits"]))),
        ("Life admin", "meals, money, the things that slip", str(len(G["life"]))),
        ("Blank space", "dot grid, ruled, plain", str(len(bp.note_specs()))),
    ]
    rows = "".join(
        f'<div style="display:flex;align-items:center;gap:12pt;padding:11pt 0;'
        f'{"" if i == len(items) - 1 else "border-bottom:1px solid var(--line)"}">'
        f'<div class="dot"></div>'
        f'<div style="flex:1"><div style="font-size:10pt;font-weight:700">{t}</div>'
        f'<div style="font-size:8.5pt;color:var(--soft);margin-top:2pt">{d}</div></div>'
        f'<span class="chip">{c}</span></div>'
        for i, (t, d, c) in enumerate(items))
    start = "MONDAY" if WS == 0 else "SUNDAY"
    return f"""
    <div class="head" style="flex:1;display:flex;flex-direction:column;
         align-items:center;justify-content:center;text-align:center">
      <div class="coverrule"></div>
      <span class="chip">JAN &ndash; DEC {YEAR} &middot; {start} START</span>
      <div class="covertitle" style="font-size:31pt;font-weight:700;
                  line-height:1.18;margin-top:20pt;letter-spacing:-.02em">{YEAR} ADHD &amp;<br>Wellness Planner</div>
      <div style="color:var(--mid);font-size:11pt;margin-top:12pt">
        One page a day. Skip one &mdash; nothing to catch up on.</div>
    </div>
    <div class="card" style="flex:none;padding:18pt 22pt;margin-bottom:6pt">
      <div class="label">What's inside</div>{rows}
    </div>"""


def mini(m):
    order = weekday_order()
    th = "".join(f'<th class="{"we" if is_weekend(wd) else ""}">'
                 f'{"MTWTFSS"[wd]}</th>' for wd in order)
    weeks = calendar.Calendar(firstweekday=WS).monthdayscalendar(YEAR, m)
    rows = ""
    for w in weeks:
        rows += "<tr>"
        for i, d in enumerate(w):
            we = "we" if is_weekend(order[i]) else ""
            cell = (f'<a href="#d{m}-{d}" style="color:inherit;'
                    f'text-decoration:none">{d}</a>' if d else "")
            rows += f'<td class="{we}">{cell}</td>'
        rows += "</tr>"
    return (f'<div><a href="#m{m}" style="display:block;font-size:8pt;'
            f'font-weight:700;margin-bottom:5pt;color:var(--ink);'
            f'text-decoration:none">{calendar.month_name[m]}</a>'
            f'<table class="mini"><tr>{th}</tr>{rows}</table></div>')


def p_year():
    """MONTH 탭의 첫 장. 열두 달이 한 장에, 날짜마다 그날로 간다."""
    months = "".join(mini(m) for m in range(1, 13))
    return (dhead(str(YEAR), "Year at a glance",
                  "Tap a month to open it, or a date to go straight there.")
            + f"""<div class="body">
      <div class="card" style="flex:none;padding:18pt">
        <div style="display:grid;grid-template-columns:repeat(4,1fr);
             gap:22pt 14pt">{months}</div>
      </div>
      <div class="card" style="flex:1">
        <div class="label">Three things that matter this year</div>
        <div style="flex:1;display:flex;flex-direction:column;gap:12pt">
          {''.join('<div style="display:flex;align-items:stretch;gap:10pt;flex:1">'
                   '<div class="box" style="margin-top:10pt"></div>'
                   '<div class="field" style="flex:1;height:auto"></div></div>'
                   for _ in range(3))}
        </div>
      </div></div>""")


def month_grid(m):
    order = weekday_order()
    th = ('<th style="width:30pt"></th>'
          + "".join(f'<th class="{"we" if is_weekend(wd) else ""}">'
                    f'{DAY_ABBR[wd]}</th>' for wd in order))
    rows = ""
    for w in calendar.Calendar(firstweekday=WS).monthdatescalendar(YEAR, m):
        wn = WEEK_OF.get(w[0]) or WEEK_OF.get(w[-1])
        rows += (f'<tr><td style="vertical-align:middle;text-align:center;'
                 f'padding:0">'
                 f'<a href="#w{wn}" style="font-size:7.5pt;font-weight:800;'
                 f'color:var(--soft);text-decoration:none">W{wn}</a></td>')
        for d in w:
            if d.month == m:
                rows += (f'<td class="{"we" if is_weekend(d.weekday()) else ""}">'
                         f'<a href="#{dkey(d)}" style="font-size:8.5pt;'
                         f'font-weight:700;color:var(--accent-text);'
                         f'text-decoration:none">{d.day}</a></td>')
            else:
                rows += "<td></td>"
        rows += "</tr>"
    return f'<table class="cal"><tr>{th}</tr>{rows}</table>'


def p_month(m):
    prev_c = link_chip(f"m{m - 1}", f"&lsaquo; {calendar.month_abbr[m - 1]}") if m > 1 else ""
    next_c = link_chip(f"m{m + 1}", f"{calendar.month_abbr[m + 1]} &rsaquo;") if m < 12 else ""
    return (dhead(str(YEAR), calendar.month_name[m],
                  "Tap a date for that day, or a week number for that week.",
                  chips=f'{prev_c}{next_c}')
            + '<div class="body">'
              f'<div class="card" style="flex:1;padding:16pt 18pt">'
              f'{month_grid(m)}</div>'
            + bp.field_row("This month's focus") + '</div>')


def p_weeks():
    chips = "".join(
        f'<a href="#w{n}" style="width:74pt;text-align:center;padding:11pt 0;'
        f'background:var(--chip);color:var(--accent-text);border-radius:10pt;'
        f'font-size:9.5pt;font-weight:800;text-decoration:none">{n}'
        f'<span style="font-weight:600;color:var(--mid);font-size:8pt;'
        f'margin-left:5pt">{md(first)}</span></a>'
        for n, first in WEEKS)
    return (dhead(str(YEAR), f"{len(WEEKS)} weeks",
                  "Tap a week to open it. The date is its first day.")
            + '<div class="body"><div class="card" style="flex:1">'
              '<div style="display:grid;grid-template-columns:repeat(5,74pt);'
              'gap:11pt;justify-content:center;align-content:center;'
              f'height:100%">{chips}</div></div></div>')


def p_week(n, first):
    chips = []
    for i in range(7):
        d = first + dt.timedelta(days=i)
        text = f"{DAY_ABBR[d.weekday()]} &nbsp;{d.day}"
        if d.year != YEAR:
            # 다른 해의 날 -- 목적지가 이 PDF 에 없다
            chips.append(f'<span class="chip" style="background:transparent;'
                         f'color:var(--soft)">{text}</span>')
        elif is_weekend(d.weekday()):
            chips.append(f'<a href="#{dkey(d)}" class="chip" style="'
                         f'text-decoration:none;background:var(--field);'
                         f'color:var(--mid)">{text}</a>')
        else:
            chips.append(f'<a href="#{dkey(d)}" class="chip" '
                         f'style="text-decoration:none">{text}</a>')
    months = sorted({(first + dt.timedelta(days=i)).month
                     for i in range(7)
                     if (first + dt.timedelta(days=i)).year == YEAR})
    mchips = "".join(link_chip(f"m{m}", calendar.month_abbr[m]) for m in months)
    return bp.p_week(chips=chips,
                     head_html=dhead(f"{YEAR} &middot; Week {n}",
                                     week_range(first), chips=mchips))


def p_day(d):
    n = WEEK_OF[d]
    title = f"{calendar.day_name[d.weekday()]}, {md(d)}"
    chips = (link_chip(f"m{d.month}", calendar.month_abbr[d.month])
             + link_chip(f"w{n}", f"Week {n}"))
    return bp.p_day(head_html=dhead(f"{YEAR} &middot; Daily page", title,
                                    chips=chips))


# --------------------------------------------------------------- specs --
def specs(base):
    """상품 1 의 고정 페이지 목록을 받아, 반복 세트를 날짜형으로 붙인다."""
    out = [(k, p_year if k == "month" else fn) for k, fn in base]
    for m in range(1, 13):
        out.append((f"m{m}", (lambda mm: lambda: p_month(mm))(m)))
        for day in range(1, days_in(m) + 1):
            d = dt.date(YEAR, m, day)
            out.append((dkey(d), (lambda dd: lambda: p_day(dd))(d)))
    out.append(("week", p_weeks))
    for n, first in WEEKS:
        out.append((f"w{n}", (lambda nn, ff: lambda: p_week(nn, ff))(n, first)))
    return out
