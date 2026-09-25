# -*- coding: utf-8 -*-
"""상품 1 도구 41장의 내용(문구·칸 구성)을 상품 3 용 스냅숏으로 떠 온다. 한 번만 돌린다.

    python scripts/p3/extract_p1_tools.py     # -> scripts/p3/p1_tools.json (커밋한다)

상품 1 코드(build_planner.py)는 import 하지 않는다(scripts/p3/README.md 격리 규칙).
상품 1 이 이미 뽑아 둔 HTML(src/planner_v8.20-undated.html)에서 페이지 본문만 읽어,
모양(색·배경·그림자·모서리·글꼴)만 벗기고 레이아웃(flex·크기·간격)은 남긴다.
모양은 planner_build.py 의 Lifted Paper CSS 가 다시 입힌다.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "planner_v8.20-undated.html"
OUT = pathlib.Path(__file__).resolve().parent / "p1_tools.json"

KEYS = ["tasks", "braindump", "session", "obstacle", "paralysis", "mindmap", "hyperfocus", "screen",
        "estimate", "avoiding", "deadline",
        "sta", "worry", "rsd", "kind", "dose", "gratitude", "reframe", "name-it", "boundaries", "energy",
        "habits-grid", "routines", "meds", "sleep", "symptoms", "doctor", "therapy", "intake", "movement", "cycle",
        "meals", "wheel", "cleaning", "budget", "impulse", "reading", "dates", "subs", "travel", "chores",
        "goals", "project", "vision"]

# 모양 속성만 벗긴다. 레이아웃(display/flex/width/height/gap/padding/margin/grid ...)은 남긴다.
DROP = re.compile(r"^\s*(background(-color|-image)?|color|box-shadow|border-radius|font-family|opacity|"
                  r"--acc|--accent|--chip|--accent-text)\s*:", re.I)


def clean_style(m):
    decls = [d for d in m.group(1).split(";") if d.strip() and not DROP.match(d)]
    return f' style="{";".join(d.strip() for d in decls)}"' if decls else ""


def main():
    h = SRC.read_text(encoding="utf-8")
    secs = {m.group(1): m.group(2) for m in
            re.finditer(r'<section class="page" id="([^"]+)"[^>]*>(.*?)</section>', h, re.S)}
    out = {}
    for k in KEYS:
        s = secs[k]
        s = re.sub(r"<nav.*?</nav>", "", s, flags=re.S)                     # 탭 레일
        s = re.sub(r'<div class="bg-[^"]*"[^>]*></div>', "", s)              # 배경 번짐
        head = re.search(r'<div class="head">(.*?)</div>\s*<div class="body"', s, re.S)
        eyebrow = re.search(r'<div class="eyebrow">(.*?)</div>', head.group(1), re.S).group(1)
        title = re.search(r"<h1>(.*?)</h1>", head.group(1), re.S).group(1)
        sub = re.search(r'<div class="sub">(.*?)</div>', head.group(1), re.S)
        body = s[s.index('<div class="body"'):]
        body = body[:body.rindex("</div>")]                                  # .content 닫기 제거
        body = re.sub(r' style="([^"]*)"', clean_style, body)
        body = re.sub(r'\sdata-ln="\d+"', "", body)
        out[k] = {"eyebrow": eyebrow.strip(), "title": title.strip(),
                  "sub": sub.group(1).strip() if sub else "", "body": body}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"{len(out)} pages -> {OUT} ({OUT.stat().st_size:,} B)")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
