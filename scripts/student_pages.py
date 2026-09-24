# -*- coding: utf-8 -*-
"""상품 2(학생용)의 탭 구성과 페이지들.

`build_planner.py` 가 `T["app"]` 테마에서 이 모듈의 TABS/GROUPS/specs() 로
갈아끼운다. 상품 1(v1~v8)의 페이지 세트는 건드리지 않는다.

페이지 선정 근거는 `product2-student.md` 의 "타겟" 과 "구성안" 이다.
타겟의 실제 고통 다섯 가지에 각각 페이지가 붙어 있어야 한다:
  1 강의계획서를 옮겨 적지 않는다      -> Syllabus unpack
  2 마감을 역산하지 못한다              -> Working backwards
  3 시험 범위를 쪼개지 못한다           -> Exam study plan
  4 조별과제에서 자기 몫이 흐려진다     -> Group project
  5 걸릴 시간을 과소평가한다            -> Guess vs actual
페이지를 더하거나 뺄 때 이 대응이 깨지지 않는지 먼저 볼 것.
"""
import app_style as A

bp = None                      # build_planner. init() 에서 채운다


def init(module):
    global bp
    bp = module


# ------------------------------------------------------------------ 탭
TABS = [
    ("index",    "INDEX"),
    ("semester", "SEMESTER"),
    ("week",     "WEEKS"),   # 목차·제목·북마크와 같은 복수형
    ("day",      "DAYS"),
    ("classes",  "CLASSES"),
    ("work",     "WORK"),
    ("study",    "STUDY"),
    ("focus",    "FOCUS"),
    ("life",     "LIFE"),
    ("notes",    "NOTES"),
]

# 탭 하나가 묶는 하위 페이지들. 탭은 분류고, 상품의 깊이는 여기에 있다.
GROUPS = {
    # 학기마다 반복되는 것은 여기 넣지 않는다. 칩 격자로 간다(REPEATS).
    "semester": [
        ("terms", "All eight terms", "four years on one page"),
    ],
    "classes": [],
    "work": [
        ("backwards", "Working backwards", "from the deadline, not from today"),
        ("group", "Group project", "who does what, by when"),
        ("estimate", "Guess vs actual", "how long it really took"),
        ("obstacle", "Obstacle plan", "what will get in the way"),
    ],
    "study": [
        ("cornell", "Lecture notes", "cue, notes, summary"),
        ("reading", "Reading log", "to read, and read"),
        ("session", "Study session log", "when and where it worked"),
        ("office", "Office hours", "what to ask, before you forget"),
    ],
    "focus": [
        ("braindump", "Brain dump", "empty your head onto the page"),
        ("focus-session", "Focus session", "one block, one thing"),
        ("deciding", "Stuck on deciding", "pick, don't optimise"),
        ("avoiding", "Why I am avoiding it", "name it and it shrinks"),
        ("energy", "Energy budget", "what you actually have today"),
    ],
    "life": [
        ("meds", "Medication log", "what you took, and when"),
        ("sleep", "Sleep log", "hours in, hours slept"),
        ("mood", "Mood", "how the week actually felt"),
    ],
}

TERMS = 8                      # 4년 = 8학기
WEEKS_PER_TERM = 16
DAYS_PER_TERM = 14             # 매일치가 아니다 -- 필요한 날에 쓰는 장수
CLASSES_PER_TERM = 5           # 학기당 수강 과목
SYLLABUS_PER_TERM = 5          # 과목마다 강의계획서 한 장
EXAMS_PER_TERM = 3             # 중간·기말·퀴즈

# 반복 세트. (앞글자, 학기당 장수, 라벨). 앞글자는 한 글자여야 한다 --
# build_planner 의 rail_key 가 ([a-z])(\d+) 로 읽는다.
REPEATS = [("t", 1, "Term overview"), ("o", 1, "Term goals"),
           ("r", 1, "Term review"),
           ("w", WEEKS_PER_TERM, "Weeks"), ("d", DAYS_PER_TERM, "Days"),
           ("h", 1, "Class schedule"), ("k", 1, "Who to ask"),
           ("c", CLASSES_PER_TERM, "Class pages"),
           ("s", SYLLABUS_PER_TERM, "Syllabus unpack"),
           ("a", 1, "Assignment tracker"),
           ("e", EXAMS_PER_TERM, "Exam study plan"),
           ("g", 1, "Grade tracker")]


# --------------------------------------------------------------- 조각들
def card(label, inner, flex="none", pad=""):
    """라벨이 비면 라벨 줄을 아예 만들지 않는다. 빈 문자열을 넘겨도
    .label 의 색 바(2.6pt)는 그려져, 제목 아래에 의미 없는 색 조각이
    떠 있었다(brain dump / notes)."""
    head = '<div class="label">%s</div>' % label if label else ""
    return ('<div class="card" style="flex:%s;%s">%s%s</div>'
            % (flex, pad, head, inner))


def tbl(kind, cols, rows, check_last=False, parts=None):
    """표 하나. kind 는 t4(4열) 또는 t6(6열) -- 가로 점선 규칙이 열 수마다
    따로 만들어져 있으므로 새 열 수를 쓰려면 app_style 에 먼저 추가한다.

    parts 는 열 너비 비율. 기본 T4 는 첫 열이 가장 넓은 "과제명" 표에
    맞춘 것이라, 첫 열에 짧은 것(DAY)을 적는 표에서는 빈 열이 가장
    넓고 정작 길게 쓰는 열이 좁았다(2026-09-24 전수 검수)."""
    widths = (A.prop(A.CW, parts) if parts
              else A.T4 if kind == "t4" else A.T6)
    hd = "".join('<td style="width:%.2fpt">%s</td>' % (w, c)
                 for w, c in zip(widths, cols))
    cells = []
    for i in range(len(cols)):
        last = check_last and i == len(cols) - 1
        cells.append('<td class="bx"><i></i></td>' if last else "<td></td>")
    row = "<tr>%s</tr>" % "".join(cells)
    return ('<div class="tbwrap"><table class="tb %s"><tr>%s</tr>%s</table>%s'
            '</div>' % (kind, hd, row * rows, A.rules_svg(widths, rows, head_h=24.0)))


def field(h=24):
    return '<div class="field" style="height:%gpt"></div>' % h


def fill(flex=1):
    """면 하나를 괘선으로 채운다. 줄은 SVG pattern 이 높이에 맞춰 깐다 --
    <div> 로 줄을 세던 방식은 면 높이와 안 맞아 아래가 비었다."""
    rows = "<div></div>" * 26 if A.DASH_BORDER else ""
    return ('<div class="lines" style="flex:%g">%s%s</div>'
            % (flex, rows, A.lines_svg()))


def body(*parts):
    return '<div class="body">%s</div>' % "".join(parts)


def head(term, title, sub_, date=None):
    """반복 페이지의 머리. eyebrow 에 학기를 적고 제목은 학기 내 번호다.

    전에는 제목이 통번호("Week 36")라, 목차에서 TERM 3 의 "4" 를 눌러
    도착하면 숫자가 달라 잘못 눌렀다고 판단했다.

    date 를 주면 머리 오른쪽 빈자리에 날짜 칸을 둔다. 날짜 없는 상품인데
    적을 칸이 한 곳도 없었다(2026-09-24). 머리는 높이 72pt 고정이라
    본문은 한 줄도 줄지 않는다(시안 A/B/C 중 사용자가 A 선택).
    """
    h = bp.head("Term %d" % term, title, sub_)
    if date:
        assert h.endswith("</div>")
        h = (h[:-6] + '<div class="datebox"><span>%s</span>'
             '<div class="field"></div></div></div>' % date)
    return h


# --------------------------------------------------------- 핵심 페이지들
def p_syllabus(term=1, i=1):
    """이 상품의 핵심 셀링 포인트. 강의계획서 한 장을 세 종류로 분해한다.

    쓰기 시작하는 문턱을 낮추려고 과목/교수 같은 머리 정보를 먼저 받고,
    그 다음에 표 세 개로 나눈다. 한 표에 다 넣으면 옮겨 적기를 포기한다.
    """
    return (head(term, "Syllabus unpack",
                    "One handout. Pull out the dates, then close it.")
            + body(
                card("Class", field(24)),
                card("Assignments &mdash; what is due, and when",
                     tbl("t4", ["WHAT", "TYPE", "DUE", "DONE"], 5,
                         check_last=True)),
                card("Exams &amp; quizzes",
                     tbl("t4", ["WHAT", "COVERS", "DATE", "DONE"], 3,
                         check_last=True)),
                card("Reading &mdash; what has to be read before class",
                     tbl("t4", ["READING", "FOR WEEK", "PAGES", "DONE"], 4,
                         check_last=True))))
    # "Anything else" 필기면은 뺐다(2026-09-23). 표 셋 아래에 남는 높이가
    # 라벨 한 줄뿐이라 면 전체가 페이지 밖으로 밀려 라벨만 떠 있었다.
    # 살리려면 표에서 4행을 덜어야 하는데, 이 페이지의 값은 표에 있다.


def p_assignments(term=1, i=1):
    return (head(term, "Assignment tracker",
                    "Everything with a deadline, in one place")
            + body(card("This term",
                        tbl("t4", ["ASSIGNMENT", "CLASS", "DUE", "DONE"], 22,
                            check_last=True))))


def p_group_project():
    return (bp.head("Work", "Group project",
                    "The part that goes wrong is who was doing what.")
            + body(
                card("The project", field(24)),
                card("Who does what, by when",
                     tbl("t4", ["PIECE", "WHO", "BY WHEN", "DONE"], 7,
                         check_last=True)),
                card("My part &mdash; in my own words", fill(), flex="1")))


def p_exam(term=1, i=1):
    """범위를 쪼개고 날짜에 배분한다. '공부하기'는 과제가 아니다."""
    return (head(term, "Exam study plan",
                    "Split the scope first. Then give each piece a day.")
            + body(
                card("Exam", field(24)),
                card("The scope, in pieces",
                     tbl("t4", ["PIECE", "SOURCE", "DAY", "DONE"], 12,
                         check_last=True)),
                card("What I keep getting wrong", fill(), flex="1")))


def p_cornell():
    """코넬 노트. 왼쪽 단서 / 오른쪽 본문 / 아래 요약."""
    return (bp.head("Study", "Lecture notes", "Cue, notes, summary")
            + body(
                card("Class &amp; date", field(24)),
                '<div class="row" style="flex:1;gap:14pt">'
                + card("Cue", fill(), flex="1")
                + card("Notes", fill(), flex="2.1")
                + '</div>',
                card("Summary &mdash; in your own words",
                     '<div class="lines" style="flex:none;height:%gpt">%s%s'
                     '</div>' % (3 * A.ROW_H,
                                 "<div></div>" * 3 if A.DASH_BORDER else "",
                                 A.lines_svg()))))


def p_grades(term=1, i=1):
    return (head(term, "Grade tracker",
                    "What each piece is worth, and what you got")
            + body(
                card("Class", field(24)),
                card("Pieces",
                     tbl("t4", ["PIECE", "WEIGHT", "SCORE", "DONE"], 16,
                         check_last=True)),
                card("Where I stand", field(36))))
    # "Anything else" 는 뺐다(2026-09-23). 표와 입력칸 아래로 라벨만
    # 남고 면이 페이지 밖으로 밀렸다 -- p_syllabus 와 같은 사례.


def p_reading():
    return (bp.head("Study", "Reading log", "To read, and read")
            + body(card("Readings",
                        tbl("t4", ["READING", "CLASS", "BY", "READ"], 22,
                            check_last=True))))


def p_session():
    return (bp.head("Study", "Study session log",
                    "Notice when it works, and do that again.")
            + body(card("Sessions",
                        tbl("t4", ["WHAT I STUDIED", "WHERE", "HOW LONG",
                                   "IT WORKED"], 22, check_last=True))))


def p_office():
    return (bp.head("Study", "Office hours",
                    "Write the question down when you have it, not later.")
            + body(
                card("Who, and when", field(24)),
                card("What I want to ask", fill(), flex="1"),
                card("What they said", fill(), flex="1")))


def p_timetable(term=1, i=1):
    days = ["MON", "TUE", "WED", "THU", "FRI"]
    hours = ["08", "09", "10", "11", "12", "13", "14", "15", "16",
             "17", "18", "19", "20"]
    widths = A.T6
    hd = ('<tr><td style="width:%.2fpt"></td>' % widths[0]
          + "".join('<td style="width:%.2fpt">%s</td>' % (widths[i + 1], d)
                    for i, d in enumerate(days)) + "</tr>")
    rows = "".join("<tr><td>%s</td>%s</tr>" % (h, "<td></td>" * len(days))
                   for h in hours)
    return (head(term, "Class schedule",
                    "Write it once, in week one.")
            + body('<div class="tbwrap" style="flex:none">'
                   '<table class="tb t6">%s%s</table>%s</div>'
                   % (hd, rows, A.rules_svg(widths, len(hours), head_h=24.0)),
                   card("Notes for the week", fill(), flex="1")))


def p_contacts(term=1, i=1):
    return (head(term, "Who to ask",
                    "The name you will need at 11pm the night before")
            + body(card("Professors &amp; TAs",
                        tbl("t4", ["NAME", "CLASS", "OFFICE HOURS", "ASKED"],
                            22, check_last=True))))


def p_class(term, i):
    """과목별 페이지. 한 과목의 모든 것이 한 장에 있어야 찾으러 가지 않는다."""
    return (head(term, "Class %d" % i,
                 "Everything about one class, on one page")
            + body(
                card("Class", field(24)),
                '<div class="row" style="flex:none;gap:14pt">'
                + card("Professor / TA", field(24), flex="1")
                + card("Room &amp; time", field(24), flex="1")
                + '</div>',
                card("How the grade is made up",
                     tbl("t4", ["PIECE", "WEIGHT", "DUE", "DONE"], 5,
                         check_last=True)),
                card("Things to remember", fill(), flex="1")))


# ----------------------------------------------------- 학기 / 주간 / 일간
def p_terms():
    return (bp.head("Semester", "All eight terms", "Four years, one page")
            + body(card("Terms",
                        tbl("t4", ["TERM", "WHAT IT IS FOR", "CREDITS",
                                   "DONE"], 8, check_last=True,
                                 parts=[100, 240, 100, 60])),
                   card("Notes on the four years", fill(), flex="1")))


def p_term(term, i=1):
    """학기 개요 한 장. 16주를 한 장에 놓고, 무거운 주를 미리 본다."""
    # Week N 은 그 주 페이지로 가는 링크다. 칸 전체를 덮어(display:flex)
    # 손가락으로 누르기 쉽게 하고, 목차 행과 같은 › 로 눌린다는 걸 보인다.
    rows = "".join(
        '<tr><td><a href="#w%d" style="display:flex;justify-content:'
        'space-between;align-items:center;height:100%%;color:inherit;'
        'text-decoration:none">Week %d<span style="color:#5B5375;'
        'font-size:11pt">'
        '&rsaquo;</span></a></td><td></td><td></td>'
        '<td class="bx"><i></i></td></tr>'
        % ((term - 1) * WEEKS_PER_TERM + w, w)
        for w in range(1, WEEKS_PER_TERM + 1))
    # WEEK 열은 라벨과 링크뿐이라 적을 게 없다. T4 의 첫 열(과제명용
    # 220 비율)을 물려받아 넓고 비어 보였다(2026-09-24 지적). 좁히고 그
    # 폭을 실제로 적는 WHAT IS DUE 에 준다.
    widths = A.prop(A.CW, [100, 240, 100, 60])
    hd = "".join('<td style="width:%.2fpt">%s</td>' % (w, c)
                 for w, c in zip(widths, ["WEEK", "WHAT IS DUE", "EXAMS",
                                          "CLEAR"]))
    return (bp.head("Semester", "Term %d" % term,
                    "Sixteen weeks. Fill in the heavy ones first.")
            + body('<div class="tbwrap" style="flex:none">'
                   '<table class="tb t4"><tr>%s</tr>%s</table>%s</div>'
                   % (hd, rows,
                      A.rules_svg(widths, WEEKS_PER_TERM, head_h=24.0)),
                   card("What this term is really about", fill(), flex="1")))


def p_week(term, i):
    return (head(term, "Week %d" % i, "What has to happen this week",
                 date="WEEK OF")
            + body(
                card("Due this week",
                     tbl("t4", ["WHAT", "CLASS", "DAY", "DONE"], 6,
                         check_last=True)),
                card("Reading", fill(), flex="1"),
                card("One thing I will not drop", field(36))))


def p_day(term, i):
    return (head(term, "Day %d" % i, "One thing. Then the rest.",
                 date="DATE")
            + body(
                card("Just one thing today", field(36)),
                card("Due soon",
                     tbl("t4", ["ASSIGNMENT", "CLASS", "DUE", "DONE"], 5,
                         check_last=True)),
                card("Brain dump", fill(), flex="1")))


# ------------------------------------------------------------ 집중 / 생활
def p_braindump():
    return (bp.head("Focus", "Brain dump",
                    "Everything in your head, on the page. No order.")
            + body(card("", fill(), flex="1")))


def p_focus_session():
    return (bp.head("Focus", "Focus session", "One block. One thing.")
            + body(
                card("The one thing", field(36)),
                # flex:none -- .row 기본값은 flex:1 이라 입력칸만 든 이 행이
                # 남는 높이를 삼켜 Start/Stop 아래가 222pt 비었다
                '<div class="row" style="flex:none;gap:14pt">'
                + card("Start", field(24), flex="1")
                + card("Stop", field(24), flex="1")
                + '</div>',
                card("What pulled me away", fill(), flex="1")))


def p_deciding():
    return (bp.head("Focus", "Stuck on deciding",
                    "Pick one. You can change it later.")
            + body(
                card("The decision", field(36)),
                '<div class="row" style="flex:1;gap:14pt">'
                + card("If I pick this", fill(), flex="1")
                + card("If I pick that", fill(), flex="1")
                + '</div>',
                card("Picked", field(36))))


def p_avoiding():
    return (bp.head("Focus", "Why I am avoiding it",
                    "Name it and it gets smaller.")
            + body(
                card("The thing", field(36)),
                card("What I think will happen", fill(), flex="1"),
                card("The smallest possible first step", field(36))))


def p_energy():
    return (bp.head("Focus", "Energy budget",
                    "What you actually have today, not what you wish")
            + body(
                card("Today I have about this much",
                     tbl("t4", ["WHAT I WILL SPEND IT ON", "CLASS", "COST",
                                "DONE"], 6, check_last=True)),
                card("What I am not doing today", fill(), flex="1")))


def p_backwards():
    return (bp.head("Work", "Working backwards",
                    "Start at the deadline and walk back.")
            + body(
                card("Due", field(24)),
                card("Steps, in reverse",
                     tbl("t4", ["STEP", "NEEDS", "BY WHEN", "DONE"], 16,
                         check_last=True)),
                card("So I start on", field(36))))
    # "Anything else" 는 뺐다(2026-09-23). 표와 입력칸 아래로 라벨만
    # 남고 면이 페이지 밖으로 밀렸다 -- p_syllabus 와 같은 사례.


def p_estimate():
    return (bp.head("Work", "Guess vs actual",
                    "You are not bad at this. You just have no data yet.")
            + body(card("Tasks",
                        tbl("t4", ["TASK", "I GUESSED", "IT TOOK", "DONE"],
                            22, check_last=True))))


def p_obstacle():
    return (bp.head("Work", "Obstacle plan",
                    "Decide now what you will do when it goes wrong.")
            + body(
                card("The plan", field(36)),
                card("What will get in the way",
                     tbl("t4", ["OBSTACLE", "WHEN", "WHAT I WILL DO",
                                "READY"], 6, check_last=True)),
                card("If it all falls apart", fill(), flex="1")))


def p_goals(term=1, i=1):
    return (head(term, "Term goals",
                    "Three is plenty. Make them checkable.")
            + body(
                card("This term",
                     tbl("t4", ["GOAL", "HOW I WILL KNOW", "BY WHEN", "DONE"],
                         5, check_last=True)),
                card("Why these", fill(), flex="1")))


def p_term_review(term=1, i=1):
    return (head(term, "Term review", "Five minutes, once a term")
            + body(
                card("What actually happened", fill(), flex="1"),
                card("What I will do differently", fill(), flex="1"),
                card("What worked &mdash; keep it", field(36))))


def p_meds():
    return (bp.head("Life", "Medication log", "What you took, and when")
            + body(card("This month",
                        tbl("t4", ["DAY", "WHAT", "TIME", "TAKEN"], 22,
                            check_last=True, parts=[100, 240, 100, 60]))))


def p_sleep():
    return (bp.head("Life", "Sleep log", "Hours in bed, hours asleep")
            + body(card("This month",
                        tbl("t4", ["DAY", "IN BED", "ASLEEP", "OK"], 22,
                            check_last=True, parts=[100, 170, 170, 60]))))


def p_mood():
    return (bp.head("Life", "Mood", "How the week actually felt")
            + body(
                card("This week",
                     tbl("t4", ["DAY", "HOW IT FELT", "WHAT HAPPENED", "OK"],
                         7, check_last=True, parts=[100, 140, 200, 60])),
                card("Anything else", fill(), flex="1")))


def p_notes():
    return (bp.head("Notes", "Blank space")
            + body(card("", fill(), flex="1")))


# --------------------------------------------------- 반복 페이지의 목차
# 칩 그림자. flat_paint 에서는 box-shadow 대신 0.4pt 헤어라인 -- 흐린
# 그림자가 칩마다 소프트마스크가 되어 Weeks 목차 한 장에 128개, 렌더
# 545ms 였다(check_render, 2026-09-24). RELEASE.md 2 절 표 첫 줄.
CHIP_H = 19.0                  # 칩 높이 (app_style.CHIP_H 와 같게)
CHIP_ROW_GAP = 4.5             # 칩 줄 사이
CHIP_EDGE = ("" if A.CHIP_SHADOW       # v0.4~: 줄 단위로 구운 그림자(chip_card)
             else "border:.4pt solid rgba(120,110,160,.22);" if A.FLAT
             else "box-shadow:0 1pt 5pt rgba(40,28,90,.12);")


def chip_w(cols, single):
    """칩 폭 pt. 그림자 PNG 를 칩 폭에 맞춰 굽는 데 쓴다. 격자 식과 같아야
    한다: 학기당 1장은 본문 폭 8칸(간격 6), 여럿은 TERM 라벨(34+8) 뺀 폭."""
    if single:
        return (A.CW - 6 * 7) / 8.0
    return (A.CW - 42 - 5 * (cols - 1)) / float(cols)


def chip(href, text, w=None):
    return '<a href="#%s" style="%s">%s</a>' % (href, CHIP, text)


def grid_shadow(cols, rows, single):
    """칩 묶음 전체의 그림자(v0.4~). 묶음 div 에 position:relative 를
    주고 이것을 첫 자식으로 넣는다."""
    if not A.CHIP_SHADOW:
        return ""
    if single:
        return A.chip_grid_shadow_tag(8, 1, chip_w(8, True), 6.0, 0, 0)
    return A.chip_grid_shadow_tag(cols, rows, chip_w(cols, False), 5.0,
                                  CHIP_H + CHIP_ROW_GAP, 42.0)
CHIP = ("display:flex;align-items:center;justify-content:center;"
        "height:19pt;border-radius:7pt;text-decoration:none;"
        "background:rgba(255,255,255,.55);" + CHIP_EDGE +
        "font-size:7.5pt;font-weight:700;color:#2B2540")


def chip_card(label, prefix, per_term, cols=16):
    """학기별로 묶은 칩 격자 한 장.

    학기당 1장인 세트는 학기 칩 8개만 놓는다. 링크가 없는 목차는 목차가
    아니다 -- Chrome 은 목적지 없는 <a href="#x"> 를 조용히 버린다.
    """
    if per_term == 1:
        chips = "".join(chip("%s%d" % (prefix, t), t)
                        for t in range(1, TERMS + 1))
        grid = ('<div style="position:relative;display:grid;'
                'grid-template-columns:repeat(8,1fr);gap:6pt">%s%s</div>'
                % (grid_shadow(8, 1, True), chips))
        return ('<div class="card" style="flex:none">'
                '<div class="label">%s</div>%s</div>' % (label, grid))
    blocks = []
    for t in range(1, TERMS + 1):
        chips = "".join(
            chip("%s%d" % (prefix, (t - 1) * per_term + i), i)
            for i in range(1, per_term + 1))
        blocks.append(
            '<div style="display:flex;align-items:center;gap:8pt;'
            'margin-bottom:%gpt">' % CHIP_ROW_GAP +
            '<div style="font-size:6.6pt;letter-spacing:.12em;font-weight:800;'
            'color:#4A4260;width:34pt;flex:none">TERM %d</div>'
            '<div style="flex:1;display:grid;'
            'grid-template-columns:repeat(%d,1fr);gap:5pt">%s</div></div>'
            % (t, cols, chips))
    return ('<div class="card" style="flex:none"><div class="label">%s</div>'
            '<div style="position:relative">%s%s</div></div>'
            % (label, grid_shadow(cols, TERMS, False), "".join(blocks)))


def chip_index(eyebrow, title, sub_, prefix, per_term, cols):
    return (bp.head(eyebrow, title, sub_)
            + body(chip_card("", prefix, per_term, cols),
                   card("Anything else", fill(), flex="1")))


def p_week_index():
    return chip_index("Jump to", "Weeks",
                      "Sixteen weeks a term, eight terms", "w",
                      WEEKS_PER_TERM, WEEKS_PER_TERM)


def p_day_index():
    return chip_index("Jump to", "Days",
                      "Fourteen a term. Use them on the days you need.",
                      "d", DAYS_PER_TERM, DAYS_PER_TERM)


def group_page(key, title, sub, chips=""):
    """탭의 목차 페이지. build_planner 의 p_group 을 쓰지 않는 이유:
    그쪽은 'Anything else' 칸에 bp.lines(6) 을 쓰는데, 앱 테마의 괘선은
    SVG 가 그리므로 줄이 하나도 안 나온다."""
    items = GROUPS.get(key, [])
    rows = "".join(
        '<a href="#%s" style="display:flex;align-items:center;gap:12pt;'
        'padding:7pt 0;text-decoration:none;color:#241E3A;%s">'
        '<div class="dot"></div>'
        '<div style="flex:1"><div style="font-size:10.5pt;font-weight:700">'
        '%s</div><div style="font-size:8.5pt;color:#5B5375;margin-top:2pt">'
        '%s</div></div><div style="color:#5B5375;font-size:11pt">&rsaquo;</div>'
        '</a>'
        % (k, "" if i == len(items) - 1
           else "border-bottom:.6pt solid rgba(120,110,160,.20)", n, d)
        for i, (k, n, d) in enumerate(items))
    body_parts = []
    if rows:
        body_parts.append('<div class="card" style="flex:none">%s</div>' % rows)
    if chips:
        body_parts.append(chips)
    body_parts.append(card("Anything else", fill(), flex="1"))
    return bp.head("Jump to", title, sub) + body("".join(body_parts))


# -------------------------------------------------------------- 페이지 목록
def specs():
    """(키, 본문 만드는 함수) 목록. 순서가 PDF 페이지 순서다."""
    out = [("cover", bp.p_cover), ("index", bp.p_index)]

    def group(key, title, sub_, *chips):
        out.append((key, (lambda k=key, t=title, u=sub_, c="".join(chips):
                          lambda: group_page(k, t, u, c))()))

    def rep(prefix, per, fn):
        """학기 × 학기당 장수. 키는 통번호, 제목은 학기 내 번호다."""
        for t in range(1, TERMS + 1):
            for i in range(1, per + 1):
                out.append(("%s%d" % (prefix, (t - 1) * per + i),
                            (lambda tt=t, ii=i, f=fn: lambda: f(tt, ii))()))

    group("semester", "Semester", "Eight terms, sixteen weeks each",
          chip_card("Term overview", "t", 1),
          chip_card("Term goals", "o", 1),
          chip_card("Term review", "r", 1))
    out.append(("terms", p_terms))
    rep("t", 1, p_term)
    rep("o", 1, p_goals)
    rep("r", 1, p_term_review)

    out.append(("week", p_week_index))
    rep("w", WEEKS_PER_TERM, p_week)

    out.append(("day", p_day_index))
    rep("d", DAYS_PER_TERM, p_day)

    group("classes", "Classes", "Timetable, and one page per class",
          chip_card("Class schedule", "h", 1),
          chip_card("Who to ask", "k", 1),
          chip_card("One page per class", "c", CLASSES_PER_TERM,
                    CLASSES_PER_TERM))
    rep("h", 1, p_timetable)
    rep("k", 1, p_contacts)
    rep("c", CLASSES_PER_TERM, p_class)

    group("work", "Work", "Syllabus, assignments, group projects",
          chip_card("Syllabus unpack", "s", SYLLABUS_PER_TERM,
                    SYLLABUS_PER_TERM),
          chip_card("Assignment tracker", "a", 1))
    rep("s", SYLLABUS_PER_TERM, p_syllabus)
    rep("a", 1, p_assignments)
    out += [("backwards", p_backwards), ("group", p_group_project),
            ("estimate", p_estimate), ("obstacle", p_obstacle)]

    group("study", "Study", "Exams, lecture notes, grades",
          chip_card("Exam study plan", "e", EXAMS_PER_TERM, EXAMS_PER_TERM),
          chip_card("Grade tracker", "g", 1))
    rep("e", EXAMS_PER_TERM, p_exam)
    rep("g", 1, p_grades)
    out += [("cornell", p_cornell), ("reading", p_reading),
            ("session", p_session), ("office", p_office)]

    group("focus", "Focus", "For when starting is the hard part")
    out += [("braindump", p_braindump), ("focus-session", p_focus_session),
            ("deciding", p_deciding), ("avoiding", p_avoiding),
            ("energy", p_energy)]

    group("life", "Life", "The admin that eats the week")
    out += [("meds", p_meds), ("sleep", p_sleep), ("mood", p_mood)]

    out.append(("notes", p_notes))
    return out


# 반복 페이지가 어느 탭을 켜는가. 하나라도 빠지면 그 페이지에서 레일이
# 통째로 꺼져 "앱에서 튕겨나온" 느낌이 된다.
REPEAT_TAB = [("t", "semester"), ("o", "semester"), ("r", "semester"),
              ("w", "week"), ("d", "day"),
              ("h", "classes"), ("k", "classes"), ("c", "classes"),
              ("s", "work"), ("a", "work"),
              ("e", "study"), ("g", "study")]


# ------------------------------------------------------------ 북마크(개요)
# 맨 위 항목의 이름. 레일 글자는 대문자라 사이드바에서 소리치듯 읽힌다.
TAB_TITLES = {"index": "Where to?", "semester": "Semester", "week": "Weeks",
              "day": "Days", "classes": "Classes", "work": "Work",
              "study": "Study", "focus": "Focus", "life": "Life",
              "notes": "Notes"}


def outline():
    """뷰어 사이드바의 북마크. [(제목, 페이지 id, [하위...]), ...]

    손으로 적지 않고 TABS / GROUPS / REPEATS 에서 뽑는다 -- 페이지를
    더하거나 옮기면 북마크가 저절로 따라간다. 탭 아래 순서는 실제
    페이지 순서다. 반복 세트는 학기별로 한 단계 더 내려가고, 한 탭이
    반복 세트 하나뿐이면(Weeks, Days) 학기를 바로 탭 아래에 둔다.
    """
    order = {k: n for n, (k, _) in enumerate(specs())}
    reps = {pre: (per, label) for pre, per, label in REPEATS}

    def terms(pre):
        per = reps[pre][0]
        return [("Term %d" % t, "%s%d" % (pre, (t - 1) * per + 1), [])
                for t in range(1, TERMS + 1)]

    out = []
    for key, _ in TABS:
        kids = [(reps[pre][1], "%s1" % pre, terms(pre))
                for pre, tab in REPEAT_TAB if tab == key]
        kids += [(name, k, []) for k, name, _ in GROUPS.get(key, [])]
        kids.sort(key=lambda it: order[it[1]])
        if len(kids) == 1 and kids[0][2]:
            kids = kids[0][2]
        out.append((TAB_TITLES[key], key, kids))
    return out


def add_outline(pdf_path):
    """PDF 에 북마크를 심는다. 하위가 있는 항목은 접어 둔다 -- 처음
    사이드바에는 탭 10개만 보인다."""
    import pikepdf
    page = {k: n for n, (k, _) in enumerate(specs())}

    def item(title, key, kids):
        it = pikepdf.OutlineItem(title, page[key])
        for k in kids:
            it.children.append(item(*k))
        it.is_closed = bool(kids)
        return it

    with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
        with pdf.open_outline() as ol:
            ol.root.clear()
            for top in outline():
                ol.root.append(item(*top))
        pdf.save(pdf_path)
    return sum(1 + sum(1 + len(g[2]) for g in t[2]) for t in outline())
