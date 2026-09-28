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
    nib, cone, edge = 1.30 * R, 3.3 * R, 0.95 * R          # v0.46: 뒤끝 거의 반구(0.60 -> 0.95R, 사진 펜슬처럼 -- 사용자) / v0.45: 사진 펜슬(Unsplash B)처럼 원뿔 짧게, 뒤끝 둥글게, 펜촉 보이게
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


SEAM_AMP, NIB_ALB = 0.6, 0.84   # 이음선 진하기·펜촉 밝기 -- Apple 원본 이음선 밝기 곡선과 RMS 4.7 (가장 어두운 점 193 vs 195)


def _real_profile(x, R, L):
    """Apple Pencil 윤곽 (v0.51) -- 사용자가 준 Apple Pencil Pro 제품 이미지에서 윤곽을 재어 비율만 쓴다(이미지·픽셀·로고는 쓰지 않는다).
    잰 값(바닥 그림자 없는 쪽 가장자리, 흰 배경 밝기 245 기준): 길이/지름 18.56(실제 규격 166/8.9 = 18.65).
    펜촉 끝은 둥근 캡(반지름 ~0.21R, 뭉툭), 거기서 u 0.105 까지 한 직선 원뿔(r/R = 0.17 + 7.6u), 0.105~0.125 에서 몸통에 붙음, 이음선 u 0.04, 뒤끝 반구.
    (v0.47~v0.50 은 짐작·무료 사진 자동 측정이라 틀렸다 -- 사용자)"""
    u = x / L
    a0, b0, cone_u, body_u = 0.17, 7.6, 0.105, 0.125                  # 원뿔 직선 r/R = a0 + b0·u (잰 점 u .01 .248 / .04 .49 / .10 .936)
    cone_r = a0 + b0 * cone_u
    r = np.full_like(x, R)
    m = u < cone_u
    r[m] = R * (a0 + b0 * u[m])                                     # 곧은 원뿔
    m = (u >= cone_u) & (u < body_u)                                  # 몸통에 붙기: 원뿔 기울기에서 0 으로 (3차 Hermite)
    t = (u[m] - cone_u) / (body_u - cone_u)
    m0 = b0 * (body_u - cone_u)
    r[m] = R * np.minimum(1.0, (2 * t ** 3 - 3 * t ** 2 + 1) * cone_r + (t ** 3 - 2 * t ** 2 + t) * m0 + (-2 * t ** 3 + 3 * t ** 2))
    rho = a0 * R / (1 - b0 * R / L)                                   # 펜촉 끝 = 원뿔 직선에 닿는 둥근 캡 (Apple 원본은 끝이 뭉툭 -- 바늘 끝 아님)
    k = x < rho
    r[k] = np.sqrt(np.clip(rho ** 2 - (rho - x[k]) ** 2, 0, None))
    xe = L - R                                                        # 뒤끝 반구
    m = x > xe
    r[m] = np.sqrt(np.clip(R ** 2 - (x[m] - xe) ** 2, 0, None))
    xs = 0.0525 * L                                                   # 펜촉-몸통 틈: 원본에서 잰 이음선 38.5px / 733 (4% 는 틀렸다)
    r *= 1 - 0.08 * np.exp(-((x - xs) / (0.0008 * L)) ** 2)        # 좁은 홈 (0.0022 는 뭉툭했다 -- 사용자)
    r[(x < 0) | (x > L)] = 0
    return r, xs, None


def _photo_profile(x, R, L):
    """무료 사진 펜슬(Unsplash B)의 실루엣을 길이 L 에 맞춘다 -- photo_devices_p3.pencil_silhouette"""
    import photo_devices_p3 as ph  # noqa: E402  (OpenCV -- 여기서만)
    u, rr, nib_u = ph.pencil_silhouette()
    r = R * np.interp(x / L, u, rr, left=0, right=0)
    r[(x < 0) | (x > L)] = 0
    return r, nib_u * L, None


def pencil_png(length, angle, light=(-0.35, -0.55, 0.76), ss=4, shadow=((1, 2, 2.0, 0.10), (4, 7, 9, 0.02)), tone=0.5, radius=None, silhouette="real", matte=True, gain=1.03):   # v0.51 밝기: Apple 원본 단면과 RMS 4.5 (tone .75 는 13 단계 어두웠다)   # v0.45: 그림자 크게 줄임, 아래 그늘 밝게 (사용자: 사진 펜슬이 시커멓다, 그림자 많이 제거)
    """length = 캔버스에서의 펜슬 길이(px), angle = 화면에서 반시계 회전(도), shadow = (닿는 그림자, 넓은 그림자) 각 (dx, dy, 흐림, 농도).
    tone = 음영 세기(1 = 계산 그대로, 0.75 = 그늘을 25% 밝게). radius = 몸통 반지름 px (없으면 실제 비율 length/37.3).
    반환: (RGBA 그림자 포함, 펜촉 끝 (x, y))"""
    R = (radius or length / 37.3) * ss
    L = length * ss
    W, H = int(L + 4 * ss), int(2 * R + 6 * ss)
    x = np.arange(W, dtype=np.float64)[None, :] - 2 * ss + 0.5
    y = np.arange(H, dtype=np.float64)[:, None] - H / 2 + 0.5
    r, nib_end, _ = {"real": _real_profile, "photo": _photo_profile}.get(silhouette, _profile)(x[0].copy(), R, L)   # v0.50: 실제 비율
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
    if matte:   # v0.49 무광 (사용자: 유광이라 촌스럽다) -- 반짝이는 줄 없음, 빛을 넓게 감싸 명암 폭을 줄인다. 펜촉만 아주 약한 광
        wrap = np.clip((ndl + 0.9) / 1.9, 0, 1)
        amb = 0.40 * (0.70 + 0.30 * nz)
        spec_p = np.where(tip > 0, 30.0, 4.0)
        spec_k = np.where(tip > 0, 0.08, 0.0)
    else:
        wrap = np.clip((ndl + 0.45) / 1.45, 0, 1)
        amb = 0.34 * (0.55 + 0.45 * nz)
        spec_p = np.where(tip > 0, 60.0, 14.0)
        spec_k = np.where(tip > 0, 0.30, 0.10)
    spec = spec_k * np.clip(n @ Hh, 0, 1) ** spec_p
    rim = 0.0 if matte else 0.06 * (1 - nz) ** 3                          # 가장자리 반사광(바닥 빛) -- 무광은 없음
    I = amb + (0.62 if matte else 0.70) * wrap + spec + rim
    albedo = np.where(tip[..., None] > 0, [NIB_ALB, NIB_ALB + .005, NIB_ALB + .01], [0.965, 0.965, 0.958])   # 펜촉 흰색, 몸통보다 살짝 어둡게
    col = albedo * I[..., None]
    col = col * [0.985, 0.99, 1.0] + (1 - I[..., None]) * 0.0          # 그늘이 아주 약간 차갑게
    # 펜촉-원뿔 이음매: 가는 틈
    seam = np.exp(-((x - nib_end) / (0.0008 * L)) ** 2) * SEAM_AMP   # 원본 이음선: 주변보다 약 21 단계 어둡고 폭 1~1.5px
    col *= (1 - seam)[..., None]
    col = 1 - (1 - np.clip(col * gain, 0, 1)) * tone
    col = np.clip(col, 0, 1) ** (1 / 1.08)
    rgba = np.dstack([col * 255, inside * 255.0]).astype(np.uint8)
    # 줄이기·돌리기는 premultiplied(RGBa)로 -- 곧은 알파로 하면 투명한 가장자리 색이 섞여 윤곽에 흰 점선이 생겼다(v0.49 확대 검수)
    # LANCZOS 는 날카로운 윤곽에 밝은 테두리(링잉)를 만들고 돌리면 점선이 됐다 -> 면적 평균(BOX)
    im = Image.fromarray(rgba, "RGBA").convert("RGBa").resize((W // ss, H // ss), Image.BOX)
    tip_xy = np.array([2.0, im.height / 2])                                # 돌리기 전 펜촉 끝
    # 돌리고 그림자 -- 빛이 왼쪽 위라 그림자는 오른쪽 아래
    pad = 90
    big = Image.new("RGBa", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    big.paste(im, (pad, pad))
    c = np.array(big.size) / 2
    rot = big.rotate(angle, resample=Image.BILINEAR, expand=True).convert("RGBA")
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
# v0.50: 상품 1 리스팅 패드와 같게 (scripts/build_mockups.py .tab) -- 단색 짙은 베젤 #2B2A33, 둥근 모서리, 부드러운 그림자 한 겹.
# 알루미늄 띠(회색 선)·카메라·유리 반사 없음 (사용자: 원복하랬더니 테두리에 회색 선, 상품 1 패드 모양으로).
# 상품 1: 베젤 26px / 화면 폭 885px(2.9%), 바깥 모서리 56px(6.3%), 화면 모서리 30px(3.4%), 그림자 0 40px 90px .18 (화면 높이 1180 기준)
ALU = "#2B2A33"
IPAD_SHADOW = "0 27px 60px rgba(0,0,0,.18)"
SHEEN = "none"
GLASS = "#2B2A33"
GLASS_EDGE = "none"
CAM = "transparent"
IPAD_CSS = f"""
.ipad{{position:absolute;box-sizing:border-box;background:{ALU};box-shadow:{IPAD_SHADOW}}}
.ipad .glass{{position:absolute;background:{GLASS};box-shadow:{GLASS_EDGE}}}
.ipad .cam{{position:absolute;border-radius:50%;background:{CAM}}}
.ipad .scr{{position:absolute;overflow:hidden;background-size:cover;background-position:center}}
.ipad .scr::after{{content:"";position:absolute;inset:0;background:{SHEEN}}}
"""

def ipad(src, w, left, top, rot=0, z=1):
    """w = 화면 폭(px), 화면 3:4. 상품 1 패드 비율 -- 베젤 = 화면 폭의 2.9%, 바깥 모서리 6.3%, 화면 모서리 3.4%"""
    h = round(w * 4 / 3)
    rim, bz = 0, round(w * .029)                                  # 상품 1 비율: 베젤 = 화면 폭의 2.9%
    W, Hh = w + 2 * (rim + bz), h + 2 * (rim + bz)
    R = round(w * .063)
    cam = max(6, round(w * .012))
    return (f'<div class="ipad" style="left:{left}px;top:{top}px;width:{W}px;height:{Hh}px;border-radius:{R}px;transform:rotate({rot}deg);z-index:{z}">'
            f'<div class="glass" style="inset:{rim}px;border-radius:{R - rim}px"></div>'
            f'<div class="cam" style="left:{W / 2 - cam / 2:.1f}px;top:{rim + bz / 2 - cam / 2:.1f}px;width:{cam}px;height:{cam}px"></div>'
            f'<div class="scr" style="left:{rim + bz}px;top:{rim + bz}px;width:{w}px;height:{h}px;border-radius:{round(w * .034)}px;background-image:url({src})"></div></div>')
