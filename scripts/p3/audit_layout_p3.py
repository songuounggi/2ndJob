# -*- coding: utf-8 -*-
"""상품 3 플래너 전수 레이아웃 검사 -- 598쪽 전부, 빌드와 같은 JS 를 적용한 뒤 브라우저에서 잰다. Prod 3 방 소유.

    python scripts/p3/audit_layout_p3.py v0.5 2027 mon
    python scripts/p3/audit_layout_p3.py v0.5            # 네 판 전부

사용자가 iPad 에서 하나씩 찾던 결함(표와 겹친 글자, 공휴일과 겹친 날짜, 잘린 줄)을 먼저 찾는다.
  A. 잘림    -- 글자가 들어 있는 요소가 overflow:hidden 조상 밖으로 나간다(보이지 않는 내용)
  B. 넘침    -- 글자 요소의 scrollWidth 가 자기 폭보다 크다(칸 밖으로 삐져나온 글자)
  C. 겹침    -- 서로 다른 두 글자 조각의 상자가 겹친다(같은 줄의 형제 제외 없이 전부)
  D. 발문 침범 -- 본문 요소가 발문(footer) 위쪽 선 아래로 내려간다
  E. 삐져나옴 -- 글자가 자기 칸(부모) 위나 아래로 1/3 이상 나간다
결과는 페이지 번호·페이지 id·요소 글자로 찍는다. 0 이 아니면 종료 코드 1.
"""
import json
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "p3"))
VER = sys.argv[1] if len(sys.argv) > 1 else "v0.5"
EDS = [(sys.argv[2], sys.argv[3])] if len(sys.argv) > 3 else [(y, w) for y in ("2026", "2027") for w in ("mon", "sun")]
sys.argv = [sys.argv[0], "2027", "mon"]
import editions_build as E                      # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

CODE = (ROOT / "scripts" / "p3" / "planner_build.py").read_text(encoding="utf-8")
ROWS_JS = re.search(r'ROWS_JS = r"""(.*?)"""', CODE, re.S).group(1)
FILL_JS = re.search(r'FILL_JS = r"""(.*?)"""', CODE, re.S).group(1)
ROW = int(re.search(r"^ROW = (\d+)", CODE, re.M).group(1))

AUDIT_JS = r"""
() => {
  const out = [];
  const txt = e => (e.innerText || e.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 40);
  const R = e => e.getBoundingClientRect();
  document.querySelectorAll('section.pg').forEach((s, pi) => {
    const add = (k, e, extra) => out.push([pi + 1, s.id, k, txt(e) || e.tagName, extra || '']);
    const ink = s.querySelector('.ink') || s;
    // 글자를 직접 가진 요소(잎)
    const leaves = [...s.querySelectorAll('*')].filter(e => {
      if (e.closest('nav.rail')) return false;
      if (!['block', 'inline', 'inline-block', 'flex', 'inline-flex', 'table-cell', 'list-item'].includes(getComputedStyle(e).display)) return false;
      return [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    });
    // A. 잘림 + B. 넘침
    leaves.forEach(e => {
      const r = R(e); if (!r.width || !r.height) return;
      let a = e.parentElement;
      while (a && a !== s) {
        const cs = getComputedStyle(a);
        if (cs.overflow !== 'visible' || cs.overflowY !== 'visible') {
          const ar = R(a);
          // 줄 상자가 몇 px 나가는 건 글자와 무관하다 -- 글자 높이의 1/3 이상 가려질 때만
          const cut = Math.max(r.bottom - ar.bottom, ar.top - r.top, r.right - ar.right);
          if (cut > r.height / 3) add('A clipped', e, `${Math.round(cut)}px hidden`);
          break;
        }
        a = a.parentElement;
      }
      if (s.id !== 'cover' && e.scrollWidth > e.clientWidth + 1 && getComputedStyle(e).display !== 'inline') add('B overflow', e, `${e.scrollWidth}>${e.clientWidth}`);
      // E. 칸 밖으로 삐져나옴 -- 고정 높이 줄 안에서 글자가 꺾여 이웃 줄에 붙었다(v0.6 13쪽 Password hints)
      const pr = R(e.parentElement);
      if (s.id !== 'cover' && getComputedStyle(e.parentElement).display !== 'inline' && (pr.top - r.top > r.height / 3 || r.bottom - pr.bottom > r.height / 3)) add('E spills out', e, `${Math.round(Math.max(pr.top - r.top, r.bottom - pr.bottom))}px`);
    });
    // C. 겹침 -- 글자 조각 상자(텍스트 노드 범위)끼리
    const boxes = [];
    leaves.forEach(e => [...e.childNodes].forEach(n => {
      if (n.nodeType !== 3 || !n.textContent.trim()) return;
      const rg = document.createRange(); rg.selectNodeContents(n);
      [...rg.getClientRects()].forEach(r => { if (r.width > 1 && r.height > 1) boxes.push([r, e]); });
    }));
    for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
      const [a, ea] = boxes[i], [b, eb] = boxes[j];
      if (ea === eb || ea.contains(eb) || eb.contains(ea)) continue;
      const ox = Math.min(a.right, b.right) - Math.max(a.left, b.left), oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
      if (s.id !== 'cover' && ox > 1.5 && oy > Math.min(a.height, b.height) / 3) add('C overlap', ea, `with "${txt(eb)}"`);   // 표지는 겹치게 디자인됐다
    }
    // D. 발문 침범
    const f = s.querySelector('footer');
    if (f) {
      const ft = R(f).top;
      leaves.filter(e => !f.contains(e)).forEach(e => {      // 글자만 -- 잘려 안 보이는 빈 줄 상자는 A 가 본다
        const r = R(e); if (r.height && r.bottom - ft > r.height / 3) add('D into footer', e, `${Math.round(r.bottom - ft)}px`);
      });
    }
  });
  return out;
}
"""

total = 0
with sync_playwright() as p:
    br = p.chromium.launch(channel="chrome")
    for y, w in EDS:
        src = ROOT / "src" / "prod3" / "planner" / VER / f"ADHD-Year-Planner-{y}-{w}.html"
        pg = br.new_context(user_agent=E.STATIC_FONT_UA, viewport={"width": 768, "height": 1024}).new_page()
        pg.emulate_media(media="print")
        pg.goto(src.as_uri(), timeout=300000)
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(800)
        pg.evaluate(ROWS_JS, ROW)
        pg.evaluate(FILL_JS)
        res = pg.evaluate(AUDIT_JS)
        # 같은 결함이 반복 페이지마다 나오면 묶어서 보여 준다
        groups = {}
        for n, pid, k, t, x in res:
            key = (k, re.sub(r"\d+(-\d+)?$", "#", pid), re.sub(r"\d+", "#", t))
            groups.setdefault(key, []).append((n, pid, t, x))
        print(f"== {VER} {y}-{w}: {len(res)} findings, {len(groups)} kinds")
        for (k, pid, t), items in sorted(groups.items(), key=lambda kv: kv[1][0][0]):
            n, pid0, t0, x = items[0]
            more = f" (+{len(items) - 1} more pages like it)" if len(items) > 1 else ""
            print(f"  p{n:<4} {pid0:<12} {k:<14} {t0!r:<44} {x}{more}")
        total += len(res)
        pg.close()
    br.close()
print(f"\nTOTAL {total}")
sys.exit(1 if total else 0)
