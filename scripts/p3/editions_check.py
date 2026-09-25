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
        tabs = sorted([l for l in links if l["from"].x0 >= 480], key=lambda l: l["from"].y0)
        if len(tabs) != len(want):
            F(f"{ids[i]}: 탭 링크 {len(tabs)}개 (기대 {len(want)})")
            continue
        for l, (label, target) in zip(tabs, want):
            dest = l.get("page")
            if dest is None and l.get("nameddest") is not None:
                dest = doc.resolve_names().get(l["nameddest"], {}).get("page")
            if dest != ids.index(target):
                F(f"{ids[i]}: 탭 {label} -> p{None if dest is None else dest + 1} (기대 {ids.index(target) + 1} {target})")

    # 3-2. 종이+탭 묶음이 가운데인가 -- 코드의 SHIFT 값이 아니라 PDF 안의 실제 위치로 잰다
    #      (같은 숫자로 만들고 같은 숫자로 재면 틀려도 맞다고 나온다).
    #      종이 왼쪽 = 배경 이미지의 x + 38px (이미지에 종이가 구워져 있다), 오른쪽 = 가장 오른쪽 탭 링크 끝.
    sheet_left = None
    for x in big:
        pix = fitz.Pixmap(doc, x)
        row = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)[pix.h // 2, :, :3].mean(axis=1)
        sheet_left = int(np.argmax(row > 240)) / (pix.w / 768)     # 2x -> px
        break
    for i, pg in enumerate(doc):
        tabs = [l["from"] for l in pg.get_links() if l["from"].x0 >= 480]
        bg = [pg.get_image_bbox(im) for im in pg.get_images(full=True) if (im[2], im[3]) == (1536, 2048)]
        if not tabs or not bg:
            F(f"{ids[i]}: 가운데 검사 불가 (탭 {len(tabs)}, 배경 {len(bg)})")
            continue
        # 배경 이미지는 이미 SHIFT 만큼 옮겨 구웠으므로(0,0 에 놓인다) 종이 왼쪽 = 38 - 옮긴 양.
        # 옮긴 양은 이미지에서 잰다: 종이 가장자리(밝은 종이 vs 책상)가 처음 나타나는 x.
        left_gap = bg[0].x0 / 0.75 + sheet_left
        right_gap = 768 - max(t.x1 for t in tabs) / 0.75
        res["info"].setdefault("gaps", {})[ids[i]] = (round(left_gap, 1), round(right_gap, 1))
        if abs(right_gap - left_gap) > 1:
            F(f"{ids[i]}: 가운데 아님 — 왼쪽 {left_gap:.1f}px / 오른쪽 {right_gap:.1f}px")

    # 3-3. 배경 오른쪽 끝에 세로 이음매가 없는가. 묶음을 옮기고 빈 띠를 책상색으로 칠했을 때
    #      오른쪽 아래(들린 모서리 그림자)에서 x=755px 을 경계로 225 -> 231 로 끊겼다(2026-09-25).
    for i, pg in enumerate(doc):
        pix = pg.get_pixmap(matrix=fitz.Matrix(4 / 3, 4 / 3), alpha=False)
        a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, 3).astype(int).mean(axis=2)
        # 탭 레일 아래(y 880~) 만 본다 -- 탭 모서리(청록 활성 탭)가 계단으로 잡혔다. 가장 긴 레일
        # (Focus 9탭)도 y≈780px 에서 끝난다. 이음매가 났던 곳은 들린 모서리 그림자(오른쪽 아래)다.
        step = np.abs(np.diff(a[880:1024, 740:768], axis=1)).max()
        if step > 3:
            F(f"{ids[i]}: 오른쪽 끝 이음매 (가로 밝기 계단 {step:.0f})")

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
        # 묶음을 왼쪽으로 SHIFT 옮겼으니 레퍼런스도 같이 옮겨 비교한다(오른쪽 빈 띠는 책상색)
        sh = Image.new("L", ref.size, 231)
        sh.paste(ref, (-B.SHIFT, 0))
        ref = sh
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
        print("   gaps L/R px:", sorted(set(r["info"].get("gaps", {}).values())))
        print("   accent:", {k: (v["plates"], v["cmyk_num"], v["cyan_refs"]) for k, v in r["info"]["accent"].items()})
        for f in r["fail"]:
            print("   FAIL", f)
        for w in r["warn"]:
            print("   warn", w)
        nf += len(r["fail"])
    print("\n전부 통과" if not nf else f"\nFAIL {nf}")
    sys.exit(1 if nf else 0)
