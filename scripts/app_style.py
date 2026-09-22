# -*- coding: utf-8 -*-
"""앱 UI 풍(유리) 스타일. 상품 2 (v9-student) 전용.

`build_planner.py` 는 `T["app"]` 가 켜진 테마에서만 이 모듈을 쓴다.
v1~v8 은 이 파일을 아예 불러오지 않으므로 출력이 변하지 않는다.

여기 있는 것:
  · 레이아웃 상수 (레일 / 섹션 / 본문 폭)  -- 숫자가 사는 유일한 곳
  · dline()  -- 점선 생성기. 세로·가로·괘선 전부 이 함수 하나가 만든다
  · CSS      -- 내지(라이트) + 표지·목차(다크)
  · bake()   -- 배경 PNG 한 장. 전 페이지가 같은 파일을 참조한다

2026-09-22 에 여기 값들을 정하며 겪은 것은 `product2-student.md` 에 있다.
특히 "점선 주기와 줄 간격은 4의 배수 pt" 규칙은 이유를 모르면 되돌리기
쉬우니 고치기 전에 그 절을 읽을 것.
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# ----------------------------------------------------------------- 레이아웃
# 페이지는 612x792pt. 아래 다섯 값에서 나머지가 전부 파생된다.
SHEET = 6.75              # 내지 바깥으로 보이는 표지 띠 (사방 동일)
RAIL_L = 13.0             # 탭 레일 왼쪽 여백 (위아래도 같은 값)
RAIL_W = 40.0             # 탭 레일 폭
RAIL_PAD = 4.0            # .rail 의 padding. 선택 알약은 이만큼 안쪽에서 끝난다
CONTENT_R = 28.0          # 섹션 오른쪽 여백

PAGE_W, PAGE_H = 612.0, 792.0

# 선택된 탭의 알약 오른쪽 끝 ~ 섹션 왼쪽 간격을
# 섹션 오른쪽 ~ 내지 오른쪽 간격과 같게 맞춘다.
SIDE_GAP = (PAGE_W - SHEET) - (PAGE_W - CONTENT_R)      # 21.25pt
RAIL_GAP = SIDE_GAP - RAIL_PAD
CONTENT_L = RAIL_L + RAIL_W + RAIL_GAP                  # 70.25pt
CW = PAGE_W - CONTENT_L - CONTENT_R                     # 본문 폭
RAIL_R = RAIL_L + RAIL_W                                # 레일 오른쪽 끝

# ------------------------------------------------------------------- 점선
# 전부 고정 pt. % 나 calc 는 인쇄 경로에서 칸마다 다른 결과를 낸다.
C = "#d3d8de"
DASH = 4.0                # 선분
PERIOD = 8.0              # 선분 + 틈
# 주기와 줄 간격은 반드시 4의 배수 pt. 뷰어는 pt x 배율을 픽셀에 맞춰
# 자르는데, 6.75pt 주기는 1.5/2/2.5/3배 어디서도 정수가 아니라 점이
# 4px/5px 로 갈렸다. 파일 안 기하는 완벽한데 화면만 깨지는 종류의 결함이다.
FADE = 3 * PERIOD         # 양 끝 페이드. 주기보다 짧으면 아예 안 보인다
INSET = 8.0               # 가로선을 칸 좌우에서 띄우는 거리
INSET_V = 2.0             # 세로선을 칸 위아래에서 띄우는 거리
ROW_H = 24.0              # 표/괘선 한 줄 높이
THICK = "1px"             # = 0.75pt


def split(total, n, fixed=()):
    """total 을 n 칸으로. 반올림 오차는 마지막 칸이 흡수한다."""
    rest = total - sum(fixed)
    w = [round(v, 2) for v in fixed] + [round(rest / (n - len(fixed)), 2)] * (
        n - len(fixed) - 1)
    return w + [round(total - sum(w), 2)]


def prop(total, parts):
    """비율을 유지한 채 현재 본문 폭에 맞춘 pt 폭 목록."""
    w = [round(p * total / sum(parts), 2) for p in parts[:-1]]
    return w + [round(total - sum(w), 2)]


def dline(sel, axis, length, box):
    """점선 하나. 길이(pt)를 받아 페이드 길이까지 같이 계산한다.

    세 곳에 손으로 복사돼 있던 것을 여기로 모았다. 열 폭이 바뀌면 페이드도
    같이 바뀌어야 하는데 복사본은 그걸 따라오지 못했다.
    """
    d = "right" if axis == "x" else "bottom"
    f = min(FADE, length / 3.0)
    g = ("linear-gradient(to %s,transparent,#000 %.2fpt,"
         "#000 %.2fpt,transparent)" % (d, f, length - f))
    return "".join([
        "%s{" % sel,
        'content:"";position:absolute;%s;pointer-events:none;' % box,
        "background-image:repeating-linear-gradient(to %s,%s 0,%s %.2fpt,"
        "transparent %.2fpt,transparent %.2fpt);" % (d, C, C, DASH, DASH, PERIOD),
        "-webkit-mask-image:%s;" % g,
        "mask-image:%s}" % g,
    ])


HBOX = "left:%.2fpt;right:%.2fpt;bottom:0;height:%s" % (INSET, INSET, THICK)
VBOX = "top:%.2fpt;bottom:%.2fpt;right:0;width:%s" % (INSET_V, INSET_V, THICK)


def table_cols(name, widths):
    """표 한 종류의 가로 구분선. 열 수가 다르면 반드시 따로 만들어야 한다 --
    4열에 맞춰 두고 6열 시간표를 돌렸다가 THU/FRI 에 선이 없었다."""
    return "".join(
        dline(".tb.%s tr:not(:last-child) td:nth-child(%d)::before" % (name, i),
              "x", w - 2 * INSET, HBOX)
        for i, w in enumerate(widths, 1))


# 표 종류. 열 폭은 본문 폭에서 비율로 계산한다(손으로 적지 않는다).
T4 = prop(CW, [220, 120, 100, 60])          # 과제/할 일 4열
T6 = split(CW, 6, fixed=(60.0,))            # 시간표: 시각 열 60pt + 요일 5


BASE = """
/* 배경: 표지 한 장을 전 페이지가 공유한다. 페이지마다 그라데이션을 깔면
   페이지당 3초씩 걸려 뷰어에서 스크롤이 멈춘다(실측 2,973ms vs 49ms). */
.bgimg{position:absolute;inset:0;background-size:cover;pointer-events:none;
       z-index:0}
.content{z-index:2}
.rail{z-index:3;border-right:none;height:auto}
.page{background:#17133E !important}
h1{color:#241E3A}
.eyebrow{color:#4A4260}
.sub{color:#5B5375}
.label{color:#2B2540;margin-bottom:9pt}
.card{background:none;border:none;padding:0 0 6pt}
.card::after{display:none}
.body{gap:20pt}

/* 유리 -- 필기면·표·선택 탭이 전부 같은 재질이어야 한다.
   흰 테두리(0.7pt)를 줬더니 2px 짜리 흰 선으로 보여서 뺐다. 경계는
   그림자가 맡는다. */
.field, .lines, .tbwrap{position:relative;border-radius:13pt;
    background:rgba(255,255,255,.55);border:none;
    box-shadow:0 1.5pt 9pt rgba(40,28,90,.16)}
.tbwrap{overflow:hidden}
.tb{width:100%;border-collapse:separate;border-spacing:0;table-layout:fixed;
    background:transparent}
.tb td{height:@ROW@pt;padding:0 10pt;font-size:8.5pt;background:transparent;
    border:none;position:relative}
.tb tr:first-child td{height:21pt;font-size:6.6pt;letter-spacing:.14em;
    font-weight:800;color:#403A5C;text-align:center;
    background:rgba(232,227,247,.62)}
.tb .bx{text-align:center}
.tb .bx i{display:inline-block;width:10pt;height:10pt;border-radius:3pt;
    border:.9pt solid rgba(120,110,160,.42);background:rgba(255,255,255,.75)}

/* 괘선 면은 줄을 넉넉히 넣고 잘라 쓴다. 줄 높이가 고정이라 면 높이와 딱
   떨어지지 않는데, 줄 수를 면에 맞춰 세면 레이아웃이 조금만 바뀌어도
   아래쪽이 텅 빈다(줄 높이를 27->24pt 로 바꾸자 68pt 가 비었다). */
.lines{overflow:hidden;padding:0 @INSET@pt}
.lines>div{border:none;position:relative;flex:none;height:@ROW@pt}
/* 마지막 줄의 구분선은 뺀다. 면의 아래 가장자리와 맞닿아 테두리처럼
   보이고, 그 아래로는 쓸 칸이 없어 구분할 것도 없다. */
.lines>div:last-child::after{display:none}

/* 선택 탭 = 표지 카드와 같은 유리 레시피.
   불투명 흰 알약은 페이지에서 유일한 불투명 개체라 혼자 튀었다. */
.rail a.on{background:rgba(255,255,255,.09);
    border:.8pt solid rgba(255,255,255,.19);
    border-top-color:rgba(255,255,255,.34);box-shadow:none}
.rail a.on::before{display:none}
.rail a.on::after{display:none}
"""


DARK = """
/* 표지·목차. 색만 다르고 좌표는 라이트와 같은 값에서 나온다 --
   여기에 left/top/width 를 다시 적으면 표지만 어긋난다(실제로 겪음). */
.dk{background:#17133E !important}
.dk .rail{border-right-color:rgba(255,255,255,.10);height:auto}
.dk .rail a span{color:rgba(232,228,255,.5)}
.dk .rail a.on span{color:#FFFFFF}
.dk h1{color:#F4F1FF}
.dk .eyebrow{color:rgba(232,228,255,.72)}
.dk .sub{color:rgba(232,228,255,.56)}
.dk .label{color:#F0EDFF}
.dk .card{background:rgba(255,255,255,.08);
     border:.8pt solid rgba(255,255,255,.17);
     border-top-color:rgba(255,255,255,.32);border-radius:24pt;
     box-shadow:none;padding:16pt}
.dk .card::after{display:none}

/* 표지 본문 블록: 폭 고정, "레일 오른쪽 영역"의 가운데.
   페이지 기준으로 가운데에 놓으면 레일이 왼쪽 53pt 를 차지하고 있어
   눈에는 왼쪽으로 쏠려 보인다. */
.cv{position:absolute;left:@CVL@pt;right:@CVR@pt;top:148pt}
.cv-eye{font-size:7pt;letter-spacing:.3em;font-weight:800;
        color:rgba(232,228,255,.72)}
.cv-t{font-size:46pt;font-weight:800;line-height:1.14;margin-top:20pt;
      letter-spacing:-.02em;color:#FFFFFF}
.cv-sub{font-size:10pt;line-height:1.8;color:rgba(232,228,255,.66);
        margin-top:16pt}
.cv-card{position:absolute;left:@CVL@pt;right:@CVR@pt;bottom:62pt;
     background:rgba(255,255,255,.09);border:.8pt solid rgba(255,255,255,.19);
     border-top-color:rgba(255,255,255,.34);border-radius:26pt;
     padding:18pt 24pt}
.crow{display:flex;align-items:center;gap:13pt;padding:10pt 0;
      text-decoration:none}
.crow+.crow{border-top:.7pt solid rgba(255,255,255,.10)}
.cn{font-size:10pt;font-weight:700;color:#F4F1FF;flex:1}
.cd{font-size:8pt;color:rgba(232,228,255,.55);margin-top:2pt;font-weight:400}
.orb{width:12pt;height:12pt;border-radius:99pt;flex:none}
.cq{font-size:8pt;font-weight:800;color:rgba(232,228,255,.5)}
"""

# 표지 본문 블록 폭. 레일 오른쪽 영역의 가운데에 놓는다.
CV_W = 330.0
_cv_side = (PAGE_W - RAIL_R - CV_W) / 2.0


def css():
    """이 테마가 BASE_CSS 뒤에 덧붙이는 전부."""
    out = (BASE
           .replace("@ROW@", "%g" % ROW_H)
           .replace("@INSET@", "%g" % INSET))
    # 점선: 아래는 전부 dline() 이 만든다. 손으로 고치지 말 것.
    out += dline(".tb td:not(:last-child)::after", "y",
                 ROW_H - 2 * INSET_V, VBOX)
    out += table_cols("t4", T4)
    out += table_cols("t6", T6)
    out += dline(".lines>div::after", "x", CW - 2 * INSET,
                 "left:0;right:0;bottom:0;height:%s" % THICK)
    # 좌표는 여기 한 곳에서만 나온다.
    out += ("\n.content{left:%.2fpt;right:%.2fpt}"
            "\n.rail{left:%.2fpt;width:%.2fpt;top:%.2fpt;bottom:%.2fpt}\n"
            % (CONTENT_L, CONTENT_R, RAIL_L, RAIL_W, RAIL_L, RAIL_L))
    out += (DARK
            .replace("@CVL@", "%.2f" % (RAIL_R + _cv_side - CONTENT_L))
            .replace("@CVR@", "%.2f" % (_cv_side - CONTENT_R)))
    return out


# ------------------------------------------------------------------- 배경
PT = 3                              # 배경 PNG 의 pt 당 픽셀
_W, _H = int(PAGE_W) * PT, int(PAGE_H) * PT
_SS = 4                             # 둥근 모서리용 수퍼샘플링

# 표지의 blob 하나짜리 원본. 내지는 이 목록을 그대로 쓰고 색만 밝힌다 --
# 좌표까지 새로 잡으면 "내지가 표지를 톤다운한 것"으로 안 읽힌다.
BLOBS = [(-20, 120, 250, 230, "#7C4DFF", .95, 74),   # 왼쪽   보라
         (640, 90, 240, 220, "#F45D9B", .90, 76),    # 오른쪽 핑크
         (60, 700, 260, 210, "#FF8A3D", .80, 80),    # 왼아래 주황
         (600, 640, 250, 230, "#22D3EE", .62, 84),   # 오른아래 청록
         (300, 400, 300, 260, "#4C1D95", .55, 100)]  # 가운데 짙은 보라


def _blur(layer, r):
    """알파 프리멀티플라이 후 블러. 안 그러면 투명한 쪽의 검정이 번진다."""
    a = np.asarray(layer).astype(np.float64)
    a[..., :3] *= a[..., 3:4] / 255.0
    b = np.asarray(Image.fromarray(a.astype(np.uint8), "RGBA")
                   .filter(ImageFilter.GaussianBlur(r))).astype(np.float64)
    al = b[..., 3:4]
    rgb = np.divide(b[..., :3] * 255.0, np.maximum(al, 1e-6))
    return Image.fromarray(
        np.concatenate([np.clip(rgb, 0, 255), al], axis=2).astype(np.uint8),
        "RGBA")


def _lighten(col, w):
    r, g, b = (int(col[i:i + 2], 16) for i in (1, 3, 5))
    return tuple(int(round(c + (255 - c) * w)) for c in (r, g, b))


def _mesh(base, w=0.0, s=1.0):
    img = Image.new("RGBA", (_W, _H), base + (255,))
    for x, y, rx, ry, col, a, blur in BLOBS:
        x, y, rx, ry, blur = (v * PT for v in (x, y, rx, ry, blur))
        layer = Image.new("RGBA", (_W, _H), (0, 0, 0, 0))
        ImageDraw.Draw(layer).ellipse([x - rx, y - ry, x + rx, y + ry],
                                      fill=_lighten(col, w) + (int(a * s * 255),))
        img = Image.alpha_composite(img, _blur(layer, blur))
    return img


def _rounded(box, radius):
    """PIL 의 rounded_rectangle 은 안티에일리어싱이 없다. 4배로 그리고 줄인다."""
    m = Image.new("L", (_W * _SS, _H * _SS), 0)
    ImageDraw.Draw(m).rounded_rectangle(
        [round(v * _SS) for v in box], radius=round(radius * _SS), fill=255)
    return m.resize((_W, _H), Image.LANCZOS)


def bake(path, cover_only=False, w=0.62, s=0.58):
    """배경 PNG 한 장. 표지를 깔고, 같은 그림을 밝힌 내지를 얹는다."""
    if cover_only:
        _mesh((0x14, 0x10, 0x3A)).convert("RGB").save(path, optimize=True)
        return path
    gap = SHEET * PT
    box = [gap, gap, _W - 1 - gap, _H - 1 - gap]
    r = 20 * PT
    out = _mesh((0x14, 0x10, 0x3A))
    sm = _rounded([box[0], box[1] + 7, box[2], box[3] + 7], r)
    sm = sm.filter(ImageFilter.GaussianBlur(16))
    sh = Image.new("RGBA", (_W, _H), (8, 4, 28, 0))
    sh.putalpha(sm.point(lambda v: int(v * .55)))
    out = Image.alpha_composite(out, sh)
    out.paste(_mesh((0xF9, 0xF6, 0xFE), w=w, s=s), (0, 0), _rounded(box, r))
    out.convert("RGB").save(path, optimize=True)
    return path


def build_assets(version, force=False):
    """배경 두 장. 이미 있으면 다시 굽지 않는다(한 장에 ~20초)."""
    os.makedirs("assets", exist_ok=True)
    made = []
    for name, cover in (("app_cover", True), ("app_page", False)):
        p = "assets/%s_%s.png" % (name, version)
        if force or not os.path.exists(p):
            bake(p, cover_only=cover)
            made.append(p)
    return made
