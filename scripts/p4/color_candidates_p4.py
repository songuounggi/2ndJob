# -*- coding: utf-8 -*-
"""상품 4 색 후보 -- 상품 1(v8.20) 모양에 색만 바꿔 한 페이지씩 렌더한다 (PROCESS.md 3단계).

2026-09-30 사용자 결정: 디자인 = 상품 1 모양 + 색만 바꿈 (product4-content.md 5절 ④).
상품 1 의 빌드된 HTML(src/planner_v8.20-undated.html)에서 <head> 와 'cleaning' 페이지를 가져와
  - :root 색 변수(bg·line·field·ink…)를 후보 값으로
  - 오른쪽 탭을 상품 4 의 6개(HOME·ENERGY·ROOMS·ROUTINES·WEEKS·TOOLS)로
  - 배경 번짐(bloom)을 후보 색으로 새로 구운 불투명 PNG 로 (상품 1 fast_paint 와 같은 방식)
  - 제목·부제를 상품 4 의 Weekly rotation 페이지 문구로
바꿔서 렌더한다. build_planner.py 는 다른 방과 공유하는 파일이라 import·수정하지 않는다.

    python scripts/p4/color_candidates_p4.py            # -> output/prod4/preview/colors-v0.1/

글자용 색(세 번째 값)은 카드·field·bg·칩 네 배경 모두에서 4.5:1 이상이 되게 자동으로 어둡게 한다(CLAUDE.md).
"""
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from chrome_auto import launch  # noqa: E402

VER = "colors-v0.2"   # v0.1 -> v0.2 (2026-09-30 사용자): A 오른쪽 번짐, C 왼쪽 번짐을 더 보이게
OUT = os.path.join(ROOT, "output", "prod4", "preview", VER)
SRC = os.path.join(ROOT, "src", "planner_v8.20-undated.html")

# 탭 -> 색 칸. 카테고리 색은 4개가 상한(CLAUDE.md 공통 디자인 규칙)
TABS = [("home", "HOME", 0), ("energy", "ENERGY", 0), ("rooms", "ROOMS", 1),
        ("routines", "ROUTINES", 2), ("weeks", "WEEKS", 2), ("tools", "TOOLS", 3)]
ON = "routines"            # 보여 줄 페이지 = Weekly rotation (ROUTINES)

# 후보: 이름, 한 줄, 종이 색, 번짐 색 2개(따뜻한 중심 / 왼쪽 꼬리), 강조색 4개(장식용 파스텔)
CANDIDATES = [
    dict(key="A", name="Fresh linen", ko="세이지·민트 -- 막 빨래한 리넨",
         bg="#F5F8F5", ink="#34403A", mid="#5F6B65", soft="#78837D", line="#DDE7E0", field="#EDF3EE",
         bloom=("#C4E7D2", "#CFE6EE"),
         acc=["#7FB59C", "#6AAFC0", "#E59A84", "#D6B04E"]),
    dict(key="B", name="Lemon & sky", ko="레몬·하늘 -- 상쾌하고 밝게",
         bg="#FBFAF2", ink="#3A3A34", mid="#6B6A60", soft="#838177", line="#ECE8D6", field="#F6F3E4",
         bloom=("#FBF0B8", "#D3E6F5"),
         acc=["#E2BE3E", "#7EB3DC", "#8CBB78", "#EE9F7C"]),
    dict(key="C", name="Lavender soap", ko="라벤더·로즈 -- 차분한 비누 향",
         bg="#F8F6FA", ink="#3B3844", mid="#686474", soft="#7F7B8B", line="#E6E1EE", field="#F1EEF6",
         bloom=("#E9E0F6", "#EFC6D8"),
         acc=["#A393D8", "#E293AA", "#84B49B", "#85AED9"]),
    dict(key="D", name="Aqua pop", ko="아쿠아·코랄 -- 채도 높게",
         bg="#F3F9FA", ink="#2F3C40", mid="#5A6A6F", soft="#728287", line="#D9EAEE", field="#E9F4F6",
         bloom=("#C9EEF3", "#FFE0D2"),
         acc=["#2FB3C6", "#F07C66", "#8DC23F", "#F2B233"]),
]


# ------------------------------------------------------------ colour math --
def _rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def _hex(c):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(v))) for v in c)


def _lum(h):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in _rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def mix(a, b, t):
    ra, rb = _rgb(a), _rgb(b)
    return _hex(tuple(x + (y - x) * t for x, y in zip(ra, rb)))


def tint(acc, bg):
    """칩·틴트 배경: 강조색을 종이에 아주 옅게"""
    return mix(acc, "#FFFFFF", 0.84)


def text_tone(acc, backs, need=4.6):
    """글자용: 모든 배경에서 need 이상이 될 때까지 검정 쪽으로 섞는다"""
    t = 0.0
    while t < 1:
        c = mix(acc, "#101010", t)
        if min(contrast(c, b) for b in backs) >= need:
            return c
        t += 0.02
    return "#101010"


def palette(c):
    out = []
    for a in c["acc"]:
        ti = tint(a, c["bg"])
        tx = text_tone(a, ["#FFFFFF", c["field"], c["bg"], ti])
        out.append((a, ti, tx))
    return out


# ------------------------------------------------------------------ bloom --
def bake_bloom(c, path, W=306, H=396):
    """상품 1 bloom_png 과 같은 생각: 흐린 타원 몇 겹을 종이에 미리 합성한 불투명 PNG (반쪽 크기)"""
    warm, cool = c["bloom"]
    s = W / 612
    # 상품 1 페이지처럼 위쪽에 번짐: 오른쪽 위 따뜻한 중심, 왼쪽으로 꼬리
    stops = [(400, 40, 170, 110, warm, .90), (470, 60, 150, 100, warm, .55),
             (240, 30, 160, 100, cool, .60), (120, 20, 160, 100, cool, .45)]
    img = Image.new("RGB", (W, H), _rgb(c["bg"]))
    for x, y, rx, ry, col, a in stops:
        layer = Image.new("L", (W, H), 0)
        ImageDraw.Draw(layer).ellipse([(x - rx) * s, (y - ry) * s, (x + rx) * s, (y + ry) * s],
                                      fill=int(255 * a))
        layer = layer.filter(ImageFilter.GaussianBlur(52 * s))
        img = Image.composite(Image.new("RGB", (W, H), _rgb(col)), img, layer)
    img.save(path)


# ------------------------------------------------------------------- page --
ASSETS_URI = "file:///" + os.path.join(ROOT, "assets").replace(os.sep, "/") + "/"


def fix_assets(html):
    """상품 1 HTML 은 src/ 기준 '../assets/…' 를 쓴다. 미리보기 폴더에서는 그 경로가 없어
    카드 그림자(shadow_*.png)가 조용히 빠졌다(colors-v0.2·mix-v0.1). 절대 경로로 바꾼다"""
    return html.replace("'../assets/", "'" + ASSETS_URI).replace('"../assets/', '"' + ASSETS_URI)


def check_urls(html, base):
    """url(...) 로 부르는 파일이 전부 있는지. 없으면 멈춘다 -- Chrome 은 빠진 이미지를 경고 없이 넘긴다"""
    missing = []
    for u in re.findall(r"url\(['\"]?([^'\")]+)['\"]?\)", html):
        if u.startswith(("http", "data:")):
            continue
        path = u[len("file:///"):] if u.startswith("file:///") else os.path.join(base, u)
        if not os.path.exists(path):
            missing.append(u)
    if missing:
        raise SystemExit(f"빠진 이미지: {missing}")


def page_html(c, pal, bloom_name):
    h = open(SRC, encoding="utf-8").read()
    head = h[:h.index("</head>")]
    for var in ("bg", "ink", "mid", "soft", "line", "field"):
        head = re.sub(rf"--{var}:#[0-9A-Fa-f]{{6}}", f"--{var}:{c[var]}", head, count=1)
    sec = re.search(r'<section class="page" id="cleaning".*?</section>', h, re.S).group(0)

    a, ti, tx = pal[[t[2] for t in TABS if t[0] == ON][0]]
    sec = re.sub(r'^<section class="page" id="cleaning" style="[^"]*"',
                 f'<section class="page" id="cleaning" style="--accent:{a};--chip:{ti};--accent-text:{tx}"', sec)
    sec = re.sub(r"url\('[^']*bloom[^']*'\)", f"url('{bloom_name}')", sec)
    rail = "".join(
        f'<a class="{"on" if k == ON else ""}" href="#{k}" style="--acc:{pal[i][0]};--acc-text:{pal[i][2]}">'
        f'<i style="background:{pal[i][0]}"></i><span>{lab}</span></a>' for k, lab, i in TABS)
    sec = re.sub(r'<nav class="rail">.*?</nav>', f'<nav class="rail">{rail}</nav>', sec, flags=re.S)
    # 상품 4 문구 (Weekly rotation, product4-content.md 3-4)
    sec = sec.replace(">Life<", ">Routines<", 1).replace(">Cleaning<", ">Weekly rotation<", 1)
    sec = sec.replace("One room, ten minutes. Not the whole house.",
                      "One room a day. Missed one? Slide it to the next.", 1)
    sec = sec.replace("The one that bothers me most", "Slid to next week", 1).replace(
        ">start there<", ">no penalty, just the next slot<", 1)
    return fix_assets(head + "</head><body>" + sec + "</body></html>")


SLOTS = ["HOME · ENERGY", "ROOMS", "ROUTINES · WEEKS", "TOOLS"]


def sheet(files, path):
    """네 장을 2x2 로 붙이고, 이름 + 강조색 4개 견본(탭 이름·칩 글자)을 단다.
    페이지 한 장만으로는 색이 탭 점·세로 막대에만 보여 후보 차이가 안 읽혔다 -- 견본이 그걸 메운다"""
    ims = [Image.open(f) for f in files]
    w, h = ims[0].size
    pad, lab = 40, 200
    out = Image.new("RGB", (w * 2 + pad * 3, (h + lab) * 2 + pad * 3), (236, 236, 236))
    try:
        font = ImageFont.truetype("malgun.ttf", 32)
        small = ImageFont.truetype("malgunbd.ttf", 19)
    except OSError:
        font = small = ImageFont.load_default()
    d = ImageDraw.Draw(out)
    for n, (im, c) in enumerate(zip(ims, CANDIDATES)):
        x = pad + (n % 2) * (w + pad)
        y = pad + (n // 2) * (h + lab + pad)
        d.text((x, y), f"{c['key']}  {c['name']} -- {c['ko']}", fill=(40, 40, 40), font=font)
        sw = (w - 3 * 14) // 4
        for i, (a, ti, tx) in enumerate(palette(c)):
            sx = x + i * (sw + 14)
            d.rounded_rectangle([sx, y + 56, sx + sw, y + 112], radius=10, fill=_rgb(a))
            d.rounded_rectangle([sx, y + 118, sx + sw, y + 150], radius=8, fill=_rgb(ti))
            d.text((sx + 12, y + 123), SLOTS[i], fill=_rgb(tx), font=small)
        out.paste(im, (x, y + lab - 30))
    out.save(path)


def main():
    os.makedirs(OUT, exist_ok=True)
    from playwright.sync_api import sync_playwright
    shots = []
    with sync_playwright() as p:
        br = launch(p)
        pg = br.new_page(viewport={"width": 816, "height": 1056}, device_scale_factor=1)
        for c in CANDIDATES:
            pal = palette(c)
            bloom = f"bloom_{c['key']}.png"
            bake_bloom(c, os.path.join(OUT, bloom))
            html = os.path.join(OUT, f"cand_{c['key']}.html")
            doc = page_html(c, pal, bloom)
            check_urls(doc, OUT)
            open(html, "w", encoding="utf-8").write(doc)
            pg.goto("file:///" + html.replace(os.sep, "/"))
            pg.wait_for_timeout(600)
            png = os.path.join(OUT, f"cand_{c['key']}.png")
            pg.locator("section.page").screenshot(path=png)
            shots.append(png)
            worst = min(contrast(tx, b) for _, ti, tx in pal for b in ("#FFFFFF", c["field"], c["bg"], ti))
            print(c["key"], c["name"], "accents", [t[0] for t in pal], "text", [t[2] for t in pal],
                  f"min contrast {worst:.2f}")
        br.close()
    sheet(shots, os.path.join(OUT, "candidates.png"))
    print("->", os.path.join(OUT, "candidates.png"))


if __name__ == "__main__":
    main()
