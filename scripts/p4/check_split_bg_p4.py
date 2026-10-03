# -*- coding: utf-8 -*-
"""상품 4 -- 배경 나누기(v0.23, split_bg_p4) 검사: 모양은 그대로인가, 넘김은 빨라졌나 (10-04 사용자).

    python scripts/p4/check_split_bg_p4.py <판> [기준 판=v0.22]

  1 모양: 쪽마다 기준 판과 렌더(2배) 비교 -- 평균 차이 0.3 단계 이하, 8x8 칸 평균의 최대 차이 3 단계 이하
    (조각 경계에 이음매가 생기면 칸 최대가 튄다. 그림자 이음매는 이 프로젝트에서 가장 예민한 항목 -- CLAUDE.md 그림자 절)
  2 큰 그림: 쪽마다 "처음 나오는 큰 그림(0.5백만 픽셀 이상)" -- 표지 빼고 섹션마다 첫 쪽에서만 나와야 한다
  3 넘김(pdf.js, 두 번째): 섹션별 중앙값 -- 기준 판보다 느려진 섹션 0, Tools 45ms 이하
"""
import os
import statistics as st
import sys

import pikepdf
import pypdfium2 as pdfium
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.stdout.reconfigure(encoding="utf-8")

SEC = [(1, "HOME"), (6, "ENERGY"), (10, "ROOMS"), (31, "ROUTINES"), (40, "WEEKS"), (93, "TOOLS")]
sec_of = lambda n: [s for f, s in SEC if n >= f][-1]
pdf_of = lambda v: os.path.join(ROOT, "output", "prod4", "planner", v, f"home-reset_{v}_color-FINAL.pdf")


def big_new(path, min_px=500_000):
    pdf = pikepdf.open(path)
    seen, out = set(), []
    for n, pg in enumerate(pdf.pages, 1):
        new = []
        for _, x in pg.obj.Resources.get("/XObject", {}).items():
            if x.get("/Subtype") == "/Image" and int(x.Width) * int(x.Height) >= min_px and x.objgen not in seen:
                seen.add(x.objgen)
                new.append(x.objgen)
        if new:
            out.append(n)
    return out


def main(ver, base="v0.22"):
    fails = []
    A = pdfium.PdfDocument(open(pdf_of(base), "rb").read())
    B = pdfium.PdfDocument(open(pdf_of(ver), "rb").read())
    worst = []
    for i in range(len(A)):
        a = A[i].render(scale=2).to_pil().convert("L")
        b = B[i].render(scale=2).to_pil().convert("L")
        d = ImageChops.difference(a, b)
        h = d.histogram()
        mean = sum(k * c for k, c in enumerate(h)) / (a.width * a.height)
        blk = max(d.resize((a.width // 8, a.height // 8), Image.BOX).getdata())
        worst.append((round(blk, 1), round(mean, 3), i + 1))
        if mean > 0.3 or blk > 3:
            fails.append(f"{i + 1}쪽 모양 차이: 평균 {mean:.3f} · 8x8 칸 최대 {blk} ({base} 대비)")
    worst.sort(reverse=True)
    print(f"1 모양 ({base} 대비): 칸 최대 차이 상위 {worst[:5]} (칸 최대 · 평균 · 쪽)")
    nb, nv = big_new(pdf_of(base)), big_new(pdf_of(ver))
    allowed = {f for f, _ in SEC} | {2}          # 섹션 첫 쪽 + 2쪽(순서도 -- design 이 구운 배경, 섹션 바탕과 다르면 나누지 않는다)
    extra = [n for n in nv if n not in allowed]
    print(f"2 처음 나오는 큰 그림이 있는 쪽: {base} {len(nb)}쪽 -> {ver} {len(nv)}쪽 {nv[:20]}")
    if extra:
        fails.append(f"섹션 첫 쪽이 아닌데 새 큰 그림: {extra[:12]} ({len(extra)}쪽)")
    import check_scroll_speed as cs
    wb, wv = cs.flip_pdfjs(pdf_of(base))["warm"], cs.flip_pdfjs(pdf_of(ver))["warm"]
    print("3 넘김(pdf.js 두 번째, 섹션 중앙 ms):")
    for f, s in SEC:
        ix = [i for i in range(len(wv)) if sec_of(i + 1) == s]
        mb, mv = st.median(wb[i] for i in ix), st.median(wv[i] for i in ix)
        print(f"   {s:9} {base} {mb:4.0f} -> {ver} {mv:4.0f}")
        if mv > mb * 1.25 + 10:
            fails.append(f"{s} 넘김이 느려짐 {mb:.0f} -> {mv:.0f}ms")
        if s == "TOOLS" and mv > 45:
            fails.append(f"TOOLS 넘김 {mv:.0f}ms > 45")
    print("FAIL:" if fails else "검사 통과 (FAIL 0)")
    for x in fails:
        print("  ", x)
    return len(fails)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], *(sys.argv[2:3])))
