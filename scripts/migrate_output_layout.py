# -*- coding: utf-8 -*-
"""옛 output 배치를 상품별 폴더(prod1/prod2/prod3)로 옮긴다 (2026-09-25 사용자 결정).

output/ 는 git 밖이라 `git pull` 로는 따라오지 않는다. 다른 PC(회사 PC)에서 pull 한 뒤
한 번 돌린다. 집 PC 는 2026-09-25 에 옮겼다(306 파일, 해시 전부 일치).

    python scripts/migrate_output_layout.py            # 무엇을 옮길지만 보여 준다
    python scripts/migrate_output_layout.py --apply    # 실제로 옮긴다

규칙:
  - 옮기기만 한다(이름 바꾸기). 지우지 않는다. 옮긴 뒤 해시가 같은지 확인한다
  - 목적지에 같은 이름이 이미 있으면 **건드리지 않고** 보고한다(내용이 같으면 원본을 그대로 둔다)
  - 어느 상품 것인지 모르는 파일은 옮기지 않고 목록만 낸다
"""
import hashlib
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if "--root" in sys.argv:
    ROOT = sys.argv[sys.argv.index("--root") + 1]
OUT = os.path.join(ROOT, "output")
APPLY = "--apply" in sys.argv

# (옛 경로 정규식 -- output/ 기준, 새 상위 폴더). 위에서부터 첫 일치.
RULES = [
    (r"planner_(student-|v9-student|v10-ink).*\.pdf$", "prod2"),
    (r"planner_dated-.*\.pdf$", "prod3/archive_dated-v0.1"),
    (r"planner_v\d.*\.pdf$", "prod1"),
    (r"upload/student-[^/]+(/.*)?$", "prod2"),
    (r"upload/v\d[^/]*(/.*)?$", "prod1"),
    (r"(listing_student|preview_student_qa|preview_audit)(/.*)?$", "prod2"),
    (r"preview/(listing_src|review)(/.*)?$", "prod2"),
    (r"(listing_v815|listing|pinterest|pinterest_v815|perf|ipad-test)(/.*)?$", "prod1"),
    (r"preview/(rail_strip_v815\.png|v8_p\d+\.png)$", "prod1"),
    (r"(editions)(/.*)?$", "prod3"),
    (r"p3_(wireframe|content)_.*$", "prod3/wireframe"),
]
KEEP = ("prod1", "prod2", "prod3")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def plan():
    moves, unknown = [], []
    for dp, dn, fn in os.walk(OUT):
        rel_dir = os.path.relpath(dp, OUT).replace("\\", "/")
        if rel_dir.split("/")[0] in KEEP:
            continue
        for f in fn:
            rel = (f if rel_dir == "." else f"{rel_dir}/{f}")
            for pat, dst in RULES:
                if re.match(pat, rel):
                    # 하위 경로가 붙은 목적지(prod3/wireframe 등)는 파일 이름만, 아니면 옛 상대 경로 그대로
                    tail = os.path.basename(rel) if "/" in dst else rel
                    moves.append((rel, f"{dst}/{tail}"))
                    break
            else:
                unknown.append(rel)
    return moves, unknown


def main():
    moves, unknown = plan()
    print(f"{'옮김' if APPLY else '옮길 예정'}: {len(moves)}개   분류 못 함(그대로 둠): {len(unknown)}개\n")
    clash = done = 0
    for src, dst in moves:
        s, d = os.path.join(OUT, src), os.path.join(OUT, dst)
        if os.path.exists(d):
            same = sha(s) == sha(d)
            print(f"  이미 있음{' (내용 같음)' if same else ' (내용 다름!)'}: {dst}  <- {src}  -- 건드리지 않음")
            clash += 1
            continue
        print(f"  {src}  ->  {dst}")
        if APPLY:
            h = sha(s)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            os.rename(s, d)
            if sha(d) != h:
                sys.exit(f"해시가 달라졌다: {dst} -- 멈춘다")
            done += 1
    for u in unknown:
        print(f"  ??  {u}  (어느 상품 것인지 모른다 -- 손으로 옮길 것)")
    if APPLY:
        # 비어 버린 옛 폴더만 치운다(파일이 하나라도 있으면 둔다)
        for dp, dn, fn in sorted(os.walk(OUT), key=lambda x: -len(x[0])):
            rel = os.path.relpath(dp, OUT).replace("\\", "/")
            if rel != "." and rel.split("/")[0] not in KEEP and not os.listdir(dp):
                os.rmdir(dp)
    print(f"\n{'옮김 ' + str(done) if APPLY else '(--apply 로 실행하면 옮긴다)'} · 충돌 {clash} · 미분류 {len(unknown)}")


if __name__ == "__main__":
    main()
