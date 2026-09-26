# -*- coding: utf-8 -*-
"""상품 3 직접 써 보기 (PROCESS.md 6단계) -- 완성 PDF 에서 구매자처럼 링크를 눌러 따라간다. Prod 3 방 소유.

    python scripts/p3/dogfood_p3.py v0.15 [2027 mon]

글자가 적힌 링크를 "누르고"(그 링크 상자 안의 글자로 고른다) 도착한 페이지가 기대한 곳인지 본다.
넘기기(스와이프)는 다음 쪽으로 가며 켜진 탭을 읽는다. 막힌 곳은 쪽 번호로 찍는다.
"""
import re
import sys
import pathlib
import pymupdf

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[2]
VER = sys.argv[1] if len(sys.argv) > 1 else "v0.15"
Y, WS = (sys.argv[2], sys.argv[3]) if len(sys.argv) > 3 else ("2027", "mon")
name = f"ADHD-Year-Planner-{Y}-{WS}"
html = (ROOT / "src/prod3/planner" / VER / f"{name}.html").read_text(encoding="utf-8")
ids = re.findall(r'<section class="pg" id="([^"]+)"', html)
on = [(re.findall(r'<a href="#([^"]+)" class="on"', m.group(0)) or [None])[0]
      for m in re.finditer(r'<section class="pg" id="[^"]+".*?</nav>', html, re.S)]
doc = pymupdf.open(ROOT / "output/prod3/planner" / VER / f"{name}.pdf")
fails = []


def links(p):
    """쪽 p(0부터)의 링크 [(글자, 도착 쪽)]"""
    pg = doc[p]
    words = pg.get_text("words")
    out = []
    for l in pg.get_links():
        if "page" not in l or l["page"] < 0:
            continue
        r = l["from"]
        # 글자 한가운데가 링크 상자 안에 있을 때만 -- 누르는 영역을 넓혀 두어서 옆 알약 글자가 걸린다
        t = " ".join(w[4] for w in words if r.contains(pymupdf.Point((w[0] + w[2]) / 2, (w[1] + w[3]) / 2)))
        out.append((t, l["page"]))
    return out


def tap(p, label):
    """글자가 정확히 같은 링크 > 정규식(re:) > 글자를 포함하는 링크 중 가장 짧은 것"""
    ls = links(p)
    if label.startswith("re:"):
        return next((d for t, d in ls if re.search(label[3:], t, re.I)), None)
    exact = [d for t, d in ls if t.strip().lower() == label.lower()]
    if exact:
        return exact[0]
    part = sorted(((len(t), d) for t, d in ls if label.lower() in t.lower()))
    return part[0][1] if part else None


def step(journey, p, label, expect):
    d = tap(p, label)
    got = ids[d] if d is not None else None
    ok = got is not None and (re.fullmatch(expect, got) is not None)
    print(f"  {'OK  ' if ok else 'FAIL'} p{p + 1} {ids[p]} --[{label}]--> " + (f"p{d + 1} {got}" if d is not None else "링크 없음"))
    if not ok:
        fails.append(f"{journey}: p{p + 1} [{label}] 기대 {expect}, 실제 {got}")
    return d if d is not None else p


P = lambda k: ids.index(k)

print("1. 처음 연 사람: 표지 -> 넘기기 -> 사용법 -> 목차 -> 도구")
for i in range(0, 5):
    print(f"  p{i + 1} {ids[i]:<8} 켜진 탭: {on[i]}")
if on[0] is not None or on[1] != "index" or on[2] != "index" or on[3] != "sos" or on[4] != "year":
    fails.append("1: 앞 5쪽 탭 표시가 표지(없음)/INDEX/INDEX/SOS/YEAR 가 아니다")
p = step("1", P("index"), "Focus tools", r"focus")
p = step("1", p, "Brain dump", r"braindump")
for lab, exp in (("Kickoff", "kickoff"), ("Year in pixels", "pixels"), ("Q3", "q3"), ("Vision", "vision")):
    step("1 목차 알약", P("index"), lab, exp)

print("2. 오늘 쓰기: YEAR -> 날짜 -> 일간 -> Tomorrow -> 30일 뒤 메모")
p = step("2", 1, "Year", r"year")
# 미니 달력에서 3월 15일: 링크 글자가 "15" 인 것이 12개라 도착 id 로 고른다
d = next((dest for t, dest in links(P("year")) if ids[dest] == "d3-15"), None)
print(f"  {'OK  ' if d is not None else 'FAIL'} Year at a glance -> 3월 15일 " + (f"p{d + 1}" if d is not None else ""))
if d is None:
    fails.append("2: Year at a glance 에 3/15 링크 없음")
else:
    p = step("2", d, "Tomorrow", r"d3-16")
    p = step("2", p, "From yesterday", r"d3-15")
    step("2", p, "Arrives", r"d4-14")

print("3. 한 주·한 달: 주간 -> 월 계획 -> 월 리뷰 -> 연 합계")
p = step("3", P("d3-15"), r"re:^week \d+", r"w\d+")
step("3", P("m3"), "Plan", r"mp3")
step("3", P("mp3"), "Birthdays", r"bday1")
step("3", P("mp3"), "Admin radar", r"admin")
step("3", P("m3"), "Review", r"mr3")
step("3", P("mr3"), "ADHD tax", r"yearreview")
step("3", P("q1"), "W1", r"w1")

print("4. 막혔을 때: SOS -> 상황 -> 도구 -> 탭으로 돌아오기")
p = step("4", 30, "SOS", r"sos")
p = step("4", p, "can't start", r"tasks")
step("4", p, "Month", r"month")

print("5. 넘기기만: 탭이 순서대로 흐르나")
order = ["index", "sos", "year", "month", "week", "focus", "feel", "health", "life", "notes"]
seq = []
for k, t in zip(ids[1:], on[1:]):
    if k in ("playbook", "mailbox", "yearreview"):
        continue
    if t and (not seq or seq[-1] != t):
        seq.append(t)
ok = seq == order
print(f"  {'OK  ' if ok else 'FAIL'} {' > '.join(seq)}")
if not ok:
    fails.append(f"5: 넘길 때 탭 순서 {seq}")

print("6. 연말: 12월 31일 -> Year review / 12월 메모 -> Mailbox")
step("6", P("d12-31"), "Year review", r"yearreview")
step("6", P("d12-10"), "mailbox", r"mailbox")
step("6", P("playbook"), "52 experiments", r"experiments")

print(f"\n{'ALL OK' if not fails else 'FAILURES ' + str(len(fails))}")
for f in fails:
    print("  - " + f)
sys.exit(1 if fails else 0)
