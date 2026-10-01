# -*- coding: utf-8 -*-
"""상품 4 5-1 기획서 대조 (v0.10~ 디자인 시안 판) -- 원고의 문구가 **있어야 할 쪽에** 들어갔나.

    python scripts/p4/check_plan_p4.py v0.10

v0.10 은 시안 HTML 을 틀로 쓴다. 시안이 문구를 빼거나 바꿨으면 check_v2_p4 의 "원고 밖 문구" 는 바뀐 글자만 잡고,
빠진 문구는 못 잡는다 -- 그래서 반대 방향(원고 -> 쪽)을 잰다.
  1 쪽별 문구: p4_content.all_texts() 의 문구마다 그 쪽(들)의 글자에 있나 (대소문자·줄바꿈 무시)
  2 공용 라벨(LABELS·섹션 이름 등)은 판 어딘가에 있나 -- 없는 것은 목록만 낸다(원고에 남은 옛 라벨일 수 있다)
  3 페이지 순서: 판의 쪽 key 순서 = pages_p4.specs() (기획서 페이지 지도는 check_docs_p4 가 specs 와 대조)
  4 인쇄된 숫자(5-4): 목차의 쪽 번호 = 그 줄 링크가 가는 쪽 (5쪽은 번호가 링크 안, 10·29·91쪽은 같은 높이의 줄 링크,
    38쪽 Weeks 칸은 주 번호) /
    1쪽 표지 알약 = 섹션 첫 쪽 번호 (6 · 10 · 29 · 91). v0.9~v0.10 첫 판은 섹션 쪽 수(4 · 19 · 62 · 18)였는데 구매자 역할 3명이
    쪽 번호로 읽어 10-01 사용자 결정으로 다른 목차와 같은 뜻으로 바꿈
  5 판 글자의 금지 표현(5-4): 원고 검사(p4_content.check)는 원고만 본다 -- 시안에 박힌 글자까지 완성 판에서 다시.
    BANNED(실패·의학 표현) · FIRST_PERSON(1인칭 당사자) · UK(영국식) -- 허용은 원고와 같은 ALLOWED_BANNED 만
  6 써 보기 뒤 더한 것(10-01 사용자): 39~90쪽 Wins "this week" · "WEEK OF" 칸 / 7~9쪽 "FROM THE ENERGY MENU" 에 그 배터리
    할 일이 원고(ENERGY)와 같은 목록 · 같은 목적지 / 방 카드 9장 "← Energy menu" -> 6쪽
의도한 차이(사용자 확정)는 ALLOW 에 이유와 함께.
"""
import html as H
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import p4_content as C  # noqa: E402
import pages_p4  # noqa: E402

ALLOW = {
    # 문구: 이유
    "no penalty, just the next slot": "39~90쪽 힌트를 'no penalty' 로 줄임 (10-01 사용자, 카드 넘침)",
    "How much is left": "98쪽 Restock 머리 -- 시안 README 9절이 남은 양을 Full / Half / Low 체크 칸으로 정했다"
                        "(기획서 '남은 양 칸 + 살 것' 은 그대로)",
}


def norm(s):
    # 시안은 "제목 · 설명" 을 대문자 라벨 한 줄로 묶기도 한다(7~9쪽 "TODAY I'LL DO · PICK THREE AT MOST") -- · 는 띄어쓰기로
    return re.sub(r"\s+", " ", H.unescape(s).replace("’", "'").replace(" · ", " ")).strip().lower()


def page_texts(html):
    out = {}
    for m in re.finditer(r'<section class="page" id="([^"]+)"[^>]*>(.*?)</section>', html, re.S):
        body = re.sub(r"<br\s*/?>", " ", m.group(2))
        parts = [p for p in re.split(r"<[^>]+>", body) if p.strip()]
        out[m.group(1)] = (norm(" ".join(parts)), [norm(p) for p in parts])
    return out


def where_pages(where, ids):
    rooms = [r[0] for r in C.ROOMS]
    if where in ids:
        return [where]
    table = {"day": [i for i in ids if i.startswith("day-")],
             "deep": [i for i in ids if i.startswith("deep-")],
             "week": [i for i in ids if re.fullmatch(r"w\d+", i)],
             "notes-blank": [i for i in ids if i.startswith("notes-blank")],
             "loop": ["laundry-loop", "dishes-loop"]}
    if where in table:
        return table[where]
    if where in rooms:
        return [where]
    return None         # 공용 라벨 -- 판 어디든


def found(text, pages, T):
    t = norm(text)
    if "{n}" in t:
        return all(norm(text.replace("{n}", k[1:])) in T[k][0] for k in pages)
    for k in pages:
        whole, parts = T[k]
        if t in whole:
            continue
        # "제목 설명" 묶음(순서도 칸·단계 카드)은 두 요소로 나뉘어 있다 -- 앞뒤 조각이 모두 그 쪽에 있으면 같은 것
        if not any(t.startswith(p + " ") and t[len(p) + 1:] in whole for p in parts if p):
            return False
    return True


def main(ver):
    src = os.path.join(ROOT, "src", f"p4_home-reset_{ver}_full_color.html")
    html = open(src, encoding="utf-8").read()
    T = page_texts(html)
    ids = list(T)
    fails, unused = [], []
    alldoc = " ".join(w for w, _ in T.values())

    # 3
    order = [k for k, _, _ in pages_p4.specs()]
    if ids != order:
        fails.append(f"쪽 순서가 specs 와 다름: 처음 다른 곳 {next(i for i, (a, b) in enumerate(zip(ids, order)) if a != b) + 1}쪽")

    # 1 · 2 (방 카드는 깊은 청소 목록이 짝 쪽에 있다 -- 따로 본다)
    items = []
    for key, name, steps, done, tools, deep in C.ROOMS:
        items += [(key, x) for x in [name, done] + list(steps) + list(tools)] + [("deep-" + key, d) for d in deep]
    skip = {(r[0], t) for r in C.ROOMS for t in [r[1], r[3]] + list(r[2]) + list(r[4]) + list(r[5])}
    # all_texts 의 "어디" 가 여러 쪽을 묶은 것은 쪽별로 푼다
    for b, (t, sub) in C.DAY_PAGES.items():
        items += [("day-" + b, t), ("day-" + b, sub)]
        skip |= {("day", t), ("day", sub)}
    for k, pairs in (("laundry-loop", C.LAUNDRY_LOOP), ("dishes-loop", C.DISHES_LOOP)):
        items += [(k, f"{a} {b}") for a, b in pairs]
        skip |= {("loop", f"{a} {b}") for a, b in pairs}
    for w, t in C.all_texts():
        if "{room}" in t:
            items += [("deep-" + r[0], t.replace("{room}", r[1])) for r in C.ROOMS] + [("deep-myroom", t.replace("{room}", C.MY_ROOM[1]))]
            skip.add((w, t))
        if w == "daily" and t in C.DAILY_RESET:          # "Morning (5 min)" -> 시안은 "Morning" / "5 min" 두 요소
            items += [("daily", x.strip(" ()")) for x in re.split(r"[()]", t) if x.strip(" ()")]
            skip.add((w, t))
    items += [(w, t) for w, t in C.all_texts() if (w, t) not in skip]
    seen = set()
    for where, text in items:
        if not text or (where, text) in seen:
            continue
        seen.add((where, text))
        if norm(text) in {norm(a) for a in ALLOW}:
            continue
        pages = where_pages(where, ids)
        if pages is None:
            if norm(text) not in alldoc:
                unused.append((where, text))
            continue
        if not found(text, pages, T):
            miss = [k for k in pages if not found(text, [k], T)]
            fails.append(f"{where}: \"{text}\" -- 없는 쪽 {[ids.index(k) + 1 for k in miss][:6]}")

    # 4
    secs = {m.group(1): m.group(2) for m in re.finditer(r'<section class="page" id="([^"]+)"[^>]*>(.*?)</section>', html, re.S)}
    nums = 0
    for k, body in secs.items():
        if k == "cover":
            continue
        for href, inner in re.findall(r'<a href="#([^"]+)"[^>]*>(.*?)</a>', body, re.S):   # 번호가 링크 안 (5쪽)
            for t in re.findall(r">\s*(\d{1,3})\s*<", ">" + inner + "<"):
                nums += 1
                want = int(href[1:]) if "WEEK" in inner and re.fullmatch(r"w\d+", href) else ids.index(href) + 1 if href in ids else None
                if want is not None and int(t) != want:          # 38쪽 Weeks 칸 "WEEK n" 은 주 번호
                    fails.append(f"{ids.index(k) + 1} {k}: 번호 {t} 인데 링크는 {href} ({want})")
        tops = {}
        for href, top in re.findall(r'<a href="#([^"]+)" style="position:absolute;left:[\d.]+px;top:([\d.]+)px', body):
            tops.setdefault(top, []).append(href)
        for top, t in re.findall(r'<div style="position:absolute;left:[\d.]+px;top:([\d.]+)px;[^"]*">(\d{1,3})</div>', body):
            if top in tops:                                                          # 같은 줄(10·29·91쪽 표)
                nums += 1
                dest = [ids.index(h) + 1 for h in tops[top] if h in ids and not h.startswith("deep-")]
                if dest and int(t) not in dest:
                    fails.append(f"{ids.index(k) + 1} {k}: 번호 {t} 인데 그 줄 링크는 {dest}쪽")
    want = [ids.index(s) + 1 for s in ("energy", "rooms", "routines", "tools")]     # 섹션 첫 쪽 번호 (10-01 사용자)
    pills = [int(x) for x in re.findall(r'border-radius:9px;[^"]*">(\d{1,3})</span></a>', secs["cover"])]
    if pills != want:
        fails.append(f"1 cover: 목차 알약 {pills} != 섹션 첫 쪽 {want}")
    print(f"  인쇄된 번호 {nums}개 대조 · 표지 알약 {pills}")
    # 5
    for k, body in secs.items():
        plain = H.unescape(" ".join(p for p in re.split(r"<[^>]+>", re.sub(r"<br\s*/?>", " ", body)) if p.strip()))
        for name, rx in (("금지 표현", C.BANNED), ("1인칭 당사자", C.FIRST_PERSON), ("영국식", C.UK)):
            for m in rx.finditer(plain):
                if name == "금지 표현" and any(m.group(0) in a for a in C.ALLOWED_BANNED) and                         any(a in re.sub(r"\s+", " ", plain) for a in C.ALLOWED_BANNED):
                    continue
                fails.append(f"{ids.index(k) + 1} {k}: {name} \"{m.group(0)}\"")

    # 6
    for k, body in secs.items():
        n = ids.index(k) + 1
        if re.fullmatch(r"w\d+", k):
            if f'>Wins</span><span style="font-size:8.5px;color:#66716B">{C.LABELS["wins_hint"]}</span>' not in body:
                fails.append(f"{n} {k}: Wins 옆 '{C.LABELS['wins_hint']}' 없음")
            if f'>{C.LABELS["week_of"].upper()}</span><div style="flex:1;box-sizing:border-box;height:22px;border-bottom:' not in body:
                fails.append(f"{n} {k}: 날짜 칸(WEEK OF) 없음")
        elif k.startswith("day-"):
            b_ = k[4:]
            i = body.find(f'>{C.LABELS["from_menu"].upper()}<')
            got = re.findall(r'<a href="#([^"]+)">([^<]+)</a>', body[i:]) if i >= 0 else []
            want = [(tg, H.escape(t)) for m in C.MINUTES for t, tg in C.ENERGY.get((b_, m), [])]
            if got != want:
                fails.append(f"{n} {k}: 할 일 목록이 원고와 다름 ({len(got)} / {len(want)})")
        elif k in {r[0] for r in C.ROOMS} | {C.MY_ROOM[0]}:
            if not re.search(r'<a href="#energy" style="position:absolute;left:84px;top:754px;[^"]*">.*?Energy menu</a>', body, re.S):
                fails.append(f"{n} {k}: '← Energy menu' 없음")

    print(f"상품 4 기획서 대조 {ver} -- 문구 {len(seen)}개, 쪽 {len(ids)}")
    if unused:
        print(f"  (참고) 판 어디에도 안 쓰인 공용 라벨 {len(unused)}: " + "; ".join(f"{w}:{t}" for w, t in unused))
    for a, why in ALLOW.items():
        print(f"  (예외) \"{a}\" -- {why}")
    print("FAIL:" if fails else "검사 통과 (FAIL 0)")
    for f in fails:
        print("  ", f)
    return len(fails)


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1] if len(sys.argv) > 1 else "v0.10") else 0)
