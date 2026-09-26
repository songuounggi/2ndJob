# 상품 3 — ADHD 날짜형 플래너 2026-2027

방: `Prod 3. Something`. 조사 근거는 `product3-research.md` 6절.

## 0. 타겟과 콘셉트 (2026-09-26 사용자 확정)

**타겟 -- 상품 1 과 같은 사람, 사는 이유가 다르다.** 성인 ADHD, 대략 25~45세, 일·집안일·돈·건강을 직접 굴리는
사람(`listing.md` 타겟). 그중 **날짜가 이미 박힌 플래너**를 찾는 사람.

| | 상품 1 (undated) | **상품 3 (dated)** |
|---|---|---|
| 찾는 말 | adhd planner, undated | **digital planner 2027, adhd planner 2027** |
| 원하는 것 | 언제 시작해도 되는 것, 빈 날짜 죄책감 없음 | 날짜를 직접 적기 싫다. 달력·날짜가 박혀 있고 오늘로 바로 간다 |
| 사는 때 | 아무 때나 | **새해 앞(12~1월) 성수기.** 2026 판은 "지금 남은 석 달" |

근거: `digital planner 2027` 상위 10개 하루 50건, ADHD 날짜형 경쟁작 7/일 × $10.99 (측정한 리스팅 중 매출 1위).
**상품 1 과 서로 뺏지 않는다** -- 날짜형을 찾는 사람은 undated 를 안 사고 반대도 같다.

**콘셉트** -- *The ADHD Year: one small experiment a week. By December, a user manual for your own brain.*
경쟁작은 "페이지 수 + 스티커"를 판다. 우리는 **1년 동안 진행되는 이야기**를 판다. 날짜형이라 가능한 세 장치:
① 52 Experiments (주마다 전략 하나 → 12월 Playbook) ② Time Links (오늘↔내일, 30일 뒤 도착 메모)
③ 보이는 시간 (`Day 74 · 291 left`, 시간맹). 쪽수로 겨루지 않는다(상품 1 리뷰 최다 불만 "너무 많아 못 찾겠다").

**경쟁작 대비 보강 (사용자 확정, 진행 중):** 5번째 파일에 **스티커**(독창적으로 -- 우리 장치에 맞춘 것) +
**Goodnotes 설치 안내**. 우리만 있는 것: 52 experiments, Time Links, SOS, 전 세계 공통 날짜, 8.5mm 누르는 영역, 7.7MB.

## 결정 (2026-09-25, 사용자 확정)

| 항목 | 값 |
|---|---|
| 상품 | **The ADHD Year — 날짜형(dated)**. ~~상품 1 디자인·템플릿 그대로~~ → **디자인은 사용자의 Lifted Paper 핸드오프**(2026-09-25), 내용은 `product3-content.md`, 상품 1 도구 44장은 문구만 가져옴 |
| 기간 | **2026년 1~12월 / 2027년 1~12월, 연도별 PDF.** 미드이어(7월·9월 시작)는 안 한다 — 해를 걸치면 애매하다(사용자) |
| 판매 | **한 리스팅에 묶어서** "2026-2027". 2026 은 지금 당장 쓰려는 사람용(남은 석 달), 2027 이 본품 |
| 주 시작 | **월요일 시작 / 일요일 시작** 두 판 |
| 파일 | PDF 4개(2026-월, 2026-일, 2027-월, 2027-일) + **5번째: 스티커 + Goodnotes 설치 안내 ZIP** (진행 중) ≤ Etsy 5개·각 20MB |
| 가격 | **정가 $19.99, 런칭 세일 35% = $12.99** (2026-09-26 확정, `listing-p3.md`) |

### 근거 한 줄씩
- `digital planner 2027` 상위 10개가 하루 50건. 올해+내년 묶음("2026, 2027, 2028")이 하루 24건
- ADHD 라벨 날짜형(Manifestable 2026-2027)이 **$10.99 × 7/일** — 측정한 리스팅 중 매출 1위
- 날짜형 수요는 12~1월(약한 근거). 10월 중순 등록이면 자리 잡는 3~6주를 채운다

## 경쟁작 기준선 — Manifestable "ADHD Planner 2026-2027"

709p / 미드이어 2026.7~2027.6 / 주간 레이아웃 4종 / 월·일 시작 PDF 2개 / 스티커 200+ ZIP /
설치 안내 PDF / 리뷰 217(4.8). 우리 v8.20 은 502p, 고유 61종.

## 구조

| 키 | 페이지 | 링크 |
|---|---|---|
| `year-grid` | 연간 달력 한 장(미니 달력 12개) | 월 이름 → `m{월}`, 날짜 → `d{월}-{일}` |
| `month` | 열두 달 목차 | → `m1`~`m12` |
| `m{월}` | 실제 요일에 맞춘 월 달력 | 날짜 → 일간, 주 번호 → 주간 |
| `week` | 주 목차 | → `w{n}` |
| `w{n}` | 주간(그 주 7일에 날짜) | 요일 칩 → 그 날 일간 |
| `d{월}-{일}` | 일간(날짜 박힘) | 머리 칩 → 그 달, 그 주 |

키 모양은 undated 와 같다(`m`/`d`/`w`) → `rail_key()`·탭 하이라이트 규칙을 그대로 탄다.
주는 **그 해에 걸친 주 전부**(1월 1일이 든 주 ~ 12월 31일이 든 주). 해 밖의 날은 날짜만 흐리게, 링크 없음.

## 코드

| 파일 | 역할 |
|---|---|
| `scripts/dated_pages.py` (새 파일, 이 방 소유) | 날짜형 반복 세트·표지·목차 |
| `scripts/build_planner.py` (**공유**) | THEMES 등록 + `import dated_pages` 훅. 상품 1·2 출력은 바이트 단위로 그대로여야 한다 |

버전: `dated-v0.1-{2026|2027}-{mon|sun}` → `output/planner_dated-v0.1-2027-mon.pdf` 등 (지금은 `output/prod3/archive_dated-v0.1/`).
테마는 `v8.20-undated` 를 상속(`fast_paint`, `vector_dots` 켜짐) + `dated`, `year`, `week_start`.

## 진행

- [x] 코드: `dated_pages.py` + 훅 (2026-09-25)
- [x] 공유 파일 회귀: 상품 1 `v8.20-undated`·상품 2 `student-v1.1` 의 HTML 이 수정 전과 **바이트 동일** (`cmp`)
- [x] 4판 빌드 + dedupe: 전부 **496p / 약 16.48MB** (고정 65 + 월 12 + 일 365 + 주 목차 1 + 주 53)
- [x] `verify_dated.py` 14항목 4판 전부 통과. 검사기 자체 확인: 월요일판을 일요일판이라 치면 요일 418건,
      2026판을 2027판이라 치면 783건 + 연도, 8/15 링크 하나 지우면 `d8-15 <- m8` 로 잡힌다
- [x] `check_lines.py` 11항목 / `check_render.py` 4판 전부 통과

| 판 | 크기 (B) | 렌더 평균 / 최대 | A-1·2·3 |
|---|---|---|---|
| 2026-mon | 16,481,551 | 61 / 74 ms | 0·0·0 |
| 2026-sun | 16,479,970 | 63 / 82 ms | 0·0·0 |
| 2027-mon | 16,478,499 | 59 / 73 ms | 0·0·0 |
| 2027-sun | 16,480,974 | 60 / 73 ms | 0·0·0 |

다시 뽑기: `PLANNER_VERSION=dated-v0.1-2027-mon python scripts/build_planner.py` →
`python scripts/dedupe_pdf.py output/planner_dated-v0.1-2027-mon.pdf output/planner_dated-v0.1-2027-mon-FINAL.pdf` →
`python scripts/verify_dated.py dated-v0.1-2027-mon`
- [ ] 렌더 눈 검수 → 사용자
- [ ] iPad 실기기 (RELEASE.md)
- [ ] 리스팅 원고·이미지·가격

## 역할 분담 (2026-09-25, 사용자 확정)

**디자인은 사용자가 직접 한다. Claude 는 내용(페이지 구성·문구·데이터) 계획과 생성만.**
내용 계획은 `product3-content.md`, 문구 데이터는 `scripts/p3/p3_content.py`.
Claude 가 만든 시안·색·레이아웃은 결정 사항이 아니다.

## 디자인 차별화 (2026-09-25) — 사용자에게 넘어감

사용자: "상품 1 과 배경·개체가 너무 똑같다. 획기적인 아이디어를." → dated-v0.1 은 **올리지 않는다**(구조·검사는 그대로 재사용).

| 시도 | 결과 |
|---|---|
| 색만 바꾼 시안(Night 다크 / Sunrise 웜톤 / 월 탭) | **반려** — "1·4 는 거의 같고 3 은 하늘색만 뺀 것". 다크 모드는 `dark mode digital planner` 상위 10개 하루 3건 → 새 디자인감이 아니라 나중에 라이트+다크 **세트 옵션** 정도 |
| 새 콘셉트 4종 (일간·월간 시안, 아래) | 참고용으로만 남김 |

| | 콘셉트 | 핵심 |
|---|---|---|
| A | Clockwise | 일간 = 24시간 원형 다이얼(안 = 계획, 밖 = 실제) + 예상 vs 실제 표. 시간맹(time blindness) |
| B | Quest Log | DAY 68 / XP 바 / 에너지 하트 / 메인·사이드 퀘스트 / 물약·보물상자. 월간 = 31일 월드맵 + 주간 깃발 + 월말 보스. 게임화 |
| C | Bold | 네오 브루탈리즘. 굵은 외곽선, 원색 블록, 딱딱한 그림자, 거대한 날짜 숫자 |
| D | Notebook | 불렛저널. 스프링 구멍, 점지 전면, 튀어나온 인덱스 탭, 손글씨 제목, 마스킹테이프·포스트잇 |

시안 스크립트: `scripts/p3/concepts_p3.py` (저장소 밖 스크래치에서 옮겨 둠). 콘셉트 키워드 자체는 검색 수요가 없다
(`gamified planner`·`time blindness planner` 상위에 전용 상품 없음) — 파는 키워드는 여전히 `adhd planner 2027`,
콘셉트는 썸네일·스토리 차별화용.

## 파이프라인 분리 (2026-09-25, 사용자)

상품 3 은 `scripts/p3/` 만 쓴다. `build_planner.py` 의 상품 3 훅을 걷어내 `eb3f67e` 직전으로 되돌렸고,
상품 1 `v8.20-undated`·상품 2 `student-v1.1` HTML 이 상품 3 작업 전 기준선과 **바이트 동일**(cmp)함을 확인했다.
위 dated-v0.1 절은 기록이다 — 코드는 `archive/p3_dated_v0.1/`. 규칙은 `scripts/p3/README.md`.

## 디자인 확정본 → 에디션 PDF (2026-09-25)

사용자 디자인 "Lifted Paper"(핸드오프 `ADHD Planner 디자인 컨셉_v0.1/`) → `python scripts/p3/editions_build.py`.
결과·문제점은 `output/prod3/editions/<버전>/check_report.json`, 보고는 대화 기록.

## 출시 체크리스트 — 판매용 플래너 v0.7 (2026-09-26, `RELEASE.md` 1절 기준)

파일: `output/prod3/planner/v0.7/ADHD-Year-Planner-{2026,2027}-{mon,sun}.pdf` (각 598쪽, 7.7MB)

### 1-1. 자동 검사 — 전부 돌렸다

| 검사 | 명령 | v0.7 |
|---|---|---|
| 구조·링크·시간 링크·폰트·누르는 영역·레이아웃 | 빌드가 함께 돈다 (`planner_build.py`) | 통과 (깨진 링크 0) |
| 전수 레이아웃 (잘림·넘침·겹침·발문·삐져나옴, 598쪽 × 4) | `python scripts/p3/audit_layout_p3.py v0.7` | **0건** |
| 리스팅 원고 ↔ 파일 | `python scripts/p3/check_listing_p3.py v0.7` | ALL OK |
| 뷰어 위험·속도·용량 | `python scripts/check_render.py output/prod3/planner/v0.7/ADHD-Year-Planner-2027-mon.pdf` | A 0·0·0, D 7.7MB 통과. **B 렌더 최대 209ms — 기준 150ms 미달** |

**B 는 알고 가는 미달이다.** 원인은 배경 이미지(2×, 핸드오프 README 지정) -- 페이지 시간의 ~90ms.
사용자가 2× 유지로 결정(2026-09-25), 7쪽 버벅임은 "괜찮은 듯, 스킵"(2026-09-26).
RELEASE.md 는 전부 통과를 요구하므로 **iPad 확인(아래 2번)을 사용자가 통과시켜야** 올린다.
비교용: `output/prod3/ipad-test/v0.4-background/TEST-bg-{2x-now,1.5x}-p1-40.pdf` (1.5× = 98ms, 픽셀 차이 평균 0.06).

### 1-3. iPad 실기기 — 사용자 (GoodNotes, `2027-mon` 한 판으로)

| # | 할 일 | 페이지 (2027-mon) | 볼 것 |
|---|---|---|---|
| 1 | GoodNotes 에서 열기 | | 오래 걸리지 않는가, 598쪽인가 |
| 2 | 1~30쪽 빠르게 넘기기 | 1–30 | 바둑판처럼 늦게 채워지지 않는가 (**B 미달이라 가장 중요**) |
| 3 | **오른쪽** 탭 10개를 하나씩 | 아무 쪽 | 전부 이동하는가, 지금 탭이 진한 청록인가 |
| 4 | YEAR 탭 → 날짜 하나 | 5 → 일간 | 2탭에 그날로 가는가 |
| 5 | 일간 맨 아래 `Tomorrow →` / 위 `From yesterday ←` | 25 (1/1), 26 | 다음 날·전날로 가는가 |
| 6 | 일간 `Arrives … →` | 25 | 30일 뒤(1/31)로 가는가 |
| 7 | MONTH → January → 날짜 | 21 → 22 | 달력 칸 아무 데나 눌러도 그날로 가는가 |
| 8 | 도트·격자 노트 확대 | 595, 598 | 흐리거나 간격이 이상하지 않은가 |
| 9 | 펜으로 몇 줄 | 583 Monthly budget | 34px 줄에 쓰기 편한가 |

**사용자 확인 (2026-09-26, v0.7):** "스크롤이 아주 가끔 뚝뚝 거리지만 큰 이상은 없다." -- **아이폰 미리보기(파일 앱)** 에서 본 것. iPad GoodNotes 확인은 아직.
원인 후보는 배경 2× (B 미달과 같은 원인). 같은 기기에서 `ipad-test/v0.4-background/` 두 파일을 비교해 1.5× 로 바꿀지 사용자가 정한다.

바뀐 페이지 (v0.3 이후): 9 Life admin radar · 13 Where I put it · 15 Project planner · 22/331/400 달력(1·10·12월) ·
89·106 (3월 달력, 3/15 NCW) · 24 Brain weather · 540 53주차 · 544 Year review · 556·567·570·583·585·586·588 입력 줄.

### 올릴 때 (아직 하지 않는다)

- Etsy 파일 이름 **제안** (사용자 확정 필요, RELEASE.md 3-3): `ADHD-Year-Planner-2027-Monday-start.pdf` 처럼
  `mon`/`sun` 을 풀어 쓴다 -- 구매자가 받는 이름이라 약어가 헷갈린다. 70자 이내, 영숫자 `.` `_` `-`
- 올린 판은 `output/prod3/upload/v0.7/` 에 복사, `shop.md` 0-1절 이력표에 한 줄
- 가격: 정가 $19.99, 런칭 세일 35% = $12.99 (`listing-p3.md`)

## 설치 안내서 근거 (2026-09-26 조사, 공식 도움말만) — `scripts/p3/guide_p3.py`

| 안내서 문장 | 출처 | 비고 |
|---|---|---|
| Etsy 앱은 디지털 파일을 못 받는다, Safari 로 Your account → Purchases → Download Files | help.etsy.com 115013328108 (2026-09-26) | iPad Safari 의 정확한 탭 경로는 미확인 |
| 다운로드 횟수 제한 없음 / 폰·태블릿은 파일 관리 앱으로 ZIP 풀기 | 같은 글 | |
| 파일 앱에서 ZIP 탭 → 폴더 생성 | support.apple.com 102532 | |
| Open in Goodnotes → New Document → Import to… / + New → Import → Open | support.goodnotes.com 7353717816463 (2026-05-22) | |
| **무료 Goodnotes: 노트 3개, 파일당 5MB** | 같은 글 (원문 직접 확인) | 우리 PDF 7.7MB -- 안내서·리스팅에 명시 (A안, 사용자 확정 대기) |
| 링크: 그냥 탭. 선이 그어지면 Read Only Mode(Nav Bar 아이콘) 또는 길게 눌러 Open Link | 13623343439631, 7353757120655 (2026-09) | |
| 스티커: Elements → 목록 끝 + → 이름 → Import from… → Create | 7353727577359 (2026-09-16) | **투명 PNG 유지 미확인** -- 사용자 iPad 확인 |
| Notability: +New → Import | support.gingerlabs.com 206061357 | Notability 링크 동작은 미확인이라 약속하지 않는다 |
