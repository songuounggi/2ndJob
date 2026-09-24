# -*- coding: utf-8 -*-
"""Full structural + content verification of v8.20 (v8.19 + vector_dots)."""
import io, os, re, sys
import pikepdf
from collections import Counter
from pypdf import PdfReader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, 'output', 'planner_v8.20-undated-FINAL.pdf')
HTML = os.path.join(ROOT, 'src', 'planner_v8.20-undated.html')
# 인자로 다른 판을 재볼 수 있다: python scripts/verify_v8_20.py output/x.pdf src/x.html
if len(sys.argv) == 3:
    PDF, HTML = (os.path.join(ROOT, a) for a in sys.argv[1:])

h = io.open(HTML, encoding='utf-8').read()
r = PdfReader(PDF)
nd = r.named_destinations
idx = {id(p.indirect_reference.get_object()): n + 1 for n, p in enumerate(r.pages)}

links = broken = 0
reach = set()
norail = []
for n, pg in enumerate(r.pages, 1):
    rail = 0
    for a in pg.get('/Annots') or []:
        o = a.get_object()
        d = o.get('/Dest')
        if d is None:
            broken += 1
            continue
        links += 1
        try:
            reach.add(idx[id(nd[d]['/Page'].get_object())])
        except Exception:
            broken += 1
        if float(o['/Rect'][0]) < 60:
            rail += 1
    if rail != 10:
        norail.append((n, rail))

ids = set(re.findall(r'id="([^"]+)"', h))
dead = sorted({a for a in re.findall(r'href="#([^"]*)"', h) if a not in ids})
tabbad = [m.group(1) for m in
          re.finditer(r'<section class="page" id="([^"]+)".*?</nav>', h, re.S)
          if len(re.findall(r'<a class="on"', m.group(0))) != 1
          and m.group(1) != 'cover']

MONTHS = (r'\b(January|February|March|April|May|June|July|August|September|'
          r'October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b')
months = Counter(re.findall(MONTHS, h))
# strip URLs first -- the SVG namespace (w3.org/2000/svg) is not a date
years = re.findall(r'\b(?:19|20)\d{2}\b', re.sub(r'https?://\S+', '', h))
korean = re.findall(r'[\uac00-\ud7a3]', h)

# v8.19: GoodNotes 바둑판 렌더링 (2026-09-24). 페이지마다 그라데이션
# 셰이딩(카드 그림자)과 소프트마스크(bloom 반투명)가 5~6개씩 있으면 iPad 가
# 타일을 늦게 채운다. 표지는 하늘 사진 위에 bloom 을 섞으므로 예외다.
def heavy(res, seen):
    sh = sm = 0
    if res is None:
        return 0, 0
    for gs in (res.get('/ExtGState') or {}).values():
        if '/SMask' in gs and gs.SMask != pikepdf.Name('/None'):
            sm += 1
    for p in (res.get('/Pattern') or {}).values():
        if int(p.get('/PatternType', 0)) == 2:
            sh += 1
        if p.get('/Resources') is not None:
            a, b = heavy(p.Resources, seen); sh += a; sm += b
    for v in (res.get('/XObject') or {}).values():
        if v.get('/Subtype') == '/Form' and v.objgen not in seen:
            seen.add(v.objgen)
            a, b = heavy(v.get('/Resources'), seen); sh += a; sm += b
    return sh, sm
# v8.20: 도트 그리드 (2026-09-24). CSS 도트는 이미지 타일 패턴으로 들어가고,
# GoodNotes 가 그 타일을 4배 넓게·흐릿하게 그렸다. 이미지를 담은 타일
# 패턴이 한 장도 없어야 한다.
def img_tiles(res, seen):
    n = 0
    if res is None:
        return 0
    for p in (res.get('/Pattern') or {}).values():
        if int(p.get('/PatternType', 0)) == 1:
            xo = (p.get('/Resources') or {}).get('/XObject') or {}
            n += any(x.get('/Subtype') == '/Image' for x in xo.values())
        n += img_tiles(p.get('/Resources'), seen)
    for v in (res.get('/XObject') or {}).values():
        if v.get('/Subtype') == '/Form' and v.objgen not in seen:
            seen.add(v.objgen)
            n += img_tiles(v.get('/Resources'), seen)
    return n
shade_pages = smask_pages = tile_pages = 0
with pikepdf.open(PDF) as kp:
    for n, pg in enumerate(kp.pages, 1):
        if n == 1:
            continue
        a, b = heavy(pg.Resources, set())
        shade_pages += a > 0
        smask_pages += b > 0
        tile_pages += img_tiles(pg.Resources, set()) > 0

nbytes = os.path.getsize(PDF)
checks = [
    ('pages', len(r.pages), 502),
    ('bytes', nbytes, '< 20,000,000'),
    ('MB (decimal)', round(nbytes / 1_000_000, 2), '< 20'),
    ('destinations', len(nd), 501),
    ('link annots', links, 5893),
    ('broken links', broken, 0),
    ('dead anchors', len(dead), 0),
    ('unreachable (cover excluded)', len(set(range(1, len(r.pages) + 1)) - reach - {1}), 0),
    ('pages without 10 tabs', len(norail), 0),
    ('wrong tab highlight', len(tabbad), 0),
    ('month names in HTML', sum(months.values()), 0),
    ('year numbers in HTML', len(years), 0),
    ('korean chars in HTML', len(korean), 0),
    ('pages w/ gradient shading (cover excl)', shade_pages, 0),
    ('pages w/ soft mask (cover excl)', smask_pages, 0),
    ('pages w/ image tiling pattern', tile_pages, 0),
]
fail = 0
for k, got, exp in checks:
    ok = True
    if isinstance(exp, int):
        ok = got == exp
    elif exp == '< 20':
        ok = got < 20
    elif exp.startswith('<'):
        ok = nbytes < 20_000_000
    if not ok:
        fail += 1
    print(('  OK  ' if ok else '  FAIL') + f'  {k:32} {str(got):>14}   expect {exp}')
if months:
    print('   month names found:', dict(months))
if dead:
    print('   dead anchors:', dead[:8])
if tabbad:
    print('   bad tab pages:', tabbad[:8])
print()
print('FAILURES:', fail)
sys.exit(1 if fail else 0)
