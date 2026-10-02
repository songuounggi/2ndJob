# -*- coding: utf-8 -*-
"""상품 4 리스팅 사진 10장 + 핀 6장을 claude.ai/design 에 맡길 묶음 (product4-listing-handoff.md).

    python scripts/p4/handoff_listing_p4.py [판, 기본 v0.14]
    -> output/prod4/handoff/<HANDOFF_VER>/ (00_HANDOFF.md + pages/*.png) + <HANDOFF_VER>.zip

쪽 그림은 판매 PDF 를 그대로 렌더한다(2배, 1224 x 1584) -- 사진 속 화면은 실제 쪽만 쓰게. 쪽 목록 = 인수인계서 4절 · 8-3절.
이미 있는 묶음 폴더면 멈춘다(덮어쓰지 않는다) -- 인수인계서를 고치면 HANDOFF_VER 를 올린다.
"""
import os
import re
import shutil
import sys
import zipfile

import pypdfium2 as pdfium

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pages_p4  # noqa: E402

VER = sys.argv[1] if len(sys.argv) > 1 else "v0.14"
HANDOFF_VER = "listing-v0.3"   # v0.3: 판 v0.14 -- 2쪽이 design 순서도 시안으로 확정(임시 표시 뺌) / v0.2: 쪽 그림 이름을 쪽 제목으로(w1 -> reset-week-1), 2쪽은 _TEMP 표시 / v0.1: 첫 묶음(보내지 않음)
DOC = os.path.join(ROOT, "product4-listing-handoff.md")
OUT = os.path.join(ROOT, "output", "prod4", "handoff", HANDOFF_VER)

# 인수인계서 4절(사진 10장) · 8-3절(핀 6장)의 "쓸 쪽"
COLOR = [1, 2, 3, 4, 5, 6, 7, 11, 12, 32, 33, 36, 40, 41, 94, 96, 101, 103]
BW = [1, 6, 11, 41]


def slug(key):
    t = pages_p4.title_of(key)
    if re.fullmatch(r"w\d+", key):
        t = f"Reset week {key[1:]}"
    elif key.startswith("deep-") and t == key:
        t = key[5:] + " deep clean"
    s = re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
    return s


def main():
    if os.path.exists(OUT):
        raise SystemExit(f"이미 있다 -- 덮어쓰지 않는다: {OUT}")
    keys = [k for k, _, _ in pages_p4.specs()]
    os.makedirs(os.path.join(OUT, "pages"))
    shutil.copyfile(DOC, os.path.join(OUT, "00_HANDOFF.md"))
    for tag, nums in (("color", COLOR), ("BW", BW)):
        pdf = os.path.join(ROOT, "output", "prod4", "planner", VER, f"home-reset_{VER}_{tag}-FINAL.pdf")
        with open(pdf, "rb") as fh:
            doc = pdfium.PdfDocument(fh.read())
        if len(doc) != len(keys):
            raise SystemExit(f"{tag} 쪽 수 {len(doc)} != {len(keys)}")
        for n in nums:
            name = f"{tag.lower()}_p{n:03d}_{slug(keys[n - 1])}.png"
            doc[n - 1].render(scale=2).to_pil().save(os.path.join(OUT, "pages", name))
        doc.close()
    z = OUT + ".zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for base, _, files in os.walk(OUT):
            for f in sorted(files):
                p = os.path.join(base, f)
                zf.write(p, os.path.join(HANDOFF_VER, os.path.relpath(p, OUT)))
    print(f"{OUT}\n{z} {os.path.getsize(z) / 1e6:.1f} MB -- 쪽 그림 {len(COLOR)} + 흑백 {len(BW)}")


if __name__ == "__main__":
    main()
