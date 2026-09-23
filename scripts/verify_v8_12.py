# -*- coding: utf-8 -*-
"""Full structural + content verification of the v8 deliverable."""
import io, os, re, sys
from collections import Counter
from pypdf import PdfReader

ROOT = r'C:\Users\ThinkBook\AiProject\2ndJob'
PDF = os.path.join(ROOT, 'output', 'planner_v8.12-undated-FINAL.pdf')
HTML = os.path.join(ROOT, 'src', 'planner_v8.12-undated.html')

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

nbytes = os.path.getsize(PDF)
checks = [
    ('pages', len(r.pages), 514),
    ('bytes', nbytes, '< 20,000,000'),
    ('MB (decimal)', round(nbytes / 1_000_000, 2), '< 20'),
    ('destinations', len(nd), 513),
    ('link annots', links, 6025),
    ('broken links', broken, 0),
    ('dead anchors', len(dead), 0),
    ('unreachable (cover excluded)', len(set(range(1, len(r.pages) + 1)) - reach - {1}), 0),
    ('pages without 10 tabs', len(norail), 0),
    ('wrong tab highlight', len(tabbad), 0),
    ('month names in HTML', sum(months.values()), 0),
    ('year numbers in HTML', len(years), 0),
    ('korean chars in HTML', len(korean), 0),
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
