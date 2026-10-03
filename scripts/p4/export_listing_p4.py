# -*- coding: utf-8 -*-
"""상품 4 리스팅 사진 10장 -- design 최종 HTML 을 2000 x 2000 JPG 로 내보낸다 (design 인수인계 1절).

    python scripts/p4/export_listing_p4.py [HTML] [OUT_VER]
    기본 HTML = src/p4_listing_design/design_handoff_listing_final/Etsy Listing 10 - Final.dc.html
    -> output/prod4/listing/<OUT_VER>/ : NN_name.png(무손실 원본) · NN_name.jpg(올릴 것, 1MB 이하) · _layout.json(글자 · 그림 자리)

실제 브라우저 화면 캡처(element.screenshot) -- 배경 질감(SVG 필터)과 알약 backdrop-filter 가 DOM 재렌더 방식에선 사라진다.
미리보기 축소(zoom 0.3)를 1 로 풀고, Nunito 를 다 불러온 뒤 찍는다. 이미 있는 폴더면 멈춘다(덮어쓰지 않는다).
"""
import io
import json
import os
import sys

from PIL import Image
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from chrome_auto import launch  # noqa: E402

HTML = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(
    ROOT, "src", "p4_listing_design", "design_handoff_listing_final", "Etsy Listing 10 - Final.dc.html")
OUT_VER = sys.argv[2] if len(sys.argv) > 2 else "design-final-v1.0"
OUT = os.path.join(ROOT, "output", "prod4", "listing", OUT_VER)
MAX_B = 1_000_000

# 글자 상자 · 그림 상자를 2000 틀 기준 좌표로
LAYOUT_JS = r"""
(frame) => {
  const fr = frame.getBoundingClientRect();
  const out = {text: [], img: []};
  const walker = document.createTreeWalker(frame, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = walker.nextNode())) {
    const t = n.textContent.trim();
    if (!t) continue;
    const el = n.parentElement, cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) continue;
    const r = document.createRange(); r.selectNodeContents(n);
    const b = r.getBoundingClientRect();
    if (!b.width) continue;
    out.text.push({t, x0: b.left - fr.left, y0: b.top - fr.top, x1: b.right - fr.left, y1: b.bottom - fr.top,
                   size: parseFloat(cs.fontSize), weight: cs.fontWeight, color: cs.color, family: cs.fontFamily});
  }
  for (const im of frame.querySelectorAll('img')) {
    const b = im.getBoundingClientRect();
    out.img.push({src: im.getAttribute('src'), x0: b.left - fr.left, y0: b.top - fr.top, x1: b.right - fr.left, y1: b.bottom - fr.top});
  }
  return out;
}
"""


def main():
    if os.path.exists(OUT):
        raise SystemExit(f"이미 있다 -- 덮어쓰지 않는다: {OUT}")
    os.makedirs(OUT)
    layout = {}
    with sync_playwright() as p:
        br = launch(p)
        page = br.new_page(viewport={"width": 2200, "height": 2200}, device_scale_factor=1)
        page.goto("file:///" + HTML.replace(os.sep, "/"), wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        # check 만 기다리면 아직 쓰이지 않은 굵기는 영영 false -- load 로 불러온 뒤 확인
        page.evaluate("Promise.all([400, 600, 700, 800].map(w => document.fonts.load(w + ' 150px Nunito')))")
        bad = [w for w in (400, 600, 700, 800) if not page.evaluate(f"document.fonts.check('{w} 150px Nunito')")]
        if bad:
            raise SystemExit(f"Nunito 굵기 {bad} 를 못 불러왔다 -- 대체 글꼴로 찍힌다")
        # 미리보기 축소 풀기 -- 각 장을 감싼 zoom 상자를 1 로
        page.evaluate("""() => document.querySelectorAll('[data-screen-label]').forEach(el => {
            let a = el.parentElement; a.style.zoom = '1'; a.style.borderRadius = '0'; a.style.boxShadow = 'none'; })""")
        page.wait_for_timeout(1500)
        labels = page.eval_on_selector_all("[data-screen-label]", "els => els.map(e => e.dataset.screenLabel)")
        for lab in labels:
            el = page.locator(f'[data-screen-label="{lab}"]')
            el.scroll_into_view_if_needed()
            page.wait_for_timeout(300)
            png = el.screenshot(type="png")
            im = Image.open(io.BytesIO(png)).convert("RGB")
            if im.size != (2000, 2000):
                raise SystemExit(f"{lab}: 크기 {im.size} != 2000x2000")
            im.save(os.path.join(OUT, f"{lab}.png"))
            for q in (90, 88, 85):
                buf = io.BytesIO(); im.save(buf, "JPEG", quality=q, optimize=True, progressive=True)
                if buf.tell() <= MAX_B:
                    break
            open(os.path.join(OUT, f"{lab}.jpg"), "wb").write(buf.getvalue())
            layout[lab] = el.evaluate(LAYOUT_JS)
            print(f"{lab}: JPG q{q} {buf.tell():,} B" + ("  ** 1MB 넘음 **" if buf.tell() > MAX_B else ""))
        br.close()
    json.dump(layout, open(os.path.join(OUT, "_layout.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(OUT)


if __name__ == "__main__":
    main()
