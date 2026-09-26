# -*- coding: utf-8 -*-
"""상품 3 줄 간격 전수 검사 -- 한 페이지 안의 "쓰는 줄" 높이가 모두 같은가. Prod 3 방 소유.

    python scripts/p3/audit_pitch_p3.py v0.10 2026 mon

2026-09-26 사용자: "줄 간격 한번 맞췄는데도 이 모양이네, 제대로 검수한 거 맞아?" -- 그때까지 검사는
찾은 결함을 하나씩 뒤따라 만든 것이라, 페이지 전체의 줄 간격을 한 번에 묻는 검사가 없었다.

쓰는 줄 = 괘선(.ln), 상품 1 줄 묶음(.lines>div), 입력 행(밑줄 칸이 든 행), 문구 붙은 줄(.tr3),
         기록표 행(.trk, 체크 격자 1~31일 제외)
빼는 것  = 체크 격자(1~31일 칸 -- 간격을 건드리지 말라고 확정), 실험 줄(.xr, 누르는 영역 41px), 칸 밖에 잘려 안 보이는 줄,
           이름 붙은 행 5장(Gratitude·Meals·Focus session·Stuck on deciding·Goals -- 넓은 게 의도, 사용자 확정), 일간 에너지 칸(24px, 사용자 확정)
기준 34px. 페이지마다 34 가 아닌 줄의 종류·높이·개수를 찍는다.
"""
import collections
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "p3"))
VER, Y, WS = (sys.argv[1:4] + ["v0.10", "2026", "mon"][len(sys.argv[1:4]):])
sys.argv = [sys.argv[0], "2027", "mon"]
import editions_build as E                        # noqa: E402
from playwright.sync_api import sync_playwright   # noqa: E402

CODE = (ROOT / "scripts" / "p3" / "planner_build.py").read_text(encoding="utf-8")
J = {k: re.search(k + r' = r"""(.*?)"""', CODE, re.S).group(1) for k in ("ROWS_JS", "GAP_JS", "TRK_FILL_JS", "FILL_JS")}
PITCH_JS = r"""
() => {
  const out = [];
  const vis = (s, e) => { const r = e.getBoundingClientRect(); if (!r.width || !r.height) return null; let a = e.parentElement;
    while (a && a !== s) { const cs = getComputedStyle(a); if (cs.overflow !== 'visible' && r.bottom > a.getBoundingClientRect().bottom + 1) return null; a = a.parentElement; }
    return r; };
  document.querySelectorAll('section.pg').forEach((s, i) => {
    const add = (kind, e) => { const r = vis(s, e); if (r) out.push([i + 1, s.id, kind, Math.round(r.height)]); };
    s.querySelectorAll('.ln:not(.fl)').forEach(e => { if (!e.closest('.lane')) add('rule', e); });
    s.querySelectorAll('.p1 .lines > div').forEach(e => add('lines', e));
    // 이름 붙은 입력 행(MON..SUN, 1..6, A/B/C, SMART)은 넓은 게 의도 -- 사용자 확정(2026-09-26) 예외. 빈 입력 행만 잰다
    s.querySelectorAll('.p1 div:has(> .field)').forEach(e => { if (getComputedStyle(e).display === 'flex' && !e.innerText.trim() && !['meals','goals','gratitude','session','paralysis'].includes(s.id)) add('input', e); });
    s.querySelectorAll('.tr3').forEach(e => add('labeled', e));
    s.querySelectorAll('.p1 table.trk').forEach(t => { if (t.rows[0].cells.length >= 29) return;
      [...t.rows].slice(1).forEach(r => add('table', r)); });
  });
  return out;
}
"""
src = ROOT / "src" / "prod3" / "planner" / VER / f"ADHD-Year-Planner-{Y}-{WS}.html"
with sync_playwright() as p:
    br = p.chromium.launch(channel="chrome")
    pg = br.new_context(user_agent=E.STATIC_FONT_UA, viewport={"width": 768, "height": 1024}).new_page()
    pg.emulate_media(media="print")
    pg.goto(src.as_uri(), timeout=300000)
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(600)
    for k, arg in (("ROWS_JS", 34), ("GAP_JS", 16), ("TRK_FILL_JS", None), ("FILL_JS", None)):
        pg.evaluate(J[k], arg) if arg is not None else pg.evaluate(J[k])
    rows = pg.evaluate(PITCH_JS)
    br.close()

pages = collections.defaultdict(collections.Counter)
names = {}
for n, pid, kind, h in rows:
    if abs(h - 34) > 1:
        pages[n][(kind, h)] += 1
        names[n] = pid
kinds = collections.defaultdict(list)
for n, c in pages.items():
    key = re.sub(r"\d+(-\d+)?$", "#", names[n])
    kinds[(key, tuple(sorted(c)))].append(n)
print(f"{VER} {Y}-{WS}: pages with writing rows not 34px = {len(pages)}")
for (key, sig), ns in sorted(kinds.items(), key=lambda kv: kv[1][0]):
    desc = ", ".join(f"{k} {h}px x{pages[ns[0]][(k, h)]}" for k, h in sig)
    print(f"  p{ns[0]:<4} {key:<12} {desc}" + (f"   (+{len(ns) - 1} pages like it)" if len(ns) > 1 else ""))
sys.exit(1 if pages else 0)
