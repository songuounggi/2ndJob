# -*- coding: utf-8 -*-
"""상품 4 -- 쪽 배경 JPG 를 "섹션 바탕(같이 씀) + 그림자 조각(쪽마다 작게)" 으로 나눈다 (v0.23, 10-04 사용자).

왜: design 시안은 카드 그림자를 쪽 배경 JPG(1224x1584)에 구워 넣는다. 카드 배치가 쪽마다 다른 HOME · ROUTINES · TOOLS 는
쪽마다 배경이 달라 넘길 때마다 큰 그림을 새로 푼다 -- iPad 에서 93~100쪽(Tools) 넘김이 뚝뚝 끊겼다(사용자). pdf.js 두 번째 넘김
Tools 중앙 72ms vs 배경을 같이 쓰는 Weeks 27ms.

어떻게(모양은 그대로 -- CLAUDE.md 속도 규칙 "같은 모양을 싸게"):
  1 섹션 바탕 = design 굽기 코드(bake_bg_p4.BAKE_JS)로 카드 없이 구운 것 -- 번짐 · 유리 탭 · 켜진 탭 · SOS 그림자. 섹션(탭)마다 한 장
  2 쪽 배경과 바탕이 다른 곳(그림자)만 32px 칸 단위로 잘라 원본 그대로의 조각 JPG 로 위에 얹는다. 투명도 없음(GoodNotes 안전)
  3 HTML 흰 카드가 덮는 카드 안쪽은 비교에서 뺀다(어차피 안 보인다)
  4 조각은 내용 지문으로 이름 -- 같은 조각은 여러 쪽이 같이 쓴다(Reset week 52장 등)
검증: 빌드 뒤 v0.22 와 쪽마다 픽셀 비교(scripts/p4/check_split_bg_p4.py).
"""
import hashlib
import io
import os
import re

from PIL import Image, ImageChops, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
S = 2                 # 배경 그림 1pt = 2px
CELL = 48             # 조각 칸(px) = 24pt. **3pt 의 배수여야 한다** -- Chrome 은 인쇄할 때 그림 위치 · 크기를 96dpi 정수 픽셀(= 0.75pt)로
                      # 맞춘다. 64px(32pt) 칸은 64 -> 63.75pt, 128 -> 128.25pt 로 밀려 그림자가 1px 어긋났다(10-04 첫 v0.23, 카드 경계 띠).
                      # 48px = 24pt = 32 CSS px 라 밀림 0, JPEG 4:2:0 블록(16px)과도 맞다. 실측(85~109쪽 pdf.js 두 번째 넘김 Tools 중앙):
                      # 원본 74ms -> 32px 21ms(조각 31/쪽) · 48px 23ms(15/쪽) · 64px 19ms(18/쪽). 덩어리 하나로 합치면 66ms(넓어서 이득 없음)
THRESH = 1.5          # 바탕과 이만큼(밝기 단계) 넘게 다르면 조각으로. 흐림(반지름 1.5px) 뒤에 재서 JPEG 잡티는 무시
MAX_SHARE = 0.75      # 조각이 쪽의 이보다 넓으면 나누지 않는다(이득 없음) -- 원본 그대로
BG_RE = re.compile(r'<img src="([^"]+\.jpg)" alt="" style="position:absolute;left:0;top:0;width:612px;height:792px">')


def base_path(design_dir, col, tab):
    return os.path.join(design_dir, "generated", f"p4-base-{col}-t{tab}.jpg")


def ensure_base(design_dir, col, tab):
    """섹션 바탕: 카드 · 알약 없이 굽는다(번짐 · 유리 탭 · 켜진 탭 · SOS 는 그대로)"""
    out = base_path(design_dir, col, tab)
    if not os.path.exists(out):
        import bake_bg_p4 as K
        K.bake([(out, K.COLORS[col], tab, [])])
    return out


def covered(page_html):
    """HTML 이 흰 바탕으로 덮는 카드 안쪽(px, 1pt 안으로) -- 비교에서 뺀다"""
    import bake_bg_p4 as K
    out = []
    for r in K.rects_of(page_html):
        if r.get("ban"):
            continue
        if r["y"] == 754.0:          # 쪽 아래 알약은 HTML 에 흰 바탕이 없다(배경에 구워져 있다) -- 덮지 않는다
            continue
        out.append(((r["x"] + 1) * S, (r["y"] + 1) * S, (r["x"] + r["w"] - 1) * S, (r["y"] + r["h"] - 1) * S, r["r"] * S))
    return out


def patches(orig_path, base, cover):
    """원본 배경과 바탕이 다른 칸 -> 직사각형 목록(px). 카드 안쪽(cover)은 빼고"""
    src = Image.open(orig_path)
    qt = getattr(src, "quantization", None)        # 원본 양자화 표 -- 조각을 같은 표 · 4:2:0 으로 저장하면 칸(64px)이 블록과 맞아 거의 손실 없다
    A = src.convert("RGB")
    A.info["p4_qtables"] = qt
    B = Image.open(base).convert("RGB")
    d = ImageChops.difference(A.filter(ImageFilter.GaussianBlur(1.5)), B.filter(ImageFilter.GaussianBlur(1.5))).convert("L")
    m = d.point(lambda v: 255 if v > THRESH else 0)
    from PIL import ImageDraw
    dr = ImageDraw.Draw(m)
    for x0, y0, x1, y1, r in cover:
        dr.rounded_rectangle([x0, y0, x1, y1], radius=max(r - 2, 0), fill=0)
    W, H = A.size
    cols, rows = (W + CELL - 1) // CELL, (H + CELL - 1) // CELL
    on = [[m.crop((c * CELL, r * CELL, min(W, (c + 1) * CELL), min(H, (r + 1) * CELL))).getbbox() is not None for c in range(cols)]
          for r in range(rows)]
    # 줄마다 이어진 칸 -> 구간, 위아래로 같은 구간이면 합친다
    rects, open_ = [], {}
    for r in range(rows + 1):
        runs = set()
        if r < rows:
            c = 0
            while c < cols:
                if on[r][c]:
                    s = c
                    while c < cols and on[r][c]:
                        c += 1
                    runs.add((s, c))
                else:
                    c += 1
        for k in list(open_):
            if k not in runs:
                s, e = k
                rects.append((s * CELL, open_.pop(k) * CELL, min(W, e * CELL), min(H, r * CELL)))
        for k in runs:
            open_.setdefault(k, r)
    return A, rects


def split(page_html, design_dir, col, tab, rel_of):
    """쪽 HTML 의 배경 그림 하나 -> 바탕 + 조각들. 바꾼 HTML 과 (조각 넓이 비율) 을 돌려준다"""
    m = BG_RE.search(page_html)
    if not m:
        return page_html, None
    orig = os.path.join(ROOT, "src", m.group(1).replace("/", os.sep))
    base = ensure_base(design_dir, col, tab)
    A, rects = patches(orig, base, covered(page_html))
    area = sum((x1 - x0) * (y1 - y0) for x0, y0, x1, y1 in rects) / (A.width * A.height)
    if area > MAX_SHARE:
        return page_html, area
    gen = os.path.join(design_dir, "generated", "patches")
    os.makedirs(gen, exist_ok=True)
    imgs = []
    for x0, y0, x1, y1 in rects:
        crop = A.crop((x0, y0, x1, y1))
        buf = io.BytesIO()
        # 10-04 첫 v0.23 은 quality 92 · 4:4:4 로 저장해 컬러판이 6.02MB(리스팅 "under 6 MB" 넘음) -- 원본과 같은 표 · 4:2:0 으로
        qt = A.info.get("p4_qtables")
        crop.save(buf, "JPEG", qtables=qt, subsampling=2) if qt else crop.save(buf, "JPEG", quality=85, subsampling=2)
        data = buf.getvalue()
        f = os.path.join(gen, f"pt-{hashlib.md5(data).hexdigest()[:12]}.jpg")
        if not os.path.exists(f):
            open(f, "wb").write(data)
        imgs.append(f'<img class="bg-patch" src="{rel_of(f)}" alt="" style="position:absolute;left:{x0 / S:g}px;top:{y0 / S:g}px;'
                    f'width:{(x1 - x0) / S:g}px;height:{(y1 - y0) / S:g}px">')
    new = (f'<img src="{rel_of(base)}" alt="" style="position:absolute;left:0;top:0;width:612px;height:792px">' + "".join(imgs))
    return page_html[:m.start()] + new + page_html[m.end():], area
