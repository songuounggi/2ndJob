# -*- coding: utf-8 -*-
"""뷰어에서 느리거나 다르게 그려질 위험을 잰다. 버전·상품 중립.

2026-09-24 판매본(v8.18)을 iPad GoodNotes 에서 넘기자 페이지가 바둑판처럼
늦게 채워졌고, 도트 그리드는 4배 넓게·흐릿하게 나왔다. 둘 다 PC 의 pdfium
렌더에서는 멀쩡했다. 그래서 "PC 에서 맞게 보인다"만으로는 통과시키지 않는다.

    python scripts/check_render.py output/prod1/planner_v8.20-undated-FINAL.pdf

재는 것:
  A. 구조 -- 뷰어마다 비싸거나 다르게 그리는 요소가 페이지에 있는가
     1. 그라데이션 셰이딩 (CSS gradient)      -> 타일마다 계산, GoodNotes 에서 느리다
     2. 소프트마스크 (opacity < 1 레이어)       -> 반투명 합성, 느리다
     3. 이미지를 담은 타일 패턴 (반복 배경)     -> GoodNotes 가 배율을 다르게 읽었다
     표지(1p)는 사진 위 번짐이 있어 예외로 둔다.
  B. 속도 -- iPad 해상도(scale 2.7)로 표본 페이지를 그리는 시간 (pdfium)
  C. 교차 엔진 -- 같은 페이지를 pdfium 과 MuPDF 로 그려 차이가 큰 페이지 (경고만)
     애플 엔진은 PC 에 없다. 두 엔진이 갈리면 세 번째도 갈릴 수 있다는 신호일 뿐이다.
     **도트 그리드 결함은 C 가 못 잡는다** -- MuPDF 도 pdfium 처럼 맞게 그린다.
     그 결함은 A-3 이 잡는다. C 를 통과했다고 iPad 확인을 건너뛰지 말 것
  D. 용량 -- Etsy 디지털 파일 상한 20MB

통과해도 iPad 실기기 확인(RELEASE.md 2절)은 따로 한다.
"""
import os, sys, time
import numpy as np
import pikepdf
import pypdfium2 as pdfium
import pymupdf

sys.stdout.reconfigure(encoding="utf-8")   # 한국어 Windows 콘솔은 cp949

MS_LIMIT = 150        # 페이지당 ms, 이 PC(집, 2026-09-24) 기준. v8.18=~200, v8.20=~70
XENG_MEAN = 1.5       # 두 엔진 평균 차이(0~255) 이상이면 경고
ETSY_MAX = 20_000_000


def scan(res, seen):
    """(shading, softmask, image-tile) counts under a resource dict."""
    sh = sm = it = 0
    if res is None:
        return 0, 0, 0
    for gs in (res.get('/ExtGState') or {}).values():
        if '/SMask' in gs and gs.SMask != pikepdf.Name('/None'):
            sm += 1
    for p in (res.get('/Pattern') or {}).values():
        pt = int(p.get('/PatternType', 0))
        if pt == 2:
            sh += 1
        if pt == 1:
            xo = (p.get('/Resources') or {}).get('/XObject') or {}
            it += any(x.get('/Subtype') == '/Image' for x in xo.values())
        a, b, c = scan(p.get('/Resources'), seen)
        sh += a; sm += b; it += c
    for v in (res.get('/XObject') or {}).values():
        if v.get('/Subtype') == '/Form' and v.objgen not in seen:
            seen.add(v.objgen)
            a, b, c = scan(v.get('/Resources'), seen)
            sh += a; sm += b; it += c
    return sh, sm, it


def gray(img):
    """RGB 단순 평균. MuPDF 쪽(C 항목)과 **같은 공식**이어야 한다.
    전에는 여기만 convert('L')(밝기 가중치)이라, 같은 그림도 채도가 높을수록
    차이가 나왔다 -- 상품 2 목차가 14.2 로 경고됐는데 같은 공식으로 재면
    0.59 였다. 상품 1 v8.20 도 0.76 -> 0.29 (2026-09-24, Prod 2 가 고침)."""
    return np.asarray(img.convert('RGB')).astype(np.int16).mean(axis=2)


def main(path):
    fail = 0
    def report(ok, msg, warn=False):
        nonlocal fail
        if not ok and not warn:
            fail += 1
        print(("  OK    " if ok else ("  WARN  " if warn else "  FAIL  ")) + msg)

    print(f"{path}\n")
    # A. 구조
    bad = {"gradient shading": [], "soft mask": [], "image tile pattern": []}
    with pikepdf.open(path) as pdf:
        n = len(pdf.pages)
        for i, pg in enumerate(pdf.pages, 1):
            sh, sm, it = scan(pg.Resources, set())
            if i == 1:
                continue
            if sh: bad["gradient shading"].append(i)
            if sm: bad["soft mask"].append(i)
            if it: bad["image tile pattern"].append(i)
    for k, pages in bad.items():
        report(not pages, f"A. {k:20s} 페이지 {len(pages):4d}  expect 0 (표지 제외)"
               + (f"  예: {pages[:8]}" if pages else ""))

    # 표본: 앞 70장(고유 템플릿이 모여 있다) + 이후 20장마다 한 장.
    # 표지는 A 처럼 빼고 따로 보여준다 -- 사진 위 반투명 번짐이라 원래 무겁고,
    # 한 번 열고 지나가는 페이지다.
    sample = list(range(2, min(n, 70) + 1)) + list(range(90, n + 1, 20))

    with open(path, 'rb') as fh:
        data = fh.read()
    pd = pdfium.PdfDocument(data)
    md = pymupdf.open(stream=data, filetype="pdf")

    # B. 속도
    times = []
    # 페이지마다 3번 재서 중앙값. 한 번만 재면 PC 가 순간 바쁠 때 튀어서,
    # 바뀐 것 없는 페이지가 160~180ms 로 FAIL 이 났다 -- 같은 페이지 10회
    # 중앙값은 105ms 였다 (2026-09-24, 집 PC, Prod 2 가 고침).
    for p in sample[::3]:
        pd[p - 1].render(scale=2.7)
        ts = []
        for _ in range(3):
            t = time.perf_counter()
            pd[p - 1].render(scale=2.7)
            ts.append((time.perf_counter() - t) * 1000)
        times.append((sorted(ts)[1], p))
    times.sort(reverse=True)
    pd[0].render(scale=2.7)
    t = time.perf_counter(); pd[0].render(scale=2.7)
    cover_ms = (time.perf_counter() - t) * 1000
    avg = sum(t for t, _ in times) / len(times)
    report(times[0][0] < MS_LIMIT,
           f"B. 렌더 시간  평균 {avg:.0f} ms / 최대 {times[0][0]:.0f} ms (p{times[0][1]})  expect < {MS_LIMIT}"
           f"  [표지 {cover_ms:.0f} ms, 참고]")

    # C. 교차 엔진
    worst = []
    for p in sample:
        a = gray(pd[p - 1].render(scale=1.5).to_pil())
        pix = md[p - 1].get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5), alpha=False)
        b = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, pix.n)
        b = b[..., :3].mean(axis=2).astype(np.int16)
        h, w = min(a.shape[0], b.shape[0]), min(a.shape[1], b.shape[1])
        d = np.abs(a[:h, :w] - b[:h, :w])
        worst.append((float(d.mean()), p))
    worst.sort(reverse=True)
    flagged = [p for m, p in worst if m >= XENG_MEAN]
    report(not flagged, f"C. 두 엔진 차이  최대 평균 {worst[0][0]:.2f} (p{worst[0][1]})  "
           f"경고 기준 {XENG_MEAN}  -> 페이지 {flagged[:10]}", warn=True)
    pd.close(); md.close()

    # D. 용량
    size = os.path.getsize(path)
    report(size < ETSY_MAX, f"D. 용량 {size:,} B  expect < {ETSY_MAX:,}")

    print(f"\nFAILURES: {fail}")
    return fail


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1]) else 0)
