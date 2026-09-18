# -*- coding: utf-8 -*-
"""Generate the ADHD/wellness planner as HTML, then print it to PDF with Chrome.

Pipeline per CLAUDE.md: HTML/CSS -> headless Chrome print-to-PDF, which keeps
internal `#anchor` links as PDF named destinations.
"""

import calendar
import os
import tempfile
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = "v1-admin"          # muted green enterprise-admin look
SRC = os.path.join(ROOT, "src", f"planner_{VERSION}.html")
OUT = os.path.join(ROOT, "output", f"planner_{VERSION}.pdf")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

YEAR = 2026

TABS = [
    ("index",  "INDEX"),
    ("year",   "YEAR"),
    ("month",  "MONTH"),
    ("week",   "WEEK"),
    ("day",    "DAY"),
    ("tasks",  "TASKS"),
    ("habits", "HABITS"),
    ("meds",   "MEDS"),
    ("notes",  "NOTES"),
]

CSS = """
:root{
  --bg:#F4F6F5; --card:#FFFFFF; --accent:#12855C; --chip:#E7F2EC;
  --ink:#22262B; --mid:#5A616B; --soft:#9AA0A8; --line:#E4E7E6; --field:#F3F5F4;
  --shadow:0 4px 12px rgba(0,0,0,.08);
}
*{box-sizing:border-box;-webkit-print-color-adjust:exact;print-color-adjust:exact}
@page{size:612pt 792pt;margin:0}
body{margin:0;font-family:'Inter',system-ui,sans-serif;color:var(--ink);
     -webkit-font-smoothing:antialiased}

.page{width:612pt;height:792pt;background:var(--bg);position:relative;
      page-break-after:always;overflow:hidden}
.page:last-child{page-break-after:auto}

/* ---------- tab rail ---------- */
.rail{position:absolute;left:0;top:0;width:58pt;height:792pt;
      border-right:1px solid var(--line);display:flex;flex-direction:column;
      padding:4pt}
.rail a{flex:1;display:flex;align-items:center;justify-content:center;
        position:relative;margin:2pt 0;border-radius:9pt;text-decoration:none}
.rail a span{writing-mode:vertical-rl;transform:rotate(180deg);font-size:7pt;
        font-weight:600;letter-spacing:.06em;color:var(--soft)}
.rail a.on{background:var(--card);box-shadow:var(--shadow)}
.rail a.on span{color:var(--accent);font-weight:700}
.rail a.on::before{content:"";position:absolute;left:5pt;top:50%;
        transform:translateY(-50%);width:2.4pt;height:24pt;
        background:var(--accent);border-radius:2pt}

/* ---------- page skeleton ---------- */
.content{position:absolute;left:84pt;right:28pt;top:0;bottom:0;
         display:flex;flex-direction:column;padding:42pt 0 34pt}
.head{flex:none}
.body{flex:1;display:flex;flex-direction:column;gap:12pt;margin-top:20pt;
      min-height:0}

.eyebrow{display:flex;align-items:center;gap:8pt;font-size:9.5pt;font-weight:600;
         color:var(--mid)}
.eyebrow::before{content:"";width:2.6pt;height:11pt;background:var(--accent);
         border-radius:1pt}
h1{font-size:23pt;font-weight:700;margin:11pt 0 0;letter-spacing:-.01em}
.sub{color:var(--soft);font-size:9.5pt;margin-top:5pt}
.titlerow{display:flex;align-items:center;gap:16pt}

/* ---------- pieces ---------- */
.card{background:var(--card);border-radius:10pt;box-shadow:var(--shadow);
      padding:16pt;display:flex;flex-direction:column;min-height:0;
      position:relative}
/* box-shadow spreads evenly along the bottom edge; this pool sits under the
   card and deepens toward the middle, thinning out at both ends. */
.card::after{content:"";position:absolute;left:7%;right:7%;bottom:-9pt;height:12pt;
      background:radial-gradient(ellipse 58% 100% at 50% 0%, rgba(0,0,0,.13),
      rgba(0,0,0,0) 72%);pointer-events:none}
.label{display:flex;align-items:center;gap:7pt;font-size:9pt;font-weight:700;
       color:var(--ink);margin-bottom:10pt;flex:none}
.label::before{content:"";width:2.6pt;height:10pt;background:var(--accent);
       border-radius:1pt;flex:none}
.chip{display:inline-block;background:var(--chip);color:var(--accent);
      font-size:7.5pt;font-weight:700;padding:3pt 9pt;border-radius:99pt;
      letter-spacing:.03em}
.field{background:var(--field);border-radius:6pt;height:19pt;flex:none}
.box{width:12pt;height:12pt;border:1px solid #C9D2CE;border-radius:3pt;flex:none}

.lines{flex:1;display:flex;flex-direction:column;min-height:0}
.lines>div{flex:1;border-bottom:1px solid var(--line);min-height:16pt}

.row{display:flex;gap:12pt;flex:1;min-height:0}
.col{display:flex;flex-direction:column;gap:12pt;min-height:0}

/* ---------- grids ---------- */
.cal{border-collapse:collapse;width:100%;height:100%;table-layout:fixed}
.cal td{border:1px solid var(--line);vertical-align:top;padding:5pt 6pt;
        font-size:8.5pt;font-weight:600}
.cal th{font-size:7.5pt;color:var(--soft);font-weight:700;padding-bottom:7pt;
        letter-spacing:.05em;height:18pt}
.cal .we{color:var(--accent)}

.mini{width:100%;border-collapse:collapse}
.mini td,.mini th{text-align:center;font-size:5.6pt;padding:1.3pt 0;line-height:1}
.mini th{color:var(--soft);font-weight:700;font-size:5.2pt}
.mini .we{color:var(--accent)}

.trk{border-collapse:collapse;width:100%;height:100%;table-layout:fixed}
.trk td{border:1px solid var(--line)}
.trk .nm{border:none;border-bottom:1px solid var(--line);text-align:left;
         font-size:8.5pt;padding:0 8pt 0 2pt;white-space:nowrap;width:104pt}
.trk .dh{border:none;font-size:5.4pt;color:var(--soft);font-weight:700;
         height:13pt;vertical-align:bottom;padding-bottom:3pt;text-align:center}
.trk .dh.we{color:var(--accent)}
.trk tr:first-child .nm{border-bottom:none}

.dots{background-image:radial-gradient(var(--line) 1.1px, transparent 1.1px);
      background-size:14pt 14pt;background-position:8pt 8pt}
"""


# ---------------------------------------------------------------- helpers --
def rail(active):
    links = "".join(
        f'<a class="{"on" if k == active else ""}" href="#{k}"><span>{lb}</span></a>'
        for k, lb in TABS)
    return f'<nav class="rail">{links}</nav>'


def page(key, body):
    return (f'<section class="page" id="{key}">{rail(key)}'
            f'<div class="content">{body}</div></section>')


def head(eyebrow, title, sub="", field_after=False):
    t = f"<h1>{title}</h1>"
    if field_after:
        t = (f'<div class="titlerow"><h1>{title}</h1>'
             f'<div class="field" style="flex:1;max-width:210pt;height:22pt"></div></div>')
    s = f'<div class="sub">{sub}</div>' if sub else ""
    return f'<div class="head"><div class="eyebrow">{eyebrow}</div>{t}{s}</div>'


def lines(n):
    return '<div class="lines">' + "<div></div>" * n + "</div>"


def checkrow(field_flex=1):
    return ('<div style="display:flex;align-items:center;gap:9pt">'
            f'<div class="box"></div><div class="field" style="flex:{field_flex}"></div></div>')


# ------------------------------------------------------------------ pages --
def p_cover():
    items = [
        ("Index &amp; year view", "see everything, jump anywhere", "2"),
        ("Monthly / weekly / daily", "the three you'll use every day", "3"),
        ("Task breakdown", "make the big thing smaller", "1"),
        ("Habit &amp; medication log", "31-day grid, no streak guilt", "2"),
        ("Notes", "dot grid, yours to fill", "1"),
    ]
    rows = "".join(
        f'<div style="display:flex;align-items:center;gap:12pt;padding:11pt 0;'
        f'{"" if i == len(items) - 1 else "border-bottom:1px solid var(--line)"}">'
        f'<div style="width:5pt;height:5pt;border-radius:99pt;background:var(--accent);'
        f'flex:none"></div>'
        f'<div style="flex:1"><div style="font-size:10pt;font-weight:700">{t}</div>'
        f'<div style="font-size:8.5pt;color:var(--soft);margin-top:2pt">{d}</div></div>'
        f'<span class="chip">{c}</span></div>'
        for i, (t, d, c) in enumerate(items))
    return f"""
    <div class="head" style="flex:1;display:flex;flex-direction:column;
         align-items:center;justify-content:center;text-align:center">
      <div style="width:28pt;height:2.6pt;background:var(--accent);margin-bottom:18pt"></div>
      <span class="chip">UNDATED &middot; NO-GUILT</span>
      <div style="font-size:31pt;font-weight:700;line-height:1.18;margin-top:20pt;
                  letter-spacing:-.02em">{YEAR} ADHD &amp;<br>Wellness Planner</div>
      <div style="color:var(--mid);font-size:11pt;margin-top:12pt">
        Start any day. Skip a week. Nothing to catch up on.</div>
    </div>
    <div class="card" style="flex:none;padding:18pt 22pt;margin-bottom:6pt">
      <div class="label">What's inside</div>{rows}
    </div>"""


def p_index():
    groups = [
        ("Plan", [("year", "Year at a glance"), ("month", "Monthly overview"),
                  ("week", "Weekly spread"), ("day", "Daily page")]),
        ("Focus", [("tasks", "Task breakdown"), ("habits", "Habit tracker")]),
        ("Health", [("meds", "Medication log")]),
        ("Free", [("notes", "Notes")]),
    ]
    cards = []
    for title, links in groups:
        rows = "".join(
            f'<a href="#{k}" style="display:flex;align-items:center;gap:10pt;flex:1;'
            f'text-decoration:none;color:var(--ink);'
            f'{"" if i == len(links) - 1 else "border-bottom:1px solid var(--line)"}">'
            f'<div style="width:4pt;height:4pt;border-radius:99pt;background:var(--accent)"></div>'
            f'<div style="flex:1;font-size:10pt;font-weight:600">{n}</div>'
            f'<div style="color:var(--soft);font-size:11pt">&rsaquo;</div></a>'
            for i, (k, n) in enumerate(links))
        cards.append(f'<div class="card" style="flex:{len(links)}">'
                     f'<div class="label">{title}</div>{rows}</div>')
    return (head("Index", "Where to?", "Use the side tabs, or pick from here")
            + f'<div class="body">{"".join(cards)}</div>')


def mini_month(m):
    weeks = calendar.Calendar(firstweekday=0).monthdayscalendar(YEAR, m)
    th = "".join(f'<th class="{"we" if i >= 5 else ""}">{d}</th>'
                 for i, d in enumerate("MTWTFSS"))
    rows = "".join(
        "<tr>" + "".join(f'<td class="{"we" if i >= 5 else ""}">{d or ""}</td>'
                         for i, d in enumerate(w)) + "</tr>" for w in weeks)
    return (f'<div style="flex:1 1 21%"><div style="font-size:8pt;font-weight:700;'
            f'margin-bottom:5pt">{calendar.month_name[m]}</div>'
            f'<table class="mini"><tr>{th}</tr>{rows}</table></div>')


def p_year():
    months = "".join(mini_month(m) for m in range(1, 13))
    return (head("Year at a glance", str(YEAR))
            + f"""<div class="body">
      <div class="card" style="flex:3;padding:18pt;justify-content:space-between">
        <div style="display:flex;flex-wrap:wrap;gap:14pt;align-content:space-between;
             height:100%">{months}</div>
      </div>
      <div class="card" style="flex:1">
        <div class="label">Three things that matter this year</div>
        <div style="flex:1;display:flex;flex-direction:column;
             justify-content:space-around">{checkrow() * 3}</div>
      </div></div>""")


def p_month():
    weeks = calendar.Calendar(firstweekday=0).monthdayscalendar(YEAR, 1)
    th = "".join(f'<th class="{"we" if i >= 5 else ""}">{d}</th>' for i, d in
                 enumerate(["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]))
    rows = "".join(
        "<tr>" + "".join(f'<td class="{"we" if i >= 5 else ""}">{d or ""}</td>'
                         for i, d in enumerate(w)) + "</tr>" for w in weeks)
    return (head("Monthly overview", f"January {YEAR}")
            + f"""<div class="body">
      <div class="card" style="flex:1;padding:16pt 18pt">
        <table class="cal"><tr>{th}</tr>{rows}</table></div>
      <div class="card" style="flex:none;flex-direction:row;align-items:center;gap:14pt">
        <div class="label" style="margin:0;white-space:nowrap">This month's focus</div>
        <div class="field" style="flex:1"></div></div></div>""")


def p_week():
    days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    rows = "".join(
        f'<div style="flex:1;display:flex;align-items:flex-start;padding-top:8pt;'
        f'{"" if i == 6 else "border-bottom:1px solid var(--line)"}">'
        f'<span class="chip" style="{"" if i < 5 else "background:var(--field);color:var(--mid)"}">{d}</span>'
        f'</div>' for i, d in enumerate(days))
    return (head("Weekly spread", "Week of", field_after=True)
            + f"""<div class="body"><div class="row">
      <div class="card" style="flex:1.45">{rows}</div>
      <div class="col" style="flex:1">
        <div class="card" style="flex:1.6">
          <div class="label">Brain dump</div>{lines(8)}</div>
        <div class="card" style="flex:1">
          <div class="label">Top 3 priorities</div>
          <div style="flex:1;display:flex;flex-direction:column;
               justify-content:space-around">{checkrow() * 3}</div></div>
        <div class="card" style="flex:none">
          <div class="label">Energy</div>
          <div style="display:flex;justify-content:space-between;padding:0 4pt">
            {'<div class="box" style="width:14pt;height:14pt"></div>' * 5}</div>
          <div style="display:flex;justify-content:space-between;font-size:7pt;
               color:var(--soft);margin-top:6pt;padding:0 2pt">
            <span>low</span><span>high</span></div></div>
      </div></div></div>""")


def p_day():
    hours = ["7 AM", "9 AM", "11 AM", "1 PM", "3 PM", "5 PM", "7 PM", "9 PM"]
    blocks = "".join(
        f'<div style="flex:1;display:flex;align-items:center;'
        f'{"" if i == len(hours) - 1 else "border-bottom:1px solid var(--line)"}">'
        f'<span style="font-size:7.5pt;font-weight:700;color:var(--soft);'
        f'width:34pt">{h}</span></div>' for i, h in enumerate(hours))
    mood = "".join(
        f'<div><div class="box" style="width:14pt;height:14pt;margin:0 auto"></div>'
        f'<div style="font-size:7pt;color:var(--soft);margin-top:5pt">{m}</div></div>'
        for m in ["Low", "OK", "Good", "Great"])
    return (head("Daily page", "Today", field_after=True)
            + f"""<div class="body">
      <div class="card" style="flex:none;flex-direction:row;align-items:center;
           gap:14pt;padding:13pt 16pt">
        <div class="label" style="margin:0;white-space:nowrap">Just one thing today</div>
        <div class="field" style="flex:1"></div></div>
      <div class="row">
        <div class="card" style="flex:1.3">{blocks}</div>
        <div class="col" style="flex:1">
          <div class="card" style="flex:none">
            <div class="label">Meds / water</div>
            <div style="display:flex;align-items:center;gap:8pt;margin-bottom:11pt">
              <span style="font-size:7.5pt;color:var(--soft);width:30pt">Meds</span>
              {'<div class="box" style="width:13pt;height:13pt"></div>' * 2}</div>
            <div style="display:flex;align-items:center;gap:5pt">
              <span style="font-size:7.5pt;color:var(--soft);width:30pt">Water</span>
              {'<div class="box" style="width:11pt;height:11pt"></div>' * 8}</div></div>
          <div class="card" style="flex:none">
            <div class="label">Mood</div>
            <div style="display:flex;justify-content:space-between;text-align:center">
              {mood}</div></div>
          <div class="card" style="flex:1">
            <div class="label">Brain dump</div>{lines(8)}</div>
        </div></div></div>""")


def p_tasks():
    chunks = "".join(
        f'<div style="display:flex;align-items:center;gap:9pt">'
        f'<span style="font-size:8pt;color:var(--soft);width:12pt;font-weight:700">{i}</span>'
        f'<div class="box"></div><div class="field" style="flex:1"></div></div>'
        for i in range(1, 9))
    quads = [
        f'<div style="background:var(--field);border-radius:7pt;padding:10pt;flex:1">'
        f'<div style="font-size:7.5pt;font-weight:700;color:{c}">{t}</div></div>'
        for t, c in [("Now &middot; Important", "var(--accent)"),
                     ("Later &middot; Important", "var(--mid)"),
                     ("Now &middot; Less important", "var(--mid)"),
                     ("Doesn't need doing", "var(--soft)")]]
    return (head("Task breakdown", "Make it smaller", "One piece at a time")
            + f"""<div class="body">
      <div class="card" style="flex:none;flex-direction:row;align-items:center;gap:14pt">
        <div class="label" style="margin:0;white-space:nowrap">The big thing</div>
        <div class="field" style="flex:1"></div></div>
      <div class="row">
        <div class="card" style="flex:1.25">
          <div class="label">Broken into pieces</div>
          <div style="flex:1;display:flex;flex-direction:column;
               justify-content:space-around">{chunks}</div></div>
        <div class="col" style="flex:1">
          <div class="card" style="flex:1.6">
            <div class="label">Sort it out</div>
            <div style="flex:1;display:flex;flex-direction:column;gap:8pt">
              <div style="display:flex;gap:8pt;flex:1">{quads[0]}{quads[1]}</div>
              <div style="display:flex;gap:8pt;flex:1">{quads[2]}{quads[3]}</div>
            </div></div>
          <div class="card" style="flex:1">
            <div class="label">The first five minutes</div>
            <div style="font-size:8pt;color:var(--soft);margin-bottom:8pt">
              Just start. You don't have to finish.</div>
            <div class="field" style="flex:1;height:auto"></div></div>
        </div></div></div>""")


def tracker(names, blanks=0):
    dh = "".join(f'<td class="dh {"we" if (d % 7) in (6, 0) else ""}">{d}</td>'
                 for d in range(1, 32))
    body = "".join(f'<tr><td class="nm">{n}</td>' + "<td></td>" * 31 + "</tr>"
                   for n in names)
    body += "".join('<tr><td class="nm">&nbsp;</td>' + "<td></td>" * 31 + "</tr>"
                    for _ in range(blanks))
    return f'<table class="trk"><tr><td class="nm"></td>{dh}</tr>{body}</table>'


def p_habits():
    names = ["Water", "Meds", "Movement", "Sleep 7h+", "Journal",
             "Tidy 10 min", "Outside", "Screen cutoff"]
    return (head("Habit tracker", f"January {YEAR}")
            + f"""<div class="body">
      <div class="card" style="flex:2.2;padding:16pt 18pt">{tracker(names, 2)}</div>
      <div class="row" style="flex:1">
        <div class="card" style="flex:1"><div class="label">What worked</div>{lines(5)}</div>
        <div class="card" style="flex:1"><div class="label">What to change</div>{lines(5)}</div>
      </div></div>""")


def p_meds():
    return (head("Medication log", f"January {YEAR}", "Track the dose and how it felt")
            + f"""<div class="body">
      <div class="card" style="flex:2;padding:16pt 18pt">{tracker([], 9)}</div>
      <div class="card" style="flex:1">
        <div class="label">Side effects &middot; how you felt</div>{lines(6)}</div>
      </div>""")


def p_notes():
    return (head("Notes", "Blank space")
            + '<div class="body"><div class="card dots" style="flex:1"></div></div>')


# ------------------------------------------------------------------ build --
def build_html():
    pages = [page(k, fn()) for k, fn in [
        ("cover", p_cover), ("index", p_index), ("year", p_year),
        ("month", p_month), ("week", p_week), ("day", p_day),
        ("tasks", p_tasks), ("habits", p_habits), ("meds", p_meds),
        ("notes", p_notes),
    ]]
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>{YEAR} ADHD &amp; Wellness Planner</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap"
      rel="stylesheet">
<style>{CSS}</style></head>
<body>{"".join(pages)}</body></html>"""
    os.makedirs(os.path.dirname(SRC), exist_ok=True)
    with open(SRC, "w", encoding="utf-8") as f:
        f.write(html)
    return SRC


def to_pdf():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    before = os.path.getmtime(OUT) if os.path.exists(OUT) else 0

    # A dedicated profile dir is required: with the default one, a Chrome the
    # user already has open holds the lock, and the headless call exits 0
    # without ever writing the PDF.
    profile = os.path.join(tempfile.gettempdir(), "planner-chrome-profile")
    r = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", f"--user-data-dir={profile}",
         "--no-pdf-header-footer", f"--print-to-pdf={OUT}",
         "file:///" + SRC.replace("\\", "/")],
        capture_output=True, text=True, encoding="utf-8", errors="replace")

    if not os.path.exists(OUT) or os.path.getmtime(OUT) <= before:
        raise RuntimeError(
            "Chrome exited without writing a new PDF.\n"
            f"returncode={r.returncode}\nstdout={r.stdout}\nstderr={r.stderr}")
    return OUT


if __name__ == "__main__":
    build_html()
    to_pdf()
    print("Saved:", OUT)
