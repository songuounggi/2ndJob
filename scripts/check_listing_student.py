# -*- coding: utf-8 -*-
"""상품 2 리스팅 원고(product2-listing.md) 검사. 원고의 숫자가 파일과 맞는가.

    python scripts/check_listing_student.py student-v0.9 [원고 경로]

2026-09-24: 목업 문구에서 "33 templates", "every page is one tap away",
"4,700 links", "248 day pages", "or print" 이 전부 실제와 달랐다. 페이지를
늘리거나 줄일 때마다 원고 숫자가 조용히 틀어진다 -- 파일에서 다시 재서 대조한다.
"""
import io
import os
import re
import sys
from collections import deque

from pypdf import PdfReader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = sys.argv[1] if len(sys.argv) > 1 else "student-v0.9"
DOC = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "product2-listing.md")
sys.stdout.reconfigure(encoding="utf-8")

md = io.open(DOC, encoding="utf-8").read()
blocks = re.findall(r"```\n(.*?)```", md, re.S)
title, tags, desc = blocks[0].strip(), blocks[1].split(), blocks[2]
tags = [t for t in blocks[1].splitlines() if t.strip()]

# ------------------------------------------------------------- 파일에서 잰 값
h = io.open(os.path.join(ROOT, "src", "planner_%s.html" % VERSION), encoding="utf-8").read()
ids = re.findall(r'<section class="page[^"]*" id="([^"]+)"', h)
sec = dict(re.findall(r'<section class="page[^"]*" id="([^"]+)"(.*?)</section>', h, re.S))
r = PdfReader(os.path.join(ROOT, "output", "planner_%s-FINAL.pdf" % VERSION))
nd = r.named_destinations
idx = {id(p.indirect_reference.get_object()): n for n, p in enumerate(r.pages)}
G = [set() for _ in r.pages]
links = 0
for n, pg in enumerate(r.pages):
    for a in pg.get("/Annots") or []:
        d = a.get_object().get("/Dest")
        if d is not None:
            links += 1
            G[n].add(idx[id(nd[d]["/Page"].get_object())])
taps = 0
for s in range(1, len(G)):
    D, q = {s: 0}, deque([s])
    while q:
        u = q.popleft()
        for v in G[u]:
            if v not in D:
                D[v] = D[u] + 1
                q.append(v)
    taps = max(taps, max(D.values()))
NAV = {"cover", "index", "semester", "week", "day", "classes", "work",
       "study", "focus", "life", "notes"}
designs = set()
for p in ids:
    if p in NAV:
        continue
    k = re.sub(r"\d+$", "#", p)
    if k == "n#":
        k += re.search(r"<h1>([^<]+)</h1>", sec[p]).group(1)
    designs.add(k)
count = lambda pre: sum(1 for p in ids if re.fullmatch(pre + r"\d+", p))
terms = count("t")
tabs = len(re.findall(r'<a class="[^"]*" href="#', h.split("</nav>")[0]))
WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 8: "eight",
         9: "nine", 10: "ten", 14: "14", 16: "16"}

checks = []


def add(name, ok, got=""):
    checks.append((name, ok, got))


# ------------------------------------------------------------- Etsy 규칙
caps = [w for w in re.findall(r"[A-Za-z][A-Za-z&']*", title) if len(w) > 1 and w.isupper()]
add("제목 140자 이하", len(title) <= 140, len(title))
add("제목 대문자 단어 3개 이하", len(caps) <= 3, caps)
add("태그 13개", len(tags) == 13, len(tags))
add("태그 20자 이하", all(len(t) <= 20 for t in tags), [t for t in tags if len(t) > 20])
add("태그 중복 없음", len(set(tags)) == len(tags))
# "printed" (날짜가 인쇄돼 있지 않다)는 괜찮다 -- print / printable 단어만 잡는다
bad = [w for w in ("print", "printable", "cure", "treat", "heal", "symptom",
                   "diagnos", "one tap", "therapy for")
       if re.search(r"\b" + w + (r"\b" if w == "print" else ""), desc, re.I)]
add("금지·거짓 표현 없음 (print, cure, treat, one tap ...)", not bad, bad)
lines = desc.splitlines()
wrapped = [a for a, b in zip(lines, lines[1:])
           if a.strip() and b.strip() and not re.match(r"[•\d]|[A-Z' –0-9,]+$", b.strip())
           and not a.strip().endswith(":") and not re.match(r"[A-Z' –0-9,]+$", a.strip())]
add("문단 안 줄바꿈 없음", not wrapped, wrapped[:2])

# ------------------------------------------------------------- 숫자 대조
def has(pat, name, got):
    add(name, re.search(pat, desc, re.I) is not None, got)


has(r"\b%d PAGES\b" % len(ids), "페이지 수", len(ids))
has(r"\b%d PAGE DESIGNS\b" % len(designs), "페이지 디자인 수", len(designs))
m = re.search(r"over ([\d,]+) working links", desc, re.I)
lk = int(m.group(1).replace(",", "")) if m else -1
add("링크 수 (over N <= 실제)", 0 < lk <= links and links - lk < 100, (lk, links))
has(r"at most %s taps" % WORDS[taps], "최대 탭 수", taps)
has(r"\b%s tabs\b" % WORDS[tabs].capitalize(), "탭 수", tabs)
has(r"\b%s terms\b" % WORDS[terms].capitalize(), "학기 수", terms)
has(r"\b%d week pages and %d day pages\b" % (count("w") // terms, count("d") // terms),
    "학기당 위클리·데일리", (count("w") // terms, count("d") // terms))
has(r"\b%s class pages and %s syllabus pages\b"
    % (WORDS[count("c") // terms].capitalize(), WORDS[count("s") // terms]),
    "학기당 과목·강의계획서", (count("c") // terms, count("s") // terms))
has(r"\b%s exam study plans\b" % WORDS[count("e") // terms], "학기당 시험 계획", count("e") // terms)
has(r"\b%s note pages\b" % WORDS[count("n")], "노트 수", count("n"))
has(r"There are %s for every term" % WORDS[count("s") // terms], "학기당 Syllabus", count("s") // terms)

# ------------------------------------------------------------- 썸네일 이름
# 최종 검수(2026-09-24): 썸네일에 "Cornell notes", "Exam plans" 처럼 제품에
# 없는 이름이 있었다. 썸네일 카드 이름과 7번 하단 목록의 이름이 제품의 페이지
# 제목·라벨·목록 이름에 있어야 한다.
mock = io.open(os.path.join(ROOT, "scripts", "build_mockups_student.py"),
               encoding="utf-8").read()
names_in_product = set(re.findall(r"<h1>([^<]+)</h1>", h))
names_in_product |= set(re.findall(r'<div class="label">([^<]+)</div>', h))
names_in_product |= set(re.findall(
    r'<div style="font-size:10.5pt;font-weight:700">([^<]+)</div>', h))
names_in_product |= {n + "s" for n in names_in_product}      # 복수형 허용
cards = re.findall(r'\("[a-z0-9_]+", "([A-Z][^"]+)", "[^"]*"\)', mock)
foot = re.search(r'class="foot" style="font-size:38px">(.*?)</div>', mock, re.S)
foot_names = []
if foot:
    txt = re.sub(r"'\s*'", "", foot.group(1))
    foot_names = [x.strip() for x in re.split(r"&middot;|<br>", txt)]
unknown = sorted(set(n for n in cards + foot_names
                     if n and n not in names_in_product
                     and n not in ("Buy and download", "Open in your notes app",
                                   "Tap the side tabs", "Assignments",
                                   "Exams &amp; quizzes", "Reading")))
add("썸네일의 페이지 이름이 제품에 있음", not unknown, unknown)

fails = 0
for name, ok, got in checks:
    fails += not ok
    print(("  OK    " if ok else "  실패  ") + "%-40s %s" % (name, got))
print("\n실패:", fails)
sys.exit(1 if fails else 0)
