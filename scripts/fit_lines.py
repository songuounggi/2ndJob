# -*- coding: utf-8 -*-
"""괘선 줄 수를 카드 높이에 맞춰 자동 보정한다.

LINES.md 규칙대로 줄 높이를 고정하면 카드 아래에 여백이 남는다. 카드는
여전히 늘어나는데 괘선은 제 높이만 차지하기 때문이다. 여기서는 렌더해서
남는 여백을 재고, `lines(n)` 의 n 을 그만큼 올린 뒤 다시 재기를 반복한다.

    python scripts/fit_lines.py v8-undated

측정 -> 수정 -> 재측정을 여백이 1줄 미만이 될 때까지 돌린다(최대 6회).
손으로 페이지마다 맞추면 다음 디자인 변경 때 또 어긋난다.
"""

import io
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BUILD = os.path.join(ROOT, "scripts", "build_planner.py")

PROBE = r"""
const out=[];
document.querySelectorAll('section.page').forEach(sec=>{
  sec.querySelectorAll('.lines').forEach((L,i)=>{
    const kids=[...L.children];
    if(!kids.length) return;
    const one=kids[0].getBoundingClientRect().height;
    const card=L.closest('.card');
    if(!card) return;
    const pad=parseFloat(getComputedStyle(card).paddingBottom)||0;
    const gap=card.getBoundingClientRect().bottom-pad
              -L.getBoundingClientRect().bottom;
    out.push({p:sec.id,i,n:kids.length,room:Math.floor(gap/one)});
  });
});
document.body.setAttribute('data-probe', JSON.stringify(out));
"""


def build(version):
    env = dict(os.environ, PLANNER_VERSION=version)
    r = subprocess.run([sys.executable, BUILD], env=env, cwd=ROOT,
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode:
        raise SystemExit("빌드 실패\n" + (r.stderr or "")[-600:])


def measure(version):
    src = os.path.join(ROOT, "src", f"planner_{version}.html")
    html = io.open(src, encoding="utf-8").read()
    tmp = os.path.join(tempfile.gettempdir(), "fit_lines.html")
    io.open(tmp, "w", encoding="utf-8").write(
        html.replace("</body>", "<script>" + PROBE + "</script></body>"))
    prof = os.path.join(tempfile.gettempdir(), "fit-lines-prof")
    r = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--user-data-dir=" + prof,
         "--virtual-time-budget=25000", "--dump-dom",
         "file:///" + tmp.replace("\\", "/")],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.search(r'data-probe="([^"]*)"', r.stdout or "")
    if not m:
        raise SystemExit("측정 실패 — Chrome 이 결과를 내놓지 않았다")
    d = json.loads(m.group(1).replace("&quot;", '"'))
    # 반복 페이지는 같은 빌더에서 나오므로 고유 페이지만 본다
    return [x for x in d
            if not re.fullmatch(r"[dwm]\d+(-\d+)?", x["p"]) and x["room"] > 0]


def bump(src_text, page_id, block_i, add):
    """해당 페이지 빌더 안의 block_i 번째 lines(n) 을 n+add 로 바꾼다."""
    fn = PAGE_FN.get(page_id)
    if not fn:
        return src_text, False
    m = re.search(r"^def %s\(.*?(?=^def )" % re.escape(fn), src_text,
                  re.S | re.M)
    if not m:
        return src_text, False
    body = m.group(0)
    calls = list(re.finditer(r"lines\((\d+)\)", body))
    if block_i >= len(calls):
        return src_text, False
    c = calls[block_i]
    new_body = body[:c.start()] + f"lines({int(c.group(1)) + add})" + body[c.end():]
    return src_text[:m.start()] + new_body + src_text[m.end():], True


if __name__ == "__main__":
    version = sys.argv[1] if len(sys.argv) > 1 else "v8-undated"
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    src_text = io.open(BUILD, encoding="utf-8").read()
    # 페이지 id -> 빌더 함수 이름. specs 목록에서 뽑는다.
    PAGE_FN = dict(re.findall(r'\("([\w-]+)",\s*(p_\w+)\)', src_text))

    for round_ in range(1, 7):
        build(version)
        gaps = measure(version)
        if not gaps:
            print(f"{round_}회차: 여백 남는 블록 없음 — 완료")
            break
        print(f"{round_}회차: 여백 남는 블록 {len(gaps)}개 "
              f"(최대 {max(g['room'] for g in gaps)}줄분)")
        src_text = io.open(BUILD, encoding="utf-8").read()
        changed = 0
        for g in sorted(gaps, key=lambda x: -x["room"]):
            src_text, ok = bump(src_text, g["p"], g["i"], g["room"])
            changed += ok
        if not changed:
            print("   더 고칠 수 있는 lines() 호출을 찾지 못했다")
            break
        io.open(BUILD, "w", encoding="utf-8").write(src_text)
        print(f"   {changed}개 블록의 줄 수를 올렸다")
    else:
        print("6회차까지 돌았지만 여백이 남아 있다 — 수동 확인 필요")
