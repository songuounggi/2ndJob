# -*- coding: utf-8 -*-
"""상품 4 v0.10~ (디자인 시안 틀) 검사 -- PROCESS.md 5단계.

    python scripts/p4/check_v2_p4.py v0.10

  1 쪽 수 108 · 쪽 크기 612x792pt (v0.10 첫 표본은 px 단위 때문에 459x594pt 였다)
  2 링크: 죽은 링크 0 · 들어올 길 없는 쪽 0 · PDF 링크 주석이 쪽마다 있음
    + 기획서 링크: v0.9(기획서대로 써 보기 통과한 판)의 쪽별 목적지가 전부 있음 -- 시안에 화살표가 없다고 링크가
      빠지면 안 된다(10-01 사용자). v0.10 첫 빌드는 빠진 쪽이 57개였다
    + HTML 링크 = PDF 링크: 쪽마다 목적지 집합이 같고 외부 링크 0 (Chrome 은 목적지 없는 링크를 조용히 버린다)
    + 주 번호: 39~90쪽 제목 "Reset week n" 과 Previous -> n-1 · Next -> n+1 (1주는 Previous 없음, 52주는 Next 없음)
  3 탭 하이라이트: 쪽마다 켜진 탭(굵기 800) 정확히 1개
  4 원고 밖 문구 0 (p4_content 와 디자인이 정한 표 머리 대문자만)
  5 글꼴: Nunito(Chrome 이 이름 없는 Type3 로 넣음) 말고 없음 -- 화살표가 대체 글꼴로 찍히던 일(v0.6)
  6 넘침: 글자가 자기 카드의 안쪽 여백(10pt)을 넘거나 카드 밖으로 나가지 않음 -- Reset week 힌트(10-01)
  7 디자인 대조: 대표 38쪽을 screenshots/ 정답 그림과 비교, 평균 차이(0~255) 기준 이하
"""
import html as H
import io
import os
import re
import sys

import pymupdf
from pypdf import PdfReader

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import p4_content as C  # noqa: E402

SHOTS = os.path.join(ROOT, "src", "p4_design_v1.0", "design_handoff_adhd_home_reset", "screenshots")
# 대표 쪽 key -> 정답 그림 (README §2)
REP = {"cover": "p001", "flow": "p002", "start": "p003", "house-map": "p004", "index": "p005", "energy": "p006",
       "day-Low": "p007", "rooms": "p010", "kitchen": "p011", "deep-kitchen": "p012", "myroom": "p027",
       "routines": "p029", "daily": "p030", "rotation": "p031", "monthly": "p032", "seasonal": "p033",
       "laundry-loop": "p034", "who-does-what": "p036", "kids-pets": "p037", "weeks": "p038", "w1": "p039",
       "tools": "p091", "rescue": "p092", "sprint": "p093", "guests": "p094", "doom": "p095", "declutter": "p096",
       "where-things-live": "p097", "restock": "p098", "dopamine": "p099", "body-doubling": "p100", "wins": "p101",
       "guess-actual": "p102", "projects": "p103", "big-reset": "p104", "notes-ruled": "p105", "notes-dots": "p106",
       "notes-blank-1": "p107"}
DIFF_MAX = 3.5      # 같은 틀·같은 내용이면 글자 안티에일리어싱 차이로 1.4~2.9 (v0.10 표본 실측)
DESIGN_LABELS = {"page", "week", "room", "task"}     # 디자인이 정한 표 머리(원고의 칸 이름을 대문자로 쓴 것 포함)

PAGE_JS = """() => {
  const out = {pages: [], over: []};
  document.querySelectorAll('section.page').forEach(sec => {
    const id = sec.id;
    // 켜진 탭: 왼쪽 레일 링크(세로 글자) 중 굵기 800
    const rail = [...sec.querySelectorAll('a span')].filter(s => s.style.writingMode === 'vertical-rl');
    const on = rail.filter(s => s.style.fontWeight === '800').length;
    const texts = [];
    const cards = [...sec.querySelectorAll('div')].filter(d => d.style.borderRadius === '16px')
                    .map(d => d.getBoundingClientRect());
    const w = document.createTreeWalker(sec, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = w.nextNode())) {
      const t = n.textContent.trim(); if (!t) continue;
      texts.push(t);
      const r = document.createRange(); r.selectNodeContents(n); const b = r.getBoundingClientRect();
      const cx = b.left + 1, cy = b.top + b.height / 2;
      const card = cards.find(c => cx >= c.left && cx <= c.right && cy >= c.top && cy <= c.bottom);
      if (card && (b.right > card.right - 10 || b.bottom > card.bottom)) out.over.push([id, t.slice(0, 40), Math.round(b.right - card.right)]);
    }
    out.pages.push([id, on, texts]);
  });
  return out;
}"""


def known_texts():
    k = set()
    for _, t in C.all_texts():
        k.add(t.lower())
        k.update(x.strip().lower() for x in re.split(r"(?<=[.?!])\s+", t))
    for a, b, _ in C.START_HERE["steps"] + C.RESCUE["steps"]:
        k.update([a.lower(), b.lower()])
    for a, b in C.LAUNDRY_LOOP + C.DISHES_LOOP + C.DOPAMINE[2] + C.DAY_PAGE_CARDS:
        k.update([a.lower(), b.lower()])
    for a, b, _ in C.FLOW["boxes"].values():
        k.update([a.lower(), b.lower()])
    k.update(x.lower() for x in C.COVER[0].replace("ADHD ", "ADHD\n").split("\n"))
    for lab in C.DAILY_RESET:                       # "Morning (5 min)" -> "Morning", "5 min"
        k.update(p.strip(" ()").lower() for p in re.split(r"[()]", lab) if p.strip(" ()"))
    return k | DESIGN_LABELS


def check(ver, tag):
    fails = []
    src = os.path.join(ROOT, "src", f"p4_home-reset_{ver}_full_{tag}.html")
    pdf = os.path.join(ROOT, "output", "prod4", "planner", ver, f"home-reset_{ver}_{tag}-FINAL.pdf")
    html = open(src, encoding="utf-8").read()
    doc = pymupdf.open(pdf)
    ids = re.findall(r'<section class="page" id="([^"]+)"', html)

    # 1
    if len(doc) != 108 or len(ids) != 108:
        fails.append(f"쪽 수 PDF {len(doc)} / HTML {len(ids)} != 108")
    sizes = {(round(p.rect.width), round(p.rect.height)) for p in doc}
    if sizes != {(612, 792)}:
        fails.append(f"쪽 크기 {sizes} != 612x792pt")
    # 2
    hrefs = set(re.findall(r'href="#([^"]+)"', html))
    nd = {k.lstrip("/") for k in PdfReader(pdf).named_destinations}
    if hrefs - nd:
        fails.append(f"죽은 링크 {sorted(hrefs - nd)[:10]}")
    incoming = {i: set() for i in ids}
    for m in re.finditer(r'<section class="page" id="([^"]+)">(.*?)</section>', html, re.S):
        for t in set(re.findall(r'href="#([^"]+)"', m.group(2))):
            if t in incoming and t != m.group(1):
                incoming[t].add(m.group(1))
    orph = [i for i, s in incoming.items() if not s and i != "cover"]
    if orph:
        fails.append(f"들어올 길 없는 쪽 {orph}")
    base = os.path.join(ROOT, "src", f"p4_home-reset_v0.9_{tag}.html")
    if os.path.exists(base):
        per = lambda h: {m.group(1): set(re.findall(r'href="#([^"]+)"', m.group(2))) for m in
                         re.finditer(r'<section class="page" id="([^"]+)"[^>]*>(.*?)</section>', h, re.S)}
        old, new = per(open(base, encoding="utf-8").read()), per(html)
        lost = {k: sorted(old[k] - new.get(k, set()) - {k}) for k in old if old[k] - new.get(k, set()) - {k}}
        if lost:
            fails.append(f"기획서 링크 빠짐 {len(lost)}쪽: " + "; ".join(f"{ids.index(k) + 1} {k} {v}" for k, v in list(lost.items())[:8]))
    else:
        print("   (v0.9 HTML 없음 -- 기획서 링크 대조 건너뜀. python scripts/p4/build_p4.py full 로 v0.9 를 뽑으면 잰다)")
    secs = list(re.finditer(r'<section class="page" id="([^"]+)"[^>]*>(.*?)</section>', html, re.S))
    mism = []
    for n, m in enumerate(secs):
        want = set(re.findall(r'href="#([^"]+)"', m.group(2)))
        links = doc[n].get_links()
        got = {ids[l["page"]] for l in links if l.get("page", -1) >= 0}
        if want != got or any(l.get("page", -1) < 0 for l in links):
            mism.append(f"{n + 1} {m.group(1)} {sorted(want ^ got)[:4]}")
    if mism:
        fails.append(f"HTML 링크와 PDF 링크가 다른 쪽 {mism[:8]}")
    badw = []
    for m in secs:
        k = m.group(1)
        if not re.fullmatch(r"w\d+", k):
            continue
        n = int(k[1:])
        body = m.group(2)
        hrefs = re.findall(r'href="#(w\d+)"[^>]*>(.*?)</a>', body, re.S)
        nav = {re.sub(r"<[^>]+>", "", t).strip(): w for w, t in hrefs}
        ok = (f">Reset week {n}<" in body and nav.get(C.LABELS["next"]) == (f"w{n + 1}" if n < 52 else None)
              and nav.get(C.LABELS["prev"]) == (f"w{n - 1}" if n > 1 else None))
        if not ok:
            badw.append(f"{k} {nav}")
    if badw:
        fails.append(f"주 번호·앞뒤 주 링크가 틀린 쪽 {badw[:6]}")
    thin = [n + 1 for n, p in enumerate(doc) if len(list(p.links())) < 7]
    if thin:
        fails.append(f"링크 주석이 7개 미만인 쪽 {thin[:10]}")
    # 5
    other = sorted({f[3] for p in doc for f in p.get_fonts() if f[3] and "Nunito" not in f[3]})
    if other:
        fails.append(f"허용 밖 글꼴 {other}")
    # 3 4 6 -- 브라우저에서
    from chrome_auto import launch
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = launch(p)
        pg = br.new_page(viewport={"width": 900, "height": 1000})
        pg.goto("file:///" + src.replace(os.sep, "/"))
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(1500)
        got = pg.evaluate(PAGE_JS)
        br.close()
    bad_on = [(i, n) for i, n, _ in got["pages"] if n != 1]
    if bad_on:
        fails.append(f"켜진 탭 != 1 {bad_on[:10]}")
    K = known_texts()
    KW = {wd for t in K for wd in re.findall(r"[a-z0-9'&?]+", t)}      # 원고에 나오는 단어
    extra = {}
    for i, _, texts in got["pages"]:
        for t in texts:
            t2 = H.unescape(t).strip()
            parts = [x.strip() for x in t2.split(" · ")]
            if re.fullmatch(r"[\d\s+]+|[MTWFS]|MON|TUE|WED|THU|FRI|SAT|SUN|\d+ MIN|5:00|SOS|Round \d|Reset week \d+|.+: deep clean|Notes \(.+\)", t2):
                continue
            if all(x.lower() in K for x in parts):
                continue
            # 화살표를 앞 단어와 묶으면 글자 조각이 "Check your" / "battery" 처럼 나뉜다 -- 조각은 단어 단위로 본다
            if all(wd in KW for wd in re.findall(r"[a-z0-9'&?]+", t2.lower())):
                continue
            extra.setdefault(t2, i)
    if extra:
        fails.append(f"원고 밖 문구 {len(extra)}: " + "; ".join(f"{t} ({i})" for t, i in list(extra.items())[:12]))
    if got["over"]:
        fails.append(f"카드 넘침 {len(got['over'])}: {got['over'][:8]}")
    # 7
    if tag == "color" and os.path.isdir(SHOTS):
        from PIL import Image, ImageChops
        files = {f[:4]: f for f in os.listdir(SHOTS)}
        worst = []
        for key, sh in REP.items():
            ref = Image.open(os.path.join(SHOTS, files[sh])).convert("L")
            pix = doc[ids.index(key)].get_pixmap(matrix=pymupdf.Matrix(ref.width / 612, ref.width / 612))
            mine = Image.open(io.BytesIO(pix.tobytes("png"))).convert("L").resize(ref.size)
            hist = ImageChops.difference(ref, mine).histogram()
            v = sum(k * n for k, n in enumerate(hist)) / (ref.width * ref.height)
            worst.append((round(v, 2), key))
        worst.sort(reverse=True)
        over = [w for w in worst if w[0] > DIFF_MAX]
        print(f"   디자인 대조: 대표 {len(worst)}쪽, 평균 차이 최대 {worst[0]} · 중앙 {worst[len(worst)//2][0]}")
        if over:
            fails.append(f"디자인과 차이 큼(>{DIFF_MAX}) {over}")
    return fails


if __name__ == "__main__":
    ver = sys.argv[1] if len(sys.argv) > 1 else "v0.10"
    total = 0
    for tag in ("color", "BW"):
        f = check(ver, tag)
        print(f"{tag}: ", "OK" if not f else "FAIL")
        for x in f:
            print("   ", x)
        total += len(f)
    print("FAILURES:", total)
