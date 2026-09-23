# -*- coding: utf-8 -*-
"""선의 일관성 검사. 규칙은 LINES.md.

어느 버전에도 쓴다 -- v8, v9-student, 앞으로의 상품 전부.

    python scripts/check_lines.py src/planner_v8-undated.html
    python scripts/check_lines.py src/planner_v9-student.html --gap 22

레이아웃은 레이아웃 엔진에게 묻는다. 렌더 이미지에서 어두운 행을 세는
방식으로 먼저 해봤더니 표 테두리·카드 경계·점자가 섞여 14~119px 이 나왔고
쓸 수 없었다. 여기서는 헤드리스 Chrome 에 HTML 을 띄우고 실제 렌더된
getBoundingClientRect().height 를 읽는다.

실패하면 종료코드 1. 빌드 스크립트에서 이어 붙여 쓸 수 있다.
"""

import argparse
import io
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# 페이지 안에서 실제로 재는 코드. 여기만 고치면 검사 항목이 바뀐다.
PROBE = r"""
const out = {pages:{}, trk:[]};
document.querySelectorAll('section.page').forEach(sec => {
  const rules = [...sec.querySelectorAll('.lines > div')];
  if (rules.length) {
    const hs = rules.map(d => Math.round(d.getBoundingClientRect().height*10)/10);
    out.pages[sec.id] = [...new Set(hs)].sort((a,b) => a-b);
  }
  sec.querySelectorAll('table.trk').forEach((t, i) => {
    const cs = e => getComputedStyle(e);
    const rows = [...t.rows];
    const last = rows[rows.length-1];
    const firstRow = rows[0];
    // 헤더 아래 선은 헤더 칸의 border-bottom 에서 올 수도, 첫 본문 행의
    // border-top 에서 올 수도 있다(border-collapse). 어느 쪽이든 선이
    // 있으면 되고, 결함은 "열마다 유무가 다른 것"이다.
    const body0 = rows[1];
    let per = [];
    if (firstRow && body0) {
      const n = Math.min(firstRow.cells.length, body0.cells.length);
      for (let c = 0; c < n; c++) {
        const hb = parseFloat(cs(firstRow.cells[c]).borderBottomWidth) > 0;
        const bt = parseFloat(cs(body0.cells[c]).borderTopWidth) > 0;
        per.push(hb || bt);
      }
    }
    const uneven = per.length > 1 && new Set(per).size > 1;
    const labelled = firstRow && [...firstRow.cells].some(
      c => c.textContent.trim().length > 0);
    // 바깥 테두리: 마지막 칸 오른쪽 / 마지막 행 아래는 없어야 한다
    const rightCell = firstRow && firstRow.cells[firstRow.cells.length-1];
    const anyRight = [...rows].some(r => {
      const c = r.cells[r.cells.length-1];
      return c && parseFloat(cs(c).borderRightWidth) > 0;
    });
    const anyBottom = last && [...last.cells].some(
      c => parseFloat(cs(c).borderBottomWidth) > 0);
    out.trk.push({page: sec.id, i,
                  labelledHeader: !!labelled,
                  unevenHeaderRule: !!uneven,
                  cols: per,
                  outerRight: !!anyRight,
                  outerBottom: !!anyBottom});
  });
});
document.body.setAttribute('data-probe', JSON.stringify(out));
"""


def measure(src_html):
    """HTML 에 측정 스크립트를 주입해 헤드리스 Chrome 으로 렌더하고 결과를 읽는다."""
    html = io.open(src_html, encoding="utf-8").read()
    if "</body>" not in html:
        raise SystemExit(f"</body> 를 찾지 못했다: {src_html}")
    inj = html.replace("</body>", f"<script>{PROBE}</script></body>")
    tmp = os.path.join(tempfile.gettempdir(), "check_lines_probe.html")
    io.open(tmp, "w", encoding="utf-8").write(inj)

    profile = os.path.join(tempfile.gettempdir(), "check-lines-profile")
    r = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", f"--user-data-dir={profile}",
         "--virtual-time-budget=25000", "--dump-dom",
         "file:///" + tmp.replace("\\", "/")],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.search(r'data-probe="([^"]*)"', r.stdout or "")
    if not m:
        raise SystemExit("측정 실패 — Chrome 이 결과를 내놓지 않았다.\n"
                         + (r.stderr or "")[-400:])
    return json.loads(m.group(1).replace("&quot;", '"'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html", help="src/planner_*.html")
    ap.add_argument("--gap", type=float, default=None,
                    help="기대하는 괘선 높이(px). 주면 그 값만 허용한다")
    ap.add_argument("--max-kinds", type=int, default=1,
                    help="문서 전체에서 허용할 괘선 높이 종류 수 (기본 1)")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    d = measure(a.html)
    pages, trk = d["pages"], d["trk"]
    fails = []

    # --- 1. 한 페이지 안에서 섞였는가 -------------------------------------
    mixed = {k: v for k, v in pages.items() if len(v) > 1}
    print(f"괘선 페이지 {len(pages)}개")
    if mixed:
        fails.append(f"한 페이지 안에 괘선 높이가 2종 이상: {len(mixed)}페이지")
        for k, v in list(mixed.items())[:10]:
            print(f"   FAIL  {k:<16} {v}")
        if len(mixed) > 10:
            print(f"   ... 외 {len(mixed)-10}개")
    else:
        print("   OK    페이지 안에서는 모두 균일")

    # --- 2. 문서 전체에서 몇 종인가 ---------------------------------------
    kinds = Counter(h for v in pages.values() for h in v)
    print(f"\n문서 전체 괘선 높이 {len(kinds)}종")
    for h, n in kinds.most_common(8):
        print(f"   {h:>7}px  ×{n}")
    if len(kinds) > a.max_kinds:
        fails.append(f"괘선 높이가 {len(kinds)}종 (허용 {a.max_kinds})")
    if a.gap is not None:
        bad = [h for h in kinds if abs(h - a.gap) > 0.6]
        if bad:
            fails.append(f"기대값 {a.gap}px 과 다른 높이: {sorted(bad)[:8]}")

    # --- 3. 표 -------------------------------------------------------------
    no_underline = [t for t in trk if t["unevenHeaderRule"]]
    outer = [t for t in trk if t["outerRight"] or t["outerBottom"]]
    print(f"\n.trk 표 {len(trk)}개")
    if no_underline:
        fails.append(f"헤더 아래 선이 열마다 다른 표: {len(no_underline)}개")
        for t in no_underline[:6]:
            print(f"   FAIL  {t['page']} 표#{t['i']} 헤더선 불균일 {t['cols']}")
    if outer:
        fails.append(f"바깥 테두리가 남은 표: {len(outer)}개")
        for t in outer[:6]:
            side = "우" if t["outerRight"] else ""
            side += "하" if t["outerBottom"] else ""
            print(f"   FAIL  {t['page']} 표#{t['i']} 바깥선({side})")
    if not no_underline and not outer:
        print("   OK    헤더선 균일, 바깥 테두리 없음")

    print()
    if fails:
        print("실패:")
        for f in fails:
            print(f"  - {f}")
        sys.exit(1)
    print("통과 — LINES.md 규칙을 모두 만족한다.")


if __name__ == "__main__":
    main()
