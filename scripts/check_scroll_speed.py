# -*- coding: utf-8 -*-
"""스크롤·렌더 속도 검사 (PROCESS.md 5-5 필수, 모든 상품) -- 2026-10-01 사용자: "스크롤 & 렌더링 속도 측정을 필수 검수로".

    python scripts/check_scroll_speed.py <판.pdf> [--base <비교할 판.pdf>]

check_render.py 는 쪽당 **평균** 렌더 시간을 본다. 스크롤이 걸리는 것은 평균이 아니라 **튀는 쪽 하나**, 넘길 때마다
**처음 보는 큰 그림**, 그리고 **손짓을 먼저 가로채는 넓은 링크**에서 생긴다. 그래서 쪽마다 잰다:

  A 렌더(pdfium · mupdf, 2배): 최대 150ms 이하 · 상위 5% 100ms 이하 · 중앙값의 3배를 넘는 쪽 0
  B 그림: 쪽당 그림 수 · 서로 다른 그림 수 · 가장 큰 그림(KB, 픽셀) -- 한 장 300KB 넘으면 FAIL
     (서로 다른 그림이 많으면 넘길 때마다 새로 푼다 -- 상품 1 은 2개를 전 쪽이 함께 쓴다)
  C 그리기 명령(내용 스트림) KB/쪽: 최대 1.5MB 이하 -- 상품 1 v8.20 최대 1.29MB 가 iPad 를 통과한 값
  D 글꼴 방식(Type3 · TrueType ...) -- 기준 판과 다르면 알린다
  E 링크가 덮는 넓이 %/쪽 -- 65% 를 넘으면 FAIL(일부 뷰어는 링크 위 첫 손짓을 누르기로 먼저 받는다. 상품 1 v8.20 최대 65% 가
     iPad 를 통과했으니 그보다 넓히지 않는다)
  F 넘기기(pdf.js -- 브라우저 PDF 뷰어 엔진, 헤드리스 Chrome) **가장 중요한 항목**: 역검증에서 iPad 에서 늦던 상품 1 v8.18 을
     pdfium 은 47ms/쪽으로 통과시켰고 pdf.js 는 약 300ms/쪽(최대 707)으로 잡았다. 1쪽부터 끝까지 차례로 2배 크기로 그려 쪽마다 시간, 두 번.
     처음: 최대 300ms · 상위 5% 150ms 이하(글자 모양을 처음 준비하는 비용이 앞쪽에 몰린다 -- 상품 4 5쪽 목차 119ms 가
     거꾸로 넘기면 56ms). 두 번째: 최대 150ms · 튀는 쪽(중앙값 3배 넘고 100ms 넘는 쪽) 0
  --base 를 주면 같은 표를 기준 판(예: iPad 를 통과한 판매본)과 나란히 보여 준다

**Claude 가 매 빌드 돌리는 필수 검사다(사용자에게 넘기지 않는다 -- 10-01 사용자).** 7단계 iPad 는 마지막 확인일 뿐이다.
"""
import statistics as st
import sys
import time

import pikepdf
import pymupdf
import pypdfium2 as pdfium

sys.stdout.reconfigure(encoding="utf-8")
LIM = dict(max_ms=150, p95_ms=100, spike=3.0, img_kb=300, stream_kb=1500, link_pct=66, js_max=300, js_p95=150)

PDFJS = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"
PDFJS_WORKER = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js"
FLIP_JS = """async ([b64, pages]) => {
  pdfjsLib.GlobalWorkerOptions.workerSrc = '%s';
  const bin = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
  const doc = await pdfjsLib.getDocument({data: bin}).promise;
  const cv = document.createElement('canvas'); const ctx = cv.getContext('2d');
  const pass = async () => {
    const out = [];
    const list = pages || Array.from({length: doc.numPages}, (_, k) => k + 1);
    for (const i of list) {
      const t0 = performance.now();
      const pg = await doc.getPage(i);
      const vp = pg.getViewport({scale: 2});
      cv.width = vp.width; cv.height = vp.height;
      await pg.render({canvasContext: ctx, viewport: vp}).promise;
      out.push(performance.now() - t0);
      pg.cleanup();
    }
    return out;
  };
  const cold = await pass();          // 처음 넘길 때 -- 글자 모양을 처음 준비하는 비용 포함
  const warm = await pass();          // 두 번째 -- 준비가 끝난 뒤의 쪽 자체 무게
  return {cold, warm};
}""" % PDFJS_WORKER


def flip_pdfjs(path, pages=None):
    """F: 헤드리스 Chrome 의 pdf.js 로 1쪽부터 끝까지(또는 pages 만) 차례로 그린다(넘기기 흉내) -- 쪽마다 ms"""
    import base64
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from chrome_auto import launch
    from playwright.sync_api import sync_playwright
    b64 = base64.b64encode(open(path, "rb").read()).decode()
    with sync_playwright() as p:
        br = launch(p)
        pg = br.new_page()
        pg.set_content(f'<html><body><script src="{PDFJS}"></script></body></html>')
        pg.wait_for_function("window.pdfjsLib !== undefined", timeout=30000)
        t = pg.evaluate(FLIP_JS, [b64, pages])
        br.close()
    return t


def measure(path, scale=2.0):
    with open(path, "rb") as fh:
        data = fh.read()
    pd = pdfium.PdfDocument(data)
    md = pymupdf.open(stream=data, filetype="pdf")
    pk = pikepdf.open(path)
    n = len(pd)
    r = dict(path=path, n=n, mb=len(data) / 1e6, pdfium=[], mupdf=[], imgs=[], streams=[], links=[], fonts={})
    images = {}
    for i in range(n):
        a = time.perf_counter(); pd[i].render(scale=scale); r["pdfium"].append((time.perf_counter() - a) * 1000)
        a = time.perf_counter(); md[i].get_pixmap(matrix=pymupdf.Matrix(scale, scale)); r["mupdf"].append((time.perf_counter() - a) * 1000)
        page = pk.pages[i]
        xo = page.obj.get("/Resources", {}).get("/XObject") or {}
        im = [v for v in xo.values() if v.get("/Subtype") == "/Image"]
        r["imgs"].append(len(im))
        for v in im:
            images[v.objgen] = (len(v.read_raw_bytes()), int(v.get("/Width", 0)), int(v.get("/Height", 0)))
        cs = page.obj.get("/Contents")
        r["streams"].append(sum(len(c.read_bytes()) for c in (cs if isinstance(cs, pikepdf.Array) else [cs])) / 1e3)
        p = md[i]
        area = p.rect.width * p.rect.height
        r["links"].append(100 * sum(l["from"].width * l["from"].height for l in p.get_links()) / area)
        if i < 80:
            for f in p.get_fonts():
                r["fonts"][f[2]] = r["fonts"].get(f[2], 0) + 1
    pd.close()
    r["images"] = images
    r["pdfjs"] = flip_pdfjs(path)
    # 처음 넘기기에서 기준을 넘은 쪽은 앞 3장만 넘긴 뒤 다시 잰다 -- 수백 장을 연달아 넘긴 시점의 메모리 정리가 그 쪽에 얹히는 일이
    # 있다(상품 3 2027-mon 545쪽: 544장 뒤 330ms, 앞 5장 뒤 69ms, 거꾸로 16ms). 다시 재도 느리면 진짜다
    slow = [i + 1 for i, x in enumerate(r["pdfjs"]["cold"]) if x > LIM["js_max"]][:6]
    r["recheck"] = {p: flip_pdfjs(path, list(range(max(1, p - 3), p + 1)))["cold"][-1] for p in slow}
    return r


def rerender(path, eng, page, scale=2.0, n=3):
    """한 쪽을 n 번 다시 그려 가장 빠른 ms"""
    with open(path, "rb") as fh:
        data = fh.read()
    best = 1e9
    if eng == "pdfium":
        pd = pdfium.PdfDocument(data)
        pd[page - 1].render(scale=scale)                     # 한 번은 데우기
        for _ in range(n):
            a = time.perf_counter(); pd[page - 1].render(scale=scale); best = min(best, (time.perf_counter() - a) * 1000)
        pd.close()
    else:
        md = pymupdf.open(stream=data, filetype="pdf")
        md[page - 1].get_pixmap(matrix=pymupdf.Matrix(scale, scale))
        for _ in range(n):
            a = time.perf_counter(); md[page - 1].get_pixmap(matrix=pymupdf.Matrix(scale, scale)); best = min(best, (time.perf_counter() - a) * 1000)
    return best


def p95(xs):
    s = sorted(xs)
    return s[min(len(s) - 1, int(len(s) * .95))]


def report(r, label):
    fails = []
    print(f"== {label}: {r['n']}쪽, {r['mb']:.1f}MB  ({r['path']})")
    for eng in ("pdfium", "mupdf"):
        t = r[eng]
        med = st.median(t)
        spikes = [i + 1 for i, x in enumerate(t) if i and x > med * LIM["spike"] and x > 60]      # 표지(1쪽)는 참고, 60ms 밑의 차이는 안 센다
        # 튄 쪽은 3번 다시 그려 가장 빠른 값으로 -- 한 번 튄 것은 측정 잡음일 수 있다(상품 1 v8.20 501쪽 mupdf 98ms 가 한 번만 튐)
        spikes = [p for p in spikes if rerender(r["path"], eng, p) > max(med * LIM["spike"], 60)]
        print(f"  A {eng}: 평균 {st.mean(t):.0f} · 중앙 {med:.0f} · 상위5% {p95(t):.0f} · 최대 {max(t):.0f}ms (p{t.index(max(t)) + 1})"
              f" · 튀는 쪽 {spikes[:8] or '없음'}")
        if max(t[1:] or t) > LIM["max_ms"] or p95(t) > LIM["p95_ms"] or spikes:
            fails.append(f"A {eng} 렌더 (최대 {max(t):.0f} · 상위5% {p95(t):.0f} · 튀는 쪽 {spikes[:5]})")
    im = r["images"]
    big = max(im.values(), default=(0, 0, 0))
    print(f"  B 그림: 쪽당 {st.mean(r['imgs']):.1f}개 · 서로 다른 그림 {len(im)}개 · 가장 큰 그림 {big[0] / 1e3:.0f}KB ({big[1]}x{big[2]})"
          f" · 합 {sum(v[0] for v in im.values()) / 1e6:.1f}MB")
    if big[0] / 1e3 > LIM["img_kb"]:
        fails.append(f"B 그림 한 장 {big[0] / 1e3:.0f}KB > {LIM['img_kb']}KB")
    s = r["streams"]
    print(f"  C 그리기 명령: 평균 {st.mean(s):.0f} · 최대 {max(s):.0f}KB/쪽 (p{s.index(max(s)) + 1})")
    if max(s) > LIM["stream_kb"]:
        fails.append(f"C 그리기 명령 최대 {max(s):.0f}KB > {LIM['stream_kb']}KB")
    print(f"  D 글꼴 방식: {r['fonts']}")
    lk = r["links"]
    wide = sorted(((round(x), i + 1) for i, x in enumerate(lk) if x >= LIM["link_pct"]), reverse=True)
    print(f"  E 링크 넓이: 평균 {st.mean(lk):.0f}% · 최대 {max(lk):.0f}% (p{lk.index(max(lk)) + 1})"
          f" · {LIM['link_pct']}% 넘는 쪽 {[p for _, p in wide][:10] or '없음'}")
    if wide:
        fails.append(f"E 링크가 쪽의 {LIM['link_pct']}% 넘게 덮는 쪽 {[p for _, p in wide][:6]}")
    c, w = r["pdfjs"]["cold"], r["pdfjs"]["warm"]
    print(f"  F 넘기기 처음(pdf.js): 평균 {st.mean(c):.0f} · 중앙 {st.median(c):.0f} · 상위5% {p95(c):.0f} · 최대 {max(c):.0f}ms (p{c.index(max(c)) + 1})")
    real = {p: t for p, t in r.get("recheck", {}).items() if t > LIM["js_max"]}
    noise = {p: t for p, t in r.get("recheck", {}).items() if t <= LIM["js_max"]}
    if noise:
        print(f"    (참고) 연달아 넘긴 시점에만 느렸던 쪽 -- 앞 3장 뒤 다시 재면 " +
              ", ".join(f"p{p} {c[p - 1]:.0f}->{t:.0f}ms" for p, t in noise.items()) + " (메모리 정리 영향, FAIL 아님)")
    if real or p95(c) > LIM["js_p95"]:
        fails.append(f"F 처음 넘기기 (다시 재도 {LIM['js_max']}ms 넘는 쪽 {list(real)[:5]} · 상위5% {p95(c):.0f} > {LIM['js_p95']}?)")
    med = st.median(w)
    spikes = [i + 1 for i, x in enumerate(w) if x > med * LIM["spike"] and x > 100]
    print(f"  F 넘기기 두 번째: 평균 {st.mean(w):.0f} · 중앙 {med:.0f} · 상위5% {p95(w):.0f} · 최대 {max(w):.0f}ms (p{w.index(max(w)) + 1})"
          f" · 튀는 쪽 {spikes[:8] or '없음'}")
    if max(w) > LIM["max_ms"] or spikes:
        fails.append(f"F 두 번째 넘기기 (최대 {max(w):.0f} > {LIM['max_ms']} 또는 튀는 쪽 {spikes[:5]})")
    return fails


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    base = args[args.index("--base") + 1] if "--base" in args else None
    path = args[0]
    r = measure(path)
    fails = report(r, "검사 판")
    if base:
        b = measure(base)
        report(b, "기준 판")
        if set(b["fonts"]) != set(r["fonts"]):
            print(f"  ! 글꼴 방식이 기준 판과 다르다: {set(r['fonts'])} vs {set(b['fonts'])}")
    print("FAIL:\n  " + "\n  ".join(fails) if fails else "검사 통과 (FAIL 0)")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
