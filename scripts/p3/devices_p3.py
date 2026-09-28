# -*- coding: utf-8 -*-
"""상품 3 리스팅 소품 -- 사진처럼 보이는 Apple Pencil(3D 음영 계산)과 iPad 틀(CSS). Prod 3 방 소유.

2026-09-28 사용자: SVG 도형 펜슬이 "너무 구리다 -- 진짜 사진 찍은 것처럼", iPad 테두리도 진짜처럼.
펜슬은 도형을 겹치지 않고 회전체(반지름 프로필 r(x))의 표면 법선을 픽셀마다 구해 조명을 계산한다.
비율은 Apple Pencil 2세대 공개값: 길이 166mm, 지름 8.9mm(길이/반지름 = 37.3). 자석 평면은 넣지 않는다 --
위에서 찍은 사진에선 거의 안 보이는데 넣으면 어두운 띠가 생겼다(시안 첫 렌더).
사진·로고는 쓰지 않는다(외부 이미지 없음, 상표 없음).

    from devices_p3 import pencil_png, IPAD_CSS, ipad
    img, tip = pencil_png(620, 62)       # PIL RGBA(그림자 포함), tip = 그림 안 펜촉 끝 좌표(px). angle 은 PIL 처럼 반시계가 + (CSS rotate 와 반대)
"""
import math

import numpy as np
from PIL import Image, ImageFilter

# ---------------------------------------------------------------- Apple Pencil


def _profile(x, R, L):
    """펜촉 끝 x=0 에서 뒤끝 x=L 까지의 반지름. 펜촉(둥근 끝) -> 원뿔(몸통에 접선으로 이어짐) -> 몸통 -> 둥근 모서리 뒤끝"""
    nib, cone, edge = 1.30 * R, 3.3 * R, 0.60 * R          # v0.45: 사진 펜슬(Unsplash B)처럼 원뿔 짧게, 뒤끝 둥글게, 펜촉 보이게
    rn0, rn1 = 0.18 * R, 0.38 * R
    r = np.full_like(x, R)
    t = x / nib
    m = x < nib
    r[m] = rn0 + (rn1 - rn0) * np.clip(t[m], 0, 1) ** 0.75
    cap = x < rn0                                                   # 펜촉 끝 반구
    r[cap] = np.sqrt(np.clip(rn0 ** 2 - (rn0 - x[cap]) ** 2, 0, None))
    t = (x - nib) / cone
    m = (x >= nib) & (x < nib + cone)
    r[m] = rn1 + (R - rn1) * (1 - (1 - t[m]) ** 2)                  # 몸통 쪽에서 접선 -- 이음매 없이
    xe = L - edge
    m = x > xe
    r[m] = R - edge + np.sqrt(np.clip(edge ** 2 - (x[m] - xe) ** 2, 0, None))
    r[x > L] = 0
    return r, nib, nib + cone


def pencil_png(length, angle, light=(-0.35, -0.55, 0.76), ss=4, shadow=((1, 2, 2.0, 0.10), (4, 7, 9, 0.02)), tone=0.75):   # v0.45: 그림자 크게 줄임, 아래 그늘 밝게 (사용자: 사진 펜슬이 시커멓다, 그림자 많이 제거)
    """length = 캔버스에서의 펜슬 길이(px), angle = 화면에서 반시계 회전(도), shadow = (닿는 그림자, 넓은 그림자) 각 (dx, dy, 흐림, 농도).
    tone = 음영 세기(1 = 계산 그대로, 0.75 = 그늘을 25% 밝게).
    반환: (RGBA 그림자 포함, 펜촉 끝 (x, y))"""
    R = length / 37.3 * ss
    L = length * ss
    W, H = int(L + 4 * ss), int(2 * R + 6 * ss)
    x = np.arange(W, dtype=np.float64)[None, :] - 2 * ss + 0.5
    y = np.arange(H, dtype=np.float64)[:, None] - H / 2 + 0.5
    r, nib_end, _ = _profile(x[0].copy(), R, L)
    dr = np.gradient(r)
    r, dr = r[None, :], dr[None, :]
    inside = (y ** 2 <= r ** 2) & (r > 0)
    z = np.sqrt(np.clip(r ** 2 - y ** 2, 0, None))
    n = np.stack([-r * dr * np.ones_like(y), y * np.ones_like(x), z], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True) + 1e-9
    # 조명을 펜슬 좌표로 -- 화면에서 반시계 angle 도 돌아가므로 월드 빛을 거꾸로 돌린다
    a = math.radians(angle)
    ex, ey = np.array([math.cos(a), -math.sin(a)]), np.array([math.sin(a), math.cos(a)])
    Lw = np.array(light[:2]); Lz = light[2]
    Lv = np.array([Lw @ ex, Lw @ ey, Lz]); Lv /= np.linalg.norm(Lv)
    V = np.array([0, 0, 1.0]); Hh = (Lv + V) / np.linalg.norm(Lv + V)
    ndl = n @ Lv
    nz = n[..., 2]
    tip = (x < nib_end) * np.ones_like(y)
    # 무광 흰 플라스틱: 감싸는 확산광 + 하늘 앰비언트 + 넓은 약한 반사. 펜촉은 살짝 회색·더 반질
    wrap = np.clip((ndl + 0.45) / 1.45, 0, 1)
    amb = 0.34 * (0.55 + 0.45 * nz)
    spec_p = np.where(tip > 0, 60.0, 14.0)
    spec_k = np.where(tip > 0, 0.30, 0.10)
    spec = spec_k * np.clip(n @ Hh, 0, 1) ** spec_p
    rim = 0.06 * (1 - nz) ** 3                                           # 가장자리 반사광(바닥 빛)
    I = amb + 0.70 * wrap + spec + rim
    albedo = np.where(tip[..., None] > 0, [0.80, 0.805, 0.815], [0.965, 0.965, 0.958])
    col = albedo * I[..., None]
    col = col * [0.985, 0.99, 1.0] + (1 - I[..., None]) * 0.0          # 그늘이 아주 약간 차갑게
    # 펜촉-원뿔 이음매: 가는 틈
    seam = np.exp(-((x - nib_end) / (0.9 * ss)) ** 2) * 0.22
    col *= (1 - seam)[..., None]
    col = 1 - (1 - np.clip(col, 0, 1)) * tone
    col = np.clip(col, 0, 1) ** (1 / 1.08)
    rgba = np.dstack([col * 255, inside * 255.0]).astype(np.uint8)
    im = Image.fromarray(rgba, "RGBA").resize((W // ss, H // ss), Image.LANCZOS)
    tip_xy = np.array([2.0, im.height / 2])                                # 돌리기 전 펜촉 끝
    # 돌리고 그림자 -- 빛이 왼쪽 위라 그림자는 오른쪽 아래
    pad = 90
    big = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    big.paste(im, (pad, pad))
    c = np.array(big.size) / 2
    rot = big.rotate(angle, resample=Image.BICUBIC, expand=True)
    a_ = -math.radians(angle)
    v = tip_xy + pad - c
    tip_rot = np.array([v[0] * math.cos(a_) - v[1] * math.sin(a_), v[0] * math.sin(a_) + v[1] * math.cos(a_)]) + np.array(rot.size) / 2
    A = rot.split()[3]

    def drop(dx, dy, blur, op):
        s = Image.new("L", rot.size, 0)
        s.paste(A, (dx, dy))
        s = s.filter(ImageFilter.GaussianBlur(blur))
        return np.asarray(s, np.float64) / 255 * op

    (c_dx, c_dy, c_b, c_o), (w_dx, w_dy, w_b, w_o) = shadow
    sh = 1 - (1 - drop(c_dx, c_dy, c_b, c_o)) * (1 - drop(w_dx, w_dy, w_b, w_o))   # 닿는 그림자 + 넓은 그림자
    out = np.zeros((rot.size[1], rot.size[0], 4))
    out[..., :3] = [38, 32, 26]
    out[..., 3] = sh
    fg = np.asarray(rot, np.float64) / 255
    fa = fg[..., 3:4]
    rgb = fg[..., :3] * 255 * fa + out[..., :3] * out[..., 3:4] * (1 - fa)
    alpha = fa + out[..., 3:4] * (1 - fa)
    rgb = np.where(alpha > 0, rgb / np.maximum(alpha, 1e-6), 0)
    res = Image.fromarray(np.dstack([rgb, alpha * 255]).clip(0, 255).astype(np.uint8), "RGBA")
    return res, (float(tip_rot[0]), float(tip_rot[1]))


# ---------------------------------------------------------------- iPad (CSS)
# 알루미늄 테두리(스페이스 그레이, 왼쪽 위 빛) -> 검은 유리 베젤 -> 화면. 화면 위 유리 반사, 그림자 네 겹.
# v0.45: 처음 그린 v0.41 값으로 되돌림 (사용자: "패드는 원래 처음 그렸던 걸로"). v0.43 의 옅은 값은 git 커밋 4224195.
ALU = "linear-gradient(145deg,#8d8f93 0%,#55575b 9%,#35363a 30%,#2a2b2e 62%,#46484c 88%,#6c6e72 100%)"
IPAD_SHADOW = "0 1px 1px rgba(0,0,0,.45),0 3px 5px rgba(20,22,26,.30),0 16px 30px rgba(20,25,30,.24),0 44px 80px rgba(20,25,30,.22)"
SHEEN = "linear-gradient(118deg,rgba(255,255,255,.10) 0%,rgba(255,255,255,.035) 38%,rgba(255,255,255,0) 38.2%,rgba(255,255,255,0) 100%)"
GLASS = "#0c0c0e"
GLASS_EDGE = "inset 0 0 0 1px rgba(255,255,255,.07),inset 0 1px 0 rgba(255,255,255,.10)"
CAM = "radial-gradient(circle at 38% 35%,#3b4a5c 0%,#161a22 45%,#060607 70%)"
IPAD_CSS = f"""
.ipad{{position:absolute;box-sizing:border-box;background:{ALU};box-shadow:{IPAD_SHADOW}}}
.ipad .glass{{position:absolute;background:{GLASS};box-shadow:{GLASS_EDGE}}}
.ipad .cam{{position:absolute;border-radius:50%;background:{CAM}}}
.ipad .scr{{position:absolute;overflow:hidden;background-size:cover;background-position:center}}
.ipad .scr::after{{content:"";position:absolute;inset:0;background:{SHEEN}}}
"""

def ipad(src, w, left, top, rot=0, z=1):
    """w = 화면 폭(px), 화면 3:4. 테두리 = 알루미늄 띠(폭의 1.1%) + 유리 베젤(폭의 4%)"""
    h = round(w * 4 / 3)
    rim, bz = max(4, round(w * .011)), round(w * .040)
    W, Hh = w + 2 * (rim + bz), h + 2 * (rim + bz)
    R = round(w * .085)
    cam = max(6, round(w * .012))
    return (f'<div class="ipad" style="left:{left}px;top:{top}px;width:{W}px;height:{Hh}px;border-radius:{R}px;transform:rotate({rot}deg);z-index:{z}">'
            f'<div class="glass" style="inset:{rim}px;border-radius:{R - rim}px"></div>'
            f'<div class="cam" style="left:{W / 2 - cam / 2:.1f}px;top:{rim + bz / 2 - cam / 2:.1f}px;width:{cam}px;height:{cam}px"></div>'
            f'<div class="scr" style="left:{rim + bz}px;top:{rim + bz}px;width:{w}px;height:{h}px;border-radius:{round(w * .045)}px;background-image:url({src})"></div></div>')
