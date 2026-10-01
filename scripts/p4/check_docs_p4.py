# -*- coding: utf-8 -*-
"""상품 4 문서 정합성 검사 -- 기획서·리스팅·인수인계서가 실제 판과 모순되지 않는가 (PROCESS.md 5-6).

    python scripts/p4/check_docs_p4.py v0.9

2026-10-01 사용자 "기획서에 모순은 없어?" 로 찾은 것: 쪽 번호가 1~2쪽 밀림, 목차 페이지 위치·누락, "105쪽 점 노트"(실제 106),
"90쪽 Rescue"(실제 92), 쪽 수가 문서 안에서 107/108/110 제각각. 결정이 바뀔 때 본문이 따라오지 않아 생겼다.

잰다:
  a 기획서 3절 페이지 지도의 "| N | 이름 |" 행 -> 그 쪽의 실제 제목과 같은가 (5-1 기획서 대조)
  b 문서 속 "N쪽 English Name" -> 그 쪽의 실제 제목과 같은가 (기획서·리스팅·인수인계서)
  c 문서 속 "합계·총 N쪽", 리스팅 "N pages" -> 실제 쪽 수
  d 3절 섹션 제목 "(N)" -> 그 섹션 실제 쪽 수
인용(> 로 시작하는 줄)과 제목에 "기록"이 든 절은 그날의 기록이라 보지 않는다 -- 현재 사실은 표와 본문에 쓴다.
링크가 갈 곳이 없는지는 check_p4 가 본다(죽은 링크·들어올 길 없는 페이지·링크 주석 수).
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import p4_content as C  # noqa: E402
import pages_p4  # noqa: E402

DOCS = ["product4-content.md", "listing-p4.md", "product4-design-handoff.md"]


def titles():
    """쪽 번호(1부터) -> (key, 제목, 탭)"""
    rooms = {k: n for k, n, *_ in C.ROOMS}
    rooms["myroom"] = C.MY_ROOM[1]
    out = {}
    for i, (k, _, tab) in enumerate(pages_p4.specs(), 1):
        if k == "cover":
            t = C.COVER[0]
        elif k.startswith("deep-"):
            t = C.PAGE_TEXT["deep"][0].format(room=rooms[k[5:]])
        elif re.fullmatch(r"w\d+", k):
            t = C.WEEK_PAGE[0].format(n=k[1:])
        elif k == "myroom":
            t = C.PAGE_TEXT["myroom"][0]
        else:
            t = pages_p4.title_of(k)
        out[i] = (k, t, tab)
    return out


def norm(s):
    s = re.sub(r"\*\*|`|\(.*?\)", "", s).replace(" / ", " or ").replace("&amp;", "&")
    s = re.sub(r"\s+index$", "", s.strip(), flags=re.I)
    return re.sub(r"[^a-z0-9& ]", " ", s.lower()).split()


def same(a, b):
    a, b = norm(a), norm(b)
    return bool(a) and (a == b[:len(a)] or b == a[:len(b)])


def check():
    T = titles()
    n_pages = len(T)
    fails = []
    for doc in DOCS:
        path = os.path.join(ROOT, doc)
        if not os.path.exists(path):
            continue
        lines = open(path, encoding="utf-8").read().split("\n")
        in_map = history = False
        for no, line in enumerate(lines, 1):
            if line.startswith("## "):
                in_map = doc == "product4-content.md" and line.startswith("## 3.")
            if line.startswith("#"):
                history = "기록" in line          # 제목에 "기록" -- 그날의 기록이라 대조하지 않는다
            if line.lstrip().startswith(">") or history:
                continue
            # a 페이지 지도 행
            m = re.match(r"\|\s*(\d{1,3})\s*\|\s*([^|]+?)\s*\|", line)
            if in_map and m:
                n, name = int(m.group(1)), m.group(2)
                if re.search(r"[A-Za-z]", name) and n in T and not same(name, T[n][1]):
                    fails.append(f"{doc}:{no} 지도 {n}쪽 '{name.strip()}' -- 실제 {n}쪽은 '{T[n][1]}'")
                elif n not in T:
                    fails.append(f"{doc}:{no} 지도 {n}쪽 -- 판은 {n_pages}쪽까지")
            # d 섹션 제목 (N)
            m = re.match(r"### 3-\d\. ([A-Z]+) \((\d+)\)", line)
            if in_map and m:
                real = sum(1 for _, _, tab in T.values() if tab == m.group(1).lower())
                if real != int(m.group(2)):
                    fails.append(f"{doc}:{no} {m.group(1)} ({m.group(2)}) -- 실제 {real}쪽")
            # b "N쪽 Name"
            for m in re.finditer(r"(\d{1,3})쪽 ([A-Z][A-Za-z0-9&' ]*[A-Za-z0-9])", line):
                n, name = int(m.group(1)), m.group(2)
                if n not in T:
                    fails.append(f"{doc}:{no} '{m.group(0)}' -- 판은 {n_pages}쪽까지")
                elif not same(name, T[n][1]):
                    fails.append(f"{doc}:{no} '{m.group(0)}' -- 실제 {n}쪽은 '{T[n][1]}'")
            # c 쪽 수
            for m in re.finditer(r"(?:합계|총)\s*약?\s*(\d{2,3})쪽|(\d{2,3}) pages|약 (\d{3})쪽", line):
                n = int(next(g for g in m.groups() if g))
                if n != n_pages and n >= 60:
                    fails.append(f"{doc}:{no} 쪽 수 '{m.group(0)}' -- 실제 {n_pages}쪽")
    return n_pages, fails


if __name__ == "__main__":
    n, f = check()
    print(f"문서 정합성 ({', '.join(DOCS)}) ↔ 판 {n}쪽")
    print("FAIL:\n  " + "\n  ".join(f) if f else "검사 통과 (FAIL 0)")
