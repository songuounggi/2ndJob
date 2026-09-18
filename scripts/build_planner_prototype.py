# -*- coding: utf-8 -*-
"""Build a 5-page hyperlinked ADHD/wellness digital planner prototype.

Design language follows the reference admin UI: white cards on a very
light background, a single green accent, vertical-bar section headers,
tinted chips, soft grey filled fields, and restrained diffuse shadows.
"""

import os
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas

W, H = 612, 792  # Letter portrait

# ---------------------------------------------------------------- palette --
BG       = HexColor("#F4F6F5")
CARD     = HexColor("#FFFFFF")
ACCENT   = HexColor("#12855C")
ACCENT_T = HexColor("#E7F2EC")   # tinted chip background
INK      = HexColor("#22262B")
INK_MID  = HexColor("#5A616B")
INK_SOFT = HexColor("#9AA0A8")
LINE     = HexColor("#E4E7E6")
FIELD    = HexColor("#F3F5F4")

FONT, FONT_B = "Helvetica", "Helvetica-Bold"

# ------------------------------------------------------------- geometry --
TAB_W     = 58
CONTENT_X = TAB_W + 28
CONTENT_R = W - 28
CONTENT_W = CONTENT_R - CONTENT_X
GAP       = 12
R_CARD    = 10
R_FIELD   = 6

TABS = [
    ("cover",   "COVER"),
    ("monthly", "MONTH"),
    ("weekly",  "WEEK"),
    ("daily",   "DAY"),
    ("habits",  "HABITS"),
]


# ---------------------------------------------------------------- helpers --
def paper(c):
    c.setFillColor(BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)


def soft_shadow(c, x, y, w, h, r, spread=1.0, layers=14, alpha=0.0045):
    """Directional drop shadow, as if lit from above.

    PDF has no blur filter, so the shadow is built from stacked
    translucent rounded rects. Two passes:

    1. Halo -- offset outlines expanded per side (barely any above, some
       at the sides, more below), giving the `0 Npx Mpx` direction.
    2. Bottom pool -- layers that grow *narrower* as they reach further
       down. Only the middle is covered by every layer, so the bottom
       shadow deepens toward the centre and thins out at both ends, the
       way a real blur rounds off at the corners.
    """
    c.saveState()
    c.setFillColor(black)
    c.setFillAlpha(alpha)

    s_top, s_side, s_bot = 1.5 * spread, 5.0 * spread, 6.0 * spread
    for i in range(layers, 0, -1):
        t = i / layers
        et, es, eb = s_top * t, s_side * t, s_bot * t
        c.roundRect(x - es, y - eb, w + 2 * es, h + et + eb, r + es,
                    fill=1, stroke=0)

    pool_n = 12
    pool_depth = 12.0 * spread
    pool_inset = w * 0.38
    for j in range(pool_n, 0, -1):
        u = j / pool_n
        ix, d = pool_inset * u, pool_depth * u
        pw, ph = w - 2 * ix, d + 16
        if pw <= 4:
            continue
        c.roundRect(x + ix, y - d, pw, ph,
                    min(r + d, pw / 2, ph / 2), fill=1, stroke=0)
    c.restoreState()


def card(c, x, y, w, h, r=R_CARD, spread=1.0):
    soft_shadow(c, x, y, w, h, r, spread=spread)
    c.setFillColor(CARD)
    c.roundRect(x, y, w, h, r, fill=1, stroke=0)


def bar_label(c, x, y, text, size=10, color=INK, bar_h=11):
    """Section header: short green vertical bar + bold label."""
    c.setFillColor(ACCENT)
    c.rect(x, y - 1, 2.6, bar_h, fill=1, stroke=0)
    c.setFillColor(color)
    c.setFont(FONT_B, size)
    c.drawString(x + 9, y + 1, text)


def chip(c, x, y, text, size=7.5, pad=8, h=15,
         bg=ACCENT_T, fg=ACCENT):
    w = c.stringWidth(text, FONT_B, size) + pad * 2
    c.setFillColor(bg)
    c.roundRect(x, y, w, h, h / 2, fill=1, stroke=0)
    c.setFillColor(fg)
    c.setFont(FONT_B, size)
    c.drawString(x + pad, y + h / 2 - size / 2 + 0.8, text)
    return w


def field(c, x, y, w, h=20, r=R_FIELD):
    """Soft grey filled input area."""
    c.setFillColor(FIELD)
    c.roundRect(x, y, w, h, r, fill=1, stroke=0)


def checkbox(c, x, y, size):
    c.setStrokeColor(HexColor("#C9D2CE"))
    c.setLineWidth(1)
    c.roundRect(x, y, size, size, 2.5, fill=0, stroke=1)


def rule(c, x1, y, x2, color=LINE):
    c.setStrokeColor(color)
    c.setLineWidth(0.8)
    c.line(x1, y, x2, y)


def tab_bar(c, current_key):
    seg_h = H / len(TABS)
    c.setFillColor(BG)
    c.rect(0, 0, TAB_W, H, fill=1, stroke=0)
    rule_x = TAB_W
    c.setStrokeColor(LINE)
    c.setLineWidth(0.8)
    c.line(rule_x, 0, rule_x, H)

    for i, (key, label) in enumerate(TABS):
        y0 = H - (i + 1) * seg_h
        mid = y0 + seg_h / 2
        is_current = key == current_key

        if is_current:
            card(c, 7, mid - 48, TAB_W - 14, 96, r=10, spread=0.8)
            c.setFillColor(ACCENT)
            c.rect(14, mid - 20, 2.4, 40, fill=1, stroke=0)

        c.saveState()
        c.translate(TAB_W / 2 + 7, mid)
        c.rotate(90)
        c.setFillColor(ACCENT if is_current else INK_SOFT)
        c.setFont(FONT_B if is_current else FONT, 9)
        c.drawCentredString(0, 0, label)
        c.restoreState()

        c.linkRect("", key, (0, y0, TAB_W, y0 + seg_h), relative=0, thickness=0)


def header(c, section, title, y_top=H - 56):
    bar_label(c, CONTENT_X, y_top, section, size=10, color=INK_MID)
    c.setFillColor(INK)
    c.setFont(FONT_B, 23)
    c.drawString(CONTENT_X, y_top - 34, title)
    return y_top - 34 - 26


def footer_hint(c):
    c.setFillColor(INK_SOFT)
    c.setFont(FONT, 7.5)
    c.drawString(CONTENT_X, 22,
                 "Tap a tab on the left to jump between sections "
                 "(GoodNotes / Notability / Xodo / Acrobat).")


# ================================================================= PAGES ==
def page_cover(c):
    paper(c)
    cx = (W + TAB_W) / 2

    c.setFillColor(ACCENT)
    c.rect(cx - 14, H - 150, 28, 2.6, fill=1, stroke=0)

    w = c.stringWidth("UNDATED DIGITAL PLANNER", FONT_B, 7.5) + 16
    chip(c, cx - w / 2, H - 182, "UNDATED DIGITAL PLANNER")

    c.setFillColor(INK)
    c.setFont(FONT_B, 31)
    c.drawCentredString(cx, H - 224, "2026 ADHD &")
    c.drawCentredString(cx, H - 260, "Wellness Planner")

    c.setFillColor(INK_MID)
    c.setFont(FONT, 11)
    c.drawCentredString(cx, H - 288, "Monthly  ·  Weekly  ·  Daily  ·  Habit Tracker")

    card_x = CONTENT_X + 26
    card_w = (W - card_x) - 26
    card_y, card_h = 196, 232
    card(c, card_x, card_y, card_w, card_h, r=12)

    bar_label(c, card_x + 20, card_y + card_h - 34, "What's inside", size=11)

    items = [
        ("Monthly overview", "big-picture view, low visual clutter", "12"),
        ("Weekly spread",    "brain dump + top 3 priorities",        "52"),
        ("Daily page",       "time blocks, energy & meds tracker",   "365"),
        ("Habit tracker",    "simple grid, no guilt streaks",        "12"),
    ]
    yy = card_y + card_h - 68
    for title, desc, count in items:
        c.setFillColor(ACCENT)
        c.circle(card_x + 24, yy + 3, 2.6, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont(FONT_B, 10)
        c.drawString(card_x + 36, yy, title)
        c.setFillColor(INK_SOFT)
        c.setFont(FONT, 8.5)
        c.drawString(card_x + 36, yy - 13, desc)
        cw = c.stringWidth(count, FONT_B, 7.5) + 16
        chip(c, card_x + card_w - 20 - cw, yy - 4, count)
        if title != items[-1][0]:
            rule(c, card_x + 20, yy - 25, card_x + card_w - 20)
        yy -= 46

    tab_bar(c, "cover")
    footer_hint(c)


def page_monthly(c):
    paper(c)
    top = header(c, "Monthly Overview", "January 2026")

    grid_y = 96
    grid_h = top - grid_y
    card(c, CONTENT_X, grid_y, CONTENT_W, grid_h, r=R_CARD)

    pad = 16
    inner_x = CONTENT_X + pad
    inner_w = CONTENT_W - 2 * pad
    inner_top = grid_y + grid_h - pad
    inner_bottom = grid_y + pad

    cols, rows = 7, 5
    cell_w = inner_w / cols
    head_h = 22
    cell_h = (inner_top - inner_bottom - head_h) / rows

    days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    c.setFont(FONT_B, 7.5)
    for i, d in enumerate(days):
        c.setFillColor(ACCENT if i >= 5 else INK_SOFT)
        c.drawCentredString(inner_x + i * cell_w + cell_w / 2, inner_top - 13, d)
    rule(c, inner_x, inner_top - head_h, inner_x + inner_w)

    grid_top = inner_top - head_h
    n = 1
    for r in range(rows):
        for col in range(cols):
            x = inner_x + col * cell_w
            y = grid_top - (r + 1) * cell_h
            c.setStrokeColor(LINE)
            c.setLineWidth(0.7)
            c.rect(x, y, cell_w, cell_h, fill=0, stroke=1)
            if n <= 31:
                c.setFillColor(ACCENT if col >= 5 else INK)
                c.setFont(FONT_B, 8.5)
                c.drawString(x + 6, y + cell_h - 14, str(n))
                n += 1

    c.setFillColor(INK_MID)
    c.setFont(FONT_B, 8.5)
    c.drawString(CONTENT_X, grid_y - 21, "This month's focus")
    field(c, CONTENT_X + 106, grid_y - 27, CONTENT_W - 106, 20)

    tab_bar(c, "monthly")
    footer_hint(c)


def page_weekly(c):
    paper(c)
    top = header(c, "Weekly Spread", "Jan 5 – 11")

    bottom = 96
    total_h = top - bottom
    left_w = CONTENT_W * 0.58
    right_x = CONTENT_X + left_w + GAP
    right_w = CONTENT_W - left_w - GAP

    # ---- left: seven day rows ----
    card(c, CONTENT_X, bottom, left_w, total_h, r=R_CARD)
    pad = 14
    row_h = (total_h - 2 * pad) / 7
    for i, d in enumerate(["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]):
        row_top = bottom + total_h - pad - i * row_h
        cy = row_top - row_h / 2
        chip(c, CONTENT_X + pad, cy + 6, d,
             bg=ACCENT_T if i < 5 else FIELD,
             fg=ACCENT if i < 5 else INK_MID)
        if i < 6:
            rule(c, CONTENT_X + pad, row_top - row_h, CONTENT_X + left_w - pad)

    # ---- right: stacked cards ----
    h_energy = 88
    remaining = total_h - 2 * GAP - h_energy
    h_dump, h_top3 = remaining * 0.55, remaining * 0.45

    y_dump = bottom + total_h - h_dump
    y_top3 = y_dump - GAP - h_top3
    y_energy = y_top3 - GAP - h_energy

    card(c, right_x, y_dump, right_w, h_dump, r=R_CARD)
    bar_label(c, right_x + 14, y_dump + h_dump - 26, "Brain Dump", size=9)
    body_top, body_bottom = y_dump + h_dump - 48, y_dump + 14
    n_lines = max(3, int((body_top - body_bottom) / 22))
    step = (body_top - body_bottom) / n_lines
    for i in range(n_lines):
        rule(c, right_x + 14, body_top - i * step, right_x + right_w - 14)

    card(c, right_x, y_top3, right_w, h_top3, r=R_CARD)
    bar_label(c, right_x + 14, y_top3 + h_top3 - 26, "Top 3 Priorities", size=9)
    body_top, body_bottom = y_top3 + h_top3 - 50, y_top3 + 18
    step = (body_top - body_bottom) / 3
    for i in range(3):
        yy = body_top - i * step
        checkbox(c, right_x + 14, yy - 5, 12)
        field(c, right_x + 34, yy - 7, right_w - 50, 17)

    card(c, right_x, y_energy, right_w, h_energy, r=R_CARD)
    bar_label(c, right_x + 14, y_energy + h_energy - 26, "Energy Level", size=9)
    mid = y_energy + 30
    span = right_w - 60
    for i in range(5):
        cx = right_x + 30 + i * (span / 4)
        checkbox(c, cx - 7, mid - 7, 14)
    c.setFillColor(INK_SOFT)
    c.setFont(FONT, 7)
    c.drawCentredString(right_x + 30, mid - 20, "low")
    c.drawCentredString(right_x + 30 + span, mid - 20, "high")

    tab_bar(c, "weekly")
    footer_hint(c)


def page_daily(c):
    paper(c)
    top = header(c, "Daily Page", "Monday, Jan 5")

    bottom = 96
    banner_h = 36
    card(c, CONTENT_X, top - banner_h, CONTENT_W, banner_h, r=R_CARD, spread=0.75)
    bar_label(c, CONTENT_X + 14, top - banner_h / 2 - 4, "Today's #1 priority", size=9)
    field(c, CONTENT_X + 158, top - banner_h / 2 - 10, CONTENT_W - 172, 20)

    content_top = top - banner_h - GAP
    total_h = content_top - bottom
    left_w = CONTENT_W * 0.56
    right_x = CONTENT_X + left_w + GAP
    right_w = CONTENT_W - left_w - GAP

    # ---- left: hour blocks ----
    card(c, CONTENT_X, bottom, left_w, total_h, r=R_CARD)
    pad = 14
    hours = ["7 AM", "9 AM", "11 AM", "1 PM", "3 PM", "5 PM", "7 PM", "9 PM"]
    row_h = (total_h - 2 * pad) / len(hours)
    for i, hl in enumerate(hours):
        row_top = bottom + total_h - pad - i * row_h
        c.setFillColor(INK_SOFT)
        c.setFont(FONT_B, 7.5)
        c.drawString(CONTENT_X + pad, row_top - row_h / 2 - 3, hl)
        if i < len(hours) - 1:
            rule(c, CONTENT_X + pad, row_top - row_h, CONTENT_X + left_w - pad)

    # ---- right: stacked cards ----
    h_meds = total_h * 0.26
    h_mood = total_h * 0.26
    h_dump = total_h - h_meds - h_mood - 2 * GAP

    y_meds = bottom + total_h - h_meds
    y_mood = y_meds - GAP - h_mood
    y_dump = y_mood - GAP - h_dump

    card(c, right_x, y_meds, right_w, h_meds, r=R_CARD)
    bar_label(c, right_x + 14, y_meds + h_meds - 24, "Meds / Water", size=9)
    rows = [("Meds", 2), ("Water", 8)]
    body_top, body_bottom = y_meds + h_meds - 46, y_meds + 16
    step = (body_top - body_bottom) / len(rows)
    for i, (label, count) in enumerate(rows):
        yy = body_top - i * step
        c.setFillColor(INK_SOFT)
        c.setFont(FONT, 7.5)
        c.drawString(right_x + 14, yy - 3, label)
        box = 11 if count > 4 else 13
        gap = min(19, (right_w - 62) / count)
        for j in range(count):
            checkbox(c, right_x + 48 + j * gap, yy - 5, box)

    card(c, right_x, y_mood, right_w, h_mood, r=R_CARD)
    bar_label(c, right_x + 14, y_mood + h_mood - 24, "Mood Today", size=9)
    faces = ["Low", "OK", "Good", "Great"]
    fy = y_mood + h_mood / 2 - 14
    fw = (right_w - 28) / len(faces)
    for i, f in enumerate(faces):
        cx = right_x + 14 + fw * i + fw / 2
        checkbox(c, cx - 7, fy, 14)
        c.setFillColor(INK_SOFT)
        c.setFont(FONT, 7)
        c.drawCentredString(cx, fy - 14, f)

    card(c, right_x, y_dump, right_w, h_dump, r=R_CARD)
    bar_label(c, right_x + 14, y_dump + h_dump - 24, "Brain Dump", size=9)
    body_top, body_bottom = y_dump + h_dump - 46, y_dump + 14
    n_lines = max(2, int((body_top - body_bottom) / 21))
    step = (body_top - body_bottom) / n_lines
    for i in range(n_lines):
        rule(c, right_x + 14, body_top - i * step, right_x + right_w - 14)

    tab_bar(c, "daily")
    footer_hint(c)


def page_habits(c):
    paper(c)
    top = header(c, "Habit Tracker", "January 2026")

    bottom = 96
    total_h = top - bottom
    card(c, CONTENT_X, bottom, CONTENT_W, total_h, r=R_CARD)

    habits = ["Water", "Meds", "Movement", "Sleep 7h+", "Journal", "Tidy 10 min",
              "Outside time", "Screen cutoff", "Meals", "Connect w/ someone"]
    days = list(range(1, 32))

    pad = 16
    label_w = 104
    grid_x = CONTENT_X + pad + label_w
    grid_w = CONTENT_X + CONTENT_W - pad - grid_x
    head_h = 16
    row_h = 25
    grid_top = bottom + total_h - pad - head_h
    grid_bottom = grid_top - row_h * len(habits)
    col_w = grid_w / len(days)

    c.setFont(FONT_B, 5.6)
    for d in days:
        x = grid_x + (d - 1) * col_w
        c.setFillColor(ACCENT if (d % 7) in (6, 0) else INK_SOFT)
        c.drawCentredString(x + col_w / 2, grid_top + 5, str(d))

    for i, hb in enumerate(habits):
        y = grid_top - (i + 1) * row_h
        if i % 2 == 0:
            c.setFillColor(FIELD)
            c.rect(CONTENT_X + pad, y, label_w + grid_w, row_h, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont(FONT, 8.5)
        c.drawString(CONTENT_X + pad + 6, y + row_h / 2 - 3, hb)

    for d in days:
        x = grid_x + (d - 1) * col_w
        c.setStrokeColor(LINE)
        c.setLineWidth(0.6)
        c.line(x, grid_bottom, x, grid_top)
    for i in range(len(habits) + 1):
        y = grid_top - i * row_h
        c.setStrokeColor(LINE)
        c.setLineWidth(0.7)
        c.line(grid_x, y, grid_x + grid_w, y)

    refl_top = grid_bottom - 32
    col_gap = 18
    refl_w = (label_w + grid_w - col_gap) / 2
    for i, title in enumerate(["What worked this month", "What to adjust"]):
        x = CONTENT_X + pad + i * (refl_w + col_gap)
        bar_label(c, x, refl_top, title, size=8.5, color=INK_MID, bar_h=10)
        body_top, body_bottom = refl_top - 24, bottom + pad
        n_lines = max(2, int((body_top - body_bottom) / 23))
        step = (body_top - body_bottom) / n_lines
        for j in range(n_lines):
            rule(c, x, body_top - j * step, x + refl_w)

    tab_bar(c, "habits")
    footer_hint(c)


def build(path):
    c = canvas.Canvas(path, pagesize=(W, H))
    c.setTitle("2026 ADHD & Wellness Planner - Prototype")

    pages = [
        ("cover", page_cover),
        ("monthly", page_monthly),
        ("weekly", page_weekly),
        ("daily", page_daily),
        ("habits", page_habits),
    ]
    for i, (key, fn) in enumerate(pages):
        c.bookmarkPage(key)
        fn(c)
        if i < len(pages) - 1:
            c.showPage()
    c.save()


if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "adhd_wellness_planner_prototype.pdf")
    build(out_path)
    print("Saved:", os.path.abspath(out_path))
