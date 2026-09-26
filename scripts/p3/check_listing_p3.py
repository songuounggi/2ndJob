# -*- coding: utf-8 -*-
"""상품 3 리스팅 원고(listing-p3.md)의 주장을 실제 판매 파일에 대조한다. Prod 3 방 소유.

    python scripts/p3/check_listing_p3.py            # 기본 v0.6
    python scripts/p3/check_listing_p3.py v0.5

구매자 글은 기억으로 쓰지 않는다(shop.md 0-1절) -- 원고의 숫자·문장을 네 파일 모두에서 잰다.
"""
import datetime as dt
import pathlib
import re
import sys

import pikepdf

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[2]
VER = sys.argv[1] if len(sys.argv) > 1 else "v0.8"
sys.path.insert(0, str(ROOT / "scripts" / "p3"))
sys.argv = [sys.argv[0], "2027", "mon"]          # p3_content/p3_wireframe 는 argv 로 연도를 읽는다
import p3_content as C                           # noqa: E402

LISTING = (ROOT / "listing-p3.md").read_text(encoding="utf-8")
fails = []


def ok(cond, msg):
    print(("  OK   " if cond else "  FAIL ") + msg)
    if not cond:
        fails.append(msg)


def block(name):
    return re.search(rf"## {name}.*?```\n(.*?)```", LISTING, re.S).group(1)


# ---- 제목·태그 (Etsy 제약)
title = block("제목").strip()
caps = [w for w in re.findall(r"[A-Za-z][A-Za-z&']*", title) if len(w) > 1 and w.isupper()]
ok(len(title) <= 140 and len(caps) <= 3, f"title {len(title)} chars, all-caps words {caps}")
tags = [t for t in block("태그").splitlines() if t.strip()]
ok(len(tags) == 13 and all(len(t) <= 20 for t in tags), f"tags {len(tags)}, longest {max(map(len, tags))}")
desc = block(r"설명 \(Description\)")
ok(not re.search(r"\b(cure|cures|treat|treats|treatment|diagnos\w*|reduce symptoms|heal)\b", desc, re.I),
   "no medical claims in description")

# ---- 파일 4개
for y in (2026, 2027):
    for ws in ("mon", "sun"):
        name = f"ADHD-Year-Planner-{y}-{ws}"
        pdf = ROOT / "output" / "prod3" / "planner" / VER / f"{name}.pdf"
        html = (ROOT / "src" / "prod3" / "planner" / VER / f"{name}.html").read_text(encoding="utf-8")
        print(f"== {name}")
        n = len(pikepdf.open(pdf).pages)
        ids = re.findall(r'<section class="pg" id="([^"]+)"', html)
        ok(n == 598 == len(ids), f"598 pages (pdf {n}, html {len(ids)})")
        ok(pdf.stat().st_size < 20_000_000, f"under Etsy 20MB ({pdf.stat().st_size:,} B)")
        days = [i for i in ids if re.fullmatch(r"d\d+-\d+", i)]
        ndays = (dt.date(y, 12, 31) - dt.date(y, 1, 1)).days + 1
        ok(len(days) == ndays and days[0] == "d1-1" and days[-1] == "d12-31", f"a page for every day Jan 1-Dec 31 ({len(days)})")
        wk = [i for i in ids if re.fullmatch(r"w\d+", i)]
        wr = [i for i in ids if re.fullmatch(r"wr\d+", i)]
        ok(len(wk) == len(wr) >= 52, f"weekly page + Sunday reset for every week ({len(wk)}/{len(wr)})")
        for k in ("m", "mp", "bw", "mr"):
            ok(len([i for i in ids if re.fullmatch(rf"{k}\d+", i)]) == 12, f"12 x {k}")
        ok(len([i for i in ids if re.fullmatch(r"q\d", i)]) == 4, "4 quarter pages")
        ok(html.count("KEEP 3 · DROP 3") == 4, "quarterly keep-or-drop on all 4")
        ok(len(re.findall(r"Day \d+ · \d+ left", html)) == ndays, "every daily shows day n · m left")
        ok(html.count("Tomorrow starts") >= ndays and html.count("From yesterday") >= ndays - 1, "tomorrow/yesterday on dailies")
        ok(len(re.findall(r"this week", html, re.I)) >= len(wk), "this week's experiment on weekly pages")
        ok(all(int(x) <= 52 for x in re.findall(r"(\d+)/52", html)), "no week numbered past 52/52 (53rd is BONUS WEEK)")
        rail = re.search(r'<nav class="rail">(.*?)</nav>', html, re.S).group(1)
        tabs = re.findall(r'<span class="tv">([A-Za-z]+)<', rail)
        ok(tabs == ["Index", "SOS", "Year", "Month", "Week", "Focus", "Feel", "Body", "Life", "Notes"], f"ten tabs {tabs}")
        ok(html.count('<nav class="rail">') == len(ids), "tabs on every page (cover too)")
        # 달력 칸 링크는 PDF 에서 잰다(HTML 원본의 section 을 정규식으로 자르면 빠진다)
        with pikepdf.open(pdf) as doc:
            annots = doc.pages[ids.index("year")].get("/Annots", [])
            linked = {str(a.get("/Dest")).lstrip("/") for a in annots} & set(days)
        ok(linked == set(days), f"every day linked from Year at a glance ({len(linked)})")
        for s in ("I can't start", "I'm overwhelmed", "Someone's words stung"):
            ok(s.replace("'", "&#x27;") in html or s in html, f"SOS has {s!r}")
        for t in ("Dot grid", "Ruled", "Plain", "Grid"):
            ok(f">{t}<" in html, f"note page {t}")
        hol = list(C.holidays(y).values())          # dict 를 돌면 날짜(키)만 나와 검사가 헛돈다
        ok(not any(re.search(r"Thanksgiving|Independence|Memorial|Labor Day|Halloween", str(h)) for h in hol),
           f"only worldwide holidays ({len(hol)})")
        # 원고에 적은 인쇄 기념일 목록과 실제가 같은가
        named = {"New Year's Day", "Neurodiversity Celebration Week", "ADHD Awareness Month",
                 "World Mental Health Day", "Christmas Day", "New Year's Eve"}
        ok(set(hol) == named and all(n in desc for n in named), "printed dates == listed dates")
        ok(all(n.replace("'", "&#x27;") in html or n in html for n in named), "every listed date is printed in the file")

print(f"\n{'ALL OK' if not fails else f'FAILURES: {len(fails)}'}")
sys.exit(1 if fails else 0)
