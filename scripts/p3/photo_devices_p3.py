# -*- coding: utf-8 -*-
"""상품 3 리스팅 01 -- 실제 사진(Unsplash, 무료 라이선스)에서 iPad·Apple Pencil 을 오려 우리 바탕에 놓는다. Prod 3 방 소유.

2026-09-28 사용자: 코드로 그린 기기(devices_p3.py)는 사진처럼 안 된다 -> 무료 사진 두 장을 받아 "머징",
펜슬은 오려서 우리 바탕 위에. 사진·라이선스는 `assets/p3/unsplash/README.md`.

    from photo_devices_p3 import ipad_photo, pencil_photo
    ipad_photo("A", page_png)        # -> PIL RGBA: 사진 속 iPad(테두리·베젤 그대로), 화면 = 우리 페이지
    pencil_photo(600, 62)            # -> (PIL RGBA, 펜촉 끝 (x, y)) 길이 px, 펜촉->뒤끝 방향이 화면에서 반시계 angle 도

A = 회색 쿠션 사진(은색 알루미늄 테두리가 보인다), B = 나무 책상 사진(펜슬이 가장 깨끗하게 오려진다).
오려낸 뒤 사진의 따뜻한 색보정을 빼고(채도 줄임) 우리 바탕 톤에 맞춘다. 그림자는 여기서 넣지 않는다(CSS 에서 얇게).
"""
import math
import pathlib

import cv2
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
PHOTO = {"A": ROOT / "assets/p3/unsplash/unsplash-ipgtlzD86O4-1920.jpg",
         "B": ROOT / "assets/p3/unsplash/unsplash-FvhyAFRE414-1920.jpg"}


def _load(k):
    return cv2.imread(str(PHOTO[k]))                           # BGR


def _largest(mask):
    n, lab, st, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8))
    if n < 2:
        raise RuntimeError("오려낼 덩어리를 못 찾았다")
    i = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    return lab == i


def _neutral(bgr, keep_sat=0.25, lift=1.0):
    """사진 색보정(따뜻한·녹색 기운)을 뺀다: 채도를 keep_sat 배로, 밝기 lift 배"""
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] *= keep_sat
    hsv[..., 2] = np.clip(hsv[..., 2] * lift, 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


def _screen_quad(img):
    """흰 화면 = 가장 큰 밝은 덩어리 -> 네 꼭짓점(왼위, 오위, 오아래, 왼아래)"""
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = g.shape
    roi = g[h // 5: h * 4 // 5, w // 6: w * 5 // 6]
    t = np.percentile(roi, 97) * 0.80
    m = _largest(g > t)
    cnt, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    box = cv2.boxPoints(cv2.minAreaRect(max(cnt, key=cv2.contourArea)))
    s, d = box.sum(1), np.diff(box, axis=1)[:, 0]
    return np.array([box[np.argmin(s)], box[np.argmin(d)], box[np.argmax(s)], box[np.argmax(d)]], np.float32), m


def _outer_offset(g, quad):
    """화면 가장자리에서 바깥으로 베젤(어두움, < 45)이 끝나는 곳까지 -- 네 변 × 30줄의 가운데값 + 은색 테두리 4px.
    쿠션 결이 밝았다 어두웠다 해서 GrabCut 이 베젤을 배경으로 봤다(첫 시도) -> 모양을 잰다"""
    x0, y0 = quad.min(0); x1, y1 = quad.max(0)
    runs = []
    for f in np.linspace(0.2, 0.8, 30):
        cy, cx = int(y0 + (y1 - y0) * f), int(x0 + (x1 - x0) * f)
        for line in (g[cy, int(x1) + 2:int(x1) + 120], g[cy, int(x0) - 120:int(x0) - 2][::-1],
                     g[int(y1) + 2:int(y1) + 120, cx], g[int(y0) - 120:int(y0) - 2, cx][::-1]):
            i = int(np.argmax(line > 45)) if (line > 45).any() else len(line)
            runs.append(i)
    return float(np.median(runs)) + 2 + 4


def _snap_to_bezel(g, quad):
    """밝기로 잡은 화면 사각형을 네 변마다 베젤(< 60)이 시작되는 곳까지 넓힌다 -- 사진 B 화면은 밝기가 고르지 않아
    가장자리가 덜 잡혀 사진 화면이 들쭉날쭉 보였다"""
    x0, y0 = quad.min(0); x1, y1 = quad.max(0)
    side = {"r": [], "l": [], "b": [], "t": []}
    for f in np.linspace(0.15, 0.85, 40):
        cy, cx = int(y0 + (y1 - y0) * f), int(x0 + (x1 - x0) * f)
        for k, line in (("r", g[cy, int(x1) - 30:int(x1) + 40]), ("l", g[cy, int(x0) - 40:int(x0) + 30][::-1]),
                        ("b", g[int(y1) - 30:int(y1) + 40, cx]), ("t", g[int(y0) - 40:int(y0) + 30, cx][::-1])):
            side[k].append(int(np.argmax(line < 60)) - 30 if (line < 60).any() else 0)
    d = {k: float(np.median(v)) for k, v in side.items()}
    q = quad.copy()
    q[[1, 2], 0] += d["r"]; q[[0, 3], 0] -= d["l"]; q[[2, 3], 1] += d["b"]; q[[0, 1], 1] -= d["t"]
    return q


def _rrect(shape, quad, pad, radius, ss=3):
    """quad(화면 원근)를 pad 만큼 넓힌 둥근 사각형 마스크 0~1 (안티앨리어스)"""
    W = float(np.linalg.norm(quad[1] - quad[0])); H = float(np.linalg.norm(quad[3] - quad[0]))
    cw, ch = int((W + 2 * pad) * ss), int((H + 2 * pad) * ss)
    can = np.zeros((ch, cw), np.uint8)
    r = max(1, int(radius * ss))
    cv2.rectangle(can, (r, 0), (cw - r, ch), 255, -1); cv2.rectangle(can, (0, r), (cw, ch - r), 255, -1)
    for cx, cy in ((r, r), (cw - r, r), (cw - r, ch - r), (r, ch - r)):
        cv2.circle(can, (cx, cy), r, 255, -1, lineType=cv2.LINE_AA)
    src = np.float32([[pad * ss, pad * ss], [(W + pad) * ss, pad * ss], [(W + pad) * ss, (H + pad) * ss], [pad * ss, (H + pad) * ss]])
    m = cv2.warpPerspective(can, cv2.getPerspectiveTransform(src, quad), (shape[1], shape[0]), flags=cv2.INTER_AREA)
    return m.astype(np.float32) / 255


def _screen_radius(mask, quad):
    """화면 모서리 반지름 -- 왼쪽 위 꼭짓점에서 대각선 안쪽으로 첫 화면 점까지 d, r = d / (√2 - 1)"""
    x, y = quad[0]
    for d in range(0, 200):
        if mask[int(y + d / 1.414), int(x + d / 1.414)]:
            return d / (1.414 - 1) * 0.707
    return 30.0


def _device_mask(img, quad, rs):
    """iPad 몸통 = 화면 사각형을 베젤만큼 넓힌 둥근 사각형 (화면 원근 그대로)"""
    o = _outer_offset(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), quad)
    return _rrect(img.shape, quad, o, rs + o)


def ipad_photo(k, page_png, light=0.35):
    """사진 k 의 iPad 를 오려 화면에 우리 페이지를 넣는다. light = 사진 화면의 밝기 얼룩을 페이지에 얼마나 남길지(자연스러움)"""
    img = _load(k)
    quad0, scr_mask = _screen_quad(img)
    g0 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rs = _screen_radius(scr_mask, quad0)
    quad = _snap_to_bezel(g0, quad0)
    alpha = _device_mask(img, quad, rs)
    body = _neutral(img, keep_sat=0.15)
    # 페이지를 화면 사각형에 원근 변환
    page = cv2.cvtColor(np.asarray(Image.open(page_png).convert("RGB")), cv2.COLOR_RGB2BGR)
    ph, pw = page.shape[:2]
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [pw, 0], [pw, ph], [0, ph]]), quad)
    warped = cv2.warpPerspective(page, M, (img.shape[1], img.shape[0]), flags=cv2.INTER_AREA)
    sm = _rrect(img.shape, quad, 0, rs)                          # 화면 = 둥근 사각형 (사진 밝기 덩어리는 가장자리가 들쭉날쭉)
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    shade = g / max(1, np.percentile(g[scr_mask], 95))          # 화면 빛 얼룩(가장자리 어두움 등)
    shade = 1 - light * (1 - np.clip(shade, 0, 1))
    comp = warped.astype(np.float32) * shade[..., None]
    out = body.astype(np.float32) * (1 - sm[..., None]) + comp * sm[..., None]
    x, y, w, h = cv2.boundingRect((alpha > 0.02).astype(np.uint8))
    rgba = np.dstack([cv2.cvtColor(np.clip(out, 0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB), (alpha * 255).astype(np.uint8)])[y:y + h, x:x + w]
    return Image.fromarray(rgba, "RGBA")


def pencil_photo(length, angle):
    """사진 B 의 펜슬을 오린다. 길이 length px, 펜촉->뒤끝 방향이 화면에서 반시계 angle 도(0 = 오른쪽). 반환: (RGBA, 펜촉 끝 (x, y))"""
    img = _load("B")
    x0, y0, x1, y1 = 150, 1040, 520, 1990                       # 펜슬 둘레 (사진 B, 1920 기준)
    roi = img[y0:y1, x0:x1]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV).astype(int)
    like = (hsv[..., 1] < 60) & (hsv[..., 2] > 110)             # 흰 펜슬 vs 갈색 나무(채도 높음)·틈(어두움)
    m0 = _largest(cv2.morphologyEx(like.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)))
    ys, xs = np.nonzero(m0)
    pts = np.stack([xs, ys], 1).astype(np.float32)
    c = pts.mean(0)
    ax = np.linalg.svd(pts - c, full_matrices=False)[2][0]     # 펜슬 축
    nrm = np.array([-ax[1], ax[0]])
    proj = (pts - c) @ ax
    # 축을 따라 1px 마다: 가운데에서 양옆으로 "펜슬다운" 점이 이어지는 폭 -> 가운데값으로 매끈하게 -> 윤곽 다각형
    left, right, ts = [], [], np.arange(int(proj.min()), int(proj.max()) + 1)
    h, w = like.shape
    for t in ts:
        p0 = c + ax * t
        ext = []
        for sgn in (-1, 1):
            k = 0
            while k < 60:
                q = p0 + nrm * sgn * (k + 1)
                xi, yi = int(round(q[0])), int(round(q[1]))
                if not (0 <= xi < w and 0 <= yi < h) or not like[yi, xi]:
                    break
                k += 1
            ext.append(k)
        left.append(ext[0]); right.append(ext[1])
    def med(v, k=21):
        v = np.pad(np.array(v, float), k // 2, mode="edge")
        return np.median(np.lib.stride_tricks.sliding_window_view(v, k), axis=1)
    lw, rw = med(left), med(right)
    ok = (lw + rw) > 4
    ts, lw, rw = ts[ok], lw[ok], rw[ok]
    poly = [c + ax * t - nrm * l for t, l in zip(ts, lw)] + [c + ax * t + nrm * r for t, r in zip(ts[::-1], rw[::-1])]
    ss = 3
    can = np.zeros((h * ss, w * ss), np.uint8)
    cv2.fillPoly(can, [np.round(np.array(poly) * ss).astype(np.int32)], 255, lineType=cv2.LINE_AA)
    a = cv2.resize(can, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    a = cv2.erode(a, np.ones((2, 2), np.uint8))                 # 가장자리 나무색 1px 빼기
    e0, e1 = c + ax * ts[0], c + ax * ts[-1]
    tip, end = (e0, e1) if e0[1] < e1[1] else (e1, e0)          # 펜촉 = 위쪽 끝 (사진 B)
    body = _neutral(roi, keep_sat=0.12, lift=1.10)
    rgba = np.dstack([cv2.cvtColor(body, cv2.COLOR_BGR2RGB), (np.clip(a, 0, 1) * 255).astype(np.uint8)])
    im = Image.fromarray(rgba, "RGBA")
    # 크기: 펜촉~뒤끝 길이를 length 로
    L = float(np.linalg.norm(end - tip))
    sc = length / L
    im = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
    tip, end = tip * sc, end * sc
    # 회전: 지금 펜촉->뒤끝 방향(화면, 반시계 +) -> angle
    cur = math.degrees(math.atan2(-(end[1] - tip[1]), end[0] - tip[0]))
    rot = angle - cur
    pad = 40
    big = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    big.paste(im, (pad, pad))
    cxy = np.array(big.size) / 2
    out = big.rotate(rot, resample=Image.BICUBIC, expand=True)
    r = -math.radians(rot)
    v = tip + pad - cxy
    t = np.array([v[0] * math.cos(r) - v[1] * math.sin(r), v[0] * math.sin(r) + v[1] * math.cos(r)]) + np.array(out.size) / 2
    return out, (float(t[0]), float(t[1]))


def pencil_silhouette():
    """사진 B 펜슬의 실루엣 -- 펜촉(u=0) -> 뒤끝(u=1) 을 따라 굵기 / 몸통 굵기. 반환 (u, 비율, 펜촉 끝 u).
    devices_p3.pencil_png 가 이 윤곽으로 3D 펜슬을 그린다 (사용자 2026-09-28: 촉이 더 뾰족해야, 실루엣은 무료 사진 펜슬 따라).
    사진의 그늘진 쪽은 밝기 기준에서 빠져 굵기가 덜 재진다 -> 절대 굵기는 쓰지 않고 몸통 대비 비율만 쓴다."""
    img = _load("B")
    x0, y0, x1, y1 = 150, 1040, 520, 1990
    hsv = cv2.cvtColor(img[y0:y1, x0:x1], cv2.COLOR_BGR2HSV).astype(int)
    like = (hsv[..., 1] < 60) & (hsv[..., 2] > 110)
    m0 = _largest(cv2.morphologyEx(like.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)))
    ys, xs = np.nonzero(m0)
    pts = np.stack([xs, ys], 1).astype(np.float32)
    c = pts.mean(0)
    ax = np.linalg.svd(pts - c, full_matrices=False)[2][0]
    if ax[1] > 0:
        ax = -ax                                                 # 위쪽(펜촉)을 향하게
    nrm = np.array([-ax[1], ax[0]])
    proj = (pts - c) @ ax
    ts = np.arange(int(proj.max()), int(proj.min()) - 1, -1)    # 펜촉 -> 뒤끝
    h, w = like.shape
    wid, val = [], []
    for t in ts:
        p0 = c + ax * t
        n = 0
        for sgn in (-1, 1):
            k = 0
            while k < 60:
                q = p0 + nrm * sgn * (k + 1)
                xi, yi = int(round(q[0])), int(round(q[1]))
                if not (0 <= xi < w and 0 <= yi < h) or not like[yi, xi]:
                    break
                k += 1
            n += k
        wid.append(n)
        xi, yi = int(round(p0[0])), int(round(p0[1]))
        val.append(hsv[yi, xi, 2] if 0 <= xi < w and 0 <= yi < h else 0)
    wid = np.array(wid, float)
    k = 5
    wid = np.median(np.lib.stride_tricks.sliding_window_view(np.pad(wid, k // 2, mode="edge"), k), axis=1)
    L = len(wid)
    u = np.arange(L) / (L - 1)
    body = np.median(wid[int(L * .2):int(L * .9)])
    r = np.clip(wid / body, 0, 1)
    head, tail = u < 0.12, u > 0.9
    r[head] = np.maximum.accumulate(r[head])                   # 펜촉 쪽은 굵어지기만, 뒤끝 쪽은 가늘어지기만 (재는 잡음 제거)
    r[tail] = np.maximum.accumulate(r[tail][::-1])[::-1]
    r[(u >= 0.12) & (u <= 0.9)] = 1.0
    # 1px 단위로 잰 굵기라 계단이 진다(3D 로 그리면 고리처럼 보였다) -> 가우시안으로 부드럽게 이음
    g = np.exp(-0.5 * (np.arange(-12, 13) / 4.0) ** 2); g /= g.sum()
    r = np.convolve(np.pad(r, 12, mode="edge"), g, mode="valid")
    r[(u >= 0.15) & (u <= 0.88)] = 1.0
    r[0] = r[-1] = 0.0                                          # 양 끝을 닫는다 (뒤끝이 납작하게 잘려 보였다)
    nib_u = float(u[int(np.argmax(np.array(val[2:]) > 170)) + 2])   # 펜촉(회색) -> 원뿔(흰색) 밝기가 뛰는 곳
    return u, r, nib_u
