# -*- coding: utf-8 -*-
"""셀페이드 -- 점선을 칸(셀)마다 양 끝이 흐려지게 긋는다. 상품 중립.

    import dashfade as DF
    paths = DF.h_cells(x0, x1, ys)                  # 가로선: 한 칸(열) 폭
    paths += DF.v_cells(xs, cells, y0, offset)      # 세로선: 칸(행)마다
    svg = '<svg ... fill="none" stroke-width="0.75" stroke-dasharray="4 4">'
          + "".join(paths) + '</svg>'

약어: **셀페이드** (`/cellfade`). 쓰는 법과 규칙은 `.claude/skills/cellfade/SKILL.md`.

왜 이렇게 만드는가 (2026-09-24, 상품 2 student-v0.3~v0.6)
  · 그라데이션 stroke 로 흐리면 PDF 에서 셰이딩 + 소프트마스크가 되어 iPad
    GoodNotes 가 바둑판처럼 느리게 그린다(RELEASE.md). 대신 **끝쪽 점을
    옅은 단색(stroke-opacity, PDF 고정 알파 /CA)으로** 긋는다
  · 점 단위로 옅게 하면 좁은 칸(점 2~3개)에서 흐림이 안 보인다. 페이드 구간의
    점은 **1pt 조각(piece)으로 쪼개** 조각 중심에서 그라데이션을 샘플링한다
  · 흐림은 **칸마다**: 가로선은 열 폭 [x0, x1] 의 양 끝, 세로선은 행 높이의
    위아래 끝. 선 전체의 양 끝이 아니다(사용자 지적)
  · 점 위치는 흐림을 넣기 전과 같아야 한다. 세로선은 행 경계마다 틈이 오도록
    dashoffset 을 민 선이라, 브라우저 규칙 (t + offset) mod period < dash 를
    그대로 따라 점을 찍는다
  · 불투명도 1 인 가운데 구간은 dasharray 가 걸린 path 한 줄 -- 바이트를 아낀다.
    그래서 **감싸는 <svg> 에 stroke-dasharray 가 있어야** 한다

좌표 단위는 호출하는 쪽 SVG 의 사용자 단위다(pt viewBox 권장). 인자의 기본값은
상품 2 의 값(점 4 / 주기 8 / 페이드 24 / 조각 1 / 눈금 0.1).
"""

DASH = 4.0          # 점 길이
PERIOD = 8.0        # 점 + 틈
FADE = 24.0         # 끝에서 이만큼 안쪽까지 흐려진다 (칸이 짧으면 칸 길이의 1/3)
PIECE = 1.0         # 페이드 구간 점을 쪼개는 조각 길이. 0 이면 점 단위
STEP = 0.1          # 불투명도 눈금. 같은 값끼리 path 하나로 묶는다
COLOR = "#d3d8de"


def _alpha(c, a0, a1, f, step):
    a = min(1.0, max(0.0, min(c - a0, a1 - c) / f))
    return round(a / step) * step


def _paths(groups, full_d, color):
    out = []
    if full_d:
        out.append('<path stroke="%s" d="%s"/>' % (color, full_d))
    for a, d in sorted(groups.items()):
        op = "" if a >= 1.0 else ' stroke-opacity="%g"' % a
        out.append('<path stroke="%s"%s stroke-dasharray="none" d="%s"/>'
                   % (color, op, d))
    return out


def h_cells(x0, x1, ys, dash=DASH, period=PERIOD, fade=FADE, piece=PIECE,
            step=STEP, color=COLOR):
    """가로 점선 한 칸(열) 폭 [x0, x1] 을 여러 행 ys 에 긋는다. 양 끝 흐림.
    점은 x0 에서 시작해 period 마다 dash 길이."""
    L = x1 - x0
    f = min(fade, L / 3.0)
    full, part = [], {}
    s0 = x0
    while s0 < x1 - 1e-6:
        e = min(s0 + dash, x1)
        if piece and min(s0 - x0, x1 - e) < f:
            y = s0
            while y < e - 1e-6:
                ye = min(y + piece, e)
                a = _alpha((y + ye) / 2, x0, x1, f, step)
                if a > 0:
                    part.setdefault(round(a, 2), []).append((y, ye))
                y = ye
            s0 += period
            continue
        a = _alpha((s0 + e) / 2, x0, x1, f, step)
        if a >= 1.0:
            full.append((s0, e))
        elif a > 0:
            part.setdefault(round(a, 2), []).append((s0, e))
        s0 += period
    full_d = ""
    if full:
        a0, b0 = full[0][0], full[-1][1]
        full_d = "".join("M%.2f %.2fH%.2f" % (a0, y, b0) for y in ys)
    groups = {a: "".join("M%.2f %.2fH%.2f" % (p0, y, p1)
                         for y in ys for p0, p1 in segs)
              for a, segs in part.items()}
    return _paths(groups, full_d, color)


def v_cells(xs, cells, y0, offset, inset=2.0, dash=DASH, period=PERIOD,
            fade=FADE, piece=PIECE, step=STEP, color=COLOR):
    """세로 점선을 칸(행)마다 위아래 끝이 흐려지게. xs: 세로선 x 들.
    cells: [(칸 위, 칸 아래), ...]. 흐림은 [위+inset, 아래-inset] 에서.
    점 위치: 원래 선이 y0 에서 시작하고 stroke-dashoffset=offset 이었다면
    그 선과 같은 자리 -- (t + offset) mod period < dash."""
    groups = {}
    for top, bot in cells:
        c0, c1 = top + inset, bot - inset
        f = min(fade, (c1 - c0) / 3.0)
        k = int((c0 - y0 + offset) // period) - 1
        while True:
            ds = y0 - offset + k * period
            if ds >= c1:
                break
            a0, b0 = max(ds, c0), min(ds + dash, c1)
            k += 1
            if b0 <= a0:
                continue
            y = a0
            while y < b0 - 1e-6:
                e = min(y + (piece or dash), b0)
                a = _alpha((y + e) / 2, c0, c1, f, step)
                if a > 0:
                    groups.setdefault(round(a, 2), []).append((y, e))
                y = e
    out = []
    for a, ss in sorted(groups.items()):
        op = "" if a >= 1.0 else ' stroke-opacity="%g"' % a
        out.append('<path stroke="%s"%s stroke-dasharray="none" d="%s"/>'
                   % (color, op, "".join("M%.2f %.2fV%.2f" % (x, p0, p1)
                                         for x in xs for p0, p1 in ss)))
    return out


def table_svg(widths, n_rows, head_h=24.0, row_h=24.0, inset=8.0, inset_v=2.0,
              thick=0.75, **kw):
    """표 한 장의 구분선 전부 -- 셀페이드 적용판. 새 상품이 표를 그릴 때 이것
    하나로 끝낸다. 마감선은 긋지 않는다(표가 곧 면일 때. LINES.md 2 절 예외)."""
    dash = kw.get("dash", DASH)
    period = kw.get("period", PERIOD)
    w_tot, H = sum(widths), head_h + n_rows * row_h
    body, x, bounds = [], 0.0, []
    for w in widths:
        body += h_cells(x + inset, x + w - inset,
                        [head_h + r * row_h for r in range(1, n_rows)], **kw)
        x += w
        bounds.append(x)
    cells = [(0.0, head_h)] + [(head_h + r * row_h, head_h + (r + 1) * row_h)
                               for r in range(n_rows)]
    body += v_cells(bounds[:-1], cells, inset_v, period - dash / 2 - inset_v,
                    inset=inset_v, **kw)
    return ('<svg viewBox="0 0 %.2f %.2f" width="%.2fpt" height="%.2fpt" '
            'xmlns="http://www.w3.org/2000/svg" fill="none" stroke-width="%.2f" '
            'stroke-dasharray="%g %g">%s</svg>'
            % (w_tot, H, w_tot, H, thick, dash, period - dash, "".join(body)))


def ruled_svg(w_pt, rows, row_h=24.0, thick=0.75, **kw):
    """필기칸 괘선 -- 셀페이드 적용판. 줄 rows-1 개(맨 아래 행은 면 가장자리가
    닫는다). 면 크기에 맞춰 늘어나도록 viewBox 를 pt 로 둔다."""
    dash = kw.get("dash", DASH)
    period = kw.get("period", PERIOD)
    hv = rows * row_h - row_h / 2
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.2f %.2f" '
            'preserveAspectRatio="none" fill="none" stroke-width="%.2f" '
            'stroke-dasharray="%g %g">%s</svg>'
            % (w_pt, hv, thick, dash, period - dash,
               "".join(h_cells(0.0, w_pt, [n * row_h for n in range(1, rows)],
                               **kw))))


if __name__ == "__main__":
    # 자체 검사: 그라데이션·마스크가 없고, 끝 조각이 옅고, 가운데는 불투명
    s = table_svg([226.05, 123.3, 102.75, 61.65], 5)
    assert "Gradient" not in s and "mask" not in s
    assert 'stroke-opacity="0.1"' in s and 'stroke-dasharray="none"' in s
    r = ruled_svg(497.75, 10)
    assert r.count("<path") >= 2
    print("dashfade ok  table %d B  ruled %d B" % (len(s), len(r)))
