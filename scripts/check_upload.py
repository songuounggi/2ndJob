# -*- coding: utf-8 -*-
"""shop.md 의 업로드 이력표와 실제 파일을 대조한다.

파일 규칙 (2026-09-24 확정):
  원본      output/planner_<버전>-FINAL.pdf   버전마다 하나, 지우지 않는다
  올릴 것   output/upload/<Etsy 이름>        딱 한 장. 이력표 맨 아래 줄의 사본

그래서 두 가지를 본다:
  1. 이력표 각 줄의 버전 FINAL 이 있고 바이트 수가 표와 같은가
  2. output/upload/ 에 한 장만 있고, 맨 아래 줄의 이름·바이트와 같은가

    python scripts/check_upload.py
"""
import os, re, sys

sys.stdout.reconfigure(encoding="utf-8")   # 한국어 Windows 콘솔은 cp949

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(ROOT, "output")
UPLOAD = os.path.join(OUTPUT, "upload")

md = open(os.path.join(ROOT, "shop.md"), encoding="utf-8").read()
sec = md.split("## 0-1.", 1)[1].split("### 리스팅 이미지", 1)[0]

rows = []
for n, rest in re.findall(r"^\|\s*(\d+)\s*\|(.+)$", sec, re.M):
    cells = [c.strip() for c in rest.split("|")]
    ver = re.search(r"`([^`]+)`", cells[1]).group(1)
    name = re.search(r"`([^`]+\.pdf)`", cells[2])
    rows.append((n, cells[0], ver, name.group(1) if name else None,
                 int(cells[3].replace(",", ""))))

fail = 0
def report(ok, msg):
    global fail
    fail += not ok
    print(("  OK    " if ok else "  FAIL  ") + msg)

for n, date, ver, name, want in rows:
    f = os.path.join(OUTPUT, f"planner_{ver}-FINAL.pdf")
    if not os.path.exists(f):
        report(False, f"#{n} {ver}: output/planner_{ver}-FINAL.pdf 없음 (SETUP.md 로 다시 빌드)")
        continue
    got = os.path.getsize(f)
    report(got == want, f"#{n} {ver}: FINAL {got:,} B  expect {want:,}")

n, date, ver, name, want = rows[-1]
files = [f for f in os.listdir(UPLOAD)] if os.path.isdir(UPLOAD) else []
report(len(files) == 1, f"output/upload/ 에 파일 {len(files)}개  expect 1")
if name:
    f = os.path.join(UPLOAD, name)
    ok = os.path.exists(f) and os.path.getsize(f) == want
    report(ok, f"upload/{name} = #{n} {ver} ({want:,} B)")

print(f"\nFAILURES: {fail}")
sys.exit(1 if fail else 0)
