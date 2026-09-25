# -*- coding: utf-8 -*-
"""상품 3 날짜형 플래너 -- Lifted Paper 디자인 + 와이어프레임 v0.2 의 내용·링크. Prod 3 방 소유.

    python scripts/p3/planner_build.py 2027 mon            # 전체 -> output/prod3/planner/<VERSION>/
    python scripts/p3/planner_build.py 2027 mon --sample   # 대표 페이지만 (검수용, sample/ 폴더)

구조·문구·링크(52 실험, Time links, SOS, 날짜)는 p3_wireframe.py 와 p3_content.py 가 정한다 -- 이미 검사된 것.
이 파일은 모양만 입힌다:
  - 페이지 틀: 768x1024, 배경 이미지(Sheet A/B, 종이+탭 묶음 가운데), 오른쪽 탭 레일, 발문(footer)
  - 잉크 규칙(핸드오프 README): Source Serif 4 하나, 소문자 대문자 라벨, 1px 괘선 34px 피치,
    시안은 페이지의 리드 항목에만, 마젠타 판은 페이지당 2번 이하
  - 상품 1 도구 44장은 p1_tools.json 스냅숏(extract_p1_tools.py)을 같은 모양으로
GoodNotes 안전: 그라데이션·블러·반투명 레이어 없음. 괘선은 실제 1px 요소, 점은 SVG 원.
"""
import calendar
import datetime as dt
import json
import os
import pathlib
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
SAMPLE = "--sample" in sys.argv
sys.argv = [sys.argv[0]] + ARGS          # p3_wireframe 는 argv 로 연도·주 시작을 읽는다
import p3_content as C
import p3_wireframe as W
import editions_build as E

ROOT = HERE.parents[1]
Y, WS, TAG = W.Y, W.WS, W.TAG
VERSION = "v0.1"
OUT = ROOT / "output" / "prod3" / "planner" / VERSION
SRC = ROOT / "src" / "prod3" / "planner" / VERSION
if SAMPLE:
    # 검수용 표본도 보여 준 것은 남긴다(덮어쓰지 않는다) -- sample-01, sample-02 ... 새 번호로
    _n = 1
    while (OUT / f"sample-{_n:02d}").exists():
        _n += 1
    OUT, SRC = OUT / f"sample-{_n:02d}", SRC / f"sample-{_n:02d}"
FNAME = f"ADHD-Year-Planner-{TAG}"
P1 = json.loads((HERE / "p1_tools.json").read_text(encoding="utf-8"))

# ------------------------------------------------------------------ colours --
PAPER, INK = "#f8f4f4", "#201e1d"
N300, N400, N500, N600, N700, N800 = "#d7d3d3", "#bab6b6", "#9b9797", "#7d7979", "#605d5d", "#444141"
CYAN, CYAN700, CYAN800 = "#0088b0", "#006786", "#004961"
CYAN40 = "#95c9d9"          # 시안 40% 를 종이 위에 미리 섞은 불투명색 (반투명 레이어를 만들지 않는다)
CYAN6 = "#e9eef0"
MAG = "#d6006c"
PLATE = "2.5px 2px 0 rgba(214,0,108,.45)"   # 번짐 없는 text-shadow = 벡터 사본 한 벌
BT, BTR = '<span class="bt"></span>', '<span class="bt r"></span>'   # 칸 / 동그라미

TABS = [("index", "Index"), ("sos", "SOS"), ("year", "Year"), ("month", "Month"), ("week", "Week"),
        ("focus", "Focus"), ("feel", "Feel"), ("health", "Body"), ("life", "Life"), ("notes", "Notes")]
SHEET_B = {"cover", "focus", "feel", "health", "life"}      # 표지·섹션 구분 페이지만

# 페이지마다 시안을 받을 "리드" 칸 (라벨 글자로 찾는다). 없으면 그 페이지는 시안 없음.
LEAD = [
    (r"^mp\d+$", "THIS MONTH, ONE THING"), (r"^q\d$", "THIS QUARTER, ONE THING"),
    (r"^w\d+$", "THIS WEEK EXPERIMENT"), (r"^wr\d+$", "SUNDAY SETUP"),
    (r"^kickoff$", "IF I ONLY DO ONE THING THIS YEAR"), (r"^year$", "THREE THINGS THAT MATTER THIS YEAR"),
    (r"^mr\d+$", "WHAT WENT WELL"), (r"^playbook$", "WHAT WORKED"), (r"^yearreview$", "TEN WINS FROM THIS YEAR"),
    (r"^mailbox$", "NOTES WAITING FOR YOU"), (r"^sos$", "WHAT IS HAPPENING?"),
]

CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,wght@0,400;0,600;1,400&display=swap');
@page{{size:768px 1024px;margin:0}}
*{{box-sizing:border-box;margin:0;padding:0;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
html,body{{background:none}}
body{{font-family:"Source Serif 4",Georgia,serif;color:{INK};font-size:13px;line-height:1.35}}
a{{color:inherit;text-decoration:none}}
.pg{{position:relative;width:768px;height:1024px;overflow:hidden;break-after:page;background:#eae7e7}}
.pg:last-child{{break-after:auto}}
.pg>img.bg{{position:absolute;inset:0;width:768px;height:1024px;display:block}}
.sheet{{position:absolute;left:{38 - E.SHIFT}px;top:38px;width:692px;height:948px;isolation:isolate}}
.ink{{position:absolute;inset:0;padding:40px 44px 30px;display:flex;flex-direction:column}}
.rail{{position:absolute;left:100%;top:64px;display:flex;flex-direction:column;gap:6px;z-index:-1}}
.rail a{{position:relative;display:flex;align-items:center;justify-content:center;width:22px;height:70px;
  writing-mode:vertical-rl;font-size:10px;letter-spacing:.12em;text-transform:uppercase;
  background:{PAPER};color:{N800};border-radius:0 2px 2px 0}}
.rail a.on{{width:26px;background:{CYAN};color:#f3f2f2}}
.rail a img{{position:absolute;z-index:-1;pointer-events:none}}
footer{{flex:none;display:flex;justify-content:space-between;margin-top:14px;font-size:10px;
  letter-spacing:.1em;text-transform:uppercase;color:{N700}}}

/* ---- head ---- */
.hd{{flex:none}}
.eb{{font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:{N700}}}
.tr{{display:flex;align-items:flex-end;gap:8px;margin-top:8px}}.sp{{flex:1}}
h1{{font-weight:600;font-size:40px;line-height:1;letter-spacing:-.02em}}
.sub{{font-style:italic;font-size:14px;line-height:1.45;color:{N800};margin-top:8px;max-width:470px}}
.chip{{display:inline-block;font-size:9.5px;letter-spacing:.08em;text-transform:uppercase;line-height:1;
  border:1px solid {N600};border-radius:1px;padding:4px 6px 3px;margin:1px 0 1px 4px;color:{N800};white-space:nowrap}}
.chip.note{{background:{INK};border-color:{INK};color:{PAPER}}}
.chip.off{{border-style:dotted;color:{N500}}}
.holchip{{font-style:italic;font-size:12px;color:{N800};margin-right:6px}}

/* ---- body (wireframe classes, re-inked) ---- */
.bd{{flex:1;display:flex;flex-direction:column;gap:16px;margin-top:20px;min-height:0}}
.rw{{display:flex;gap:26px;min-height:0}}.rw.a{{align-items:center;gap:6px;flex:none}}
.col{{display:flex;flex-direction:column;gap:16px;min-height:0}}
.box{{display:flex;flex-direction:column;min-height:0;overflow:hidden}}
.box .box{{padding-top:2px}}
.lab{{flex:none;font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:{N700};line-height:1.2}}
.hint{{text-transform:none;letter-spacing:0;font-style:italic;color:{N800};font-size:11.5px}}
.txt{{font-size:13.5px;line-height:1.5;margin-top:3px}}
.txt b{{font-weight:600}}
.ln{{flex:none;height:34px;border-bottom:1px solid {N400}}}.ln.fl{{flex:1;height:22px}}
.fill{{flex:1;border-bottom:1px solid {N300}}}
a.row{{display:flex;align-items:baseline;gap:12px;padding:10px 0 9px;border-bottom:1px solid {N300};font-size:15px}}
a.row b{{font-weight:600}} a.row span:last-child{{margin-left:auto;color:{N600}}}
.ck{{display:flex;align-items:center;gap:9px;font-size:13px;padding:5px 0}}
.ck i{{flex:none;width:11px;height:11px;border:1px solid {N600};border-radius:1px}}
.prog{{flex:none;display:flex;align-items:center;gap:10px;font-size:10px;letter-spacing:.08em;
  text-transform:uppercase;color:{N700};margin-top:12px}}
.bar{{flex:3;height:5px;border:1px solid {N500}}}.bar.sm{{flex:1}}.bar i{{display:block;height:100%;background:{N500}}}
.bt{{display:inline-block;width:12px;height:12px;border:1px solid {N600};border-radius:1px;margin-left:5px;vertical-align:-1px}}
.bt.r{{border-radius:50%}}
.hr{{flex:1;display:flex;align-items:flex-start;border-bottom:1px solid {N300};font-size:11px;color:{N700};padding-top:3px}}
.tb4{{display:flex;font-size:9.5px;letter-spacing:.08em;text-transform:uppercase;color:{N700};margin-top:4px}}
.tb4 span{{flex:1}}.tb4 span:first-child{{flex:2}}
.dy{{flex:1;border-bottom:1px solid {N300};padding-top:5px}}
.dy .chip{{margin-left:0}}
.chips{{display:flex;flex-wrap:wrap;gap:3px}}
.chips .chip{{margin:0}}
.yg{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px 22px}}
.mname{{font-weight:600;font-size:13px}}
.mini{{width:100%;border-collapse:collapse;margin-top:4px}}
.mini td,.mini th{{text-align:center;font-size:9px;padding:1.5px 0;font-weight:400}}.mini th{{color:{N700};font-size:8px}}
.cal{{width:100%;height:100%;border-collapse:collapse;table-layout:fixed}}
.cal tr:first-child{{height:18px}}
.cal th{{font-size:9.5px;font-weight:400;letter-spacing:.08em;color:{N700};padding:0 0 6px;text-align:left}}
.cal td{{border-top:1px solid {N400};vertical-align:top;padding:5px 4px;font-size:13px;font-weight:600}}
.cal td.wk{{width:30px;font-size:9.5px;font-weight:400;color:{N700};letter-spacing:.06em}}
.cal td.out{{color:{N300}}}
.hol{{font-size:9.5px;font-style:italic;font-weight:400;color:{N800};margin-top:3px}}
.px{{border-collapse:collapse;width:100%}}.px th{{font-size:9px;font-weight:400;color:{N700};width:18px}}
.px td{{border:1px solid {N400};height:21px}}.px td.x{{background:{N300}}}
.bw{{border-collapse:collapse;width:100%;table-layout:fixed}}
.bw th{{font-size:8px;font-weight:400;color:{N700}}}.bw th.rl{{width:52px;text-align:left;font-size:9.5px;letter-spacing:.06em}}
.bw td{{border:1px solid {N400};height:26px}}.bw small{{font-size:7px;color:{N500}}}
.ag{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px 22px}}.am b{{font-size:13px;font-weight:600}}
.g2{{display:grid;grid-template-columns:1fr 1fr;grid-template-rows:repeat(3,1fr);gap:16px 26px;flex:1}}
.g3{{display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(4,1fr);gap:14px 22px;flex:1}}
.tr3{{display:flex;align-items:flex-end;gap:10px;height:30px;font-size:13px}}.tr3 b{{width:150px;font-weight:600}}
.xl{{display:grid;grid-template-columns:1fr 1fr;grid-template-rows:repeat(27,auto);grid-auto-flow:column;gap:0 24px}}
.xr{{display:flex;align-items:center;gap:8px;font-size:11.5px;height:24px;border-bottom:1px solid {N300}}}
.wn{{width:28px;font-size:9.5px;letter-spacing:.06em;color:{N700}}}.xn{{flex:1}}
.xd{{color:{N600};font-size:10px;font-style:italic}}.rate{{color:{N600};font-size:10px;letter-spacing:.1em}}
.wg{{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}}
.wc{{border-bottom:1px solid {N400};padding:8px 2px 6px;font-size:12px}}.wc b{{font-weight:600;margin-right:4px}}

/* ---- lead: 시안은 리드 항목에만 ---- */
.lead>.lab{{color:{CYAN700}}}
.lead .ln{{border-color:{CYAN40}}}
.lead .xr,.lead .ck{{border-color:{CYAN40}}}

/* ---- 상품 1 도구 (p1_tools.json) 를 같은 잉크로 ---- */
.p1 .body{{flex:1;display:flex;flex-direction:column;gap:16px;margin-top:20px;min-height:0}}
.p1 .row{{display:flex;gap:26px;min-height:0;flex:1}}
.p1 .col{{display:flex;flex-direction:column;gap:16px;min-height:0}}
.p1 .card{{display:flex;flex-direction:column;min-height:0;overflow:hidden;background:none;border:0;padding:0}}
.p1 .card::after{{display:none}}
.p1 .label{{flex:none;font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:{N700};margin-bottom:2px}}
.p1 .label::before{{display:none}}
.p1 .lines{{flex:1;display:flex;flex-direction:column;overflow:hidden;min-height:0}}
.p1 .lines>div{{flex:none;height:34px;border-bottom:1px solid {N400}}}
.p1 .field{{background:none;border-bottom:1px solid {N400};border-radius:0;min-height:26px}}
.p1 .box{{flex:none;width:12px;height:12px;background:none;border:1px solid {N600};border-radius:1px}}
.p1 .dot{{background:{N600}}}
.p1 .chip{{margin:0}}
.p1 table{{border-collapse:collapse}}
.p1 .trk td{{border-bottom:1px solid {N400};font-size:9px;color:{N700};padding:3px 2px}}
.p1 .trk td.dh{{text-align:center}}.p1 .trk td.we{{color:{N500}}}
.p1 .trk td.nm{{font-size:12px;color:{INK}}}
.p1 span{{font-size:12px}}
.p1 svg text{{font-family:"Source Serif 4",Georgia,serif}}
.p1{{--line:{N400};--soft:{N600};--mid:{N700};--ink:{INK};--field:transparent;--accent:{N700};--accent-text:{N800};--chip:transparent;--card:transparent;--bg:{PAPER}}}

/* 상품 1 은 굵기 700·800 을 썼다. 여기 폰트는 400·600 뿐 -- 700 을 두면 없는 굵기라 글자가 대체 폰트로 샌다
   (사분면 "Now · Important" 의 가운뎃점이 굴림으로 나왔다). 잉크 규칙대로 600 으로 */
.p1 [style*="font-weight:700"],.p1 [style*="font-weight:800"],.p1 b,.p1 strong{{font-weight:600!important}}
.p1 .q4>div>div>div{{font-weight:400!important}}
.p1 .q4>div{{border-top:1px solid {N400}}}
.p1 .q4>div>div{{border-left:1px solid {N400};padding:6px 8px;font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:{N700}}}
.p1 .q4>div>div:first-child{{border-left:0}}
/* ---- 표지·구분·일간 (여기서 새로 짠 것) ---- */
.cv-top{{display:flex;justify-content:space-between;font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:{N800}}}
.cv-t{{font-weight:600;font-size:88px;line-height:.95;letter-spacing:-.045em}}
.plate{{text-shadow:{PLATE}}}
.cmyk{{position:relative;font-weight:600;font-size:170px;line-height:.9;letter-spacing:-.04em;color:{PAPER};
  text-shadow:.036em .025em 0 {PAPER},-.031em -.023em 0 {PAPER}}}
.cmyk span{{position:absolute;left:0;top:0;mix-blend-mode:multiply;text-shadow:none}}
.cmyk .c{{color:#0088b0;transform:translate(-.026em,-.012em)}}
.cmyk .m{{color:#d6006c;transform:translate(.022em,.016em)}}
.cmyk .y{{color:#edbb00;transform:translate(.008em,-.02em)}}
.div-t{{font-weight:600;font-size:118px;line-height:.9;letter-spacing:-.045em}}
.one{{display:flex;align-items:flex-start;gap:16px}}
.one .n{{font-weight:600;font-size:62px;line-height:.8;color:{CYAN};text-shadow:{PLATE}}}
.one .l44{{flex:none;height:44px;border-bottom:1px solid {CYAN40}}}
.dots{{flex:1;min-height:40px;position:relative;overflow:hidden}}
"""


# ------------------------------------------------------------ custom pages --
def p_cover():
    idx = [("How this planner works", "how"), ("SOS — I'm stuck", "sos"), ("The 52 experiments", "experiments"),
           ("Year at a glance", "year"), ("Months", "month"), ("Weeks", "week"),
           ("Focus tools", "focus"), ("Feelings tools", "feel"), ("Body tools", "health"),
           ("Life admin", "life"), ("My ADHD playbook", "playbook"), ("Notes", "notes")]
    rows = "".join(f'<a href="#{k}" style="display:flex;gap:8px;font-size:13.5px"><span style="flex:1">{t}</span>'
                   f'<span style="color:{N700}" data-pn="{k}"></span></a>' for t, k in idx)
    start = "Monday" if WS == 0 else "Sunday"
    return f"""
    <div class="cv-top"><span>Jan – Dec {Y} · {start} start</span><span>Vol. {Y}</span></div>
    <div style="margin-top:40px"><div class="cv-t">The</div><div class="cv-t plate">ADHD</div><div class="cv-t">Year</div></div>
    <div style="font-style:italic;font-size:21px;line-height:1.45;color:{N800};margin-top:24px;max-width:470px">
      One small experiment a week. By December, a user manual for your own brain.</div>
    <div style="flex:1;display:flex;align-items:center;gap:36px;min-height:0">
      <div class="cmyk">52<span class="c">52</span><span class="m">52</span><span class="y">52</span></div>
      <div style="font-style:italic;font-size:19px;line-height:1.4;max-width:250px;color:{N800}">
        Fifty-two things to try. Keep the ones that work. Skip the weeks that don't.</div></div>
    <div style="font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:{CYAN700};margin-bottom:8px">In this planner</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:5px 40px">{rows}</div>
    <div style="margin-top:28px;display:flex;align-items:flex-end;gap:8px;font-size:13px">
      <span style="font-style:italic">Belongs to</span><span style="flex:1;height:1px;background:{N500}"></span></div>"""


GROUP_INTRO = {
    "focus": ("Focus", "For the moments when starting is the hard part."),
    "feel": ("Feelings", "For the days that land heavier than they should."),
    "health": ("Body", "Medication, sleep, food, movement — what you'll want to remember at your next visit."),
    "life": ("Life", "The admin that eats the week, and a few tools for the mess."),
}


def p_group(g):
    title, intro = GROUP_INTRO[g]
    _, items = W.P1[g]
    extra = [(k, C.TOOLS[k][0]) for k in W.NEW_TOOLS] if g == "life" else []
    rows = "".join(f'<a href="#{k}" style="display:flex;gap:8px;font-size:14px;padding:3px 0">'
                   f'<span style="flex:1">{t}</span><span style="color:{N700}" data-pn="{k}"></span></a>'
                   for k, t in items + extra)
    return f"""
    <div class="cv-top"><span>Part · Tools</span><span>{Y}</span></div>
    <div style="flex:1;display:flex;flex-direction:column;justify-content:center">
      <div class="div-t plate">{title}</div>
      <div style="font-style:italic;font-size:20px;line-height:1.45;color:{N800};margin-top:22px;max-width:470px">{intro}</div></div>
    <div style="columns:2;column-gap:40px">{rows}</div>"""


def p_day(d):
    n = W.WEEK_OF[d]
    doy = d.timetuple().tm_yday
    nd = calendar.monthrange(Y, d.month)[1]
    cat, q = C.question(d)
    yd, td = d - dt.timedelta(1), d + dt.timedelta(1)
    fut = C.future_note_target(d)
    arrived = "".join(W.chip(W.dk(s), f"Note from {W.md(s)} ←", "note") for s in W.NOTES_IN.get(d, []))
    hol = f'<span class="holchip">{W.e(W.HOL[d])}</span>' if d in W.HOL else ""
    head = W.head(f"{Y} · Week {n} · {calendar.day_name[d.weekday()]}", W.md(d), "",
                  hol + W.chip(f"m{d.month}", W.MA[d.month]) + W.chip(f"w{n}", f"Week {n}"))
    prog = (f'<div class="prog"><span>Day {doy} · {W.TOTAL - doy} left</span><div class="bar"><i style="width:{doy / W.TOTAL * 100:.1f}%"></i></div>'
            f'<span>{W.MA[d.month]} {d.day} of {nd}</span><div class="bar sm"><i style="width:{d.day / nd * 100:.1f}%"></i></div></div>')
    frm = W.chip(W.dk(yd), "From yesterday ←") if yd.year == Y else '<span class="chip off">Day one</span>'
    hours = ["7am", "8", "9", "10", "11", "12", "1pm", "2", "3", "4", "5", "6", "7", "8", "9"]
    sched = "".join(f'<div class="hr">{h}</div>' for h in hours)
    lanes = "".join(f'<div class="box" style="flex:none"><div class="lab">{t}<span class="hint"> {h}</span></div>{W.lines(1)}</div>'
                    for t, h in [("Low battery", "easy wins"), ("Medium", ""), ("Full", "the hard thing")])
    tom = W.chip(W.dk(td), "Tomorrow →") if td.year == Y else W.chip("yearreview", "Year review →")
    fut_c = W.chip(W.dk(fut), f"Arrives {W.md(fut)} →") if fut else W.chip("mailbox", "To the year-end mailbox →")
    return (head + prog
            + f'<div class="bd" style="gap:14px;margin-top:14px"><div class="rw a">{frm}{arrived}<span class="sp"></span>'
              f'<span class="lab" style="margin-right:2px">Battery</span>{BT * 5}</div>'
            + f'<div class="box lead" style="flex:none"><div class="one"><div class="n">1</div><div style="flex:1">'
              f'<div class="lab" style="color:{CYAN700}">The one thing<span class="hint" style="color:{CYAN800}"> if only this gets done</span></div>'
              f'<div class="l44"></div><div class="l44"></div>'
              f'<div style="display:flex;align-items:flex-end;gap:10px;margin-top:6px"><span class="hint" style="color:{CYAN800}">Tiniest first step</span>'
              f'<div class="ln fl" style="border-color:{CYAN40}"></div></div></div></div></div>'
            + f'<div class="rw" style="flex:1"><div class="box" style="flex:1.05"><div class="lab">Schedule<span class="hint"> leave a buffer after each thing</span></div>{sched}</div>'
              f'<div class="col" style="flex:1">'
              f'<div class="box" style="flex:none"><div class="lab">By energy</div>{lanes}</div>'
              f'<div class="box" style="flex:none"><div class="lab">Not today<span class="hint"> permission to drop</span></div>{W.lines(1)}</div>'
              f'<div class="box" style="flex:none"><div class="lab">Guess vs actual</div>'
              f'<div class="tb4"><span>task</span><span></span><span>guess</span><span>took</span></div>{W.lines(1)}</div>'
              f'<div class="box" style="flex:1;justify-content:flex-end"><div class="lab">Meds · water · mood</div>'
              f'<div style="margin-top:6px;font-size:12px">meds{BT * 2} &nbsp; water{BTR * 8}</div>'
              f'<div style="margin-top:6px;font-size:12px">mood{BTR * 5}</div></div></div></div>'
            + f'<div class="box" style="flex:none"><div class="lab">Question of the day · {cat}</div>'
              f'<div class="txt" style="font-style:italic;font-size:15px">{W.e(q)}</div>{W.lines(1)}</div>'
            + f'<div class="rw" style="flex:none"><div class="box" style="flex:1"><div class="lab">Tomorrow starts with</div>{W.lines(1)}<div style="margin-top:6px">{tom}</div></div>'
              f'<div class="box" style="flex:1"><div class="lab">Note to future me</div>{W.lines(1)}<div style="margin-top:6px">{fut_c}</div></div></div>'
            + '</div>')


def unwire(body):
    """와이어프레임이 인라인으로 준 회색 면을 벗긴다(면을 칠하지 않는다 -- 핸드오프 잉크 규칙)."""
    return body.replace("background:#EDEDED", "")


def p_p1(key, name):
    t = P1.get(key)
    if not t:
        return W.p_p1(key, name)
    body = t["body"]
    if key == "tasks":      # 사분면: 원본은 칸마다 배경색으로 나눴다 -> 괘선으로
        body = re.sub(r'(<div class="label">Sort it out</div>\s*<div)', lambda m: m.group(1) + ' class="q4"', body, count=1)
    return W.head(t["eyebrow"], t["title"], t["sub"]) + f'<div class="p1" style="flex:1;display:flex;flex-direction:column;min-height:0">{body}</div>'


def p_note(i):
    kind = ["Dot grid", "Ruled", "Plain", "Grid"][i - 1]
    if kind == "Dot grid":
        inner = dot_svg(604, 760)
    elif kind == "Ruled":
        inner = W.lines(22)
    elif kind == "Grid":
        inner = grid_svg(604, 760)
    else:
        inner = ""
    return W.head("Notes", kind) + f'<div class="bd"><div class="box" style="flex:1">{inner}</div></div>'


def dot_svg(w, h, step=17, r=1.1):
    d = "".join(f"M{x - r:.1f} {y}a{r} {r} 0 1 0 {2 * r} 0a{r} {r} 0 1 0 {-2 * r} 0"
                for y in range(step // 2, h, step) for x in range(step // 2, w, step))
    return f'<svg width="{w}" height="{h}" style="display:block"><path d="{d}" fill="{N400}"/></svg>'


def grid_svg(w, h, step=17):
    d = "".join(f"M{x}.5 0V{h}" for x in range(0, w, step)) + "".join(f"M0 {y}.5H{w}" for y in range(0, h, step))
    return f'<svg width="{w}" height="{h}" style="display:block"><path d="{d}" stroke="{N300}" stroke-width="1"/></svg>'


# -------------------------------------------------------------------- chrome --
def rail(on):
    out = []
    for k, t in TABS:
        a = k == on
        w, h = (26 if a else 22), 70
        sh = (f'<img src="bg/tabshadow-{w}x{h}.png" alt="" style="left:-{E.SHADOW_M}px;top:-{E.SHADOW_M}px;'
              f'width:{w + 2 * E.SHADOW_M}px;height:{h + 2 * E.SHADOW_M}px">')
        out.append(f'<a href="#{k}" class="{"on" if a else ""}">{t}{sh}</a>')
    return f'<nav class="rail">{"".join(out)}</nav>'


def footer_name(key, body):
    for pat, name in [(r"d\d+-\d+", "Daily"), (r"wr\d+", "Weekly reset"), (r"w\d+", "Weekly"), (r"mp\d+", "Month plan"),
                      (r"bw\d+", "Brain weather"), (r"mr\d+", "Month review"), (r"m\d+", "Monthly"), (r"q\d", "Quarter")]:
        if re.fullmatch(pat, key):
            return name
    m = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
    if m:
        return re.sub(r"<[^>]+>", "", m.group(1)).strip()
    return {"cover": "Cover", "focus": "Focus", "feel": "Feelings", "health": "Body", "life": "Life"}.get(key, key)


def mark_lead(key, body):
    for pat, label in LEAD:
        if re.fullmatch(pat, key):
            i = body.find(f'<div class="lab">{W.e(label)}')
            if i < 0:
                i = body.find(f'<div class="lab">{label}')
            if i > 0:
                j = body.rfind('<div class="box"', 0, i)
                if j >= 0:
                    body = body[:j] + '<div class="box lead"' + body[j + len('<div class="box"'):]
    return body


def page(key, body, n):
    sheet = "b" if key in SHEET_B else "a"
    body = mark_lead(key, unwire(body))
    fname = footer_name(key, body)
    foot = "" if key == "cover" else f'<footer><span>The ADHD Year · {Y}</span><span>{W.e(fname)} · {n:03d}</span></footer>'
    return (f'<section class="pg" id="{key}"><img class="bg" src="bg/sheet-{sheet}-2x.jpg" alt="">'
            f'<div class="sheet">{rail(W.rail_of(key) if key != "cover" else "index")}'
            f'<div class="ink">{body}{foot}</div></div></section>')


SAMPLE_KEYS = ["cover", "how", "sos", "experiments", "year", "kickoff", "m3", "mp3", "bw3", "d3-9", "mr3",
               "w11", "wr11", "playbook", "focus", "rsd", "tasks", "dopamine", "q1", "pixels"]


def specs():
    out = []
    for k, fn in W.specs():
        if k == "cover":
            fn = p_cover
        elif k in ("focus", "feel", "health", "life"):
            fn = (lambda g: lambda: p_group(g))(k)
        elif re.fullmatch(r"d\d+-\d+", k):
            m, d = map(int, k[1:].split("-"))
            fn = (lambda dd: lambda: p_day(dd))(dt.date(Y, m, d))
        elif k in P1:
            fn = (lambda kk: lambda: p_p1(kk, kk))(k)
        elif re.fullmatch(r"note\d", k):
            fn = (lambda i: lambda: p_note(i))(int(k[4:]))
        out.append((k, fn))
    if SAMPLE:
        out = [s for s in out if s[0] in SAMPLE_KEYS]
    return out


# Source Serif 4 에 없는 글자 -> 벡터. 두면 Chrome 이 시스템 폰트(굴림·Segoe UI Symbol)로 채운다.
_SV = '<svg viewBox="0 0 14 10" style="width:{w}em;height:.62em;vertical-align:{v}em;overflow:visible" aria-hidden="true"><path d="{d}" fill="none" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round"/></svg>'
GLYPHS = {
    "→": _SV.format(w=".95", v=".05", d="M1 5H13M10 2l3 3-3 3"),       # →
    "←": _SV.format(w=".95", v=".05", d="M13 5H1M4 2L1 5l3 3"),        # ←
    "✓": _SV.format(w=".7", v="-.02", d="M2 5.5l3 3L12 1.5"),          # ✓
    "✗": _SV.format(w=".6", v="-.02", d="M3 1.5l8 7M11 1.5l-8 7"),      # ✗
}


def vectorize_glyphs(html):
    body_at = html.index("<body>")
    head, body = html[:body_at], html[body_at:]
    for ch, svg in GLYPHS.items():
        body = body.replace(ch, svg)
    return head + body


def build():
    from playwright.sync_api import sync_playwright
    import pikepdf
    E.refuse_overwrite(OUT)
    (SRC / "bg").mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    for s in ("a", "b"):
        E.shift_background(E.HAND / "backgrounds" / f"sheet-{s}-2x.png", SRC / "bg" / f"sheet-{s}-2x.jpg")
    sp = specs()
    ids = [k for k, _ in sp]
    pages = "".join(page(k, fn(), i + 1) for i, (k, fn) in enumerate(sp))
    # 목차 쪽 번호 채우기
    pages = re.sub(r'<span style="color:#605d5d" data-pn="([^"]+)"></span>',
                   lambda m: f'<span style="color:{N700}">{ids.index(m.group(1)) + 1:03d}</span>' if m.group(1) in ids else "", pages)
    html = (f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>The ADHD Year {Y}</title>'
            f'<style>{CSS}</style></head><body>{pages}</body></html>')
    html = vectorize_glyphs(html)
    # 제어 문자가 본문에 끼면 Chrome 이 대체 폰트(굴림)로 그린다 -- 치환 버그로 U+0001 이 들어간 적이 있다(2026-09-25)
    ctrl = [c for c in html if ord(c) < 32 and c not in "\t\n\r"]
    if ctrl:
        raise SystemExit(f"HTML 에 제어 문자 {len(ctrl)}개 {sorted(set(map(repr, ctrl)))}")
    src = SRC / f"{FNAME}.html"
    src.write_text(html, encoding="utf-8")
    raw = OUT / f"{FNAME}.raw.pdf"
    with sync_playwright() as p:
        br = p.chromium.launch(channel="chrome")
        ctx = br.new_context(device_scale_factor=2)
        pg = ctx.new_page()
        for w in (22, 26):
            pg.set_content(f'<html><body style="margin:0;background:transparent"><div style="position:absolute;'
                           f'left:{E.SHADOW_M}px;top:{E.SHADOW_M}px;width:{w}px;height:70px;border-radius:0 2px 2px 0;'
                           f'box-shadow:{E.TAB_SHADOW}"></div></body></html>')
            pg.screenshot(path=str(SRC / "bg" / f"tabshadow-{w}x70.png"), omit_background=True,
                          clip={"x": 0, "y": 0, "width": w + 2 * E.SHADOW_M, "height": 70 + 2 * E.SHADOW_M})
        ctx.close()
        ctx = br.new_context(user_agent=E.STATIC_FONT_UA)
        pg = ctx.new_page()
        pg.goto(src.as_uri(), timeout=300000)
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(800)
        pg.pdf(path=str(raw), width="768px", height="1024px", print_background=True, prefer_css_page_size=False,
               margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
        br.close()
    final = OUT / f"{FNAME}.pdf"
    subprocess.run([sys.executable, str(ROOT / "scripts" / "dedupe_pdf.py"), str(raw), str(final)], check=True,
                   capture_output=True)
    with pikepdf.open(final, allow_overwriting_input=True) as pdf:
        pdf.save(final, object_stream_mode=pikepdf.ObjectStreamMode.generate, recompress_flate=True)
    raw.unlink()
    print(f"{final}  {len(ids)}p  {final.stat().st_size:,} B")
    # 폰트는 Source Serif 4 서브셋만 -- 대체 폰트가 끼면 실패 (에디션·표본에서 굴림·Segoe 가 끼었다)
    import pymupdf
    fonts = {f[3] for pg in pymupdf.open(final) for f in pg.get_fonts(full=True)}
    stray = sorted(f for f in fonts if "SourceSerif4" not in f)
    print(f"  fonts {sorted(fonts)}")
    if stray:
        raise SystemExit(f"Source Serif 4 가 아닌 폰트: {stray} -- GLYPHS 에 그 글자를 넣을 것")
    if not SAMPLE:
        bad, miss = W.check_links(html)
        dead = sorted(set(re.findall(r'href="?#([^" >]+)', html)) - set(ids))
        print(f"  dead links {len(dead)} {dead[:5]} · time links broken {len(bad)} · weeks missing {miss}")
    return ids, html


if __name__ == "__main__":
    build()
