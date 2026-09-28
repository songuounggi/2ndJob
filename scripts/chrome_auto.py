# -*- coding: utf-8 -*-
"""자동화 Chrome 이 Windows 계정을 잠그지 않게 켠다 -- 모든 방·모든 상품 공용.

2026-09-28 회사 PC: 로컬 계정이 "참조된 계정이 잠겨 있다" 로 로그인이 안 됐다(9/23 부터 반복).
Security 로그 4625(로그온 실패) 30건이 전부 chrome.exe, 종류 2, 시각이 빌드와 겹쳤다.
Chrome 은 켤 때 "OS 비밀번호가 비었나" 를 빈 비밀번호 로그온으로 확인하고, 결과를 프로필의
`Local State`(password_manager.os_password_blank / os_password_last_changed)에 저장한다.
빌드는 Chrome 을 켤 때마다 **새 빈 프로필**이라 매번 확인 -> 매번 로그온 실패 1회 -> 10분에 10회면 잠금
(이 PC: 잠금 임계 10, 기간 10분).

실측 (BadPasswordCount): 새 프로필 = 켤 때마다 +1 (headless 인쇄·Playwright 둘 다),
고정 프로필 = 첫 번만 +1, **새 프로필에 저장된 `Local State` 만 넣어 두면 +0**.
그래서 여기서는 매번 새 임시 프로필을 만들되 `Local State` 를 미리 넣는다. 스크립트 구조는 그대로 둘 수 있다.

    from chrome_auto import launch, chrome_args
    with sync_playwright() as p:
        br = launch(p)                      # p.chromium.launch(channel="chrome") 대신
        pg = br.new_page(viewport={...})    # new_context(...)·new_page(...)·close() 그대로
    subprocess.run([CHROME, "--headless", *chrome_args(), ...])   # chrome.exe 직접 부를 때

비밀번호를 바꾸면 Chrome 이 한 번 다시 확인하고(+1), 그 결과가 원판에 다시 저장된다(close 때).
검사: `python scripts/check_chrome_lockout.py`
"""
import json
import os
import pathlib
import shutil
import subprocess
import tempfile

CHROME = os.environ.get("CHROME", r"C:\Program Files\Google\Chrome\Application\chrome.exe")
TEMPLATE = pathlib.Path(os.environ.get("LOCALAPPDATA", pathlib.Path.home())) / "2ndJob-chrome" / "Local State"
_KEY = "password_manager"


def _has_cache(path):
    try:
        pm = json.loads(pathlib.Path(path).read_text(encoding="utf-8")).get(_KEY, {})
        return "os_password_blank" in pm and "os_password_last_changed" in pm
    except (OSError, ValueError):
        return False


def _save_back(profile):
    """프로필이 확인한 결과를 원판으로 -- 비밀번호가 바뀌어 다시 확인했으면 새 값이 남는다"""
    ls = pathlib.Path(profile) / "Local State"
    if _has_cache(ls):
        TEMPLATE.parent.mkdir(parents=True, exist_ok=True)
        pm = json.loads(ls.read_text(encoding="utf-8"))[_KEY]
        TEMPLATE.write_text(json.dumps({_KEY: {k: pm[k] for k in ("os_password_blank", "os_password_last_changed")}}), encoding="utf-8")


def _ensure_template():
    """원판이 없으면 한 번 만든다 -- 이 PC 에서 처음 한 번만 로그온 실패 1회"""
    if _has_cache(TEMPLATE):
        return
    prof = tempfile.mkdtemp(prefix="2ndjob-chrome-")
    try:
        html = pathlib.Path(prof) / "t.html"
        html.write_text("<p>t</p>", encoding="utf-8")
        subprocess.run([CHROME, "--headless", "--disable-gpu", f"--user-data-dir={prof}", "--no-pdf-header-footer",
                        f"--print-to-pdf={pathlib.Path(prof) / 't.pdf'}", html.as_uri()], capture_output=True, timeout=120)
        _save_back(prof)
    finally:
        shutil.rmtree(prof, ignore_errors=True)
    if not _has_cache(TEMPLATE):
        raise RuntimeError(f"Chrome 이 Local State 에 OS 비밀번호 확인 결과를 남기지 않았다 -- {TEMPLATE} (Chrome 버전이 바뀌었나?)")


def seeded_profile():
    """새 임시 프로필 + 확인 결과가 든 Local State"""
    _ensure_template()
    prof = tempfile.mkdtemp(prefix="2ndjob-chrome-")
    shutil.copyfile(TEMPLATE, pathlib.Path(prof) / "Local State")
    return prof


def chrome_args():
    """chrome.exe 를 직접 부를 때 붙인다. 임시 폴더는 OS 임시 폴더에 남는다(작다)"""
    return [f"--user-data-dir={seeded_profile()}"]


class _Browser:
    """p.chromium.launch() 의 Browser 처럼 쓴다. 컨텍스트마다 Local State 를 넣은 새 프로필(= Chrome 프로세스 하나)"""

    def __init__(self, p, headless=True):
        self._p, self._headless, self._open = p, headless, []

    def new_context(self, **kw):
        prof = seeded_profile()
        ctx = self._p.chromium.launch_persistent_context(prof, channel="chrome", headless=self._headless, **kw)
        self._open.append((ctx, prof))
        return ctx

    def new_page(self, **kw):
        ctx = self.new_context(**kw)
        return ctx.pages[0] if ctx.pages else ctx.new_page()

    def close(self):
        for ctx, prof in self._open:
            try:
                ctx.close()
            finally:
                _save_back(prof)
                shutil.rmtree(prof, ignore_errors=True)
        self._open = []


def launch(p, headless=True):
    return _Browser(p, headless)
