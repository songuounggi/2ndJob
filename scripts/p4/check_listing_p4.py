# -*- coding: utf-8 -*-
"""상품 4 리스팅 원고(listing-p4.md) <-> 완성 판 대조 (PROCESS.md 8단계 리스팅 검사, 5-4 수치·문구).

    python scripts/p4/check_listing_p4.py v0.9

제목: 15단어 이하·140자 이하·대문자 단어 3개 이하·같은 단어 반복 없음 (Etsy 2025 가을 지침, listing-p3.md)
태그: 13개·20자 이하·중복 없음·**기존 리스팅 태그와 겹침 수**를 보인다
설명: 쪽 수·개수·파일 크기·탭 이름·Rescue 단계·도구 목록이 판과 같은가 / 금지 표현(1인칭 당사자·의학·영국식)
파일명: 70자 이하, 영숫자와 . _ - 만 (shop.md 5-5)
"""
import os
import re
import sys

import pymupdf

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import p4_content as C  # noqa: E402

VER = sys.argv[1] if len(sys.argv) > 1 else "v0.9"
md = open(os.path.join(ROOT, "listing-p4.md"), encoding="utf-8").read()
blocks = re.findall(r"```\n(.*?)```", md, re.S)
title, tags, desc = blocks[0].strip(), blocks[1].split(), blocks[2]
tags = [t.strip() for t in blocks[1].strip().split("\n")]
fails = []


def need(ok, msg):
    if not ok:
        fails.append(msg)


# 제목
words = title.split()
need(len(words) <= 15, f"제목 {len(words)}단어 > 15")
need(len(title) <= 140, f"제목 {len(title)}자 > 140")
need(sum(w.strip(",").isupper() and len(w) > 1 for w in words) <= 3, "제목 대문자 단어 3개 초과")
core = [w.strip(",").lower() for w in words if w.strip(",").lower() not in ("and", "for", "the", "a")]
need(len(core) == len(set(core)), f"제목 같은 단어 반복 {[w for w in core if core.count(w) > 1]}")

# 태그
need(len(tags) == 13, f"태그 {len(tags)} != 13")
need(all(len(t) <= 20 for t in tags), f"20자 초과 태그 {[t for t in tags if len(t) > 20]}")
need(len(set(tags)) == len(tags), "태그 중복")
old = set()
for f in ("listing.md", "product2-listing.md", "listing-p3.md"):
    s = open(os.path.join(ROOT, f), encoding="utf-8").read()
    m = re.search(r"##\s*태그.*?```\n(.*?)```", s, re.S)
    if m:
        old |= {t.strip() for t in m.group(1).strip().split("\n")}
overlap = sorted(set(tags) & old)

# 판에서 뽑은 숫자
out = os.path.join(ROOT, "output", "prod4", "planner", VER)
pdfs = {t: os.path.join(out, f"home-reset_{VER}_{t}-FINAL.pdf") for t in ("color", "BW")}
pages = {t: len(pymupdf.open(p)) for t, p in pdfs.items()}
mb = {t: os.path.getsize(p) / 1e6 for t, p in pdfs.items()}
low = desc.lower()
need(all(n == pages["color"] for n in pages.values()), f"두 파일 쪽 수가 다름 {pages}")
need(f"{pages['color']} pages" in desc, f"설명 쪽 수 != 판 {pages['color']}")
need(f"{sum(len(v) for v in C.ENERGY.values())} tasks" in desc, "Energy 할 일 개수 불일치")
n_rooms = len(C.ROOMS) + 1
need({9: "nine"}.get(n_rooms, str(n_rooms)) + " rooms" in low, f"방 개수 불일치 ({n_rooms})")
need(all(len(r[2]) == 6 for r in C.ROOMS) and "six-step" in low, "방 카드 6단계 불일치")
need("52 undated reset weeks" in desc, "주간 52 불일치")
# 설명의 예시 "Low battery and five minutes? Load five dishes." 가 실제 Energy menu 칸에 있나 -- v0.10 까지 "Full ... twenty
# minutes? Clean out the fridge" 였는데 fridge 는 Medium x 20 칸이었다(써 보기 6단계, 리뷰어 구매자 역할이 찾음)
WORD_MIN = {"two": 2, "five": 5, "ten": 10, "twenty": 20}
examples = re.findall(r"(Low|Medium|Full) battery and (two|five|ten|twenty) minutes\? ([^.?]+)\.", desc)
need(examples, "설명에 배터리 예시 문장이 없음")
for bat, m, task in examples:
    cell = [t for t, _ in C.ENERGY.get((bat, WORD_MIN[m]), [])]
    need(task in cell, f"설명 예시 '{bat} x {m} min -> {task}' 가 Energy menu 칸 {cell} 에 없음")
tab_line = re.search(r"Six tabs run down the side of every page: (.*?)\.", desc)
need(tab_line and tab_line.group(1) == "Home, Energy, Rooms, Routines, Weeks, Tools", "탭 이름 불일치")
cap = re.search(r"Each file is under (\d+) MB", desc)
need(cap and max(mb.values()) < int(cap.group(1)), f"파일 크기 {mb} 가 설명의 상한을 넘거나 문장이 없음")
for a, _, _ in C.RESCUE["steps"]:
    need(a.lower() in low, f"Rescue 단계 '{a}' 가 설명에 없음")
tools = [C.SPRINT[0], C.GUESTS[0], C.DOOM_PILE[0], C.DECLUTTER[0], C.DOPAMINE[0]] + \
        [C.TOOL_PAGES[k][0] for k in ("where-things-live", "restock", "body-doubling", "wins", "guess-actual",
                                      "projects", "big-reset")]
need(not [t for t in tools if t.lower() not in low], f"도구가 설명에 없음 {[t for t in tools if t.lower() not in low]}")

# 금지 표현 -- 원칙을 말하는 줄("no streaks", "nothing to catch up on")만 허용
text = "\n".join([title, desc] + tags)
for line in text.split("\n"):
    ok_line = re.search(r"no streaks|nothing to catch up on", line, re.I)
    if C.BANNED.search(line) and not ok_line:
        fails.append(f"금지어: {line.strip()[:80]}")
    if C.FIRST_PERSON.search(line):
        fails.append(f"1인칭 당사자: {line.strip()[:80]}")
    if C.UK.search(line):
        fails.append(f"영국식 표기: {line.strip()[:80]}")

# 파일명
for name in re.findall(r"`(The-ADHD-[^`]+\.pdf)`", md):
    need(len(name) <= 70 and re.fullmatch(r"[A-Za-z0-9._-]+", name), f"파일명 규칙 위반 {name}")

print(f"상품 4 리스팅 원고 ↔ {VER}")
print(f"  제목 {len(words)}단어 {len(title)}자 · 태그 {len(tags)}개 (기존 리스팅과 겹침 {len(overlap)}개 {overlap})")
print(f"  판: {pages['color']}쪽, 컬러 {mb['color']:.1f}MB · 흑백 {mb['BW']:.1f}MB")
print("FAIL:\n  " + "\n  ".join(fails) if fails else "검사 통과 (FAIL 0)")
