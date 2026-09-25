---
name: cellfade
description: 셀페이드 — 표·필기칸의 점선을 칸(셀)마다 양 끝이 흐려지게 긋는다. 그라데이션 없이 끝 점만 옅은 단색 조각으로 (iPad GoodNotes 안전). 사용자가 "셀페이드", "점선 셀페이드", "점선 양끝 흐림", "cellfade" 라고 하거나 새 상품·새 페이지에 점선 표나 괘선을 만들 때 사용.
---

# 셀페이드 (cellfade)

점선을 **칸마다** 양 끝이 흐려지게 긋는 방법. 상품 2 에서 v0.3 → v0.6 까지 여섯 번
고쳐 가며 사용자가 확정한 모양이다. 어느 상품에서든 **이 절차와 이 코드**로 한다.

## 무엇인가 (사용자가 확정한 모양)

- **표 가로선:** 칸(열) 폭마다 양 끝이 흐려진다
- **표 세로선:** 칸(행) 높이마다 위아래 끝이 흐려진다. 선 전체의 위아래가 **아니다**
- **필기칸 괘선:** 줄마다 양 끝이 흐려진다 (표와 똑같이 보여야 한다)
- 가운데 진하기는 흐림을 넣기 전과 **같다**. 점 위치도 같다 (세로선은 행 경계마다 틈)
- 흐림 폭은 24pt, 칸이 짧으면 칸 길이의 1/3

## 코드 — 새로 짜지 말고 부른다

`scripts/dashfade.py` (상품 중립). 자체 검사: `python scripts/dashfade.py`

```python
import dashfade as DF
DF.table_svg(widths, n_rows)            # 표 한 장 전부 (가로·세로·칸마다)
DF.ruled_svg(w_pt, rows)                # 필기칸 괘선 (줄 rows-1 개)
DF.h_cells(x0, x1, ys)                  # 가로 점선 한 칸 폭, 여러 행
DF.v_cells(xs, cells, y0, offset)       # 세로 점선, 칸(행)마다
```

- 감싸는 `<svg>` 에 `fill="none" stroke-width stroke-dasharray` 가 있어야 한다
  (가운데 구간은 dasharray 로 긋는다). `table_svg`/`ruled_svg` 는 이미 붙어 있다
- 좌표는 pt viewBox. 상품 2 의 연결 예: `scripts/app_style.py` 의 `_fade_dashes`,
  `_fade_dashes_vcell`, `flat_lines` (LINE_FADE)
- 값(점 4 / 주기 8 / 페이드 24 / 조각 1pt / 눈금 0.1 / 색 #d3d8de)은 인자로 바꾼다

## 절대 하지 말 것 (전부 실제로 겪음)

| 하지 말 것 | 왜 |
|---|---|
| stroke 에 `linearGradient` 로 흐리기 | PDF 에서 셰이딩 + 소프트마스크 → iPad 바둑판 렌더 (RELEASE.md) |
| 점 **단위**로만 옅게 | 좁은 칸(점 2~3개)은 흐림이 안 보인다 → **1pt 조각**(piece=1) |
| 선 전체의 양 끝만 흐리기 | 사용자 요구는 **칸마다** |
| 흐림 넣으며 점 위치 새로 계산 | 세로선의 행 경계 틈이 깨진다. `v_cells` 는 브라우저 규칙 `(t+offset) mod period < dash` 를 따른다 |
| `opacity` 로 path 전체를 옅게 | 그룹 투명도 = 소프트마스크. `stroke-opacity` 는 고정 알파(/CA)라 괜찮다 |
| 괘선을 CSS `border: dashed` | 점이 작은 사각형으로 나가 27MB (상품 2 실험) |

## 적용 순서

1. 표는 `DF.table_svg`, 필기칸은 `DF.ruled_svg` (또는 기존 코드에서 `h_cells`/`v_cells` 호출)
2. 새 버전 이름 + 플래그로 켠다 (RELEASE.md 3-1). 옛 버전은 바이트까지 재현돼야 한다
3. 빌드 → dedupe → 검사:
   ```bash
   python scripts/check_render.py output/prod<N>/planner_<버전>-FINAL.pdf   # A 셋 다 0, B < 150ms
   ```
   상품 2 는 `verify_student.py` 에 이미 있다: "양 끝 페이드 없는 표",
   "세로선 끝 페이드 없는 표", "양 끝 페이드 없는 필기칸". 다른 상품이면 이 셋을
   옮겨 온다 (HTML 에서 rules svg 에 `stroke-opacity` 가 있는지, 세로 `V` 경로에도 있는지)
4. **눈으로:** 표 모서리와 좁은 칸(DONE 열)을 5배 확대해 전후 비교 이미지를 만든다.
   가운데 진하기를 전후로 재서 같은지 숫자로 확인한다
5. 사용자에게: 비교 이미지는 대화창에, PDF 는 파일로 보낸다

## 비용 (상품 2, 437p)

용량 영향 거의 없음(같은 모양 페이지는 dedupe 가 접는다). 렌더 10회 중앙값
평균 104 → 106ms.
