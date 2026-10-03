# -*- coding: utf-8 -*-
"""상품 4 리스팅 사진 10장 검사 -- export_listing_p4.py 가 만든 폴더(JPG + _layout.json)를 판과 대조한다.

    python scripts/p4/check_listing_images_p4.py <폴더 이름, 예: design-final-v1.1> [판 v0.17]

  A 파일: 10장 · 이름 01_hero~10_files · 2000x2000 · JPG 1MB 이하
  B 잘림: 글자 잉크 260~1740 x 250~1750 (폰 4:5 · PC 4:3 검색 자르기 + 여백) -- 상자가 아니라 렌더 픽셀로 잰다
  C 글자 크기: 큰 제목 01 >= 170, 02~10 >= 150 · 그 밖 >= 30 (46px 기준은 사용자 예외로 30 -- design 인수인계 2절)
  D 금지 문구: 혼자 읽으면 거짓이 되는 말 (CLAUDE.md "오해할 만한 문구")
  E 숫자: 사진 속 109 pages · 31 tasks · 52 · Six tabs · Five small steps · Six steps · under 6 MB 를 판에서 센 값과

2026-10-03: design 최종판 v1.0 의 06 이 "Every page is one tap away"(거짓 -- 탭 한 번은 섹션까지, 106쪽 같은 곳은 두 번)
+ TOOLS 줄이 아래 1750 을 넘었다(1773~1865). v1.0 에서 둘 다 FAIL, v1.1 에서 PASS 를 확인하고 붙였다.
"""
import json
import os
import re
import sys

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
os.environ.setdefault("PLANNER_VERSION", "v8.20-undated")
import p4_content as C  # noqa: E402
import pages_p4  # noqa: E402

DIR = os.path.join(ROOT, "output", "prod4", "listing", sys.argv[1] if len(sys.argv) > 1 else "design-final-v1.1")
VER = sys.argv[2] if len(sys.argv) > 2 else "v0.17"
NAMES = ["01_hero", "02_energy", "03_rooms", "04_rescue", "05_flow", "06_tabs", "07_print", "08_weeks", "09_inside", "10_files"]
SAFE = (260, 250, 1740, 1750)
BANNED = [r"every page is one tap away", r"any page in one tap", r"no app to install", r"works (in|with) any (pdf )?(app|viewer|reader)",
          r"I have ADHD", r"for myself", r"as someone with"]

fails = []


def fail(m):
    fails.append(m)
    print("  FAIL", m)


def ink_box(im, t):
    """글자 상자 안에서 글자색에 가까운 픽셀의 범위 (그라데이션 글자는 None)"""
    m = re.findall(r"[\d.]+", t["color"])
    if len(m) > 3 and float(m[3]) == 0:
        return None
    c = tuple(int(float(v)) for v in m[:3])
    x0, y0 = max(int(t["x0"]) - 20, 0), max(int(t["y0"]) - 20, 0)
    x1, y1 = min(int(t["x1"]) + 20, 2000), min(int(t["y1"]) + 20, 2000)
    px = im.crop((x0, y0, x1, y1)).load()
    xs, ys = [], []
    for y in range(y1 - y0):
        for x in range(x1 - x0):
            p = px[x, y]
            if abs(p[0] - c[0]) + abs(p[1] - c[1]) + abs(p[2] - c[2]) < 60:
                xs.append(x); ys.append(y)
    return (x0 + min(xs), y0 + min(ys), x0 + max(xs), y0 + max(ys)) if xs else None


def main():
    L = json.load(open(os.path.join(DIR, "_layout.json"), encoding="utf-8"))
    print("A 파일")
    if sorted(L) != NAMES:
        fail(f"장 이름 {sorted(L)}")
    for n in NAMES:
        p = os.path.join(DIR, n + ".jpg")
        if not os.path.exists(p):
            fail(f"{n}.jpg 없음"); continue
        if Image.open(p).size != (2000, 2000):
            fail(f"{n} 크기 {Image.open(p).size}")
        if os.path.getsize(p) > 1_000_000:
            fail(f"{n} {os.path.getsize(p):,} B > 1MB")

    print("B 잘림 (렌더 픽셀) · C 글자 크기")
    for n in NAMES:
        im = Image.open(os.path.join(DIR, n + ".png")).convert("RGB")
        big = max(t["size"] for t in L[n]["text"])
        need = 170 if n == "01_hero" else 150
        if big < need:
            fail(f"{n} 큰 제목 {big}px < {need}")
        for t in L[n]["text"]:
            if t["size"] < 30:
                # 04 의 그림 위 작은 번호(쪽 위 자리 표시) 는 글자 대신 표시라 예외 -- 숫자 하나만
                if not re.fullmatch(r"\d", t["t"]):
                    fail(f"{n} '{t['t'][:30]}' {t['size']}px < 30")
            inside = t["x0"] >= SAFE[0] and t["y0"] >= SAFE[1] and t["x1"] <= SAFE[2] and t["y1"] <= SAFE[3]
            if inside:
                continue
            b = ink_box(im, t)
            if b is None:          # 그라데이션 글자(08 의 52) -- 상자 여백이 커서 상자로만 본다
                b = (t["x0"] + 0.05 * t["size"], t["y0"] + 0.25 * t["size"], t["x1"], t["y1"] - 0.2 * t["size"])
            if b[0] < SAFE[0] or b[1] < SAFE[1] or b[2] > SAFE[2] or b[3] > SAFE[3]:
                fail(f"{n} '{t['t'][:30]}' 잉크 {tuple(int(v) for v in b)} -- 안전 영역 {SAFE} 밖")

    print("D 금지 문구 · E 숫자")
    text = {n: " ".join(t["t"] for t in L[n]["text"]) for n in NAMES}
    for n, s in text.items():
        for b in BANNED:
            if re.search(b, s, re.I):
                fail(f"{n} 금지 문구 /{b}/: {s[:80]}")
    pdf = lambda tag: os.path.join(ROOT, "output", "prod4", "planner", VER, f"home-reset_{VER}_{tag}-FINAL.pdf")
    import pypdfium2 as pdfium
    with open(pdf("color"), "rb") as fh:
        npages = len(pdfium.PdfDocument(fh.read()))
    weeks = sum(1 for k, _, _ in pages_p4.specs() if re.fullmatch(r"w\d+", k))
    room_steps = {len(r[2]) if len(r) > 2 and isinstance(r[2], (list, tuple)) else None for r in C.ROOMS}
    n_tasks = sum(len(v) for v in C.ENERGY.values())      # ENERGY = (기운, 분) 칸 12개 -> 칸마다 할 일 목록
    facts = [(r"(\d+) pages", npages), (r"(\d+) tasks", n_tasks), (r"(\d+)\s+undated reset weeks", weeks),
             (r"\b52\b", weeks)]
    for n, s in text.items():
        for pat, val in facts:
            for m in re.finditer(pat, s):
                got = int(m.group(1)) if m.groups() else int(m.group(0))
                if got != val:
                    fail(f"{n} '{m.group(0)}' != 판 {val}")
    words = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7}
    m = re.search(r"(\w+) small steps", text["04_rescue"])
    if m and words.get(m.group(1).lower()) != len(C.RESCUE["steps"]):
        fail(f"04 '{m.group(0)}' != Rescue 단계 {len(C.RESCUE['steps'])}")
    m = re.search(r"(\w+) steps a room", text["03_rooms"])
    if m and room_steps != {words.get(m.group(1).lower())}:
        fail(f"03 '{m.group(0)}' != 방 카드 단계 수 {room_steps}")
    m = re.search(r"(\w+) tabs", text["06_tabs"], re.I)
    if m and words.get(m.group(1).lower()) != len(C.SECTION_NAMES):
        fail(f"06 '{m.group(0)}' != 탭 {len(C.SECTION_NAMES)}")
    m = re.search(r"under (\d+) MB", text["10_files"])
    if m:
        big = max(os.path.getsize(pdf(t)) for t in ("color", "BW")) / 1e6
        if big >= int(m.group(1)):
            fail(f"10 'under {m.group(1)} MB' 인데 판 {big:.2f} MB")

    print(f"\n리스팅 사진 {os.path.basename(DIR)} (판 {VER}): " + ("PASS" if not fails else f"FAIL {len(fails)}개"))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
