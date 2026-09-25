# -*- coding: utf-8 -*-
"""상품 3 와이어프레임 -- 디자인 없이 내용과 링크만. Prod 3 방 소유.

    python scripts/p3_wireframe.py 2027 mon     # -> output/p3_wireframe_2027-mon.pdf

회색 상자 + 라벨 + 실제 문구(p3_content.py). 모든 링크가 살아 있어서 GoodNotes 에서
흐름(Time links, SOS, 52 experiments)을 눌러 볼 수 있다. 디자인은 사용자가 입힌다.
계획: product3-content.md
"""
import calendar
import datetime as dt
import html as H
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p3_content as C

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
Y = int(sys.argv[1]) if len(sys.argv) > 1 else 2027
WS = 0 if (sys.argv[2] if len(sys.argv) > 2 else "mon") == "mon" else 6
TAG = f"{Y}-{'mon' if WS == 0 else 'sun'}"
SRC = os.path.join(ROOT, "src", f"p3_wireframe_{TAG}.html")
OUT = os.path.join(ROOT, "output", f"p3_wireframe_{TAG}.pdf")

WEEKS = C.year_weeks(Y, WS)
WEEK_OF = {w + dt.timedelta(i): n for n, w in enumerate(WEEKS, 1) for i in range(7)}
DAYS = [dt.date(Y, 1, 1) + dt.timedelta(i) for i in range(366 if calendar.isleap(Y) else 365)]
TOTAL = len(DAYS)
HOL = C.holidays(Y)
def home_month(first):
    """주가 속한 달 = 그 주 목요일의 달. 해를 넘는 주는 1월/12월에 붙인다."""
    th = first + dt.timedelta((3 - first.weekday()) % 7)
    return 1 if th.year < Y else 12 if th.year > Y else th.month


NOTES_IN = {}                                     # 도착일 -> [보낸 날]
for d in DAYS:
    t = C.future_note_target(d)
    NOTES_IN.setdefault(t or "mailbox", []).append(d)

# 상품 1 도구(재사용). 와이어프레임에서는 이름만 있는 자리표시 페이지.
P1 = {
    "focus": ("Focus tools", [("tasks", "Task breakdown"), ("braindump", "Brain dump"), ("session", "Focus session"),
                              ("obstacle", "Obstacle plan"), ("paralysis", "Stuck on deciding"), ("mindmap", "Mind map"),
                              ("hyperfocus", "Hyperfocus log"), ("screen", "Screen time"), ("estimate", "Guess vs actual"),
                              ("avoiding", "Why I am avoiding it"), ("deadline", "Working backwards")]),
    "feel": ("Feelings tools", [("sta", "Stop · Think · Act"), ("worry", "Cycle of worry"), ("rsd", "Rejection sensitivity"),
                                ("kind", "Talk to yourself kindly"), ("dose", "D.O.S.E."), ("gratitude", "Gratitude"),
                                ("reframe", "Reframe a belief"), ("name-it", "Name the feeling"),
                                ("boundaries", "Boundaries"), ("energy", "Energy budget")]),
    "health": ("Health & habits", [("habits-grid", "Habit tracker"), ("routines", "Morning & evening"),
                                   ("meds", "Medication log"), ("sleep", "Sleep"), ("symptoms", "Symptom tracker"),
                                   ("doctor", "Doctor visit"), ("therapy", "Therapy notes"), ("intake", "Water & food"),
                                   ("movement", "Movement"), ("cycle", "Cycle tracker")]),
    "life": ("Life admin", [("meals", "Meals & groceries"), ("wheel", "Wheel of life"), ("cleaning", "Cleaning"),
                            ("budget", "Monthly budget"), ("impulse", "Before you buy it"), ("reading", "Reading log"),
                            ("dates", "Dates to remember"), ("subs", "Subscriptions"), ("travel", "Trip checklist"),
                            ("chores", "Who does what")]),
}
NEW_TOOLS = ["dopamine", "doompile", "graveyard", "waiting"]
TABS = [("index", "INDEX"), ("sos", "SOS"), ("year", "YEAR"), ("month", "MONTH"), ("week", "WEEK"),
        ("focus", "FOCUS"), ("feel", "FEEL"), ("health", "BODY"), ("life", "LIFE"), ("notes", "NOTES")]

e = H.escape
MA = calendar.month_abbr
MN = calendar.month_name


def dk(d):
    return f"d{d.month}-{d.day}"


def md(d):
    return f"{MA[d.month]} {d.day}"


# ------------------------------------------------------------ pieces --
def chip(href, text, cls=""):
    return f'<a class="chip {cls}" href="#{href}">{text}</a>'


def box(label, inner="", flex="1", hint="", style=""):
    h = f'<span class="hint"> {e(hint.strip())}</span>' if hint else ""
    return f'<div class="box" style="flex:{flex};{style}"><div class="lab">{e(label)}{h}</div>{inner}</div>'


def lines(n):
    return '<div class="ln"></div>' * n


def fill():
    return '<div class="fill"></div>'


def head(eyebrow, title, sub="", chips=""):
    s = f'<div class="sub">{sub}</div>' if sub else ""
    return (f'<div class="hd"><div class="eb">{eyebrow}</div><div class="tr"><h1>{title}</h1>'
            f'<div class="sp"></div>{chips}</div>{s}</div>')


def rail_of(key):
    if re.fullmatch(r"(d\d+-\d+|m\d+|mp\d+|bw\d+|mr\d+|q\d)", key) or key in ("month",):
        return "month"
    if re.fullmatch(r"(w|wr)\d+", key) or key == "week":
        return "week"
    if key in ("year", "how", "kickoff", "goals", "project", "vision", "myhol", "experiments", "pixels", "admin", "bday1", "bday2", "where",
               "playbook", "mailbox", "yearreview"):
        return "year"
    for g, (_, items) in P1.items():
        if key == g or key in [k for k, _ in items]:
            return g
    if key in NEW_TOOLS:
        return "life"
    if key.startswith("note") or key == "notes":
        return "notes"
    return key


def page(key, body):
    on = rail_of(key)
    tabs = "".join(f'<a href="#{k}" class="{"on" if k == on else ""}"><span>{t}</span></a>' for k, t in TABS)
    return (f'<section class="pg" id="{key}"><nav class="rail">{tabs}</nav>'
            f'<div class="c">{body}</div><div class="pgk">{key}</div></section>')


# ------------------------------------------------------------- front --
def p_cover():
    return f"""<div style="flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center">
      <div class="eb">JAN – DEC {Y} · {"MONDAY" if WS == 0 else "SUNDAY"} START</div>
      <h1 style="font-size:34pt;margin-top:14pt">{Y} ADHD Year Planner</h1>
      <div class="sub" style="font-size:12pt;margin-top:10pt">52 experiments to find what works for your brain</div>
      <div class="box" style="flex:none;width:360pt;margin-top:40pt;text-align:left">
        <div class="lab">WHAT'S INSIDE</div>
        <div class="txt">Every date of {Y}, all linked · 52 weekly experiments · Time links between days ·
        Brain weather & ADHD tax trackers · SOS page for stuck moments · 65+ ADHD tools · Notes</div></div></div>"""


def p_how():
    H_ = C.HOW_IT_WORKS
    ideas = "".join(box(f"{i + 1}. {t}", f'<div class="txt">{e(x)}</div>', "none") for i, (t, x) in enumerate(H_["ideas"]))
    rules = "".join(f'<div class="txt">• {e(r)}</div>' for r in H_["rules"])
    return head("START HERE", H_["title"], e(H_["sub"])) + f'<div class="bd">{ideas}{box("HOW TO MOVE AROUND", rules, "1")}</div>'


def p_index():
    rows = [("how", "How this planner works"), ("sos", "SOS — I'm stuck"), ("year", "Year at a glance"),
            ("experiments", "The 52 experiments"), ("goals", "Goals · Project · Vision"), ("month", "Months"), ("week", "Weeks"),
            ("focus", "Focus tools"), ("feel", "Feelings tools"), ("health", "Health & habits"),
            ("life", "Life admin & new tools"), ("playbook", "My ADHD playbook (December)"), ("notes", "Notes")]
    inner = "".join(f'<a class="row" href="#{k}">{e(t)}<span>›</span></a>' for k, t in rows)
    return head("INDEX", "Where to?") + f'<div class="bd">{box("GO TO", inner)}</div>'


def p_sos():
    rows = "".join(f'<a class="row" href="#{k}"><b>{e(s)}</b><span class="hint">{e(h)}</span><span>›</span></a>'
                   for s, h, k in C.SOS)
    return (head("SOS", "I'm stuck", "Find the feeling, tap the line. Every page has an SOS tab.")
            + f'<div class="bd">{box("WHAT IS HAPPENING?", rows)}</div>')


def mini(m):
    th = "".join(f"<th>{'MTWTFSS'[(WS + i) % 7]}</th>" for i in range(7))
    rows = ""
    for w in calendar.Calendar(WS).monthdayscalendar(Y, m):
        rows += "<tr>" + "".join(f'<td>{f"<a href=#d{m}-{d}>{d}</a>" if d else ""}</td>' for d in w) + "</tr>"
    return (f'<div><a class="mname" href="#m{m}">{MN[m]}</a>'
            f'<table class="mini"><tr>{th}</tr>{rows}</table></div>')


def p_year():
    grid = "".join(mini(m) for m in range(1, 13))
    return (head(str(Y), "Year at a glance", "Tap a month or a date.")
            + f'<div class="bd">{box("TWELVE MONTHS", f"<div class=yg>{grid}</div>", "none")}'
            f'{box("THREE THINGS THAT MATTER THIS YEAR", lines(3), "1")}</div>')


def p_kickoff():
    return (head(str(Y), "Systems, not resolutions",
                 "Resolutions ask for willpower. Systems make it easy. Build one you'll still use in March.")
            + '<div class="bd"><div class="rw">'
            + box("WHAT WORKED LAST YEAR", lines(4)) + box("WHAT DIDN'T", lines(4)) + '</div>'
            + box("THREE SYSTEMS I'LL SET UP", "".join(f'<div class="ck"><i></i><div class="ln fl"></div></div>' for _ in range(3)), "none")
            + box("IF I ONLY DO ONE THING THIS YEAR", lines(2), "none")
            + box("WHAT I'M LEAVING IN LAST YEAR", lines(3), "1") + '</div>')


def p_experiments():
    rows = ""
    for n, first in enumerate(WEEKS, 1):
        name, _, _ = C.experiment(n)
        rows += (f'<a class="xr" href="#w{n}"><span class="wn">W{n}</span><span class="xn">{e(name)}</span>'
                 f'<span class="xd">{md(first)}</span><span class="rate">✓ ~ ✗</span></a>')
    return (head(str(Y), "The 52 experiments",
                 "One small strategy a week. Mark it on Friday: helped, sort of, not for me.")
            + f'<div class="bd">{box("TAP A WEEK", f"<div class=xl>{rows}</div>")}</div>')


def p_pixels():
    hdr = "<tr><th></th>" + "".join(f"<th>{MA[m][0]}</th>" for m in range(1, 13)) + "</tr>"
    rows = ""
    for day in range(1, 32):
        rows += f"<tr><th>{day}</th>" + "".join(
            f'<td class="{"x" if day > calendar.monthrange(Y, m)[1] else ""}"></td>' for m in range(1, 13)) + "</tr>"
    legend = " · ".join(["1 rough", "2 low", "3 okay", "4 good", "5 great"])
    return (head(str(Y), "Year in pixels — brain weather", "One square a day. Pick a color for how the day felt.")
            + f'<div class="bd">{box("LEGEND: " + legend, f"<table class=px>{hdr}{rows}</table>")}</div>')


def p_admin():
    cols = ""
    for m in range(12):
        items = "".join(f'<div class="ck"><i></i><span>{e(t)}</span></div>' for t in C.ADMIN[m])
        cols += f'<div class="am"><a href="#mp{m + 1}"><b>{MN[m + 1]}</b></a>{items}<div class="ln"></div></div>'
    return (head(str(Y), "Life admin radar", "The grown-up stuff, spread across the year. Each month's plan shows its four.")
            + f'<div class="bd">{box("TWELVE MONTHS", f"<div class=ag>{cols}</div>")}</div>')


def p_bday(part):
    ms = range(1, 7) if part == 1 else range(7, 13)
    cols = "".join(box(MN[m].upper(), '<div class="tb4"><span>name</span><span>date</span><span>buy by</span><span>idea</span></div>' + lines(3), "1")
                   for m in ms)
    return (head(str(Y), f"Birthdays & gift radar {part}/2", "Write the buy-by date ten days early.")
            + f'<div class="bd"><div class="g2">{cols}</div></div>')


def p_myhol():
    t, sub = C.MY_HOLIDAYS
    cols = "".join(box(MN[m].upper(), '<div class="tb4"><span>what</span><span></span><span>date</span><span>off?</span></div>' + lines(3), "1")
                   for m in range(1, 13))
    return (head(str(Y), t, sub)
            + f'<div class="bd"><div class="g3">{cols}</div></div>')


def p_where():
    items = ["Passport & ID", "Spare keys", "Warranties & receipts", "Important papers",
             "Password hints (not passwords)", "Chargers & cables", "Medical records", "Gift wrap & cards"]
    rows = "".join(f'<div class="tr3"><b>{e(t)}</b><div class="ln fl"></div></div>' for t in items)
    return (head("LIFE", "Where I put it", "For the things you only need once a year, and can never find.")
            + f'<div class="bd">{box("THING — WHERE IT LIVES", rows + lines(4))}</div>')


# -------------------------------------------------------- quarterly --
def p_quarter(q):
    ms = range(3 * q - 2, 3 * q + 1)
    wk = [n for n, f in enumerate(WEEKS, 1) if home_month(f) in ms]
    chips = "".join(chip(f"w{n}", f"W{n}") for n in wk)
    return (head(str(Y), f"Q{q} · {MA[ms[0]]} – {MA[ms[-1]]}", "Three months at a time.")
            + '<div class="bd">' + box("THIS QUARTER, ONE THING", lines(1), "none")
            + '<div class="rw">' + "".join(box(MN[m].upper(), lines(3)) for m in ms) + '</div>'
            + box("EXPERIMENTS: KEEP 3 · DROP 3", f'<div class="chips">{chips}</div><div class="rw">'
                  f'{box("KEEP", lines(3))}{box("DROP", lines(3))}</div>', "none")
            + box("HOBBY CHECK", '<div class="hint">started · stopped · still going — no shame</div>' + lines(3), "1")
            + '</div>')


# ----------------------------------------------------------- months --
def p_months():
    return p_year().replace("Year at a glance", "Months", 1)


def p_month(m):
    th = "<tr><th></th>" + "".join(f"<th>{calendar.day_abbr[(WS + i) % 7].upper()}</th>" for i in range(7)) + "</tr>"
    rows = ""
    for w in calendar.Calendar(WS).monthdatescalendar(Y, m):
        n = WEEK_OF.get(w[0]) or WEEK_OF.get(w[-1])
        rows += f'<tr><td class="wk"><a href="#w{n}">W{n}</a></td>'
        for d in w:
            if d.month == m:
                hol = f'<div class="hol">{e(HOL[d])}</div>' if d in HOL else ""
                rows += f'<td><a href="#{dk(d)}">{d.day}</a>{hol}</td>'
            else:
                rows += "<td class=out></td>"
        rows += "</tr>"
    nav = (chip(f"m{m - 1}", f"‹ {MA[m - 1]}") if m > 1 else "") + (chip(f"m{m + 1}", f"{MA[m + 1]} ›") if m < 12 else "")
    subs = chip(f"mp{m}", "Plan") + chip(f"bw{m}", "Brain weather") + chip(f"mr{m}", "Review")
    return (head(str(Y), MN[m], "", nav)
            + f'<div class="bd"><div class="chips">{subs}</div>'
            f'<div class="box" style="flex:1"><table class="cal">{th}{rows}</table></div></div>')


def p_mplan(m):
    t, line, _ = C.MONTHS[m - 1]
    adm = "".join(f'<div class="ck"><i></i><span>{e(x)}</span></div>' for x in C.ADMIN[m - 1])
    return (head(f"{MN[m].upper()} {Y} · PLAN", e(t), e(line), chip(f"m{m}", MA[m]))
            + '<div class="bd">' + box("THIS MONTH, ONE THING", lines(1), "none")
            + '<div class="rw">' + box("DATES & DEADLINES", lines(6)) + box("BILLS & RENEWALS", lines(6)) + '</div>'
            + '<div class="rw">' + box("BIRTHDAYS", lines(3), hint=" → gift radar") + box("APPOINTMENTS & REFILLS", lines(3)) + '</div>'
            + '<div class="rw">' + box("ADMIN RADAR", adm) + box("I'M LETTING GO OF", lines(3)) + '</div>'
            + '<div class="rw">' + box("FUN ON THE CALENDAR", lines(3), hint="plan joy like an appointment · see dopamine menu")
            + box("THIS MONTH'S EXPERIMENTS", "".join(
                f'<a class="xr" href="#w{n}"><span class="wn">W{n}</span><span class="xn">{e(C.experiment(n)[0])}</span></a>'
                for n, f in enumerate(WEEKS, 1) if home_month(f) == m)) + '</div></div>')


def p_bweather(m):
    nd = calendar.monthrange(Y, m)[1]
    th = "<tr><th></th>" + "".join(
        f'<th><a href="#d{m}-{d}">{d}</a><br><small>{"MTWTFSS"[dt.date(Y, m, d).weekday()]}</small></th>' for d in range(1, nd + 1)) + "</tr>"
    rows = "".join(f"<tr><th class=rl>{r}</th>" + "<td></td>" * nd + "</tr>"
                   for r in ["Mood", "Energy", "Focus", "Sleep", "Meds ✓", "Moved"])
    return (head(f"{MN[m].upper()} {Y}", "Brain weather", "Color or number (1–5). Patterns show up by week three.", chip(f"m{m}", MA[m]))
            + f'<div class="bd">{box("DAILY", f"<table class=bw>{th}{rows}</table>", "none")}'
            f'<div class="rw">{box("WHAT I NOTICE", lines(5))}{box("TO MENTION AT MY NEXT VISIT", lines(5))}</div>'
            + box("PATTERN DETECTIVE", "".join(f'<div class="txt">{e(q)}</div>' + lines(1) for q in C.PATTERN_QS), "1") + '</div>')


def p_mreview(m):
    _, _, q = C.MONTHS[m - 1]
    wk = [n for n, f in enumerate(WEEKS, 1) if home_month(f) == m]
    exps = "".join(f'<a class="xr" href="#w{n}"><span class="wn">W{n}</span><span class="xn">{e(C.experiment(n)[0])}</span>'
                   f'<span class="rate">✓ ~ ✗</span></a>' for n in wk)
    base = "".join(box(t.upper(), lines(2), "none", h) for t, h in C.MONTH_REVIEW)
    return (head(f"{MN[m].upper()} {Y} · REVIEW", "Month review", "Not a report card. Just a look back.", chip(f"m{m}", MA[m]))
            + f'<div class="bd">{base}{box(q.upper(), lines(2), "none")}'
            + '<div class="rw">' + box("ADHD TAX THIS MONTH", '<div class="hint">late fees, rebuys, forgotten subscriptions</div>'
                                        + '<div class="tb4"><span>what</span><span></span><span></span><span>$</span></div>' + lines(3) + '<div class="txt"><b>Total $ ____</b></div>')
            + box("HYPERFOCUS HARVEST", '<div class="hint">what grabbed you · useful? · fun?</div>' + lines(4)) + '</div>'
            + box("THIS MONTH'S EXPERIMENTS", exps, "1") + '</div>')


# ------------------------------------------------------------ weeks --
def p_weeks():
    ch = "".join(f'<a class="wc" href="#w{n}"><b>{n}</b> {md(f)}</a>' for n, f in enumerate(WEEKS, 1))
    return head(str(Y), f"{len(WEEKS)} weeks", "Tap a week.") + f'<div class="bd">{box("WEEKS", f"<div class=wg>{ch}</div>")}</div>'


def p_week(n, first):
    name, try_, why = C.experiment(n)
    days = ""
    for i in range(7):
        d = first + dt.timedelta(i)
        lab = f"{calendar.day_abbr[d.weekday()].upper()} {d.day}"
        cell = chip(dk(d), lab) if d.year == Y else f'<span class="chip off">{lab}</span>'
        hol = f'<span class="hint"> {e(HOL[d])}</span>' if d in HOL else ""
        days += f'<div class="dy">{cell}{hol}</div>'
    last = first + dt.timedelta(6)
    mchips = "".join(chip(f"m{m}", MA[m]) for m in sorted({(first + dt.timedelta(i)).month for i in range(7)
                                                            if (first + dt.timedelta(i)).year == Y}))
    exp = (f'<div class="txt"><b>{e(name)}</b></div><div class="txt">Try: {e(try_)}</div>'
           f'<div class="hint">Why: {e(why)}</div><div class="txt" style="margin-top:6pt">Friday — did it help? &nbsp;✓ helped &nbsp; ~ sort of &nbsp; ✗ not for me</div>')
    return (head(f"{Y} · WEEK {n}", f"{md(first)} – {md(last)}", "", mchips + chip(f"wr{n}", "Reset"))
            + f'<div class="bd">{box(f"THIS WEEK EXPERIMENT · {n}/52", exp, "none", style="background:#EDEDED")}'
            f'<div class="rw" style="flex:1">{box("SEVEN DAYS", days, "1.4")}'
            f'<div class="col">{box("TOP 3", lines(3), "none")}{box("BRAIN DUMP", lines(6))}</div></div></div>')


def p_wreset(n, first):
    items = "".join(f'<div class="ck"><i></i><span>{e(t)}</span></div>' for t in C.WEEKLY_RESET)
    return (head(f"{Y} · WEEK {n}", "Weekly reset", "Sunday setup, then one look back.", chip(f"w{n}", f"Week {n}"))
            + '<div class="bd">' + box("SUNDAY SETUP", items, "none")
            + box("NEXT WEEK'S HEAVIEST DAY — AND ONE THING TO MAKE IT LIGHTER", lines(2), "none")
            + box("DONE LIST — COUNT THE SMALL ONES", lines(6))
            + box(f"EXPERIMENT: {C.experiment(n)[0].upper()} — ONE LINE", lines(2), "none") + '</div>')


# ------------------------------------------------------------- days --
def p_day(d):
    n = WEEK_OF[d]
    doy = d.timetuple().tm_yday
    nd = calendar.monthrange(Y, d.month)[1]
    cat, q = C.question(d)
    y_ = d - dt.timedelta(1)
    t_ = d + dt.timedelta(1)
    fut = C.future_note_target(d)
    arrived = "".join(chip(dk(s), f"A note from {md(s)} ←", "note") for s in NOTES_IN.get(d, []))
    hol = f'<span class="holchip">{e(HOL[d])}</span>' if d in HOL else ""
    chips = chip(f"m{d.month}", MA[d.month]) + chip(f"w{n}", f"Week {n}")
    prog = (f'<div class="prog"><span>Day {doy} · {TOTAL - doy} left</span><div class="bar"><i style="width:{doy / TOTAL * 100:.1f}%"></i></div>'
            f'<span>{MA[d.month]} {d.day}/{nd}</span><div class="bar sm"><i style="width:{d.day / nd * 100:.1f}%"></i></div></div>')
    frm = chip(dk(y_), "From yesterday ←") if y_.year == Y else '<span class="chip off">First day of the year</span>'
    hours = ["7", "8", "9", "10", "11", "12", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    sched = "".join(f'<div class="hr"><span>{h}</span></div>' for h in hours)
    lanes = "".join(box(t, lines(2), "none", h) for t, h in [("LOW BATTERY", " easy wins"), ("MEDIUM", ""), ("FULL", " the hard thing")])
    batt = '<span class="bt"></span>' * 5
    tom = chip(dk(t_), "Tomorrow →") if t_.year == Y else chip("yearreview", "Year review →")
    fut_c = chip(dk(fut), f"Arrives {md(fut)} →") if fut else chip("mailbox", "Arrives in the year-end mailbox →")
    return (head(f"{Y} · WEEK {n} · {calendar.day_name[d.weekday()].upper()}", md(d), "", hol + chips)
            + prog
            + f'<div class="bd"><div class="rw a">{frm}{arrived}<span class="sp"></span><span class="hint">Battery</span>{batt}</div>'
            + f'<div class="rw" style="flex:1"><div class="col" style="flex:1.1">{box("SCHEDULE", sched + "<div class=hint>leave a buffer after each thing</div>")}</div>'
            + f'<div class="col" style="flex:1">{box("TO-DO BY ENERGY", lanes, "none")}{box("NOT TODAY", lines(2), "none", " permission to drop")}'
            + box("GUESS vs ACTUAL", '<div class="tb4"><span>task</span><span></span><span>guess</span><span>took</span></div>' + lines(2), "none")
            + box("MEDS · WATER · MOOD", '<div>meds ' + '<span class="bt"></span>' * 2 + ' &nbsp; water ' + '<span class="bt r"></span>' * 8 + '</div><div style="margin-top:3pt">mood ' + '<span class="bt r"></span>' * 5 + '</div>', "none") + '</div></div>'
            + box(f"QUESTION OF THE DAY · {cat.upper()}", f'<div class="txt">{e(q)}</div>' + lines(1), "none")
            + f'<div class="rw">{box("TOMORROW STARTS WITH", lines(1) + tom, "1")}{box("NOTE TO FUTURE ME", lines(1) + fut_c, "1")}</div>'
            + '</div>')


# ---------------------------------------------------------- year end --
def p_playbook():
    rows = "".join(f'<div class="tr3"><b>W__</b><div class="ln fl"></div><span class="hint">why it worked</span><div class="ln fl"></div></div>' for _ in range(10))
    return (head(f"{Y} · DECEMBER", "My ADHD playbook",
                 "Copy every ✓ from the 52 experiments. This is your brain's user manual, tested on you.",
                 chip("experiments", "The 52 experiments"))
            + f'<div class="bd">{box("WHAT WORKED", rows)}<div class="rw">{box("MY TOP 5 MOVES", lines(5))}'
            f'{box("NOT FOR ME (AND THAT IS FINE)", lines(5))}</div></div>')


def p_mailbox():
    src = NOTES_IN.get("mailbox", [])
    ch = "".join(chip(dk(s), f"{md(s)} ←", "note") for s in src)
    return (head(f"{Y} · YEAR-END", "Year-end mailbox",
                 "Notes to future you written in December land here. Open on New Year's Day.")
            + f'<div class="bd">{box("NOTES WAITING FOR YOU", f"<div class=chips>{ch}</div>", "none")}{box("A NOTE FROM ME TO NEXT YEAR", lines(10))}</div>')


def p_yreview():
    return (head(f"{Y}", "Year review", "Read your done lists and your playbook first.")
            + '<div class="bd">' + box("TEN WINS FROM THIS YEAR", lines(10), "none")
            + '<div class="rw">' + box("ADHD TAX — YEAR TOTAL", "".join(chip(f"mr{m}", MA[m]) for m in range(1, 13)) + lines(1) + '<div class="txt"><b>$ ______</b></div>')
            + box("BEST MONTH, AND WHY", lines(3)) + '</div>'
            + box("THREE THINGS TO CARRY INTO NEXT YEAR", lines(3), "1") + '</div>')


# ------------------------------------------------------------ tools --
def p_group(g):
    title, items = P1[g]
    extra = [(k, C.TOOLS[k][0]) for k in NEW_TOOLS] if g == "life" else []
    rows = "".join(f'<a class="row" href="#{k}">{e(t)}<span>›</span></a>' for k, t in items)
    rows += "".join(f'<a class="row" href="#{k}"><b>NEW · {e(t)}</b><span>›</span></a>' for k, t in extra)
    return head("TOOLS", e(title)) + f'<div class="bd">{box("PAGES", rows)}</div>'


def p_p1(key, name):
    return (head("PRODUCT 1 TEMPLATE", e(name), "Same content as the ADHD & Wellness Planner. New design goes here.")
            + f'<div class="bd">{box("REUSED FROM PRODUCT 1", fill())}</div>')


def p_tool(k):
    title, sub, parts = C.TOOLS[k]
    boxes = "".join(box(p.upper(), (f'<div class="hint">e.g. {e(ex)}</div>' if ex else "") + lines(3), "1", f" {h}" if h else "")
                    for p, h, ex in parts)
    return head("NEW TOOL", e(title), e(sub)) + f'<div class="bd">{boxes}</div>'


def p_notes():
    rows = "".join(f'<a class="row" href="#note{i}">{t}<span>›</span></a>' for i, t in enumerate(["Dot grid", "Ruled", "Plain", "Grid"], 1))
    return head("NOTES", "Notes") + f'<div class="bd">{box("PAGES", rows)}</div>'


# ------------------------------------------------------------ build --
def specs():
    s = [("cover", p_cover), ("how", p_how), ("index", p_index), ("sos", p_sos),
         ("year", p_year), ("kickoff", p_kickoff), ("experiments", p_experiments), ("pixels", p_pixels),
         ("admin", p_admin), ("myhol", p_myhol), ("bday1", lambda: p_bday(1)), ("bday2", lambda: p_bday(2)), ("where", p_where),
         # 상품 1 YEAR 그룹에서 그대로 오는 세 장
         ("goals", lambda: p_p1("goals", "Goals")), ("project", lambda: p_p1("project", "Project planner")),
         ("vision", lambda: p_p1("vision", "Vision page"))]
    s += [(f"q{q}", (lambda qq: lambda: p_quarter(qq))(q)) for q in range(1, 5)]
    s += [("month", p_months)]
    for m in range(1, 13):
        s += [(f"m{m}", (lambda mm: lambda: p_month(mm))(m)), (f"mp{m}", (lambda mm: lambda: p_mplan(mm))(m)),
              (f"bw{m}", (lambda mm: lambda: p_bweather(mm))(m))]
        s += [(dk(d), (lambda dd: lambda: p_day(dd))(d)) for d in DAYS if d.month == m]
        s += [(f"mr{m}", (lambda mm: lambda: p_mreview(mm))(m))]
    s += [("week", p_weeks)]
    for n, f in enumerate(WEEKS, 1):
        s += [(f"w{n}", (lambda nn, ff: lambda: p_week(nn, ff))(n, f)), (f"wr{n}", (lambda nn, ff: lambda: p_wreset(nn, ff))(n, f))]
    s += [("playbook", p_playbook), ("mailbox", p_mailbox), ("yearreview", p_yreview)]
    for g, (_, items) in P1.items():
        s += [(g, (lambda gg: lambda: p_group(gg))(g))]
        s += [(k, (lambda kk, nn: lambda: p_p1(kk, nn))(k, n)) for k, n in items]
        if g == "life":
            s += [(k, (lambda kk: lambda: p_tool(kk))(k)) for k in NEW_TOOLS]
    s += [("notes", p_notes)] + [(f"note{i}", (lambda ii: lambda: p_p1(f"note{ii}", ["Dot grid", "Ruled", "Plain", "Grid"][ii - 1]))(i)) for i in range(1, 5)]
    return s


CSS = """
*{box-sizing:border-box;margin:0;padding:0;-webkit-print-color-adjust:exact;print-color-adjust:exact}
@page{size:612pt 792pt;margin:0}
body{font-family:Arial,Helvetica,sans-serif;color:#222;font-size:8pt}
a{color:inherit;text-decoration:none}
.pg{width:612pt;height:792pt;position:relative;overflow:hidden;page-break-after:always;background:#fff}
.rail{position:absolute;left:0;top:0;bottom:0;width:40pt;border-right:1pt solid #bbb;display:flex;flex-direction:column}
.rail a{flex:1;display:flex;align-items:center;justify-content:center;border-bottom:.5pt solid #ddd}
.rail span{writing-mode:vertical-rl;transform:rotate(180deg);font-size:6pt;font-weight:700;color:#888;letter-spacing:.08em}
.rail a.on{background:#222}.rail a.on span{color:#fff}
.pgk{position:absolute;right:6pt;bottom:4pt;font-size:5pt;color:#bbb}
.c{position:absolute;left:54pt;right:18pt;top:22pt;bottom:18pt;display:flex;flex-direction:column}
.hd{flex:none}.eb{font-size:6.5pt;font-weight:700;letter-spacing:.14em;color:#777}
.tr{display:flex;align-items:center;gap:6pt;margin-top:3pt}.sp{flex:1}
h1{font-size:18pt;font-weight:700}.sub{font-size:7.5pt;color:#666;margin-top:3pt}
.bd{flex:1;display:flex;flex-direction:column;gap:6pt;margin-top:8pt;min-height:0}
.rw{display:flex;gap:6pt;min-height:0}.rw.a{align-items:center;flex:none}
.col{display:flex;flex-direction:column;gap:6pt;min-height:0}
.box{border:1pt solid #bbb;background:#f6f6f6;padding:5pt 7pt;display:flex;flex-direction:column;min-height:0;overflow:hidden}
.box .box{background:#fff;padding:3pt 5pt}
.lab{font-size:6.3pt;font-weight:700;letter-spacing:.1em;color:#555;margin-bottom:3pt}
.hint{font-weight:400;letter-spacing:0;color:#999;font-size:6.3pt}
.txt{font-size:8pt;line-height:1.4;margin:1pt 0}
.ln{height:14pt;border-bottom:.8pt solid #ccc;flex:none}.ln.fl{flex:1}
.fill{flex:1;border:1pt dashed #ccc;background:#fff}
.chip{display:inline-block;border:1pt solid #999;border-radius:8pt;padding:1.5pt 6pt;font-size:6.5pt;font-weight:700;background:#fff;margin:1pt}
.chip.note{border-color:#222;background:#222;color:#fff}.chip.off{border-style:dashed;color:#aaa}
.holchip{font-size:6.5pt;font-weight:700;border:1pt solid #222;padding:1.5pt 5pt}
.chips{display:flex;flex-wrap:wrap;gap:2pt}
.row{display:flex;align-items:center;gap:6pt;padding:5pt 2pt;border-bottom:.8pt solid #ddd;font-size:9pt}.row span:last-child{margin-left:auto;color:#999}
.ck{display:flex;align-items:center;gap:5pt;font-size:7.5pt;padding:2pt 0}.ck i{width:8pt;height:8pt;border:1pt solid #888;flex:none}
.prog{display:flex;align-items:center;gap:6pt;font-size:6.5pt;color:#555;margin-top:4pt}
.bar{flex:3;height:5pt;border:.8pt solid #999}.bar.sm{flex:1}.bar i{display:block;height:100%;background:#999}
.bt{display:inline-block;width:9pt;height:9pt;border:1pt solid #888;margin-left:2pt}.bt.r{border-radius:9pt;width:8pt;height:8pt}
.hr{flex:1;border-bottom:.8pt solid #ddd;font-size:6.5pt;color:#888;padding-top:1pt}
.tb4{display:flex;font-size:5.8pt;color:#999;letter-spacing:.08em}.tb4 span{flex:1}.tb4 span:first-child{flex:2}
.dy{flex:1;border-bottom:.8pt solid #ddd;padding-top:3pt}
.yg{display:grid;grid-template-columns:repeat(4,1fr);gap:8pt 10pt}.mname{font-weight:700;font-size:7.5pt}
.mini{width:100%;border-collapse:collapse;margin-top:2pt}.mini td,.mini th{text-align:center;font-size:5.6pt;padding:.8pt 0}
.cal{width:100%;height:100%;border-collapse:collapse;table-layout:fixed}.cal tr:first-child{height:14pt}.cal th{font-size:6pt;color:#777;padding:2pt}
.cal td{border:.8pt solid #bbb;vertical-align:top;padding:3pt;font-size:8pt;font-weight:700;background:#fff}.cal td.wk{width:24pt;font-size:6pt;color:#777;vertical-align:middle;text-align:center}
.cal td.out{background:#eee}.hol{font-size:5.3pt;font-weight:400;color:#666;margin-top:2pt}
.px{border-collapse:collapse;width:100%}.px th{font-size:5.5pt;color:#777;width:14pt}.px td{border:.6pt solid #bbb;height:16.4pt;background:#fff}.px td.x{background:#ddd}
.bw{border-collapse:collapse;width:100%;table-layout:fixed}.bw th{font-size:5pt;color:#777;font-weight:700}.bw th.rl{width:34pt;text-align:left}
.bw td{border:.6pt solid #bbb;height:22pt;background:#fff}.bw small{font-size:4.5pt;color:#aaa}
.ag{display:grid;grid-template-columns:repeat(3,1fr);gap:8pt}.am b{font-size:8pt}
.g3{display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(4,1fr);gap:6pt;flex:1}
.g2{display:grid;grid-template-columns:1fr 1fr;grid-template-rows:repeat(3,1fr);gap:6pt;flex:1}
.tr3{display:flex;align-items:end;gap:8pt;height:22pt;font-size:8pt}.tr3 b{width:110pt}
.xl{display:grid;grid-template-columns:1fr 1fr;grid-template-rows:repeat(27,auto);grid-auto-flow:column;gap:0 10pt}
.xr{display:flex;align-items:center;gap:5pt;font-size:6.8pt;height:12.6pt;border-bottom:.6pt solid #ddd}
.wn{width:18pt;font-weight:700;color:#777}.xn{flex:1}.xd{color:#999;font-size:6pt}.rate{color:#aaa;font-size:6pt}
.wg{display:grid;grid-template-columns:repeat(5,1fr);gap:5pt}.wc{border:1pt solid #bbb;background:#fff;padding:5pt;font-size:7pt;text-align:center}
"""


def build():
    sp = specs()
    body = "".join(page(k, fn()) for k, fn in sp)
    html = (f'<!DOCTYPE html><html><head><meta charset="utf-8"><title>{Y} ADHD Year Planner — wireframe</title>'
            f"<style>{CSS}</style></head><body>{body}</body></html>")
    os.makedirs(os.path.dirname(SRC), exist_ok=True)
    open(SRC, "w", encoding="utf-8").write(html)
    before = os.path.getmtime(OUT) if os.path.exists(OUT) else 0
    prof = os.path.join(tempfile.gettempdir(), "p3-wire-profile")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", f"--user-data-dir={prof}", "--no-pdf-header-footer",
                    f"--print-to-pdf={OUT}", "file:///" + SRC.replace("\\", "/")], capture_output=True)
    if not os.path.exists(OUT) or os.path.getmtime(OUT) <= before:
        raise RuntimeError("Chrome 이 PDF 를 쓰지 않았다 (열려 있는 뷰어가 잠갔는지 확인)")
    ids = [k for k, _ in sp]
    hrefs = set(re.findall(r'href="?#([^" >]+)', html))
    dead = sorted(hrefs - set(ids))
    bad, wk_miss = check_links(html)
    print(f"{OUT}\n  pages {len(ids)} · dead links {len(dead)} {dead[:5]} · {os.path.getsize(OUT):,} B"
          f"\n  time links broken {len(bad)} {bad[:3]} · weeks missing from quarters {wk_miss}")
    return ids, html, bad + dead, wk_miss


def check_links(html):
    """Time links 는 양방향이어야 한다: 보낸 날 -> 받는 날 칩, 받는 날 -> 보낸 날 칩.
    모든 주는 어느 분기의 Keep/Drop 에 나와야 한다(1주차가 빠졌던 적이 있다, 2026-09-25)."""
    sec = {m.group(1): m.group(0) for m in re.finditer(r'<section class="pg" id="([^"]+)".*?</section>', html, re.S)}
    bad = []
    for d in DAYS:
        me, t = sec[dk(d)], C.future_note_target(d)
        tgt = dk(t) if t else "mailbox"
        if f'href="#{tgt}">' not in me or f'href="#{dk(d)}"' not in sec[tgt]:
            bad.append(f"note {dk(d)}<->{tgt}")
        nx = d + dt.timedelta(1)
        if nx.year == Y and (f'href="#{dk(nx)}">Tomorrow' not in me
                             or f'href="#{dk(d)}">From yesterday' not in sec[dk(nx)]):
            bad.append(f"handoff {dk(d)}->{dk(nx)}")
    wk_miss = [n for n in range(1, len(WEEKS) + 1)
               if not any(f'href="#w{n}"' in sec[f"q{q}"] for q in range(1, 5))]
    return bad, wk_miss


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    _, _, bad, miss = build()
    sys.exit(1 if bad or miss else 0)
