# -*- coding: utf-8 -*-
"""모든 상품 공용 PDF 검사 -- 완성된 PDF 만 보고 잰다. 상품·HTML 구조와 무관 (2026-09-26 사용자 확정 규칙).

    python scripts/qa_pdf.py <pdf> [--skip 1,545,557] [--allow pitch:563,580]

  1. links   -- 모든 링크 주석의 목적지가 있고 페이지를 가리키는가
  2. overlap -- 서로 다른 줄의 글자가 겹치는가 / 알약·칸 테두리가 글자를 가로지르는가
  3. pitch   -- 한 페이지 안의 괘선 묶음들이 같은 간격인가 (같은 폭으로 3줄 이상 나란한 가로선 = 한 묶음)
  4. label   -- 글자 줄이 바로 위 가로선에 붙어 있지 않은가 (기준 12pt = 16px, 10pt 미만이면 FAIL)

--skip  : 검사하지 않을 페이지(1부터). 표지처럼 겹침이 디자인인 곳
--allow : 검사별 예외 페이지. 상품 문서에 이유를 적은 것만 넣는다
배경: 상품 3 에서 사용자가 줄 간격·라벨 붙음·겹침을 수십 건 찾았다. HTML 기준 검사는 상품마다 다시 짜야 하고,
화면 배치와 PDF 배치가 다를 때(상품 3 v0.11 mailbox) 놓친다. 그래서 PDF 를 직접 잰다.
"""
import argparse
import collections
import statistics
import sys

import pymupdf

sys.stdout.reconfigure(encoding="utf-8")
ap = argparse.ArgumentParser()
ap.add_argument("pdf")
ap.add_argument("--skip", default="")
ap.add_argument("--allow", default="", help="kind:page,page;kind:page  e.g. pitch:563,580;label:55")
ap.add_argument("--show", type=int, default=8)
a = ap.parse_args()
skip = {int(x) for x in a.skip.split(",") if x.strip()}
allow = collections.defaultdict(set)
for part in filter(None, a.allow.split(";")):
    k, ps = part.split(":")
    allow[k] |= {int(x) for x in ps.split(",") if x.strip()}

doc = pymupdf.open(a.pdf)
found = collections.defaultdict(list)          # kind -> [(page, detail)]


def add(kind, n, detail):
    if n not in allow[kind]:
        found[kind].append((n, detail))


# 1. links ---------------------------------------------------------------
for i, pg in enumerate(doc):
    for l in pg.get_links():
        if l.get("kind") == pymupdf.LINK_GOTO and (l.get("page", -1) < 0 or l["page"] >= len(doc)):
            add("links", i + 1, f"goto page {l.get('page')}")
        if l.get("kind") == pymupdf.LINK_NAMED and not doc.resolve_names().get(l.get("name") or l.get("nameddest"), None):
            add("links", i + 1, f"dest {l.get('name') or l.get('nameddest')} missing")

for i, pg in enumerate(doc):
    n = i + 1
    if n in skip:
        continue
    words = pg.get_text("words")                           # x0,y0,x1,y1,word,block,line,wno
    draws = pg.get_drawings()
    # 가로선: 높이 1.5pt 이하, 폭 40pt 이상 (선이든 얇은 사각형이든)
    hl = []
    for d in draws:
        for it in d["items"]:
            if it[0] == "l":
                p1, p2 = it[1], it[2]
                if abs(p1.y - p2.y) < 0.6 and abs(p2.x - p1.x) > 40:
                    hl.append((min(p1.x, p2.x), max(p1.x, p2.x), (p1.y + p2.y) / 2))
            elif it[0] == "re":
                r = it[1]
                if r.height <= 1.5 and r.width > 40:
                    hl.append((r.x0, r.x1, r.y0 + r.height / 2))
    hl = sorted(set((round(x0), round(x1), round(y, 1)) for x0, x1, y in hl), key=lambda t: t[2])

    # 2. overlap -----------------------------------------------------------
    for p in range(len(words)):
        for q in range(p + 1, len(words)):
            A, B = words[p], words[q]
            if (A[5], A[6]) == (B[5], B[6]):
                continue
            ox = min(A[2], B[2]) - max(A[0], B[0]); oy = min(A[3], B[3]) - max(A[1], B[1])
            if ox > 1 and oy > min(A[3] - A[1], B[3] - B[1]) * 0.35:
                add("overlap", n, f"text {A[4]!r}/{B[4]!r}")
    for d in draws:
        r = d["rect"]
        if not (10 <= r.height <= 30 and 15 <= r.width <= 200 and d.get("color")):
            continue
        for W in words:
            wr = pymupdf.Rect(W[:4]); inter = wr & r
            if inter.is_empty or inter.get_area() < 1.5:
                continue
            inside = wr.x0 >= r.x0 - 1 and wr.x1 <= r.x1 + 1 and wr.y0 >= r.y0 - 1 and wr.y1 <= r.y1 + 1
            if not inside and inter.height > wr.height * 0.25:
                add("overlap", n, f"border/{W[4]!r}")

    # 쓰기 줄 묶음: 같은 폭의 가로선이 연달아 있고, 두 선 사이에 글자가 없는 것 (표 안 글자·일정표 시각은 빠진다)
    def text_between(x0, x1, ya, yb):
        return any(w[1] < yb - 1 and w[3] > ya + 1 and w[0] < x1 and w[2] > x0 for w in words)
    groups = collections.defaultdict(list)
    for x0, x1, y in hl:
        groups[(x0 // 3, x1 // 3)].append((x0, x1, y))
    empty_runs = []                                    # [(x0, x1, [y...])]
    for key, ls in groups.items():
        ls = sorted(ls, key=lambda t: t[2]); cur = [ls[0]]
        for prev, nxt in zip(ls, ls[1:]):
            gap = nxt[2] - prev[2]
            if gap > 4 and gap < 60 and not text_between(prev[0], prev[1], prev[2], nxt[2]):
                cur.append(nxt)
            else:
                if len(cur) >= 3: empty_runs.append(cur)
                cur = [nxt]
        if len(cur) >= 3: empty_runs.append(cur)

    # 3. pitch -- 한 묶음 안은 같은 간격, 한 페이지의 묶음끼리도 같은 간격
    pitches = []
    for run in empty_runs:
        gaps = [round(b[2] - a[2], 1) for a, b in zip(run, run[1:])]
        if max(gaps) - min(gaps) > 1.2:
            add("pitch", n, f"uneven lines {sorted(set(gaps))}pt at y={run[0][2]:.0f}")
        pitches.append(statistics.median(gaps))
    if len(pitches) >= 2 and max(pitches) - min(pitches) > 1.2:
        add("pitch", n, f"line groups differ {sorted(set(round(x, 1) for x in pitches))}pt")

    # 4. label -- 쓰기 줄 묶음의 제목(묶음 첫 줄 바로 위 글자 줄)이 그 위 가로선에 붙어 있지 않은가
    lines_ = collections.defaultdict(list)
    for W in words:
        lines_[(W[5], W[6])].append(W)
    tl = [(min(w[0] for w in ws), max(w[2] for w in ws), min(w[1] for w in ws), max(w[3] for w in ws), " ".join(w[4] for w in ws))
          for ws in lines_.values()]
    for run in empty_runs:
        rx0, rx1, ry = run[0]
        heads = [t for t in tl if t[3] <= ry + 0.5 and ry - t[3] < 45 and t[0] < rx1 and t[1] > rx0]
        if not heads:
            continue
        top = min(heads, key=lambda t: t[2])           # 제목 묶음의 맨 윗줄 (두 줄 라벨이면 윗줄)
        above = [y for lx0, lx1, y in hl if y <= top[2] + 0.5 and lx0 < top[1] - 3 and lx1 > top[0] + 3 and top[2] - y < 40]
        if above:
            g = top[2] - max(above)
            if g < 6:
                add("label", n, f"{top[4][:24]!r} {g:.1f}pt below a line")

bad = 0
for kind in ("links", "overlap", "pitch", "label"):
    items = found[kind]
    pages = sorted({p for p, _ in items})
    print(f"{'FAIL' if items else 'OK  '} {kind:<8} pages {len(pages)}" + (f"  e.g. {pages[:12]}" if pages else ""))
    for p, d in items[:a.show]:
        print(f"       p{p}: {d}")
    bad += bool(items)
print(f"\n{a.pdf}: {'ALL OK' if not bad else f'FAILURES {bad}'}  ({len(doc)} pages)")
sys.exit(1 if bad else 0)
