# -*- coding: utf-8 -*-
"""상품 4 써 보기 도구 (PROCESS.md 6단계) -- 구매자 역할 에이전트가 완성 PDF 를 "보고 누른다".

    python scripts/p4/tap_p4.py show 6                 # 6쪽을 그림으로 -> 그림 경로 출력 (좌표: 그림 픽셀 = pt x 2)
    python scripts/p4/tap_p4.py tap 6 160 470          # 6쪽 그림의 (160, 470) 픽셀을 손가락으로 누른다 -> 넘어간 쪽 또는 "아무 일 없음"
    python scripts/p4/tap_p4.py next 6 / prev 6        # 쪽 넘기기
    python scripts/p4/tap_p4.py --bw ...               # 흑백 인쇄판

링크 목록은 일부러 보여 주지 않는다 -- 구매자는 그림만 보고 "여기 누르면 가겠지" 하고 누른다. 그 기대가 틀린 곳이 찾을 것이다.
손가락 오차: 누른 점에서 6pt(그림 12픽셀) 안의 링크까지 잡는다(iPad 에서 손끝이 그 정도 넓다).
그림은 임시 폴더(%TEMP%/p4_tap/)에 쓴다 -- 프로젝트 폴더에는 아무것도 만들지 않는다.
"""
import os
import re
import sys
import tempfile

import pymupdf

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VER = os.environ.get("P4_VER", "v0.17")
SCALE = 2
FINGER = 6

args = sys.argv[1:]
tag = "BW" if "--bw" in args else "color"
args = [a for a in args if a != "--bw"]
pdf = os.path.join(ROOT, "output", "prod4", "planner", VER, f"home-reset_{VER}_{tag}-FINAL.pdf")
doc = pymupdf.open(pdf)
src = os.path.join(ROOT, "src", f"p4_home-reset_{VER}_full_{tag}.html")
names = re.findall(r'<section class="page" id="([^"]+)"', open(src, encoding="utf-8").read())
out_dir = os.path.join(tempfile.gettempdir(), "p4_tap")
os.makedirs(out_dir, exist_ok=True)


def show(n):
    path = os.path.join(out_dir, f"{tag}_p{n:03d}.png")
    if not os.path.exists(path) or os.path.getmtime(path) < os.path.getmtime(pdf):
        doc[n - 1].get_pixmap(matrix=pymupdf.Matrix(SCALE, SCALE)).save(path)
    print(f"{n}쪽 / {len(doc)} ({names[n - 1]}) -> 그림: {path}  (1224x1584 픽셀)")


def tap(n, x, y):
    px, py = x / SCALE, y / SCALE
    best = None
    for l in doc[n - 1].get_links():
        r = l["from"]
        dx = max(r.x0 - px, 0, px - r.x1)
        dy = max(r.y0 - py, 0, py - r.y1)
        d = (dx * dx + dy * dy) ** .5
        if d <= FINGER and (best is None or d < best[0]):
            best = (d, l)
    if best is None:
        print(f"{n}쪽 ({x}, {y}) 을 눌렀다 -> 아무 일 없음 (링크가 아니다)")
        return
    dest = best[1]["page"] + 1
    print(f"{n}쪽 ({x}, {y}) 을 눌렀다 -> {dest}쪽 ({names[dest - 1]}) 로 넘어감")
    show(dest)


cmd = args[0] if args else ""
if cmd == "show":
    show(int(args[1]))
elif cmd == "tap":
    tap(int(args[1]), float(args[2]), float(args[3]))
elif cmd in ("next", "prev"):
    n = int(args[1]) + (1 if cmd == "next" else -1)
    if 1 <= n <= len(doc):
        show(n)
    else:
        print("더 넘길 쪽이 없다")
else:
    print(__doc__)
