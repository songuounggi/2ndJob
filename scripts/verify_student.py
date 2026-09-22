# -*- coding: utf-8 -*-
"""상품 2(학생용) 산출물 검사. 구조 + 눈으로 보이는 결함까지.

    python scripts/verify_student.py [버전]        기본 student-v0.1

`verify_v8.py` 의 구조 검사 13항목을 옮겨오고, 2026-09-22 하루 동안
"검사는 통과인데 눈으로는 깨져 있던" 종류를 항목으로 만들었다:

  · 점선이 확대율마다 길이·두께가 달라짐
      -> 정수 배율(12배)로만 재면 전부 통과한다. 1.5/2/2.5/3배로 재야
         드러난다. 주기와 줄 간격이 4의 배수 pt 가 아니면 여기서 잡힌다.
  · 면 그림자가 한 종류만 빠짐
      -> brain dump 의 필기면만 overflow:hidden 이라 ::after 가 잘렸다.
         고유 템플릿 전부에서 면 아래 어두워지는지 잰다.
  · 괘선이 면의 반쪽만 채움
      -> <svg> 를 width:auto 로 두면 고유 크기(300x150px)로 눕는다.
         마지막 줄이 면 바닥 가까이 오는지 잰다.

검사가 사용자의 눈보다 느슨하면 검사가 아니다. 새 결함을 만나면
반드시 여기에 항목을 하나 추가하고 나서 고칠 것.
"""
import io
import os
import re
import sys
from collections import Counter

import numpy as np
import pypdfium2 as pdfium
from pypdf import PdfReader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = sys.argv[1] if len(sys.argv) > 1 else "student-v0.1"
PDF = os.path.join(ROOT, "output", "planner_%s.pdf" % VERSION)
HTML = os.path.join(ROOT, "src", "planner_%s.html" % VERSION)

LIMIT = 20_000_000          # Etsy 디지털 파일 상한
ZOOMS = (1.5, 2.0, 2.5, 3.0)
MIN_SHADOW = 15.0           # 면 아래 밝기 회복폭. 정상은 23~27
MONTHS = (r"\b(January|February|March|April|May|June|July|August|September|"
          r"October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|"
          r"Nov|Dec)\b")

checks = []                 # (이름, 실제값, 기대, 통과?)


def add(name, got, exp, ok):
    checks.append((name, got, exp, ok))


# ------------------------------------------------------------------ 구조
h = io.open(HTML, encoding="utf-8").read()
r = PdfReader(PDF)
nd = r.named_destinations
idx = {id(p.indirect_reference.get_object()): n + 1
       for n, p in enumerate(r.pages)}

ids = re.findall(r'<section class="page[^"]*" id="([^"]+)"', h)
n_tabs = len(re.findall(r'<a class="[^"]*" href="#', h.split("</nav>")[0])) or 10

links = broken = 0
reach = set()
norail = []
for n, pg in enumerate(r.pages, 1):
    rail = 0
    for a in pg.get("/Annots") or []:
        o = a.get_object()
        d = o.get("/Dest")
        if d is None:
            broken += 1
            continue
        links += 1
        try:
            reach.add(idx[id(nd[d]["/Page"].get_object())])
        except Exception:
            broken += 1
        if float(o["/Rect"][0]) < 60:
            rail += 1
    if rail != n_tabs:
        norail.append((n, rail))

dead = sorted({a for a in re.findall(r'href="#([^"]*)"', h)
               if a not in set(ids)})
tabbad = [m.group(1) for m in
          re.finditer(r'<section class="page[^"]*" id="([^"]+)".*?</nav>',
                      h, re.S)
          if len(re.findall(r'<a class="on"', m.group(0))) != 1
          and m.group(1) != "cover"]
# SVG 경로 데이터에 H2048 같은 좌표가 있어 연도로 오인된다. 먼저 걷어낸다.
prose = re.sub(r"<svg.*?</svg>", "", h, flags=re.S)
prose = re.sub(r"https?://" + chr(92) + "S+", "", prose)
months = Counter(re.findall(MONTHS, prose))
years = re.findall(r"(?:19|20)\d{2}", prose)
korean = re.findall(r"[가-힣]", h)
nbytes = os.path.getsize(PDF)

add("페이지 수", len(r.pages), len(ids), len(r.pages) == len(ids))
add("용량 (MB)", round(nbytes / 1_000_000, 2), "< 20", nbytes < LIMIT)
# 여유는 참고값이다. 2026-09-22 에 "일단 올려 보고 막히면 줄인다"로
# 결정했다. v8 은 19.23MB 로 통과한 전례가 있다.
add("여유 (참고)", "%.1f%%" % (100 * (LIMIT - nbytes) / LIMIT), "-", True)
add("목적지", len(nd), len(ids) - 1, len(nd) == len(ids) - 1)
add("링크 주석", links, "> 0", links > 0)
add("끊어진 링크", broken, 0, broken == 0)
add("목적지 없는 앵커", len(dead), 0, not dead)
add("도달 불가 페이지", len(set(range(2, len(r.pages) + 1)) - reach), 0,
    not (set(range(2, len(r.pages) + 1)) - reach))
add("탭 %d개가 아닌 페이지" % n_tabs, len(norail), 0, not norail)
add("탭 하이라이트 오류", len(tabbad), 0, not tabbad)
add("HTML 속 월 이름", sum(months.values()), 0, not months)
add("HTML 속 연도", len(years), 0, not years)
add("HTML 속 한글", len(korean), 0, not korean)


# ------------------------------------------------------------------ 시각
with open(PDF, "rb") as fh:
    doc = pdfium.PdfDocument(fh.read())


def gray(page, scale):
    return np.asarray(doc[page].render(scale=scale).to_pil().convert("L")
                      ).astype(float)


def runs(vals, cut):
    out, i = [], 0
    while i < len(vals):
        if vals[i] < cut:
            j = i
            while j < len(vals) and vals[j] < cut:
                j += 1
            out.append((i, j - i))
            i = j
        else:
            i += 1
    return out


def uniq(page, y_lo, y_hi, x0, x1):
    """확대율마다 점 길이와 선 두께가 단일값인지.

    주의: 대역에 세로 구분선이나 면 가장자리가 끼면 3~4px 짜리 가짜
    '선'이 잡힌다. 그래서 가로로 점이 5개 이상 끊겨 있는 줄만 센다.
    이 함정에 두 번 빠졌다.
    """
    bad = []
    for z in ZOOMS:
        a = gray(page, z)
        H = a.shape[0]
        band = a[:, int(x0 * z):int(x1 * z)]
        rm = band.min(axis=1)
        y0, y1 = int(H * y_lo), int(H * y_hi)
        bg = np.median(rm[y0:y1])
        th, dash = [], []
        for st, ln in runs(rm[y0:y1], bg - 3):
            if ln / z >= 2:
                continue
            row = band[y0 + st + ln // 2]
            d = [n for _, n in runs(row, row.max() - 4)]
            if len(d) < 5:          # 점선이 아니라 선/가장자리다
                continue
            th.append(ln)
            dash += d[1:-1]
        if th and (max(th) != min(th)):
            bad.append("%.1f배 두께 %d~%d px" % (z, min(th), max(th)))
        if dash and (max(dash) != min(dash)):
            bad.append("%.1f배 점 길이 %d~%d px" % (z, min(dash), max(dash)))
    return bad


def shadows(page, xs=(150, 300, 450), scale=6):
    """면 아래로 밝기가 회복되는 폭. 그림자가 있으면 15 이상."""
    a = gray(page, scale)
    deps = []
    for x in xs:
        col = a[:, int(x * scale) - 20:int(x * scale) + 20].mean(axis=1)
        for y in range(int(120 * scale), int(775 * scale)):
            if col[y - 1] - col[y] > 8 and col[y - 1] > 234:
                b = y / scale
                v = [col[int((b + t) * scale)] for t in (1, 4, 8, 13)
                     if (b + t) * scale < len(col)]
                if len(v) == 4:
                    deps.append(v[-1] - v[0])
    return max(deps) if deps else 0.0


def dashed_rows(a, scale, x0=120, x1=280):
    """점선인 가로줄의 y 목록. 가로로 5번 이상 끊긴 줄만 센다."""
    band = a[:, int(x0 * scale):int(x1 * scale)]
    rm = band.min(axis=1)
    bg = np.median(rm)
    out = []
    for st, ln in runs(rm, bg - 3):
        if ln / scale >= 2:
            continue
        row = band[st + ln // 2]
        if len([n for _, n in runs(row, row.max() - 4)]) >= 5:
            out.append((st + ln / 2) / scale)
    return out


def lines_fill(page, scale=6):
    """괘선이 면 바닥까지 차 있는가.

    (마지막 줄 ~ 면 바닥) / 줄 간격. 1.0 근처면 정상이고, 2 를 넘으면
    아래가 비었다는 뜻이다. <svg> 가 고유 크기로 누워 면의 반쪽만
    채웠던 사고를 잡는 항목이다.
    """
    a = gray(page, scale)
    rows = dashed_rows(a, scale)
    if len(rows) < 3:
        return None
    groups = [[rows[0]]]
    for y in rows[1:]:
        if y - groups[-1][-1] > 40:
            groups.append([])
        groups[-1].append(y)
    g = max(groups, key=len)
    if len(g) < 3:
        return None
    step = np.median(np.diff(g))
    col = a[:, int(300 * scale) - 40:int(300 * scale) + 40].mean(axis=1)
    y = int(g[-1] * scale)
    while y < len(col) - 1 and not (col[y] - col[y + 1] > 6 and col[y] > 234):
        y += 1
    return (y / scale - g[-1]) / step


uniq_pages = [k for k in ("d1", "syllabus", "timetable") if k in ids]
bad_uniform = []
for k in uniq_pages:
    bad_uniform += ["%s: %s" % (k, b)
                    for b in uniq(ids.index(k), 0.20, 0.95, 120, 280)]
add("점선 균일 (1.5/2/2.5/3배)", len(bad_uniform), 0, not bad_uniform)

panels = {m.group(1) for m in
          re.finditer(r'<section class="page[^"]*" id="([^"]+)"'
                      r'(?:(?!<section).)*?class="(?:field|lines|tbwrap)',
                      h, re.S)}
tpl = [k for k in ids if not re.fullmatch(r"[twdc]\d+", k)
       and k not in ("cover", "index") and k in panels]
weak = [(k, round(shadows(ids.index(k)), 1)) for k in tpl]
weak = [(k, v) for k, v in weak if v < MIN_SHADOW]
add("면 그림자 없는 템플릿", len(weak), 0, not weak)

gap = lines_fill(ids.index("d1")) if "d1" in ids else None
add("괘선 빈 구간 (줄 간격 배수)",
    "-" if gap is None else round(gap, 2), "< 1.6",
    gap is not None and gap < 1.6)

doc.close()

# ------------------------------------------------------------------ 출력
print()
print("  %-28s %14s   %s" % ("항목", "값", "기대"))
print("  " + "-" * 62)
fail = 0
for name, got, exp, ok in checks:
    if not ok:
        fail += 1
    print(("  OK  " if ok else "  실패") + "  %-26s %14s   %s"
          % (name, got, exp))
if dead:
    print("   목적지 없는 앵커:", dead[:8])
if tabbad:
    print("   탭이 잘못된 페이지:", tabbad[:8])
if months:
    print("   월 이름:", dict(months))
if bad_uniform:
    print("   점선 불균일:", bad_uniform[:6])
if weak:
    print("   그림자 약한 템플릿:", weak[:8])
print()
print("실패:", fail)
sys.exit(1 if fail else 0)
