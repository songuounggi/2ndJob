# -*- coding: utf-8 -*-
"""완성된 PDF 에서 직접 글자 겹침을 잰다 -- 브라우저 화면 배치와 인쇄(PDF) 배치가 다를 수 있다. Prod 3 방 소유.

    python scripts/p3/audit_pdf_overlap_p3.py v0.11            # 네 판

2026-09-26: Year-end mailbox 알약 격자가 브라우저 화면에서는 멀쩡했는데 PDF 에서는 첫 줄만 벌어지고
나머지가 좁혀져 DEC 30·31 이 아래 라벨과 겹쳤다. 화면 기준 검사(audit_layout_p3)는 이걸 못 본다.
서로 다른 줄의 단어 상자가 겹치면 찍는다(같은 줄의 이웃 단어는 뺀다). 표지(1쪽)는 판 겹침 디자인이라 뺀다.
"""
import pathlib, re, sys, collections
import pymupdf
sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[2]
VER = sys.argv[1] if len(sys.argv) > 1 else "v0.11"
total = 0
for y in ("2026", "2027"):
    for w in ("mon", "sun"):
        name = f"ADHD-Year-Planner-{y}-{w}"
        ids = re.findall(r'<section class="pg" id="([^"]+)"', (ROOT / "src/prod3/planner" / VER / f"{name}.html").read_text(encoding="utf-8"))
        doc = pymupdf.open(ROOT / "output/prod3/planner" / VER / f"{name}.pdf")
        hits = collections.defaultdict(list)
        skip = {"cover", "focus", "feel", "health", "life"}   # 표지·섹션 표지: 제목을 판 겹침으로 두 번 찍는다(디자인)
        for i, pg in enumerate(doc):
            if ids[i] in skip:
                continue
            ws = pg.get_text("words")          # x0,y0,x1,y1,word,block,line,wno
            # 알약·칸 테두리가 글자를 가로지르는가 (글자가 상자 안에 다 들어 있으면 괜찮다)
            for dr in pg.get_drawings():
                r = dr["rect"]
                if not (14 <= r.height <= 40 and 20 <= r.width <= 260 and dr.get("color")):
                    continue
                for W_ in ws:
                    wr = pymupdf.Rect(W_[:4]); inter = wr & r
                    if inter.is_empty or inter.get_area() < 2:
                        continue
                    inside = r.contains(wr) or (wr.x0 >= r.x0 - 1 and wr.x1 <= r.x1 + 1 and wr.y0 >= r.y0 - 1 and wr.y1 <= r.y1 + 1)
                    if not inside and inter.height > wr.height * 0.25:
                        hits[i + 1].append(f"box/{W_[4]}")
            for a in range(len(ws)):
                for b in range(a + 1, len(ws)):
                    A, B = ws[a], ws[b]
                    if (A[5], A[6]) == (B[5], B[6]):
                        continue
                    ox = min(A[2], B[2]) - max(A[0], B[0]); oy = min(A[3], B[3]) - max(A[1], B[1])
                    h = min(A[3] - A[1], B[3] - B[1])
                    if ox > 1 and oy > h * 0.35:
                        hits[i + 1].append(f"{A[4]}/{B[4]}")
        kinds = collections.defaultdict(list)
        for n, v in hits.items():
            kinds[re.sub(r"\d+(-\d+)?$", "#", ids[n - 1])].append((n, v))
        print(f"== {VER} {name}: pages with overlapping text {len(hits)}")
        for k, lst in kinds.items():
            n, v = lst[0]
            print(f"  p{n:<4} {k:<12} {v[:4]}" + (f"  (+{len(lst) - 1} pages like it)" if len(lst) > 1 else ""))
        total += len(hits)
print("TOTAL", total)
sys.exit(1 if total else 0)
