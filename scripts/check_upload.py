# -*- coding: utf-8 -*-
"""shop.md 의 업로드 이력표와 output/upload/ 의 실제 파일을 대조한다.

이력표에 이름이 적힌 PDF 가 output/upload/ 에 있고, 바이트 수가 표와
같은지 본다. 다른 PC 에서 다시 빌드한 뒤, 그리고 Etsy 에 올린 직후 돌린다.

    python scripts/check_upload.py
"""
import os, re, sys

sys.stdout.reconfigure(encoding="utf-8")   # 한국어 Windows 콘솔은 cp949

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD = os.path.join(ROOT, "output", "upload")

md = open(os.path.join(ROOT, "shop.md"), encoding="utf-8").read()
sec = md.split("## 0-1.", 1)[1].split("### 리스팅 이미지", 1)[0]

fail = 0
for row in re.findall(r"^\|\s*(\d+)\s*\|(.+)$", sec, re.M):
    n, rest = row
    cells = [c.strip() for c in rest.split("|")]
    date, ver, name, size = cells[0], cells[1], cells[2], cells[3]
    want = int(size.replace(",", ""))
    m = re.search(r"`([^`]+\.pdf)`", name)
    if not m:
        print(f"  ??    #{n} {date} {ver}: 파일 이름 미확인 -- 대조 불가")
        continue
    path = os.path.join(UPLOAD, m.group(1))
    if not os.path.exists(path):
        print(f"  FAIL  #{n} {date} {ver}: output/upload/{m.group(1)} 없음")
        fail += 1
        continue
    got = os.path.getsize(path)
    ok = got == want
    fail += not ok
    print(f"  {'OK  ' if ok else 'FAIL'}  #{n} {date} {ver}: {got:,} B  expect {want:,}")

print(f"\nFAILURES: {fail}")
sys.exit(1 if fail else 0)
