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
  7 방 카드로 가는 길: 집 지도 · 방 목록 · 목차에 방 카드 10개 전부(v0.11 빈 방 둘째) -- 방 목록엔 깊은 청소도
  8 할 일이 그 쪽에 있다: Energy 할 일마다 목적지(방 카드 단계·Done enough·준비물 / 깊은 청소 목록)에 핵심 단어가 하나 이상
    (관사·방 이름 빼고). 루프로 가는 일은 빼고 본다(리스팅 "the loop it belongs to"). v0.11 재시험 리뷰어 "누른 쪽에 그 일이 없다"
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
    "no penalty, just the next slot": "Reset week 힌트를 'no penalty' 로 줄임 (10-01 사용자, 카드 넘침)",
    "How much is left": "Restock list 머리 -- 시안 README 9절이 남은 양을 Full / Half / Low 체크 칸으로 정했다"
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
            items += [("deep-" + r[0], t.replace("{room}", r[1])) for r in C.ROOMS] + [("deep-" + k, t.replace("{room}", n)) for k, n in C.MY_ROOMS]
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
                # 10쪽은 v0.18 부터 깊은 청소 번호 칸도 있다(10-03 A안) -- 어느 칸이 어느 번호인지는 15 에서 칸별로 잰다
                dest = [ids.index(h) + 1 for h in tops[top] if h in ids and (k == "rooms" or not h.startswith("deep-"))]
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
        for name, rx in (("금지 표현", C.BANNED), ("1인칭 당사자", C.FIRST_PERSON), ("영국식", C.UK), ("미국에서만", C.US_ONLY)):
            for m in rx.finditer(plain):
                if name == "금지 표현" and any(m.group(0) in a for a in C.ALLOWED_BANNED) and                         any(a in re.sub(r"\s+", " ", plain) for a in C.ALLOWED_BANNED):
                    continue
                fails.append(f"{ids.index(k) + 1} {k}: {name} \"{m.group(0)}\"")

    # 6
    for k, body in secs.items():
        n = ids.index(k) + 1
        if re.fullmatch(r"w\d+", k):
            # 10-02 S7: 이긴 것은 103쪽 한 곳 -- 주마다 쪽 Wins 칸은 쓰는 줄 없이 Wins log 링크
            win_txt = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", t)) for t in re.findall(r'<a href="#wins"[^>]*>(.*?)</a>', body, re.S)]
            if not any(pages_p4.title_of("wins") in t for t in win_txt) or 'left:108px;top:550px;width:194px"><div' in body:     # 옆 Slid 카드 줄(left 366)은 그대로
                fails.append(f"{n} {k}: Wins 칸이 Wins log 링크가 아님 (S7 -- 같은 기록 두 곳)")
            if f'>{C.LABELS["week_of"].upper()}</span><div style="flex:1;box-sizing:border-box;height:22px;border-bottom:' not in body:
                fails.append(f"{n} {k}: 날짜 칸(WEEK OF) 없음")
        elif k.startswith("day-"):
            b_ = k[4:]
            i = body.find(f'>{C.LABELS["from_menu"].upper()}')        # 라벨 뒤에 " · TAP ONE" 이 붙는다(10-01 재시험)
            got = re.findall(r'<a href="#([^"]+)">([^<]+)</a>', body[i:]) if i >= 0 else []
            want = [(tg, H.escape(t)) for m in C.MINUTES for t, tg in C.ENERGY.get((b_, m), [])]
            if got != want:
                fails.append(f"{n} {k}: 할 일 목록이 원고와 다름 ({len(got)} / {len(want)})")
        elif k in {r[0] for r in C.ROOMS} | {kk for kk, _ in C.MY_ROOMS}:
            if not re.search(r'<a href="#energy" style="position:absolute;left:84px;top:754px;[^"]*">.*?Energy menu</a>', body, re.S):
                fails.append(f"{n} {k}: '← Energy menu' 없음")

    # 8 할 일이 그 쪽에 있다
    stop = {"the", "a", "an", "one", "and", "to", "of", "in", "out", "up", "by", "for", "or", "into", "on", "off", "your",
            "it", "its", "from", "with", "at", "all", "two", "five", "room", "rooms"}
    wd = lambda s: {w for w in re.findall(r"[a-z]+", s.lower()) if w not in stop}
    R = {r[0]: r for r in C.ROOMS}
    for (b_, m_), tasks in C.ENERGY.items():
        for t, tg in tasks:
            if tg.endswith("-loop"):
                continue
            room = tg[5:] if tg.startswith("deep-") else tg
            if room not in R:
                continue
            page_txt = " ".join(R[room][5]) if tg.startswith("deep-") else " ".join(R[room][2]) + " " + R[room][3] + " " + " ".join(R[room][4])
            if not (wd(t) - wd(R[room][1])) & wd(page_txt):
                fails.append(f"할 일 '{t}' ({b_} {m_}분) -> {tg}: 그 쪽에 이 일이 없음")

    # 7 방 카드로 가는 길 (v0.11 빈 방 둘째, 10-01 사용자): 집 지도 · 10쪽 방 목록 · 5쪽 목차에 방 카드 전부, 방 목록엔 깊은 청소도
    rooms_all = [r[0] for r in C.ROOMS] + [k for k, _ in C.MY_ROOMS]
    for k, need_keys in (("house-map", rooms_all), ("rooms", rooms_all + ["deep-" + r for r in rooms_all]), ("index", rooms_all)):
        if k in secs:
            miss = [x for x in need_keys if f'href="#{x}"' not in secs[k]]
            if miss:
                fails.append(f"{ids.index(k) + 1} {k}: 가는 링크 없음 {miss}")

    # 9 구조 논리 L2 (PROCESS.md 5-7, 10-02 사용자): 2쪽 순서도에서 같은 쪽으로 가는 상자 둘 금지 -- 원고와 완성 판 둘 다.
    #   옛 판(v0.12)은 질문 상자와 답 상자가 같은 쪽으로 가는 쌍이 셋(6쪽 · 94쪽 · 103쪽)이었다
    tg = [t for *_, t in C.FLOW["boxes"].values()]
    dup = sorted({t for t in tg if tg.count(t) > 1})
    if dup:
        fails.append(f"원고 FLOW: 같은 쪽으로 가는 상자 {dup}")
    if "flow" in secs:
        body = secs["flow"]
        hrefs = [h for h, left, inner in re.findall(r'<a href="#([^"]+)" style="position:absolute;left:([\d.]+)px[^>]*>(.*?)</a>', body, re.S)
                 if float(left) > 60 and re.sub(r"<[^>]+>", "", inner).strip() != C.SOS_LABEL]          # 왼쪽 탭(left 10)과 SOS 칩은 뺀다
        dup = sorted({ids.index(h) + 1 for h in hrefs if hrefs.count(h) > 1 and h in ids})
        if dup:
            fails.append(f"2 flow: 같은 쪽으로 가는 상자가 둘 이상 -- {', '.join(map(str, dup))}쪽 (구조 논리 L2)")

    # 10 구조 논리 L4 (10-02 사용자, S2): 순서도 "그 하나만 하고 멈춤 → Wins log" -- 방 카드 10장 · 배터리 날 3장에서 Wins log 로 가는 길
    for k in [r[0] for r in C.ROOMS] + [kk for kk, _ in C.MY_ROOMS] + ["day-" + b for b in C.BATTERIES]:
        if k in secs and not re.search(r'<a href="#wins"[^>]*>[^<]*' + re.escape(pages_p4.title_of("wins")), secs[k]):
            fails.append(f"{ids.index(k) + 1} {k}: Wins log 로 가는 알약 없음 (구조 논리 L4)")
    # 11 구조 논리 L1 (10-02 사용자, S1): 3쪽 카드는 둘 중 하나(기운 / 방) + 벅찬 날 갈래라 1 · 2 · 3 번호를 매기지 않는다
    if "start" in secs and re.search(r'justify-content:center">\d</span>', secs["start"]):
        fails.append(f"{ids.index('start') + 1} start: 카드에 번호(1, 2, 3) -- 차례가 아니라 갈림이다 (구조 논리 L1)")

    # 12 L11 · L5 (10-02 사용자): 3쪽 "Set up once" -- 빈 방 이름 · 짝 나누기는 그 쪽에 쓰게 링크로(같은 기록 두 곳 금지).
    #    미리 채운 표 문구가 제 쪽에 있는지는 1(all_texts 의 PREFILL)이 본다
    if "start" in secs:
        need_links = [k for k, _ in C.MY_ROOMS] + ["who-does-what"]
        miss = [k for k in need_links if f'href="#{k}"' not in secs["start"]]
        if miss:
            fails.append(f"{ids.index('start') + 1} start: Set up once 에서 가는 링크 없음 {miss} (L5 -- 그 쪽에 쓰게)")

    # 13 구조 논리 S5 · S6 · S10 · S13 (10-02 사용자) -- 같은 기록 · 같은 말 두 곳 금지, 한 장짜리 "오늘" 쪽 다시 쓰기 안내
    if "house-map" in secs and "LAST RESET" in secs["house-map"]:
        fails.append(f"{ids.index('house-map') + 1} house-map: LAST RESET 칸 -- 마지막 리셋은 방 카드에만 (S5)")
    deep_all = {t.lower() for r in C.ROOMS for t in r[5]}
    dup = sorted(t for t in C.MONTHLY + [x for v in C.SEASONAL.values() for x in v] if t.lower() in deep_all)
    if dup:
        fails.append(f"34 · 35쪽 할 일이 방 깊은 청소 목록과 같음 {dup} (S6)")
    for k in ["day-" + b for b in C.BATTERIES]:
        if k in secs and H.escape(C.LABELS["day_reuse"]) not in secs[k] and C.LABELS["day_reuse"] not in secs[k]:
            fails.append(f"{ids.index(k) + 1} {k}: 다시 쓰기 안내 없음 (S10)")
    # S13 은 10-03 사용자 결정으로 되돌림 -- 96쪽 배너는 강조 문장(쓰는 칸 아님), 빼니 휑했다. 이제는 있어야 한다
    if "guests" in secs and C.LABELS["hide"] not in H.unescape(secs["guests"]):
        fails.append(f"{ids.index('guests') + 1} guests: 아래 배너 '{C.LABELS['hide']}' 없음 (10-03 되살림)")

    # 14 재검수 R1~R5 (10-02 사용자, 처음부터 전수 재검수에서 -- R1·R2 는 그날 고치다 만든 모순)
    if "rotation" in secs and C.LABELS["slid"] in secs["rotation"]:
        fails.append(f"{ids.index('rotation') + 1} rotation: '{C.LABELS['slid']}' 칸 -- 33쪽은 계획 전용, 미룬 일은 주마다 쪽에만 (R1)")
    if "start" in secs and "DOABLE TODAY" in secs["start"]:
        fails.append(f"{ids.index('start') + 1} start: 'Doable today?' 라벨이 All too much? 카드까지 덮는다 (R2)")
    if "energy" in secs:
        e = secs["energy"]
        miss = [b for b in C.BATTERIES if f'href="#day-{b}"' not in e[e.find(C.LABELS["pick"]):]]
        if miss or 'left:108px;top:652px;width:452px"><div' in e:
            fails.append(f"{ids.index('energy') + 1} energy: Today's pick 이 쓰는 칸 -- 오늘 고른 일은 7~9쪽에만 (R3) {miss}")
    if "start" in secs:     # R5 줄 간격 -> 10-03 사용자 A안: 적는 칸 둘 + 옅은 칸 둘(My rooms 칸 안에 Room 1 · Room 2 링크)
        st = secs["start"]
        tile1 = re.search(r'<div class="setup-tile".*?</span></div>', st, re.S)
        ok = (st.count('class="setup-field"') == 2 and st.count('class="setup-line"') == 2      # 적는 칸마다 쓰는 줄 (10-03 사용자)
              and st.count('class="setup-tile"') == 2 and tile1
              and all(f'href="#{k}"' in tile1.group(0) for k, _ in C.MY_ROOMS) and '<a href="#who-does-what" class="setup-tile"' in st)
        if not ok:
            fails.append(f"{ids.index('start') + 1} start: Set up once 가 적는 칸 둘 + 옅은 칸 둘(Room 1 · Room 2 링크)이 아님 (10-03 A안)")

    # 15 빈 칸 채우기 (10-03 사용자 -- S5 · R3 로 쓰는 줄을 뺀 자리가 휑했다. 4쪽 B안 · 6쪽 A안)
    if "house-map" in secs:
        hm = H.unescape(secs["house-map"])
        miss = [r[1] for r in C.ROOMS if r[3] not in hm] + ([C.LABELS["my_rooms"]] if C.LABELS["my_rooms_done"] not in hm else [])
        icons = hm.count('class="hm-ic"')
        if miss or icons != len(C.ROOMS) + 1:
            fails.append(f"{ids.index('house-map') + 1} house-map: 타일에 방 그림 + Done enough 문장 없음 {miss} · 그림 {icons} (10-03 B안)")
    if "energy" in secs:
        e = H.unescape(secs["energy"])
        tiles = re.findall(r'<a href="#day-(\w+)" class="today-tile".*?</a>', e, re.S)
        bad = [b for b in C.BATTERIES if b not in tiles or C.DAY_PAGES[b][1] not in e]
        if bad:
            fails.append(f"{ids.index('energy') + 1} energy: Today's pick 배터리 날 칸(그림 + 쪽 이름 + 부제) 없음 {bad} (10-03 A안)")
    if "rotation" in secs:
        r = H.unescape(secs["rotation"])
        got = re.findall(r'<a href="#([\w-]+)" class="mini-tile"', r)
        if got != ["weeks", "house-map"] or C.LABELS["then_weeks"] not in r:
            fails.append(f"{ids.index('rotation') + 1} rotation: 아래 Then 카드(Weeks · House map 칸) 없음 {got} (10-03 A안)")
    if "rooms" in secs:     # 10쪽: 방 쪽 번호와 깊은 청소 쪽 번호가 각자 링크 옆에 (10-03 A안 -- PAGE 가 deep clean 옆이라 오해)
        r = secs["rooms"]
        bad = []
        for key in [x[0] for x in C.ROOMS] + [x[0] for x in C.MY_ROOMS]:
            top = re.search(r'<a href="#' + key + r'" style="position:absolute;left:108px;top:(\d+)px', r)
            if not top:
                bad.append(key); continue
            t = top.group(1)
            a = re.search(r'left:330px;top:' + t + r'px;[^"]*">(\d+)<', r)
            b = re.search(r'left:510px;top:' + t + r'px;[^"]*">(\d+)<', r)
            if not a or not b or int(a.group(1)) != ids.index(key) + 1 or int(b.group(1)) != ids.index("deep-" + key) + 1:
                bad.append(key)
        if bad or "M510,182" in r or "M410,182" not in r:
            fails.append(f"{ids.index('rooms') + 1} rooms: 번호 두 칸(방 쪽 · 깊은 청소 쪽)이 아님 {bad[:3]} · 4열 왼쪽 선 {'M510,182' in r} (10-03 A안)")
    # 흰 미니카드 그림자 그림(10-03): 흰 바탕 그림이라 미니카드보다 위로 올라가면 카드 머리글(Today's pick · Then · Wins)을 덮는다
    # (첫 빌드에서 실제로 덮었다). 그림 윗변 = 미니카드 윗변 - 4 이내
    for k, body in secs.items():
        tile_tops = [int(t) for t in re.findall(r'class="(?:today|mini|setup)-tile" style="(?:border:[^;]*;)?position:absolute;left:\d+px;top:(\d+)px', body)]
        for t in re.findall(r'class="tile-shadow" src="[^"]*" alt="" style="position:absolute;left:\d+px;top:(\d+)px', body):
            if not any(tt - 4 <= int(t) <= tt for tt in tile_tops):
                fails.append(f"{ids.index(k) + 1} {k}: 미니카드 그림자 그림이 미니카드 위로 올라가 머리글을 덮을 수 있다 (top {t}, 미니카드 {tile_tops})")
    # 그림자 그림이 바깥 카드 아래 모서리까지 닿으면 그 모서리가 둥글어야 한다 -- 네모 흰 바탕이 카드의 둥근 모서리를 덮었다(10-03 41쪽)
    for k, body in secs.items():
        cards = [tuple(int(v) for v in m) for m in re.findall(
            r'style="position:absolute;left:(\d+)px;top:(\d+)px;width:(\d+)px;height:(\d+)px;border-radius:16px;background:#FFFFFF', body)]
        for m in re.finditer(r'class="tile-shadow" src="[^"]*" alt="" style="position:absolute;left:(\d+)px;top:(\d+)px;width:(\d+)px;height:(\d+)px([^"]*)"', body):
            x, y, w, h = (int(v) for v in m.groups()[:4])
            rest = m.group(5)
            for cx, cy, cw, ch in cards:
                if cx <= x and x + w <= cx + cw and cy <= y and y + h <= cy + ch:
                    need = [s for s, hit in (("bottom-left", x == cx and y + h == cy + ch), ("bottom-right", x + w == cx + cw and y + h == cy + ch)) if hit]
                    miss = [s for s in need if f"border-{s}-radius:16px" not in rest]
                    if miss:
                        fails.append(f"{ids.index(k) + 1} {k}: 미니카드 그림자 그림이 카드 모서리({', '.join(miss)})를 네모로 덮는다")
    # 16 10-03 사용자 결정(오른쪽 창으로 보며 고름)
    # Q1 6쪽 줄 이름 Low / Medium / Full 은 글자만 -- 아래 Today's pick 칸이 같은 7~9쪽으로 간다(L2, 같은 곳으로 가는 것 둘)
    if "energy" in secs:
        e = secs["energy"]
        dup = re.findall(r'<a href="#day-(\w+)" style="position:absolute;left:84px;', e)
        if dup:
            fails.append(f"{ids.index('energy') + 1} energy: 줄 이름 {dup} 가 링크 -- Today's pick 칸과 같은 쪽으로 가는 것 둘 (L2, 10-03)")
    # Q2 Reset week 방 줄 수 = 33쪽 Weekly rotation 방 줄 수 (L7 -- 계획을 다 옮겨 적을 수 있게)
    def room_rows(body, x1):
        m = re.search(r'<path d="((?:M108,\d+ H' + str(x1) + r' )+)"', body)
        return len(re.findall(r"M108,", m.group(1))) if m else 0
    if "rotation" in secs:
        plan = room_rows(secs["rotation"], 242)          # 33쪽 방 이름 줄 (x 108~242)
        bad_w = [k for k in secs if re.fullmatch(r"w\d+", k) and room_rows(secs[k], 270) != plan]
        if not plan or bad_w:
            fails.append(f"Reset week 방 줄 수가 33쪽 Weekly rotation({plan}줄)과 다름 {bad_w[:3]} (L7, 10-03)")
    # Q3a 4쪽 My rooms 링크 = 다른 타일 Go 와 같은 아래 줄 (margin-top:auto)
    if "house-map" in secs and "align-self:flex-end;margin-top:auto;display:flex;gap:12px" not in secs["house-map"]:
        fails.append(f"{ids.index('house-map') + 1} house-map: My rooms 링크가 Go 와 같은 아래 줄이 아님 (10-03)")
    # Q3b 미니카드 둘레 여백 = 18pt (좌 · 우 · 아래), 3쪽 적는 칸도 같은 격자
    for k, body in secs.items():
        cards = [tuple(float(v) for v in m) for m in re.findall(
            r'style="position:absolute;left:([\d.]+)px;top:([\d.]+)px;width:([\d.]+)px;height:([\d.]+)px;border-radius:16px;background:#FFFFFF', body)]
        tiles = [tuple(float(v) for v in m) for m in re.findall(
            r'class="(?:today|mini|setup)-tile" style="(?:border:[^;]*;)?position:absolute;left:([\d.]+)px;top:([\d.]+)px;width:([\d.]+)px;height:([\d.]+)px', body)]
        tiles += [tuple(float(v) for v in m) for m in re.findall(
            r'class="setup-field" style="position:absolute;left:([\d.]+)px;top:([\d.]+)px;width:([\d.]+)px;height:([\d.]+)px', body)]
        for cx, cy, cw, ch in cards:
            inside = [t for t in tiles if cx <= t[0] and t[0] + t[2] <= cx + cw and cy <= t[1] and t[1] + t[3] <= cy + ch]
            if not inside:
                continue
            l = min(t[0] for t in inside) - cx
            r = cx + cw - max(t[0] + t[2] for t in inside)
            b = cy + ch - max(t[1] + t[3] for t in inside)
            if (round(l), round(r), round(b)) != (18, 18, 18):
                fails.append(f"{ids.index(k) + 1} {k}: 미니카드 둘레 여백 좌 {l:g} · 우 {r:g} · 아래 {b:g} != 18 (10-03)")
    # Q3c 흑백판 미니카드에 쪽 번호 = 그 링크가 가는 쪽
    bw_src = src.replace("_full_color.html", "_full_BW.html")
    if os.path.exists(bw_src):
        bw = open(bw_src, encoding="utf-8").read()
        for m in re.finditer(r'<a href="#([\w-]+)" class="(?:today|mini|setup)-tile" style="[^"]*">(<span class="bw-pno"[^>]*>p\.(\d+)</span>)?', bw):
            if not m.group(2) or int(m.group(3)) != ids.index(m.group(1)) + 1:
                fails.append(f"흑백판: 미니카드 {m.group(1)} 에 쪽 번호가 없거나 틀림 ({m.group(3)}) (10-03)")
                break
        for k in [kk for kk, _ in C.MY_ROOMS]:
            mm = re.search(rf'<a href="#{k}" style="white-space:nowrap">.*?p\.(\d+)</span></a>', bw, re.S)
            if not mm or int(mm.group(1)) != ids.index(k) + 1:
                fails.append(f"흑백판: 3쪽 {k} 링크에 쪽 번호가 없거나 틀림 (10-03)")
    wk = [k for k in secs if re.fullmatch(r"w\d+", k)]
    nowin = [k for k in wk if 'href="#wins" class="mini-tile"' not in secs[k] or C.LABELS["wins_tile"] not in H.unescape(secs[k])]
    if nowin:
        fails.append(f"Reset week {len(nowin)}쪽: Wins 칸이 옅은 칸(별 그림 + Wins log + 한 줄)이 아님 {nowin[:3]} (10-03 A안)")

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
    sys.exit(1 if main(sys.argv[1] if len(sys.argv) > 1 else "v0.17") else 0)
