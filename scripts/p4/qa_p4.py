# -*- coding: utf-8 -*-
"""상품 4 검수 한 번에 (PROCESS.md 5단계 5-1~5-6 + 6단계 dogfood) -- Claude 가 매 빌드 뒤 돌린다.

    python scripts/p4/qa_p4.py v0.16

하나라도 FAIL 이면 사용자에게 "완료" 라고 보내지 않는다(PROCESS.md 5절 규칙).
스크롤·렌더 속도(check_scroll_speed)도 여기서 컬러판·흑백판 둘 다 -- 10-01 사용자: "필수 검수로, 네가 검수하는 곳에".
"""
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
VER = sys.argv[1] if len(sys.argv) > 1 else "v0.16"
PDF = lambda t: os.path.join(ROOT, "output", "prod4", "planner", VER, f"home-reset_{VER}_{t}-FINAL.pdf")

CHECKS = [
    ("5-1·5-4 기획서 대조 · 인쇄된 번호 · 금지 표현", ["scripts/p4/check_plan_p4.py", VER]),
    ("5-2 디자인 (README 11절 · 탭 · 쓰는 칸 옆 링크 · 카드 전체)", ["scripts/p4/check_design_p4.py", VER]),
    ("5-3 판 · 링크 · 흑백판", ["scripts/p4/check_v2_p4.py", VER]),
    ("5-5 렌더 (GoodNotes 위험 효과)  컬러", ["scripts/check_render.py", PDF("color")]),
    ("5-5 렌더 (GoodNotes 위험 효과)  흑백", ["scripts/check_render.py", PDF("BW")]),
    ("5-5 스크롤·렌더 속도  컬러", ["scripts/check_scroll_speed.py", PDF("color")]),
    ("5-5 스크롤·렌더 속도  흑백", ["scripts/check_scroll_speed.py", PDF("BW")]),
    ("5-4 리스팅", ["scripts/p4/check_listing_p4.py", VER]),
    ("5-6 문서 정합성", ["scripts/p4/check_docs_p4.py"]),
    ("6 써 보기 (dogfood)", ["scripts/p4/dogfood_p4.py", VER]),
]


def ok(name, out, code):
    """결과 줄을 찾아 판정한다 -- 마지막 줄로 보면 뒤에 붙은 경고(stderr)를 결과로 읽는다(첫 실행에서 5-3 을 거짓 FAIL)"""
    if "dogfood" in name:
        return "막힌 곳 0개" in out
    if code != 0 or re.search(r"^FAIL:|^\s*(color|BW):\s+FAIL|FAILURES: [1-9]", out, re.M):
        return False
    return bool(re.search(r"FAIL 0|FAILURES: 0|검사 통과", out))


def main():
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    bad = []
    for name, cmd in CHECKS:
        r = subprocess.run([sys.executable] + cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
        out = (r.stdout or "") + (r.stderr or "")
        good = ok(name, out, r.returncode)
        print(f"  {'OK  ' if good else 'FAIL'} {name}")
        if not good:
            bad.append(name)
            print("      " + "\n      ".join(out.strip().splitlines()[-8:]))
    print(f"\n상품 4 {VER} 검수: {'전부 통과' if not bad else f'FAIL {len(bad)}개'}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
