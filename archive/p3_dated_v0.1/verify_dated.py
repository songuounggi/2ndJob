# -*- coding: utf-8 -*-
"""상품 3 날짜형 플래너 구조 검사. 판 하나를 받는다.

    python scripts/verify_dated.py dated-v0.1-2027-sun

날짜는 dated_pages.py 를 import 하지 않고 여기서 따로 계산한다 -- 같은
코드로 만들고 같은 코드로 재면 틀린 것도 맞다고 나온다.

  1. 페이지 수 = 고정 템플릿(상품 1 v8.20 과 같은 키) + 12 + 날수 + 1 + 주수
  2. 죽은 링크: HTML href 와 PDF named destination 둘 다
  3. 빠진 링크: 모든 날 <- 그 달 달력·그 주 주간 / 모든 주 <- 주 목차·월 달력 /
     모든 달 <- 연간 / 모든 일간 -> 그 달·그 주 칩 / 표지 빼고 전 페이지가 어딘가에서 닿는다
  4. 날짜-요일: 일간 제목, 주간 칩 7개, 월 달력 칸의 열 위치
  5. 탭 하이라이트 정확히 1개 (표지 제외), 탭 링크 페이지당 10개
  6. 다른 해 숫자가 섞이지 않았는가 (2027 판에 2026 등)
"""
import calendar
import datetime as dt
import io
import os
import re
import sys
from pypdf import PdfReader

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VER = sys.argv[1] if len(sys.argv) > 1 else "dated-v0.1-2026-mon"
m_ = re.fullmatch(r"dated-v[\d.]+-(\d{4})-(mon|sun)", VER)
YEAR, WS = int(m_.group(1)), (0 if m_.group(2) == "mon" else 6)
HTML = os.path.join(ROOT, "src", f"planner_{VER}.html")
PDF = os.path.join(ROOT, "output", f"planner_{VER}-FINAL.pdf")
BASE = os.path.join(ROOT, "src", "planner_v8.20-undated.html")
# 검사기 자체 확인용: 다른 파일을 이 판이라 치고 잴 수 있다
#   python scripts/verify_dated.py dated-v0.1-2026-sun src/x.html output/x.pdf
if len(sys.argv) == 4:
    HTML, PDF = (os.path.join(ROOT, a) for a in sys.argv[2:])
ABBR = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

fails = []


def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  -- {detail}" if detail else ""))
    if not ok:
        fails.append(name)


# ---------------------------------------------------------- 기대값 계산 --
days = [dt.date(YEAR, 1, 1) + dt.timedelta(n)
        for n in range((dt.date(YEAR, 12, 31) - dt.date(YEAR, 1, 1)).days + 1)]
jan1 = days[0]
first = jan1 - dt.timedelta((jan1.weekday() - WS) % 7)
weeks = []
while first <= days[-1]:
    weeks.append(first)
    first += dt.timedelta(7)
week_of = {first + dt.timedelta(i): n + 1
           for n, first in enumerate(weeks) for i in range(7)}
dk = lambda d: f"d{d.month}-{d.day}"

h = io.open(HTML, encoding="utf-8").read()
sections = {m.group(1): m.group(0) for m in
            re.finditer(r'<section class="page" id="([^"]+)".*?</section>', h, re.S)}
ids = re.findall(r'<section class="page" id="([^"]+)"', h)
CAL = re.compile(r"(m\d+|d\d+-\d+|w\d+|week)$")
fixed = [k for k in ids if not CAL.match(k)]

# 1 -------------------------------------------------------------------------
base_fixed = None
if os.path.exists(BASE):
    bids = re.findall(r'<section class="page" id="([^"]+)"', io.open(BASE, encoding="utf-8").read())
    base_fixed = [k for k in bids if not CAL.match(k)]
check("고정 템플릿이 상품 1(v8.20)과 같은 키·순서",
      base_fixed is None or fixed == base_fixed,
      f"{len(fixed)}장" + ("" if base_fixed is None else f" / v8.20 {len(base_fixed)}장"))
expect = len(fixed) + 12 + len(days) + 1 + len(weeks)
check("페이지 수", len(ids) == expect == len(sections),
      f"{len(ids)} (기대 {expect} = 고정 {len(fixed)} + 12 + {len(days)}일 + 1 + {len(weeks)}주)")
check("키 중복 없음", len(set(ids)) == len(ids))

# 2 -------------------------------------------------------------------------
hrefs = set(re.findall(r'href="#([^"]+)"', h))
check("HTML 죽은 링크 0", not (hrefs - set(ids)), str(sorted(hrefs - set(ids))[:5]))

r = PdfReader(PDF)
check("PDF 페이지 수 = HTML", len(r.pages) == len(ids), f"{len(r.pages)}")
nd = r.named_destinations
pidx = {id(p.indirect_reference.get_object()): n for n, p in enumerate(r.pages)}
check("PDF named destination 이 모든 href 를 덮는다",
      not (hrefs - set(k.lstrip("/") for k in nd)),
      str(sorted(hrefs - set(k.lstrip("/") for k in nd))[:5]))
reach, bad_rail, broken = set(), [], 0
for n, pg in enumerate(r.pages):
    rail = 0
    for a in pg.get("/Annots") or []:
        o = a.get_object()
        d = o.get("/Dest")
        try:
            reach.add(pidx[id(nd[d]["/Page"].get_object())])
        except Exception:
            broken += 1
            continue
        if float(o["/Rect"][0]) < 60:
            rail += 1
    if rail != 10:
        bad_rail.append((n + 1, rail))
check("PDF 링크 전부 목적지 있음", broken == 0, f"깨진 것 {broken}")
check("탭 링크 페이지당 10개", not bad_rail, str(bad_rail[:5]))
unreached = [ids[i] for i in range(len(ids)) if i not in reach and ids[i] != "cover"]
check("표지 빼고 전 페이지가 어딘가에서 닿는다", not unreached, str(unreached[:5]))

# 3 -------------------------------------------------------------------------
def links(key):
    return set(re.findall(r'href="#([^"]+)"', sections.get(key, "")))


miss = []
for d in days:
    if dk(d) not in links(f"m{d.month}"):
        miss.append(f"{dk(d)} <- m{d.month}")
    if dk(d) not in links(f"w{week_of[d]}"):
        miss.append(f"{dk(d)} <- w{week_of[d]}")
    own = links(dk(d))
    if f"m{d.month}" not in own or f"w{week_of[d]}" not in own:
        miss.append(f"{dk(d)} -> m/w 칩")
for n in range(1, len(weeks) + 1):
    if f"w{n}" not in links("week"):
        miss.append(f"w{n} <- week")
for m in range(1, 13):
    if f"m{m}" not in links("month"):
        miss.append(f"m{m} <- month")
    grid_w = {week_of[d] for d in days if d.month == m}
    if not {f"w{n}" for n in grid_w} <= links(f"m{m}"):
        miss.append(f"m{m} 주 번호")
check("빠진 링크 0 (날·주·달 상호 연결)", not miss, f"{len(miss)}건 {miss[:4]}")

# 4 -------------------------------------------------------------------------
bad = []
for d in days:
    t = re.search(r"<h1>([A-Za-z]+), ([A-Za-z]{3}) (\d+)</h1>", sections[dk(d)])
    if not t or (t.group(1), t.group(2), int(t.group(3))) != (
            calendar.day_name[d.weekday()], calendar.month_abbr[d.month], d.day):
        bad.append(f"{dk(d)} 제목 {t.group(0) if t else None}")
for n, first in enumerate(weeks, 1):
    got = re.findall(r"(MON|TUE|WED|THU|FRI|SAT|SUN) &nbsp;(\d+)", sections[f"w{n}"])
    want = [(ABBR[(first + dt.timedelta(i)).weekday()], str((first + dt.timedelta(i)).day))
            for i in range(7)]
    if got != want:
        bad.append(f"w{n} 칩 {got[:2]}")
for m in range(1, 13):
    rows = re.findall(r"<tr>(.*?)</tr>", sections[f"m{m}"], re.S)[1:]
    for row in rows:
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)[1:]   # 첫 칸은 주 번호
        for col, c in enumerate(cells):
            a = re.search(rf'href="#d{m}-(\d+)"', c)
            if a and (dt.date(YEAR, m, int(a.group(1))).weekday() - WS) % 7 != col:
                bad.append(f"m{m} {a.group(1)}일이 {col}열")
check("날짜-요일 일치 (일간 제목·주간 칩·월 달력 열)", not bad, f"{len(bad)}건 {bad[:4]}")
first_col = re.findall(r"<th[^>]*>(MON|SUN)</th>", sections["m1"])
check("주 시작 요일", first_col[:1] == [ABBR[WS]], str(first_col[:1]))

# 5 -------------------------------------------------------------------------
tabbad = [m.group(1) for m in
          re.finditer(r'<section class="page" id="([^"]+)".*?</nav>', h, re.S)
          if len(re.findall(r'<a class="on"', m.group(0))) != 1 and m.group(1) != "cover"]
check("탭 하이라이트 정확히 1개", not tabbad, str(tabbad[:5]))

# 6 -------------------------------------------------------------------------
yrs = set(re.findall(r"\b20\d{2}\b", re.sub(r"https?://\S+", "", h)))
check("다른 해 숫자 없음", yrs <= {str(YEAR)}, str(sorted(yrs)))

print()
print(f"{VER}: {len(ids)}p, {os.path.getsize(PDF):,} B -- "
      + ("전부 통과" if not fails else f"FAIL {len(fails)}: {fails}"))
sys.exit(1 if fails else 0)
