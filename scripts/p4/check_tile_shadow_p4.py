# -*- coding: utf-8 -*-
"""상품 4 흰 미니카드 그림자 그림 검사 (10-03) -- 렌더한 PDF 픽셀로 잰다.

    python scripts/p4/check_tile_shadow_p4.py v0.18

  1 경계: 그림자 그림의 좌우 끝 양옆 밝기 차이 <= 1 (흰 바탕이라 끊기면 세로 선처럼 보인다 -- 첫 판 3단계)
  2 모서리: 바깥 카드 아래 두 모서리가 둥근가 -- 모서리 바로 바깥 점(카드 사각형 안, 원호 밖)이 흰색(>=250)이면 네모로 덮인 것
    (41쪽에서 사용자가 찾음: 그림자 그림의 흰 바탕이 둥근 모서리를 덮었다)
  그림자 그림 자리는 빌드 HTML 에서 읽는다(class="tile-shadow").
"""
import os
import re
import sys

import pypdfium2 as pdfium

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
VER = sys.argv[1] if len(sys.argv) > 1 else "v0.18"
S = 4


def main():
    html = open(os.path.join(ROOT, "src", f"p4_home-reset_{VER}_full_color.html"), encoding="utf-8").read()
    secs = re.findall(r'<section class="page" id="([^"]+)">(.*?)</section>', html, re.S)
    ids = [k for k, _ in secs]
    with open(os.path.join(ROOT, "output", "prod4", "planner", VER, f"home-reset_{VER}_color-FINAL.pdf"), "rb") as fh:
        doc = pdfium.PdfDocument(fh.read())
    fails, n = [], 0
    for k, body in secs:
        shadows = [tuple(int(v) for v in m) for m in re.findall(
            r'class="tile-shadow" src="[^"]*" alt="" style="position:absolute;left:(\d+)px;top:(\d+)px;width:(\d+)px;height:(\d+)px', body)]
        if not shadows:
            continue
        n += 1
        no = ids.index(k) + 1
        im = doc[no - 1].render(scale=S).to_pil().convert("L")
        cards = [tuple(int(v) for v in m) for m in re.findall(
            r'style="position:absolute;left:(\d+)px;top:(\d+)px;width:(\d+)px;height:(\d+)px;border-radius:16px;background:#FFFFFF', body)]
        for x, y, w, h in shadows:
            worst = 0
            # 경계 바로 바깥(0.5pt)과 바로 안쪽(0.25pt) -- 그 사이가 끊김. 더 넓게 재면 미니카드 옆 그림자의 자연스러운 변화까지 센다
            # (10-03: 미니카드가 경계에서 2pt 인 Reset week 에서 ±1pt 로 쟀더니 그림자 자체의 기울기 2단계를 끊김으로 셌다)
            for yy in range(y + 2, y + h - 1, 3):
                for xx, out_, in_ in ((x, -2, 1), (x + w, 2, -2)):
                    worst = max(worst, abs(im.getpixel((xx * S + out_, yy * S)) - im.getpixel((xx * S + in_, yy * S))))
            if worst > 1:
                fails.append(f"{no} {k}: 그림자 그림 경계에서 밝기가 {worst}단계 끊긴다 (x {x} / {x + w})")
            for cx, cy, cw, ch in cards:
                if cx <= x and x + w <= cx + cw and cy <= y and y + h <= cy + ch:
                    for px in (cx + 1, cx + cw - 2):          # 모서리 바로 안쪽 1pt -- 둥글면 카드 밖(배경색)
                        v = im.getpixel((px * S, (cy + ch - 1) * S))
                        if v >= 250:
                            fails.append(f"{no} {k}: 카드 아래 모서리({px}, {cy + ch - 1})가 네모로 덮였다 (밝기 {v})")
    doc.close()
    print(f"흰 미니카드 그림자 {VER}: 그림자 있는 쪽 {n}")
    for f in fails[:20]:
        print("  FAIL", f)
    print("검사 통과 (FAIL 0)" if not fails else f"FAIL {len(fails)}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
