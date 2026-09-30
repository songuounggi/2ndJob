# -*- coding: utf-8 -*-
"""상품 4 색 섞기 비교 -- "페이지마다 4색 번갈아" vs "섹션마다 한 색" (2026-09-30 사용자 제안)

사용자 제안: A~D 네 색을 페이지마다 번갈아 나오게. 비교안: 섹션(탭)마다 색 하나를 정해 그 섹션 페이지는
종이 번짐·강조색이 그 색 -- 넘기면 섹션이 바뀔 때만 색이 바뀐다. 레일의 탭 색은 전 페이지 같다(4색).

    python scripts/p4/mix_study_p4.py        # -> output/prod4/preview/mix-v0.1/mix_study.png

본문은 색 비교용으로 Weekly rotation 표를 그대로 쓴다(제목·탭만 바꿈). 실제 페이지 내용이 아니다.
"""
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import color_candidates_p4 as cc  # noqa: E402

OUT = os.path.join(cc.ROOT, "output", "prod4", "preview", "mix-v0.2")   # v0.2: 카드 그림자 경로 수정(fix_assets) + 섹션안 PDF -> check_render
C = {c["key"]: c for c in cc.CANDIDATES}


def render_page(c, rail_pal, on, eyebrow, title, bloom_name):
    """c = 종이·번짐·본문 강조색 후보, rail_pal = 탭 색 4칸 (탭 순서 cc.TABS 의 색 칸 번호)"""
    h = open(cc.SRC, encoding="utf-8").read()
    head = h[:h.index("</head>")]
    for var in ("bg", "ink", "mid", "soft", "line", "field"):
        head = re.sub(rf"--{var}:#[0-9A-Fa-f]{{6}}", f"--{var}:{c[var]}", head, count=1)
    sec = re.search(r'<section class="page" id="cleaning".*?</section>', h, re.S).group(0)
    slot = [t[2] for t in cc.TABS if t[0] == on][0]
    a, ti, tx = rail_pal[slot]
    sec = re.sub(r'^<section class="page" id="cleaning" style="[^"]*"',
                 f'<section class="page" id="cleaning" style="--accent:{a};--chip:{ti};--accent-text:{tx}"', sec)
    sec = re.sub(r"url\('[^']*bloom[^']*'\)", f"url('{bloom_name}')", sec)
    rail = "".join(
        f'<a class="{"on" if k == on else ""}" href="#{k}" style="--acc:{rail_pal[i][0]};--acc-text:{rail_pal[i][2]}">'
        f'<i style="background:{rail_pal[i][0]}"></i><span>{lab}</span></a>' for k, lab, i in cc.TABS)
    sec = re.sub(r'<nav class="rail">.*?</nav>', f'<nav class="rail">{rail}</nav>', sec, flags=re.S)
    sec = sec.replace(">Life<", f">{eyebrow}<", 1).replace(">Cleaning<", f">{title}<", 1)
    return cc.fix_assets(head + "</head><body>" + sec + "</body></html>")


def main():
    os.makedirs(OUT, exist_ok=True)
    for k, c in C.items():
        cc.bake_bloom(c, os.path.join(OUT, f"bloom_{k}.png"))
    # 섹션안: 탭 색 4칸 = A 의 1번, B 의 1번, C 의 1번, D 의 1번 (각 후보의 대표색)
    sec_pal = [cc.palette(C[k])[0] for k in "ABCD"]
    rows = {
        "alt": [(C[k], cc.palette(C[k]), "weeks", "Weeks", f"Reset week {n}", k)
                for n, k in enumerate("ABCD", 1)],
        "sec": [(C["A"], sec_pal, "home", "Home", "Start here", "A"),
                (C["B"], sec_pal, "rooms", "Rooms", "Kitchen", "B"),
                (C["C"], sec_pal, "routines", "Routines", "Weekly rotation", "C"),
                (C["D"], sec_pal, "tools", "Tools", "Rescue mode", "D")],
    }
    from playwright.sync_api import sync_playwright
    shots = {}
    with sync_playwright() as p:
        br = cc.launch(p)
        pg = br.new_page(viewport={"width": 816, "height": 1056}, device_scale_factor=1)
        for row, items in rows.items():
            shots[row] = []
            for n, (c, pal, on, eb, title, bk) in enumerate(items):
                html = os.path.join(OUT, f"{row}_{n}.html")
                doc = render_page(c, pal, on, eb, title, f"bloom_{bk}.png")
                cc.check_urls(doc, OUT)
                open(html, "w", encoding="utf-8").write(doc)
                pg.goto("file:///" + html.replace(os.sep, "/"))
                pg.wait_for_timeout(500)
                png = os.path.join(OUT, f"{row}_{n}.png")
                pg.locator("section.page").screenshot(path=png)
                shots[row].append(png)
                if row == "sec":
                    pg.pdf(path=png[:-4] + ".pdf", width="8.5in", height="11in", print_background=True)
        br.close()

    ims = {r: [Image.open(f).resize((408, 528)) for f in fs] for r, fs in shots.items()}
    pad, lab = 30, 64
    W = pad + 4 * (408 + pad)
    H = 2 * (lab + 528 + pad) + pad
    out = Image.new("RGB", (W, H), (236, 236, 236))
    d = ImageDraw.Draw(out)
    try:
        font = ImageFont.truetype("malgun.ttf", 28)
    except OSError:
        font = ImageFont.load_default()
    titles = {"alt": "① 페이지마다 번갈아 -- 연속한 4쪽(Week 1~4). 탭 색도 페이지마다 바뀐다",
              "sec": "② 섹션마다 한 색 -- Home·Rooms·Routines·Tools 첫 쪽. 탭 색은 전 페이지 같다"}
    for r, (key, row) in enumerate(ims.items()):
        y = pad + r * (lab + 528 + pad)
        d.text((pad, y + 14), titles[key], fill=(40, 40, 40), font=font)
        for n, im in enumerate(row):
            out.paste(im, (pad + n * (408 + pad), y + lab))
    import pikepdf
    merged = pikepdf.Pdf.new()
    for n in range(4):
        with pikepdf.open(os.path.join(OUT, f"sec_{n}.pdf")) as one:
            merged.pages.extend(one.pages)
    merged.save(os.path.join(OUT, "sec_sample.pdf"))
    path = os.path.join(OUT, "mix_study.png")
    out.save(path)
    print("->", path)


if __name__ == "__main__":
    main()
