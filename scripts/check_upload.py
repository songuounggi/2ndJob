# -*- coding: utf-8 -*-
"""shop.md 의 업로드 이력표와 실제 파일을 대조한다.

파일 규칙 (2026-09-24 사용자 확정):
  작업본    output/planner_<버전>-FINAL.pdf     버전을 올려 가며 고친다. 지우지 않는다
  마켓 판   output/upload/<Etsy 이름>           지금 Etsy 에 올라가 있는 파일.
                                               최종 확인 전에는 건드리지 않는다
  보관      output/upload/<#>/<Etsy 이름>       Etsy 에 올렸던 판을 이력 번호대로

이력표에서 날짜가 적힌 줄 = 올린 것, "올리기 전" = 후보. 그래서 본다:
  1. 모든 줄: 버전 FINAL 이 있고 바이트가 표와 같은가
  2. 올린 줄: upload/<#>/ 에 보관본이 있고 바이트가 같은가
  3. upload/ 바로 아래 파일 = 올린 줄 중 마지막(지금 마켓 판)인가

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
    uploaded = bool(re.match(r"\d{4}-\d{2}-\d{2}", cells[0]))
    rows.append((n, ver, name.group(1) if name else None,
                 int(cells[3].replace(",", "")), uploaded))

fail = 0
def report(ok, msg):
    global fail
    fail += not ok
    print(("  OK    " if ok else "  FAIL  ") + msg)

def size(p):
    return os.path.getsize(p) if os.path.exists(p) else None

for n, ver, name, want, uploaded in rows:
    tag = f"#{n} {ver}" + ("" if uploaded else " (올리기 전)")
    got = size(os.path.join(OUTPUT, f"planner_{ver}-FINAL.pdf"))
    report(got == want, f"{tag}: 작업본 FINAL {got and f'{got:,}'} B  expect {want:,}")
    if not uploaded:
        continue
    if not name:
        print(f"  ??    {tag}: Etsy 파일 이름 미확인 -- 보관본 대조 불가")
        continue
    got = size(os.path.join(UPLOAD, n, name))
    report(got == want, f"{tag}: 보관본 upload/{n}/ {got and f'{got:,}'} B  expect {want:,}")

live = [r for r in rows if r[4]][-1]
n, ver, name, want, _ = live
files = [f for f in os.listdir(UPLOAD) if os.path.isfile(os.path.join(UPLOAD, f))]
report(files == [name], f"upload/ 바로 아래 = 마켓 판 1장 ({files})")
got = size(os.path.join(UPLOAD, name))
report(got == want, f"마켓 판 = #{n} {ver}: {got and f'{got:,}'} B  expect {want:,}")

print(f"\nFAILURES: {fail}")
sys.exit(1 if fail else 0)
