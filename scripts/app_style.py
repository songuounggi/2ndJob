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
import zlib

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

# flat_paint (student-v0.2~, 2026-09-24). GoodNotes 가 바둑판처럼 늦게 그리는
# 요소를 뺀다(RELEASE.md 2 절). build_planner 가 테마 플래그를 보고 켠다.
# 끄면 student-v0.1 과 같은 결과가 나온다.
#   · 면 그림자 radial-gradient  -> 공유 PNG 한 장 (그라데이션 셰이딩 + 소프트마스크)
#   · 표 점선 양 끝 페이드       -> 단색 점선      (같음)
#   · 필기 괘선 SVG <pattern>     -> 면마다 벡터 선 (Chrome 이 이미지 타일로 구웠다)
FLAT = False
# dash_fade (student-v0.3~): FLAT 에서 뺐던 표 점선 양 끝 페이드를 그라데이션
# 없이 되살린다(_fade_dashes). 사용자 요청 2026-09-24.
DASH_FADE = False
# chip_shadow / orb_png (student-v0.4~): v0.2 에서 헤어라인·단색으로 바꿨던 칩
# 그림자와 목차 색 점을 미리 구운 PNG 로 되살린다. 사용자 요청 2026-09-24.
CHIP_SHADOW = False
ORB_PNG = False
# hanji (student-v0.5~): 내지 바닥에 한지 질감. 사용자 요청 2026-09-24 --
# "뭔가 아쉽고 썰렁해 보였다". 내지 배경은 전 페이지가 공유하는 이미지 한
# 장이라 질감을 거기에 구우면 뷰어 부담이 거의 없다(반복 타일 아님).
HANJI = False
# line_fade / tab_pill (student-v0.6~, 사용자 지적 2026-09-24):
#  · 필기칸 괘선에도 표 점선과 같은 양 끝 페이드 (p.17 "Why these" 가 표와 달랐다)
#  · 밝은 페이지의 현재 탭 알약이 흰색 9% 라 안 보였다 -- 채움과 테두리를 올린다
LINE_FADE = False
TAB_PILL = False
HANJI_STRENGTH = 1.0
VERSION = ""


def sheet_file():
    """내지 배경 파일 이름(확장자 포함). 한지는 섬유 무늬라 PNG 로는 압축이
    안 된다 -- JPEG."""
    return "app_sheet_%s.%s" % (VERSION, "jpg" if HANJI else "png")


RAIL_TEXT_DARKEN = 0.82   # 레일 글자만 진하게. 본문 색은 건드리지 않는다
RAIL_DIM = "#5B5375"      # 비선택 탭 글자


def darken(hexcol, f=RAIL_TEXT_DARKEN):
    """색상은 두고 명도만 낮춘다.

    유리 알약은 페이지 배경보다 밝아서, 본문에서 4.5:1 을 넘기던 글자색이
    레일에서는 3.9~4.0 으로 떨어진다(실측). 레일에서만 18% 어둡게 하면
    5.3~5.4 가 된다. 비선택 탭은 2.59 -> 5.05.
    """
    r, g, b = (int(hexcol[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02X%02X%02X" % tuple(max(0, int(round(v * f)))
                                   for v in (r, g, b))


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


FADE_STEP = 0.1
FADE_PIECE = 0.0          # 0 이면 점 단위(v0.3~0.5). snap 전에 build_planner 가 켠다          # 양 끝 점의 투명도 눈금. 같은 값끼리 path 하나로 묶는다


def _fade_dashes(x0, x1, ys):
    """가로 점선 한 열(여러 행)을 양 끝이 흐려지게. 그라데이션 없이.

    점은 x0 에서 시작해 PERIOD 마다 DASH 길이. 점 중심에서 가까운 끝까지의
    거리를 페이드 폭 f 로 나눈 값이 그 점의 불투명도다 -- _stops() 의
    그라데이션(끝 0 -> f 에서 1)을 점마다 한 번 샘플링한 것과 같다.
    불투명도 1 인 가운데 구간은 dasharray 한 줄로 두어 바이트를 아낀다.
    stroke-opacity 는 PDF 에서 고정 알파(/CA)라 소프트마스크가 아니다."""
    L = x1 - x0
    f = min(FADE, L / 3.0)
    full, part = [], {}
    s0 = x0
    while s0 < x1 - 1e-6:
        e = min(s0 + DASH, x1)
        # 페이드 구간에 걸친 점은 PIECE(1pt) 조각으로 쪼개 조각마다 샘플링
        # (student-v0.6). 점 단위로는 좁은 칸(DONE 열 등)에서 흐림이 거의
        # 안 보였다 -- "양끝 흐림은 각 셀마다"(사용자 지적 2026-09-24).
        if FADE_PIECE and min(s0 - x0, x1 - e) < f:
            y = s0
            while y < e - 1e-6:
                ye = min(y + FADE_PIECE, e)
                xc = (y + ye) / 2
                a = min(1.0, max(0.0, min(xc - x0, x1 - xc) / f))
                a = round(a / FADE_STEP) * FADE_STEP
                if a > 0:
                    part.setdefault(round(a, 2), []).append((y, ye))
                y = ye
            s0 += PERIOD
            continue
        xc = (s0 + e) / 2
        a = min(1.0, max(0.0, min(xc - x0, x1 - xc) / f))
        a = round(a / FADE_STEP) * FADE_STEP
        if a >= 1.0:
            full.append((s0, e))
        elif a > 0:
            part.setdefault(round(a, 2), []).append((s0, e))
        s0 += PERIOD
    out = []
    if full:
        a0, b0 = full[0][0], full[-1][1]
        out.append('<path stroke="%s" d="%s"/>' % (C, "".join(
            "M%.2f %.2fH%.2f" % (a0, y, b0) for y in ys)))
    for a, segs in sorted(part.items()):
        out.append('<path stroke="%s"%s stroke-dasharray="none" '
                   'd="%s"/>' % (C, "" if a >= 1.0 else ' stroke-opacity="%g"' % a, "".join(
                       "M%.2f %.2fH%.2f" % (p0, y, p1)
                       for y in ys for p0, p1 in segs)))
    return out


def _fade_dashes_v(xs, y0, y1, offset):
    """세로 점선(여러 경계)을 위아래 끝이 흐려지게. _fade_dashes 의 세로판.

    세로선은 행 경계마다 틈이 오도록 dashoffset 을 민다. 점 위치를 브라우저
    규칙 그대로 계산한다: 경로 위 거리 t 에서 (t + offset) mod PERIOD < DASH
    이면 점이다. 가운데(불투명도 1) 구간은 그 첫 점에서 시작하는 dasharray
    한 줄로, 끝 점들만 따로 옅게 긋는다."""
    L = y1 - y0
    f = min(FADE, L / 3.0)
    segs, t = [], 0.0
    while t < L - 1e-6:
        ph = (t + offset) % PERIOD
        if ph < DASH:
            e = min(t + (DASH - ph), L)
            segs.append((y0 + t, y0 + e))
            t = e
        else:
            t += PERIOD - ph
    full, part = [], {}
    for a0, b0 in segs:
        yc = (a0 + b0) / 2
        a = min(1.0, max(0.0, min(yc - y0, y1 - yc) / f))
        a = round(a / FADE_STEP) * FADE_STEP
        if a >= 1.0:
            full.append((a0, b0))
        elif a > 0:
            part.setdefault(round(a, 2), []).append((a0, b0))
    out = []
    if full:
        a0, b0 = full[0][0], full[-1][1]
        out.append('<path stroke="%s" d="%s"/>' % (C, "".join(
            "M%.2f %.2fV%.2f" % (x, a0, b0) for x in xs)))
    for a, ss in sorted(part.items()):
        out.append('<path stroke="%s" stroke-opacity="%g" stroke-dasharray="none" '
                   'd="%s"/>' % (C, a, "".join(
                       "M%.2f %.2fV%.2f" % (x, p0, p1) for x in xs for p0, p1 in ss)))
    return out


def _fade_dashes_vcell(xs, cells, y0, offset, piece=1.0):
    """세로 구분선을 **칸마다** 위아래 끝이 흐려지게 (사용자 지적 2026-09-24:
    "양끝 흐림은 각 셀마다"). 가로선이 열마다 흐려지는 것과 같은 규칙.

    칸 하나는 24pt 에 점이 둘뿐이라 점 단위로 옅게 하면 둘 다 0.9 로 거의
    같아 흐림이 안 보인다. 점을 piece(1pt) 조각으로 쪼개 조각 중심에서
    그라데이션(_stops 와 같은 f)을 샘플링한다. 점 위치는 원래 세로선과
    같다: 경로 시작 y0 에서 거리 t, (t + offset) mod PERIOD < DASH 이면 점.
    cells: [(칸 위, 칸 아래), ...] -- 흐림은 [위+INSET_V, 아래-INSET_V] 에서."""
    groups = {}
    for top, bot in cells:
        c0, c1 = top + INSET_V, bot - INSET_V
        f = min(FADE, (c1 - c0) / 3.0)
        k = int((c0 - y0 + offset) // PERIOD) - 1
        while True:
            ds = y0 - offset + k * PERIOD          # 점 시작 (전역 위상)
            if ds >= c1:
                break
            a0, b0 = max(ds, c0), min(ds + DASH, c1)
            k += 1
            if b0 <= a0:
                continue
            y = a0
            while y < b0 - 1e-6:
                e = min(y + piece, b0)
                yc = (y + e) / 2
                al = min(1.0, max(0.0, min(yc - c0, c1 - yc) / f))
                al = round(al / FADE_STEP) * FADE_STEP
                if al > 0:
                    groups.setdefault(round(al, 2), []).append((y, e))
                y = e
    out = []
    for al, ss in sorted(groups.items()):
        op = "" if al >= 1.0 else ' stroke-opacity="%g"' % al
        out.append('<path stroke="%s"%s stroke-dasharray="none" d="%s"/>'
                   % (C, op, "".join("M%.2f %.2fV%.2f" % (x, p0, p1)
                                     for x in xs for p0, p1 in ss)))
    return out


def _flat_stroke(b, tag, n):
    for i in range(n):
        b = b.replace('url(#%sh%d)' % (tag, i), C)
    return b


def rules_svg(widths, n_rows, head_h=24.0):
    """표 한 장의 구분선 전부를 SVG 한 장으로.

    CSS 의사요소로 그리면 Chrome 이 요소마다 타일 패턴 객체를 내보내
    표 하나에 40~50개가 생긴다. 40페이지 실측으로 592KB/page 였고
    SVG 로 몰아 그리니 95KB/page 가 됐다. 덤으로 진짜 stroke 라
    뷰어가 얇은 선을 픽셀에 맞춰 스냅해 준다.
    """
    w_tot = sum(widths)
    h = head_h + n_rows * ROW_H
    # 그라데이션 id 는 문서 전체에서 하나의 이름공간이다. 전에는 표마다
    # h0~h5/vh/vr 을 똑같이 붙여 두 가지가 깨졌다(2026-09-23):
    #  · 페이지 id h1~h5(시간표)와 겹쳐 Chrome 이 명명 목적지를 첫 표의
    #    <linearGradient> 에 걸었다 -- 시간표 칩을 누르면 1페이지로 갔다
    #  · url(#h1) 은 문서의 첫 정의로 풀린다. 열 폭이 다른 표가 첫 표의
    #    페이드 좌표를 빌려 썼다
    # 표 모양에서 id 를 만든다. 같은 모양이면 같은 정의라 겹쳐도 무해하다.
    tag = "rg%08x" % (zlib.crc32(repr((list(widths), head_h)).encode()))
    defs = []
    # 가로선: 열마다 그 열 안에서 페이드
    x = 0.0
    for i, w in enumerate(widths):
        L = w - 2 * INSET
        defs.append(_stops("%sh%d" % (tag, i), x + INSET, 0, x + w - INSET, 0, L))
        x += w
    # 세로선: 칸 한 줄 안에서 페이드. 줄마다 g 로 옮겨 쓴다
    defs.append(_stops(tag + "vh", 0, INSET_V, 0, head_h - INSET_V,
                       head_h - 2 * INSET_V))
    defs.append(_stops(tag + "vr", 0, INSET_V, 0, ROW_H - INSET_V,
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
            body.append('<path stroke="url(#%sh%d)" d="%s"/>' % (tag, i, d))
        x += w
    # 세로 구분선. 칸마다 끊어 그리면 표 하나에 (행수+1)개의 셰이딩이
    # 생긴다(22행이면 23개). 경계마다 한 줄로 긋고, 대시 위상을 밀어
    # **행 경계마다 틈이 오게** 한다 -- 가로선과 십자로 만나지 않는다.
    # 행 높이 24pt 는 주기 8pt 의 3배라 위상이 매 행 같은 자리에 온다.
    bounds = []
    x = 0.0
    for w in widths[:-1]:
        x += w
        bounds.append(x)
    if bounds:
        H = head_h + n_rows * ROW_H
        d = "".join("M%.2f %.2fV%.2f" % (bx, INSET_V, H - INSET_V)
                    for bx in bounds)
        body.append('<path stroke="%s" stroke-dashoffset="%.2f" d="%s"/>'
                    % (C, PERIOD - DASH / 2 - INSET_V, d))

    # 마감선은 긋지 않는다(2026-09-24). 학생용은 표가 곧 유리 면이라
    # 면의 둥근 가장자리가 표를 닫는다. 가장자리 위에 점선을 겹쳤더니
    # 점선 테두리처럼 애매하게 보였다. 마지막 행은 면 바닥까지 딱 한 행
    # 높이로 끝난다 -- Prod 1 필기면과 같은 마감이다. LINES.md 2 절의
    # "표는 닫는다"는 카드 안에 표가 따로 떠 있는 v8 의 .trk 이야기다.

    if FLAT:
        # 페이드용 그라데이션은 PDF 에서 셰이딩 + 소프트마스크가 된다.
        # 대신 양 끝 점 몇 개를 따로 떼어 점마다 옅은 단색으로 긋는다
        # (사용자 요청 2026-09-24: 페이드는 살린다). 가로선만 해당 --
        # 세로선은 원래 페이드가 없었다.
        defs = []
        if DASH_FADE:
            body = [b for b in body if "url(#" not in b]
            x = 0.0
            for w in widths:
                body[:0] = _fade_dashes(
                    x + INSET, x + w - INSET,
                    [head_h + r * ROW_H for r in range(1, n_rows)])
                x += w
            if LINE_FADE and bounds:
                # 세로선도 위아래 끝을 흐리게 (student-v0.6, 사용자 지적)
                body = [b for b in body if "stroke-dashoffset" not in b]
                cells = [(0.0, head_h)] + [(head_h + r * ROW_H,
                                            head_h + (r + 1) * ROW_H)
                                           for r in range(n_rows)]
                body += _fade_dashes_vcell(bounds, cells, INSET_V,
                                           PERIOD - DASH / 2 - INSET_V)
        else:                                # student-v0.2: 페이드 없이 단색
            body = [_flat_stroke(b, tag, len(widths)) for b in body]
    return ('<svg class="rules" viewBox="0 0 %.2f %.2f" width="%.2fpt" '
            'height="%.2fpt" xmlns="http://www.w3.org/2000/svg" '
            'fill="none" stroke-width="%.2f" stroke-dasharray="%g %g">'
            '<defs>%s</defs>%s</svg>'
            % (w_tot, h, w_tot, h, THICK_PT, DASH, PERIOD - DASH,
               "".join(defs), "".join(body)))


# 실험 기록(2026-09-23): 괘선을 CSS `border-bottom: dashed` 로 그려 보았다.
# v8 이 쓰는 방식이고 "테두리 선은 벡터라 싸다"(LINES.md)는 기대였는데,
# 428페이지에서 27.58MB 가 나왔다(SVG pattern 19.84MB). Chrome 이 점선
# 테두리를 작은 사각형 여러 개로 내보낸다. 실선일 때만 싼 것이다.
# 스위치는 남겨 둔다 -- 다음에 또 궁금해지면 한 번 돌려 보면 된다.
DASH_BORDER = bool(os.environ.get("DASH_BORDER"))


FLAT_SVG = '<svg class="rules rows" xmlns="http://www.w3.org/2000/svg"></svg>'


def flat_lines(k, w_pt):
    """면 하나의 괘선을 벡터 선으로. 줄 k-1 개(맨 아래 행은 면 가장자리가
    닫는다), 폭은 잰 면 폭. <pattern> 과 같은 자리에 같은 점선을 긋는다."""
    q = 4.0 / 3.0                       # pt -> px (SVG 사용자 단위)
    W = (w_pt - 2 * INSET) * q
    # 선 중심은 행 경계 정중앙 -- 표 점선(rules_svg)과 같은 자리라야 뷰어
    # 배율마다 두 선이 같은 픽셀 두께로 떨어진다. <pattern> 시절의 반 두께
    # 올림은 래스터 타일용이었다(벡터에 두면 2배에서 2px/3px 로 갈렸다).
    d = "".join("M0 %.2fH%.2f" % (n * ROW_H * q, W)
                for n in range(1, k))
    if not d:
        return FLAT_SVG
    if LINE_FADE:
        # pt 좌표 viewBox 로 그려 표 점선의 _fade_dashes 를 그대로 쓴다.
        # 크기는 CSS(.rules.rows: 폭 100%-2*INSET, 높이 100%-12pt)가 정하므로
        # viewBox 를 같은 pt 값으로 두면 1pt = 1 사용자 단위가 된다.
        wv, hv = w_pt - 2 * INSET, k * ROW_H - ROW_H / 2
        return ('<svg class="rules rows" xmlns="http://www.w3.org/2000/svg" '
                'viewBox="0 0 %.2f %.2f" preserveAspectRatio="none" fill="none" '
                'stroke-width="%.2f" stroke-dasharray="%g %g">%s</svg>'
                % (wv, hv, THICK_PT, DASH, PERIOD - DASH,
                   "".join(_fade_dashes(0.0, wv, [n * ROW_H for n in range(1, k)]))))
    return ('<svg class="rules rows" xmlns="http://www.w3.org/2000/svg">'
            '<path d="%s" fill="none" stroke="%s" stroke-width="%.4f" '
            'stroke-dasharray="%.4f %.4f"/></svg>'
            % (d, C, THICK_PT * q, DASH * q, (PERIOD - DASH) * q))


def lines_svg(width=None):
    if DASH_BORDER:                      # 실험: CSS 점선 테두리로 대체
        return ""
    if FLAT:                             # 빈 자리. snap_lines 가 재고 채운다
        return FLAT_SVG
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
            '<defs><pattern id="rl-lp" width="2048" height="%.4f" '
            'patternUnits="userSpaceOnUse">'
            '<path d="M0 %.4fH2048" stroke="%s" stroke-width="%.4f" '
            'stroke-dasharray="%.4f %.4f"/>'
            '</pattern></defs>'
            '<rect width="100%%" height="100%%" fill="url(#rl-lp)"/></svg>'
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
/* 날짜 칸 -- 데일리 DATE / 위클리 WEEK OF. 머리 오른쪽 빈자리에 띄운다.
   top 24pt / 높이 24pt 로 12pt 격자를 지킨다. 그림자(::after 11pt)까지
   머리 72pt 안에 들어가야 overflow:hidden 에 안 잘린다(24+24+11=59). */
.head{position:relative}
.datebox{position:absolute;right:0;top:24pt;display:flex;align-items:center;
    gap:8pt}
.datebox span{font-size:6.6pt;letter-spacing:.14em;font-weight:800;
    color:#403A5C}
.datebox .field{width:132pt;height:24pt}
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
   "떠 있는" 느낌을 만든다.
   불투명 .95 / 두께 .7pt / 좌우 13pt 잘라내기로 두었더니 양 끝이 뭉툭하게
   끊긴 "흰 줄"로 보였다(2026-09-23 지적). 양 끝을 흐리고 농도를 낮춘다. 원래 쓰던 사방 box-shadow 는 428페이지에서
   +19.3MB 라 쓸 수 없었다(실측 18.60 -> 37.87MB).
   표는 머리띠가 자기 배경으로 윗변을 덮으므로 z-index 로 위에 얹는다.
   좌우를 모서리 반경만큼 비워야 둥근 모서리 밖으로 삐져나오지 않는다. */

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
/* 높이를 한 행 모자라게 -- 패턴은 행마다 바닥에 선을 긋는데, 맨 아래
   행의 선은 면 가장자리와 겹친다. 면 높이는 snap_lines() 가 24pt
   배수로 고정하므로 마지막 행은 가장자리까지 딱 한 행이다. */
.rules.rows{left:@INSET@pt;top:0;width:calc(100% - @INSET2@pt);
    height:calc(100% - @HALF@pt)}
/* 괘선은 타일 배경이 그린다. 줄 <div> 는 높이만 잡는다 */
.lines>div{border:none;flex:none;height:@ROW@pt}
@DASHB@

/* 선택 탭 = 표지 카드와 같은 유리 레시피.
   불투명 흰 알약은 페이지에서 유일한 불투명 개체라 혼자 튀었다. */
.rail a span{color:@DIM@}
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
/* 윗변만 밝게 두면(표지 카드 레시피) 목차 카드에서는 "흰 실선 하나"로
   보인다(2026-09-23 지적). 테두리는 사방 같은 농도로 둔다.
   표지 .cv-card 는 배경이 훨씬 어둡고 카드가 커서 그대로 둔다. */
.dk .card{background:rgba(255,255,255,.08);
     border:.8pt solid rgba(255,255,255,.14);border-radius:24pt;
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
           .replace("@HALF@", "%g" % (ROW_H / 2))
           .replace("@INSET@", "%g" % INSET)
           .replace("@DASHB@",
                    ".lines>div{border-bottom:%.2fpt dashed %s}"
                    % (THICK_PT, C) if DASH_BORDER else "")
           .replace("@DIM@", RAIL_DIM)
           .replace("@SHEETR@", "%g" % SHEET_R)
           .replace("@SHEET@", "%g" % SHEET))
    # 좌표는 여기 한 곳에서만 나온다.
    out += ("\n.content{left:%.2fpt;right:%.2fpt}"
            "\n.rail{left:%.2fpt;width:%.2fpt;top:%.2fpt;bottom:%.2fpt}\n"
            % (CONTENT_L, CONTENT_R, RAIL_L, RAIL_W, RAIL_L, RAIL_L))
    out += (DARK
            .replace("@CVL@", "%.2f" % (RAIL_R + _cv_side - CONTENT_L))
            .replace("@CVR@", "%.2f" % (_cv_side - CONTENT_R)))
    if TAB_PILL:
        # 사용자가 다섯 단계 중 L2 를 골랐다(2026-09-24). v0.4(9%/19%)의
        # 은은함은 남기고 밝은 페이지에서도 알약이 구분되게.
        out += (chr(10) + ".rail a.on{background:rgba(255,255,255,.22);"
                "border:.8pt solid rgba(255,255,255,.40);"
                "border-top-color:rgba(255,255,255,.55)}"
                ".dk .rail a.on{background:rgba(255,255,255,.09);"
                "border:.8pt solid rgba(255,255,255,.19);"
                "border-top-color:rgba(255,255,255,.34)}")
    if FLAT:
        out += (chr(10) + ".field::after,.lines::after,.tbwrap::after{background:"
                "url('../assets/app_shadow_%s.png') 0 0/100%% 100%% no-repeat}"
                % VERSION)
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
    if kind == "sheet" and HANJI:
        return _bake_hanji_sheet(path, w, s)
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
        if kind == "sheet":
            p = "assets/" + sheet_file()
        if force or not os.path.exists(p):
            bake(kind, p)
            made.append(p)
    if FLAT:
        p = "assets/app_shadow_%s.png" % version
        if force or not os.path.exists(p):
            shadow_png(p)
            made.append(p)
    return made


def shadow_png(path, w=800, h=80):
    """면 그림자 radial-gradient(ellipse 64% 100% at 50% 0%,
    rgba(40,28,90,.15), 0 at 72%) 를 한 번 샘플링한 것. 두 반지름이 상자
    기준이라 어느 면에 늘려 붙여도 CSS 그라데이션과 같은 모양이다.
    build_planner.shadow_png 와 같은 방식, 색·농도만 이 테마 값."""
    x = (np.arange(w) + .5) / w - .5
    y = (np.arange(h) + .5) / h
    d = np.sqrt((x[None, :] / .64) ** 2 + (y[:, None] / 1.0) ** 2)
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = 40, 28, 90
    rgba[..., 3] = np.round(np.clip(1 - d / .72, 0, 1) * .15 * 255)
    Image.fromarray(rgba, "RGBA").save(path, optimize=True)
    return path


# ---------------------------------------------------------------- snap ----
SNAP_JS = """
const out = [];
document.querySelectorAll('.lines').forEach(L =>
  out.push([L.getBoundingClientRect().height * 0.75,
            L.getBoundingClientRect().width * 0.75]));
document.body.setAttribute('data-probe', JSON.stringify(out));
"""


def snap_lines(src, chrome):
    """필기면 높이를 행 높이(24pt)의 배수로 내림해 고정한다.

    v8 의 build_planner.snap_cards() 는 줄 <div> 를 세는데, 학생용은 줄을
    SVG 패턴이 그려 <div> 가 없다. 그래서 한 곳도 고정하지 못했고(pinned 0)
    필기면 369개의 바닥 나머지가 0~22pt 로 제각각이었다 -- 마지막 괘선이
    가장자리 위에 애매하게 떠 있었다(2026-09-24 지적).

    면을 재서 내림한 높이를 박는다. 카드는 배경이 없으므로 flex 로 늘어난
    채 두어도 보이지 않는다 -- 보이는 것은 면(.lines)뿐이다. 남는 높이는
    면 아래로 빠져 페이지 여백이 된다. 허용치 0.5pt: Chrome 의 반올림은
    흡수하고 정말 모자란 행은 버린다(LINES.md 1-3 절 함정 3).
    """
    import io, json, subprocess, tempfile
    html = io.open(src, encoding="utf-8").read()
    tmp = os.path.join(tempfile.gettempdir(), "snap_lines_probe.html")
    io.open(tmp, "w", encoding="utf-8").write(
        html.replace("</body>", "<script>%s</script></body>" % SNAP_JS))
    r = subprocess.run(
        [chrome, "--headless=new", "--disable-gpu",
         "--user-data-dir=" + os.path.join(tempfile.gettempdir(),
                                          "planner-snap-profile"),
         "--virtual-time-budget=25000", "--dump-dom",
         "file:///" + tmp.replace(chr(92), "/")],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.search(r'data-probe="([^"]*)"', r.stdout or "")
    if not m:
        raise RuntimeError("snap_lines 측정 실패 " + (r.stderr or "")[-400:])
    hs = json.loads(m.group(1).replace("&quot;", '"'))
    marks = list(re.finditer(r'class="lines" style="([^"]*)"', html))
    if len(marks) != len(hs):
        raise RuntimeError("snap_lines: 면 %d개를 쟀는데 마크업은 %d개"
                           % (len(hs), len(marks)))
    parts, last, n, ks = [], 0, 0, []
    for mk, (hpt, wpt) in zip(marks, hs):
        k = int((hpt + 0.5) // ROW_H)
        if k < 1:
            raise RuntimeError("snap_lines: 한 행도 안 들어가는 면 (%.1fpt)"
                               % hpt)
        ks.append((k, wpt))
        style = re.sub(r"flex:[^;]*;?|height:[^;]*;?", "", mk.group(1))
        style = "flex:none;height:%gpt;%s" % (k * ROW_H, style)
        n += style != mk.group(1)
        parts.append(html[last:mk.start(1)] + style)
        last = mk.end(1)
    parts.append(html[last:])
    html = "".join(parts)
    if FLAT:
        slots = html.split(FLAT_SVG)
        if len(slots) - 1 != len(ks):
            raise RuntimeError("snap_lines: 괘선 자리 %d개, 면 %d개"
                               % (len(slots) - 1, len(ks)))
        html = slots[0] + "".join(flat_lines(k, w) + rest
                                  for (k, w), rest in zip(ks, slots[1:]))
    # 면을 담은 카드와 행도 더는 늘어나지 않게 한다. 카드가 flex:1 로
    # 남으면 면 아래에 빈 띠가 생겨 다음 카드를 밀었다(위클리 Reading 아래,
    # 2026-09-24). 남는 높이는 페이지 맨 아래로 간다. flex:1 인 행은 전부
    # 필기면을 담는다 -- 아닌 행은 verify_student 의 "늘어나는 행"이 잡는다.
    # 단, 가로 .row 안의 카드는 건드리지 않는다. 거기서 flex 는 **폭**을
    # 정해서, flex:none 을 걸자 코넬 노트의 Cue/Notes 가 글자 폭으로
    # 쪼그라들었다(LINES.md 1-3 절 함정 2 를 다시 밟음). 행만 고정한다.
    row_re = re.compile(r'<div class="row" style="[^"]*">.*?</div></div></div>',
                        re.S)
    card_re = re.compile(r'(<div class="card" style=")flex:1(?=[;"])'
                         r'([^"]*">(?:<div class="label">[^<]*</div>)?'
                         r'<div class="lines" style="flex:none)')
    out, last = [], 0
    for m in row_re.finditer(html):
        out.append(card_re.sub(r"\1flex:none\2", html[last:m.start()]))
        out.append(re.sub(r'^(<div class="row" style=")flex:1(?=[;"])',
                          r"\1flex:none", m.group(0)))
        last = m.end()
    out.append(card_re.sub(r"\1flex:none\2", html[last:]))
    html = "".join(out)
    io.open(src, "w", encoding="utf-8").write(html)
    return n


# ------------------------------------------------------------ 구운 이미지들
# 그라데이션·blur 는 PDF 에서 셰이딩·소프트마스크가 되어 GoodNotes 를 느리게
# 한다(RELEASE.md 2 절). 같은 모양을 PNG 로 한 번 굽고 여러 곳이 나눠 쓴다.
# 이미지의 알파는 이미지 자체의 마스크라 check_render A 에 걸리지 않는다.
CHIP_H = 19.0              # 칩 높이 pt (student_pages.CHIP 과 같아야 한다)
CHIP_R = 7.0               # 칩 모서리
CHIP_M = 6.0               # 그림자가 칩 밖으로 번지는 여백 pt


def chip_shadow(w_pt):
    """칩 폭 w_pt 에 맞춘 그림자 PNG 의 url. 없으면 굽는다.
    원래 CSS: box-shadow 0 1pt 5pt rgba(40,28,90,.12). CSS 그림자처럼
    칩 안쪽은 비운다 -- 반투명 칩 아래로 그림자가 비치면 안 된다."""
    k = 4                                          # px / pt
    name = "assets/app_chip_%d_%s.png" % (round(w_pt * 4), VERSION)
    if not os.path.exists(name):
        W = int(round((w_pt + 2 * CHIP_M) * k))
        H = int(round((CHIP_H + 2 * CHIP_M) * k))
        def rr(dy):
            m = Image.new("L", (W, H), 0)
            ImageDraw.Draw(m).rounded_rectangle(
                [CHIP_M * k, (CHIP_M + dy) * k,
                 (CHIP_M + w_pt) * k - 1, (CHIP_M + dy + CHIP_H) * k - 1],
                radius=CHIP_R * k, fill=255)
            return m
        sh = rr(1.0).filter(ImageFilter.GaussianBlur(2.5 * k))   # blur 5pt = sigma 2.5pt
        a = np.asarray(sh).astype(np.float64) * 0.12
        a[np.asarray(rr(0.0)) > 0] = 0                           # 칩 안쪽 비움
        rgba = np.zeros((H, W, 4), np.uint8)
        rgba[..., 0], rgba[..., 1], rgba[..., 2] = 40, 28, 90
        rgba[..., 3] = np.round(a).astype(np.uint8)
        Image.fromarray(rgba, "RGBA").save(name, optimize=True)
    return "../" + name


def chip_shadow_tag(w_pt):
    """칩 안에 넣는 그림자 요소. 칩(position:relative) 뒤로 깔린다."""
    return ('<i style="position:absolute;left:-%gpt;top:-%gpt;'
            'width:calc(100%% + %gpt);height:calc(100%% + %gpt);z-index:-1;'
            "background:url('%s') 0 0/100%% 100%% no-repeat;"
            'pointer-events:none"></i>'
            % (CHIP_M, CHIP_M, 2 * CHIP_M, 2 * CHIP_M, chip_shadow(w_pt)))


def orb_png(c1, c2, angle=140, d_pt=12.0):
    """목차 색 점: linear-gradient(<angle>deg, c1, c2) 를 원에 칠한 PNG."""
    name = "assets/app_orb_%s_%s_%s.png" % (c1[1:], c2[1:], VERSION)
    if not os.path.exists(name):
        n, ss = int(d_pt * 8), 4
        N = n * ss
        yy, xx = np.mgrid[0:N, 0:N].astype(np.float64) + .5
        th = np.radians(angle)
        dx, dy = np.sin(th), -np.cos(th)           # CSS 각도: 0deg = 위쪽
        L = N * (abs(dx) + abs(dy))
        t = np.clip(((xx - N / 2) * dx + (yy - N / 2) * dy) / L + .5, 0, 1)
        col = lambda h: np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float)
        rgb = col(c1)[None, None, :] * (1 - t[..., None]) + col(c2)[None, None, :] * t[..., None]
        inside = ((xx - N / 2) ** 2 + (yy - N / 2) ** 2) <= (N / 2) ** 2
        rgba = np.dstack([rgb, inside * 255.0])
        img = Image.fromarray(np.round(rgba).astype(np.uint8), "RGBA")
        img.resize((n, n), Image.LANCZOS).save(name, optimize=True)
    return "../" + name


def chip_grid_shadow_tag(cols, rows, w_pt, gap_pt, pitch_pt, left_pt):
    """칩 격자 전체(rows 줄 x cols 칸)의 그림자를 PNG 한 장으로.

    칩마다 한 장이면 Weeks 목차에서 128번 그려 220ms, 줄마다 한 장이면
    8번에 174ms 였다(check_render B, 기준 150). 격자 한 장 + pt 당 2px.
    그림자는 흐린 모양이라 해상도를 낮춰도 티가 안 난다. 격자는 1fr 이라
    칩 위치가 계산된다: 칸 폭 w, 칸 간격 gap, 줄 간격 pitch, 격자 왼쪽 left.
    칩 묶음을 감싼 div(position:relative) 의 첫 자식으로 넣는다.
    해상도: pt 당 2px 에서 Days 목차가 153ms(10회 중앙값, 칩 없는 v0.3 은
    109). 반투명 이미지 합성 비용은 픽셀 수에 비례한다 -- pt 당 1px."""
    k = 1
    name = "assets/app_chipgrid_%d_%d_%d_%d_%s.png" % (
        cols, rows, round(w_pt * 4), round(pitch_pt * 4), VERSION)
    span_w = cols * w_pt + (cols - 1) * gap_pt
    span_h = (rows - 1) * pitch_pt + CHIP_H
    if not os.path.exists(name):
        W = int(round((span_w + 2 * CHIP_M) * k))
        H = int(round((span_h + 2 * CHIP_M) * k))
        def rr(dy):
            m = Image.new("L", (W, H), 0)
            d = ImageDraw.Draw(m)
            for r_ in range(rows):
                for i in range(cols):
                    x = CHIP_M + i * (w_pt + gap_pt)
                    y = CHIP_M + r_ * pitch_pt + dy
                    d.rounded_rectangle([x * k, y * k, (x + w_pt) * k - 1,
                                         (y + CHIP_H) * k - 1],
                                        radius=CHIP_R * k, fill=255)
            return m
        sh = rr(1.0).filter(ImageFilter.GaussianBlur(2.5 * k))
        a = np.asarray(sh).astype(np.float64) * 0.12
        a[np.asarray(rr(0.0)) > 0] = 0
        rgba = np.zeros((H, W, 4), np.uint8)
        rgba[..., 0], rgba[..., 1], rgba[..., 2] = 40, 28, 90
        rgba[..., 3] = np.round(a).astype(np.uint8)
        Image.fromarray(rgba, "RGBA").save(name, optimize=True)
    return ('<i style="position:absolute;left:%gpt;top:-%gpt;width:%gpt;'
            'height:%gpt;z-index:-1;'
            "background:url('../%s') 0 0/100%% 100%% no-repeat;"
            'pointer-events:none"></i>'
            % (left_pt - CHIP_M, CHIP_M, span_w + 2 * CHIP_M,
               span_h + 2 * CHIP_M, name))


# ------------------------------------------------------------------- 한지
HANJI_PX = 1.25            # pt 당 px. 0.75 는 섬유가 안 보이고, 2 는 렌더 평균 161ms,
                           # 1.5 는 최대 150ms(기준선). 1.25 = 평균 126 / 최대 136ms
HANJI_CLOUD = 1.0          # 구름무늬 세기
HANJI_FIBER = 2.5          # 섬유 결 세기. 1 은 안 보였고 4 는 긁힌 자국 같았다


def _hanji_texture(W, H, k, strength, seed=7):
    """한지 질감. 밝기 변화량(-/+) 배열을 돌려준다(0 = 변화 없음).

    · 구름무늬: 아주 낮은 주파수의 얼룩 (닥 섬유가 뭉친 곳과 성긴 곳)
    · 긴 섬유:  가늘고 긴 곡선. 대부분 종이보다 살짝 밝고, 일부는 살짝 어둡다
    · 섬유 티:  드문드문 짧고 어두운 조각 (닥 껍질)
    전부 아주 약하게 -- 괘선(#d3d8de)과 글자 대비를 해치면 안 된다."""
    rng = np.random.default_rng(seed)
    # 구름무늬
    n = rng.standard_normal((H // 8 + 2, W // 8 + 2))
    cloud = np.asarray(Image.fromarray(((n - n.min()) / (n.max() - n.min()) * 255)
                                       .astype(np.uint8)).resize((W, H), Image.BICUBIC)
                       .filter(ImageFilter.GaussianBlur(18 * k))).astype(np.float64)
    cloud = (cloud - cloud.mean()) / (cloud.std() + 1e-6) * 1.6
    # 섬유
    light = Image.new("L", (W, H), 0)
    dark = Image.new("L", (W, H), 0)
    dl, dd = ImageDraw.Draw(light), ImageDraw.Draw(dark)
    area = (W / k) * (H / k)                        # pt^2
    for i in range(int(area / 260)):                # 긴 섬유
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        ang = rng.uniform(0, np.pi)
        L = rng.uniform(18, 90) * k
        steps = int(L / (3 * k)) + 2
        pts = []
        for _ in range(steps):
            pts.append((x, y))
            ang += rng.normal(0, 0.18)
            x += np.cos(ang) * 3 * k
            y += np.sin(ang) * 3 * k
        wdt = max(1, int(round(rng.uniform(0.25, 0.6) * k)))
        if rng.random() < 0.8:
            dl.line(pts, fill=int(rng.uniform(90, 200)), width=wdt)
        else:
            dd.line(pts, fill=int(rng.uniform(60, 140)), width=wdt)
    for i in range(int(area / 2200)):               # 섬유 티
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        ang = rng.uniform(0, np.pi)
        L = rng.uniform(1.5, 5) * k
        dd.line([(x, y), (x + np.cos(ang) * L, y + np.sin(ang) * L)],
                fill=int(rng.uniform(150, 255)), width=max(1, int(0.6 * k)))
    light = np.asarray(light.filter(ImageFilter.GaussianBlur(0.35 * k))).astype(np.float64)
    dark = np.asarray(dark.filter(ImageFilter.GaussianBlur(0.35 * k))).astype(np.float64)
    return (strength * cloud * HANJI_CLOUD
            + HANJI_FIBER * strength * (light / 255 * 5.5 - dark / 255 * 5.0))


def _bake_hanji_sheet(path, w, s):
    """내지 배경(sheet) 을 pt 당 HANJI_PX 로, 한지 질감을 얹어 JPEG 로."""
    g = SHEET * PT
    base = (_mesh((0xF9, 0xF6, 0xFE), w=w, s=s).convert("RGB")
            .crop((int(g), int(g), int(_W - g), int(_H - g))))
    k = HANJI_PX
    Wp = int(round((PAGE_W - 2 * SHEET) * k))
    Hp = int(round((PAGE_H - 2 * SHEET) * k))
    rgb = np.asarray(base.resize((Wp, Hp), Image.BICUBIC)).astype(np.float64)
    t = _hanji_texture(Wp, Hp, k, HANJI_STRENGTH)
    # 한지는 살짝 따뜻하다 -- 밝아지는 쪽은 흰색으로, 어두워지는 쪽은 미색으로
    warm = np.array([1.0, 0.97, 0.90])
    out = rgb + np.where(t[..., None] >= 0, t[..., None], t[..., None] * warm)
    Image.fromarray(np.clip(np.round(out), 0, 255).astype(np.uint8), "RGB").save(
        path, quality=88, optimize=True)
    return path
