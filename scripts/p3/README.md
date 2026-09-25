# scripts/p3 — 상품 3 전용 파이프라인 (Prod 3 방 소유)

> **디자인은 사용자 것이다. 디자인에 영향을 주는 것은 사용자와 상의하기 전에 절대 건드리지 않는다** (2026-09-25).
> 선·간격·모양·색·굵기·배치, 요소를 더하거나 빼는 것 전부. 요청받은 속성만 고친다("간격" = 간격만).
> 그 밖에 필요해 보이면 렌더 이미지와 함께 **제안만** 하고 승낙을 기다린다. 애매하면 디자인으로 본다.
> 내용·논리(문구·링크·날짜·이스케이프·검사·빌드 도구)는 고치고 **무엇을 고쳤는지 말만** 하면 된다.
> 계기: 기록표 행 간격만 맞추랬는데 세로선·동그라미를 멋대로 넣었다 -> 전부 원복(`b361a3a`).

**상품 1·2 와 코드를 나누지 않는다** (2026-09-25 사용자: "다른 Prod 1, Prod 2 에 영향을 끼치면 안 되니").

| 규칙 | |
|---|---|
| `scripts/build_planner.py` · `student_pages.py` · `app_style.py` | **import 하지 않는다. 고치지 않는다.** 상품 1·2 의 것이다 |
| 공용 도구 `dedupe_pdf.py` · `check_render.py` | 읽기 전용으로 **호출만** 한다(파일을 인자로 넘겨 실행). 고칠 일이 생기면 여기로 복사해서 고친다 |
| 출력 | **`output/prod3/`** 와 `src/prod3/` 아래에만 쓴다 (2026-09-25 사용자: output 을 상품별로) |

## 파일

| 파일 | 하는 일 |
|---|---|
| `editions_build.py` | 디자인 핸드오프(`ADHD Planner 디자인 컨셉_v0.1/design_handoff_adhd_planner_pdf/`)의 레퍼런스 HTML 을 Playwright(설치된 Chrome)로 열어 에디션별 PDF 4개를 만든다 |
| `editions_check.py` | 핸드오프 README 체크리스트 자동 검사 + 레퍼런스 스크린샷과 픽셀 비교 |
| `p3_content.py` | 날짜형 1년 플래너 문구 원본(질문 371·실험 53·테마 12 …) + 검사 + CSV |
| `p3_wireframe.py` | 위 문구로 1년치 와이어프레임 PDF(598p) + Time links 검사 |
| `concepts_p3.py` | 반려된 디자인 콘셉트 시안(참고용) |

```bash
python scripts/p3/editions_build.py      # -> output/prod3/editions/*.pdf
python scripts/p3/editions_check.py      # README 체크리스트
python scripts/check_render.py output/prod3/editions/ADHD-Planner-Focus-Edition.pdf   # GoodNotes 위험
```

필요: `pip install playwright` (브라우저는 받지 않는다 — `channel="chrome"` 으로 설치된 Chrome 사용).

## 폐기된 것

`archive/p3_dated_v0.1/` — 상품 1 모양 그대로 달력만 날짜로 바꾼 첫 시도(dated-v0.1). "상품 1 과 너무 똑같다"로
반려(2026-09-25). `build_planner.py` 에 훅을 넣어야 돌아가는 구조였고, 그 훅은 이번 분리 때 걷어냈다.
다시 돌리려면 커밋 `eb3f67e` 로 worktree 를 떠서 빌드한다.

## 레퍼런스와 다르게 한 것 (사용자 요청·결함 수정)

| 무엇 | 왜 |
|---|---|
| **종이+탭 묶음을 페이지 가운데로** (왼쪽으로 13px, 좌우 여백 25px) | 사용자: 탭이 우측에 쏠려 누르기 어렵다. 배경은 옮겨 다시 굽고(`shift_background`) 오른쪽 띠는 끝 열을 늘려 채운다 — 책상색으로 칠하면 모서리 그림자에서 이음매가 생긴다 |
| 탭 그림자 = 구운 PNG | 블러 box-shadow 가 페이지당 소프트 마스크 10개 → GoodNotes 바둑판 위험 |
| 폰트 = Google Fonts 정적 WOFF | 가변 폰트는 Chrome 이 Type3 로 넣는다 |
| `→` = SVG | Source Serif 4 에 없는 글리프 (맑은 고딕으로 대체됐다) |
| inset box-shadow 선 → border/outline | 표 페이지 렌더 267ms. 크기가 1px 이라도 바뀌면 되돌림(0건) |
| 페이지 없는 탭 → Home, Directions 의 Home/Day = 그 방향의 표지/일간 | README "Tabs" |

## output/prod3/ 지도 — 버전마다 폴더, 절대 덮어쓰지 않는다

2026-09-25: 같은 이름으로 다시 빌드해 첫 판을 덮어쓴 적이 있다(사용자: "절대 지우면 안돼").
빌드 스크립트는 이미 있는 버전 폴더면 멈춘다(`refuse_overwrite`) -- 고치면 `VERSION` 을 올린다.

| 폴더 | 담는 것 | 만든 커밋 |
|---|---|---|
| `editions/v0.1/` | 에디션 4종 첫 판 (핸드오프 그대로, 탭 오른쪽) | `6f73359` |
| `editions/v0.2/` | 종이+탭 묶음 가운데 정렬 (좌우 25px) | `7e70a83` |
| `wireframe/v0.1/` | 날짜형 와이어프레임 597p (미국 공휴일) + 문구 CSV | `490fee2` |
| `wireframe/v0.2/` | 598p (공통 공휴일 + My holidays) + 문구 CSV | `33495b6` |
| `archive_dated-v0.1/` | 상품 1 모양 날짜형 첫 시도 8판 (반려) | `eb3f67e` |
| `archive_color-mocks/` | 색만 바꾼 시안 5종 PDF+PNG (반려) | `490fee2` 트리에서 재생성 |
| `archive_concepts-A-D/` | 새 콘셉트 4종(시계·퀘스트·볼드·노트북) HTML·PDF·PNG (참고용) | `concepts_p3.py` |
| `preview/` | 검수용 렌더 PNG | |
| `upload/<버전>/` | (앞으로) Etsy 에 올린 판. 한 번 넣으면 건드리지 않는다 | |
