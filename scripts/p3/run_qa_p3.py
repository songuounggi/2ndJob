# -*- coding: utf-8 -*-
"""상품 3 검수 전부를 돌리고 보고서를 파일로 남긴다 (PROCESS.md 5단계). Prod 3 방 소유.

    python scripts/p3/run_qa_p3.py v0.15      # -> output/prod3/qa/<버전>/report.md + 각 검사 로그

2026-09-26 사용자: "몇 시간 검사한 결과는 대체 어디 있냐" -- 그때까지 결과는 터미널에만 찍혔다. 이제 판마다 파일로 남는다.
"""
import datetime as dt
import pathlib
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[2]
VER = sys.argv[1]
OUT = ROOT / "output" / "prod3" / "qa" / VER
if OUT.exists():
    raise SystemExit(f"{OUT} 는 이미 있다. 덮어쓰지 않는다.")
OUT.mkdir(parents=True)
PY = sys.executable
EDS = [(y, w) for y in ("2026", "2027") for w in ("mon", "sun")]
P = lambda *a: [PY, *a]
CHECKS = [("5-1 기획서 대조", [P("scripts/p3/check_plan_p3.py", VER, y, w) for y, w in EDS]),
          ("5-2 디자인: 줄 간격", [P("scripts/p3/audit_pitch_p3.py", VER, y, w) for y, w in EDS]),
          ("5-2 디자인: 잘림·넘침·겹침(화면)", [P("scripts/p3/audit_layout_p3.py", VER)]),
          ("5-2 디자인: 겹침(PDF)", [P("scripts/p3/audit_pdf_overlap_p3.py", VER)]),
          ("5-3 논리: 링크·탭·날짜(PDF)", [P("scripts/p3/check_links_p3.py", VER)]),
          ("5-4 수치·문구: 리스팅 대조", [P("scripts/p3/check_listing_p3.py", VER)]),
          ("5-5 뷰어·용량", [P("scripts/check_render.py", f"output/prod3/planner/{VER}/ADHD-Year-Planner-2027-mon.pdf")])]
rows = []
for name, cmds in CHECKS:
    ok = True
    log = OUT / (name.split()[0] + "_" + str(len(rows)) + ".log")
    with open(log, "w", encoding="utf-8") as fh:
        for c in cmds:
            r = subprocess.run(c, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
            fh.write("$ " + " ".join(c[1:]) + "\n" + r.stdout + r.stderr + "\n")
            ok &= r.returncode == 0
    last = [l for l in log.read_text(encoding="utf-8").splitlines() if l.strip()][-1]
    rows.append((name, ok, log.name, last))
    print(("OK   " if ok else "FAIL ") + name)
known = "5-5 는 렌더 시간 B 가 기준(150ms) 미달 -- 배경 2x 때문, 사용자 iPad 확인으로 넘김(product3-dated.md)"
md = [f"# 상품 3 검수 보고서 — {VER}", "", f"{dt.datetime.now():%Y-%m-%d %H:%M} · 네 판(2026·2027 × 월·일) · PROCESS.md 5단계", "",
      "| 검수 | 결과 | 로그 | 마지막 줄 |", "|---|---|---|---|"]
md += [f"| {n} | {'**통과**' if ok else '**FAIL**'} | `{lg}` | {last[:90]} |" for n, ok, lg, last in rows]
md += ["", "참고: " + known]
(OUT / "report.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print(OUT / "report.md")
