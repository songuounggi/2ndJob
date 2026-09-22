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
    ("week",     "WEEK"),
    ("day",      "DAY"),
    ("classes",  "CLASSES"),
    ("work",     "WORK"),
    ("study",    "STUDY"),
    ("focus",    "FOCUS"),
    ("life",     "LIFE"),
    ("notes",    "NOTES"),
]

# 탭 하나가 묶는 하위 페이지들. 탭은 분류고, 상품의 깊이는 여기에 있다.
GROUPS = {
    "semester": [
        ("terms", "All eight terms", "four years on one page"),
        ("goals", "Term goals", "what you want out of this term"),
        ("term-review", "Term review", "what actually happened"),
    ],
    "classes": [
        ("timetable", "Class schedule", "the week, hour by hour"),
        ("contacts", "Who to ask", "professors, TAs, office hours"),
    ],
    "work": [
        ("syllabus", "Syllabus unpack", "one handout, broken into dates"),
        ("assignments", "Assignment tracker", "due, started, handed in"),
        ("backwards", "Working backwards", "from the deadline, not from today"),
        ("group", "Group project", "who does what, by when"),
        ("estimate", "Guess vs actual", "how long it really took"),
        ("obstacle", "Obstacle plan", "what will get in the way"),
    ],
    "study": [
        ("exam", "Exam study plan", "split the scope, spread the days"),
        ("cornell", "Lecture notes", "cue, notes, summary"),
        ("reading", "Reading log", "to read, and read"),
        ("grades", "Grade tracker", "what each piece is worth"),
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
DAYS_PER_TERM = 31             # 매일치가 아니다 -- 필요한 날에 쓰는 31장
CLASSES = 8                    # 과목별 페이지


# --------------------------------------------------------------- 조각들
def card(label, inner, flex="none", pad=""):
    return (f'<div class="card" style="flex:{flex};{pad}">'
            f'<div class="label">{label}</div>{inner}</div>')


def tbl(kind, cols, rows, check_last=False):
    """표 하나. kind 는 t4(4열) 또는 t6(6열) -- 가로 점선 규칙이 열 수마다
    따로 만들어져 있으므로 새 열 수를 쓰려면 app_style 에 먼저 추가한다."""
    widths = A.T4 if kind == "t4" else A.T6
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
    return '<div class="lines" style="flex:%g">%s</div>' % (flex, A.lines_svg())


def body(*parts):
    return '<div class="body">%s</div>' % "".join(parts)


# --------------------------------------------------------- 핵심 페이지들
def p_syllabus():
    """이 상품의 핵심 셀링 포인트. 강의계획서 한 장을 세 종류로 분해한다.

    쓰기 시작하는 문턱을 낮추려고 과목/교수 같은 머리 정보를 먼저 받고,
    그 다음에 표 세 개로 나눈다. 한 표에 다 넣으면 옮겨 적기를 포기한다.
    """
    return (bp.head("Work", "Syllabus unpack",
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
                         check_last=True), flex="1")))


def p_assignments():
    return (bp.head("Work", "Assignment tracker",
                    "Everything with a deadline, in one place")
            + body(card("This term",
                        tbl("t4", ["ASSIGNMENT", "CLASS", "DUE", "DONE"], 12,
                            check_last=True), flex="1")))


def p_group_project():
    return (bp.head("Work", "Group project",
                    "The part that goes wrong is who was doing what")
            + body(
                card("The project", field(24)),
                card("Who does what, by when",
                     tbl("t4", ["PIECE", "WHO", "BY WHEN", "DONE"], 7,
                         check_last=True)),
                card("My part &mdash; in my own words", fill(), flex="1")))


def p_exam():
    """범위를 쪼개고 날짜에 배분한다. '공부하기'는 과제가 아니다."""
    return (bp.head("Study", "Exam study plan",
                    "Split the scope first. Then give each piece a day.")
            + body(
                card("Exam", field(24)),
                card("The scope, in pieces",
                     tbl("t4", ["PIECE", "SOURCE", "DAY", "DONE"], 8,
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
                card("Summary &mdash; three lines, in your own words",
                     '<div class="lines" style="height:%gpt">%s</div>'
                     % (4 * A.ROW_H, A.lines_svg()))))


def p_grades():
    return (bp.head("Study", "Grade tracker",
                    "What each piece is worth, and what you got")
            + body(
                card("Class", field(24)),
                card("Pieces",
                     tbl("t4", ["PIECE", "WEIGHT", "SCORE", "DONE"], 10,
                         check_last=True), flex="1"),
                card("Where I stand", field(36))))


def p_reading():
    return (bp.head("Study", "Reading log", "To read, and read")
            + body(card("Readings",
                        tbl("t4", ["READING", "CLASS", "BY", "READ"], 12,
                            check_last=True), flex="1")))


def p_session():
    return (bp.head("Study", "Study session log",
                    "Notice when it works, and do that again")
            + body(card("Sessions",
                        tbl("t4", ["WHAT I STUDIED", "WHERE", "HOW LONG",
                                   "IT WORKED"], 11, check_last=True),
                        flex="1")))


def p_office():
    return (bp.head("Study", "Office hours",
                    "Write the question down when you have it, not later")
            + body(
                card("Who, and when", field(24)),
                card("What I want to ask", fill(), flex="1"),
                card("What they said", fill(), flex="1")))


def p_timetable():
    days = ["MON", "TUE", "WED", "THU", "FRI"]
    hours = ["08", "09", "10", "11", "12", "13", "14", "15", "16", "17"]
    widths = A.T6
    hd = ('<tr><td style="width:%.2fpt"></td>' % widths[0]
          + "".join('<td style="width:%.2fpt">%s</td>' % (widths[i + 1], d)
                    for i, d in enumerate(days)) + "</tr>")
    rows = "".join("<tr><td>%s</td>%s</tr>" % (h, "<td></td>" * len(days))
                   for h in hours)
    return (bp.head("Classes", "Class schedule",
                    "Write it once, in week one")
            + body('<div class="tbwrap"><table class="tb t6">%s%s</table>%s'
                   '</div>' % (hd, rows, A.rules_svg(widths, len(hours), head_h=24.0))))


def p_contacts():
    return (bp.head("Classes", "Who to ask",
                    "The name you will need at 11pm the night before")
            + body(card("Professors &amp; TAs",
                        tbl("t4", ["NAME", "CLASS", "OFFICE HOURS", "ASKED"],
                            10, check_last=True), flex="1")))


def p_class(n):
    """과목별 페이지. 한 과목의 모든 것이 한 장에 있어야 찾으러 가지 않는다."""
    return (bp.head("Classes", "Class %d" % n,
                    "Everything about one class, on one page")
            + body(
                card("Class", field(24)),
                '<div class="row" style="gap:14pt">'
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
                                   "DONE"], 8, check_last=True), flex="1")))


def p_term(n):
    """학기 개요 한 장. 16주를 한 장에 놓고, 무거운 주를 미리 본다."""
    rows = "".join(
        '<tr><td>Week %d</td><td></td><td></td><td class="bx"><i></i></td></tr>'
        % w for w in range(1, WEEKS_PER_TERM + 1))
    widths = A.T4
    hd = "".join('<td style="width:%.2fpt">%s</td>' % (w, c)
                 for w, c in zip(widths, ["WEEK", "WHAT IS DUE", "EXAMS",
                                          "CLEAR"]))
    return (bp.head("Semester", "Term %d" % n,
                    "Sixteen weeks. Fill in the heavy ones first.")
            + body('<div class="tbwrap"><table class="tb t4"><tr>%s</tr>%s'
                   '</table>%s</div>'
                   % (hd, rows, A.rules_svg(widths, WEEKS_PER_TERM, head_h=24.0))))


def p_week(n):
    return (bp.head("Week", "Week %d" % n, "What has to happen this week")
            + body(
                card("Due this week",
                     tbl("t4", ["WHAT", "CLASS", "DAY", "DONE"], 6,
                         check_last=True)),
                card("Reading", fill(), flex="1"),
                card("One thing I will not drop", field(36))))


def p_day(n):
    return (bp.head("Day", "Day %d" % n, "One thing. Then the rest.")
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
                '<div class="row" style="gap:14pt">'
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
                    "Name it and it gets smaller")
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
                    "Start at the deadline and walk back")
            + body(
                card("Due", field(24)),
                card("Steps, in reverse",
                     tbl("t4", ["STEP", "NEEDS", "BY WHEN", "DONE"], 8,
                         check_last=True), flex="1"),
                card("So I start on", field(36))))


def p_estimate():
    return (bp.head("Work", "Guess vs actual",
                    "You are not bad at this. You just have no data yet.")
            + body(card("Tasks",
                        tbl("t4", ["TASK", "I GUESSED", "IT TOOK", "DONE"],
                            11, check_last=True), flex="1")))


def p_obstacle():
    return (bp.head("Work", "Obstacle plan",
                    "Decide now what you will do when it goes wrong")
            + body(
                card("The plan", field(36)),
                card("What will get in the way",
                     tbl("t4", ["OBSTACLE", "WHEN", "WHAT I WILL DO",
                                "READY"], 6, check_last=True)),
                card("If it all falls apart", fill(), flex="1")))


def p_goals():
    return (bp.head("Semester", "Term goals",
                    "Three is plenty. Make them checkable.")
            + body(
                card("This term",
                     tbl("t4", ["GOAL", "HOW I WILL KNOW", "BY WHEN", "DONE"],
                         5, check_last=True)),
                card("Why these", fill(), flex="1")))


def p_term_review():
    return (bp.head("Semester", "Term review", "Five minutes, once a term")
            + body(
                card("What actually happened", fill(), flex="1"),
                card("What I will do differently", fill(), flex="1"),
                card("What worked &mdash; keep it", field(36))))


def p_meds():
    return (bp.head("Life", "Medication log", "What you took, and when")
            + body(card("This month",
                        tbl("t4", ["DAY", "WHAT", "TIME", "TAKEN"], 12,
                            check_last=True), flex="1")))


def p_sleep():
    return (bp.head("Life", "Sleep log", "Hours in bed, hours asleep")
            + body(card("This month",
                        tbl("t4", ["DAY", "IN BED", "ASLEEP", "OK"], 12,
                            check_last=True), flex="1")))


def p_mood():
    return (bp.head("Life", "Mood", "How the week actually felt")
            + body(
                card("This week",
                     tbl("t4", ["DAY", "HOW IT FELT", "WHAT HAPPENED", "OK"],
                         7, check_last=True)),
                card("Anything else", fill(), flex="1")))


def p_notes():
    return (bp.head("Notes", "Blank space")
            + body(card("", fill(), flex="1")))


# --------------------------------------------------- 반복 페이지의 목차
CHIP = ("display:flex;align-items:center;justify-content:center;"
        "height:19pt;border-radius:7pt;text-decoration:none;"
        "background:rgba(255,255,255,.55);box-shadow:0 1pt 5pt rgba(40,28,90,.12);"
        "font-size:7.5pt;font-weight:700;color:#2B2540")


def chip_index(eyebrow, title, sub, prefix, per_term, cols):
    """학기별로 묶은 칩 격자. 링크가 없는 목차는 목차가 아니다 --
    Chrome 은 목적지 없는 <a href="#x"> 를 조용히 버린다."""
    blocks = []
    for t in range(1, TERMS + 1):
        chips = "".join(
            '<a href="#%s%d" style="%s">%d</a>'
            % (prefix, (t - 1) * per_term + i, CHIP, i)
            for i in range(1, per_term + 1))
        blocks.append(
            '<div style="margin-bottom:11pt">'
            '<div style="font-size:6.6pt;letter-spacing:.14em;font-weight:800;'
            'color:#4A4260;margin-bottom:5pt">TERM %d</div>'
            '<div style="display:grid;grid-template-columns:repeat(%d,1fr);'
            'gap:5pt">%s</div></div>' % (t, cols, chips))
    return (bp.head(eyebrow, title, sub)
            + body('<div class="card" style="flex:1">%s</div>'
                   % "".join(blocks)))


def p_week_index():
    return chip_index("Jump to", "Weeks",
                      "Sixteen weeks a term, eight terms", "w",
                      WEEKS_PER_TERM, 16)


def p_day_index():
    return chip_index("Jump to", "Days",
                      "Thirty-one a term. Use them on the days you need.",
                      "d", DAYS_PER_TERM, 31)


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


def chip_row(label, prefix, n, cols):
    """t1..t8 / c1..c8 처럼 탭 목차에서 링크가 없던 페이지들로 가는 칩.
    링크가 하나도 없으면 스크롤 말고는 갈 방법이 없다 -- 검사기가
    '도달 불가 페이지'로 잡는 항목이다."""
    chips = "".join('<a href="#%s%d" style="%s">%d</a>' % (prefix, i, CHIP, i)
                    for i in range(1, n + 1))
    return ('<div class="card" style="flex:none"><div class="label">%s</div>'
            '<div style="display:grid;grid-template-columns:repeat(%d,1fr);'
            'gap:6pt">%s</div></div>' % (label, cols, chips))


# -------------------------------------------------------------- 페이지 목록
def specs():
    """(키, 본문 만드는 함수) 목록. 순서가 PDF 페이지 순서다."""
    s = [("cover", bp.p_cover), ("index", bp.p_index)]

    def group(key, title, sub, chips=""):
        s.append((key, (lambda k=key, t=title, u=sub, c=chips:
                        lambda: group_page(k, t, u, c))()))

    group("semester", "Semester", "Eight terms, sixteen weeks each",
          chip_row("Term overview", "t", TERMS, TERMS))
    s += [("terms", p_terms), ("goals", p_goals),
          ("term-review", p_term_review)]
    for n in range(1, TERMS + 1):
        s.append(("t%d" % n, (lambda i: lambda: p_term(i))(n)))

    s.append(("week", p_week_index))
    for n in range(1, WEEKS_PER_TERM * TERMS + 1):
        s.append(("w%d" % n, (lambda i: lambda: p_week(i))(n)))

    s.append(("day", p_day_index))
    for n in range(1, DAYS_PER_TERM * TERMS + 1):
        s.append(("d%d" % n, (lambda i: lambda: p_day(i))(n)))

    group("classes", "Classes", "Timetable, and one page per class",
          chip_row("One page per class", "c", CLASSES, CLASSES))
    s += [("timetable", p_timetable), ("contacts", p_contacts)]
    for n in range(1, CLASSES + 1):
        s.append(("c%d" % n, (lambda i: lambda: p_class(i))(n)))

    group("work", "Work", "Syllabus, assignments, group projects")
    s += [("syllabus", p_syllabus), ("assignments", p_assignments),
          ("backwards", p_backwards), ("group", p_group_project),
          ("estimate", p_estimate), ("obstacle", p_obstacle)]

    group("study", "Study", "Exams, lecture notes, grades")
    s += [("exam", p_exam), ("cornell", p_cornell), ("reading", p_reading),
          ("grades", p_grades), ("session", p_session), ("office", p_office)]

    group("focus", "Focus", "For when starting is the hard part")
    s += [("braindump", p_braindump), ("focus-session", p_focus_session),
          ("deciding", p_deciding), ("avoiding", p_avoiding),
          ("energy", p_energy)]

    group("life", "Life", "The admin that eats the week")
    s += [("meds", p_meds), ("sleep", p_sleep), ("mood", p_mood)]

    s.append(("notes", p_notes))
    return s


# 반복 페이지가 어느 탭을 켜는가. 하나라도 빠지면 그 페이지에서 레일이
# 통째로 꺼져 "앱에서 튕겨나온" 느낌이 된다.
REPEAT_TAB = [("t", "semester"), ("w", "week"), ("d", "day"), ("c", "classes")]
