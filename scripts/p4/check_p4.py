# -*- coding: utf-8 -*-
"""상품 4 완성 PDF 검사 -- 쪽 수·죽은 링크·들어올 길 없는 페이지·탭 하이라이트·문구 누락 (PROCESS.md 5단계 일부).

    python scripts/p4/check_p4.py v0.1

CLAUDE.md "500페이지 규모에서 터진 것들" 3~5: 목적지 없는 링크는 Chrome 이 조용히 버린다 / 있어야 할 링크가
빠졌는지도 본다 / 현재 탭 표시가 표지 빼고 전 페이지에 정확히 1개.
"""
import os
import re
import sys

from pypdf import PdfReader

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import p4_content as C  # noqa: E402

EXPECT_PAGES = 107

# 배치 검사 (v0.1 전체 빌드를 눈으로 보고 찾은 결함 -- 2026-09-30)
#  a 페이지 밖: 내용이 페이지 아래로 넘어가 잘림 (5쪽 Index 의 Tools 목록)
#  b 카드 밖 괘선: 괘선이 카드 아래로 삐져나옴 (92쪽 sprint)
#  c 칸 넘침: 표 칸 글자가 칸보다 넓다 (Reset week 의 요일 머리글)
#  d 내부 이름 노출: 목록에 페이지 key 가 그대로 (90쪽 notes-blank-1)
#  e 표 위아래 비대칭: 헤더 위는 열리고 마지막 행 아래만 닫힘 (v0.2 전 표, 사용자 지적)
LAYOUT_JS = """() => {
  const out = [];
  document.querySelectorAll('section.page').forEach(pg => {
    const id = pg.id, pb = pg.getBoundingClientRect().bottom;
    pg.querySelectorAll('.content *').forEach(el => {
      const r = el.getBoundingClientRect();
      const inCard = el.parentElement && el.parentElement.closest('.card');   // 카드 자신은 본다, 카드 속은 b 가 본다
      if (r.height > 0 && r.bottom > pb + 1 && !inCard) out.push(['a 페이지 밖', id, el.className || el.tagName]);
    });
    pg.querySelectorAll('.card').forEach(c => {
      const cb = c.getBoundingClientRect().bottom;
      if (getComputedStyle(c).overflow === 'hidden') return;
      c.querySelectorAll('.lines > div').forEach(d => {
        const r = d.getBoundingClientRect();
        // 여분 괘선은 잘려서 안 보이게 설계됐다(상품 1 LINE_SPARE). 보이는 부분만 본다
        let eff = Infinity, p = d.parentElement;
        while (p && p !== c) { if (getComputedStyle(p).overflow === 'hidden') eff = Math.min(eff, p.getBoundingClientRect().bottom); p = p.parentElement; }
        if (r.top >= eff - 0.5) return;
        if (Math.min(r.bottom, eff) > cb + 1) out.push(['b 카드 밖 괘선', id, '']);
      });
    });
    pg.querySelectorAll('.tb th, .tb td').forEach(t => {
      if (t.scrollWidth > t.clientWidth + 1) out.push(['c 칸 넘침', id, t.textContent.trim().slice(0, 12)]);
    });
    // e 표 위아래 대칭: 헤더 위 선과 마지막 행 아래 선이 둘 다 있거나 둘 다 없어야 한다 (2026-09-30 사용자)
    pg.querySelectorAll('.tb').forEach(t => {
      const rows = t.querySelectorAll('tr'); if (rows.length < 2) return;
      const top = [...rows[0].children].map(c => parseFloat(getComputedStyle(c).borderTopWidth) > 0);
      const bot = [...rows[rows.length - 1].children].map(c => parseFloat(getComputedStyle(c).borderBottomWidth) > 0);
      if (top.some(x => x) !== bot.some(x => x) || new Set(top).size > 1 || new Set(bot).size > 1)
        out.push(['e 표 위아래 비대칭', id, '']);
    });
    pg.querySelectorAll('a').forEach(a => {
      if (/^(notes|deep|day)-|^w\d+$/.test(a.textContent.trim())) out.push(['d 내부 이름', id, a.textContent.trim()]);
    });
  });
  const seen = new Set();
  return out.filter(x => { const k = x.join('|'); if (seen.has(k)) return false; seen.add(k); return true; });
}"""


def check_layout(src):
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from chrome_auto import launch
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = launch(p)
        pg = br.new_page(viewport={"width": 816, "height": 1056})
        pg.goto("file:///" + src.replace(os.sep, "/"))
        pg.wait_for_timeout(800)
        found = pg.evaluate(LAYOUT_JS)
        br.close()
    return found


def check(ver, tag):
    fails = []
    src = os.path.join(ROOT, "src", f"p4_home-reset_{ver}_{tag}.html")
    pdf = os.path.join(ROOT, "output", "prod4", "planner", ver, f"home-reset_{ver}_{tag}-FINAL.pdf")
    html = open(src, encoding="utf-8").read()
    r = PdfReader(pdf)
    ids = re.findall(r'<section class="page" id="([^"]+)"', html)

    if len(r.pages) != EXPECT_PAGES or len(ids) != EXPECT_PAGES:
        fails.append(f"쪽 수 PDF {len(r.pages)} / HTML {len(ids)} != {EXPECT_PAGES}")

    # 죽은 링크: href 대상이 PDF named destination 에 있나
    hrefs = set(re.findall(r'href="#([^"]+)"', html))
    nd = {k.lstrip("/") for k in r.named_destinations}
    dead = sorted(hrefs - nd)
    if dead:
        fails.append(f"죽은 링크 {dead}")

    # 들어올 길 없는 페이지: 자기 말고 다른 페이지에서 링크가 하나라도 오나 (표지 제외)
    incoming = {i: set() for i in ids}
    for m in re.finditer(r'<section class="page" id="([^"]+)".*?</section>', html, re.S):
        for t in set(re.findall(r'href="#([^"]+)"', m.group(0))):
            if t in incoming and t != m.group(1):
                incoming[t].add(m.group(1))
    orphans = [i for i, s in incoming.items() if not s and i != "cover"]
    if orphans:
        fails.append(f"들어올 길 없는 페이지 {orphans}")

    # PDF 에 실제로 링크 주석이 살아 있나 (쪽마다 SOS·탭 6개 = 최소 7, 표지는 탭 6)
    thin = [n + 1 for n, pg in enumerate(r.pages) if len(pg.get("/Annots", []) or []) < (6 if n == 0 else 7)]
    if thin:
        fails.append(f"링크 주석이 모자란 쪽 {thin[:10]}")

    # 탭 하이라이트: 표지 빼고 전부 정확히 1개
    bad_tab = []
    for m in re.finditer(r'<section class="page" id="([^"]+)".*?</nav>', html, re.S):
        n = len(re.findall(r'<a class="on"', m.group(0)))
        if n != 1 and m.group(1) != "cover":
            bad_tab.append((m.group(1), n))
    if bad_tab:
        fails.append(f"탭 하이라이트 != 1 {bad_tab[:10]}")

    # 문구 누락: 원고의 핵심 문구가 HTML 에 있나 (5-1 기획서 대조의 최소판)
    must = ([t for v in C.ENERGY.values() for t, _ in v] + [s for rm in C.ROOMS for s in rm[2]]
            + [rm[3] for rm in C.ROOMS] + [d for rm in C.ROOMS for d in rm[5]] + C.MONTHLY
            + [a for a, _, _ in C.RESCUE["steps"]] + [b for _, b in C.LAUNDRY_LOOP + C.DISHES_LOOP])
    plain = html.replace("&amp;", "&").replace("&#x27;", "'")
    missing = [t for t in must if t not in plain]
    if missing:
        fails.append(f"원고 문구가 PDF 원본에 없음 {len(missing)}: {missing[:5]}")
    lay = check_layout(src)
    if lay:
        kinds = {}
        for k, pid, what in lay:
            kinds.setdefault(k, []).append(f"{pid}:{what}" if what else pid)
        for k, v in kinds.items():
            fails.append(f"{k} {len(v)}곳: {v[:6]}")
    return len(r.pages), len(hrefs), fails


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    ver = sys.argv[1] if len(sys.argv) > 1 else "v0.1"
    total = 0
    for tag in ("color", "BW"):
        n, h, f = check(ver, tag)
        print(f"{tag}: {n}쪽, 링크 대상 {h}개 ->", "OK" if not f else "FAIL")
        for x in f:
            print("   ", x)
        total += len(f)
    print("FAILURES:", total)
