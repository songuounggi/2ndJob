# -*- coding: utf-8 -*-
"""상품 4 직접 써 보기 (PROCESS.md 6단계) -- 완성 PDF 에서 구매자처럼 링크를 눌러 따라간다.

    python scripts/p4/dogfood_p4.py v0.8

글자가 적힌 링크를 "누르고"(링크 상자 안 글자로 고른다) 도착한 쪽이 기대한 곳인지 본다. 탭(왼쪽 레일)은 이름으로 누른다.
막히는 곳 = 기대한 링크가 그 쪽에 없다 -> 쪽 번호로 적는다. 상품 3 dogfood_p3.py 와 같은 방식.
시나리오: PROCESS.md 6절 공통 3 + product4-content.md 6절 상품별 6.
"""
import os
import re
import sys

import pymupdf

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VER = sys.argv[1] if len(sys.argv) > 1 else "v0.8"
V2 = os.path.join(ROOT, "src", f"p4_home-reset_{VER}_full_color.html")       # v0.10~ 디자인 시안 틀(build_v2_p4)
html = open(V2 if os.path.exists(V2) else os.path.join(ROOT, "src", f"p4_home-reset_{VER}_color.html"),
            encoding="utf-8").read()
ids = re.findall(r'<section class="page" id="([^"]+)"', html)
if os.path.exists(V2):     # 켜진 탭 = 세로 글자 중 굵기 800
    ON = [(re.findall(r'writing-mode:vertical-rl;[^"]*font-weight:800;[^"]*">([A-Z]+)<', m.group(1)) or [None])[0]
          for m in re.finditer(r'<section class="page" id="[^"]+">(.*?)</section>', html, re.S)]
else:
    ON = [(re.findall(r'<a class="on"[^>]*><i[^>]*></i><span>([A-Z]+)</span>', m.group(0)) or [None])[0]
          for m in re.finditer(r'<section class="page" id="[^"]+".*?</nav>', html, re.S)]
doc = pymupdf.open(os.path.join(ROOT, "output", "prod4", "planner", VER, f"home-reset_{VER}_color-FINAL.pdf"))
P = {k: i for i, k in enumerate(ids)}          # key -> 0부터 쪽
stuck = []


def links(p):
    pg, words, out = doc[p], doc[p].get_text("words"), []
    for l in pg.get_links():
        if l.get("page", -1) < 0:
            continue
        r = l["from"]
        t = " ".join(w[4] for w in words if r.contains(pymupdf.Point((w[0] + w[2]) / 2, (w[1] + w[3]) / 2)))
        # 두 줄로 감긴 링크는 줄마다 상자가 따로 생긴다(6쪽 "Clear the" / "nightstand") -- 바로 아래 붙은 같은 목적지면 한 링크
        if out and out[-1][1] == l["page"] and abs(out[-1][2].y1 - r.y0) < 2 and abs(out[-1][2].x0 - r.x0) < 2:
            out[-1] = (out[-1][0] + " " + t, l["page"], out[-1][2] | r)
        else:
            out.append((t, l["page"], r))
    return [(t, d) for t, d, _ in out]


# v0.10~ 탭 레일 글자는 세로(회전)라 PDF 에서 글자로 못 고른다 -- 레일 자리(x<60)·SOS 배지 자리(오른쪽 위) 링크를 목적지로 고른다
RAIL = {"HOME": "index", "ENERGY": "energy", "ROOMS": "rooms", "ROUTINES": "routines", "WEEKS": "weeks",
        "TOOLS": "tools", "SOS": "rescue"}


def tap(p, label):
    for t, dest in links(p):
        if label.lower() in t.lower():
            return dest
    # 글자 끝 → 만 링크인 줄(94쪽 방 이름 줄 · 92쪽 2·3단계, 10-01): 그 글자와 같은 줄, 오른쪽에 있는 링크
    words = doc[p].get_text("words")
    hit = [w for w in words if w[4].lower().startswith(label.lower().split()[0])]
    for w in hit:
        cy = (w[1] + w[3]) / 2
        same = [l for l in doc[p].get_links() if l.get("page", -1) >= 0 and l["from"].y0 - 2 <= cy <= l["from"].y1 + 2
                and l["from"].x0 > w[2] and l["from"].x0 - w[2] < 200]
        if same:
            return min(same, key=lambda l: l["from"].x0)["page"]
    if label in RAIL and os.path.exists(V2):
        for l in doc[p].get_links():
            r = l["from"]
            spot = r.x1 < 60 if label != "SOS" else (r.x0 > 530 and r.y1 < 60)
            if spot and l.get("page", -1) == P[RAIL[label]]:
                return l["page"]
    return None


def run(name, start, steps):
    """steps: [(누를 글자, 기대 key)]. 막히면 적고 그 시나리오를 멈춘다"""
    p, path = P[start], [f"{P[start] + 1} {start}"]
    for label, expect in steps:
        dest = tap(p, label)
        if dest is None:
            stuck.append((name, p + 1, ids[p], f'"{label}" 링크 없음 (가려던 곳: {expect})'))
            print(f"  ✗ {name}: {p + 1}쪽 {ids[p]} 에서 \"{label}\" 을 누를 수 없다 -> {expect}")
            return
        if ids[dest] != expect:
            stuck.append((name, p + 1, ids[p], f'"{label}" -> {ids[dest]} (기대 {expect})'))
            print(f"  ✗ {name}: \"{label}\" 이 {ids[dest]} 로 갔다 (기대 {expect})")
            return
        p = dest
        path.append(f"{p + 1} {ids[p]}")
    print(f"  ✓ {name}: " + " → ".join(path))


# v0.10~ 시안: 3쪽 단계·4쪽 방 타일은 "Go →" 알약이 링크다(첫 Go = 첫 단계 Energy / 첫 타일 Kitchen). v0.9 는 글자가 링크
GO_START = "Go" if os.path.exists(V2) else "Check your battery"
GO_TILE = "Go" if os.path.exists(V2) else "Kitchen"

print(f"상품 4 {VER} 써 보기 -- {len(ids)}쪽\n")
print("[공통]")
run("1 처음 연 사람", "cover", [("The ADHD", "flow"), ("Open the planner", "start"), (GO_START, "energy"),
                             ("TOOLS", "tools"), ("Rescue mode", "rescue")])
# 2 넘기기만: 쪽을 넘기며 켜진 탭이 HOME -> ENERGY -> ROOMS -> ROUTINES -> WEEKS -> TOOLS 순으로 흐르나
order = ["HOME", "ENERGY", "ROOMS", "ROUTINES", "WEEKS", "TOOLS"]
seq = [o for o in ON]
back = [(i + 1, ids[i], seq[i - 1], seq[i]) for i in range(1, len(seq))
        if seq[i] and seq[i - 1] and order.index(seq[i]) < order.index(seq[i - 1])]
none = [(i + 1, ids[i]) for i, s in enumerate(seq) if not s and ids[i] != "cover"]
if back or none:
    stuck.append(("2 넘기기만", 0, "", f"탭이 거꾸로 {back} / 꺼짐 {none}"))
    print(f"  ✗ 2 넘기기만: 거꾸로 {back}, 꺼짐 {none}")
else:
    runs = [s for i, s in enumerate(seq) if s and (i == 0 or s != seq[i - 1])]
    print("  ✓ 2 넘기기만: " + " → ".join(runs))
bad_home = [k for k in ("w30", "deep-car", "restock", "seasonal", "kids-pets") if tap(P[k], "HOME") != P["index"]
            or tap(P[k], "SOS") != P["rescue"]]
if bad_home:
    stuck.append(("3 돌아오기", 0, "", f"HOME/SOS 가 안 되는 쪽 {bad_home}"))
    print(f"  ✗ 3 돌아오기: {bad_home}")
else:
    print(f"  ✓ 3 돌아오기: 아무 쪽(w30·deep-car·restock·seasonal·kids-pets)에서 HOME → {P['index'] + 1} Index, "
          f"SOS → {P['rescue'] + 1} Rescue")

print("\n[상품별 -- product4-content.md 6절]")
run("1 기운 없는 날", "cover", [("The ADHD", "flow"), ("Open the planner", "start"), (GO_START, "energy"),
                             ("Clear the nightstand", "bedroom"), ("HOME", "index")])
run("2 엉망일 때", "w10", [("SOS", "rescue"), ("15-minute sprint", "sprint"), ("Wins log", "wins")])
run("3 한 주", "rooms", [("WEEKS", "weeks"), ("7", "w7"), ("This week", "house-map"), (GO_TILE, "kitchen"),
                        ("Deep clean list", "deep-kitchen")])
run("3b 다음 주", "w7", [("Next week", "w8")])
run("4 빨래 산", "index", [("ROUTINES", "routines"), ("Laundry loop", "laundry-loop"), ("Wins log", "wins")])
run("5 손님 온다", "w20", [("SOS", "rescue"), ("Guests in 2 hours", "guests"), ("Entry", "entry")])
run("6 같이 산다", "index", [("ROUTINES", "routines"), ("Who does what", "who-does-what"), ("ROUTINES", "routines"),
                          ("Kids", "kids-pets"), ("ROUTINES", "routines"), ("Weekly rotation", "rotation")])
print("\n[빈틈 링크 -- 6단계에서 추가]")
run("Energy -> 그날 페이지", "energy", [("Low battery day", "day-Low")])   # 10-03: 줄 이름은 글자만, 길은 Today's pick 칸
run("Guests -> 방 카드", "guests", [("Bathroom", "bathroom")])
run("루프 -> Wins", "dishes-loop", [("Wins log", "wins")])

print(f"\n막힌 곳 {len(stuck)}개")
for s in stuck:
    print("  -", s)
