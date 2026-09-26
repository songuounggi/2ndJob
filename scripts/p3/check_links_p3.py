"""상품 3 완성 PDF 를 빌드와 무관하게 다시 잰다 (python scripts/p3/check_links_p3.py v0.15): 링크 목적지, 페이지마다 탭 10개, 켜진 탭(표지 0·나머지 1), 날짜 링크 짝."""
import re, sys, collections
sys.stdout.reconfigure(encoding="utf-8")
import pikepdf
ROOT = str(__import__("pathlib").Path(__file__).resolve().parents[2])
VER = sys.argv[1] if len(sys.argv) > 1 else "v0.8"
fails = 0
for y in ("2026", "2027"):
    for w in ("mon", "sun"):
        name = f"ADHD-Year-Planner-{y}-{w}"
        pdf = pikepdf.open(fr"{ROOT}\output\prod3\planner\{VER}\{name}.pdf")
        html = open(fr"{ROOT}\src\prod3\planner\{VER}\{name}.html", encoding="utf-8").read()
        ids = re.findall(r'<section class="pg" id="([^"]+)"', html)
        # named destinations
        names = {}
        if "/Dests" in pdf.Root:                       # Chrome 은 카탈로그의 /Dests 사전에 넣는다
            for k, v in pdf.Root.Dests.items():
                names[str(k).lstrip("/")] = v
        nt = pdf.Root.Names.Dests if "/Names" in pdf.Root and "/Dests" in pdf.Root.Names else {}
        def walk(n):
            if "/Names" in n:
                a = n.Names
                for i in range(0, len(a), 2):
                    names[str(a[i])] = a[i + 1]
            for k in n.get("/Kids", []):
                walk(k)
        if nt:
            walk(nt)
        pageidx = {p.objgen: i for i, p in enumerate(pdf.pages)}
        dead = 0; total = 0; tabs_bad = []; per_page_targets = []
        TABS = ["index", "sos", "year", "month", "week", "focus", "feel", "health", "life", "notes"]
        for i, pg in enumerate(pdf.pages):
            tg = []
            for a in pg.get("/Annots", []):
                if a.get("/Subtype") != "/Link":
                    continue
                total += 1
                d = str(a.get("/Dest", "")).lstrip("/")
                if d not in names:
                    dead += 1; continue
                dest = names[d]
                arr = dest.D if isinstance(dest, pikepdf.Dictionary) else dest
                tg.append((d, pageidx.get(arr[0].objgen)))
            per_page_targets.append(tg)
            # 탭 10개가 전부 링크로 있는가
            got = {d for d, _ in tg}
            miss = [t for t in TABS if t not in got]
            if miss:
                tabs_bad.append((i + 1, miss))
        # 목적지가 제 페이지를 가리키는가 (id 순서 = 페이지 순서)
        wrong = [(d, p) for d, p in {x for tg in per_page_targets for x in tg} if p is not None and ids[p] != d]
        # 활성 탭 1개
        on_bad = [m.group(1) for m in re.finditer(r'<section class="pg" id="([^"]+)".*?</nav>', html, re.S)
                  if len(re.findall(r'class="on"', m.group(0))) != (0 if m.group(1) == "cover" else 1)]   # 표지는 탭 없음(사용자 2026-09-26)
        # 일간: 어제·내일 링크 짝
        dpages = [i for i, k in enumerate(ids) if re.fullmatch(r"d\d+-\d+", k)]
        tom_bad = 0
        for j, i in enumerate(dpages[:-1]):
            if ids[dpages[j + 1]] not in {d for d, _ in per_page_targets[i]}:
                tom_bad += 1
        ok = not (dead or tabs_bad or wrong or on_bad or tom_bad) and len(pdf.pages) == 598
        fails += not ok
        print(f"{name}: pages {len(pdf.pages)}, links {total}, dead {dead}, wrong target {len(wrong)}, "
              f"pages missing tabs {len(tabs_bad)}, active-tab != 1 {len(on_bad)} {on_bad[:3]}, "
              f"daily without next-day link {tom_bad}  -> {'OK' if ok else 'FAIL'}")
print("ALL OK" if not fails else f"FAIL {fails}")
sys.exit(1 if fails else 0)
