# -*- coding: utf-8 -*-
"""상품 3 기획서 대조 -- 만든 플래너가 product3-content.md 2절(페이지 지도)대로인가. Prod 3 방 소유.

    python scripts/p3/check_plan_p3.py v0.14 [2027 mon]

2026-09-26 사용자: "몇 시간 검수를 하면서 기획서 대조는 안 했다." 그때까지 검사는 전부 "제대로 만들어졌나"였고
"기획한 것을 만들었나"는 없었다. 이 검사가 그 칸이다. 기획서를 고치면 PLAN 을 같이 고친다.
사용자 결정으로 기획과 달라진 것은 DECIDED 에, 아직 결정 대기인 것은 PENDING 에 적는다(FAIL 로 세지 않고 목록으로 보인다).
"""
import re
import sys
import pathlib

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[2]
VER = sys.argv[1] if len(sys.argv) > 1 else "v0.14"
Y, WS = (sys.argv[2], sys.argv[3]) if len(sys.argv) > 3 else ("2027", "mon")
html = (ROOT / "src/prod3/planner" / VER / f"ADHD-Year-Planner-{Y}-{WS}.html").read_text(encoding="utf-8")
secs = {m.group(1): m.group(0) for m in re.finditer(r'<section class="pg" id="([^"]+)".*?(?=<section class="pg"|</body>)', html, re.S)}
ids = list(secs)
body = {k: re.sub(r'<nav class="rail">.*?</nav>', "", v, flags=re.S) for k, v in secs.items()}
links = {k: re.findall(r'href="#([^"]+)"', v) for k, v in body.items()}
text = {k: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", v)).upper() for k, v in body.items()}
fails, pend = [], []


def ok(c, msg):
    print(("  OK   " if c else "  FAIL ") + msg)
    if not c:
        fails.append(msg)


def pno(k):
    return ids.index(k) + 1


# ---- 2절 순서 (구역 단위) -------------------------------------------------
PLAN_FRONT = ["cover", "how", "index", "sos", "year", "kickoff", "experiments", "pixels", "admin", "myhol", "bday1", "bday2", "where"]
ok(ids[:len(PLAN_FRONT)] == PLAN_FRONT, f"2-1 앞부분 순서 {PLAN_FRONT[:5]}... (실제 {ids[:6]})")
q = [pno(f"q{i}") for i in range(1, 5)]
ok(q == sorted(q) and q[-1] < pno("month") < pno("m1"), f"2-2 분기 4장이 월보다 앞 (p{q[0]}-{q[-1]}, 월 목차 p{pno('month')})")
ok(all(pno(f"m{m}") < pno(f"mp{m}") < pno(f"bw{m}") < pno(f"mr{m}") for m in range(1, 13)), "2-3 매달 달력 > 계획 > Brain weather > 리뷰")
ok(pno("mr12") < pno("week") < pno("w1") and pno("wr53" if "wr53" in ids else "wr52") < pno("playbook"), "2-4 주간은 월 뒤, 2-6 연말은 주간 뒤")
ok(pno("playbook") < pno("mailbox") < pno("yearreview") < pno("focus"), "2-6 연말 Playbook > Mailbox > Year review, 그 뒤 도구함")
ok(pno("focus") < pno("feel") < pno("health") < pno("life") < pno("notes"), "2-7 도구함 Focus > Feel > Body > Life > Notes")

# ---- 탭 표시 --------------------------------------------------------------
on = {k: (re.findall(r'<a href="#([^"]+)" class="on"', re.search(r"<nav.*?</nav>", v, re.S).group(0)) or [None])[0] for k, v in secs.items()}
ok(on["cover"] is None, "표지는 탭을 켜지 않는다 (사용자 2026-09-26)")
ok(on["how"] == "index" and on["index"] == "index" and on["sos"] == "sos", "How·목차 = INDEX, SOS = SOS")

# ---- 2절 내용·링크 --------------------------------------------------------
ok(len([l for l in links["sos"] if l in secs]) >= 14, f"SOS 상황 14개가 도구로 연결 ({len(links['sos'])})")
ok(len({l for l in links["experiments"] if re.fullmatch(r"w\d+", l)}) >= 52, "52 experiments 목록이 주마다 링크")
ok(all(any(re.fullmatch(r"w\d+", l) for l in links[f"q{i}"]) and "KEEP" in text[f"q{i}"] and "DROP" in text[f"q{i}"] for i in range(1, 5)),
   "분기: Keep·Drop + 주 링크")
ok(all("bday1" in links[f"mp{m}"] or "bday2" in links[f"mp{m}"] for m in range(1, 13)), "월 계획: 생일 -> Birthdays & gift radar")
ok(all("admin" in links[f"mp{m}"] for m in range(1, 13)), "월 계획: Admin radar -> Life admin radar")
ok(all("yearreview" in links[f"mr{m}"] for m in range(1, 13)), "월 리뷰: ADHD tax -> Year review 연 합계")
ok(all(all(f"mr{m}" in links["yearreview"] for m in range(1, 13)) for _ in [0]), "Year review: 달별 ADHD tax -> 월 리뷰")
days = [k for k in ids if re.fullmatch(r"d\d+-\d+", k)]
ok(all("DAY " in text[d] and " LEFT" in text[d] for d in days), "2-5 일간: Day n · m left")
ok(all("BATTERY" in text[d] and "NOT TODAY" in text[d] and "GUESS VS ACTUAL" in text[d] for d in days), "2-5 일간: Battery · Not today · Guess vs actual")
ok(all("THIS WEEK" in text[w] for w in ids if re.fullmatch(r"w\d+", w) and int(w[1:]) <= 52), "2-4 주간: 이번 주 실험 카드 (53주차는 BONUS WEEK)")
ok("mailbox" in {l for d in days if d.startswith("d12-") for l in links[d]}, "12월 메모 -> Year-end mailbox")

# ---- 들어오는 링크 없는 페이지 (넘겨서만 닿는 곳) ----------------------------
inc = {k: 0 for k in ids}
for k, ls in links.items():
    for l in set(ls):
        if l in inc and l != k:
            inc[l] += 1
TABS = {"index", "sos", "year", "month", "week", "focus", "feel", "health", "life", "notes"}
orph = [k for k in ids if inc[k] == 0 and k not in TABS and k != "cover"]
PENDING_ORPH = {"kickoff", "pixels", "myhol", "where", "project", "vision", "q1", "q2", "q3", "q4"}   # 목차 배치 결정 대기(사용자)
new_orph = [k for k in orph if k not in PENDING_ORPH]
ok(not new_orph, f"링크로 닿지 않는 페이지 (결정 대기 제외) {[(pno(k), k) for k in new_orph]}")
if orph:
    pend.append(f"목차에서 갈 수 없는 페이지 {len(orph)}장 -- 목차 배치 결정 대기: {[(pno(k), k) for k in orph]}")

# ---- 결정 대기 (FAIL 아님, 목록으로) -----------------------------------------
PENDING = ["일간 Guess vs actual 2줄(기획) / 지금 1줄", "일간 Schedule buffer 칸(기획) / 지금 안내 글자", "Kickoff '3월에도 쓰고 있을 것' 칸",
           "Doom pile 15분 타이머 칸", "Playbook: ✓ 실험 표 + 주 링크(기획) / 지금 빈 W__ 줄"]
pend += PENDING
print("\n결정 대기 (사용자):")
for p in pend:
    print("  - " + p)
print(f"\n{'ALL OK' if not fails else f'FAILURES {len(fails)}'}")
sys.exit(1 if fails else 0)
