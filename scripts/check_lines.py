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
const out = {pages:{}, trk:[], cards:[], over:[], uneven:[], short:[], tail:[], holes:[]};
document.querySelectorAll('section.page').forEach(sec => {
  const rules = [...sec.querySelectorAll('.lines > div')];
  if (rules.length) {
    const hs = rules.map(d => Math.round(d.getBoundingClientRect().height*10)/10);
    out.pages[sec.id] = [...new Set(hs)].sort((a,b) => a-b);
  }
  // 높이가 같은 카드는 줄 수도 같아야 한다. 사용자의 규칙 그대로다 --
  // "섹션 높이가 같다면 줄 수도 같아야 함". 같은 flex 로 묶으면 Vision
  // 페이지처럼 행이 다른 두 쌍을 놓친다(양쪽 행 모두 flex:1 이라 높이는
  // 같은데 줄 수가 6 대 5 였다). 그래서 실측 높이로 묶는다.
  sec.querySelectorAll('.lines').forEach(L => {
    const k = [...L.children];
    if (!k.length) return;
    const one = k[0].getBoundingClientRect().height;
    if (!one) return;
    const card = L.closest('.card');
    if (!card) return;
    // How much room is left under the last rule that actually renders. A
    // rule sitting exactly on the clip boundary is a coin toss in the
    // rasteriser: "Worth it?" measured three rules here and printed two.
    const lb = L.getBoundingClientRect();
    let vis = 0, lastBottom = lb.top;
    for (const d of L.children) {
      const b = d.getBoundingClientRect().bottom;
      if (b <= lb.bottom + 0.5) { vis++; lastBottom = b; } else break;
    }
    out.cards.push({
      page: sec.id,
      h: Math.round(card.getBoundingClientRect().height),
      vis: vis,
      // Only meaningful where the box is actually clipping. When the
      // rules set the box height there is no boundary to fall off.
      slack: (L.scrollHeight > L.clientHeight + 1)
             ? Math.round((lb.bottom - lastBottom) * 100) / 100 : null,
      label: (card.querySelector('.label') || {}).textContent || ''
    });
  });
  // 카드 안의 내용이 카드를 넘치는가. flex:none 카드에 여분 괘선을 찍어
  // 카드가 부풀고 위 칸을 짓눌렀던 결함("Working backwards")을 잡는다.
  sec.querySelectorAll('.card').forEach((c, i) => {
    // scrollHeight 를 쓰면 안 된다. .card::after 의 그림자 타원이
    // (top:100%, height:13pt = 17.3px) 카드 아래에 놓여 있어서 모든
    // 카드가 17~18px 넘치는 것으로 잡힌다. 자식 요소만 본다.
    const cs = getComputedStyle(c);
    const r = c.getBoundingClientRect();
    const inner = r.bottom - parseFloat(cs.paddingBottom || 0)
                           - parseFloat(cs.borderBottomWidth || 0);
    let d = 0;
    for (const ch of c.children) {
      // An absolutely positioned child with inset:0 fills the card's
      // PADDING box on purpose -- the mind map's connector svg does exactly
      // that -- so measuring it against the content box reports the bottom
      // padding as overflow. It is laid out by its own offsets, not by the
      // flow, so it cannot be crushed by a sibling either.
      const pos = getComputedStyle(ch).position;
      if (pos === 'absolute' || pos === 'fixed') continue;
      const cb = ch.getBoundingClientRect().bottom;
      if (cb - inner > d) d = cb - inner;
    }
    if (d > 2) out.over.push({page: sec.id, i, d: Math.round(d)});
  });
  // A box that its rules cannot fill. This is the LINE_SPARE class of
  // defect: lines(7) printed 15 rules into a box that fits 21, and the
  // leftover showed up as a hole once card heights followed the rules
  // (19p Screen time, 32p Boundaries). Every rule visible AND a full pitch
  // of room still left over means the card is short of rules.
  sec.querySelectorAll('.lines').forEach(L => {
    const k = [...L.children];
    if (!k.length) return;
    const P = k[0].getBoundingClientRect().height;
    if (!P) return;
    const room = L.clientHeight - k.length * P;
    if (room >= P) {
      const card = L.closest('.card');
      out.short.push({page: sec.id, have: k.length,
                      miss: Math.floor(room / P),
                      label: card ? ((card.querySelector('.label') || {})
                                     .textContent || '').trim().slice(0, 22) : ''});
    }
  });
  // How much of the page the body leaves empty at the bottom. Dropping
  // justify-content:space-between moved the slack here, so it is worth
  // watching that it stays small and even.
  const body = sec.querySelector('.body');
  if (body) {
    const kids = [...body.children];
    if (kids.length) {
      const last = kids[kids.length - 1].getBoundingClientRect().bottom;
      out.tail.push({page: sec.id,
        d: Math.round((body.getBoundingClientRect().bottom - last) * 10) / 10});
      // The space BETWEEN body items must be the stylesheet's gap and
      // nothing more. A wider one is a hole: that is how the slack from
      // pinning cards inside a row showed up on 32p Boundaries, sitting
      // between the row and the card under it.
      const want = parseFloat(getComputedStyle(body).rowGap) || 0;
      for (let i = 1; i < kids.length; i++) {
        const g = kids[i].getBoundingClientRect().top
                  - kids[i-1].getBoundingClientRect().bottom;
        if (g - want > 4) out.holes.push({page: sec.id, i,
          g: Math.round(g*10)/10, want: Math.round(want*10)/10});
      }
    }
  }
  // The two sides of a row must end level. Pinning cards inside a row
  // instead of the row itself broke this: Meals & groceries had a short
  // right card, and every daily page had a short right column.
  sec.querySelectorAll('.row').forEach((row, i) => {
    const kids = [...row.children];
    if (kids.length < 2) return;
    // Measure the cards, not the wrappers. A .col stretches to the row even
    // when the card inside it stops short, which is exactly how every daily
    // page ended up with a short right side while the row looked level.
    const bots = kids.map(k => {
      const cards = k.classList.contains('card') ? [k]
                    : [...k.querySelectorAll('.card')];
      if (!cards.length) return null;
      return Math.max(...cards.map(c => c.getBoundingClientRect().bottom));
    }).filter(b => b !== null);
    if (bots.length < 2) return;
    const d = Math.max(...bots) - Math.min(...bots);
    if (d > 2) out.uneven.push({page: sec.id, i, d: Math.round(d*10)/10});
  });
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
    cards, over = d.get("cards", []), d.get("over", [])
    uneven_rows = d.get("uneven", [])
    short, tail = d.get("short", []), d.get("tail", [])
    holes = d.get("holes", [])
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
    # Horizontals close, verticals open. The rule under the last row is now
    # required -- a table whose header rule spans the full width but whose
    # last row just stops reads as unfinished. Only a vertical outer edge is
    # a defect.
    outer = [t for t in trk if t["outerRight"]]
    unclosed = [t for t in trk if not t["outerBottom"]]
    print(f"\n.trk 표 {len(trk)}개")
    if no_underline:
        fails.append(f"헤더 아래 선이 열마다 다른 표: {len(no_underline)}개")
        for t in no_underline[:6]:
            print(f"   FAIL  {t['page']} 표#{t['i']} 헤더선 불균일 {t['cols']}")
    if outer:
        fails.append(f"세로 바깥 테두리가 남은 표: {len(outer)}개")
        for t in outer[:6]:
            print(f"   FAIL  {t['page']} 표#{t['i']} 우측 바깥선")
    if unclosed:
        fails.append(f"마지막 행 아래 선이 없는 표: {len(unclosed)}개")
        for t in unclosed[:6]:
            print(f"   FAIL  {t['page']} 표#{t['i']} 마감선 없음")
    if not no_underline and not outer and not unclosed:
        print("   OK    헤더선 균일, 가로 마감, 세로 열림")

    # --- 4. 높이가 같은 카드는 줄 수도 같아야 한다 ------------------------
    from collections import defaultdict
    by = defaultdict(set)
    where = defaultdict(list)
    for c in cards:
        by[(c["page"], c["h"])].add(c["vis"])
        where[(c["page"], c["h"])].append((c["label"].strip()[:22], c["vis"]))
    uneven = {k: v for k, v in by.items() if len(v) > 1}
    print("")
    print(f"괘선 카드 {len(cards)}개")
    if uneven:
        fails.append(f"높이가 같은데 줄 수가 다른 카드: {len(uneven)}묶음")
        for k, v in list(uneven.items())[:8]:
            print(f"   FAIL  {k[0]:<14} 높이 {k[1]}px  줄 {sorted(v)}")
            for lb, n in where[k]:
                print(f"           {n}줄  {lb}")
        if len(uneven) > 8:
            print(f"   ... 외 {len(uneven)-8}묶음")
    else:
        print("   OK    같은 높이 = 같은 줄 수")

    # --- 4-2. 마지막 줄이 잘림 경계에 붙어 있는가 ----------------------
    # 0.2px, set from measurement, not taste. A card pinned to exactly k*P
    # (slack 0) lost its last rule in the raster -- hyperfocus "Worth it?"
    # and gratitude "Someone I should tell". A card at 0.42px printed every
    # rule. The failure is the border landing on or past the clip edge.
    tight = [c for c in cards if c.get("slack") is not None
             and c["slack"] < 0.2 and c["vis"] > 0]
    if tight:
        fails.append(f"마지막 줄이 잘림 경계에 붙은 카드: {len(tight)}개")
        for c in tight[:8]:
            print(f"   FAIL  {c['page']:<14} 여유 {c['slack']}px  "
                  f"{c['label'].strip()[:22]}")
    else:
        print("   OK    마지막 줄 아래 여유 있음")

    # --- 5. 카드를 넘치는 내용 --------------------------------------------
    if over:
        pages_over = sorted({o["page"] for o in over})
        fails.append(f"내용이 카드를 넘침: {len(over)}개 "
                     f"({len(pages_over)}페이지)")
        for o in over[:8]:
            print(f"   FAIL  {o['page']:<14} 카드#{o['i']}  {o['d']}px 넘침")
    else:
        print("   OK    카드를 넘치는 내용 없음")

    # --- 6. 행의 좌우가 같은 높이에서 끝나는가 ---------------------------
    if uneven_rows:
        pages_u = sorted({u["page"] for u in uneven_rows})
        fails.append(f"좌우가 어긋난 행: {len(uneven_rows)}개 "
                     f"({len(pages_u)}페이지)")
        for u in uneven_rows[:8]:
            print(f"   FAIL  {u['page']:<14} 행#{u['i']}  {u['d']}px 어긋남")
    else:
        print("   OK    행의 좌우가 같은 높이에서 끝남")

    # --- 7. 줄이 모자라 상자를 못 채우는 카드 ----------------------------
    if short:
        seen, uniq = set(), []
        for x in short:
            key = re.sub(r"\d+", "N", x["page"]) + x["label"]
            if key in seen:
                continue
            seen.add(key)
            uniq.append(x)
        fails.append(f"줄이 모자란 카드: {len(short)}개 (형태별 {len(uniq)})")
        for x in sorted(uniq, key=lambda y: -y["miss"])[:8]:
            print(f"   FAIL  {x['page']:<14} {x['label'][:20]:<20} "
                  f"줄 {x['have']}개, {x['miss']}줄분 남음")
    else:
        print("   OK    줄이 상자를 채운다")

    # --- 7-2. 본문 요소 사이에 뚫린 구멍 ---------------------------------
    if holes:
        pages_h = sorted({h["page"] for h in holes})
        fails.append(f"본문 사이에 뚫린 구멍: {len(holes)}개 "
                     f"({len(pages_h)}페이지)")
        for h in sorted(holes, key=lambda x: -x["g"])[:8]:
            print(f"   FAIL  {h['page']:<14} 사이#{h['i']}  "
                  f"{h['g']}px (규정 {h['want']}px)")
    else:
        print("   OK    본문 사이 간격이 규정대로")

    # --- 8. 페이지 하단 여백 ----------------------------------------------
    if tail:
        ds = [t["d"] for t in tail]
        worst = max(tail, key=lambda t: t["d"])
        print(f"   본문 아래 여백  최소 {min(ds)}px  최대 {max(ds)}px "
              f"({worst['page']})")
        if max(ds) > 120:
            fails.append(f"본문 아래 여백이 {max(ds)}px "
                         f"({worst['page']}) -- 120px 초과")

    print()
    if fails:
        print("실패:")
        for f in fails:
            print(f"  - {f}")
        sys.exit(1)
    print("통과 — LINES.md 규칙을 모두 만족한다.")


if __name__ == "__main__":
    main()
