# scripts/p3 — 상품 3 전용 파이프라인 (Prod 3 방 소유)

**상품 1·2 와 코드를 나누지 않는다** (2026-09-25 사용자: "다른 Prod 1, Prod 2 에 영향을 끼치면 안 되니").

| 규칙 | |
|---|---|
| `scripts/build_planner.py` · `student_pages.py` · `app_style.py` | **import 하지 않는다. 고치지 않는다.** 상품 1·2 의 것이다 |
| 공용 도구 `dedupe_pdf.py` · `check_render.py` | 읽기 전용으로 **호출만** 한다(파일을 인자로 넘겨 실행). 고칠 일이 생기면 여기로 복사해서 고친다 |
| 출력 | `output/editions/` · `output/p3_*` · `src/editions/` · `src/p3_*` — 상품 1·2 파일명과 겹치지 않는다 |

## 파일

| 파일 | 하는 일 |
|---|---|
| `editions_build.py` | 디자인 핸드오프(`ADHD Planner 디자인 컨셉_v0.1/design_handoff_adhd_planner_pdf/`)의 레퍼런스 HTML 을 Playwright(설치된 Chrome)로 열어 에디션별 PDF 4개를 만든다 |
| `editions_check.py` | 핸드오프 README 체크리스트 자동 검사 + 레퍼런스 스크린샷과 픽셀 비교 |
| `p3_content.py` | 날짜형 1년 플래너 문구 원본(질문 371·실험 53·테마 12 …) + 검사 + CSV |
| `p3_wireframe.py` | 위 문구로 1년치 와이어프레임 PDF(598p) + Time links 검사 |
| `concepts_p3.py` | 반려된 디자인 콘셉트 시안(참고용) |

```bash
python scripts/p3/editions_build.py      # -> output/editions/*.pdf
python scripts/p3/editions_check.py      # README 체크리스트
python scripts/check_render.py output/editions/ADHD-Planner-Focus-Edition.pdf   # GoodNotes 위험
```

필요: `pip install playwright` (브라우저는 받지 않는다 — `channel="chrome"` 으로 설치된 Chrome 사용).

## 폐기된 것

`archive/p3_dated_v0.1/` — 상품 1 모양 그대로 달력만 날짜로 바꾼 첫 시도(dated-v0.1). "상품 1 과 너무 똑같다"로
반려(2026-09-25). `build_planner.py` 에 훅을 넣어야 돌아가는 구조였고, 그 훅은 이번 분리 때 걷어냈다.
다시 돌리려면 커밋 `eb3f67e` 로 worktree 를 떠서 빌드한다.
