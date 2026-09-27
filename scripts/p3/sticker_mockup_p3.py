# -*- coding: utf-8 -*-
"""상품 3 스티커 실사용 모습 -- 태블릿 필기 앱에서 주간 페이지에 스티커를 붙인 화면(목업). Prod 3 방 소유.

    python scripts/p3/sticker_mockup_p3.py     # -> output/prod3/preview/sticker_mockup/<DRAFT>/

2026-09-27 사용자: "스티커를 Goodnotes 에서 실제로 쓴 듯한 이미지로 실사용에 문제 없는지." 리스팅 이미지 한 장으로도 쓸 수 있게 둔다.
앱 화면은 특정 앱 로고·상표 없이 일반적인 필기 앱 모양(위 막대 + 도구 막대 + 스티커 창)만 흉내 낸다.
스티커 크기는 페이지 글자·알약과 견준 실제 비율: 알약 스티커 높이 ≈ 페이지 알약(22px)의 1.6배.
"""
import pathlib
import re
import sys

import pymupdf
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[2]
DRAFT = "draft-v0.4"   # v0.4 = Top 3 체크 작게, 줄 위 오른쪽 끝에 (v0.3 은 라벨에 붙었다)
# v0.3   # v0.3 = Top 3 체크를 줄 끝 안쪽으로 (v0.2 는 탭 쪽으로 삐져나감)
# v0.2   # v0.2 = 창을 아래로(Top 3 보이게), 손가락 표시 뺌, 페이지 위 스티커 크게
PLANNER = "v0.22"
STICK = ROOT / "output/prod3/stickers/draft-v0.6/png"
OUT = ROOT / "output/prod3/preview/sticker_mockup" / DRAFT
if OUT.exists():
    raise SystemExit(f"{OUT} 는 이미 있다. 덮어쓰지 않는다 -- DRAFT 를 올릴 것.")
OUT.mkdir(parents=True)

W, H = 1536, 2048                       # 태블릿 세로 화면
BAR, TOOLS = 96, 84
UI_BG, UI_LINE, UI_ICON = (246, 246, 247), (222, 222, 226), (110, 110, 118)
html = (ROOT / f"src/prod3/planner/{PLANNER}/ADHD-Year-Planner-2027-mon.html").read_text(encoding="utf-8")
ids = re.findall(r'<section class="pg" id="([^"]+)"', html)
doc = pymupdf.open(ROOT / f"output/prod3/planner/{PLANNER}/ADHD-Year-Planner-2027-mon.pdf")
KEY = "w12"
pg = doc[ids.index(KEY)]
area_h = H - BAR - TOOLS
z = area_h / pg.rect.height                                   # 페이지를 화면 높이에 맞춘다
pm = pg.get_pixmap(matrix=pymupdf.Matrix(z, z))
page = Image.frombytes("RGB", (pm.width, pm.height), pm.samples).convert("RGBA")
px = lambda pt: int(round(pt * z))                            # PDF pt -> 화면 px


def sticker(rel, h_pt):
    im = Image.open(STICK / rel).convert("RGBA")
    h = px(h_pt)
    return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)


def put(rel, x_pt, y_pt, h_pt, rot=0):
    s = sticker(rel, h_pt)
    if rot:
        s = s.rotate(rot, resample=Image.BICUBIC, expand=True)
    page.alpha_composite(s, (px(x_pt), px(y_pt)))


# 주간 페이지 (2027 Week 12) 에 붙인 모습 -- 좌표는 PDF 글자 위치(pt) 기준
put("Experiments/helped_cyan.png", 318, 158, 50, rot=-6)          # Friday -- did it help? 옆
put("Small-wins/did-the-thing_paper.png", 96, 250, 26)              # MON -- 종이색 스티커 (흰 종이 위에서 보이는지)
put("Energy/low-battery-day_blush.png", 96, 384, 26)                # WED
put("Brain-weather/good_mist.png", 96, 516, 40)                     # FRI
put("Small-wins/tiny-step_blush.png", 150, 530, 24)
for y in (222, 247):                                                # TOP 3 첫 두 줄 끝의 작은 체크
    put("Mini/check_mist.png", 474, y, 15)

screen = Image.new("RGBA", (W, H), UI_BG)
d = ImageDraw.Draw(screen)
# 위 막대: 뒤로·제목·아이콘
d.rectangle((0, 0, W, BAR), fill=(250, 250, 251)); d.line((0, BAR, W, BAR), fill=UI_LINE, width=2)
f = ImageFont.truetype("arial.ttf", 30); fb = ImageFont.truetype("arialbd.ttf", 30); fs = ImageFont.truetype("arial.ttf", 24)
d.text((40, 30), "‹", fill=UI_ICON, font=ImageFont.truetype("arial.ttf", 44))
d.text((W // 2, BAR // 2), "ADHD-Year-Planner-2027-mon", fill=(40, 40, 46), font=fb, anchor="mm")
for i in range(4):
    cx = W - 60 - i * 70
    d.ellipse((cx - 16, BAR // 2 - 16, cx + 16, BAR // 2 + 16), outline=UI_ICON, width=3)
# 도구 막대: 펜·형광펜·지우개·올가미·스티커(선택됨)
d.rectangle((0, BAR, W, BAR + TOOLS), fill=UI_BG); d.line((0, BAR + TOOLS, W, BAR + TOOLS), fill=UI_LINE, width=2)
tools = ["pen", "hl", "eraser", "lasso", "shape", "sticker", "text"]
for i, t in enumerate(tools):
    cx, cy = W // 2 - 300 + i * 100, BAR + TOOLS // 2
    if t == "sticker":
        d.rounded_rectangle((cx - 34, cy - 30, cx + 34, cy + 30), 14, fill=(214, 232, 240))
    if t == "pen":
        d.line((cx - 16, cy + 16, cx + 16, cy - 16), fill=(32, 30, 29), width=8)
    elif t == "hl":
        d.line((cx - 16, cy + 16, cx + 16, cy - 16), fill=(237, 187, 0), width=12)
    elif t == "eraser":
        d.rounded_rectangle((cx - 18, cy - 12, cx + 18, cy + 12), 5, outline=UI_ICON, width=4)
    elif t == "lasso":
        d.ellipse((cx - 18, cy - 14, cx + 18, cy + 12), outline=UI_ICON, width=4)
    elif t == "shape":
        d.rectangle((cx - 15, cy - 15, cx + 15, cy + 15), outline=UI_ICON, width=4)
    elif t == "sticker":
        d.rounded_rectangle((cx - 17, cy - 17, cx + 17, cy + 17), 6, outline=(0, 103, 134), width=4)
        d.line((cx + 5, cy + 17, cx + 17, cy + 5), fill=(0, 103, 134), width=4)
    else:
        d.text((cx, cy), "T", fill=UI_ICON, font=ImageFont.truetype("arialbd.ttf", 34), anchor="mm")
# 페이지
ox = (W - page.width) // 2
screen.alpha_composite(page, (ox, BAR + TOOLS))
# 스티커 창 (도구 막대의 스티커 버튼에서 내려온 창)
PW, PH = 560, 760
px0, py0 = W - PW - 40, BAR + TOOLS + px(420)
sh = Image.new("RGBA", (PW + 80, PH + 80), (0, 0, 0, 0))
ImageDraw.Draw(sh).rounded_rectangle((40, 46, PW + 40, PH + 46), 26, fill=(0, 0, 0, 70))
screen.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)), (px0 - 40, py0 - 40))
pop = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
pd = ImageDraw.Draw(pop)
pd.rounded_rectangle((0, 0, PW - 1, PH - 1), 26, fill=(252, 252, 253), outline=UI_LINE, width=2)
pd.text((28, 26), "Stickers", fill=(30, 30, 34), font=fb)
pd.text((28, 70), "The ADHD Year · Experiments", fill=(90, 90, 98), font=fs)
cells = ["Experiments/helped_cyan.png", "Experiments/helped_paper.png", "Experiments/sort-of_stone.png",
         "Experiments/not-for-me_ink.png", "Brain-weather/good_mist.png", "Brain-weather/rough_paper.png",
         "Mini/check_paper.png", "Mini/cross_blush.png", "Energy/bat2_cyan.png"]
for i, rel in enumerate(cells):
    p = STICK / rel
    if not p.exists():
        cand = sorted(p.parent.glob(p.stem.split("_")[0] + "_*.png"))
        p = cand[0] if cand else None
    if p is None:
        continue
    im = Image.open(p).convert("RGBA"); im.thumbnail((140, 140), Image.LANCZOS)
    cx, cy = 28 + (i % 3) * 172 + 80, 130 + (i // 3) * 180 + 80
    pop.alpha_composite(im, (cx - im.width // 2, cy - im.height // 2))
# 아래 줄: 컬렉션 탭
tabs = ["Experiments", "Brain weather", "Energy", "Small wins"]
x = 24
for i, t in enumerate(tabs):
    tw = pd.textlength(t, font=fs) + 32
    pd.rounded_rectangle((x, PH - 70, x + tw, PH - 26), 22, fill=(0, 103, 134) if i == 0 else (236, 236, 240))
    pd.text((x + tw / 2, PH - 48), t, fill=(255, 255, 255) if i == 0 else (70, 70, 78), font=fs, anchor="mm")
    x += tw + 12
screen.alpha_composite(pop, (px0, py0))
out = OUT / f"sticker_in_use_{KEY}.png"
screen.convert("RGB").save(out, quality=95)
print(out, screen.size, "page", ids.index(KEY) + 1)
