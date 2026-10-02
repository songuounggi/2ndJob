# -*- coding: utf-8 -*-
"""상품 4 5-2 디자인 검사 (v0.10~ 디자인 시안 판) -- 시안 README 11절 "검수 방법" 을 전 쪽에(v0.11 110쪽).

    python scripts/p4/check_design_p4.py v0.10

README 11절: 계산 말고 실측 / 글꼴을 다 불러온 뒤 / 축소·확대 화면 금지 / 같은 틀을 쓰는 쪽 전체를 쪽 번호별로.
그래서 브라우저에서 쪽 확대(zoom 4/3)를 끄고 1pt = 1px 로 잰다(빌드 CSS 의 zoom 은 인쇄용).

  A 같은 틀 = 같은 배치: 반복 쪽(방 카드·깊은 청소·하루·Reset week 등)의 상자 위치·크기가 대표 쪽(시안이 실측을
    통과한 쪽, 정답 그림과 일치 -- check_v2 7)과 같은가. 줄 26 · 카드 아래 18 · 짝 높이 · 번호 카드 72 · 배너는
    대표 쪽에서 정해졌으니 배치가 같으면 같다. 의도한 차이: Reset week 의 Previous 알약(10-01 사용자)
  B 글자 넘침: 글자가 자기 상자(위치가 정해진 가장 가까운 상자) 밖으로, 또는 쪽 밖으로 나가지 않는다.
    글자 상자와 카드가 따로 놓인 곳(카드 위에 얹은 글자)은 check_v2_p4 6 "카드 넘침" 이 본다 -- 99쪽 힌트(10-01)
  C 글자 겹침: 서로 다른 글자 줄이 겹치지 않는다
  D 체크 상자: 14x14 상자는 모서리 4.5(체크) 또는 원(동그라미) -- README 규칙 4
  E 쪽 아래 알약: 높이 24 · 모서리 12 알약은 y754 -- 규칙 9
  F 링크 →: 본문 링크는 → 를 단다, 간격 4, 섹션 진한색, 글자 크기를 따로 주지 않는다(앞 글자와 같은 크기) -- 규칙 5.
    예외: 탭 레일·SOS(README §7-2), 38쪽 Weeks 칸(§8), 기획서 링크 중 보이지 않게 둔 것(10-01 사용자)
  G 선: 테두리 선은 0.6 · 세 색(#D3DBD6 / #E3E9E5 / #ECF0ED) -- 규칙 7
  H 왼쪽 탭: 6개 위치가 전 쪽 같다(12 + 128 x 순서) -- 시안 원본 3·92·94쪽이 2~4pt 아래라 넘길 때 튀었다(10-01)
  I 쓰는 칸 옆 링크: 체크 상자·동그라미(14)에서 12pt 안에 링크 상자(PDF 실제 상자)가 없다 = 손끝 오차 6pt(tap_p4) + 여유 6pt.
    94쪽 Guests 는 10pt 라 체크 상자 끝에서 4pt 만 빗나가도 넘어갔다(10-01, 써 보기 6단계)
  J 카드 전체: 링크가 하나뿐이고 쓰는 칸(체크 14 · 쓰는 줄)이 없는 카드·배너는 상자 전체가 눌린다(덮개 링크).
    94쪽 Rescue 배너 "Wins log →" 만 글자·→ 로 눌렸다 -- 흰 카드만 덮고 배너를 빠뜨렸다(10-01 사용자 질문)
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import build_v2_p4 as B  # noqa: E402

LINE_COLORS = {"#D3DBD6", "#E3E9E5", "#ECF0ED"}
# 예외: 1쪽 표지 목차 구분선 0.6 #E9EEEB 3개 -- 시안 원본 값(대표 쪽, 표가 아님). README 규칙 7 은 표 선
GAP = 12
SECTION_D = {"rgb(83, 115, 100)", "rgb(125, 106, 40)", "rgb(110, 100, 144)", "rgb(35, 117, 129)"}

JS = r"""() => {
  const R = r => [Math.round(r.left * 10) / 10, Math.round(r.top * 10) / 10, Math.round(r.width * 10) / 10, Math.round(r.height * 10) / 10];
  const out = {};
  document.querySelectorAll('section.page').forEach(sec => {
    const o = sec.getBoundingClientRect();
    const rel = r => ({left: r.left - o.left, top: r.top - o.top, right: r.right - o.left, bottom: r.bottom - o.top,
                       width: r.width, height: r.height});
    const pg = {boxes: [], over: [], texts: [], checks: [], pills: [], links: [], lines: [], arects: [], crects: [], rail: []};
    const all = [...sec.querySelectorAll('*')].filter(e => !e.closest('svg') || e.tagName === 'svg');
    all.forEach(e => {
      const cs = getComputedStyle(e), r = rel(e.getBoundingClientRect());
      if (r.width === 0 && r.height === 0) return;
      if (e.tagName !== 'svg' && cs.position === 'absolute')
        pg.boxes.push([e.tagName, !!e.style.width, ...R(r), !e.style.height]);
      // 세로 넘침은 줄 높이로 잰다(글자 사각형은 글꼴 위아래 여백까지라 제목마다 4pt 쯤 크게 나온다)
      if (e.style.height && e.scrollHeight > e.clientHeight + 1 && cs.overflow === 'visible' && e.textContent.trim())
        pg.over.push([e.textContent.trim().slice(0, 30) + ' (아래로)', e.scrollHeight - e.clientHeight]);
      if (Math.abs(r.width - 14) < .3 && Math.abs(r.height - 14) < .3 && cs.borderRadius !== '0px')
        pg.checks.push([cs.borderRadius, (e.parentElement.textContent || '').trim().slice(0, 20)]);
      if (e.tagName === 'A' && Math.abs(r.height - 24) < .3 && cs.borderRadius === '12px') pg.pills.push([R(r)[1], e.textContent.trim()]);
      for (const m of (e.getAttribute('style') || '').matchAll(/border(?:-(?:top|right|bottom|left))?:\s*([\d.]+)px\s+solid\s+(#[0-9A-Fa-f]{6})/g))
        pg.lines.push([parseFloat(m[1]), m[2].toUpperCase(), e.textContent.trim().slice(0, 16)]);
      if (e.tagName === 'svg') e.querySelectorAll('[stroke-width="0.6"]').forEach(l =>
        pg.lines.push([0.6, (l.getAttribute('stroke') || '').toUpperCase(), 'svg']));
      if (e.tagName === 'A' && !e.closest('[style*="vertical-rl"]')) pg.arects.push([r.left, r.top, r.right, r.bottom, (e.textContent || '').trim().slice(0, 20)]);
      if (Math.abs(r.width - 14) < .3 && Math.abs(r.height - 14) < .3 && cs.borderRadius !== '0px') pg.crects.push([r.left, r.top, r.right, r.bottom]);
      if (e.tagName === 'A' && Math.abs(r.width - 40) < .3 && Math.abs(r.height - 128) < .3) pg.rail.push(Math.round(r.top * 10) / 10);
      if (e.tagName === 'A') {
        const vertical = [...e.querySelectorAll('span')].some(s => s.style.writingMode === 'vertical-rl');
        const svg = e.querySelector('svg.ar');
        const sp = svg && svg.closest('span[style]');
        pg.links.push({text: e.textContent.trim().slice(0, 30), vertical, styled: e.hasAttribute('style'),
                       href: e.getAttribute('href'), arrow: !!svg,
                       gap: sp ? getComputedStyle(sp).marginLeft || '' : '', mr: sp ? getComputedStyle(sp).marginRight : '',
                       color: sp ? getComputedStyle(sp).color : '', ownSize: sp ? !!sp.style.fontSize : false,
                       sizeSame: sp ? getComputedStyle(sp).fontSize === getComputedStyle(sp.parentElement).fontSize : true});
      }
    });
    // 글자: 줄 단위 사각형, 자기 상자(가장 가까운 위치 지정 조상) 안인가
    const w = document.createTreeWalker(sec, NodeFilter.SHOW_TEXT);
    let n, id = 0;
    while ((n = w.nextNode())) {
      const t = n.textContent.trim(); if (!t) continue;
      const rg = document.createRange(); rg.selectNodeContents(n);
      const rects = [...rg.getClientRects()].map(rel).filter(r => r.width > .5);
      let box = n.parentElement;
      while (box && box !== sec && getComputedStyle(box).position !== 'absolute') box = box.parentElement;
      const br = box && box !== sec ? rel(box.getBoundingClientRect()) : {left: 0, top: 0, right: 612, bottom: 792};
      const pcs = getComputedStyle(n.parentElement);
      const vertical = pcs.writingMode === 'vertical-rl';
      const lh = parseFloat(pcs.lineHeight);
      rects.forEach(r => {
        if (!vertical && (r.right > br.right + .5 || r.left < br.left - .5))
          pg.over.push([t.slice(0, 30), Math.round(Math.max(r.right - br.right, br.left - r.left) * 10) / 10]);
        if (r.right > 612 || r.top > 792 || r.left < 0) pg.over.push([t.slice(0, 30) + ' (쪽 밖)', 0]);
        const inset = lh && r.height > lh ? (r.height - lh) / 2 : 0;
        if (!vertical) pg.texts.push([id, t.slice(0, 24), r.left, r.top + inset, r.right, r.bottom - inset]);
      });
      id++;
    }
    // J: 카드·배너(모서리 16) 안 링크 -- 목적지 하나 · 쓰는 칸 없음이면 상자 전체를 덮는 링크가 있어야
    pg.cards = [];
    const links = [...sec.querySelectorAll('a[href^="#"]')].filter(a => !a.querySelector('[style*="vertical-rl"]') && a.textContent.trim() !== 'SOS');
    [...sec.querySelectorAll('div')].filter(d => d.style.borderRadius === '16px').forEach(b => {
      const r = b.getBoundingClientRect();
      const ins = links.filter(a => { const q = a.getBoundingClientRect(); return q.width && q.left >= r.left - 1 && q.right <= r.right + 1 && q.top >= r.top - 1 && q.bottom <= r.bottom + 1; });
      const hrefs = new Set(ins.map(a => a.getAttribute('href')));
      if (hrefs.size !== 1) return;
      const writes = [...sec.querySelectorAll('span,div')].some(e => { const q = e.getBoundingClientRect(); const cs = getComputedStyle(e);
        return q.left >= r.left && q.right <= r.right && q.top >= r.top && q.bottom <= r.bottom && (Math.abs(q.width - 14) < .5 && Math.abs(q.height - 14) < .5 || parseFloat(cs.borderBottomWidth) > 0 && q.width > 60); });
      if (writes) return;
      const covered = ins.some(a => { const q = a.getBoundingClientRect(); return q.width >= r.width - 2 && q.height >= r.height * .5; });
      if (!covered) pg.cards.push([Math.round(r.top - o.top), ins[0].textContent.trim().slice(0, 24)]);
    });
    out[sec.id] = pg;
  });
  return out;
}"""


def main(ver):
    src = os.path.join(ROOT, "src", f"p4_home-reset_{ver}_full_color.html")
    ids = re.findall(r'<section class="page" id="([^"]+)"', open(src, encoding="utf-8").read())
    from chrome_auto import launch
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = launch(p)
        pg = br.new_page(viewport={"width": 700, "height": 900})
        pg.goto("file:///" + src.replace(os.sep, "/"))
        pg.add_style_tag(content="section.page{zoom:1 !important}")
        pg.evaluate("Promise.all(['400 10px Nunito','700 10px Nunito','800 10px Nunito','600 10px Nunito']"
                    ".map(f => document.fonts.load(f))).then(() => document.fonts.ready)")
        ok = pg.evaluate("['400 10px Nunito','700 10px Nunito','800 15px Nunito'].every(f => document.fonts.check(f))")
        if not ok:
            raise SystemExit("글꼴(Nunito)이 다 불러와지지 않았다 -- 잰 값이 대체 글꼴 값이 된다(README 11절)")
        got = pg.evaluate(JS)
        br.close()

    fails = {k: [] for k in "ABCDEFGHIJ"}
    num = lambda k: ids.index(k) + 1
    # A
    for k in ids:
        # 대표 쪽 = 같은 틀을 쓰는 첫 쪽 (시안 쪽 번호로 찾으면 v0.11 처럼 쪽이 밀린 판에서 엉뚱한 쪽과 비교한다)
        rep = next(x for x in ids if B.template_of(x) == B.template_of(k))
        if rep == k:
            continue
        # 폭 미지정 상자는 글자 길이를, 높이 미지정 상자는 내용(줄 수)을 따라간다 -- 방 카드 준비물 칩 1~2줄(카드 크기는 고정).
        # 내용이 길어져 아래와 부딪히면 B(넘침)·C(겹침)가 잡는다
        cut = lambda b: b[2:4] + [b[4] if b[1] else None, None if b[6] else b[5]]
        a = [cut(b) for b in got[k]["boxes"]]
        r = [cut(b) for b in got[rep]["boxes"]]
        if re.fullmatch(r"w\d+", k):         # Previous 알약(높이 24 · y754)과 그 안 화살표는 대표 쪽(w1)에 없다
            bottom = lambda b: 745 <= b[1] <= 785
            a = [b for b in a if not (bottom(b) and b[0] < 300)]
            r = [b for b in r if not (bottom(b) and b[0] < 300)]
            if k == "w52":                   # 마지막 주는 Next 알약이 없다
                a = [b for b in a if not bottom(b)]
                r = [b for b in r if not bottom(b)]
        diff = [x for x in a if x not in r]
        if diff:
            fails["A"].append(f"{num(k)} {k} (대표 {num(rep)}쪽과 다른 상자 {len(diff)}: {diff[:3]})")
    for k in ids:
        g = got[k]
        # B
        for t, d in g["over"]:
            if k == "flow" and t.startswith("Check your battery"):    # README §7-2 적용 사례 "2쪽 Check your battery → 두 줄"
                continue                                              # (배경 없는 글자 상자, 위아래 2.5pt -- 그림으로 확인)
            fails["B"].append(f"{num(k)} {k}: \"{t}\" {d}pt")
        # C
        T = g["texts"]
        for i in range(len(T)):
            for j in range(i + 1, len(T)):
                a, b = T[i], T[j]
                if a[0] == b[0]:
                    continue
                ox = min(a[4], b[4]) - max(a[2], b[2])
                oy = min(a[5], b[5]) - max(a[3], b[3])
                if ox > 1 and oy > 1:
                    fails["C"].append(f"{num(k)} {k}: \"{a[1]}\" / \"{b[1]}\"")
        # D
        for rad, ctx in g["checks"]:
            if rad not in ("4.5px", "50%", "7px"):
                fails["D"].append(f"{num(k)} {k}: 모서리 {rad} ({ctx})")
        # E
        for top, t in g["pills"]:
            if abs(top - 754) > .2:
                fails["E"].append(f"{num(k)} {k}: \"{t}\" y{top}")
        # F
        for L in g["links"]:
            if not L["text"] and not L["arrow"]:          # 카드 전체를 덮는 투명 링크(3·4쪽) -- 같은 카드의 "Go →" 를 넓힌 것
                continue
            if L["vertical"] or L["text"] in ("SOS",) or not L["styled"]:      # 레일·SOS·보이지 않는 기획서 링크
                continue
            if k == "weeks" and re.fullmatch(r"WEEK\s*\d+", L["text"]):
                continue
            if not L["arrow"]:
                fails["F"].append(f"{num(k)} {k}: \"{L['text']}\" → 없음")
                continue
            back = L["mr"] == "4px"
            if not (L["gap"] == "4px" or back):
                fails["F"].append(f"{num(k)} {k}: \"{L['text']}\" 간격 {L['gap']}/{L['mr']}")
            if L["color"] not in SECTION_D:
                fails["F"].append(f"{num(k)} {k}: \"{L['text']}\" 화살표 색 {L['color']}")
            if L["ownSize"] or not L["sizeSame"]:
                fails["F"].append(f"{num(k)} {k}: \"{L['text']}\" 화살표 크기가 앞 글자와 다름")
        # G
        for wd, col, t in g["lines"]:
            if abs(wd - 0.6) > .05 or (col not in LINE_COLORS and not (k == "cover" and col == "#E9EEEB")):
                fails["G"].append(f"{num(k)} {k}: {wd}px {col} ({t})")
    # I 는 PDF 의 실제 링크 상자로 잰다 -- Chrome 이 PDF 에 넣는 상자는 DOM 보다 넓다(94쪽: DOM 은 x132 부터, PDF 는 x126 부터).
    # iPad 에서 눌리는 것은 PDF 상자다. 체크 상자 위치는 DOM(= PDF, 1pt = 1px)
    import pymupdf
    pdf = os.path.join(os.path.dirname(os.path.dirname(src)), "output", "prod4", "planner", ver, f"home-reset_{ver}_color-FINAL.pdf")
    pdf_links = [[(l["from"].x0, l["from"].y0, l["from"].x1, l["from"].y1, "") for l in pg.get_links() if l["from"].x0 > 60]
                 for pg in pymupdf.open(pdf)]
    std = [12 + 128 * i for i in range(6)]
    for k in ids:
        if got[k]["rail"] != std:
            fails["H"].append(f"{num(k)} {k}: {got[k]['rail']}")
        for c in got[k]["crects"]:
            for a in pdf_links[num(k) - 1]:
                dx = max(a[0] - c[2], c[0] - a[2], 0)
                dy = max(a[1] - c[3], c[1] - a[3], 0)
                if (dx * dx + dy * dy) ** .5 < GAP:
                    fails["I"].append(f"{num(k)} {k}: 체크 상자 옆 링크 ({a[0]:.0f}, {a[1]:.0f}) {round((dx * dx + dy * dy) ** .5, 1)}pt")
    for k in ids:
        for top, t in got[k]["cards"]:
            fails["J"].append(f"{num(k)} {k}: y{top} 카드·배너에 링크 하나뿐인데 전체가 안 눌림 (\"{t}\")")
    names = {"A": "같은 틀 = 같은 배치", "B": "글자 넘침", "C": "글자 겹침", "D": "체크 상자 14 · 4.5",
             "E": "쪽 아래 알약 y754", "F": "링크 →", "G": "선 0.6 · 세 색", "H": "왼쪽 탭 위치 통일",
             "I": f"쓰는 칸 옆 링크 {GAP}pt", "J": "카드 전체 링크"}
    total = 0
    print(f"상품 4 디자인 검사 {ver} -- {len(ids)}쪽, 글꼴 로드 후 1배 실측")
    for k, v in fails.items():
        uniq = list(dict.fromkeys(v))
        total += len(uniq)
        print(f"  {'OK  ' if not uniq else 'FAIL'} {k} {names[k]}" + (f" -- {len(uniq)}건" if uniq else ""))
        for x in uniq[:12]:
            print("        ", x)
    print("FAILURES:", total)
    return total


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1] if len(sys.argv) > 1 else "v0.17") else 0)
