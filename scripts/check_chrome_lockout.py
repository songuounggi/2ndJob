# -*- coding: utf-8 -*-
"""자동화 Chrome 이 Windows 로그온 실패를 쌓지 않는지 잰다 (chrome_auto.py 검사).

    python scripts/check_chrome_lockout.py              # chrome_auto 로 4번 켠다 -> 실패 횟수 +0 이어야 PASS
    python scripts/check_chrome_lockout.py --reverse    # 옛 방식(새 빈 프로필)으로 1번 -> +1 이어야 검사가 제대로 재는 것

실패 횟수 = Win32_NetworkLoginProfile.BadPasswordCount (일반 권한으로 읽힌다). 이 PC 는 10분에 10회면 잠긴다 --
결함이 있으면 이 검사가 최대 +4 를 쌓으므로, 지금 횟수 + 4 가 10 에 닿으면 켜지 않고 멈춘다(10분 기다린다).
"""
import os
import pathlib
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from chrome_auto import CHROME, chrome_args, launch  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402


def bad():
    ps = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "WindowsPowerShell", "v1.0", "powershell.exe")   # Git Bash 에선 PATH 에 없다
    out = subprocess.run([ps, "-NoProfile", "-Command",
                          "(Get-CimInstance Win32_NetworkLoginProfile | Where-Object Name -like \"*\\$env:USERNAME\").BadPasswordCount"],
                         capture_output=True, text=True).stdout.strip()
    return int(out or 0)


def pdf_once(extra):
    d = pathlib.Path(tempfile.mkdtemp(prefix="lockcheck-"))
    (d / "t.html").write_text("<p>t</p>", encoding="utf-8")
    subprocess.run([CHROME, "--headless", "--disable-gpu", *extra, "--no-pdf-header-footer",
                    f"--print-to-pdf={d / 't.pdf'}", (d / "t.html").as_uri()], capture_output=True, timeout=120)


b0 = bad()
if b0 + 4 >= 10:
    raise SystemExit(f"로그온 실패가 이미 {b0}회 -- 검사가 최대 +4 라 잠금(10회)에 닿을 수 있어 켜지 않는다. 10분 뒤 다시")
if "--reverse" in sys.argv:
    pdf_once([f"--user-data-dir={tempfile.mkdtemp(prefix='lockcheck-fresh-')}"])
    d = bad() - b0
    print(f"옛 방식(새 빈 프로필) 1번: {b0} -> {b0 + d} ({d:+d})", "-- 검사가 제대로 잰다" if d >= 1 else "-- 안 늘었다: 이 검사는 결함을 못 잡는다")
    sys.exit(0 if d >= 1 else 1)
pdf_once(chrome_args())
pdf_once(chrome_args())
with sync_playwright() as p:
    br = launch(p)
    br.new_page(viewport={"width": 400, "height": 300}).goto("about:blank")
    br.new_context(device_scale_factor=2).new_page().goto("about:blank")
    br.close()
d = bad() - b0
print(f"chrome_auto 로 4번(인쇄 2 · Playwright 2): {b0} -> {b0 + d} ({d:+d})", "PASS" if d == 0 else "FAIL")
sys.exit(0 if d == 0 else 1)
