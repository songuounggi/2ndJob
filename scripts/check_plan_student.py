# -*- coding: utf-8 -*-
"""상품 2 — 5-1 기획서 대조 (`PROCESS.md` 검수 절차서).

    python scripts/check_plan_student.py [버전]      # 기본 student-v1.1

`product2-content.md` 의 페이지 지도와 빌드 결과를 맞춘다. 기획한 것을
만들었는지, 페이지가 다 있는지, 칸과 링크가 지도대로인지 본다.

**상품 2 는 기획서 없이 출시했다.** 그래서 이 검사는 두 층이다:

  [기획]  만들기 전에 product2-student.md 에 적혀 있던 것.
          구성안 24종 · 고통 5가지 대응 · 반복 세트 규모.
          어긋나면 결함이다
  [지도]  v1.1 실물에서 읽어 적은 기준선. 지금은 자명하게 통과하지만
          **앞으로의 변경**을 잡는다

빌드 HTML 을 읽는다(PDF 가 아니라) -- 5-1 은 "무엇을 만들었나" 이고
링크가 실제로 PDF 에 살아남았는지는 5-3 `verify_student.py` 가 본다.
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = sys.argv[1] if len(sys.argv) > 1 else "student-v1.1"
SRC = os.path.join(ROOT, "src", "planner_%s.html" % VERSION)

# ---------------------------------------------------------------- [기획]
# product2-student.md "구성안" — 만들기 전에 정한 24종.
# (기획서의 이름, 실물 id 또는 접두사)
PLANNED_NEW = [
    ("Syllabus unpack", "s"), ("Semester at a glance", "t"),
    ("Class schedule", "h"), ("Per-class page", "c"),
    ("Assignment tracker", "a"), ("Exam study plan", "e"),
    ("Lecture notes", "cornell"), ("Reading log", "reading"),
    ("Group project", "group"), ("Questions for office hours", "office"),
    ("Grade tracker", "g"), ("Study session log", "session"),
]
PLANNED_REUSE = [
    ("Brain dump", "braindump"), ("Focus session", "focus-session"),
    ("Obstacle plan", "obstacle"), ("Stuck on deciding", "deciding"),
    ("Why I am avoiding it", "avoiding"), ("Guess vs actual", "estimate"),
    ("Working backwards", "backwards"), ("Energy budget", "energy"),
    ("Medication log", "meds"), ("Sleep", "sleep"), ("Mood", "mood"),
    ("Notes (dot grid)", "n"),
]
# 타겟의 고통 다섯 -- 이 대응이 끊기면 상품의 근거가 사라진다
PAIN = [("1 강의계획서를 옮겨 적지 않는다", "s"),
        ("2 마감을 역산하지 못한다", "backwards"),
        ("3 시험 범위를 쪼개지 못한다", "e"),
        ("4 조별과제에서 내 몫이 흐려진다", "group"),
        ("5 걸릴 시간을 과소평가한다", "estimate")]

# ---------------------------------------------------------------- [지도]
PAGES = 437
REPEATS = {"t": 8, "o": 8, "r": 8, "w": 128, "d": 112, "h": 8, "k": 8,
           "c": 40, "s": 40, "a": 8, "e": 24, "g": 8, "n": 9}
UNIQUE = ["cover", "index", "semester", "terms", "week", "day", "classes",
          "work", "backwards", "group", "estimate", "obstacle", "study",
          "cornell", "reading", "session", "office", "focus", "braindump",
          "focus-session", "deciding", "avoiding", "energy", "life",
          "meds", "sleep", "mood", "notes"]
HUBS = ["semester", "week", "day", "classes", "work", "study", "focus",
        "life", "notes"]
# 표 머리글 -- 칸이 바뀌면 그 페이지의 용도가 바뀐 것이다
COLUMNS = {
    "s1": [["WHAT", "TYPE", "DUE", "DONE"],
           ["WHAT", "COVERS", "DATE", "DONE"],
           ["READING", "FOR WEEK", "PAGES", "DONE"]],
    "a1": [["ASSIGNMENT", "CLASS", "DUE", "DONE"]],
    "e1": [["PIECE", "SOURCE", "DAY", "DONE"]],
    "g1": [["PIECE", "WEIGHT", "SCORE", "DONE"]],
    "c1": [["PIECE", "WEIGHT", "DUE", "DONE"]],
    "h1": [["MON", "TUE", "WED", "THU", "FRI"]],
    "t1": [["WEEK", "WHAT IS DUE", "EXAMS", "DONE"]],
    "d1": [["ASSIGNMENT", "CLASS", "DUE", "DONE"]],
    "w1": [["WHAT", "CLASS", "DAY", "DONE"]],
    "estimate": [["TASK", "I GUESSED", "IT TOOK", "DONE"]],
    "backwards": [["STEP", "NEEDS", "BY WHEN", "DONE"]],
    "group": [["PIECE", "WHO", "BY WHEN", "DONE"]],
}

fails = []
oks = []


def check(tag, name, ok, detail=""):
    (oks if ok else fails).append((tag, name, detail))


def main():
    if not os.path.exists(SRC):
        raise SystemExit("빌드 HTML 이 없다: %s\n"
                         "  PLANNER_VERSION=%s python scripts/build_planner.py"
                         % (SRC, VERSION))
    h = io.open(SRC, encoding="utf-8").read()
    ids = re.findall(r'<section class="page[^"]*" id="([^"]+)"', h)
    idset = set(ids)
    rep = {}
    for k in ids:
        m = re.fullmatch(r"([a-z])(\d+)", k)
        if m:
            rep[m.group(1)] = rep.get(m.group(1), 0) + 1

    def exists(target):
        return target in idset or rep.get(target, 0) > 0

    def count(target):
        return rep.get(target, 1 if target in idset else 0)

    # ---- [기획] ----
    for nm, t in PLANNED_NEW:
        check("기획", "새로 만들 것 · %s" % nm, exists(t),
              "id/접두사 '%s' 없음" % t)
    for nm, t in PLANNED_REUSE:
        check("기획", "v8 재사용 · %s" % nm, exists(t),
              "id/접두사 '%s' 없음" % t)
    for nm, t in PAIN:
        check("기획", "고통 대응 · %s" % nm, exists(t),
              "대응 페이지('%s')가 없다" % t)

    # ---- [지도] ----
    check("지도", "총 쪽 수", len(ids) == PAGES,
          "%d (기준 %d)" % (len(ids), PAGES))
    for pre, n in sorted(REPEATS.items()):
        check("지도", "반복 %s × %d" % (pre, n), rep.get(pre, 0) == n,
              "%d 장" % rep.get(pre, 0))
    for k in UNIQUE:
        check("지도", "고유 페이지 %s" % k, k in idset, "없음")

    # 목차: 9개 탭 전부로 가고, 자기 페이지로 가는 링크가 없어야 한다
    m = re.search(r'id="index".*?(?=<section class="page|</body>)', h, re.S)
    crow = re.findall(r'<a class="crow" href="#([^"]+)"', m.group(0) if m else "")
    check("지도", "목차가 9개 탭 전부로", sorted(crow) == sorted(HUBS),
          "간 곳: %s" % (crow or "없음"))
    check("지도", "목차에 자기 페이지 링크 없음", "index" not in crow,
          "href=#index 가 %d개" % crow.count("index"))

    # 표 머리글
    parts = re.split(r'(?=<section class="page)', h)
    got = {}
    for p in parts:
        mm = re.match(r'<section class="page[^"]*" id="([^"]+)"', p)
        if not mm or mm.group(1) not in COLUMNS:
            continue
        body = p.split("</nav>")[-1]
        cols = []
        for tb in re.findall(r"<table class=\"tb [^\"]+\">(.*?)</table>",
                             body, re.S):
            hdr = [x.strip() for x in
                   re.findall(r"<td[^>]*>([A-Z][A-Z ]*)</td>", tb[:900])
                   if x.strip()]
            if hdr:
                cols.append(hdr)
        got[mm.group(1)] = cols
    for k, want in COLUMNS.items():
        have = got.get(k, [])
        check("지도", "표 머리글 %s" % k, have == want,
              "실제 %s" % (have or "표 없음"))

    # ---- 출력 ----
    print()
    print("  5-1 기획서 대조 — %s" % VERSION)
    print("  %s" % ("-" * 62))
    for tag, name, detail in fails:
        print("  실패  [%s] %-40s %s" % (tag, name, detail))
    n_plan = sum(1 for t, _, _ in oks if t == "기획")
    n_map = sum(1 for t, _, _ in oks if t == "지도")
    print("  OK    [기획] %d항목 · [지도] %d항목" % (n_plan, n_map))
    print()
    print("  통과 %d / 실패 %d" % (len(oks), len(fails)))
    print("  기준 문서: product2-content.md")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
