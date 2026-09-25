# -*- coding: utf-8 -*-
"""에디션 PDF 검사 -- 핸드오프 README "Checklist before shipping each PDF" 전 항목.

    python scripts/p3/editions_check.py

pdfimages / pdffonts 가 이 PC 에 없어서 PyMuPDF 로 같은 것을 잰다.
"""
import io
import json
import pathlib
import re
import sys

import fitz  # PyMuPDF
import numpy as np
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import editions_build as B

ROOT = B.ROOT
SHOTS = B.HAND / "screenshots"
SHOT_OF = {
    "pg-fe-home": "focus-01-cover", "pg-fe-guide": "focus-02-how-to-use", "pg-fe-dump": "focus-03-brain-dump",
    "pg-fe-day": "focus-04-daily", "pg-fe-week": "focus-05-weekly", "pg-fe-month": "focus-06-monthly",
    "pg-fe-track": "focus-07-divider-trackers", "pg-fe-habits": "focus-08-habits", "pg-fe-menu": "focus-09-dopamine-menu",
    "pg-ae-home": "admin-01-cover", "pg-ae-bills": "table-7b-chunked-by-week", "pg-ae-subs": "admin-03-subscriptions",
    "pg-ae-projects": "admin-04-projects", "pg-ae-tables": "table-7f-plain",
    "pg-ee-home": "evening-01-cover", "pg-ee-shutdown": "evening-02-shutdown", "pg-ee-sleep": "evening-03-sleep-mood",
    "pg-dd-3a-home": "directions-3a-cover", "pg-dd-3a-day": "directions-3a-daily",
    "pg-dd-3b-home": "directions-3b-cover", "pg-dd-3b-day": "directions-3b-daily",
    "pg-dd-3c-home": "directions-3c-cover", "pg-dd-3c-day": "directions-3c-daily",
}
CAPTION_WORDS = re.compile(r"Sheet [AB]|\b7[a-f]\b|PDF edge|Option", re.I)


def check_edition(ed):
    fname, _, pages = B.EDITIONS[ed]
    pdf_path = B.OUT / f"{fname}.pdf"
    html = (B.SRC / f"{fname}.html").read_text(encoding="utf-8")
    doc = fitz.open(pdf_path)
    ids = [p[0] for p in pages]
    res = {"file": pdf_path.name, "bytes": pdf_path.stat().st_size, "pages": len(doc), "fail": [], "warn": [], "info": {}}
    F, Wn = res["fail"].append, res["warn"].append

    # 1. 용량 + 이미지
    if res["bytes"] > 5_000_000:
        F(f"용량 {res['bytes']:,} > 5MB")
    imgs = {}
    page_bg = {}
    for i, pg in enumerate(doc):
        for im in pg.get_images(full=True):
            xref, w, h = im[0], im[2], im[3]
            imgs.setdefault(xref, {"w": w, "h": h, "pages": set()})["pages"].add(i)
        bgs = [im[0] for im in pg.get_images(full=True) if (im[2], im[3]) == (1536, 2048)]
        page_bg[i] = bgs
    big = {x: v for x, v in imgs.items() if (v["w"], v["h"]) == (1536, 2048)}
    other = {x: v for x, v in imgs.items() if x not in big}
    res["info"]["images"] = {"backgrounds_unique": len(big),
                             "other_images": [(v["w"], v["h"], len(v["pages"])) for v in other.values()]}
    if len(big) > 2:
        F(f"배경 이미지가 {len(big)}개 (2개 이하여야)")
    if other:
        Wn(f"배경 말고 래스터 {len(other)}종: {res['info']['images']['other_images'][:6]}")

    # 2. 폰트
    fonts = set()
    for pg in doc:
        for f in pg.get_fonts(full=True):
            fonts.add((f[3], f[1]))      # (basefont, type)
    res["info"]["fonts"] = sorted(f"{n} ({t})" for n, t in fonts)
    bad_fonts = [n for n, _ in fonts if "SourceSerif4" not in n.replace(" ", "")]
    if bad_fonts:
        F(f"Source Serif 4 가 아닌 폰트: {bad_fonts}")

    # 3. 탭 링크: 페이지마다 탭 수, 각 탭의 목적지 = README 탭 세트
    for i, pg in enumerate(doc):
        want = B.tabs_for(ed, ids[i])
        links = [l for l in pg.get_links() if l.get("kind") == fitz.LINK_GOTO or l.get("kind") == fitz.LINK_NAMED]
        tabs = sorted([l for l in links if l["from"].x0 >= 725 * 0.75], key=lambda l: l["from"].y0)
        if len(tabs) != len(want):
            F(f"{ids[i]}: 탭 링크 {len(tabs)}개 (기대 {len(want)})")
            continue
        for l, (label, target) in zip(tabs, want):
            dest = l.get("page")
            if dest is None and l.get("nameddest") is not None:
                dest = doc.resolve_names().get(l["nameddest"], {}).get("page")
            if dest != ids.index(target):
                F(f"{ids[i]}: 탭 {label} -> p{None if dest is None else dest + 1} (기대 {ids.index(target) + 1} {target})")

    # 4. Sheet B 는 표지·섹션 구분 페이지에만
    sheet_of_xref = {}
    for x in big:
        pix = fitz.Pixmap(doc, x)
        a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)[:, :, :3].astype(int)
        # A: 왼쪽 위 모서리가 들렸다(밝다) / B: 왼쪽 아래
        tl, bl = a[80:160, 80:160].mean(), a[-160:-80, 80:160].mean()
        sheet_of_xref[x] = "A" if tl > bl else "B"
    for i in range(len(doc)):
        s = {sheet_of_xref.get(x) for x in page_bg[i]}
        want = "B" if ids[i] in B.COVER_OR_DIVIDER else "A"
        if s != {want}:
            F(f"{ids[i]}: 배경 {s} (기대 Sheet {want})")

    # 5. 시안(cyan)·마젠타 판: HTML 에서 센다
    secs = {m.group(1): m.group(0) for m in re.finditer(r'<section class="page" id="([^"]+)".*?</section>', html, re.S)}
    res["info"]["accent"] = {}
    for pid, sec in secs.items():
        body = re.sub(r"<nav.*?</nav>", "", sec, flags=re.S)
        plates = len(re.findall(r"text-shadow:[^;\"]*accent-2", body))
        cmyk = len(re.findall(r'class="cmyk-num"', body))
        cyan = len(re.findall(r"var\(--color-accent(?:-[0-9]+)?\)", body))
        res["info"]["accent"][pid] = {"plates": plates, "cmyk_num": cmyk, "cyan_refs": cyan}
        if plates > 2:
            F(f"{pid}: 마젠타 판 {plates}번 (2번 이하)")

    # 6. 캡션·옵션 배지·가이드가 인쇄되지 않았는가
    for i, pg in enumerate(doc):
        t = pg.get_text()
        hit = CAPTION_WORDS.findall(t)
        if hit:
            F(f"{ids[i]}: 캡션 문구 {hit}")
        # 7. 텍스트가 뽑히는가 (= 벡터)
        if len(t.strip()) < 5:
            F(f"{ids[i]}: 텍스트가 거의 없다 ({len(t.strip())}자)")

    # 8. 레퍼런스 스크린샷과 비교 (768x1024)
    res["info"]["diff"] = {}
    for i, pg in enumerate(doc):
        shot = SHOTS / f"{SHOT_OF[ids[i]]}.png"
        pix = pg.get_pixmap(matrix=fitz.Matrix(4 / 3, 4 / 3), alpha=False)
        mine = Image.frombytes("RGB", (pix.w, pix.h), pix.samples).convert("L")
        ref = Image.open(shot).convert("L").resize(mine.size)
        d = np.abs(np.asarray(mine, int) - np.asarray(ref, int))
        res["info"]["diff"][ids[i]] = round(float(d.mean()), 2)
        mine.save(B.SRC / f"_render_{ids[i]}.png")
    return res


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    allres = {ed: check_edition(ed) for ed in B.EDITIONS}
    (B.OUT / "check_report.json").write_text(json.dumps(allres, indent=1, ensure_ascii=False), encoding="utf-8")
    nf = 0
    for ed, r in allres.items():
        print(f"\n== {r['file']}  {r['pages']}p  {r['bytes']:,} B")
        print("   images:", r["info"]["images"])
        print("   fonts :", r["info"]["fonts"])
        print("   diff vs screenshot (mean |Δ| 0-255):", r["info"]["diff"])
        print("   accent:", {k: (v["plates"], v["cmyk_num"], v["cyan_refs"]) for k, v in r["info"]["accent"].items()})
        for f in r["fail"]:
            print("   FAIL", f)
        for w in r["warn"]:
            print("   warn", w)
        nf += len(r["fail"])
    print("\n전부 통과" if not nf else f"\nFAIL {nf}")
    sys.exit(1 if nf else 0)
