# -*- coding: utf-8 -*-
"""상품 2(학생용) 산출물 검사. 구조 + 눈으로 보이는 결함까지.

    python scripts/verify_student.py [버전]        기본 student-v0.1

`verify_v8.py` 의 구조 검사 13항목을 옮겨오고, 2026-09-22 하루 동안
"검사는 통과인데 눈으로는 깨져 있던" 종류를 항목으로 만들었다:

  · 점선이 확대율마다 길이·두께가 달라짐
      -> 정수 배율(12배)로만 재면 전부 통과한다. 1.5/2/2.5/3배로 재야
         드러난다. 주기와 줄 간격이 4의 배수 pt 가 아니면 여기서 잡힌다.
  · 면 그림자가 한 종류만 빠짐
      -> brain dump 의 필기면만 overflow:hidden 이라 ::after 가 잘렸다.
         고유 템플릿 전부에서 면 아래 어두워지는지 잰다.
  · 괘선이 면의 반쪽만 채움
      -> <svg> 를 width:auto 로 두면 고유 크기(300x150px)로 눕는다.
         마지막 줄이 면 바닥 가까이 오는지 잰다.

검사가 사용자의 눈보다 느슨하면 검사가 아니다. 새 결함을 만나면
반드시 여기에 항목을 하나 추가하고 나서 고칠 것.
"""
import io
import os
import re
import sys
from collections import Counter

import numpy as np
import pypdfium2 as pdfium
from pypdf import PdfReader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = sys.argv[1] if len(sys.argv) > 1 else "student-v0.1"
RAW = os.path.join(ROOT, "output", "prod2", "planner_%s.pdf" % VERSION)
HTML = os.path.join(ROOT, "src", "planner_%s.html" % VERSION)
# 검사 대상은 파는 파일(dedupe 후)이다. 2026-09-23 까지 빌드 직후 파일을
# 재서 21.21MB "상한 초과"로 판정했는데, 실제 판매본은 14.94MB 였다.
# 빌드보다 오래된 FINAL 은 낡은 결과를 재는 것이므로 거부한다.
PDF = os.path.join(ROOT, "output", "prod2", "planner_%s-FINAL.pdf" % VERSION)
# 빌드는 HTML 을 먼저 쓰고(snap 이 한 번 더 고쳐 쓴다) PDF 를 나중에 쓴다.
# PDF 가 HTML 보다 오래됐으면 Chrome 이 쓰지 못한 것이다. 2026-09-24 에
# 빌드가 실패했는데 `빌드 | tail && dedupe` 의 파이프가 종료 코드를 삼켜
# dedupe 가 낡은 PDF 로 새 FINAL 을 만들었고, 아래 FINAL 검사만으로는
# 통과했다. HTML 기반 검사는 새 HTML 을, PDF 검사는 낡은 PDF 를 재고 있었다.
if not os.path.exists(RAW) or os.path.getmtime(RAW) < os.path.getmtime(HTML):
    sys.exit("PDF 가 없거나 HTML 보다 오래됐다 -- 빌드가 PDF 를 쓰지 못했다. "
             "빌드 출력의 오류를 보고 다시 빌드할 것")
if not os.path.exists(PDF) or os.path.getmtime(PDF) < os.path.getmtime(RAW):
    sys.exit("FINAL 이 없거나 빌드보다 오래됐다. 먼저:\n"
             "  python scripts/dedupe_pdf.py %s %s" % (
                 os.path.relpath(RAW, ROOT), os.path.relpath(PDF, ROOT)))

LIMIT = 20_000_000          # Etsy 디지털 파일 상한
ZOOMS = (1.5, 2.0, 2.5, 3.0)
MIN_SHADOW = 15.0           # 면 아래 밝기 회복폭. 정상은 23~27
MONTHS = (r"\b(January|February|March|April|May|June|July|August|September|"
          r"October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|"
          r"Nov|Dec)\b")

checks = []                 # (이름, 실제값, 기대, 통과?)


def add(name, got, exp, ok):
    checks.append((name, got, exp, ok))


# ------------------------------------------------------------------ 구조
h = io.open(HTML, encoding="utf-8").read()
r = PdfReader(PDF)
nd = r.named_destinations
idx = {id(p.indirect_reference.get_object()): n + 1
       for n, p in enumerate(r.pages)}

ids = re.findall(r'<section class="page[^"]*" id="([^"]+)"', h)
n_tabs = len(re.findall(r'<a class="[^"]*" href="#', h.split("</nav>")[0])) or 10

links = broken = 0
reach = set()
norail = []
for n, pg in enumerate(r.pages, 1):
    rail = 0
    for a in pg.get("/Annots") or []:
        o = a.get_object()
        d = o.get("/Dest")
        if d is None:
            broken += 1
            continue
        links += 1
        try:
            reach.add(idx[id(nd[d]["/Page"].get_object())])
        except Exception:
            broken += 1
        if float(o["/Rect"][0]) < 60:
            rail += 1
    if rail != n_tabs:
        norail.append((n, rail))

dead = sorted({a for a in re.findall(r'href="#([^"]*)"', h)
               if a not in set(ids)})
tabbad = [m.group(1) for m in
          re.finditer(r'<section class="page[^"]*" id="([^"]+)".*?</nav>',
                      h, re.S)
          if len(re.findall(r'<a class="on"', m.group(0))) != 1
          and m.group(1) != "cover"]
# SVG 경로 데이터에 H2048 같은 좌표가 있어 연도로 오인된다. 먼저 걷어낸다.
prose = re.sub(r"<svg.*?</svg>", "", h, flags=re.S)
prose = re.sub(r"https?://" + chr(92) + "S+", "", prose)
months = Counter(re.findall(MONTHS, prose))
years = re.findall(r"\b(?:19|20)\d{2}\b", prose)
korean = re.findall(r"[가-힣]", h)
nbytes = os.path.getsize(PDF)

add("페이지 수", len(r.pages), len(ids), len(r.pages) == len(ids))
add("용량 (MB)", round(nbytes / 1_000_000, 2), "< 20", nbytes < LIMIT)
# 여유는 참고값이다. 2026-09-22 에 "일단 올려 보고 막히면 줄인다"로
# 결정했다. v8 은 19.23MB 로 통과한 전례가 있다.
add("여유 (참고)", "%.1f%%" % (100 * (LIMIT - nbytes) / LIMIT), "-", True)
add("목적지", len(nd), len(ids) - 1, len(nd) == len(ids) - 1)
add("링크 주석", links, "> 0", links > 0)
add("끊어진 링크", broken, 0, broken == 0)
add("목적지 없는 앵커", len(dead), 0, not dead)
# 페이지 id 를 다른 요소(SVG 그라데이션 등)가 같이 쓰면 Chrome 이 명명
# 목적지를 문서에서 먼저 나온 쪽에 건다. 링크는 살아 있고 목적지도 있어서
# 위 두 항목은 통과한다 -- h1~h5 가 전부 1페이지로 가던 사례(2026-09-23).
_all_ids = Counter(re.findall(r'\bid="([^"]+)"', h))
clash = sorted(k for k in ids if _all_ids[k] > 1)
add("다른 요소와 겹친 페이지 id", len(clash), 0, not clash)
# url(#x) 는 문서의 첫 정의로 풀린다. 같은 id 에 정의가 둘 이상이면 뒤쪽
# 표가 앞 표의 좌표를 빌려 쓴다 -- 시간표 월~수 열의 가로 괘선이 통째로
# 투명했던 사례(2026-09-23). 같은 id 가 같은 정의로 반복되는 것은 무해하다.
_defs = {}
for m in re.finditer(r'<(linearGradient|radialGradient|pattern) id="([^"]+)"'
                     r'.*?</\1>', h, re.S):
    _defs.setdefault(m.group(2), set()).add(m.group(0))
redef = sorted(k for k, v in _defs.items() if len(v) > 1)
add("정의가 여럿인 SVG id", len(redef), 0, not redef)
add("도달 불가 페이지", len(set(range(2, len(r.pages) + 1)) - reach), 0,
    not (set(range(2, len(r.pages) + 1)) - reach))
add("탭 %d개가 아닌 페이지" % n_tabs, len(norail), 0, not norail)
add("탭 하이라이트 오류", len(tabbad), 0, not tabbad)
add("HTML 속 월 이름", sum(months.values()), 0, not months)
add("HTML 속 연도", len(years), 0, not years)
add("HTML 속 한글", len(korean), 0, not korean)
# 문서 제목 메타. 뷰어 탭·파일 속성·GoodNotes 가져오기 이름에 뜬다.
# 상품 1 의 "ADHD & Wellness Planner" 가 그대로 박혀 있었다(2026-09-24).
_title = str((r.metadata or {}).get("/Title", ""))
add("문서 제목에 Student", _title or "(없음)", "Student",
    "Student" in _title and "Wellness" not in _title)
# 북마크(개요). 뷰어 사이드바의 목차다. 0개였다(2026-09-24). 개수만 보지
# 말고 목적지까지 본다 -- 맨 위 항목은 탭 순서대로 각 탭의 목차 페이지를,
# 모든 항목은 실제 페이지를 가리켜야 한다.
def _walk(items, depth=0):
    for it in items:
        if isinstance(it, list):
            yield from _walk(it, depth + 1)
        else:
            yield it, depth
_ol = list(_walk(r.outline))
_bad_ol = []
for it, dep in _ol:
    try:
        r.get_destination_page_number(it)
    except Exception:
        _bad_ol.append(it.title)
_tabs = re.findall(r'<a class="[^"]*" href="#([^"]+)"',
                   h.split("</nav>")[0])
_top = [ids[r.get_destination_page_number(it)]
        for it, dep in _ol if dep == 0 and it.title not in _bad_ol]
add("북마크 수", len(_ol), "> 0", len(_ol) > 0)
add("북마크 맨 위 = 탭 순서", "%d/%d" % (sum(a == b for a, b in
    zip(_top, _tabs)), len(_tabs)), "전부", _top == _tabs)
add("목적지가 없는 북마크", len(_bad_ol), 0, not _bad_ol)
# "Term 3" 북마크는 머리에 Term 3 이 적힌 페이지로 가야 한다. 학기당 장수를
# 바꾸면 통번호 계산이 어긋나기 쉽다.
_sec = dict(re.findall(r'<section class="page[^"]*" id="([^"]+)"(.*?)</section>',
                       h, re.S))
_term_bad = []
for it, dep in _ol:
    m = re.fullmatch(r"Term (\d+)", it.title)
    if m and it.title not in _bad_ol:
        pid = ids[r.get_destination_page_number(it)]
        if not re.search(r">\s*Term %s\s*<" % m.group(1), _sec[pid]):
            _term_bad.append("%s->%s" % (it.title, pid))
add("학기 북마크가 딴 학기로", len(_term_bad), 0, not _term_bad)
# .row 는 기본이 flex:1 이다(build_planner). 늘어나도 채울 필기면이 없는
# 행(입력칸만 든 행)이 flex:none 이 아니면 남는 높이를 삼켜 구멍이 된다 --
# focus-session 의 Start/Stop 아래 222pt 공백(2026-09-24).
_hole = []
for pid, body in _sec.items():
    for m in re.finditer(r'<div class="row" style="([^"]*)">(.*?)</div></div></div>',
                         body, re.S):
        if "flex:none" not in m.group(1) and 'class="lines"' not in m.group(2):
            _hole.append(pid)
add("필기면 없이 늘어나는 행", len(_hole), 0, not _hole)
# 학기 개요의 Week N 행은 그 학기 N주 페이지로 가야 한다. 링크가 없어서
# 16주 표를 보고도 해당 주로 가려면 목차로 돌아가야 했다(2026-09-24).
_wk_bad = []
for pid, body in _sec.items():
    m = re.fullmatch(r"t(\d+)", pid)
    if not m:
        continue
    t = int(m.group(1))
    want = ["w%d" % ((t - 1) * 16 + w) for w in range(1, 17)]
    got = re.findall(r'<a href="#(w\d+)"[^>]*>Week \d+', body)
    if got != want:
        _wk_bad.append(pid)
add("학기 개요 -> 주간 링크 틀림", len(_wk_bad), 0, not _wk_bad)
# 높이를 고정한 필기면을 담은 카드·행이 flex:1 이면, 카드는 늘어나고 면은
# 그대로라 면 아래에 빈 띠가 생기고 다음 카드가 밀린다 -- 위클리의 Reading
# 과 "One thing I will not drop" 사이가 규정 간격보다 벌어졌다(2026-09-24).
# 가로 .row 안의 카드는 뺀다 -- 거기서 flex 는 폭이다(아래 항목).
_row_re = r'<div class="row" style="[^"]*">.*?</div></div></div>'
_outside = re.sub(_row_re, "", h, flags=re.S)
_stretch = re.findall(r'<div class="card" style="flex:1[^"]*">'
                      r'(?:<div class="label">[^<]*</div>)?'
                      r'<div class="lines" style="flex:none', _outside)
_stretch += re.findall(r'<div class="row" style="flex:1[;"]', h)
add("고정한 면을 담고 늘어나는 카드", len(_stretch), 0, not _stretch)
# 가로 행 안의 카드가 flex:none 이면 폭이 글자만큼 쪼그라든다. 코넬 노트의
# Cue/Notes 가 가는 기둥이 됐다(2026-09-24, LINES.md 1-3 함정 2 재발).
_narrow = [pid for pid, body in _sec.items()
           for m in re.finditer(_row_re, body, re.S)
           if re.search(r'<div class="card" style="flex:none', m.group(0))]
add("가로 행 안에서 폭이 줄어든 카드", len(_narrow), 0, not _narrow)
# 날짜 없는 플래너인데 날짜 적는 칸이 한 곳도 없었다(2026-09-24). 데일리는
# DATE, 위클리는 WEEK OF 칸이 머리에 있어야 한다.
_nodate = [pid for pid, body in _sec.items()
           if re.fullmatch(r"[dw]\d+", pid)
           and not re.search(r'<div class="datebox"><span>%s</span>'
                             % ("DATE" if pid[0] == "d" else "WEEK OF"), body)]
add("날짜 칸 없는 데일리·위클리", len(_nodate), 0, not _nodate)


def wide_label_cols(html):
    """짧은 것을 적거나 미리 인쇄된 라벨뿐인 열이 넓은 표. 기본 T4 의
    첫 열(과제명용 226pt)을 물려받아, 학기 개요의 WEEK 열과 Mood 의 DAY
    열이 가장 넓고 비어 보였다(2026-09-24 지적 후 전수 검수)."""
    bad = set()
    for m in re.finditer(r'<section class="page[^"]*" id="([^"]+)"(.*?)</section>',
                         html, re.S):
        for t in re.finditer(r'<table class="tb [^"]+">(.*?)</table>',
                             m.group(2), re.S):
            rows = re.findall(r"<tr>(.*?)</tr>", t.group(1), re.S)
            head = re.findall(r'<td style="width:([0-9.]+)pt">([^<]*)</td>',
                              rows[0])
            if not head:
                continue
            first = [re.sub(r"<[^>]+>|&rsaquo;", "",
                            re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)[0]).strip()
                     for r in rows[1:]]
            w, name = float(head[0][0]), head[0][1]
            if w > 110 and (name in ("DAY", "WEEK", "TERM") or all(first)):
                bad.add(re.sub(r"\d+$", "#", m.group(1)))
    return sorted(bad)


# 같은 곳을 가리키는 이름은 어디서나 같아야 한다 -- 레일 탭 / 목차 목록 /
# 탭 페이지 제목. 레일은 WEEK·DAY, 목차는 Weeks·Days 였다(2026-09-24 지적).
_rail = re.findall(r'<a class="[^"]*" href="#([^"]+)"[^>]*>(.*?)</a>',
                   _sec["index"].split("</nav>")[0], re.S)
_list = dict(re.findall(r'<a class="crow" href="#([^"]+)">.*?'
                        r'<div class="cn">([^<]+)<',
                        _sec["index"].split("</nav>")[1], re.S))
_name_bad = []
for k, t in _rail:
    t = re.sub(r"<[^>]+>", "", t).strip().lower()
    title = re.search(r"<h1>(.*?)</h1>", _sec[k]).group(1).strip().lower()
    li = _list.get(k, t).strip().lower()
    # notes 는 v0.6 까지 목차 없이 바로 내용 페이지("Blank space")였다
    if k == "notes" and title == "blank space":
        continue
    if k != "index" and not (t == li == title):
        _name_bad.append("%s: %s/%s/%s" % (k, t, li, title))
add("탭·목차·제목 이름 불일치", len(_name_bad), 0, not _name_bad)
# 부제 문장부호: 완전한 문장은 마침표, 조각은 없음(영어 UI 문구 관례,
# 2026-09-24 정함). 문장인지는 기계로 못 가리므로 확실한 경우만 잰다 --
# 문장이 둘 이상인데("A. B") 끝에 마침표가 없으면 틀린 것이다.
_subs = set(re.findall(r'<div class="sub">([^<]*)</div>', h))
_punct = sorted(s_ for s_ in _subs
                if ". " in s_ and not s_.rstrip().endswith((".", "?", "!")))
add("문장 여럿인데 마침표 없는 부제", len(_punct), 0, not _punct)

# 표 점선 양 끝 페이드. v0.2 에서 GoodNotes 속도 때문에 그라데이션을 빼며
# 페이드도 사라졌다 -- 사용자가 살리라고 했다(2026-09-24). 그라데이션
# (v0.1) 이든 끝 점별 옅은 단색(v0.3~, stroke-opacity) 이든 있어야 한다.
_tables = re.findall(r'<svg class="rules" viewBox=.*?</svg>', h, re.S)
_nofade = [t for t in _tables
           if "url(#" not in t and "stroke-opacity" not in t]
add("양 끝 페이드 없는 표", len(_nofade), 0, not _nofade)
# 세로 구분선도 위아래 끝이 흐려야 한다 (student-v0.6~, 사용자 지적 2026-09-24:
# 가로선만 흐리고 세로선은 끝까지 같은 진하기였다). 세로선이 있는 표에서
# 옅은 세로 점(stroke-opacity 를 가진 V 경로)이 없으면 실패. v0.1 의
# 그라데이션 판도 세로는 흐리지 않았으므로 v0.5 이하는 여기서 걸린다.
_v_nofade = [t for t in _tables
             if re.search(r'd="M[0-9.]+ [0-9.]+V', t)
             and not re.search(r'stroke-opacity="[0-9.]+"[^>]*d="M[0-9.]+ [0-9.]+V', t)]
add("세로선 끝 페이드 없는 표", len(_v_nofade), 0, not _v_nofade)
# 칩 그림자와 목차 색 점. v0.2 에서 속도 때문에 헤어라인·단색으로 바꿨다가
# 사용자가 살리라고 했다(2026-09-24). CSS(v0.1) 든 구운 PNG(v0.4~) 든 있어야
# 한다. 칩 묶음마다 box-shadow 가 있거나, 묶음 그림자 이미지가 하나 있어야 한다.
_chips_flat = [pid for pid, body in _sec.items()
               if 'style="display:flex;align-items:center;justify-content:center;'
                  'height:19pt' in body
               and "box-shadow:0 1pt 5pt" not in body
               and "app_chipgrid_" not in body]
add("그림자 없는 칩", len(_chips_flat), 0, not _chips_flat)
_orbs = re.findall(r'<div class="orb" style="background:([^"]*)"', _sec["index"])
_orb_flat = [o for o in _orbs if "gradient" not in o and "url(" not in o]
add("단색으로 납작해진 목차 색 점", len(_orb_flat), 0, not _orb_flat)

# 표지 카드는 리스팅 대표 이미지다 -- 적힌 것이 실제와 같아야 한다.
#  (a) 카드의 이름은 목차·페이지 제목·북마크 어딘가에 쓰이는 이름이어야 한다
#  (b) Assignment tracker 설명의 칸 이름은 실제 표 머리에 있어야 한다.
#      "due, started, handed in" 이었는데 STARTED 칸은 없었다(2026-09-24)
_cov = re.findall(r'<div class="cn">([^<]+)<div class="cd">([^<]+)</div>',
                  _sec.get("cover", ""))
_names = set(re.findall(r"<h1>([^<]+)</h1>", h)) | set(
    re.findall(r'<div style="font-size:10.5pt;font-weight:700">([^<]+)</div>', h))
_names |= set(re.findall(r'<div class="label">([^<]+)</div>', h))
_cov_bad = [n for n, d in _cov if n.strip() not in _names]
_at = [d for n, d in _cov if n.strip() == "Assignment tracker"]
_at_head = re.findall(r'<td style="width:[0-9.]+pt">([A-Z ]+)</td>', _sec.get("a1", ""))
if _at and _at_head:
    _cov_bad += ["Assignment tracker: " + w for w in re.findall(r"[a-z]+", _at[0])
                 if w in ("due", "started", "handed", "done", "class")
                 and not any(w.upper() in x or (w == "handed" and "DONE" in x)
                             for x in _at_head)]
add("표지 카드와 실제가 다름", len(_cov_bad), 0, not _cov_bad)
if _cov_bad:
    print("   표지:", _cov_bad)

_wide = wide_label_cols(h)
add("짧은 내용 열이 넓은 표", len(_wide), 0, not _wide)
# 행이 딱 떨어지게 끝나는가 (LINES.md 1-3 절). 필기면 높이가 flex 로
# 정해지면 나머지(0~22pt)만큼 마지막 괘선이 바닥 위에 애매하게 뜬다.
# 높이는 24pt 배수로 고정되어야 하고, 맨 아래 괘선은 그리지 않는다.
# 표는 면이 곧 카드라 가장자리가 표를 닫는다 -- 가장자리에 겹친 마감선은
# 점선 테두리처럼 보였다(2026-09-24 지적).
_lh = re.findall(r'class="lines" style="([^"]*)"', h)
_off = [st for st in _lh
        if not re.search(r"height:([0-9.]+)pt", st)
        or float(re.search(r"height:([0-9.]+)pt", st).group(1)) % 24]
add("24pt 배수가 아닌 필기면", len(_off), 0, not _off)
_close = len(re.findall(r'<path stroke="[^"]*" d="M[0-9.]+ [0-9.]+H[0-9.]+"/></svg>', h))
add("표 가장자리의 마감선", _close, 0, not _close)


# ------------------------------------------------------- 링크·라벨 (H)
# 인수인계 H 항목 (2026-09-24). 셋 다 "링크 검사는 통과인데 눌러 보면
# 이상한" 종류다 -- CLAUDE.md "링크 검사는 있는 링크가 유효한가로 끝내지 마라".

def body_links(pg):
    """레일(x<60) 을 뺀 본문 링크 주석의 목적지 페이지 번호들."""
    out = []
    for a in pg.get("/Annots") or []:
        o = a.get_object()
        d = o.get("/Dest")
        if d is None or float(o["/Rect"][0]) < 60:
            continue
        try:
            out.append(idx[id(nd[d]["/Page"].get_object())])
        except Exception:
            pass
    return out


# H-1. 눌러도 제자리인 링크. 목차 네 줄이 전부 href="#index" 라 목차에서
# 목차로 갔다(2026-09-23). 목적지가 유효해서 링크 검사는 통과했다.
# 레일의 현재 탭은 원래 제자리라 뺀다.
_self = [ids[n - 1] for n, pg in enumerate(r.pages, 1) if n in body_links(pg)]
add("눌러도 제자리인 링크", len(_self), 0, not _self)

# H-3. 링크처럼 생긴 것은 링크여야 한다.
#  (a) HTML 본문의 <a href> 수 == PDF 본문 링크 주석 수. Chrome 은 목적지
#      없는 앵커를 조용히 버린다 -- 버려지면 여기서 수가 어긋난다
#  (b) › 표시와 칩이 <a> 밖에 있으면 눌리는 척만 하는 것이다
_n_bad, _fake = [], []
for n, pg in enumerate(r.pages, 1):
    body = _sec[ids[n - 1]].split("</nav>", 1)[-1]
    want = len(re.findall(r'<a [^>]*href="#', body))
    got = len(body_links(pg))
    if want != got:
        _n_bad.append("%s %d/%d" % (ids[n - 1], got, want))
    outside = re.sub(r"<a [^>]*>.*?</a>", "", body, flags=re.S)
    if "&rsaquo;" in outside or "justify-content:center;height:19pt" in outside:
        _fake.append(ids[n - 1])
add("HTML 링크 수 != PDF 링크 수", len(_n_bad), 0, not _n_bad)
# 최종 검수(2026-09-24)에서 나온 것:
#  · 표지 카드 줄이 목차 줄(<a class="crow">)과 같은 모양인데 <div> 라 안 눌렸다
#  · Weeks·Days 목차의 라벨이 비어 색 막대만 떠 있었다(card() 는 막았는데
#    chip_card() 가 다시 밟음)
#  · 라벨·열 머리 끝 마침표는 규칙 위반(부제만 문장이면 마침표)
_dead_rows = [pid for pid, body in _sec.items() if '<div class="crow">' in body]
add("눌리지 않는 목록 줄 (crow)", len(_dead_rows), 0, not _dead_rows)
_empty_lab = [pid for pid, body in _sec.items()
              if re.search(r'<div class="label">\s*</div>', body)]
add("빈 라벨 (색 막대만)", len(_empty_lab), 0, not _empty_lab)
_dot_lab = sorted(set(t for t in re.findall(
    r'<div class="label">([^<]+)</div>|<td style="width:[0-9.]+pt">([^<]+)</td>', h)
    for t in t if t.strip().endswith(".")))
add("마침표로 끝나는 라벨·열 머리", len(_dot_lab), 0, not _dot_lab)
add("링크처럼 생겼는데 링크 아님", len(_fake), 0, not _fake)


# H-2. 라벨 아래에 쓸 자리가 있는가. Syllabus 맨 아래 "Anything else" 는
# 라벨만 남고 면이 페이지 밖으로 밀렸다(2026-09-23). 선 검사기의 "넘침"이
# 잡았지만 학생용 검사기에는 없었다. 실제 배치를 헤드리스 Chrome 으로 잰다:
# 라벨 바로 뒤 요소가 없거나, 18pt 미만이거나, 페이지 아래로 나가면 실패.
# 18pt: 칩 한 줄(19pt)은 정상이다. 24pt 로 두었더니 칩 줄 7곳을 잘못 잡았다.
LABEL_JS = """
const bad = [];
document.querySelectorAll('section.page').forEach(pg => {
  const pb = pg.getBoundingClientRect().bottom;
  pg.querySelectorAll('.label').forEach(L => {
    const nx = L.nextElementSibling;
    if (!nx) { bad.push(pg.id + ':' + L.textContent + ':none'); return; }
    const r = nx.getBoundingClientRect();
    if (r.height * 0.75 < 18) bad.push(pg.id + ':' + L.textContent + ':h' + Math.round(r.height * 0.75));
    else if (r.bottom > pb + 0.5) bad.push(pg.id + ':' + L.textContent + ':off');
  });
});
document.body.setAttribute('data-probe', JSON.stringify(bad));
"""


def label_probe():
    import json, subprocess, tempfile
    chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    tmp = os.path.join(os.path.dirname(HTML), "_label_probe.html")
    io.open(tmp, "w", encoding="utf-8").write(
        h.replace("</body>", "<script>%s</script></body>" % LABEL_JS))
    try:
        out = subprocess.run(
            [chrome, "--headless=new", "--disable-gpu",
             "--user-data-dir=" + os.path.join(tempfile.gettempdir(),
                                              "verify-label-profile"),
             "--virtual-time-budget=25000", "--dump-dom",
             "file:///" + tmp.replace(chr(92), "/")],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
    finally:
        os.remove(tmp)
    m = re.search(r'data-probe="([^"]*)"', out.stdout or "")
    if not m:
        return ["(측정 실패)"]
    return json.loads(m.group(1).replace("&quot;", '"').replace("&amp;", "&"))


_lab = label_probe()

# 필기칸 괘선 양 끝 페이드 (student-v0.6~). 표는 흐려지는데 바로 아래 필기칸은
# 끝까지 같은 진하기라 p.17 에서 둘이 달라 보였다(2026-09-24 지적).
_lines_svg = re.findall(r'<svg class="rules rows"[^>]*>(.*?)</svg>', h, re.S)
_lines_nofade = [x for x in _lines_svg if x.strip() and "stroke-opacity" not in x]
add("양 끝 페이드 없는 필기칸", len(_lines_nofade), 0, not _lines_nofade)


def pill_contrast():
    """밝은 페이지의 현재 탭 알약이 눈에 보이는가. 알약 안(글자 없는 왼쪽
    띠)이 바로 위아래 레일 배경보다 얼마나 밝은지. 옆 탭과 비교하면 레일
    배경이 위아래로 색이 달라 흔들렸다. v0.4 = 1.2~2.7 (안 보임),
    흰 알약 시안 = 12.5~22, 사용자가 고른 L2 = 4.9~7.6 (STUDY 구간이 밝아 낮다). 기준 4.
    페이지 종류마다 첫 장만 잰다."""
    seen, bad = set(), []
    for n, pid in enumerate(ids):
        kind = re.sub(r"\d+$", "#", pid)
        if kind in seen or pid in ("cover", "index"):
            continue
        seen.add(kind)
        pg = r.pages[n]
        H = float(pg.mediabox.height)
        rects = sorted([[float(x) for x in a.get_object()["/Rect"]]
                        for a in pg.get("/Annots") or []
                        if float(a.get_object()["/Rect"][0]) < 60],
                       key=lambda q: -q[3])
        nav = _sec[pid].split("</nav>")[0]
        tabs = re.findall(r'<a class="([^"]*)" href="#', nav)
        on = [i for i, t in enumerate(tabs) if "on" in t.split()]
        if not on or len(rects) != len(tabs):
            bad.append(pid + ":?")
            continue
        x0, y0, x1, y1 = rects[on[0]]
        S = 3
        a = gray(n, S)
        xs = slice(int((x0 + 4) * S), int((x0 + 7) * S))
        inside = a[int((H - y1 + 8) * S):int((H - y0 - 8) * S), xs].mean()
        out = (a[int((H - y1 - 10) * S):int((H - y1 - 4) * S), xs].mean()
               + a[int((H - y0 + 4) * S):int((H - y0 + 10) * S), xs].mean()) / 2
        if inside - out < 4:
            bad.append("%s:%.1f" % (pid, inside - out))
    return bad
add("쓸 자리 없는 라벨", len(_lab), 0, not _lab)


# ------------------------------------------------------------------ 시각
with open(PDF, "rb") as fh:
    doc = pdfium.PdfDocument(fh.read())


def gray(page, scale):
    return np.asarray(doc[page].render(scale=scale).to_pil().convert("L")
                      ).astype(float)


_pill = pill_contrast()


def dot_pitch():
    """점지 노트의 점 간격이 14pt 인가 -- 상품 1 dot_svg 와 같은 값. 뷰어
    배율 1.5/2/2.7 에서 렌더해 한 줄의 점 중심 간격을 잰다. 상품 1 v8.19 는
    GoodNotes 에서 점이 4배 간격으로 그려졌다(PC 렌더는 정상 -- 그건 A-3 이
    잡는다). 이 검사는 점 간격·크기를 바꾸는 코드 변경을 잡는다.
    돌려주는 것: 문제 목록 (없으면 [])."""
    dots = [i for i, pid in enumerate(ids)
            if re.fullmatch(r"n\d+", pid) and ">Dot grid<" in _sec[pid]]
    if not dots:
        return []
    bad = []
    for z in (1.5, 2.0, 2.7):
        a = gray(dots[0], z)
        H, W = a.shape
        band = a[int(H * .3):int(H * .7), int(W * .3):int(W * .7)]
        bg = np.median(band)
        rows = (band < bg - 8).sum(axis=1)
        y = int(np.argmax(rows))
        row = band[y] < bg - 8
        cs, x = [], 0
        while x < len(row):
            if row[x]:
                e = x
                while e < len(row) and row[e]:
                    e += 1
                cs.append((x + e - 1) / 2.0)
                x = e
            else:
                x += 1
        gaps = np.diff(cs) / z
        if len(gaps) < 5:
            bad.append("%.1f배 점 %d개" % (z, len(cs)))
        elif abs(np.median(gaps) - 14.0) > 0.5 or gaps.max() - gaps.min() > 1.5:
            bad.append("%.1f배 간격 %.2f~%.2fpt" % (z, gaps.min(), gaps.max()))
    return bad


_dots = dot_pitch()
add("점지 점 간격 14pt", len(_dots), 0, not _dots)
if _dots:
    print("   점지:", _dots)
add("안 보이는 현재 탭 표시", len(_pill), 0, not _pill)


def runs(vals, cut):
    out, i = [], 0
    while i < len(vals):
        if vals[i] < cut:
            j = i
            while j < len(vals) and vals[j] < cut:
                j += 1
            out.append((i, j - i))
            i = j
        else:
            i += 1
    return out


def uniq(page, y_lo, y_hi, x0, x1):
    """확대율마다 점 길이와 선 두께가 단일값인지.

    주의: 대역에 세로 구분선이나 면 가장자리가 끼면 3~4px 짜리 가짜
    '선'이 잡힌다. 그래서 가로로 점이 5개 이상 끊겨 있는 줄만 센다.
    이 함정에 두 번 빠졌다.
    """
    bad = []
    for z in ZOOMS:
        a = gray(page, z)
        H = a.shape[0]
        band = a[:, int(x0 * z):int(x1 * z)]
        rm = band.min(axis=1)
        y0, y1 = int(H * y_lo), int(H * y_hi)
        bg = np.median(rm[y0:y1])
        th, dash = [], []
        for st, ln in runs(rm[y0:y1], bg - 3):
            if ln / z >= 2:
                continue
            row = band[y0 + st + ln // 2]
            d = [n for _, n in runs(row, row.max() - 4)]
            if len(d) < 5:          # 점선이 아니라 선/가장자리다
                continue
            th.append(ln)
            dash += d[1:-1]
        if th and (max(th) != min(th)):
            bad.append("%.1f배 두께 %d~%d px" % (z, min(th), max(th)))
        if dash and (max(dash) != min(dash)):
            bad.append("%.1f배 점 길이 %d~%d px" % (z, min(dash), max(dash)))
    return bad


def shadows(page, xs=(150, 300, 450), scale=6):
    """면 아래로 밝기가 회복되는 폭. 그림자가 있으면 15 이상."""
    a = gray(page, scale)
    deps = []
    for x in xs:
        col = a[:, int(x * scale) - 20:int(x * scale) + 20].mean(axis=1)
        for y in range(int(120 * scale), int(775 * scale)):
            if col[y - 1] - col[y] > 8 and col[y - 1] > 234:
                b = y / scale
                v = [col[int((b + t) * scale)] for t in (1, 4, 8, 13)
                     if (b + t) * scale < len(col)]
                if len(v) == 4:
                    deps.append(v[-1] - v[0])
    return max(deps) if deps else 0.0


def dashed_rows(a, scale, x0=120, x1=280):
    """점선인 가로줄의 y 목록. 가로로 5번 이상 끊긴 줄만 센다."""
    band = a[:, int(x0 * scale):int(x1 * scale)]
    rm = band.min(axis=1)
    bg = np.median(rm)
    out = []
    for st, ln in runs(rm, bg - 3):
        if ln / scale >= 2:
            continue
        row = band[st + ln // 2]
        if len([n for _, n in runs(row, row.max() - 4)]) >= 5:
            out.append((st + ln / 2) / scale)
    return out


def lines_fill(page, scale=6):
    """괘선이 면 바닥까지 차 있는가.

    (마지막 줄 ~ 면 바닥) / 줄 간격. 1.0 근처면 정상이고, 2 를 넘으면
    아래가 비었다는 뜻이다. <svg> 가 고유 크기로 누워 면의 반쪽만
    채웠던 사고를 잡는 항목이다.
    """
    a = gray(page, scale)
    rows = dashed_rows(a, scale)
    if len(rows) < 3:
        return None
    groups = [[rows[0]]]
    for y in rows[1:]:
        if y - groups[-1][-1] > 40:
            groups.append([])
        groups[-1].append(y)
    g = max(groups, key=len)
    if len(g) < 3:
        return None
    step = np.median(np.diff(g))
    col = a[:, int(300 * scale) - 40:int(300 * scale) + 40].mean(axis=1)
    y = int(g[-1] * scale)
    while y < len(col) - 1 and not (col[y] - col[y + 1] > 6 and col[y] > 234):
        y += 1
    return (y / scale - g[-1]) / step


uniq_pages = [k for k in ("d1", "syllabus", "timetable") if k in ids]
bad_uniform = []
for k in uniq_pages:
    bad_uniform += ["%s: %s" % (k, b)
                    for b in uniq(ids.index(k), 0.20, 0.95, 120, 280)]
add("점선 균일 (1.5/2/2.5/3배)", len(bad_uniform), 0, not bad_uniform)

panels = {m.group(1) for m in
          re.finditer(r'<section class="page[^"]*" id="([^"]+)"'
                      r'(?:(?!<section).)*?class="(?:field|lines|tbwrap)',
                      h, re.S)}
tpl = [k for k in ids if not re.fullmatch(r"[twdc]\d+", k)
       and k not in ("cover", "index") and k in panels]
weak = [(k, round(shadows(ids.index(k)), 1)) for k in tpl]
weak = [(k, v) for k, v in weak if v < MIN_SHADOW]
add("면 그림자 없는 템플릿", len(weak), 0, not weak)

gap = lines_fill(ids.index("d1")) if "d1" in ids else None
add("괘선 빈 구간 (줄 간격 배수)",
    "-" if gap is None else round(gap, 2), "< 1.6",
    gap is not None and gap < 1.6)

doc.close()

# ------------------------------------------------------------------ 출력
print()
print("  %-28s %14s   %s" % ("항목", "값", "기대"))
print("  " + "-" * 62)
fail = 0
for name, got, exp, ok in checks:
    if not ok:
        fail += 1
    print(("  OK  " if ok else "  실패") + "  %-26s %14s   %s"
          % (name, got, exp))
if dead:
    print("   목적지 없는 앵커:", dead[:8])
if tabbad:
    print("   탭이 잘못된 페이지:", tabbad[:8])
if months:
    print("   월 이름:", dict(months))
if _pill or _lines_nofade:
    print("   탭/괘선:", _pill[:6], len(_lines_nofade))
if _self or _n_bad or _fake or _lab:
    print("   H:", _self[:5], _n_bad[:5], _fake[:5], _lab[:6])
if clash or redef:
    print("   겹친 id:", clash[:10], "정의 여럿:", redef[:10])
if bad_uniform:
    print("   점선 불균일:", bad_uniform[:6])
if weak:
    print("   그림자 약한 템플릿:", weak[:8])
print()
print("실패:", fail)
sys.exit(1 if fail else 0)
