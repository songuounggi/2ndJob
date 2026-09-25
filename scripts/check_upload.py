# -*- coding: utf-8 -*-
"""shop.md 의 업로드 이력표와 실제 파일을 대조한다.

파일 규칙 (2026-09-24 사용자 확정):
  작업본  output/prod<N>/planner_<버전>-FINAL.pdf        버전을 올려 가며 고친다. 지우지 않는다
  올린 판 output/prod<N>/upload/<버전>/<Etsy 이름>       Etsy 에 올린 판마다 버전 이름으로
                                                 폴더를 만든다. 한 번 넣으면 건드리지 않는다
  upload/ 바로 아래에는 파일을 두지 않는다

이력표에서 날짜가 적힌 줄 = 올린 것, "올리기 전" = 후보. 그래서 본다:
  1. 모든 줄: 작업본 FINAL 이 있고 바이트가 표와 같은가
  2. 올린 줄: upload/<버전>/ 이 있고 바이트가 같은가
  3. upload/ 바로 아래에 낱개 파일이 없는가

    python scripts/check_upload.py
"""
import os, re, sys

sys.stdout.reconfigure(encoding="utf-8")   # 한국어 Windows 콘솔은 cp949

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# output 은 상품별 폴더 (2026-09-25). 상품 2 = student-*, 나머지 = 상품 1.
def prod_dir(ver):
    return os.path.join(ROOT, "output", "prod2" if ver.startswith("student") else "prod1")

md = open(os.path.join(ROOT, "shop.md"), encoding="utf-8").read()
sec = md.split("## 0-1.", 1)[1].split("### 리스팅 이미지", 1)[0]

rows = []
for n, rest in re.findall(r"^\|\s*(\d+)\s*\|(.+)$", sec, re.M):
    cells = [c.strip() for c in rest.split("|")]
    ver = re.search(r"`([^`]+)`", cells[1]).group(1)
    name = re.search(r"`([^`]+\.pdf)`", cells[2])
    uploaded = bool(re.match(r"\d{4}-\d{2}-\d{2}", cells[0]))
    rows.append((ver, name.group(1) if name else None,
                 int(cells[3].replace(",", "")), uploaded))

fail = 0
def report(ok, msg):
    global fail
    fail += not ok
    print(("  OK    " if ok else "  FAIL  ") + msg)

def size(p):
    return os.path.getsize(p) if os.path.exists(p) else None

for ver, name, want, uploaded in rows:
    tag = ver + ("" if uploaded else " (올리기 전)")
    got = size(os.path.join(prod_dir(ver), f"planner_{ver}-FINAL.pdf"))
    report(got == want, f"{tag}: 작업본 FINAL {got and f'{got:,}'} B  expect {want:,}")
    if not uploaded:
        continue
    if not name:
        print(f"  ??    {tag}: Etsy 파일 이름 미확인 -- 폴더 대조 불가")
        continue
    folder = ver.replace("-undated", "")   # 폴더 이름은 v8.18, v8.20 처럼 짧게
    got = size(os.path.join(prod_dir(ver), "upload", folder, name))
    report(got == want, f"{tag}: {os.path.basename(prod_dir(ver))}/upload/{folder}/ {got and f'{got:,}'} B  expect {want:,}")

for prod in ("prod1", "prod2", "prod3"):
    up = os.path.join(ROOT, "output", prod, "upload")
    loose = [f for f in os.listdir(up) if os.path.isfile(os.path.join(up, f))] if os.path.isdir(up) else []
    report(not loose, f"{prod}/upload/ 바로 아래 낱개 파일 {len(loose)}개  expect 0 {loose if loose else ''}")
# 옛 자리(상품별로 나누기 전)에 뭔가 다시 생기면 잡는다
stray = [f for f in os.listdir(os.path.join(ROOT, "output")) if f not in ("prod1", "prod2", "prod3")]
report(not stray, f"output/ 바로 아래는 prod1·prod2·prod3 뿐  {stray if stray else ''}")

print(f"\nFAILURES: {fail}")
sys.exit(1 if fail else 0)
