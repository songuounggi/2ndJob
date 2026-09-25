# -*- coding: utf-8 -*-
"""GoodNotes 에서 페이지를 넘길 때 바둑판처럼 조각조각 그려지는 문제의 측정.

2026-09-24 사용자가 iPad GoodNotes 에서 판매본(v8.18)을 넘길 때마다 타일이
늦게 채워지는 것을 발견했다. 판매본 HTML 에서 5장을 떼어 변형별로 PDF 를
뽑고, iPad 해상도(scale 2.7) 렌더 시간과 판매본과의 픽셀 차이를 잰다.
판매본과 src/ 는 읽기만 한다.

  0  판매본 그대로
  E  카드·탭 그림자를 공유 PNG 한 장으로 (그라데이션 계산 -> 이미지)
  F  bloom 을 배경색에 미리 합성한 불투명 이미지로 (반투명 합성 제거)
  G  E + F

    python scripts/perf_probe.py        -> output/prod1/perf/

2026-09-24 집 PC 결과: 0=248ms, E=118, F=139, G=63 ms/page.
G 의 판매본 대비 차이는 평균 0.08 / 최대 4 단계(0~255).
"""
import os, re, subprocess, time, sys
import numpy as np
from PIL import Image
import pypdfium2 as pdfium
sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output", "prod1", "perf")
os.makedirs(OUT, exist_ok=True)
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
VERSION = os.environ.get("PLANNER_VERSION", "v8.18-undated")
url = lambda p: "file:///" + p.replace("\\", "/")

# --- shadow PNG: radial-gradient(ellipse 62% 100% at 50% 0%, rgba(0,0,0,.07), transparent 72%)
W, H = 800, 80
x = (np.arange(W) + .5) / W - .5
y = (np.arange(H) + .5) / H
d = np.sqrt((x[None, :] / .62) ** 2 + (y[:, None] / 1.0) ** 2)
a = np.clip(1 - d / .72, 0, 1) * .07
rgba = np.zeros((H, W, 4), np.uint8)
rgba[..., 3] = np.round(a * 255).astype(np.uint8)
SH = os.path.join(OUT, "shadow.png")
Image.fromarray(rgba, "RGBA").save(SH)

# --- bloom baked onto #FBF8F3 at opacity .55
b = np.asarray(Image.open(os.path.join(ROOT, "assets", f"bloom_page_{VERSION}.png")).convert("RGBA")).astype(float) / 255
bg = np.array([0xFB, 0xF8, 0xF3]) / 255
al = b[..., 3:4] * .55
baked = b[..., :3] * al + bg * (1 - al)
BK = os.path.join(OUT, "bloom_baked.png")
Image.fromarray(np.round(baked * 255).astype(np.uint8), "RGB").save(BK)

h = open(os.path.join(ROOT, "src", f"planner_{VERSION}.html"), encoding="utf-8").read()
h = h.replace("../assets/", url(ROOT) + "/assets/")
head, body = h.split("<body", 1)
body = "<body" + body
body_open = re.match(r"<body[^>]*>", body).group(0)
blocks = {m.group(1): m.group(0) for m in re.finditer(r'<section class="page" id="([^"]+)".*?</section>', body, re.S)}
PICK = ["index", "vision", "m1", "w2", "d1-2"]
sample = "".join(blocks[p] for p in PICK)

SHADOW_CSS = (f".card::after,.rail a.on::after{{background:url('{url(SH)}') 0 0/100% 100% no-repeat!important}}")
bloom_url = url(ROOT) + f"/assets/bloom_page_{VERSION}.png"

def variant(css, bake):
    s = sample
    if bake:
        s = s.replace(f"background-image:url('{bloom_url}');opacity:0.55",
                      f"background-image:url('{url(BK)}');opacity:1")
        assert url(BK) in s
    return head.replace("</head>", f"<style>{css}</style></head>") + body_open + s + "</body></html>"

VARIANTS = {"0_base": ("", False), "E_shadow_png": (SHADOW_CSS, False),
            "F_bloom_baked": ("", True), "G_E+F": (SHADOW_CSS, True)}
renders = {}
for name, (css, bake) in VARIANTS.items():
    src = os.path.join(OUT, f"{name}.html"); pdf = os.path.join(OUT, f"{name}.pdf")
    open(src, "w", encoding="utf-8").write(variant(css, bake))
    if os.path.exists(pdf): os.remove(pdf)
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", url(src)], capture_output=True, timeout=120)
    with open(pdf, "rb") as fh:
        doc = pdfium.PdfDocument(fh.read())
    ms, imgs = [], []
    for i in range(len(doc)):
        doc[i].render(scale=2.7)
        t = time.perf_counter()
        for _ in range(4): doc[i].render(scale=2.7)
        ms.append((time.perf_counter() - t) / 4 * 1000)
        imgs.append(np.asarray(doc[i].render(scale=2).to_pil().convert("L")).astype(int))
    doc.close()
    renders[name] = imgs
    diff = ""
    if name != "0_base":
        dd = [np.abs(a - b) for a, b in zip(imgs, renders["0_base"])]
        diff = "  diff mean %.2f / max %d / px>2: %.3f%%" % (
            np.mean([x.mean() for x in dd]), max(x.max() for x in dd),
            100 * np.mean([(x > 2).mean() for x in dd]))
    print(f"{name:15s} avg {sum(ms)/len(ms):4.0f} ms  " + " ".join(f"{p}:{m:.0f}" for p, m in zip(PICK, ms)) + diff)
