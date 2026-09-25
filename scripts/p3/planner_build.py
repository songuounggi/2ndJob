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
import html as htmllib
import json
import os
import pathlib
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = pathlib.Path(__file__).resolve().parent
# 파이썬 문자열 안의 역참조(\1)가 제어 문자로 박힌 적이 두 번 있다(2026-09-25) -- 소스부터 확인한다
_own = pathlib.Path(__file__).read_text(encoding="utf-8")
_bad = [i for i, c in enumerate(_own) if ord(c) < 32 and ord(c) not in (9, 10, 13)]
if _bad:
    raise SystemExit(f"planner_build.py 소스에 제어 문자 {len(_bad)}개 (위치 {_bad[:5]}) -- 역참조 대신 lambda 로")
sys.path.insert(0, str(HERE))
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
SAMPLE = "--sample" in sys.argv
KEYS = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--keys=")), None)   # --keys=admin,q1
sys.argv = [sys.argv[0]] + ARGS          # p3_wireframe 는 argv 로 연도·주 시작을 읽는다
import p3_content as C
import p3_wireframe as W
import editions_build as E

ROOT = HERE.parents[1]
Y, WS, TAG = W.Y, W.WS, W.TAG
# v0.1 = 첫 전체 빌드(일간 맨 아래 칩의 누르는 영역이 칸 overflow 에 잘려 34px) / v0.2 = 그 수정
# v0.3 = 발문의 & 이중 이스케이프(Morning &amp;amp; evening 등 3장) 수정
# v0.4 = (사용자 확정) 빈 입력 행 34px + 행 추가 + 줄마다 선 하나(8장), Project planner 좌우 첫 줄 맞춤,
#        Life admin radar 월 칸 아래 줄 맞춤, Brain weather 이름 칸 52px(표와 겹침)
# v0.5 = 월 달력 공휴일 있는 줄만 길고 숫자와 겹치던 것(1·10·12월) 수정
# v0.6 = (내용) Life admin radar 문구 한 줄로 -- 10~12월 넷째 항목이 잘렸다, Neurodiversity Celebration Week 인쇄
VERSION = "v0.6"
OUT = ROOT / "output" / "prod3" / "planner" / VERSION
SRC = ROOT / "src" / "prod3" / "planner" / VERSION
if SAMPLE:
    # 검수용 표본도 보여 준 것은 남긴다(덮어쓰지 않는다) -- sample-01, sample-02 ... 새 번호로
    _n = 1
    while (OUT / f"sample-{_n:02d}").exists():
        _n += 1
    OUT, SRC = OUT / f"sample-{_n:02d}", SRC / f"sample-{_n:02d}"
# 시험본은 이름부터 다르게 -- 진짜와 같은 이름이라 사용자가 20쪽짜리 시험본을 검수한 적이 있다(2026-09-25)
FNAME = f"TEST-sample-ADHD-Year-Planner-{TAG}" if SAMPLE else f"ADHD-Year-Planner-{TAG}"
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
.rail{{position:absolute;left:100%;top:61px;display:flex;flex-direction:column;z-index:-1}}
/* 누르는 영역(링크) = 47x76px(9.8x15.9mm): 탭 오른쪽 책상 여백 25px 와 위아래 틈 3px 씩까지.
   보이는 탭(.tv)은 그대로 22x70 (활성 26). Apple 권장 최소 44pt = 8.5mm = 이 페이지에서 41px */
.rail a{{position:relative;display:block;width:{22 + 38 - E.SHIFT}px;height:76px}}
.rail .tv{{position:absolute;left:0;top:3px;display:flex;align-items:center;justify-content:center;width:22px;height:70px;
  writing-mode:vertical-rl;font-size:10px;letter-spacing:.12em;text-transform:uppercase;
  background:{PAPER};color:{N800};border-radius:0 2px 2px 0}}
/* 활성 탭은 진한 시안: 흰 글자 대비 3.65 -> 5.72 (작은 글자 기준 4.5 이상) */
.rail a.on .tv{{width:26px;background:{CYAN700};color:#f3f2f2}}
.rail .tv img{{position:absolute;z-index:-1;pointer-events:none}}
footer{{flex:none;display:flex;justify-content:space-between;margin-top:14px;font-size:10.5px;
  letter-spacing:.1em;text-transform:uppercase;color:{N700}}}

/* ---- head ---- */
.hd{{flex:none}}
.eb{{font-size:11.5px;letter-spacing:.1em;text-transform:uppercase;color:{N700}}}
.tr{{display:flex;align-items:flex-end;gap:8px;margin-top:8px}}.sp{{flex:1}}
h1{{font-weight:600;font-size:40px;line-height:1;letter-spacing:-.02em}}
.sub{{font-style:italic;font-size:14px;line-height:1.45;color:{N800};margin-top:8px;max-width:470px}}
/* 칩 = 레퍼런스 표 7c 의 알약 칸: 양 끝 반원, 1px neutral-400 선 (2026-09-25 사용자: 직사각형 버튼이 촌스럽다) */
.chip{{display:inline-flex;align-items:center;justify-content:center;min-width:44px;height:22px;
  font-size:10px;letter-spacing:.08em;text-transform:uppercase;line-height:1;
  border:1px solid {N400};border-radius:999px;padding:0 10px;margin:1px 0 1px 4px;color:{N800};white-space:nowrap;gap:5px}}
.chip.note{{background:{INK};border-color:{INK};color:{PAPER}}}
.chip.off{{border-style:dotted;color:{N500}}}
.lead .chip{{border-color:{CYAN}}}
/* 링크 칩의 누르는 영역: 알약(22px) + 위아래 10px = 42px(8.8mm). 음수 여백으로 레이아웃은 그대로 */
a.hit{{display:inline-flex;box-sizing:content-box;padding:10px 4px;margin:-10px -4px;vertical-align:middle}}
a.hit>.chip{{margin-left:0}}
.tr a.hit,.rw.a a.hit{{margin-left:0}}
.holchip{{font-style:italic;font-size:12px;color:{N800};margin-right:6px}}

/* ---- body (wireframe classes, re-inked) ---- */
.bd{{flex:1;display:flex;flex-direction:column;gap:16px;margin-top:20px;min-height:0}}
.rw{{display:flex;gap:26px;min-height:0}}.rw.a{{align-items:center;gap:6px;flex:none}}
.col{{display:flex;flex-direction:column;gap:16px;min-height:0}}
.box{{display:flex;flex-direction:column;min-height:0;overflow:hidden}}
.box .box{{padding-top:2px}}
.lab{{flex:none;font-size:11.5px;letter-spacing:.1em;text-transform:uppercase;color:{N700};line-height:1.2}}
.hint{{text-transform:none;letter-spacing:0;font-style:italic;color:{N800};font-size:11.5px}}
.txt{{font-size:13.5px;line-height:1.5;margin-top:3px}}
.txt b{{font-weight:600}}
.ln{{flex:none;height:34px;border-bottom:1px solid {N400}}}.ln.fl{{flex:1;height:22px}}
.fill{{flex:1;border-bottom:1px solid {N300}}}
a.row{{display:flex;align-items:baseline;gap:12px;padding:11px 0 10px;border-bottom:1px solid {N300};font-size:15px}}
a.row b{{font-weight:600}} a.row span:last-child{{margin-left:auto;color:{N600}}}
.ck{{display:flex;align-items:center;gap:9px;font-size:13px;padding:5px 0}}
.ck i{{flex:none;width:11px;height:11px;border:1px solid {N600};border-radius:1px}}
.prog{{flex:none;display:flex;align-items:center;gap:10px;font-size:10px;letter-spacing:.08em;
  text-transform:uppercase;color:{N700};margin-top:12px}}
.bar{{flex:3;height:5px;border:1px solid {N500}}}.bar.sm{{flex:1}}.bar i{{display:block;height:100%;background:{N500}}}
.bt{{display:inline-block;width:12px;height:12px;border:1px solid {N600};border-radius:1px;margin-left:5px;vertical-align:-1px}}
.bt.r{{border-radius:50%}}
.hr{{flex:1;display:flex;align-items:flex-start;border-bottom:1px solid {N300};font-size:11px;color:{N700};padding-top:3px}}
.tb4{{display:flex;font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:{N700};margin-top:4px}}
.tb4 span{{flex:1}}.tb4 span:first-child{{flex:2}}
.dy{{flex:1;border-bottom:1px solid {N300};padding-top:5px}}
.dy .chip{{margin-left:0}}
.chips{{display:flex;flex-wrap:wrap;gap:8px}}
/* 분기의 주 번호 알약(W1-W13): 한 줄 가운데 정렬, 간격 8px (사용자: 다닥다닥 답답하다 -> 한 줄로)
   38px x 13 + 8px x 12 = 590px < 본문 604px */
.chips.wk{{display:flex;flex-wrap:nowrap;justify-content:center;gap:8px;padding:10px 0 8px}}
.chips.wk a.hit{{flex:0 1 38px;min-width:0}}
.chips.wk a.hit>.chip{{width:100%}}
/* 14주짜리 분기도 있다(2026 Q4, 2027 Q3) -> 38px 에서 모자라면 줄어든다: 14 x 35.7 + 13 x 8 = 604 */
.chips.wk .chip{{min-width:0;padding:0;margin:0}}
.chips .chip{{margin:0}}
.yg{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px 22px}}
.mname{{font-weight:600;font-size:13px}}
.mini{{width:100%;border-collapse:collapse;margin-top:4px}}
.mini td,.mini th{{text-align:center;font-size:9px;padding:0;font-weight:400}}
.mini td>a{{display:block;padding:1.5px 0}}.mini th{{color:{N700};font-size:8px}}
.cal{{width:100%;height:100%;border-collapse:collapse;table-layout:fixed}}
.cal tr:first-child{{height:18px}}
.cal th{{font-size:9.5px;font-weight:400;letter-spacing:.08em;color:{N700};padding:0 0 6px;text-align:left}}
.cal td{{position:relative;border-top:1px solid {N400};vertical-align:top;padding:5px 4px;font-size:13px;font-weight:600}}
/* 달력 칸 전체가 그날로 가는 링크 (숫자 글자만 누르던 것) */
.cal td>a{{position:absolute;inset:0;padding:5px 4px}}
.cal td.wk>a{{display:flex;align-items:center;justify-content:center;padding:0}}
.hol{{margin-top:18px}}
/* 칸 전체를 링크로 만들며 숫자를 띄웠더니 공휴일만 칸 안에 남아, 표가 그 줄에 높이를 몰아줬다(1·10·12월 첫 줄이 길고 숫자와 겹침, v0.1~v0.4).
   공휴일도 띄워 숫자 아래(5 + 18px)에 둔다 -- 모든 줄이 같은 높이, 원래 모양 */
.cal td>.hol{{position:absolute;top:23px;left:4px;right:4px;margin:0}}
.cal td.wk{{width:30px;font-size:9.5px;font-weight:400;color:{N700};letter-spacing:.06em}}
.cal td.out{{color:{N300}}}
.hol{{font-size:9.5px;font-style:italic;font-weight:400;color:{N800};margin-top:3px}}
.px{{border-collapse:collapse;width:100%}}.px th{{font-size:9px;font-weight:400;color:{N700};width:18px}}
.px td{{border:1px solid {N400};height:21px}}.px td.x{{background:{N300}}}
.bw{{border-collapse:collapse;width:100%;table-layout:fixed}}
.bw th{{font-size:8px;font-weight:400;color:{N700}}}
.bw th>a{{display:block;padding:2px 0}}.bw th.rl{{width:52px;text-align:left;font-size:9.5px;letter-spacing:.06em}}
.bw tr:first-child>th:first-child{{width:52px}}   /* table-layout:fixed 는 첫 줄로 너비를 정한다 -- 빠져 있어 이름 칸이 17px, 글자가 표와 겹쳤다(v0.3) */
.bw td{{border:1px solid {N400};height:26px}}.bw small{{font-size:7px;color:{N500}}}
.ag{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px 22px}}.am b{{font-size:13px;font-weight:600}}
.am>a{{display:block;padding:10px 0 9px;margin:-10px 0 -9px}}
.am{{display:flex;flex-direction:column}}.am>.ln{{margin-top:auto}}   /* 월 칸 아래 줄을 칸 바닥에 -- 같은 줄 세 칸의 선 높이를 맞춘다(사용자) */
.g2{{display:grid;grid-template-columns:1fr 1fr;grid-template-rows:repeat(3,1fr);gap:16px 26px;flex:1}}
.g3{{display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(4,1fr);gap:14px 22px;flex:1}}
.tr3{{display:flex;align-items:flex-end;gap:10px;height:30px;font-size:13px}}.tr3 b{{width:150px;font-weight:600}}
.xl{{display:grid;grid-template-columns:1fr 1fr;grid-template-rows:repeat(27,auto);grid-auto-flow:column;gap:0 24px}}
.xr{{display:flex;align-items:center;gap:8px;font-size:12.5px;height:41px;border-bottom:1px solid {N300}}}
/* 52 실험 목록만 촘촘하게(한 장에 53줄) -- 누르는 영역 24px 는 알려진 예외 */
.xl .xr{{height:24px;font-size:11.5px}}
.wn{{width:28px;font-size:9.5px;letter-spacing:.06em;color:{N700}}}.xn{{flex:1}}
.xd{{color:{N600};font-size:10px;font-style:italic}}.rate{{color:{N600};font-size:10px;letter-spacing:.1em}}
.wg{{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}}
.wc{{border-bottom:1px solid {N400};padding:12px 2px 11px;font-size:12px}}.wc b{{font-weight:600;margin-right:4px}}

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
.p1 .label{{flex:none;font-size:11.5px;letter-spacing:.1em;text-transform:uppercase;color:{N700};margin-bottom:2px}}
.p1 .label::before{{display:none}}
.p1 .lines{{flex:1;display:flex;flex-direction:column;overflow:hidden;min-height:0}}
.p1 .lines>div{{flex:none;height:34px;border-bottom:1px solid {N400}}}
.p1 .field{{background:none;border-bottom:1px solid {N400};border-radius:0;min-height:26px}}
/* 빈 입력 행(.ir, ROWS_JS 가 표시)은 구분선을 빼고 항목|금액 밑줄만 -- 34px 에서 두 선이 4px 로 붙었다(사용자 확정 A안, 8장만) */
.p1 .ir{{border-bottom:0!important}}
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
/* 사분면: 원본은 색칠한 네모 4개를 8pt 간격으로 띄웠다. 선으로 바꾸면 그 간격 때문에 세로선이 끊겨
   T 자 두 개로 보였다(사용자 지적) -> 간격을 없애 + 자 하나로 */
.p1 .q4{{gap:0!important}}
.p1 .q4>div{{gap:0!important;border-top:1px solid {N400}}}
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
    rows = "".join(f'<a href="#{k}" style="display:flex;gap:8px;font-size:13.5px;padding:12px 0 10px;border-bottom:1px solid {N300}"><span style="flex:1">{t}</span>'
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
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:0 40px">{rows}</div>
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
    rows = "".join(f'<a href="#{k}" style="display:flex;gap:8px;font-size:14px;padding:11px 0 10px;border-bottom:1px solid {N300};break-inside:avoid">'
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
            + f'<div class="rw" style="flex:none"><div class="box" style="flex:1;overflow:visible"><div class="lab">Tomorrow starts with</div>{W.lines(1)}<div style="margin-top:6px">{tom}</div></div>'
              f'<div class="box" style="flex:1;overflow:visible"><div class="lab">Note to future me</div>{W.lines(1)}<div style="margin-top:6px">{fut_c}</div></div></div>'
            + '</div>')


def unwire(body):
    """와이어프레임이 인라인으로 준 회색 면을 벗긴다(면을 칠하지 않는다 -- 핸드오프 잉크 규칙)."""
    return body.replace("background:#EDEDED", "")


def p_mreview(m):
    """월 리뷰 -- 문구·칸은 와이어프레임과 같고 배치만 두 칸씩.
    라벨 11.5px·실험 줄 41px(누르는 영역) 로 키우자 한 장을 넘쳐 W13 줄이 잘렸다(2026-09-25)."""
    _, _, q = C.MONTHS[m - 1]
    wk = [n for n, f in enumerate(W.WEEKS, 1) if W.home_month(f) == m]
    exps = "".join(f'<a class="xr" href="#w{n}"><span class="wn">W{n}</span><span class="xn">{W.e(C.experiment(n)[0])}</span>'
                   f'<span class="rate">✓ ~ ✗</span></a>' for n in wk)
    (t1, h1), (t2, h2), (t3, h3), (t4, h4) = C.MONTH_REVIEW
    b = lambda t, h="": W.box(t.upper(), W.lines(2), "1", h)
    return (W.head(f"{W.MN[m].upper()} {Y} · REVIEW", "Month review", "Not a report card. Just a look back.", W.chip(f"m{m}", W.MA[m]))
            + f'<div class="bd">{W.box(t1.upper(), W.lines(2), "none", h1)}'
            + f'<div class="rw">{b(t2, h2)}{b(t3, h3)}</div>'
            + f'<div class="rw">{b(t4, h4)}{b(q)}</div>'
            + '<div class="rw">' + W.box("ADHD TAX THIS MONTH", '<div class="hint">late fees, rebuys, forgotten subscriptions</div>'
                                         + '<div class="tb4"><span>what</span><span></span><span></span><span>$</span></div>' + W.lines(2)
                                         + '<div class="txt"><b>Total $ ____</b></div>')
            + W.box("HYPERFOCUS HARVEST", '<div class="hint">what grabbed you · useful? · fun?</div>' + W.lines(3)) + '</div>'
            + W.box("THIS MONTH'S EXPERIMENTS", exps, "1") + '</div>')


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
        out.append(f'<a href="#{k}" class="{"on" if a else ""}"><span class="tv">{t}{sh}</span></a>')
    return f'<nav class="rail">{"".join(out)}</nav>'


def footer_name(key, body):
    for pat, name in [(r"d\d+-\d+", "Daily"), (r"wr\d+", "Weekly reset"), (r"w\d+", "Weekly"), (r"mp\d+", "Month plan"),
                      (r"bw\d+", "Brain weather"), (r"mr\d+", "Month review"), (r"m\d+", "Monthly"), (r"q\d", "Quarter")]:
        if re.fullmatch(pat, key):
            return name
    m = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
    if m:
        return htmllib.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()   # 발문에서 W.e 가 다시 이스케이프한다
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
    body = re.sub(r'<a class="chip( [a-z ]*)?" href="#([^"]+)">(.*?)</a>',   # class="chip " (공백 하나)도
                  lambda m: f'<a class="hit" href="#{m.group(2)}"><span class="chip{m.group(1) or ""}">{m.group(3)}</span></a>', body)
    if re.fullmatch(r"q\d", key):
        body = body.replace('<div class="chips">', '<div class="chips wk">', 1)
    fname = footer_name(key, body)
    foot = "" if key == "cover" else f'<footer><span>The ADHD Year · {Y}</span><span>{W.e(fname)} · {n:03d}</span></footer>'
    return (f'<section class="pg" id="{key}"><img class="bg" src="bg/sheet-{sheet}-2x.jpg" alt="">'
            f'<div class="sheet">{rail(W.rail_of(key) if key != "cover" else "index")}'
            f'<div class="ink">{body}{foot}</div></div></section>')


SAMPLE_KEYS = ["cover", "how", "sos", "experiments", "year", "kickoff", "q3", "m3", "mp3", "bw3", "d3-9", "mr3",
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
        elif re.fullmatch(r"mr\d+", k):
            fn = (lambda mm: lambda: p_mreview(mm))(int(k[2:]))
        elif k in P1:
            fn = (lambda kk: lambda: p_p1(kk, kk))(k)
        elif re.fullmatch(r"note\d", k):
            fn = (lambda i: lambda: p_note(i))(int(k[4:]))
        out.append((k, fn))
    if SAMPLE:
        out = [s for s in out if s[0] in (KEYS or SAMPLE_KEYS)]
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


# 괘선이 있는 칸 중, 크기가 바깥 레이아웃으로 정해져서 아래가 비어 있는 칸에만 괘선을 더 긋는다.
# 한 줄 넣어 칸 높이가 바뀌면(내용 따라 크는 칸) 그 줄을 빼고 멈춘다 -- 레이아웃은 흔들리지 않는다.
FILL_JS = r"""
() => {
  let boxes = 0, added = 0;
  document.querySelectorAll('.box').forEach(b => {
    const lns = b.querySelectorAll(':scope > .ln:not(.fl)');
    if (!lns.length || !b.lastElementChild.classList.contains('ln')) return;   // 괘선 아래 다른 것(알약 등)이 있으면 두지 않는다
    const last = lns[lns.length - 1];
    let n = 0;
    for (let i = 0; i < 40; i++) {
      const h0 = b.getBoundingClientRect().height;
      const room = b.getBoundingClientRect().bottom - last.parentNode.lastElementChild.getBoundingClientRect().bottom;
      if (room < 34) break;
      const ln = document.createElement('div'); ln.className = 'ln';
      b.appendChild(ln);
      if (Math.abs(b.getBoundingClientRect().height - h0) > 0.5 || ln.getBoundingClientRect().bottom > b.getBoundingClientRect().bottom + 0.5) { ln.remove(); break; }
      n++;
    }
    if (n) { boxes++; added += n; }
  });
  return [boxes, added];
}
"""


# 상품 1 도구의 빈 입력 행(flex:1 로 칸 높이를 행 수로 나눠 46~103px 이 됐다)을 괘선과 같은 34px 로.
# 칸(카드) 크기는 먼저 고정해 페이지 배치는 그대로 두고, 남는 자리는 행을 늘리지 않고 같은 행을 더 넣는다(사용자).
# 이름이 붙은 행(MON..SUN, 1..6, A/B/C)은 개수가 뜻이라 두지 않는다 -- 건드리지 않는다.
ROW = 34
ROWS_JS = r"""
(ROW) => {
  const isRow = r => /^flex:1;display:flex/.test(r.getAttribute('style') || '') && r.querySelector(':scope>.field');
  const groups = new Map();
  document.querySelectorAll('.p1 div').forEach(r => {
    if (!isRow(r)) return;
    const p = r.parentElement; if (!groups.has(p)) groups.set(p, []); groups.get(p).push(r);
  });
  let n = 0, added = 0;
  const box = [...groups].filter(([p, rows]) => rows.length >= 3 && rows.every(r => !r.innerText.trim()));
  // 칸의 폭·높이를 둘 다 지금 값으로 고정 (flex:none 만 주면 옆으로 나란한 칸의 폭이 줄어든다)
  box.map(([p]) => [p, p.getBoundingClientRect()]).forEach(([p, r]) => { p.style.flex = 'none'; p.style.width = r.width + 'px'; p.style.height = r.height + 'px'; });
  box.forEach(([p, rows]) => rows.forEach(r => { r.style.flex = 'none'; r.style.height = ROW + 'px'; }));
  // 옆으로 나란한 칸끼리 첫 줄 높이를 맞춘다(사용자: Project planner 왼쪽 Steps / 오른쪽 Done looks like).
  // 설명 글(be specific) 때문에 늦게 시작하는 쪽에 맞춰, 먼저 시작하는 쪽을 내린다. 간격은 그대로.
  box.forEach(([, rows]) => rows.forEach(r => r.classList.add('ir')));   // 입력 행 표시 (style 글자는 JS 가 고치면 모양이 바뀐다)
  const firstLine = c => { const f = c.querySelector('.ir>.field');
    const l = c.querySelector('.lines>div'); const ys = [f && f.getBoundingClientRect().bottom, l && l.getBoundingClientRect().bottom].filter(Boolean);
    return ys.length ? Math.min(...ys) : null; };
  let aligned = 0;
  new Set(box.map(([p]) => p.parentElement)).forEach(row => {
    const cs = getComputedStyle(row); if (cs.display !== 'flex' || cs.flexDirection !== 'row') return;
    const cards = [...row.children].map(c => [c, firstLine(c)]).filter(([, y]) => y !== null);
    if (cards.length < 2) return;
    const top = Math.max(...cards.map(([, y]) => y));
    cards.forEach(([c, y]) => {
      if (top - y < 0.5) return;
      const t = box.find(([p]) => p === c) ? box.find(([p]) => p === c)[1][0] : c.querySelector('.lines');
      t.style.marginTop = (parseFloat(getComputedStyle(t).marginTop) + top - y) + 'px'; aligned++;
    });
  });
  box.forEach(([p, rows]) => {
    const tpl = rows.find(r => /border-bottom/.test(r.getAttribute('style'))) || rows[0];
    const last = rows[rows.length - 1];
    for (let i = 0; i < 60; i++) {
      const c = tpl.cloneNode(true); c.style.marginTop = '0'; p.insertBefore(c, last);   // 첫 행의 정렬 여백은 복제하지 않는다
      if (p.scrollHeight > p.clientHeight + 0.5 || last.getBoundingClientRect().bottom > p.getBoundingClientRect().bottom + 0.5) { c.remove(); break; }
      added++;
    }
    n++;
  });
  return [n, added, aligned];
}
"""


# 레이아웃 결함 검사 (사용자가 iPad 에서 찾은 것, 2026-09-25)
#  - Brain weather 이름 칸 글자가 칸을 넘친다(표와 겹침)
#  - Life admin radar 같은 줄 세 칸의 아래 줄 높이가 다르다
#  - 상품 1 도구의 빈 입력 행이 34px 이 아니다(칸 높이를 행 수로 나눠 46~103px)
#  - 월 달력 날짜 줄 높이가 다르다(공휴일 있는 줄만 길었다)
LAYOUT_JS = r"""
() => {
  const bad = [];
  document.querySelectorAll('.bw th.rl').forEach(th => {
    if (th.scrollWidth > th.clientWidth + 1) bad.push(th.closest('section').id + ' label overflow: ' + th.textContent.trim());
  });
  document.querySelectorAll('.ag').forEach(g => {
    const rows = {};
    g.querySelectorAll(':scope > .am').forEach(a => {
      const ln = a.querySelector(':scope > .ln'); if (!ln) return;
      const k = Math.round(a.getBoundingClientRect().top);
      (rows[k] = rows[k] || []).push(Math.round(ln.getBoundingClientRect().bottom));
    });
    Object.values(rows).forEach(b => { if (new Set(b).size > 1) bad.push(g.closest('section').id + ' month lines ' + b.join('/')); });
  });
  // 월 달력: 날짜 줄은 전부 같은 높이
  document.querySelectorAll('table.cal').forEach(t => {
    const hs = [...t.rows].slice(1).map(r => Math.round(r.getBoundingClientRect().height));
    // 마지막 줄은 원래 5~8px 짧다(표 높이 나머지) -- 그건 두고, 한 줄만 크게 길어지는 것(v0.4 1월 270 vs 111)을 잡는다
    if (Math.max(...hs) - Math.min(...hs) > 10) bad.push(t.closest('section').id + ' calendar rows ' + hs.join('/'));
  });
  const groups = new Map();
  document.querySelectorAll('.p1 div:has(>.field)').forEach(r => {
    if (getComputedStyle(r).display !== 'flex' || r.innerText.trim()) return;   // style 글자가 아니라 계산된 값으로
    const p = r.parentElement; if (!groups.has(p)) groups.set(p, []); groups.get(p).push(r);
  });
  groups.forEach((rows, p) => {
    if (rows.length < 3) return;
    const hs = [...new Set(rows.map(r => Math.round(r.getBoundingClientRect().height)))];
    if (hs.length !== 1 || hs[0] !== 34) bad.push(p.closest('section').id + ' input rows ' + hs.join('/'));
    // 높이만 재면 행 사이 여백을 못 본다(복제 행에 정렬 여백이 따라간 적이 있다) -- 행 간격도 잰다
    const gaps = [...new Set(rows.slice(1).map((r, i) => Math.round(r.getBoundingClientRect().top - rows[i].getBoundingClientRect().top)))];
    if (gaps.length > 1 || (gaps.length && gaps[0] !== 34)) bad.push(p.closest('section').id + ' input row pitch ' + gaps.join('/'));
  });
  return bad;
}
"""


MIN_TOUCH = 41      # px -- Apple 권장 최소 44pt = 8.5mm (iPad 11 세로, 페이지 폭 맞춤: 1px = 0.209mm)


def touch_report(pdf_path, ids):
    """PDF 안 모든 링크의 누르는 영역을 잰다. 짧은 변이 MIN_TOUCH 미만인 것을 종류별로 센다."""
    import collections
    import pymupdf
    small, total = collections.Counter(), 0
    ex = {}
    for i, pg in enumerate(pymupdf.open(pdf_path)):
        for l in pg.get_links():
            r = l["from"]
            w, h = r.width / 0.75, r.height / 0.75
            total += 1
            if min(w, h) < MIN_TOUCH:
                src = re.sub(r"\d+(-\d+)?", "#", ids[i])
                kind = f"{src} {int(w)}x{int(h)}"
                small[kind] += 1
    print(f"  링크 {total}개 · 누르는 영역 {MIN_TOUCH}px(8.5mm) 미만 {sum(small.values())}개")
    for k, v in small.most_common(12):
        print(f"    {v:5d}  {k}")
    return small


def build():
    from playwright.sync_api import sync_playwright
    import pikepdf
    # 한 버전 폴더에 판 4개(2026/2027 x 월/일)가 들어간다 -> 폴더가 아니라 그 판 파일이 있으면 멈춘다
    if (OUT / f"{FNAME}.pdf").exists():
        raise SystemExit(f"{OUT / (FNAME + '.pdf')} 는 이미 있다. 덮어쓰지 않는다 -- VERSION 을 올릴 것.")
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
    # 이미 이스케이프된 글을 또 이스케이프하면 화면에 "&amp;" 가 글자로 찍힌다(v0.2 발문 3장)
    dbl = re.findall(r"&amp;(?:amp|lt|gt|quot|#\d+);", html)
    if dbl:
        raise SystemExit(f"HTML 에 이중 이스케이프 {len(dbl)}개 {sorted(set(dbl))}")
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
        rows = pg.evaluate(ROWS_JS, ROW)
        print(f"  입력 행 34px: 칸 {rows[0]}개, 더한 행 {rows[1]}줄, 첫 줄 맞춘 칸 {rows[2]}개")
        filled = pg.evaluate(FILL_JS)
        print(f"  괘선 채움: 칸 {filled[0]}개에 {filled[1]}줄")
        lay = pg.evaluate(LAYOUT_JS)
        if lay:
            raise SystemExit(f"레이아웃 결함 {len(lay)}개 {lay[:6]}")
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
    touch_report(final, ids)
    if not SAMPLE:
        norm = re.sub(r'<a class="hit" href="#([^"]+)"><span class="chip ?[a-z ]*">(.*?)</span></a>',
                      lambda m: '<a class="chip " href="#' + m.group(1) + '">' + m.group(2) + '</a>', html)
        bad, miss = W.check_links(norm)
        dead = sorted(set(re.findall(r'href="?#([^" >]+)', html)) - set(ids))
        print(f"  dead links {len(dead)} {dead[:5]} · time links broken {len(bad)} · weeks missing {miss}")
    return ids, html


if __name__ == "__main__":
    build()
