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
import re

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
# 필기 괘선의 양 끝 페이드는 포기했다. SVG mask 하나가 428페이지에서
# 4.1MB 를 먹는다(실측) -- 20MB 상한 안에 들어가려면 감당이 안 된다.
# 표의 점선 페이드는 유지한다: 칸이 짧아 페이드가 눈에 띄게 일하고,
# 비용은 0.5MB 뿐이다. 괘선은 500pt 짜리 긴 선이라 페이드가 있으나
# 없으나 거의 같아 보인다.
LINES_FADE = False
ROW_H = 24.0              # 표/괘선 한 줄 높이
THICK_PT = 0.75           # 선 두께 (pt)
THICK = "1px"             # = 0.75pt, CSS 쪽


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


def _stops(name, x1, y1, x2, y2, length):
    """양 끝이 흐려지는 stroke 용 그라데이션. userSpaceOnUse 여야 한다 --
    가로선은 bounding box 높이가 0 이라 objectBoundingBox 그라데이션이
    통째로 무시되고, 선이 아예 안 그려진다(실제로 겪음)."""
    f = min(FADE, length / 3.0)
    p = 100.0 * f / length
    return ('<linearGradient id="%s" gradientUnits="userSpaceOnUse" '
            'x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f">'
            '<stop offset="0" stop-color="%s" stop-opacity="0"/>'
            '<stop offset="%.3f%%" stop-color="%s"/>'
            '<stop offset="%.3f%%" stop-color="%s"/>'
            '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>'
            '</linearGradient>'
            % (name, x1, y1, x2, y2, C, p, C, 100 - p, C, C))


def rules_svg(widths, n_rows, head_h=24.0):
    """표 한 장의 구분선 전부를 SVG 한 장으로.

    CSS 의사요소로 그리면 Chrome 이 요소마다 타일 패턴 객체를 내보내
    표 하나에 40~50개가 생긴다. 40페이지 실측으로 592KB/page 였고
    SVG 로 몰아 그리니 95KB/page 가 됐다. 덤으로 진짜 stroke 라
    뷰어가 얇은 선을 픽셀에 맞춰 스냅해 준다.
    """
    w_tot = sum(widths)
    h = head_h + n_rows * ROW_H
    defs = []
    # 가로선: 열마다 그 열 안에서 페이드
    x = 0.0
    for i, w in enumerate(widths):
        L = w - 2 * INSET
        defs.append(_stops("h%d" % i, x + INSET, 0, x + w - INSET, 0, L))
        x += w
    # 세로선: 칸 한 줄 안에서 페이드. 줄마다 g 로 옮겨 쓴다
    defs.append(_stops("vh", 0, INSET_V, 0, head_h - INSET_V,
                       head_h - 2 * INSET_V))
    defs.append(_stops("vr", 0, INSET_V, 0, ROW_H - INSET_V,
                       ROW_H - 2 * INSET_V))

    body = []
    x = 0.0
    for i, w in enumerate(widths):
        # 한 열의 가로선 전부를 <path> 하나에 넣는다. 선마다 요소를 만들면
        # 그라데이션 stroke 가 선마다 셰이딩 객체로 나간다 -- 표 하나에
        # 44개. 서브패스로 묶으면 열당 1개다.
        d = "".join("M%.2f %.2fH%.2f" % (x + INSET, head_h + r * ROW_H,
                                         x + w - INSET)
                    for r in range(1, n_rows))
        if d:
            body.append('<path stroke="url(#h%d)" d="%s"/>' % (i, d))
        x += w
    # 세로 구분선 (마지막 열 뒤에는 긋지 않는다)
    bounds = []
    x = 0.0
    for w in widths[:-1]:
        x += w
        bounds.append(x)
    if bounds:
        d = "".join("M%.2f %.2fV%.2f" % (bx, INSET_V, head_h - INSET_V)
                    for bx in bounds)
        body.append('<path stroke="url(#vh)" d="%s"/>' % d)
        d = "".join("M%.2f %.2fV%.2f" % (bx, INSET_V, ROW_H - INSET_V)
                    for bx in bounds)
        for r in range(n_rows):
            body.append('<path transform="translate(0,%.2f)" '
                        'stroke="url(#vr)" d="%s"/>'
                        % (head_h + r * ROW_H, d))

    if os.environ.get("FLAT_STROKE"):          # 비용 측정용
        body = [re.sub(r'url\(#[hv][^)]*\)', C, b) for b in body]
    return ('<svg class="rules" viewBox="0 0 %.2f %.2f" width="%.2fpt" '
            'height="%.2fpt" xmlns="http://www.w3.org/2000/svg" '
            'fill="none" stroke-width="%.2f" stroke-dasharray="%g %g">'
            '<defs>%s</defs>%s</svg>'
            % (w_tot, h, w_tot, h, THICK_PT, DASH, PERIOD - DASH,
               "".join(defs), "".join(body)))


def lines_svg(width=None):
    """필기 괘선. 면 높이가 유동적이라 SVG <pattern> 으로 깐다.

    data: URI 를 background 로 깔았더니 페이지당 156KB 였다 -- 요소마다
    래스터화된다. <pattern> 은 객체 하나로 끝나고 높이가 얼마든 타일된다.
    타일 폭은 점 하나가 아니라 2048px 로 크게 잡는다 -- 점 단위로 잡으면
    가로로 60여 번 타일되고 Chrome 이 그만큼 펼쳐 낸다(+2MB).
    줄을 <path> 서브패스로 직접 찍어 보기도 했는데 62MB 가 됐다.
    선의 y 는 줄 경계에서 반 두께만큼 올려 픽셀 한 칸에 딱 맞춘다.
    경계 한가운데로 내려 보았더니 아래 줄이 잘리고 더 나빠졌다.
    단위는 px(사용자 단위). viewBox 를 두면 늘어나므로 두지 않는다.
    """
    k = 4.0 / 3.0                       # pt -> px
    return ('<svg class="rules rows" xmlns="http://www.w3.org/2000/svg">'
            '<defs><pattern id="lp" width="2048" height="%.4f" '
            'patternUnits="userSpaceOnUse">'
            '<path d="M0 %.4fH2048" stroke="%s" stroke-width="%.4f" '
            'stroke-dasharray="%.4f %.4f"/>'
            '</pattern></defs>'
            '<rect width="100%%" height="100%%" fill="url(#lp)"/></svg>'
            % (ROW_H * k, (ROW_H - THICK_PT / 2) * k, C, THICK_PT * k,
               DASH * k, (PERIOD - DASH) * k))


# 표 종류. 열 폭은 본문 폭에서 비율로 계산한다(손으로 적지 않는다).
T4 = prop(CW, [220, 120, 100, 60])          # 과제/할 일 4열
T6 = split(CW, 6, fixed=(60.0,))            # 시간표: 시각 열 60pt + 요일 5


BASE = """
/* 배경: 표지 한 장을 전 페이지가 공유한다. 페이지마다 그라데이션을 깔면
   페이지당 3초씩 걸려 뷰어에서 스크롤이 멈춘다(실측 2,973ms vs 49ms). */
.bgimg{position:absolute;inset:0;background-size:cover;pointer-events:none;
       z-index:0}
/* 내지. 이미지에 굽지 않고 여기서 자른다 -- 저해상도 배경에 구우면
   모서리가 뭉개지는데, CSS 로 자르면 경계가 벡터라 선명하다. */
.sheet{position:absolute;left:@SHEET@pt;top:@SHEET@pt;right:@SHEET@pt;
       bottom:@SHEET@pt;border-radius:@SHEETR@pt;background-size:cover;
       pointer-events:none;z-index:1}
.content{z-index:2}
.rail{z-index:3;border-right:none;height:auto}
.page{background:#17133E !important}
h1{color:#241E3A}
.eyebrow{color:#4A4260}
.sub{color:#5B5375}
.label{color:#2B2540;margin-bottom:9pt}
/* 12pt 세로 격자. 면의 페이지 상 y 가 어긋나면 같은 페이지의 표끼리
   점선 두께가 1px/2px 로 갈린다(실측: syllabus 표마다 위치가 0.25pt 씩
   달랐다). 두 조건을 동시에 만족해야 한다:
     · 3의 배수 pt  -- Chrome 이 px 격자(1px = 0.75pt)에 눕히므로
     · 4의 배수 pt  -- 뷰어 배율 1.5/2/2.5/3배에서 정수 픽셀이 되도록
   최소공배수가 12pt(=16px)다. 세로 방향 길이는 전부 12의 배수로 둔다. */
.content{padding:48pt 0 36pt}
.head{flex:none;height:72pt;overflow:hidden}
.label{height:12pt;margin-bottom:12pt}
.card{background:none;border:none;padding:0 0 12pt}
.card::after{display:none}
.body{gap:24pt}

/* 유리 -- 필기면·표·선택 탭이 전부 같은 재질이어야 한다.
   흰 테두리(0.7pt)를 줬더니 2px 짜리 흰 선으로 보여서 뺐다. 경계는
   그림자가 맡는다. */
.field, .lines, .tbwrap{position:relative;border-radius:13pt;
    background:rgba(255,255,255,.55);border:none}
/* 그림자는 box-shadow 로 내지 않는다 -- 요소마다 이미지로 래스터화돼
   면 하나에 25.8KB 를 먹는다(40페이지 실측). ::after 타원 그라데이션은
   벡터 패턴으로 남는다. CLAUDE.md 에 v8 에서 겪은 같은 사고가 있다. */
/* 윗변 하이라이트. 위에서 빛을 받는 면으로 읽혀 하단 그림자와 합쳐
   "떠 있는" 느낌을 만든다. 원래 쓰던 사방 box-shadow 는 428페이지에서
   +19.3MB 라 쓸 수 없었다(실측 18.60 -> 37.87MB).
   표는 머리띠가 자기 배경으로 윗변을 덮으므로 z-index 로 위에 얹는다.
   좌우를 모서리 반경만큼 비워야 둥근 모서리 밖으로 삐져나오지 않는다. */
.field::before, .lines::before, .tbwrap::before{content:"";position:absolute;
    left:13pt;right:13pt;top:0;height:.7pt;z-index:4;pointer-events:none;
    background:rgba(255,255,255,.95)}
.field::after, .lines::after, .tbwrap::after{content:"";position:absolute;
    left:3%;right:3%;top:100%;height:11pt;pointer-events:none;z-index:-1;
    background:radial-gradient(ellipse 64% 100% at 50% 0%,
    rgba(40,28,90,.15),rgba(40,28,90,0) 72%)}
/* overflow:hidden 을 쓰면 위 ::after 가 잘린다. 머리띠 모서리만 따로 둥글린다 */
.tb tr:first-child td:first-child{border-top-left-radius:13pt}
.tb tr:first-child td:last-child{border-top-right-radius:13pt}
.rules{position:absolute;left:0;top:0;pointer-events:none}
.tb{width:100%;border-collapse:separate;border-spacing:0;table-layout:fixed;
    background:transparent}
.tb td{height:@ROW@pt;padding:0 10pt;font-size:8.5pt;background:transparent;
    border:none;position:relative}
.tb tr:first-child td{height:24pt;font-size:6.6pt;letter-spacing:.14em;
    font-weight:800;color:#403A5C;text-align:center;
    background:rgba(232,227,247,.62)}
.tb .bx{text-align:center}
/* 체크박스와 탭 점은 각지게. border-radius 하나가 요소마다 호 4개를
   만들고, 428페이지에서 둘이 합쳐 3.3MB 였다(실측). */
.tb .bx i{display:inline-block;width:10pt;height:10pt;border-radius:0;
    border:.9pt solid rgba(120,110,160,.42);background:rgba(255,255,255,.75)}
.rail a i{border-radius:0}

/* 괘선 면은 줄을 넉넉히 넣고 잘라 쓴다. 줄 높이가 고정이라 면 높이와 딱
   떨어지지 않는데, 줄 수를 면에 맞춰 세면 레이아웃이 조금만 바뀌어도
   아래쪽이 텅 빈다(줄 높이를 27->24pt 로 바꾸자 68pt 가 비었다). */
/* overflow:hidden 을 쓰면 ::after 그림자(top:100%)가 잘린다.
   brain dump 만 그림자가 없던 원인이 이것이었다. 줄은 이제 SVG
   pattern 이 그리므로 넘치는 <div> 를 자를 일도 없다. */
.lines{overflow:visible;padding:0 @INSET@pt}
/* <svg> 는 대체 요소라 width/height 가 auto 면 고유 크기(300x150px)로
   눕는다. left/right 만 줘서는 늘어나지 않는다 -- brain dump 가
   4줄짜리 반쪽으로 나온 원인이 이것이었다. 길이를 명시한다. */
.rules.rows{left:@INSET@pt;top:0;width:calc(100% - @INSET2@pt);height:100%}
/* 괘선은 타일 배경이 그린다. 줄 <div> 는 높이만 잡는다 */
.lines>div{border:none;flex:none;height:@ROW@pt}

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
    global BASE
    b = BASE
    if os.environ.get("NOSHADOW"):
        b = b.replace("box-shadow:0 1.5pt 9pt rgba(40,28,90,.16)",
                      "border:.4pt solid rgba(120,110,160,.20)")
    out = (b
           .replace("@ROW@", "%g" % ROW_H)
           .replace("@INSET2@", "%g" % (2 * INSET))
           .replace("@INSET@", "%g" % INSET)
           .replace("@SHEETR@", "%g" % SHEET_R)
           .replace("@SHEET@", "%g" % SHEET))
    # 좌표는 여기 한 곳에서만 나온다.
    out += ("\n.content{left:%.2fpt;right:%.2fpt}"
            "\n.rail{left:%.2fpt;width:%.2fpt;top:%.2fpt;bottom:%.2fpt}\n"
            % (CONTENT_L, CONTENT_R, RAIL_L, RAIL_W, RAIL_L, RAIL_L))
    out += (DARK
            .replace("@CVL@", "%.2f" % (RAIL_R + _cv_side - CONTENT_L))
            .replace("@CVR@", "%.2f" % (_cv_side - CONTENT_R)))
    # 주석은 소스에만 남긴다. 그대로 실으면 산출물에 한글이 들어가고
    # 428페이지어치 바이트를 차지한다.
    out = re.sub(r"/\*.*?\*/", "", out, flags=re.S)
    return re.sub(chr(92) + "n" + r"\s*" + chr(92) + "n", chr(10), out)


# ------------------------------------------------------------------- 배경
# 배경 PNG 의 pt 당 픽셀. 낮을수록 좋다 -- Chrome 은 큰 배경 이미지를
# 페이지마다 복사본으로 넣는다(1836x2376 일 때 페이지당 38.4KB, 1/4 로
# 줄이면 7.5KB, 40페이지 실측). 부드러운 오로라라 해상도는 안 아쉽다.
# 대신 내지의 둥근 모서리는 이미지에 굽지 않고 CSS 로 자른다 -- 저해상도
# 이미지에 구우면 경계가 뭉개진다.
PT = 0.75
_W, _H = int(PAGE_W * PT), int(PAGE_H * PT)
_SS = 4                             # 둥근 모서리용 수퍼샘플링
SHEET_R = 20.0                      # 내지 모서리 반경 (pt)

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


def bake(kind, path, w=0.62, s=0.58):
    """배경 세 장. 셋 다 저해상도다 -- 경계는 CSS 가 만든다.

    cover : 표지·목차용 오로라
    under : 내지 아래에 깔리는 오로라 + 내지가 드리우는 그림자
    sheet : 밝힌 오로라를 내지 영역만큼 잘라낸 것
    """
    if kind == "cover":
        _mesh((0x14, 0x10, 0x3A)).convert("RGB").save(path, optimize=True)
        return path
    if kind == "sheet":
        g = SHEET * PT
        (_mesh((0xF9, 0xF6, 0xFE), w=w, s=s).convert("RGB")
         .crop((int(g), int(g), int(_W - g), int(_H - g)))
         .save(path, optimize=True))
        return path
    g = SHEET * PT
    box = [g, g, _W - 1 - g, _H - 1 - g]
    out = _mesh((0x14, 0x10, 0x3A))
    sm = _rounded([box[0], box[1] + 7 * PT / 3, box[2], box[3] + 7 * PT / 3],
                  SHEET_R * PT)
    sm = sm.filter(ImageFilter.GaussianBlur(16 * PT / 3))
    sh = Image.new("RGBA", (_W, _H), (8, 4, 28, 0))
    sh.putalpha(sm.point(lambda v: int(v * .55)))
    Image.alpha_composite(out, sh).convert("RGB").save(path, optimize=True)
    return path


def build_assets(version, force=False):
    """배경 세 장. 이미 있으면 다시 굽지 않는다."""
    os.makedirs("assets", exist_ok=True)
    made = []
    for kind in ("cover", "under", "sheet"):
        p = "assets/app_%s_%s.png" % (kind, version)
        if force or not os.path.exists(p):
            bake(kind, p)
            made.append(p)
    return made
