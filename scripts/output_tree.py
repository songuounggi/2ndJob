# -*- coding: utf-8 -*-
"""output/ 구조 스냅숏을 md 로 남긴다 -- output/ 은 git 밖이라 다른 PC 에서는 무엇이 어디 있는지 모른다 (2026-09-28 사용자).

    python scripts/output_tree.py            # -> output-tree-home.md
    python scripts/output_tree.py office     # -> output-tree-office.md (회사 PC)

폴더 이름·파일 수·크기만 적는다(깊이 3). 파일 내용은 옮기지 않는다 -- 다시 뽑는 법은 SETUP.md.
"""
import datetime
import os
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[1]
label = sys.argv[1] if len(sys.argv) > 1 else "home"
out = ROOT / f"output-tree-{label}.md"


def size(d):
    return sum(f.stat().st_size for f in d.rglob("*") if f.is_file())


lines = [f"# output/ 구조 스냅숏 -- {label} PC `{ROOT.as_posix()}` ({datetime.date.today()}, {os.environ.get('COMPUTERNAME', '')})", "",
         "output/ 은 git 밖이다. 다른 PC 에는 이 폴더들이 없다 -- 다시 뽑는 법은 `SETUP.md`, 상품 3 지도는 `scripts/p3/README.md`.",
         f"폴더 이름과 파일 수·크기만 적는다(깊이 3). 다시 만들려면 `python scripts/output_tree.py {label}`.", "", "```"]


def walk(d, depth):
    for c in sorted(x for x in d.iterdir() if x.is_dir()):
        n = sum(1 for f in c.rglob("*") if f.is_file())
        lines.append(f"{'  ' * depth}{c.name}/  ({n} files, {size(c) / 1e6:.1f} MB)")
        if depth < 2:
            walk(c, depth + 1)


walk(ROOT / "output", 0)
lines.append("```")
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(out, len(lines), "lines")
