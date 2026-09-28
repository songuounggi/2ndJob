# -*- coding: utf-8 -*-
"""리스팅 펜슬 검사 -- 사용자가 확대해서 찾은 두 결함을 잰다 (2026-09-28).

    python scripts/p3/check_pencil_p3.py            # 지금 코드
    python scripts/p3/check_pencil_p3.py --reverse  # 고치기 전 방식(잰 굵기 그대로 + LANCZOS·BICUBIC)에서 걸리는지

1. 촉 우글거림 (v0.48): 사진에서 1px 단위로 잰 굵기를 그대로 윤곽으로 써서 원뿔에 굴곡 -> 3D 음영이 줄무늬.
   잰다: 원뿔 구간(u < 0.12) 윤곽의 2차 차분(굽는 정도가 바뀌는 횟수) -- 매끈한 곡선이면 부호가 거의 안 바뀐다
2. 윤곽 점선 (v0.49 확대): LANCZOS 줄이기 + BICUBIC 돌리기에서 흰 점선 -> BOX·BILINEAR 로 고침.
   **자동 검사 불가** -- 가장자리 밝기를 두 가지로 재 봤으나 옛 방식과 구분되지 않았다(확대 필터와 겹쳐 보였을 수도).
   펜슬을 바꾸면 펜촉·뒤끝을 4배로 확대(NEAREST)해서 눈으로 본다
"""
import pathlib
import sys

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

REV = "--reverse" in sys.argv
bad = []

# 1. 윤곽 매끈함 -- 리스팅이 쓰는 윤곽(devices_p3._real_profile, v0.51 Apple 원본 대조판)
import devices_p3 as D  # noqa: E402
Lx, Rx = 2000.0, 2000.0 / 37.1
x = np.linspace(0, Lx, 4001)
r = D._real_profile(x, Rx, Lx)[0] / Rx
u = x / Lx
if REV:   # 고치기 전(v0.48): 잰 굵기를 1px 단위 그대로 -- 계단 잡음을 되살린다
    r = np.round(r * 32) / 32
head = (u > 0.02) & (u < 0.12) & (np.abs(u - 0.0525) > 0.006)   # 이음선 홈은 일부러 판 것이라 뺀다
d2 = np.diff(np.sign(np.round(np.diff(r[head], 2), 6)))
flips = int((d2 != 0).sum())
print(f"1 원뿔 윤곽 굽기 방향 바뀜: {flips}회", "OK" if flips <= 8 else "FAIL (우글거림)")
if flips > 8:
    bad.append("윤곽")

print("ALL OK" if not bad else f"FAIL {bad}")
sys.exit(1 if bad else 0)
