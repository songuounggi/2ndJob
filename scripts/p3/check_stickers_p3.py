# -*- coding: utf-8 -*-
"""상품 3 스티커 검사 -- 판정 아이콘(✓ ~ ✗)이 스티커 가운데에 있는가, 종이색이 플래너와 같은가. Prod 3 방 소유.

    python scripts/p3/check_stickers_p3.py [stickers_p3.py 경로]

2026-09-27 사용자: "확인 표시와 X 표시가 묘하게 좌측 상단으로 쏠렸다." 80칸 viewBox 에서 ✓ 는 왼쪽 6·위 8,
✗ 는 6·6, ~ 는 4·4 벗어나 있었다(draft-v0.5). 브라우저 getBBox 로 실제 도형의 가운데를 잰다.
"""
import pathlib
import re
import sys

from playwright.sync_api import sync_playwright
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))   # scripts/ -- chrome_auto
from chrome_auto import launch  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "scripts" / "p3" / "stickers_p3.py"
text = SRC.read_text(encoding="utf-8")
MUST = ("check", "tilde", "cross")          # 판정 스티커 -- 가운데여야 한다
TOL = 1.5                                   # 80칸 기준

icons = {k: d for k, d in re.findall(r'"(\w+)": P\("([^"]+)"', text)}
paper = re.search(r'^PAPER, INK[^=]*= "(#[0-9a-fA-F]{6})"', text, re.M)
planner = re.search(r'^PAPER, INK = "(#[0-9a-fA-F]{6})"', (ROOT / "scripts/p3/planner_build.py").read_text(encoding="utf-8"), re.M)
fails = []
with sync_playwright() as p:
    br = launch(p)   # chrome_auto: 새 Chrome 마다 Windows 로그온 실패가 쌓여 계정이 잠겼다(2026-09-28)
    pg = br.new_page()
    for k in MUST:
        if k not in icons:
            fails.append(f"{k}: 아이콘 정의를 못 찾았다")
            continue
        pg.set_content(f'<svg viewBox="0 0 80 80"><path id="p" d="{icons[k]}"/></svg>')
        b = pg.evaluate("() => { const r = document.getElementById('p').getBBox(); return [r.x, r.y, r.width, r.height]; }")
        dx, dy = b[0] + b[2] / 2 - 40, b[1] + b[3] / 2 - 40
        ok = abs(dx) <= TOL and abs(dy) <= TOL
        print(f"  {'OK  ' if ok else 'FAIL'} {k:<6} 가운데에서 x {dx:+.1f}, y {dy:+.1f}")
        if not ok:
            fails.append(f"{k} 가 가운데에서 ({dx:+.1f}, {dy:+.1f}) 벗어났다")
    br.close()
same = paper and planner and paper.group(1).lower() == planner.group(1).lower()
print(f"  {'OK  ' if same else 'FAIL'} 스티커 종이색 {paper and paper.group(1)} = 플래너 {planner and planner.group(1)}")
if not same:
    fails.append("스티커 종이색이 플래너와 다르다")
print(f"\n{'ALL OK' if not fails else 'FAILURES ' + str(len(fails))}")
sys.exit(1 if fails else 0)
