# -*- coding: utf-8 -*-
"""Generate the ADHD/wellness planner as HTML, then print it to PDF with Chrome.

Pipeline per CLAUDE.md: HTML/CSS -> headless Chrome print-to-PDF, which keeps
internal `#anchor` links as PDF named destinations.
"""

import calendar
import io
import json
import os
import re
import tempfile
import urllib.parse
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
YEAR = 2026
MONTHS = 12
DAYS = 31
WEEKS = 52

TABS = [
    ("index",  "INDEX"),
    ("year",   "YEAR"),
    ("month",  "MONTH"),
    ("week",   "WEEK"),
    ("day",    "DAY"),
    ("focus",  "FOCUS"),
    ("feel",   "FEELINGS"),
    ("habits", "HABITS"),
    ("health", "HEALTH"),
    ("life",   "LIFE"),
    ("notes",  "NOTES"),
]

# Sub-pages reached from a tab's own index page. The rail holds categories;
# these are the unique templates underneath, which is where a planner's real
# depth lives (the category leader ships ~190 of them, we are building up).
GROUPS = {
    "year": [("month", "Twelve months", "write the month in yourself"),
             ("quarterly", "Quarterly", "three months at a time"),
             ("goals", "Goals", "what you want, made specific"),
             ("review", "Monthly review", "what actually happened"),
              ("project", "Project planner", "one thing, start to finish"),
              ("weekly-review", "Weekly review", "five minutes, once a week"),
              ("vision", "Vision page", "what you are aiming at"),],
    "focus": [("tasks", "Task breakdown", "break the big thing down"),
              ("braindump", "Brain dump", "get it out of your head"),
              ("session", "Focus session", "one timed block at a time"),
              ("obstacle", "Obstacle plan", "name it before it stops you"),
              ("paralysis", "Stuck on deciding", "when you cannot pick"),
              ("mindmap", "Mind map", "when it will not go in a list"),
              ("hyperfocus", "Hyperfocus log", "where the hours went"),
              ("screen", "Screen time", "the quiet one that eats evenings"),
              ("estimate", "Guess vs actual", "how long things really take"),
              ("avoiding", "Why I am avoiding it", "the reason is usually small"),
              ("deadline", "Working backwards", "from the date, not from today"),],
    "feel":  [("sta", "Stop \u00b7 Think \u00b7 Act", "before you react"),
              ("worry", "Cycle of worry", "break the loop"),
              ("rsd", "Rejection sensitivity", "when it stings too much"),
              ("kind", "Talk to yourself kindly", "answer the inner critic"),
              ("dose", "D.O.S.E.", "four things your brain runs on"),
              ("gratitude", "Gratitude", "small, specific, true"),
              ("reframe", "Reframe a belief", "the story you keep repeating"),
              ("name-it", "Name the feeling", "vague feelings stay louder"),
              ("boundaries", "Boundaries", "what you will and will not do"),
              ("energy", "Energy budget", "you have less than the day suggests"),],
    "habits": [("habits-grid", "Habit tracker", "31-day grid"),
               ("routines", "Morning &amp; evening", "the same few steps")],
    "health": [("meds", "Medication log", "dose and how it felt"),
               ("sleep", "Sleep", "hours in, energy out"),
               ("symptoms", "Symptom tracker", "patterns your doctor will ask for"),
               ("doctor", "Doctor visit", "questions you will forget otherwise"),
               ("therapy", "Therapy notes", "before and after the session"),
              ("intake", "Water &amp; food", "the two that slip first"),
              ("movement", "Movement", "any amount counts"),
              ("cycle", "Cycle tracker", "symptoms often follow it"),],
    "life":  [("meals", "Meals &amp; groceries", "decide once, shop once"),
              ("wheel", "Wheel of life", "where things stand"),
              ("cleaning", "Cleaning", "rooms, not the whole house"),
              ("budget", "Monthly budget", "in, out, left"),
              ("impulse", "Before you buy it", "the 10-minute check"),
              ("reading", "Reading log", "books you actually finished"),
              ("dates", "Dates to remember", "birthdays, renewals, appointments"),
              ("subs", "Subscriptions", "what renews, when, how much"),
              ("travel", "Trip checklist", "packed, booked, charged"),
              ("chores", "Who does what", "split it before it festers"),],
}

# Four category colours, reused across every page in a group.
GROUP_OF = {}
for _g, _items in GROUPS.items():
    for _k, _n, _d in _items:
        GROUP_OF[_k] = _g

# --------------------------------------------------------------- themes --
# v2 follows the researched "adult ADHD self" palette: warm paper instead of
# white, and four category colours (the ceiling before colour coding starts
# hurting recall) mapped onto the section groups.
THEMES = {
    "v1-admin": {
        "font": "Inter", "weights": "400;600;700", "display": None,
        "radius": "10pt", "tab_dots": False,
        "bg": "#F4F6F5", "card": "#FFFFFF", "ink": "#22262B",
        "mid": "#5A616B", "soft": "#7C8087", "line": "#E4E7E6",
        "field": "#F3F5F4",
        "sections": {k: ("#12855C", "#E7F2EC", "#0F6E4C") for k, _ in TABS},
    },
    "v2-warm": {
        "font": "Nunito", "weights": "400;600;700;800", "display": None,
        "radius": "14pt", "tab_dots": True,
        "bg": "#FBF8F3", "card": "#FFFFFF", "ink": "#3A3A3A",
        "mid": "#6E6A64", "soft": "#827D75", "line": "#EAE4DA",
        "field": "#F6F2EA",
        # section -> (decorative accent, tint, text tone).
        # The pastel reads well as a bar/dot/fill but only hits ~2.5:1 as text,
        # so every coloured *word* uses the darker tone (>=4.8:1 on white).
        "sections": {
            "index":  ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "year":   ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "month":  ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "week":   ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "day":    ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "tasks":  ("#E08A73", "#FBEDE8", "#B4543A"),
            "habits": ("#E08A73", "#FBEDE8", "#B4543A"),
            "meds":   ("#7FA37C", "#ECF3EB", "#4A7248"),
            "notes":  ("#D9A441", "#FBF1DC", "#8A6415"),
        },
    },
    # v2 with the user's own sky photo washed into the page background.
    # Cards stay fully opaque so writing areas keep their contrast; only the
    # paper behind them carries the image.
    "v5-sky": {
        "font": "Nunito", "weights": "400;600;700;800", "display": None,
        "radius": "14pt", "tab_dots": True,
        "bg": "#FBF8F3", "card": "#FFFFFF", "ink": "#3A3A3A",
        "mid": "#6E6A64", "soft": "#827D75", "line": "#EAE4DA",
        "field": "#F6F2EA",
        "photo": "../assets/sky.jpg",
        "photo_cover": 0.20,   # showcase page, the photo is the point
        "photo_page": 0.0,     # working pages get the bloom only -- a photo
                               # behind handwriting is visual noise
        "bloom_cover": 0.42,
        "bloom_page": 0.55,
        # one faint cool stop, as first shipped
        "bloom_cool": [(-100, -12, 124, 92, "#B3C6D6", .26)],
        "sections": {
            "index":  ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "year":   ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "month":  ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "week":   ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "day":    ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "tasks":  ("#E08A73", "#FBEDE8", "#B4543A"),
            "habits": ("#E08A73", "#FBEDE8", "#B4543A"),
            "meds":   ("#7FA37C", "#ECF3EB", "#4A7248"),
            "notes":  ("#D9A441", "#FBF1DC", "#8A6415"),
        },
    },
    # v5 with the cool side of the bloom carried further left: the sky blue
    # builds over three stops and thins out toward the page edge.
    "v6-skyblue": {
        "font": "Nunito", "weights": "400;600;700;800", "display": None,
        "radius": "14pt", "tab_dots": True,
        "bg": "#FBF8F3", "card": "#FFFFFF", "ink": "#3A3A3A",
        "mid": "#6E6A64", "soft": "#827D75", "line": "#EAE4DA",
        "field": "#F6F2EA",
        "photo": "../assets/sky.jpg",
        "photo_cover": 0.20,
        "photo_page": 0.0,
        "bloom_cover": 0.42,
        "bloom_page": 0.55,
        "bloom_cool": [
            (-104, -14, 138, 100, "#AFC9DF", .34),  # sky blue picks up
            (-152, -22, 158, 108, "#A3C4E2", .30),  # wider, airier
            (-206, -30, 172, 112, "#B6D2EC", .22),  # fades out to the edge
        ],
        "sections": {
            "index":  ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "year":   ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "month":  ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "week":   ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "day":    ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "tasks":  ("#E08A73", "#FBEDE8", "#B4543A"),
            "habits": ("#E08A73", "#FBEDE8", "#B4543A"),
            "meds":   ("#7FA37C", "#ECF3EB", "#4A7248"),
            "notes":  ("#D9A441", "#FBF1DC", "#8A6415"),
        },
    },
    # v6 with the bloom lifted toward white. The sampled photo colours sit
    # darker than the cream paper, so the wash pulled the page down; blending
    # each stop toward white raises it without touching the hue relations.
    "v7-bright": {
        "font": "Nunito", "weights": "400;600;700;800", "display": None,
        "radius": "14pt", "tab_dots": True,
        "bg": "#FBF8F3", "card": "#FFFFFF", "ink": "#3A3A3A",
        "mid": "#6E6A64", "soft": "#827D75", "line": "#EAE4DA",
        "field": "#F6F2EA",
        "photo": "../assets/sky.jpg",
        "photo_cover": 0.14,
        "photo_page": 0.0,
        "bloom_cover": 0.42,
        "bloom_page": 0.55,
        "bloom_lift": 0.38,
        "bloom_cool": [
            (-104, -14, 138, 100, "#AFC9DF", .34),
            (-152, -22, 158, 108, "#A3C4E2", .30),
            (-206, -30, 172, 112, "#B6D2EC", .22),
        ],
        "sections": {
            "index":  ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "year":   ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "month":  ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "week":   ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "day":    ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "tasks":  ("#E08A73", "#FBEDE8", "#B4543A"),
            "habits": ("#E08A73", "#FBEDE8", "#B4543A"),
            "meds":   ("#7FA37C", "#ECF3EB", "#4A7248"),
            "notes":  ("#D9A441", "#FBF1DC", "#8A6415"),
        },
    },
    # v7's look, but undated and bulked out with the repeated daily and
    # weekly sets. `undated` swaps the calendar pages for positional ones.
    "v8-undated": {
        "font": "Nunito", "weights": "400;600;700;800", "display": None,
        "radius": "14pt", "tab_dots": True,
        "bg": "#FBF8F3", "card": "#FFFFFF", "ink": "#3A3A3A",
        "mid": "#6E6A64", "soft": "#827D75", "line": "#EAE4DA",
        "field": "#F6F2EA",
        "photo": "../assets/sky.jpg",
        "photo_cover": 0.14, "photo_page": 0.0,
        "bloom_cover": 0.42, "bloom_page": 0.55, "bloom_lift": 0.38,
        "bloom_cool": [
            (-104, -14, 138, 100, "#AFC9DF", .34),
            (-152, -22, 158, 108, "#A3C4E2", .30),
            (-206, -30, 172, 112, "#B6D2EC", .22),
        ],
        "undated": True,
        "sections": {
            "index":  ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "year":   ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "month":  ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "week":   ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "day":    ("#7FA8C9", "#EAF2F8", "#3E6E93"),
            "tasks":  ("#E08A73", "#FBEDE8", "#AC5038"),
            "habits": ("#E08A73", "#FBEDE8", "#AC5038"),
            "meds":   ("#7FA37C", "#ECF3EB", "#4A7248"),
            "notes":  ("#D9A441", "#FBF1DC", "#8A6415"),
        },
    },
    # Product 2. Same sky wash as v8, but on cool paper so it reads as a
    # separate product on the shelf. The four accents are deliberately
    # unchanged -- the shop has to look like one brand. Contrast was
    # re-measured on the new field colour; the worst case is 4.71:1
    # (rust on #EDF2F8), so every coloured word still clears 4.5:1.
    "v9-student": {
        "font": "Nunito", "weights": "400;600;700;800", "display": None,
        "radius": "14pt", "tab_dots": True,
        "bg": "#F4F7FA", "card": "#FFFFFF", "ink": "#333A42",
        "mid": "#64707C", "soft": "#7C8792", "line": "#E2E8EF",
        "field": "#EDF2F8",
        "photo": "../assets/sky.jpg",
        "photo_cover": 0.14, "photo_page": 0.0,
        "bloom_cover": 0.42, "bloom_page": 0.55, "bloom_lift": 0.38,
        "bloom_cool": [
            (-104, -14, 138, 100, "#AFC9DF", .34),
            (-152, -22, 158, 108, "#A3C4E2", .30),
            (-206, -30, 172, 112, "#B6D2EC", .22),
        ],
        "undated": True,
        "student": True,
        # 앱 UI 풍(유리). 켜면 scripts/app_style.py 가 CSS 와 배경을 맡는다.
        "app": True,
        # 학생용만 채도를 올린다. 색상(hue)은 v8/v9 그대로라 숍은 한 브랜드로
        # 남고, 매대에서만 덜 묻힌다. 이유는 "학생이 알록달록을 좋아해서"가
        # 아니라 경쟁 썸네일 사이에서 눈에 띄어야 하기 때문이다.
        #
        # OKLCh 로 계산했다. HLS 채도는 지각적이지 않아서 같은 배율을 먹이면
        # 그린만 형광으로 튀었다. 원래 팔레트는 채도가 제각각이었고
        # (블루 C=0.066, 머스터드 C=0.130) 그래서 네 색이 한 세트로 안 보였다.
        # 지금은 장식 C=0.135, 글자 C=0.130 으로 통일했다.
        #
        # 글자용은 카드/field/bg/칩 네 배경 전부에서 4.5:1 을 넘긴다(최저 4.65).
        # 칩 배경 위 대비를 빠뜨리지 말 것 -- .chip 은 틴트 위에 글자색을 얹는다.
        "sections": {
            "index":    ("#4BABF0", "#E4F3FE", "#026FAB"),
            "semester": ("#4BABF0", "#E4F3FE", "#026FAB"),
            "week":     ("#4BABF0", "#E4F3FE", "#026FAB"),
            "day":      ("#4BABF0", "#E4F3FE", "#026FAB"),
            "classes":  ("#EB8367", "#FEECE5", "#AD4F36"),
            "work":     ("#EB8367", "#FEECE5", "#AD4F36"),
            "study":    ("#62AC5D", "#E2F8DF", "#30782F"),
            "focus":    ("#62AC5D", "#E2F8DF", "#30782F"),
            "life":     ("#DBA339", "#FEF1D4", "#8C6305"),
            "notes":    ("#DBA339", "#FEF1D4", "#8C6305"),
        },
    },
    # Concept C -- "ink line". Lines and planes only: no pills, no rounded
    # corners, no photographic wash. The brief was an East-Asian ink-painting
    # feel that still reads modern, so the vocabulary is borrowed literally:
    # asymmetric negative space, one tapering brush rule under each title,
    # and a soft ink bleed in a single corner.
    #
    # The four category colours survive -- the recall research still applies --
    # but they are swapped for traditional pigment tones (vermilion, azurite,
    # malachite, ochre). Desaturated, so they read as pigment rather than UI.
    "v10-ink": {
        "font": "Inter", "weights": "400;500;600;700",
        "display": "Playfair Display",
        "radius": "0pt", "tab_dots": False,
        "bg": "#F2F1EB", "card": "#FDFCF9", "ink": "#1E2321",
        "mid": "#4E5651", "soft": "#6E7771", "line": "#D9DBD3",
        "field": "#ECEAE2",
        "ink_style": True,
        "ink_wash": "#1B2428",
        "undated": True,
        "student": True,
        "sections": {
            "index":    ("#5B87A8", "#E4ECF2", "#2E5C7A"),   # 群靑 azurite
            "semester": ("#5B87A8", "#E4ECF2", "#2E5C7A"),
            "week":     ("#5B87A8", "#E4ECF2", "#2E5C7A"),
            "day":      ("#5B87A8", "#E4ECF2", "#2E5C7A"),
            "classes":  ("#C2564A", "#F5E6E2", "#9B3226"),   # 朱 vermilion
            "work":     ("#C2564A", "#F5E6E2", "#9B3226"),
            "study":    ("#6E9B82", "#E6EFE9", "#3F6B54"),   # 石綠 malachite
            "focus":    ("#6E9B82", "#E6EFE9", "#3F6B54"),
            "life":     ("#C2A050", "#F5EEDD", "#7E6118"),   # 黃土 ochre
            "notes":    ("#C2A050", "#F5EEDD", "#7E6118"),
        },
    },
    # Palette B from the research: parents + teens. Sunset range, higher
    # saturation, rounder type -- reads as "made for me", not clinical.
    "v3-sunset": {
        "font": "Quicksand", "weights": "400;600;700", "display": None,
        "radius": "16pt", "tab_dots": True,
        "bg": "#FFF4E8", "card": "#FFFFFF", "ink": "#3B3335",
        "mid": "#6F625F", "soft": "#9A8C88", "line": "#F0E2D4",
        "field": "#FDF3E9",
        "sections": {
            "index":  ("#FF8A65", "#FFE8E0", "#B84A25"),
            "year":   ("#FF8A65", "#FFE8E0", "#B84A25"),
            "month":  ("#FF8A65", "#FFE8E0", "#B84A25"),
            "week":   ("#FF8A65", "#FFE8E0", "#B84A25"),
            "day":    ("#FF8A65", "#FFE8E0", "#B84A25"),
            "tasks":  ("#F06292", "#FDE4EC", "#A82A60"),
            "habits": ("#F06292", "#FDE4EC", "#A82A60"),
            "meds":   ("#4CAF7D", "#E3F4EA", "#2A6E4A"),
            "notes":  ("#9575CD", "#EDE7F8", "#5F429B"),
        },
    },
}

# 상품 2 는 상품 1 의 시안 번호(v1~v8)를 이어받지 않는다. 별개 제품이므로
# 제품 기준으로 센다: 개발 중 v0.x, 출시하면 v1.0, 이후 수정은 v1.1 ...
# v9-student 는 이 이름이 정해지기 전에 쓰던 키라 별칭으로만 남긴다.
THEMES["student-v0.1"] = THEMES["v9-student"]

# Revisions of a shipped product get their own version name and their own
# output file. The file a buyer already downloaded is never overwritten --
# if a fix turns out wrong we need the old one to compare against, and
# output/ is gitignored so git will not bring it back.
#   v8-undated    2026-09-21  출시본 (Etsy 에 올라간 것)
#   v8.1-undated  2026-09-23  선 일관성 수정
#   v8.2-undated  2026-09-23  flex:none 카드 부풀림 + Vision 카드 경로 통일
#   v8.3-undated  2026-09-23  괘선 바닥 정렬 시안 -- 첫 줄이 잘려 폐기
#   v8.4-undated  2026-09-23  카드 높이를 행 높이의 배수로 고정 (snap_cards)
#   v8.5-undated  2026-09-23  마지막 괘선이 래스터에서 사라지던 것 수정
#   v8.6-undated  2026-09-23  넉넉한 상자도 고정 + 표/행목록 가로 마감선
#   v8.7-undated  2026-09-23  여분 줄 8 -> 26 (행 안에 뚫리던 빈 공간)
#   v8.8-undated  2026-09-23  카드가 아니라 행을 고정 (좌우 높이·중간 구멍)
#   v8.9-undated  2026-09-23  표 좌측 바깥선 제거
#   v8.10-undated 2026-09-23  주 번호 격자 마지막 줄 정렬
#   v8.11-undated 2026-09-23  NOTES 를 1장에서 인덱스+20장으로
#   v8.12-undated 2026-09-23  NOTES 인덱스 칩이 카드 밖으로 잘리던 것
#   v8.13-undated 2026-09-23  접근성 태그 유지 + 노트 8장
#   v8.14-undated 2026-09-23  NOTES 인덱스 카드가 내용만큼만 차지하도록
#   v8.15-undated 2026-09-23  빈 행을 둔 표에 왼쪽 열 라벨
#   v8.16-undated 2026-09-23  표지 Notes 행 + 적는 칸 마감선 (마감선은 반려)
#   v8.17-undated 2026-09-23  표지 Notes 행만. 마감선 확장은 되돌림
#   v8.18-undated 2026-09-23  목록 9군데 마감선 제거 (표 11개는 유지)
#   v8.19-undated 2026-09-24  GoodNotes 바둑판 렌더링: 그림자·bloom 을 이미지로
#                             (fast_paint. 모양 그대로, 페이지당 렌더 약 4배 빠름)
THEMES["v8.1-undated"] = dict(THEMES["v8-undated"])
THEMES["v8.2-undated"] = dict(THEMES["v8-undated"])
THEMES["v8.3-undated"] = dict(THEMES["v8-undated"])
THEMES["v8.4-undated"] = dict(THEMES["v8-undated"])
THEMES["v8.5-undated"] = dict(THEMES["v8-undated"])
THEMES["v8.6-undated"] = dict(THEMES["v8-undated"])
THEMES["v8.7-undated"] = dict(THEMES["v8-undated"])
THEMES["v8.8-undated"] = dict(THEMES["v8-undated"])
THEMES["v8.9-undated"] = dict(THEMES["v8-undated"])
THEMES["v8.10-undated"] = dict(THEMES["v8-undated"])
THEMES["v8.11-undated"] = dict(THEMES["v8-undated"])
THEMES["v8.12-undated"] = dict(THEMES["v8-undated"])
THEMES["v8.13-undated"] = dict(THEMES["v8-undated"])
THEMES["v8.14-undated"] = dict(THEMES["v8-undated"])
THEMES["v8.15-undated"] = dict(THEMES["v8-undated"])
THEMES["v8.16-undated"] = dict(THEMES["v8-undated"])
THEMES["v8.17-undated"] = dict(THEMES["v8-undated"])
THEMES["v8.18-undated"] = dict(THEMES["v8-undated"])
THEMES["v8.19-undated"] = dict(THEMES["v8-undated"], fast_paint=True)

VERSION = os.environ.get("PLANNER_VERSION", "v2-warm")
if VERSION == "v9-student":
    VERSION = "student-v0.1"
T = THEMES[VERSION]
SRC = os.path.join(ROOT, "src", f"planner_{VERSION}.html")
OUT = os.path.join(ROOT, "output", f"planner_{VERSION}.pdf")

ROOT_VARS = f""":root{{
  --bg:{T['bg']}; --card:{T['card']}; --ink:{T['ink']}; --mid:{T['mid']};
  --soft:{T['soft']}; --line:{T['line']}; --field:{T['field']};
  --radius:{T['radius']}; --font:'{T['font']}';
  --display:'{T['display'] or T['font']}';
  --accent:#12855C; --chip:#E7F2EC; --accent-text:#0F6E4C;
}}"""

BASE_CSS = """
*{box-sizing:border-box;-webkit-print-color-adjust:exact;print-color-adjust:exact}
@page{size:612pt 792pt;margin:0}
body{margin:0;font-family:var(--font),system-ui,sans-serif;color:var(--ink);
     -webkit-font-smoothing:antialiased}

.page{width:612pt;height:792pt;background:var(--bg);position:relative;
      page-break-after:always;overflow:hidden}
.page:last-child{page-break-after:auto}
/* Background wash layers. They sit under everything and never under a card's
   own white, so writing areas keep full contrast. */
.bg-photo,.bg-bloom{position:absolute;inset:0;background-size:cover;
      background-position:center;pointer-events:none}
.bg-bloom{background-repeat:no-repeat}

/* ---------- tab rail ---------- */
.rail{position:absolute;left:0;top:0;width:58pt;height:792pt;
      border-right:1px solid var(--line);display:flex;flex-direction:column;
      padding:4pt}
.rail a{flex:1;display:flex;align-items:center;justify-content:center;
        position:relative;margin:2pt 0;border-radius:var(--radius);
        text-decoration:none}
.rail a span{writing-mode:vertical-rl;transform:rotate(180deg);font-size:7pt;
        font-weight:700;letter-spacing:.06em;color:var(--soft)}
.rail a i{position:absolute;left:50%;margin-left:-2.5pt;top:calc(50% - 27pt);
        width:5pt;height:5pt;border-radius:99pt;opacity:.55}
.rail a.on{background:var(--card);border:0.4pt solid rgba(0,0,0,.10)}
.rail a.on i{opacity:1}
.rail a.on span{color:var(--acc-text);font-weight:800}
.rail a.on::before{content:"";position:absolute;left:5pt;top:50%;
        transform:translateY(-50%);width:2.4pt;height:24pt;
        background:var(--acc);border-radius:2pt}
/* The active tab is a raised card too, so it gets the same directional
   shadow as .card -- without this it reads as an evenly lit box and breaks
   the light source the rest of the page establishes. */
.rail a.on::after{content:"";position:absolute;left:8%;right:8%;top:100%;
        height:11pt;background:radial-gradient(ellipse 62% 100% at 50% 0%,
        rgba(0,0,0,.07), rgba(0,0,0,0) 72%);pointer-events:none}

/* ---------- page skeleton ---------- */
.content{position:absolute;left:84pt;right:28pt;top:0;bottom:0;
         display:flex;flex-direction:column;padding:42pt 0 34pt}
.head{flex:none}
.body{flex:1;display:flex;flex-direction:column;gap:12pt;margin-top:20pt;
      min-height:0}

.eyebrow{display:flex;align-items:center;gap:8pt;font-size:9.5pt;font-weight:700;
         color:var(--mid)}
.eyebrow::before{content:"";width:2.6pt;height:11pt;background:var(--accent);
         border-radius:1pt}
h1{font-size:23pt;font-weight:800;margin:11pt 0 0;letter-spacing:-.01em}
.sub{color:var(--soft);font-size:9.5pt;margin-top:5pt}
/* the h1 carries a top margin; leaving it on the flex item makes
   align-items:center centre the margin box, which floats the field
   above the text. Move the margin to the row instead. */
.titlerow{display:flex;align-items:center;gap:16pt;margin-top:11pt}
.titlerow h1{margin-top:0}

/* ---------- pieces ---------- */
/* Elevation is ONE continuous falloff, not two stacked shadows.
   - box-shadow: tight and un-offset, so it only defines the edge.
   - ::after: the drop shadow proper. It starts exactly at the card's bottom
     edge (top:100%) and its gradient centre sits at its own top-centre, so
     density peaks right under the card and fades both downward and sideways.
   Offsetting the box-shadow instead put its peak below the edge, which left a
   bright gap between the two and read as two separate lines. */
/* No box-shadow here. Chrome rasterises every box-shadow into its own
   image; across ~500 pages that alone was 56MB of a 86MB file. The
   ::after gradient below becomes a vector shading pattern instead, and a
   hairline gives back the edge definition the box-shadow provided. */
.card{background:var(--card);border-radius:var(--radius);
      border:0.4pt solid rgba(0,0,0,.10);
      padding:16pt;display:flex;flex-direction:column;min-height:0;
      position:relative}
/* `top` must be exactly 100% -- no offset. Pushing the pool even 1pt below the
   edge leaves a seam that subpixel rounding exposes on some cards and not
   others (the Focus card on the index page showed a 5-level bright row while
   its neighbours did not), which reads as the "two lines" defect on that card
   alone. At 100% every card measures identically. */
.card::after{content:"";position:absolute;left:4%;right:4%;top:100%;height:13pt;
      background:radial-gradient(ellipse 62% 100% at 50% 0%, rgba(0,0,0,.07),
      rgba(0,0,0,0) 72%);pointer-events:none}
.label{display:flex;align-items:center;gap:7pt;font-size:9pt;font-weight:800;
       color:var(--ink);margin-bottom:10pt;flex:none}
.label::before{content:"";width:2.6pt;height:10pt;background:var(--accent);
       border-radius:1pt;flex:none}
.chip{display:inline-block;background:var(--chip);color:var(--accent-text);
      font-size:7.5pt;font-weight:800;padding:3pt 9pt;border-radius:99pt;
      letter-spacing:.03em}
.field{background:var(--field);border-radius:6pt;height:19pt;flex:none}
.coverrule{width:28pt;height:2.6pt;background:var(--accent);margin-bottom:18pt}
.dot{width:5pt;height:5pt;border-radius:99pt;background:var(--accent);flex:none}
.dot.sm{width:4pt;height:4pt}
.box{width:12pt;height:12pt;border:1.2px solid var(--line);border-radius:3pt;
     flex:none}

/* Writing rules are fixed height, never flex. With flex:1 the gap became
   card-height / line-count, so it differed on every page -- measured at
   21.3px to 139.5px across v8, with 209 pages mixing two or more gaps on
   one page. Paper does not do that. See LINES.md. */
.lines{flex:1;display:flex;flex-direction:column;min-height:0;
       overflow:hidden}
.lines>div{height:20pt;flex:none;border-bottom:1px solid var(--line)}

.row{display:flex;gap:12pt;flex:1;min-height:0}
.col{display:flex;flex-direction:column;gap:12pt;min-height:0}

/* ---------- grids ---------- */
.cal{border-collapse:collapse;width:100%;height:100%;table-layout:fixed}
.cal td{border:1px solid var(--line);vertical-align:top;padding:5pt 6pt;
        font-size:8.5pt;font-weight:700}
.cal th{font-size:7.5pt;color:var(--soft);font-weight:800;padding-bottom:7pt;
        letter-spacing:.05em;height:18pt}
.cal .we{color:var(--accent-text)}

.mini{width:100%;border-collapse:collapse}
.mini td,.mini th{text-align:center;font-size:5.6pt;padding:1.3pt 0;line-height:1}
.mini th{color:var(--soft);font-weight:800;font-size:5.2pt}
.mini .we{color:var(--accent-text)}

.trk{border-collapse:collapse;width:100%;height:100%;table-layout:fixed}
.trk td{border:1px solid var(--line)}
.trk .nm{border:none;border-bottom:1px solid var(--line);text-align:left;
         font-size:8.5pt;padding:0 8pt 0 2pt;white-space:nowrap;width:104pt}
.trk .dh{border:none;font-size:5.4pt;color:var(--soft);font-weight:800;
         height:13pt;vertical-align:bottom;padding-bottom:3pt;text-align:center}
.trk .dh.we{color:var(--accent-text)}
/* The label column is borderless, so the table had no left edge but kept a
   right one from the last cell -- visibly lopsided. Drop the outer frame on
   all four sides and keep only the dividers between cells, which is the
   house rule (no outlines; shadows do the layering). */
/* No exception for the label column: the rule under the header runs the
   full width. .nm already carries border-bottom; the old
   `tr:first-child .nm{border-bottom:none}` cut it off on the left only,
   which is what made the header look lopsided on 7 tables. */
/* Both vertical edges, not just the right one. A table with a .nm
   label column has no left edge because .nm is borderless, but subs
   has no label column and showed one (54p). */
.trk td:first-child{border-left:none}
.trk td:last-child{border-right:none}
/* The closing rule stays. The header rule runs the full width, so a
   table with no line under its last row reads as unfinished. Only the
   VERTICAL frame is dropped -- horizontals close, verticals open. */

.dots{background-image:radial-gradient(var(--line) 1.1px, transparent 1.1px);
      background-size:14pt 14pt;background-position:8pt 8pt}
"""


# Concept C only. Kept as an overlay rather than branches inside BASE_CSS so
# the shipped themes (v7/v8/v9) render byte-identically to before.
INK_CSS = """
/* ---------- lines and planes ---------- */
/* Every pill becomes a plane. Rounded corners are the single strongest
   "friendly app" signal in the old look, so they all go to 0. */
.card,.field,.box,.chip,.rail a{border-radius:0}
.card{border-color:rgba(30,35,33,.15)}

/* An input is a plane closed by a line -- the plane says "write here", the
   heavier bottom rule gives it the baseline a brush would sit on. */
.field{border-bottom:1pt solid rgba(30,35,33,.30)}
.box{border-width:1pt;border-color:rgba(30,35,33,.32)}
.chip{background:transparent;border:0.7pt solid var(--accent-text);
      letter-spacing:.08em;padding:3pt 8pt}

/* ---------- the brush rule ---------- */
/* One tapering stroke under every title: thick at the start, dissolving to
   nothing. A gradient, so it stays vector -- a real brush texture would be
   an image on all 434 pages. */
h1{font-family:var(--display),Georgia,serif;font-weight:700;font-size:31pt;
   letter-spacing:0;line-height:1.05}
h1::after{content:"";display:block;width:54pt;height:2.6pt;margin-top:11pt;
   background:linear-gradient(90deg,var(--ink) 0%,var(--ink) 55%,
   rgba(30,35,33,.10) 100%)}
.titlerow h1::after{margin-bottom:0}

/* Section marks are strokes, not bars: thinner, taller, square-cut. */
.eyebrow{font-size:8.5pt;letter-spacing:.14em;text-transform:uppercase;
   font-weight:600}
.eyebrow::before{width:1.5pt;height:13pt;border-radius:0}
.label::before{width:1.5pt;height:11pt;border-radius:0}
.sub{font-size:9.5pt;letter-spacing:.01em}

/* ---------- the rail ---------- */
/* The active tab is a solid ink plane with paper-coloured type -- the one
   place a full field of colour is allowed, and it is neutral, not a category
   hue, so the "no solid accent fields" rule still holds. */
.rail{border-right:0.7pt solid rgba(30,35,33,.20)}
.rail a span{letter-spacing:.16em;font-weight:600}
.rail a.on{background:var(--ink);border:none}
.rail a.on span{color:var(--bg);font-weight:600}
.rail a.on::before{left:0;top:0;transform:none;width:100%;height:2.4pt;
   background:var(--acc);border-radius:0}
.rail a.on::after{background:radial-gradient(ellipse 62% 100% at 50% 0%,
   rgba(0,0,0,.09), rgba(0,0,0,0) 72%)}

/* ---------- points become strokes ---------- */
/* The brief was lines and planes, so the list bullets stop being dots. A
   short rule reads as the same "item starts here" mark without adding a
   third shape language to the page. */
.dot{width:10pt;height:1.5pt;border-radius:0}
.dot.sm{width:8pt;height:1.5pt}
.coverrule{width:44pt;height:2.6pt;
   background:linear-gradient(90deg,var(--ink) 0%,var(--ink) 52%,
   rgba(30,35,33,.10) 100%)}

/* ---------- the cover ---------- */
/* Playfair's default figures are lining, but force it: the daily pages run
   "Day 1" through "Day 31" and oldstyle numerals there read as roman. */
.covertitle{font-family:var(--display),Georgia,serif;font-size:38pt;
   letter-spacing:0;line-height:1.14;font-weight:700}
h1,.covertitle{font-variant-numeric:lining-nums tabular-nums;
   font-feature-settings:"lnum" 1,"tnum" 1}

/* The seal. One small vermilion plane in the empty corner, opposite the
   bleed -- the counterweight that stops the asymmetry reading as a mistake. */
.page#cover::after{content:"";position:absolute;right:56pt;top:74pt;
   width:26pt;height:26pt;border:2pt solid #9B3226;
   box-shadow:inset 0 0 0 2.4pt rgba(0,0,0,0),0 0 0 0 rgba(0,0,0,0);
   background:linear-gradient(135deg,rgba(155,50,38,.14),rgba(155,50,38,.05))}

/* ---------- the ink bleed ---------- */
.bg-ink{position:absolute;inset:0;background-size:cover;
   background-repeat:no-repeat;background-position:center;pointer-events:none}
"""

if T.get("app"):
    import app_style
else:
    app_style = None

# fast_paint: the card and tab shadows become one shared PNG instead of a
# radial-gradient each. Chrome writes every gradient as a function shading
# under its own soft mask, 5-6 per page, and GoodNotes repaints them tile by
# tile -- the user saw each page fill in as a checkerboard (2026-09-24). The
# PNG is the same gradient sampled once (shadow_png), stretched to the same
# box, so the shape is unchanged: mean difference 0.08 grey levels.
# top:100% and the box geometry stay exactly as above.
FAST_CSS = (".card::after,.rail a.on::after{background:"
            f"url('../assets/shadow_{VERSION}.png') 0 0/100% 100% no-repeat}}")

CSS = (ROOT_VARS + BASE_CSS + (INK_CSS if T.get("ink_style") else "")
       + (app_style.css() if app_style else "")
       + (FAST_CSS if T.get("fast_paint") else "")
       + os.environ.get("TRIM_CSS", ""))


def lift(col, amount):
    """Blend a colour toward white. Raises luminance, keeps the hue relations."""
    if not amount:
        return col
    r, g, b = (int(col[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02X%02X%02X" % tuple(
        int(round(c + (255 - c) * amount)) for c in (r, g, b))


def bloom_stops():
    """Warm core sampled from the photo, plus the theme's cool tail."""
    warm = [
        (0, 0, 118, 92, "#FFFBE8", .95),
        (24, 8, 150, 108, "#F5DC97", .80),
        (60, 18, 165, 112, "#E9B87E", .62),
        (104, 28, 150, 104, "#E3A492", .40),
        (-56, -6, 132, 96, "#C6D2AC", .30),
    ]
    amt = T.get("bloom_lift", 0)
    return [(dx, dy, rx, ry, lift(c, amt), a)
            for dx, dy, rx, ry, c, a in warm + T.get("bloom_cool", [])]


def bloom_svg(cx=306, cy=250):
    """Iridescent bloom traced from the user's sky photo.

    Measured hues in the photo run 34-49 deg only -- pure amber to yellow, no
    green or blue at any usable saturation. What reads as a spectrum is
    simultaneous contrast: the #FFFBE8 core looks cool against the warm
    surround. So the warm stops below are the photo's real sampled values, and
    the cool ones are held very faint and placed on the left, where the eye
    already reads them.
    """
    stops = bloom_stops()
    stops = [(cx + dx, cy + dy, rx, ry, c, a) for dx, dy, rx, ry, c, a in stops]
    ell = "".join(
        f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{c}" '
        f'opacity="{a}"/>' for x, y, rx, ry, c, a in stops)
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="612" height="792" '
        'viewBox="0 0 612 792">'
        '<defs><filter id="b" x="-40%" y="-40%" width="180%" height="180%">'
        '<feGaussianBlur stdDeviation="52"/></filter></defs>'
        f'<g filter="url(#b)">{ell}</g></svg>')
    # Percent-encode the whole payload: the SVG contains quotes, spaces and
    # parentheses (url(#b)), any of which would terminate the style attribute
    # or the url() token if passed through raw.
    return "data:image/svg+xml," + urllib.parse.quote(svg, safe="")


def bloom_png(path, cx=306, cy=250, scale=0.5, blur=52):
    """Bake the bloom to a PNG so all pages share one image resource.

    Inlining the SVG re-rasterises it per page; a single file is referenced
    once. The bloom is heavily blurred, so storing it at half size costs
    nothing visible and cuts the file substantially.
    """
    from PIL import Image, ImageDraw, ImageFilter
    W, H = 612, 792
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    stops = bloom_stops()
    for dx, dy, rx, ry, col, a in stops:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        r, g, b = (int(col[i:i + 2], 16) for i in (1, 3, 5))
        ex, ey = cx + dx, cy + dy
        ImageDraw.Draw(layer).ellipse(
            [ex - rx, ey - ry, ex + rx, ey + ry], fill=(r, g, b, int(a * 255)))
        base = Image.alpha_composite(base, layer)
    # Blur with premultiplied alpha. Blurring straight RGBA mixes the RGB of
    # fully transparent pixels -- which is black -- into the visible edge and
    # darkens the whole bloom (measured ~7 grey levels against the SVG).
    import numpy as np
    a = np.asarray(base).astype(np.float64)
    al = a[..., 3:4] / 255.0
    a[..., :3] *= al
    blurred = np.asarray(
        Image.fromarray(a.astype(np.uint8), "RGBA")
        .filter(ImageFilter.GaussianBlur(blur))).astype(np.float64)
    out_a = blurred[..., 3:4]
    rgb = np.divide(blurred[..., :3] * 255.0, np.maximum(out_a, 1e-6))
    base = Image.fromarray(
        np.concatenate([np.clip(rgb, 0, 255), out_a], axis=2).astype(np.uint8),
        "RGBA")
    if scale != 1.0:
        base = base.resize((int(W * scale), int(H * scale)), Image.LANCZOS)
    base.save(path, optimize=True)
    return path


INK_SPOTS = {
    # Asymmetric on purpose. The bleed hugs one corner and runs off the edge;
    # the rest of the sheet is left empty, because in this idiom the empty
    # part is the composition, not what is left over after filling the page.
    #
    # Each spot carries its own blur. One radius for all of them just yields a
    # smooth grey gradient -- it read as a printing smudge, not ink. A tight
    # dark core under a wide faint halo is what gives it the "soaked in and
    # spread" structure.
    # Anchored ON the page edge, not inside it, so most of the mass falls
    # outside the trim. A blob sitting fully in view reads as a toner smudge
    # however soft it is; a sweep entering from the corner reads as ink.
    # Alphas are roughly half what looked right on screen -- at 434 pages this
    # sits behind everything and only has to be felt, not seen.
    "page":  [(612, 8, 132, 52, .070, 16),
              (588, 40, 192, 82, .048, 40),
              (558, 70, 252, 118, .026, 78)],
    "cover": [(26, 32, 152, 62, .075, 18),
              (84, 68, 212, 96, .050, 44),
              (140, 96, 282, 140, .027, 84),
              (566, 648, 152, 84, .022, 70)],
}


def ink_wash_png(path, spots, scale=0.5):
    """Bake one ink bleed to a shared PNG.

    Same reasoning as bloom_png: a wash built from stacked CSS gradients
    measured ~3s per page to rasterise, which stutters in GoodNotes at this
    page count. One file, referenced by every page, costs nothing.
    """
    from PIL import Image, ImageDraw, ImageFilter
    import numpy as np
    W, H = 612, 792
    col = T.get("ink_wash", "#1B2428")
    r, g, b = (int(col[i:i + 2], 16) for i in (1, 3, 5))
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for x, y, rx, ry, a, blur in spots:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(layer).ellipse(
            [x - rx, y - ry, x + rx, y + ry], fill=(r, g, b, int(a * 255)))
        # Premultiply before blurring, exactly as bloom_png does -- otherwise
        # the black RGB of fully transparent pixels bleeds into the edge and
        # darkens the whole wash.
        arr = np.asarray(layer).astype(np.float64)
        arr[..., :3] *= arr[..., 3:4] / 255.0
        bl = np.asarray(Image.fromarray(arr.astype(np.uint8), "RGBA")
                        .filter(ImageFilter.GaussianBlur(blur))).astype(np.float64)
        out_a = bl[..., 3:4]
        rgb = np.divide(bl[..., :3] * 255.0, np.maximum(out_a, 1e-6))
        layer = Image.fromarray(
            np.concatenate([np.clip(rgb, 0, 255), out_a], axis=2).astype(np.uint8),
            "RGBA")
        base = Image.alpha_composite(base, layer)
    if scale != 1.0:
        base = base.resize((int(W * scale), int(H * scale)), Image.LANCZOS)
    base.save(path, optimize=True)
    return path


# ---------------------------------------------------------------- helpers --
# which of the four colour buckets each tab belongs to
BUCKET = {"index": "plan", "year": "plan", "month": "plan", "week": "plan",
          "day": "plan", "cover": "plan",
          "focus": "focus", "feel": "care", "habits": "care",
          "health": "care", "life": "free", "notes": "free"}
BUCKET_KEY = {"plan": "index", "focus": "tasks", "care": "meds", "free": "notes"}
# The student build names the same four buckets after its own tabs, so the
# palette can be read next to that product's tab list. The colours are
# identical to v8's -- only the keys differ.
STUDENT_BUCKET_KEY = {"plan": "index", "focus": "work", "care": "study",
                      "free": "notes"}


if T.get("app"):
    import student_pages
    student_pages.init(sys.modules[__name__])
    TABS = student_pages.TABS
    GROUPS = student_pages.GROUPS
    GROUP_OF = {sub: g for g, items in GROUPS.items() for sub, *_ in items}
    # 네 색 버킷. 색 자체는 v8 과 같고 어느 탭이 어느 색인지만 다르다.
    BUCKET = {"index": "plan", "semester": "plan", "week": "plan",
              "day": "plan", "cover": "plan",
              "classes": "focus", "work": "focus",
              "study": "care", "focus": "care",
              "life": "free", "notes": "free"}
else:
    student_pages = None


def section_colors(key):
    """(decorative accent, tint, text tone) for any page.

    Sub-pages inherit their group's colour, so a page always matches the tab
    you reached it from. Still only four colours in play -- the research put
    that at the ceiling before colour coding starts hurting recall.
    """
    group = GROUP_OF.get(key, key)
    bucket = BUCKET.get(group, "plan")
    keys = STUDENT_BUCKET_KEY if T.get("student") else BUCKET_KEY
    return T["sections"][keys[bucket]]


def rail(active):
    out = []
    # In the undated build the dailies are split into d{month}-{day}, so a
    # single "#day" target does not exist. Leaving the tab in would render a
    # link Chrome silently drops -- a tab that looks live and does nothing.
    tabs = [t for t in TABS
            if not (T.get("undated") and not student_pages and t[0] == "day")]
    for k, lb in tabs:
        acc, _, txt = section_colors(k)
        if app_style:
            # 유리 알약 위에서는 본문용 글자색이 4.5:1 에 못 미친다
            txt = app_style.darken(txt)
        dot = f'<i style="background:{acc}"></i>' if T["tab_dots"] else ""
        out.append(f'<a class="{"on" if k == active else ""}" href="#{k}" '
                   f'style="--acc:{acc};--acc-text:{txt}">{dot}<span>{lb}</span></a>')
    return f'<nav class="rail">{"".join(out)}</nav>'


REPEATED = re.compile(r"[dwm]\d+(-\d+)?")


TAB_KEYS = {k for k, _ in TABS}

# Every sub-page under a group borrows that group's tab. Without this the
# 48 pages inside the groups light nothing at all -- you tap FOCUS, land on
# Mind map, and the rail goes blank, which reads as "you have left the app".
SUB_OF = {sub: g for g, items in GROUPS.items() for sub, *_ in items}


def rail_key(key):
    """Which tab lights up. Neither the repeated pages nor the group
    sub-pages are tabs themselves, so they borrow the tab you reached them
    from -- without this nothing is highlighted and you lose your place."""
    if student_pages:
        m = re.fullmatch(r"([a-z])(\d+)", key)
        if m:
            for pre, tab in student_pages.REPEAT_TAB:
                if m.group(1) == pre:
                    return tab
        if key in TAB_KEYS:
            return key
        return SUB_OF.get(key, key)
    if re.fullmatch(r"[md]\d+(-\d+)?", key):
        return "month"
    if re.fullmatch(r"w\d+", key):
        return "week"
    if re.fullmatch(r"n\d+", key):
        return "notes"
    if key in TAB_KEYS:          # a tab's own index page, e.g. "month"
        return key
    return SUB_OF.get(key, key)


def bloom_css(cx=306, cy=250):
    """The bloom as stacked CSS radial gradients.

    A blurred SVG or PNG forces Chrome to rasterise, and at ~500 pages that
    became 11k tiled image objects and a 78MB file. Gradients stay vector,
    so the bloom costs essentially nothing per page. The radii are widened
    to make up for the blur we are no longer applying.
    """
    layers = []
    for dx, dy, rx, ry, col, a in bloom_stops():
        r, g, b = (int(col[i:i + 2], 16) for i in (1, 3, 5))
        layers.append(
            f"radial-gradient(ellipse {rx * 1.9:.0f}pt {ry * 1.9:.0f}pt at "
            f"{cx + dx}pt {cy + dy}pt, rgba({r},{g},{b},{a:.2f}) 0%, "
            f"rgba({r},{g},{b},0) 68%)")
    return ",".join(reversed(layers))


def page(key, body):
    """One page. The background wash is a shared PNG, not CSS gradients.

    Stacked radial-gradients looked identical but cost ~3s per page to
    rasterise (vs 88ms without), which would stutter badly in GoodNotes. A
    single baked image is blitted instead, and because every page points at
    the same two files it costs almost nothing in the PDF.
    """
    acc, tint, txt = section_colors(key)
    style = f"--accent:{acc};--chip:{tint};--accent-text:{txt}"
    layers = ""
    if app_style:
        dark = key in ("cover", "index")
        base = "app_cover" if dark else "app_under"
        layers = ('<div class="bgimg" style="background-image:'
                  f"url('../assets/{base}_{VERSION}.png')\"></div>")
        if not dark:
            layers += ('<div class="sheet" style="background-image:'
                       f"url('../assets/app_sheet_{VERSION}.png')\"></div>")
        return (f'<section class="page{" dk" if dark else ""}" id="{key}" '
                f'style="{style}">{layers}'
                f'{rail(rail_key(key))}<div class="content">{body}</div></section>')
    if T.get("ink_wash"):
        name = "ink_cover" if key == "cover" else "ink_page"
        layers += ('<div class="bg-ink" style="background-image:'
                   f"url('../assets/{name}_{VERSION}.png')\"></div>")
    if T.get("photo"):
        cover = key == "cover"
        name = "bloom_cover" if cover else "bloom_page"
        if cover and T["photo_cover"]:
            layers += ('<div class="bg-photo" style="background-image:'
                       f"url('{T['photo']}');opacity:{T['photo_cover']}\"></div>")
        bo = T["bloom_cover"] if cover else T["bloom_page"]
        if T.get("fast_paint") and not cover:
            # Pre-composited onto --bg (bloom_baked_png): an opaque image
            # needs no transparency group. The cover keeps the live blend
            # because the sky photo sits under it; it is one page.
            name, bo = "bloom_page_baked", 1
        layers += ('<div class="bg-bloom" style="background-image:'
                   f"url('../assets/{name}_{VERSION}.png');opacity:{bo}\"></div>")
    return (f'<section class="page" id="{key}" style="{style}">{layers}'
            f'{rail(rail_key(key))}<div class="content">{body}</div></section>')


def head(eyebrow, title, sub="", field_after=False, extra=""):
    t = f"<h1>{title}</h1>"
    if field_after:
        t = (f'<div class="titlerow"><h1>{title}</h1>'
             f'<div class="field" style="flex:1;max-width:210pt;height:22pt"></div>'
             f'{extra}</div>')
    s = f'<div class="sub">{sub}</div>' if sub else ""
    return f'<div class="head"><div class="eyebrow">{eyebrow}</div>{t}{s}</div>'


# The rules overfill and the box clips them. Sizing each block to its card
# by hand means re-tuning every page whenever a card changes -- measured
# leftovers of up to 11 rows on unique pages and 4 on every daily. n is the
# floor; the spare rows fall outside overflow:hidden.
# Spare rules exist to be clipped, and only where the card's height is set
# from outside. On a card whose height follows its content -- the cards in
# hyperfocus and doctor are like this -- every spare rule is real height:
# raising this to 18 grew one card from 334px to 575px and crushed its
# neighbours to zero rules. Keep it small; cards that need more rules get
# them from their own lines(n).
LINE_SPARE = 26
_LN = 0


def lines(n, spare=LINE_SPARE):
    """Rules for a writing area. `n` is the floor, not the count.

    The spare rules exist to be clipped: the card is taller than `n` rules
    on most pages, and we would otherwise leave a blank strip. That only
    works when the flex container sets the card's height. On a `flex:none`
    card the content sets the height instead, so the spare rules inflate
    the card rather than being cut -- on "Working backwards" it grew to ten
    rules and crushed the field rows above it. Pass spare=0 there.
    """
    global _LN
    _LN += 1
    return (f'<div class="lines" data-ln="{_LN}">'
            + "<div></div>" * (n + spare) + "</div>")


def checkrow(field_flex=1):
    return ('<div style="display:flex;align-items:center;gap:9pt">'
            f'<div class="box"></div><div class="field" style="flex:{field_flex}"></div></div>')


# ------------------------------------------------------------------ pages --
APP_ORBS = ["linear-gradient(140deg,#7C4DFF,#B388FF)",
            "linear-gradient(140deg,#F45D9B,#FF8A3D)",
            "linear-gradient(140deg,#22D3EE,#4DA3FF)",
            "linear-gradient(140deg,#FF8A3D,#FFD166)"]

# (앵커, 이름, 설명). 앵커가 없으면 목차가 만들어지지 않는다 --
# 2026-09-23 검수에서 네 줄이 전부 href="#index" 로 박혀 있어
# 눌러도 제자리였다. 목적지가 유효해서 링크 검사도 통과했다.
# 표지 카드는 실제 페이지 제목과 같아야 한다(없는 기능을 광고하지 않는다).
APP_GROUPS = [("semester", "Semester", "eight terms, sixteen weeks each"),
              ("week", "Weeks", "what is due, week by week"),
              ("day", "Days", "one thing, then the rest"),
              ("classes", "Classes", "timetable, one page per class"),
              ("work", "Work", "syllabus, assignments, group projects"),
              ("study", "Study", "exams, lecture notes, grades"),
              ("focus", "Focus", "for when starting is the hard part"),
              ("life", "Life", "medication, sleep, mood"),
              ("notes", "Notes", "blank space")]


def p_app_cover():
    """표지. 카드에 적는 것은 실제로 들어 있는 것이어야 한다 -- 리스팅의
    대표 이미지로 쓰이므로 페이지를 늘리면 여기도 같이 고친다."""
    items = [("Syllabus unpack", "one handout, broken into dates"),
             ("Assignment tracker", "due, started, handed in"),
             ("Working backwards", "from the deadline, not from today"),
             ("Term at a glance", "sixteen weeks on one sheet")]
    rows = "".join(
        f'<div class="crow"><div class="orb" style="background:{APP_ORBS[i]}">'
        f'</div><div class="cn">{n}<div class="cd">{d}</div></div></div>'
        for i, (n, d) in enumerate(items))
    return ('<div class="cv"><div class="cv-eye">UNDATED &nbsp;&middot;&nbsp; '
            'FOR THE ADHD STUDENT</div>'
            '<div class="cv-t">Semester<br>Planner</div>'
            '<div class="cv-sub">Start any week. Skip a week.<br>'
            'The page is not keeping score.</div></div>'
            f'<div class="cv-card">{rows}</div>')


def p_app_index():
    rows = "".join(
        f'<a class="crow" href="#{k}"><div class="orb" '
        f'style="background:{APP_ORBS[i % len(APP_ORBS)]}"></div>'
        f'<div class="cn">{n}<div class="cd">{d}</div></div>'
        f'<span class="cq">&rsaquo;</span></a>'
        for i, (k, n, d) in enumerate(APP_GROUPS))
    return (head("Index", "Where to?", "Use the side tabs, or pick here.")
            + '<div class="body"><div class="card" style="flex:none;'
              f'padding:6pt 22pt">{rows}</div>'
            + '<div class="card" style="flex:1">'
              '<div class="label">Anything else</div>'
            + student_pages.fill() + '</div></div>')


def p_cover():
    if app_style:
        return p_app_cover()
    # The cover card is the listing's hero shot, so it has to describe the
    # build it actually ships. The counts below are the real section sizes --
    # if a page is added to GROUPS, update them.
    if T.get("undated"):
        items = [
            ("Months, weeks &amp; days", "undated — start on any date", "436"),
            ("Focus tools", "for when starting is the hard part", "11"),
            ("Feelings tools", "the loop, the sting, the inner critic", "10"),
            ("Health &amp; habits", "medication, sleep, routines", "10"),
            ("Life admin", "meals, money, the things that slip", "10"),
            ("Blank space", "dot grid, ruled, plain", "8"),
        ]
    else:
        items = [
            ("Index &amp; year view", "see everything, jump anywhere", "2"),
            ("Monthly / weekly / daily", "the three you'll use every day", "3"),
            ("Task breakdown", "make the big thing smaller", "1"),
            ("Habit &amp; medication log", "31-day grid, no streak guilt", "2"),
            ("Notes", "dot grid, yours to fill", "1"),
        ]
    rows = "".join(
        f'<div style="display:flex;align-items:center;gap:12pt;padding:11pt 0;'
        f'{"" if i == len(items) - 1 else "border-bottom:1px solid var(--line)"}">'
        f'<div class="dot"></div>'
        f'<div style="flex:1"><div style="font-size:10pt;font-weight:700">{t}</div>'
        f'<div style="font-size:8.5pt;color:var(--soft);margin-top:2pt">{d}</div></div>'
        f'<span class="chip">{c}</span></div>'
        for i, (t, d, c) in enumerate(items))
    return f"""
    <div class="head" style="flex:1;display:flex;flex-direction:column;
         align-items:center;justify-content:center;text-align:center">
      <div class="coverrule"></div>
      <span class="chip">UNDATED &middot; NO-GUILT</span>
      <div class="covertitle" style="font-size:31pt;font-weight:700;
                  line-height:1.18;margin-top:20pt;letter-spacing:-.02em">{"" if T.get("undated") else f"{YEAR} "}ADHD &amp;<br>Wellness Planner</div>
      <div style="color:var(--mid);font-size:11pt;margin-top:12pt">
        Start any day. Skip a week. Nothing to catch up on.</div>
    </div>
    <div class="card" style="flex:none;padding:18pt 22pt;margin-bottom:6pt">
      <div class="label">What's inside</div>{rows}
    </div>"""


def p_index():
    if app_style:
        return p_app_index()
    groups = [
        ("Plan", [("year", "The long view"), ("month", "Months &amp; days" if T.get("undated")
                   else "Monthly overview"),
                  ("week", "Weekly spread")]
                 + ([] if T.get("undated") else [("day", "Daily page")])),
        ("Focus", [("focus", "Focus tools"), ("habits", "Habits")]),
        ("Care", [("feel", "Feelings"), ("health", "Health")]),
        ("Life", [("life", "Life admin"), ("notes", "Notes")]),
    ]
    cards = []
    for title, links in groups:
        rows = "".join(
            f'<a href="#{k}" style="display:flex;align-items:center;gap:10pt;flex:1;'
            f'text-decoration:none;color:var(--ink);'
            f'{"" if i == len(links) - 1 else "border-bottom:1px solid var(--line)"}">'
            f'<div class="dot sm" style="'
            f'background:{section_colors(k)[0]}"></div>'
            f'<div style="flex:1;font-size:10pt;font-weight:600">{n}</div>'
            f'<div style="color:var(--soft);font-size:11pt">&rsaquo;</div></a>'
            for i, (k, n) in enumerate(links))
        # the group's own colour, so the header bar, the row dots and the tab
        # rail all say the same thing
        cards.append(f'<div class="card" style="flex:{len(links)};'
                     f'--accent:{section_colors(links[0][0])[0]}">'
                     f'<div class="label">{title}</div>{rows}</div>')
    return (head("Index", "Where to?", "Use the side tabs, or pick from here")
            + f'<div class="body">{"".join(cards)}</div>')


def mini_month(m):
    weeks = calendar.Calendar(firstweekday=0).monthdayscalendar(YEAR, m)
    th = "".join(f'<th class="{"we" if i >= 5 else ""}">{d}</th>'
                 for i, d in enumerate("MTWTFSS"))
    rows = "".join(
        "<tr>" + "".join(f'<td class="{"we" if i >= 5 else ""}">{d or ""}</td>'
                         for i, d in enumerate(w)) + "</tr>" for w in weeks)
    return (f'<div><div style="font-size:8pt;font-weight:700;'
            f'margin-bottom:5pt">{calendar.month_name[m]}</div>'
            f'<table class="mini"><tr>{th}</tr>{rows}</table></div>')


def p_year():
    months = "".join(mini_month(m) for m in range(1, 13))
    return (head("Year at a glance", str(YEAR))
            + f"""<div class="body">
      <div class="card" style="flex:none;padding:18pt">
        <div style="display:grid;grid-template-columns:repeat(4,1fr);
             gap:22pt 14pt">{months}</div>
      </div>
      <div class="card" style="flex:1">
        <div class="label">Three things that matter this year</div>
        <div style="flex:1;display:flex;flex-direction:column;gap:12pt">
          {''.join('<div style="display:flex;align-items:stretch;gap:10pt;flex:1">'
                   '<div class="box" style="margin-top:10pt"></div>'
                   '<div class="field" style="flex:1;height:auto"></div></div>'
                   for _ in range(3))}
        </div>
      </div></div>""")


def p_month():
    weeks = calendar.Calendar(firstweekday=0).monthdayscalendar(YEAR, 1)
    th = "".join(f'<th class="{"we" if i >= 5 else ""}">{d}</th>' for i, d in
                 enumerate(["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]))
    rows = "".join(
        "<tr>" + "".join(f'<td class="{"we" if i >= 5 else ""}">{d or ""}</td>'
                         for i, d in enumerate(w)) + "</tr>" for w in weeks)
    return (head("Monthly overview", f"January {YEAR}")
            + f"""<div class="body">
      <div class="card" style="flex:1;padding:16pt 18pt">
        <table class="cal"><tr>{th}</tr>{rows}</table></div>
      <div class="card" style="flex:none;flex-direction:row;align-items:center;gap:14pt">
        <div class="label" style="margin:0;white-space:nowrap">This month's focus</div>
        <div class="field" style="flex:1"></div></div></div>""")


def p_week(label=""):
    days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    rows = "".join(
        f'<div style="flex:1;display:flex;align-items:flex-start;padding-top:8pt;'
        f'{"" if i == len(days) - 1 else "border-bottom:1px solid var(--line)"}">'
        f'<span class="chip" style="{"" if i < 5 else "background:var(--field);color:var(--mid)"}">{d}</span>'
        f'</div>' for i, d in enumerate(days))
    return (head("Weekly spread", label or "Week of", field_after=True)
            + f"""<div class="body"><div class="row">
      <div class="card" style="flex:1.45">{rows}</div>
      <div class="col" style="flex:1">
        <div class="card" style="flex:1.6">
          <div class="label">Brain dump</div>{lines(8)}</div>
        <div class="card" style="flex:1">
          <div class="label">Top 3 priorities</div>
          <div style="flex:1;display:flex;flex-direction:column;
               justify-content:space-around">{checkrow() * 3}</div></div>
        <div class="card" style="flex:none">
          <div class="label">Energy</div>
          <div style="display:flex;justify-content:space-between;padding:0 4pt">
            {'<div class="box" style="width:14pt;height:14pt"></div>' * 5}</div>
          <div style="display:flex;justify-content:space-between;font-size:7pt;
               color:var(--soft);margin-top:6pt;padding:0 2pt">
            <span>low</span><span>high</span></div></div>
      </div></div></div>""")


def p_day(label="", month=None):
    hours = ["7 AM", "9 AM", "11 AM", "1 PM", "3 PM", "5 PM", "7 PM", "9 PM"]
    blocks = "".join(
        f'<div style="flex:1;display:flex;align-items:center;'
        f'{"" if i == len(hours) - 1 else "border-bottom:1px solid var(--line)"}">'
        f'<span style="font-size:7.5pt;font-weight:700;color:var(--soft);'
        f'width:34pt">{h}</span></div>' for i, h in enumerate(hours))
    mood = "".join(
        f'<div><div class="box" style="width:14pt;height:14pt;margin:0 auto"></div>'
        f'<div style="font-size:7pt;color:var(--soft);margin-top:5pt">{m}</div></div>'
        for m in ["Low", "OK", "Good", "Great"])
    back = (f'<a href="#m{month}" class="chip" style="text-decoration:none;'
            f'margin-left:14pt">Month {month}</a>' if month else "")
    return (head("Daily page", label or "Today", field_after=True, extra=back)
            + f"""<div class="body">
      <div class="card" style="flex:none;flex-direction:row;align-items:center;
           gap:14pt;padding:13pt 16pt">
        <div class="label" style="margin:0;white-space:nowrap">Just one thing today</div>
        <div class="field" style="flex:1"></div></div>
      <div class="row">
        <div class="card" style="flex:1.3">{blocks}</div>
        <div class="col" style="flex:1">
          <div class="card" style="flex:none">
            <div class="label">Meds / water</div>
            <div style="display:flex;align-items:center;gap:8pt;margin-bottom:11pt">
              <span style="font-size:7.5pt;color:var(--soft);width:30pt">Meds</span>
              {'<div class="box" style="width:13pt;height:13pt"></div>' * 2}</div>
            <div style="display:flex;align-items:center;gap:5pt">
              <span style="font-size:7.5pt;color:var(--soft);width:30pt">Water</span>
              {'<div class="box" style="width:11pt;height:11pt"></div>' * 8}</div></div>
          <div class="card" style="flex:none">
            <div class="label">Mood</div>
            <div style="display:flex;justify-content:space-between;text-align:center">
              {mood}</div></div>
          <div class="card" style="flex:1">
            <div class="label">Brain dump</div>{lines(8)}</div>
        </div></div></div>""")


def p_tasks():
    chunks = "".join(
        f'<div style="display:flex;align-items:center;gap:9pt">'
        f'<span style="font-size:8pt;color:var(--soft);width:12pt;font-weight:700">{i}</span>'
        f'<div class="box"></div><div class="field" style="flex:1"></div></div>'
        for i in range(1, 9))
    quads = [
        f'<div style="background:var(--field);border-radius:7pt;padding:10pt;flex:1">'
        f'<div style="font-size:7.5pt;font-weight:700;color:{c}">{t}</div></div>'
        for t, c in [("Now &middot; Important", "var(--accent-text)"),
                     ("Later &middot; Important", "var(--mid)"),
                     ("Now &middot; Less important", "var(--mid)"),
                     ("Doesn't need doing", "var(--soft)")]]
    return (head("Task breakdown", "Make it smaller", "One piece at a time")
            + f"""<div class="body">
      <div class="card" style="flex:none;flex-direction:row;align-items:center;gap:14pt">
        <div class="label" style="margin:0;white-space:nowrap">The big thing</div>
        <div class="field" style="flex:1"></div></div>
      <div class="row">
        <div class="card" style="flex:1.25">
          <div class="label">Broken into pieces</div>
          <div style="flex:1;display:flex;flex-direction:column;
               justify-content:space-around">{chunks}</div></div>
        <div class="col" style="flex:1">
          <div class="card" style="flex:1.6">
            <div class="label">Sort it out</div>
            <div style="flex:1;display:flex;flex-direction:column;gap:8pt">
              <div style="display:flex;gap:8pt;flex:1">{quads[0]}{quads[1]}</div>
              <div style="display:flex;gap:8pt;flex:1">{quads[2]}{quads[3]}</div>
            </div></div>
          <div class="card" style="flex:1">
            <div class="label">The first five minutes</div>
            <div style="font-size:8pt;color:var(--soft);margin-bottom:8pt">
              Just start. You don't have to finish.</div>
            <div class="field" style="flex:1;height:auto"></div></div>
        </div></div></div>""")


def tracker(names, blanks=0, corner=""):
    """31-day grid. `corner` labels the left column, which matters when the
    rows are blank for the user to fill in -- without it the column reads as
    an empty box rather than an invitation."""
    dh = "".join(f'<td class="dh {"we" if (d % 7) in (6, 0) else ""}">{d}</td>'
                 for d in range(1, 32))
    body = "".join(f'<tr><td class="nm">{n}</td>' + "<td></td>" * 31 + "</tr>"
                   for n in names)
    body += "".join('<tr><td class="nm">&nbsp;</td>' + "<td></td>" * 31 + "</tr>"
                    for _ in range(blanks))
    # the corner needs the label column's width (.nm) with the header row's
    # typography (.dh); neither class gives both
    # a labelled corner needs the underline the day columns get; without it
    # the header row is cut on one side only (same defect as TASK)
    head_cell = (f'<td style="width:104pt;border:none;'
                 f'border-bottom:1px solid var(--line);font-size:5.4pt;'
                 f'color:var(--soft);font-weight:800;text-align:left;'
                 f'vertical-align:bottom;padding:0 0 3pt 2pt">{corner}</td>'
                 ) if corner else '<td class="nm"></td>'
    return f'<table class="trk"><tr>{head_cell}{dh}</tr>{body}</table>'


def p_habits():
    names = ["Water", "Meds", "Movement", "Sleep 7h+", "Journal",
             "Tidy 10 min", "Outside", "Screen cutoff"]
    return (head("Habit tracker", "Habits" if T.get("undated") else f"January {YEAR}",
                 "One month at a time. Mark the days you showed up.")
            + f"""<div class="body">
      <div class="card" style="flex:2.2;padding:16pt 18pt">{tracker(names, 2, corner="HABIT")}</div>
      <div class="row" style="flex:1">
        <div class="card" style="flex:1"><div class="label">What worked</div>{lines(5)}</div>
        <div class="card" style="flex:1"><div class="label">What to change</div>{lines(5)}</div>
      </div></div>""")


def p_meds():
    return (head("Medication log",
                 "Medication" if T.get("undated") else f"January {YEAR}",
                 "Track the dose and how it felt")
            + f"""<div class="body">
      <div class="card" style="flex:2;padding:16pt 18pt">
        {tracker([], 9, corner="MEDICATION")}</div>
      <div class="card" style="flex:1">
        <div class="label">Side effects &middot; how you felt</div>{lines(6)}</div>
      </div>""")


# Twenty pages of paper, not one. A tab that reads like a section but holds
# a single sheet feels short next to FOCUS or LIFE, which carry ten each.
# Three kinds, because which paper you want depends on what you are writing.
# Eight, not twenty. Twenty needed 1.0MB and the only place to find it was
# the accessibility tag tree; keeping the tags is worth more than twelve
# extra blank pages.
NOTE_KINDS = [("Dot grid", "dots", 3),
              ("Ruled", "ruled", 3),
              ("Plain", "plain", 2)]
NOTE_TOTAL = sum(c for _, _, c in NOTE_KINDS)


def note_specs():
    """(page key, kind label, kind, running number) for each blank page."""
    out, n = [], 0
    for label, kind, count in NOTE_KINDS:
        for _ in range(count):
            n += 1
            out.append((f"n{n}", label, kind, n))
    return out


def p_notes():
    """The index. Every blank page has to be reachable from somewhere or
    Chrome keeps the page and drops nothing, but the reader can never get
    to it -- the same trap as a dead link, from the other side."""
    specs, n, groups = note_specs(), 0, ""
    for label, kind, count in NOTE_KINDS:
        chips = ""
        for _ in range(count):
            n += 1
            chips += (f'<a href="#n{n}" style="text-align:center;padding:10pt 0;'
                      f'background:var(--chip);color:var(--accent-text);'
                      f'border-radius:9pt;font-size:9pt;font-weight:800;'
                      f'text-decoration:none">{n}</a>')
        # Five columns at 74pt, the same grid the 52-week index uses. Eight
        # across at 58pt came to 534pt and ran off the card, which is only
        # about 461pt wide inside its padding -- chips 8 and 16 were cut.
        top = "0" if not groups else "18pt"
        groups += (f'<div class="label" style="margin:{top} 0 10pt">{label}</div>'
                   f'<div style="display:grid;'
                   f'grid-template-columns:repeat(5,74pt);gap:11pt;'
                   f'justify-content:start">{chips}</div>')
    return (head("Notes", "Blank space",
                 f"{NOTE_TOTAL} pages. Pick the paper you want.")
            # The card hugs its rows. Stretched to the page with eight chips
            # in it, it read as a mostly empty box.
            + f'<div class="body"><div class="card" style="flex:none">'
              f'{groups}</div></div>')


def p_note(label, kind, n):
    if kind == "dots":
        inner = '<div class="card dots" style="flex:1"></div>'
    elif kind == "ruled":
        # 30 is a floor; the spare rules overfill and the card clips them,
        # so the page is ruled edge to edge whatever its height works out to.
        inner = f'<div class="card" style="flex:1">{lines(30)}</div>'
    else:
        inner = '<div class="card" style="flex:1"></div>'
    # No page number in the subtitle, deliberately. A page's whole content
    # -- rail included -- is one stream, so any per-page difference makes it
    # unique and dedupe cannot fold it. Numbering the pages cost 1.0MB over
    # twenty of them and pushed the file past Etsy's 20MB cap. Without the
    # number every page of a kind is byte-identical and folds to one stream.
    # The index numbers them anyway, which is where the reader looks.
    return (head("Notes", "Blank space", label)
            + f'<div class="body">{inner}</div>')




# ------------------------------------------------- section index + tools --
def p_group(key, title, sub=""):
    """Auto-built index for a tab that has sub-pages."""
    items = GROUPS[key]
    rows = "".join(
        f'<a href="#{k}" style="display:flex;align-items:center;gap:12pt;flex:1;'
        f'padding:6pt 0;text-decoration:none;color:var(--ink);'
        f'{"" if i == len(items) - 1 else "border-bottom:1px solid var(--line)"}">'
        f'<div class="dot"></div>'
        f'<div style="flex:1"><div style="font-size:10.5pt;font-weight:700">{n}</div>'
        f'<div style="font-size:8.5pt;color:var(--soft);margin-top:2pt">{d}</div></div>'
        f'<div style="color:var(--soft);font-size:11pt">&rsaquo;</div></a>'
        for i, (k, n, d) in enumerate(items))
    return (head("Jump to", title, sub)
            + f'<div class="body"><div class="card" style="flex:none">{rows}</div>'
              f'<div class="card" style="flex:1">'
              f'<div class="label">Anything else</div>{lines(6)}</div></div>')


def prompt_card(label, hint, n_lines, flex=1, spare=None):
    # The hint slot is reserved whether or not there is a hint. Without it a
    # card with no hint is one line taller than its neighbours, so it fits an
    # extra rule -- that is why "Talk to yourself kindly" showed 2/3/2/2.
    h = (f'<div style="font-size:8pt;color:var(--soft);margin:-4pt 0 8pt;'
         f'min-height:11pt">{hint or "&nbsp;"}</div>')
    # Spare rules are only ever clipped when something outside the card sets
    # its height. When the content sets it -- the card itself on flex:none,
    # or a whole row on flex:none -- every spare rule is real height. The
    # card cannot see its parent, so a row like that passes spare=0 itself.
    if spare is None:
        spare = 0 if str(flex) == "none" else LINE_SPARE
    return (f'<div class="card" style="flex:{flex}">'
            f'<div class="label">{label}</div>{h}'
            f'{lines(n_lines, spare)}</div>')


def field_row(label):
    return (f'<div class="card" style="flex:none;flex-direction:row;'
            f'align-items:center;gap:14pt">'
            f'<div class="label" style="margin:0;white-space:nowrap">{label}</div>'
            f'<div class="field" style="flex:1"></div></div>')


def p_braindump():
    return (head("Focus", "Brain dump", "No order, no filter. Just get it out.")
            + f'<div class="body"><div class="card" style="flex:1">{lines(20)}</div>'
              + field_row("One of these, today") + '</div>')


def p_session():
    rows = "".join(
        f'<div style="flex:1;display:flex;align-items:center;gap:10pt;'
        f'{"" if i == 5 else "border-bottom:1px solid var(--line)"}">'
        f'<span style="font-size:7.5pt;font-weight:700;color:var(--soft);'
        f'width:16pt">{i + 1}</span>'
        f'<div class="field" style="flex:2"></div>'
        f'<span style="font-size:7pt;color:var(--soft)">start</span>'
        f'<div class="field" style="width:44pt"></div>'
        f'<span style="font-size:7pt;color:var(--soft)">done</span>'
        f'<div class="box"></div></div>' for i in range(6))
    return (head("Focus", "Focus session", "Short blocks, and breaks that actually happen.")
            + '<div class="body">' + field_row("Working on")
            + f'<div class="card" style="flex:2"><div class="label">Blocks</div>{rows}</div>'
              f'<div class="row" style="flex:1">'
              + prompt_card("Break ideas", "decide now, not when you are tired", 4)
              + prompt_card("What pulled me away", "", 4)
              + '</div></div>')


def p_obstacle():
    return (head("Focus", "Obstacle plan",
                 "Name what usually stops you, and pick the counter-move now.")
            + '<div class="body">' + field_row("The plan")
            + f'<div class="card" style="flex:1">'
              f'<div class="label">If this happens &hellip;</div>{lines(6)}</div>'
              f'<div class="card" style="flex:1">'
              f'<div class="label">&hellip; then I will</div>{lines(6)}</div>'
            + prompt_card("Who can I ask",
                          "asking early is cheaper than asking late", 3, "none")
            + '</div>')


def p_paralysis():
    opts = "".join(
        f'<div style="flex:1;display:flex;gap:10pt;align-items:center;'
        f'{"" if i == 2 else "border-bottom:1px solid var(--line)"}">'
        f'<span class="chip">{c}</span><div class="field" style="flex:1"></div></div>'
        for i, c in enumerate(["A", "B", "C"]))
    return (head("Focus", "Stuck on deciding",
                 "You do not need the best one. You need one.")
            + '<div class="body">' + field_row("The choice")
            + f'<div class="card" style="flex:1">'
              f'<div class="label">The options</div>{opts}</div>'
              '<div class="row" style="flex:1">'
            + prompt_card("If I pick wrong", "usually costs less than it feels", 4)
            + prompt_card("Deciding by when", "put a time on it", 4)
            + '</div>' + field_row("Picked") + '</div>')


def p_sta():
    steps = [("Stop", "what is happening in my body right now"),
             ("Think", "what do I want to happen next"),
             ("Act", "the smallest thing that moves me there")]
    cards = "".join(prompt_card(t, h, 4) for t, h in steps)
    return (head("Feelings", "Stop · Think · Act",
                 "For the moment right before you react.")
            + f'<div class="body">{cards}</div>')


def p_worry():
    return (head("Feelings", "Cycle of worry", "Write the loop down and it gets smaller.")
            + '<div class="body">'
            + prompt_card("The thought that keeps coming back", "", 3)
            + prompt_card("What it makes me do", "avoid, check, rush, freeze", 3)
            + prompt_card("What that costs me", "", 3)
            + prompt_card("What is actually likely", "evidence, not fear", 4)
            + prompt_card("One thing I will do instead", "", 2)
            + '</div>')


def p_rsd():
    return (head("Feelings", "Rejection sensitivity",
                 "When a small thing lands like a very big one.")
            + '<div class="body">'
            # six stacked cards left each one too short -- two of them came
            # out with no rule at all. Pairing them into rows gives every
            # card the same height, so the rule count matches.
            + '<div class="row">'
            + prompt_card("What happened", "just the facts, no reading into it", 3)
            + prompt_card("What I told myself it meant", "", 3)
            + '</div>'
            + '<div class="row">'
            + prompt_card("What else it could have meant",
                          "list three, even the weak ones", 4)
            + prompt_card("What would I say to a friend here", "", 3)
            + '</div>'
            + '<div class="row">'
            + prompt_card("How strong now, 0-10", "", 2)
            + prompt_card("How strong tomorrow", "come back and fill this in", 2)
            + '</div>'
            + '</div>')


def p_kind():
    return (head("Feelings", "Talk to yourself kindly",
                 "The critic is loud. That does not make it accurate.")
            + '<div class="body">'
            + prompt_card("What the critic said", "word for word", 4)
            + prompt_card("Would I say this to someone I love", "", 2)
            + prompt_card("The fairer version", "true, but not cruel", 5)
            + prompt_card("One thing I did well today", "small counts", 3)
            + '</div>')


def p_routines():
    def steps(n):
        return "".join(
            f'<div style="flex:1;display:flex;align-items:center;gap:10pt;'
            f'{"" if i == n - 1 else "border-bottom:1px solid var(--line)"}">'
            f'<div class="box"></div><div class="field" style="flex:1"></div></div>'
            for i in range(n))
    return (head("Habits", "Morning &amp; evening",
                 "The same few steps, so you are not deciding every time.")
            + '<div class="body"><div class="row">'
              f'<div class="card" style="flex:1">'
              f'<div class="label">Morning</div>{steps(7)}</div>'
              f'<div class="card" style="flex:1">'
              f'<div class="label">Evening</div>{steps(7)}</div></div>'
            + prompt_card("The step I keep skipping", "make it smaller", 2, "none")
            + '</div>')


def p_sleep():
    heads = "".join(f'<td class="dh">{h}</td>' for h in
                    ["IN BED", "ASLEEP", "WOKE", "HOURS", "ENERGY"])
    rows = "".join(
        f'<tr><td class="nm" style="height:30pt">{d}</td>'
        + '<td style="height:30pt"></td>' * 5 + '</tr>'
        for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    return (head("Health", "Sleep",
                 "Hours in, energy out. Look for the pattern, not the score.")
            + '<div class="body">'
              f'<div class="card" style="flex:none;padding:16pt 18pt">'
              f'<table class="trk" style="height:auto">'
              f'<tr><td class="nm"></td>{heads}</tr>{rows}</table></div>'
              '<div class="row" style="flex:1">'
            + prompt_card("What helped", "", 5)
            + prompt_card("What got in the way", "", 5)
            + '</div></div>')


def p_meals():
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    rows = "".join(
        f'<div style="flex:1;display:flex;align-items:center;gap:10pt;'
        f'{"" if i == len(days) - 1 else "border-bottom:1px solid var(--line)"}">'
        f'<span class="chip" style="width:30pt;text-align:center">{d}</span>'
        f'<div class="field" style="flex:1"></div></div>'
        for i, d in enumerate(days))
    return (head("Life", "Meals &amp; groceries",
                 "Decide once so the evening does not have to.")
            + '<div class="body"><div class="row">'
              f'<div class="card" style="flex:1.3">'
              f'<div class="label">This week</div>{rows}</div>'
              f'<div class="card" style="flex:1">'
              f'<div class="label">Shopping list</div>{lines(14)}</div>'
              '</div></div>')


def p_wheel():
    areas = ["Health", "Sleep", "Work", "Money", "Home",
             "People", "Fun", "Rest", "Learning", "Me"]
    rows = "".join(
        f'<div style="flex:1;display:flex;align-items:center;gap:8pt;'
        f'{"" if i == len(areas) - 1 else "border-bottom:1px solid var(--line)"}">'
        f'<span style="font-size:9pt;width:62pt">{a}</span>'
        + "".join('<div class="box" style="width:13pt;height:13pt"></div>'
                  for _ in range(10))
        + '</div>' for i, a in enumerate(areas))
    return (head("Life", "Wheel of life", "Where things stand, not where they should be.")
            + f'<div class="body"><div class="card" style="flex:2">'
              f'<div class="label">Fill in, 1 to 10</div>{rows}</div>'
              '<div class="row" style="flex:1">'
            + prompt_card("The one I want to move", "pick one, not five", 3)
            + prompt_card("The smallest first step", "", 3)
            + '</div></div>')




# ------------------------------------------------------------- batch two --
def p_quarterly():
    # Undated builds must not name months. "Jan - Mar" here was the only
    # place a month name survived the undated conversion, and it broke the
    # product's main claim -- a buyer starting in June met a page labelled
    # "Jan - Mar". Positional labels, with a field to write the span into.
    qs = (["Quarter 1", "Quarter 2", "Quarter 3", "Quarter 4"]
          if T.get("undated") else
          ["Jan \u2013 Mar", "Apr \u2013 Jun", "Jul \u2013 Sep", "Oct \u2013 Dec"])
    span = ('<div class="field" style="height:15pt;margin:0 0 8pt"></div>'
            if T.get("undated") else "")
    nlines = 5 if T.get("undated") else 6
    def card(q):
        return (f'<div class="card" style="flex:1">'
                f'<div class="label">{q}</div>{span}{lines(nlines)}</div>')
    sub = ("Long enough to matter, short enough to picture. "
           "Write the months in yourself." if T.get("undated")
           else "Long enough to matter, short enough to picture.")
    return (head("Year", "Quarterly", sub)
            + '<div class="body">'
            + f'<div class="row">{card(qs[0])}{card(qs[1])}</div>'
            + f'<div class="row">{card(qs[2])}{card(qs[3])}</div>'
            + '</div>')


def p_goals():
    fields = [("Specific", "what exactly"), ("Measurable", "how you will know"),
              ("Achievable", "with the week you actually have"),
              ("Relevant", "why this one"), ("Time-bound", "by when")]
    rows = "".join(
        f'<div style="flex:1;display:flex;align-items:center;gap:12pt;'
        f'{"" if i == len(fields) - 1 else "border-bottom:1px solid var(--line)"}">'
        f'<div style="width:78pt"><div style="font-size:9pt;font-weight:700">{t}</div>'
        f'<div style="font-size:7.5pt;color:var(--soft)">{h}</div></div>'
        f'<div class="field" style="flex:1"></div></div>'
        for i, (t, h) in enumerate(fields))
    return (head("Year", "Goals", "Vague goals are the ones that quietly disappear.")
            + '<div class="body">'
            + field_row("The goal, in one line")
            + f'<div class="card" style="flex:1.4">{rows}</div>'
            + '<div class="row" style="flex:1">'
            + prompt_card("First step this week", "small enough to start today", 3)
            + prompt_card("What would make me drop it", "plan for that now", 3)
            + '</div></div>')


def p_review():
    return (head("Year", "Monthly review", "Not a report card. Just a look back.")
            + '<div class="body"><div class="row" style="flex:1">'
            + prompt_card("What went well", "", 6)
            + prompt_card("What was hard", "", 6)
            + '</div><div class="row" style="flex:1">'
            + prompt_card("What I learned about how I work", "", 6)
            + prompt_card("One thing to change next month", "just one", 6)
            + '</div></div>')


def p_mindmap():
    # spoke centres as page percentages, so the connector lines can use the
    # same coordinates and actually meet the boxes
    spokes = [(18, 16), (82, 16), (12, 50), (88, 50), (18, 84), (82, 84)]
    lines_svg = "".join(
        f'<line x1="50" y1="50" x2="{x}" y2="{y}" stroke="#D8CFC2" '
        f'stroke-width="0.4" vector-effect="non-scaling-stroke"/>'
        for x, y in spokes)
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" '
           'preserveAspectRatio="none" style="position:absolute;inset:0;'
           'width:100%;height:100%">' + lines_svg + '</svg>')
    boxes = "".join(
        f'<div style="position:absolute;left:{x}%;top:{y}%;'
        f'transform:translate(-50%,-50%);width:112pt;height:32pt;'
        f'background:var(--field);border-radius:8pt"></div>' for x, y in spokes)
    centre = ('<div style="position:absolute;left:50%;top:50%;'
              'transform:translate(-50%,-50%);width:150pt;height:52pt;'
              'background:var(--card);border:1.5pt solid var(--accent);'
              'border-radius:12pt"></div>')
    return (head("Focus", "Mind map", "For the thoughts that refuse to be a list.")
            + '<div class="body"><div class="card" style="flex:1;position:relative">'
            + svg + boxes + centre + '</div>'
            + prompt_card("The one to start with", "", 2, "none")
            + '</div>')


def p_hyperfocus():
    return (head("Focus", "Hyperfocus log", "Not a failure. Just worth knowing where it went.")
            + '<div class="body">'
            + field_row("What pulled me in")
            + '<div class="row" style="flex:none">'
            + prompt_card("Started", "", 1, spare=0)
            + prompt_card("Stopped", "", 1, spare=0)
            + prompt_card("Hours", "", 1, spare=0)
            + '</div>'
            + prompt_card("What I got done", "give yourself the credit", 4)
            + prompt_card("What I missed", "meals, messages, sleep", 4)
            + prompt_card("Worth it?", "honestly", 3)
            + '</div>')


def p_screen():
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    heads = "".join(f'<td class="dh">{h}</td>' for h in
                    ["MORNING", "DAY", "EVENING", "TOTAL"])
    rows = "".join(
        f'<tr><td class="nm" style="height:30pt">{d}</td>'
        + '<td style="height:30pt"></td>' * 4 + '</tr>' for d in days)
    return (head("Focus", "Screen time", "The quiet one that eats whole evenings.")
            + '<div class="body">'
              f'<div class="card" style="flex:none;padding:16pt 18pt">'
              f'<table class="trk" style="height:auto">'
              f'<tr><td class="nm"></td>{heads}</tr>{rows}</table></div>'
              '<div class="row" style="flex:1">'
            + prompt_card("What I reach for first", "", 5)
            + prompt_card("What I would rather do", "", 5)
            + '</div></div>')


def p_dose():
    four = [("Dopamine", "finishing something, novelty, music"),
            ("Oxytocin", "a hug, a message to someone, a pet"),
            ("Serotonin", "sunlight, a walk, remembering a good day"),
            ("Endorphin", "moving, laughing, a cold rinse")]
    cards = "".join(prompt_card(t, h, 3) for t, h in four)
    return (head("Feelings", "D.O.S.E.", "Four things your brain runs on. Pick one you can do now.")
            + f'<div class="body">{cards}</div>')


def p_gratitude():
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    rows = "".join(
        f'<div style="flex:1;display:flex;align-items:center;gap:10pt;'
        f'{"" if i == len(days) - 1 else "border-bottom:1px solid var(--line)"}">'
        f'<span class="chip" style="width:30pt;text-align:center">{d}</span>'
        f'<div class="field" style="flex:1"></div></div>'
        for i, d in enumerate(days))
    return (head("Feelings", "Gratitude", "Small and specific beats big and vague.")
            + f'<div class="body"><div class="card" style="flex:1.4">'
              f'<div class="label">One thing a day</div>{rows}</div>'
            + prompt_card("Someone I should tell", "they probably do not know", 3)
            + '</div>')


def p_reframe():
    return (head("Feelings", "Reframe a belief", "The sentence you have repeated so long it sounds like fact.")
            + '<div class="body">'
            + prompt_card("The belief", "write it exactly as it sounds in your head", 3)
            + prompt_card("Where it came from", "who said it first", 3)
            + prompt_card("Evidence against it", "even small, even old", 5)
            + prompt_card("The version I would tell a friend", "", 4)
            + '</div>')


def p_symptoms():
    names = ["Focus", "Restless", "Irritable", "Overwhelm",
             "Fatigue", "Appetite", "Headache"]
    return (head("Health", "Symptom tracker", "Patterns are what your doctor will ask about.")
            + f'<div class="body"><div class="card" style="flex:2;padding:16pt 18pt">'
              f'{tracker(names, 3, corner="SYMPTOM")}</div>'
            + prompt_card("What seemed to trigger it", "", 4, 1)
            + '</div>')


def p_doctor():
    return (head("Health", "Doctor visit", "Write the questions down. You will forget them in the room.")
            + '<div class="body">'
            + '<div class="row" style="flex:none">'
            + prompt_card("Date", "", 1, spare=0) + prompt_card("Who", "", 1, spare=0)
            + '</div>'
            + prompt_card("What I want to ask", "put the important one first", 6)
            + prompt_card("What they said", "", 6)
            + prompt_card("What happens next", "dose, test, follow-up, by when", 4)
            + '</div>')


def p_therapy():
    return (head("Health", "Therapy notes", "Before, so you do not blank. After, so it lasts.")
            + '<div class="body"><div class="row" style="flex:1">'
            + prompt_card("Before \u2014 what to bring up", "", 8)
            + prompt_card("After \u2014 what I took away", "", 8)
            + '</div>'
            + prompt_card("To try before next time", "one thing", 3, "none")
            + '</div>')


def p_cleaning():
    rooms = ["Kitchen", "Bathroom", "Bedroom", "Living room", "Desk", "Laundry"]
    heads = "".join(f'<td class="dh">{h}</td>' for h in
                    ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"])
    rows = "".join(
        f'<tr><td class="nm" style="height:30pt">{r}</td>'
        + '<td style="height:30pt"></td>' * 7 + '</tr>' for r in rooms)
    return (head("Life", "Cleaning", "One room, ten minutes. Not the whole house.")
            + '<div class="body">'
              f'<div class="card" style="flex:none;padding:16pt 18pt">'
              f'<table class="trk" style="height:auto">'
              f'<tr><td class="nm"></td>{heads}</tr>{rows}</table></div>'
            + prompt_card("The one that bothers me most", "start there", 3, 1)
            + '</div>')


def p_budget():
    def money_rows(n):
        return "".join(
            f'<div style="flex:1;display:flex;align-items:center;gap:10pt;'
            f'{"" if i == n - 1 else "border-bottom:1px solid var(--line)"}">'
            f'<div class="field" style="flex:2"></div>'
            f'<div class="field" style="width:62pt"></div></div>' for i in range(n))
    return (head("Life", "Monthly budget", "In, out, and what is actually left.")
            + '<div class="body"><div class="row">'
              f'<div class="card" style="flex:1">'
              f'<div class="label">Coming in</div>{money_rows(4)}</div>'
              f'<div class="card" style="flex:1">'
              f'<div class="label">Fixed</div>{money_rows(4)}</div></div>'
              f'<div class="card" style="flex:1">'
              f'<div class="label">Everything else</div>{money_rows(6)}</div>'
            + field_row("Left over")
            + '</div>')


def p_impulse():
    checks = ["Do I already own something that does this?",
              "Where exactly will it live?",
              "Would I still want it in a week?",
              "Am I buying it, or buying the feeling?",
              "Can I afford it without moving anything else?"]
    rows = "".join(
        f'<div style="flex:1;display:flex;align-items:center;gap:12pt;'
        f'{"" if i == len(checks) - 1 else "border-bottom:1px solid var(--line)"}">'
        f'<div class="box"></div>'
        f'<span style="font-size:9.5pt;flex:1">{c}</span></div>'
        for i, c in enumerate(checks))
    return (head("Life", "Before you buy it", "Ten minutes now, or a returns label later.")
            + '<div class="body">'
            + field_row("The thing")
            + f'<div class="card" style="flex:1.4">{rows}</div>'
            + '<div class="row" style="flex:1">'
            + prompt_card("Decided", "yes, no, or in a week", 2)
            + prompt_card("If no, what instead", "", 2)
            + '</div></div>')


def p_reading():
    rows = "".join(
        f'<div style="flex:1;display:flex;align-items:center;gap:10pt;'
        f'{"" if i == 9 else "border-bottom:1px solid var(--line)"}">'
        f'<div class="box"></div>'
        f'<div class="field" style="flex:3"></div>'
        f'<div class="field" style="width:52pt"></div></div>' for i in range(10))
    return (head("Life", "Reading log", "Finished, abandoned, both count.")
            + f'<div class="body"><div class="card" style="flex:1">'
              f'<div class="label">Book &amp; when</div>{rows}</div>'
            + prompt_card("The one I keep thinking about", "", 3, "none")
            + '</div>')




# ----------------------------------------------------------- batch three --
def two_col_rows(n, left=3, right=1, last=None):
    """n rows of two fields, wide then narrow."""
    return "".join(
        f'<div style="flex:1;display:flex;align-items:center;gap:10pt;'
        f'{"" if i == n - 1 else "border-bottom:1px solid var(--line)"}">'
        f'<div class="field" style="flex:{left}"></div>'
        f'<div class="field" style="flex:{right}"></div></div>' for i in range(n))


def check_rows(n, wide=1):
    return "".join(
        f'<div style="flex:1;display:flex;align-items:center;gap:10pt;'
        f'{"" if i == n - 1 else "border-bottom:1px solid var(--line)"}">'
        f'<div class="box"></div>'
        f'<div class="field" style="flex:{wide}"></div></div>' for i in range(n))


def p_project():
    return (head("Year", "Project planner", "One thing, from start to actually finished.")
            + '<div class="body">' + field_row("The project")
            + '<div class="row">'
            + f'<div class="card" style="flex:1"><div class="label">Steps</div>'
              f'{check_rows(8)}</div>'
            + '<div class="col" style="flex:1">'
            + prompt_card("Done looks like", "be specific", 4)
            + prompt_card("Waiting on someone", "name and what for", 4)
            + '</div></div>'
            + field_row("Next thing I will do")
            + '</div>')


def p_weekly_review():
    return (head("Year", "Weekly review", "Five minutes on a Sunday beats an hour in a crisis.")
            + '<div class="body"><div class="row" style="flex:1">'
            + prompt_card("What got done", "count the small ones too", 6)
            + prompt_card("What did not", "and whether it still matters", 6)
            + '</div><div class="row" style="flex:1">'
            + prompt_card("What drained me", "", 5)
            + prompt_card("What to carry into next week", "three at most", 5)
            + '</div></div>')


def p_vision():
    # All four cards go through prompt_card. Building a card by hand skips
    # the reserved hint slot, so its rules start 11pt higher and one more
    # fits -- the top pair had six rules against the bottom pair's five.
    boxes = "".join(prompt_card(t, "", 5)
                    for t in ["This year", "Three years"])
    return (head("Year", "Vision page", "Not a plan. Just the direction.")
            # both pairs go in rows: with only the top pair wrapped, the
            # row's gap made those two cards shorter and they fitted one
            # rule fewer than the pair below.
            + f'<div class="body"><div class="row">{boxes}</div>'
            + '<div class="row">'
            + prompt_card("What I want more of", "", 4)
            + prompt_card("What I want less of", "", 4)
            + '</div></div>')


def p_estimate():
    heads = "".join(f'<td class="dh">{h}</td>' for h in ["GUESS", "ACTUAL", "OFF BY"])
    rows = "".join(
        '<tr><td class="nm" style="height:30pt"></td>'
        + '<td style="height:30pt"></td>' * 3 + '</tr>' for _ in range(9))
    return (head("Focus", "Guess vs actual",
                 "Time blindness is not a character flaw. It is measurable.")
            + '<div class="body">'
              f'<div class="card" style="flex:none;padding:16pt 18pt">'
              f'<table class="trk" style="height:auto">'
              f'<tr><td class="nm">TASK</td>{heads}</tr>{rows}</table></div>'
            + prompt_card("What I consistently underestimate", "", 4, 1)
            + '</div>')


def p_avoiding():
    reasons = ["I do not know where to start",
               "It will take longer than I have",
               "I might do it badly",
               "It is boring",
               "I need something from someone else",
               "It reminds me of something else"]
    rows = "".join(
        f'<div style="flex:1;display:flex;align-items:center;gap:12pt;'
        f'{"" if i == len(reasons) - 1 else "border-bottom:1px solid var(--line)"}">'
        f'<div class="box"></div>'
        f'<span style="font-size:9.5pt;flex:1">{r}</span></div>'
        for i, r in enumerate(reasons))
    return (head("Focus", "Why I am avoiding it",
                 "Name the reason and the task usually shrinks.")
            + '<div class="body">' + field_row("The thing")
            + f'<div class="card" style="flex:1.3">'
              f'<div class="label">Which one is it</div>{rows}</div>'
            + '<div class="row" style="flex:1">'
            + prompt_card("So the first step is", "make it absurdly small", 3)
            + prompt_card("Ten minutes only", "set a timer, stop when it rings", 3)
            + '</div></div>')


def p_deadline():
    rows = "".join(
        f'<div style="flex:1;display:flex;align-items:center;gap:10pt;'
        f'{"" if i == 6 else "border-bottom:1px solid var(--line)"}">'
        f'<div class="field" style="width:58pt"></div>'
        f'<div class="field" style="flex:1"></div></div>' for i in range(7))
    return (head("Focus", "Working backwards",
                 "Start at the date it is due and walk back to today.")
            + '<div class="body">'
            + '<div class="row" style="flex:none">'
            + prompt_card("Due", "", 1, spare=0)
            + prompt_card("Today", "", 1, spare=0)
            + '</div>'
            + f'<div class="card" style="flex:1">'
              f'<div class="label">Date &amp; what has to be done by then</div>{rows}</div>'
            + prompt_card("The first one is due", "put it in the calendar now", 2, "none")
            + '</div>')


def p_name_it():
    words = ["tired", "wired", "flat", "frayed", "restless", "heavy",
             "prickly", "numb", "hopeful", "ashamed", "relieved", "lonely"]
    chips = "".join(f'<span class="chip" style="margin:3pt 4pt 3pt 0">{w}</span>'
                    for w in words)
    return (head("Feelings", "Name the feeling",
                 "A vague feeling stays loud. A named one gets quieter.")
            + '<div class="body">'
              f'<div class="card" style="flex:none"><div class="label">Borrow a word</div>'
              f'<div style="line-height:2">{chips}</div></div>'
            + prompt_card("Closest to it", "", 2)
            + prompt_card("Where I feel it in my body", "chest, jaw, stomach", 3)
            + prompt_card("What happened just before", "", 4)
            + prompt_card("What it might be asking for", "rest, food, company, an end", 3)
            + '</div>')


def p_boundaries():
    return (head("Feelings", "Boundaries", "Decide once, so you are not deciding at 11pm.")
            + '<div class="body"><div class="row" style="flex:1">'
            + prompt_card("I will", "", 7)
            + prompt_card("I will not", "", 7)
            + '</div>'
            + prompt_card("How I will say it", "one sentence, no apology", 3, "none")
            + '</div>')


def p_energy():
    rows = "".join(
        f'<div style="flex:1;display:flex;align-items:center;gap:10pt;'
        f'{"" if i == 7 else "border-bottom:1px solid var(--line)"}">'
        f'<div class="field" style="flex:3"></div>'
        + "".join('<div class="box" style="width:12pt;height:12pt"></div>'
                  for _ in range(5))
        + '</div>' for i in range(8))
    return (head("Feelings", "Energy budget",
                 "You have less than the calendar suggests. Spend it on purpose.")
            + f'<div class="body"><div class="card" style="flex:1.6">'
              f'<div class="label">What it costs, 1 to 5</div>{rows}</div>'
            + '<div class="row" style="flex:1">'
            + prompt_card("What gives it back", "", 4)
            + prompt_card("What I will drop", "something has to go", 4)
            + '</div></div>')


def p_intake():
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    rows = "".join(
        f'<div style="flex:1;display:flex;align-items:center;gap:8pt;'
        f'{"" if i == len(days) - 1 else "border-bottom:1px solid var(--line)"}">'
        f'<span class="chip" style="width:30pt;text-align:center">{d}</span>'
        + "".join('<div class="box" style="width:11pt;height:11pt"></div>'
                  for _ in range(8))
        + '<span style="font-size:7pt;color:var(--soft);margin-left:8pt">meals</span>'
        + "".join('<div class="box" style="width:11pt;height:11pt"></div>'
                  for _ in range(3))
        + '</div>' for i, d in enumerate(days))
    return (head("Health", "Water &amp; food", "The two that slip first when you are busy.")
            + f'<div class="body"><div class="card" style="flex:1.4">'
              f'<div class="label">Glasses, then meals</div>{rows}</div>'
            + prompt_card("What makes eating hard on bad days", "", 4)
            + '</div>')


def p_movement():
    heads = "".join(f'<td class="dh">{h}</td>' for h in ["WHAT", "HOW LONG", "AFTER"])
    rows = "".join(
        f'<tr><td class="nm" style="height:30pt">{d}</td>'
        + '<td style="height:30pt"></td>' * 3 + '</tr>'
        for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    return (head("Health", "Movement", "Any amount counts. Walking counts.")
            + '<div class="body">'
              f'<div class="card" style="flex:none;padding:16pt 18pt">'
              f'<table class="trk" style="height:auto">'
              f'<tr><td class="nm"></td>{heads}</tr>{rows}</table></div>'
            + '<div class="row" style="flex:1">'
            + prompt_card("What I actually enjoy", "not what I should do", 5)
            + prompt_card("Easiest version on a bad day", "", 5)
            + '</div></div>')


def p_cycle():
    names = ["Period", "Cramps", "Mood", "Energy", "Focus", "Sleep", "Appetite"]
    return (head("Health", "Cycle tracker",
                 "Symptoms often follow it. Worth having the two side by side.")
            + f'<div class="body"><div class="card" style="flex:2;padding:16pt 18pt">'
              f'{tracker(names, 2, corner="WHAT I TRACK")}</div>'
            + prompt_card("What I noticed this month", "", 4, 1)
            + '</div>')


def p_dates():
    return (head("Life", "Dates to remember",
                 "Birthdays, renewals, appointments. The ones that arrive without warning.")
            + f'<div class="body"><div class="card" style="flex:1">'
              f'<div class="label">Date &amp; what</div>{two_col_rows(12, 1, 3)}</div>'
            + prompt_card("Needs buying ahead", "", 3, "none")
            + '</div>')


def p_subs():
    heads = "".join(f'<td class="dh">{h}</td>' for h in
                    ["WHAT", "RENEWS", "COST", "STILL USE?"])
    rows = "".join(
        '<tr>' + '<td style="height:28pt"></td>' * 4 + '</tr>' for _ in range(11))
    return (head("Life", "Subscriptions", "The quiet ones that renew while you are not looking.")
            + '<div class="body">'
              f'<div class="card" style="flex:none;padding:16pt 18pt">'
              f'<table class="trk" style="height:auto">'
              f'<tr>{heads}</tr>{rows}</table></div>'
            + '<div class="row" style="flex:1">'
            + prompt_card("Cancelling this month", "", 4)
            + prompt_card("Total per month", "add it up once, it helps", 4)
            + '</div></div>')


def p_travel():
    cols = [("Booked", ["Travel", "Somewhere to stay", "Time off", "Cover for pets",
                        "Someone told"]),
            ("Packed", ["Medication", "Chargers", "Documents", "Clothes",
                        "Something for the journey"])]
    cards = "".join(
        f'<div class="card" style="flex:1"><div class="label">{t}</div>'
        + "".join(
            f'<div style="flex:1;display:flex;align-items:center;gap:12pt;'
            f'{"" if i == len(items) - 1 else "border-bottom:1px solid var(--line)"}">'
            f'<div class="box"></div>'
            f'<span style="font-size:9.5pt;flex:1">{it}</span></div>'
            for i, it in enumerate(items))
        + '</div>' for t, items in cols)
    return (head("Life", "Trip checklist", "Packed, booked, charged.")
            + f'<div class="body"><div class="row">{cards}</div>'
            + f'<div class="card" style="flex:1"><div class="label">Anything else</div>'
              f'{check_rows(5)}</div></div>')


def p_chores():
    heads = "".join(f'<td class="dh">{h}</td>' for h in ["WHO", "HOW OFTEN", "LAST DONE"])
    rows = "".join(
        '<tr><td class="nm" style="height:28pt"></td>'
        + '<td style="height:28pt"></td>' * 3 + '</tr>' for _ in range(10))
    return (head("Life", "Who does what", "Split it on paper before it turns into a row.")
            + '<div class="body">'
              f'<div class="card" style="flex:none;padding:16pt 18pt">'
              f'<table class="trk" style="height:auto">'
              f'<tr><td class="nm">TASK</td>{heads}</tr>{rows}</table></div>'
            + prompt_card("The one nobody wants", "rotate it", 3, 1)
            + '</div>')




# ------------------------------------------- undated month / week / day --
def p_months():
    """Index of the twelve month pages."""
    def card(m):
        return (f'<a href="#m{m}" class="card" style="flex:1;'
                f'text-decoration:none;color:var(--ink);'
                f'justify-content:center;align-items:center">'
                f'<div style="font-size:12pt;font-weight:800">Month {m}</div>'
                f'<div class="field" style="width:64%;height:15pt;'
                f'margin-top:9pt"></div></a>')
    rows = "".join(
        f'<div class="row" style="flex:1">'
        + "".join(card(m) for m in range(i, min(i + 4, MONTHS + 1)))
        + '</div>' for i in range(1, MONTHS + 1, 4))
    return (head("Plan", "Twelve months",
                 "Write the month in yourself. Tap one to open it.")
            + f'<div class="body">{rows}</div>')


def month_grid(m):
    """1..31, each cell linking to that month's day page."""
    rows, n = "", 1
    for _ in range(5):
        cells = ""
        for _ in range(7):
            if n <= DAYS:
                cells += (f'<td style="border:1px solid var(--line);'
                          f'vertical-align:top;padding:5pt 6pt">'
                          f'<a href="#d{m}-{n}" style="font-size:8.5pt;'
                          f'font-weight:700;color:var(--accent-text);'
                          f'text-decoration:none">{n}</a></td>')
                n += 1
            else:
                cells += '<td style="border:1px solid var(--line)"></td>'
        rows += f"<tr>{cells}</tr>"
    return f'<table class="cal">{rows}</table>'


def p_month_n(m):
    # Undated, so "Month 1" is whichever month the buyer starts in. Every
    # grid therefore carries 31 slots; saying so on the page keeps it from
    # reading as a calendar that got February wrong.
    return (head("Plan", f"Month {m}",
                 "Thirty-one slots, so any month fits. "
                 "Leave the spare ones blank.", field_after=True)
            + '<div class="body">'
              f'<div class="card" style="flex:1;padding:16pt 18pt">'
              f'{month_grid(m)}</div>'
            + field_row("This month's focus") + '</div>')


def p_weeks():
    chips = "".join(
        f'<a href="#w{w}" style="width:74pt;text-align:center;padding:11pt 0;'
        f'background:var(--chip);color:var(--accent-text);border-radius:10pt;'
        f'font-size:9.5pt;font-weight:800;text-decoration:none">{w}</a>'
        for w in range(1, WEEKS + 1))
    return (head("Plan", "Fifty-two weeks", "Tap a number to open that week.")
            # A grid, not wrapped flex. Wrapping centred the short last row,
            # so 51 and 52 floated between the columns instead of sitting
            # under 46 and 47.
            + '<div class="body"><div class="card" style="flex:1">'
              '<div style="display:grid;grid-template-columns:repeat(5,74pt);'
              'gap:11pt;justify-content:center;align-content:center;'
              f'height:100%">{chips}</div></div></div>')


# ------------------------------------------------------------------ build --
def font_url():
    fams = [f"family={T['font']}:wght@{T['weights']}"]
    if T["display"]:
        fams.append(f"family={T['display']}:wght@600;700")
    return "https://fonts.googleapis.com/css2?" + "&".join(fams) + "&display=swap"


def build_bloom_assets():
    """Bake the two bloom positions once per theme."""
    d = os.path.join(ROOT, "assets")
    os.makedirs(d, exist_ok=True)
    if T.get("ink_wash"):
        ink_wash_png(os.path.join(d, f"ink_page_{VERSION}.png"),
                     INK_SPOTS["page"])
        ink_wash_png(os.path.join(d, f"ink_cover_{VERSION}.png"),
                     INK_SPOTS["cover"])
    if not T.get("photo"):
        return
    bloom_png(os.path.join(d, f"bloom_cover_{VERSION}.png"), 306, 250, scale=0.5)
    bloom_png(os.path.join(d, f"bloom_page_{VERSION}.png"), 330, 92, scale=0.5)
    if T.get("fast_paint"):
        bloom_baked_png(os.path.join(d, f"bloom_page_{VERSION}.png"),
                        os.path.join(d, f"bloom_page_baked_{VERSION}.png"),
                        T["bg"], T["bloom_page"])
        shadow_png(os.path.join(d, f"shadow_{VERSION}.png"))


def bloom_baked_png(src, path, bg, opacity):
    """The page bloom composited onto the page colour, saved opaque.

    Same pixels the viewer would get from drawing the RGBA bloom at
    `opacity` over --bg, but done once here instead of on every page.
    """
    import numpy as np
    from PIL import Image
    b = np.asarray(Image.open(src).convert("RGBA")).astype(np.float64) / 255
    base = np.array([int(bg[i:i + 2], 16) for i in (1, 3, 5)]) / 255
    al = b[..., 3:4] * opacity
    rgb = b[..., :3] * al + base * (1 - al)
    Image.fromarray(np.round(rgb * 255).astype(np.uint8), "RGB").save(
        path, optimize=True)
    return path


def shadow_png(path, w=800, h=80):
    """radial-gradient(ellipse 62% 100% at 50% 0%, rgba(0,0,0,.07), 0 at 72%)
    sampled once. Both radii are relative to the box, so stretching this to
    any card reproduces the CSS gradient."""
    import numpy as np
    from PIL import Image
    x = (np.arange(w) + .5) / w - .5
    y = (np.arange(h) + .5) / h
    d = np.sqrt((x[None, :] / .62) ** 2 + (y[:, None] / 1.0) ** 2)
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[..., 3] = np.round(np.clip(1 - d / .72, 0, 1) * .07 * 255)
    Image.fromarray(rgba, "RGBA").save(path, optimize=True)
    return path


def build_html():
    specs = [
        ("cover", p_cover), ("index", p_index),
        ("year", lambda: p_group("year", "Year",
                                 "The long view, four ways")),
        ("quarterly", p_quarterly),
        ("goals", p_goals), ("review", p_review),
        ("project", p_project),
        ("weekly-review", p_weekly_review), ("vision", p_vision),
    ] + ([("month", p_months)] if T.get("undated") else
         [("year-grid", p_year), ("month", p_month),
          ("week", p_week), ("day", p_day)]) + [
        ("focus", lambda: p_group("focus", "Focus",
                                  "For when starting is the hard part")),
        ("tasks", p_tasks), ("braindump", p_braindump), ("session", p_session),
        ("obstacle", p_obstacle), ("paralysis", p_paralysis), ("mindmap", p_mindmap),
        ("hyperfocus", p_hyperfocus), ("screen", p_screen),
        ("estimate", p_estimate), ("avoiding", p_avoiding),
        ("deadline", p_deadline),
        ("feel", lambda: p_group("feel", "Feelings",
                                 "For the days that land heavier than they should")),
        ("sta", p_sta), ("worry", p_worry), ("rsd", p_rsd), ("kind", p_kind),
        ("dose", p_dose), ("gratitude", p_gratitude),
        ("reframe", p_reframe), ("name-it", p_name_it),
        ("boundaries", p_boundaries), ("energy", p_energy),
        ("habits", lambda: p_group("habits", "Habits",
                                   "Small things, repeated, without the guilt")),
        ("habits-grid", p_habits), ("routines", p_routines),
        ("health", lambda: p_group("health", "Health",
                                   "What you took, and how you slept")),
        ("meds", p_meds), ("sleep", p_sleep), ("symptoms", p_symptoms),
        ("doctor", p_doctor), ("therapy", p_therapy),
        ("intake", p_intake), ("movement", p_movement),
        ("cycle", p_cycle),
        ("life", lambda: p_group("life", "Life",
                                 "The admin that eats the week")),
        ("meals", p_meals), ("wheel", p_wheel), ("cleaning", p_cleaning),
        ("budget", p_budget), ("impulse", p_impulse),
        ("reading", p_reading), ("dates", p_dates), ("subs", p_subs),
        ("travel", p_travel), ("chores", p_chores),
        ("notes", p_notes),
    ] + [
        (k, (lambda lb, kd, num: lambda: p_note(lb, kd, num))(lb, kd, num))
        for k, lb, kd, num in note_specs()
    ] + [
    ]
    if student_pages:
        specs = student_pages.specs()
    elif T.get("undated"):
        # the repeated sets: twelve month grids, each month's days, the weeks
        for m in range(1, MONTHS + 1):
            specs.append((f"m{m}", (lambda mm: lambda: p_month_n(mm))(m)))
            for d in range(1, DAYS + 1):
                specs.append((f"d{m}-{d}",
                              (lambda mm, dd: lambda: p_day(f"Day {dd}", mm))(m, d)))
        specs.append(("week", p_weeks))
        for w in range(1, WEEKS + 1):
            specs.append((f"w{w}", (lambda ww: lambda: p_week(f"Week {ww}"))(w)))
    pages = [page(k, fn()) for k, fn in specs]
    font_url_v = font_url()
    # PDF 의 /Title 이 된다. 학생용에도 상품 1 이름이 박혀 있었다(2026-09-24).
    # 상품 1 값은 그대로 둔다 -- 판매본을 바이트까지 다시 뽑을 수 있어야 한다.
    doc_title = ("ADHD Student Planner &mdash; Undated Semester Planner"
                 if T.get("student") else "ADHD &amp; Wellness Planner")
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>{doc_title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{font_url_v}" rel="stylesheet">
<style>{CSS}</style></head>
<body>{"".join(pages)}</body></html>"""
    os.makedirs(os.path.dirname(SRC), exist_ok=True)
    with open(SRC, "w", encoding="utf-8") as f:
        f.write(html)
    return SRC


# ---------------------------------------------------------------- snap ----
SNAP_PROBE = r"""
// A card's height once its rules end where the box does, or null when the
// card should be left alone.
function needed(card){
  const L = card.querySelector(':scope > .lines');
  if(!L) return null;
  const k = [...L.children];
  if(!k.length) return null;
  const P = k[0].getBoundingClientRect().height;
  if(!P) return null;
  if(card.lastElementChild !== L) return null;   // something sits below
  const H = L.clientHeight;
  // The box is exactly its rules already -- a spare=0 card, sized by them.
  if(Math.abs(k.length*P - H) < 1) return null;
  const lb = L.getBoundingClientRect();
  let kk = 0;
  for(const d of k){
    if(d.getBoundingClientRect().bottom <= lb.bottom + 0.5) kk++; else break;
  }
  if(kk < 1) return null;
  // One pixel under the last rule, not zero: on the boundary the rasteriser
  // may drop it.
  return card.getBoundingClientRect().height - (H - (kk*P + 1));
}

const out = [], rowPins = [];
const inRow = new Set();

// Rows first. Pin the ROW, never the cards inside it -- pinning the cards
// and holding them with align-self:flex-start let the two sides of a row
// end at different heights (47p Meals & groceries), and left the row itself
// full size so the slack opened as a hole above the card below it
// (32p Boundaries, 49p Cleaning).
document.querySelectorAll('.row').forEach(row => {
  // Every card anywhere under the row is off limits to the per-card pass --
  // including the ones nested in a .col. Pinning one of those shortened the
  // column and left the two sides of a daily page ending at different
  // heights (121p).
  row.querySelectorAll('.card').forEach(c => inRow.add(c));
  const kids = [...row.children];
  let key = null, want = 0, any = false;
  for(const el of kids){
    const L = el.querySelector('.lines[data-ln]');
    if(L && !key) key = L.getAttribute('data-ln');
    const h = el.getBoundingClientRect().height;
    if(el.classList.contains('card')){
      const n = needed(el);
      if(n === null){ want = Math.max(want, h); }
      else { want = Math.max(want, n); any = true; }
    } else {
      // A column: its bottom is set by its last card, so it can give back
      // only that card's slack.
      const cards = [...el.children].filter(c => c.classList.contains('card'));
      const last = cards[cards.length - 1];
      const n = last ? needed(last) : null;
      if(n === null){ want = Math.max(want, h); }
      else {
        want = Math.max(want,
                        h - (last.getBoundingClientRect().height - n));
        any = true;
      }
    }
  }
  if(!key || !any) return;
  const h = row.getBoundingClientRect().height;
  if(Math.abs(h - want) < 0.5) return;
  rowPins.push({id: key, h: Math.round(want*100)/100});
});

// Cards that stand on their own in the column.
document.querySelectorAll('.lines[data-ln]').forEach(L => {
  const card = L.closest('.card');
  if(!card || inRow.has(card)) return;
  if(L.parentElement !== card) return;
  const n = needed(card);
  if(n === null) return;
  if(Math.abs(card.getBoundingClientRect().height - n) < 0.5) return;
  out.push({id: L.getAttribute('data-ln'), h: Math.round(n*100)/100});
});

document.body.setAttribute('data-probe', JSON.stringify({c: out, r: rowPins}));
"""


def snap_cards():
    """Make every ruled card an exact whole number of rule pitches tall.

    The rules have a fixed height, but the card's height comes from flex, so
    what is left over after the last rule is `H mod pitch` -- measured at
    0 to 35px across the document. That slack is visible as an uneven bottom
    margin, and it cannot be removed in CSS because CSS has no modulo.

    Pushing the slack to the top instead (justify-content:flex-end) was tried
    and is worse: it eats into the first row, which then has less than a full
    line of writing space on 87 of 115 blocks.

    So the card is measured once and then pinned to header + k*pitch. The
    slack moves out of the card and into the gaps between cards, where it is
    not readable as a half-empty row. The pins go in an appended stylesheet
    keyed by data-ln, so the generated markup stays untouched.
    """
    html = io.open(SRC, encoding="utf-8").read()
    tmp = os.path.join(tempfile.gettempdir(), "snap_probe.html")
    io.open(tmp, "w", encoding="utf-8").write(
        html.replace("</body>", f"<script>{SNAP_PROBE}</script></body>"))
    profile = os.path.join(tempfile.gettempdir(), "planner-snap-profile")
    r = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", f"--user-data-dir={profile}",
         "--virtual-time-budget=25000", "--dump-dom",
         "file:///" + tmp.replace(chr(92), "/")],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.search(r'data-probe="([^"]*)"', r.stdout or "")
    if not m:
        raise RuntimeError("snap 측정 실패: Chrome 이 결과를 내놓지 "
                           "않았다 " + (r.stderr or "")[-400:])
    got = json.loads(m.group(1).replace("&quot;", '"'))
    pins, rowpins = got["c"], got["r"]
    if not pins and not rowpins:
        return 0
    rules = ["/* snap: ruled boxes pinned to a whole number of rule pitches */"]
    for r in rowpins:
        # The row is pinned and its cards stretch to it, so the two sides of
        # a row always end level.
        rules.append(
            f'.row:has(>.card>[data-ln="{r["id"]}"])'
            f'{{flex:none!important;height:{r["h"]}px!important;'
            f'min-height:0!important}}')
    for c in pins:
        # A card standing on its own in the column: flex sets its height
        # there, so flex has to be cleared for height to win.
        rules.append(
            f'.card:has(>[data-ln="{c["id"]}"])'
            f'{{flex:none!important;height:{c["h"]}px!important;'
            f'min-height:0!important}}')
    html = html.replace("</head>",
                        "<style>" + chr(10).join(rules) + "</style></head>")
    io.open(SRC, "w", encoding="utf-8").write(html)
    return len(pins) + len(rowpins)


def to_pdf():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    before = os.path.getmtime(OUT) if os.path.exists(OUT) else 0

    # A dedicated profile dir is required: with the default one, a Chrome the
    # user already has open holds the lock, and the headless call exits 0
    # without ever writing the PDF.
    profile = os.path.join(tempfile.gettempdir(), "planner-chrome-profile")
    r = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", f"--user-data-dir={profile}",
         "--no-pdf-header-footer", f"--print-to-pdf={OUT}",
         "file:///" + SRC.replace("\\", "/")],
        capture_output=True, text=True, encoding="utf-8", errors="replace")

    if not os.path.exists(OUT) or os.path.getmtime(OUT) <= before:
        raise RuntimeError(
            "Chrome exited without writing a new PDF.\n"
            f"returncode={r.returncode}\nstdout={r.stdout}\nstderr={r.stderr}")
    return OUT


if __name__ == "__main__":
    if app_style:
        for f in app_style.build_assets(VERSION):
            print("baked:", f)
    build_bloom_assets()
    build_html()
    # One pass is not enough: pinning a card frees space that the cards still
    # on flex:1 absorb, which moves them off the pitch again. Re-measure until
    # nothing is left to pin.
    for _pass in range(1, 8):
        n = snap_cards()
        print(f"snap pass {_pass}: pinned {n}")
        if not n:
            break
    if app_style:           # 학생용 면은 SVG 괘선이라 위 측정이 못 본다
        print("snap lines: pinned", app_style.snap_lines(SRC, CHROME))
    to_pdf()
    if student_pages:       # 사이드바 북마크. Chrome 은 개요를 만들지 않는다
        print("outline:", student_pages.add_outline(OUT), "items")
    print("Saved:", OUT)
