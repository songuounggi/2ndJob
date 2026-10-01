# 상품 4 — 기획서 (2026-09-30 사용자 확정)

## ▶ 지금 어디까지 — 인계 (2026-10-01, 회사 PC `Prod 4. The ADHD Home Reset` -- 옛 이름 `Prod 4. Something`)

방 이름: 회사 `Prod 4. The ADHD Home Reset` / 집 **`Prod 4. The ADHD Home Reset (Home)`** (10-01 사용자, 상품 이름 확정으로)

**다른 방·다른 PC 는 여기부터 읽는다.** 이 절 아래의 긴 기록은 그날 무슨 일이 있었는지이고, 할 일은 여기에만 모았다.

### 단계 (`PROCESS.md` 10단계)

| 단계 | 상태 |
|---|---|
| 1 시장 조사 | **통과** -- 사용자가 H-a(청소·루틴, 입구 가격) 선택 (`product4-research.md`) |
| 2 기획서 | **통과** -- 구조·결정 6건 + 문구 원고(`scripts/p4/p4_content.py`) 사용자 확인 |
| 3 디자인 | **통과** -- 상품 1 모양 + 섹션마다 한 색(아래 색 확정표). **10-01: 사용자가 claude.ai/design 에서 전체 시안을 다시 만드는 중 → 받으면 3단계부터 다시** |
| 4 제작 | **통과** -- 전체 빌드 v0.1 → v0.9 |
| 5 검수 | **통과** -- 자동 검사 전부 0, 새 문구 119개 사용자 확인 |
| 6 직접 써 보기 | **통과** -- 시나리오 12개 막힌 곳 0 (Routines 목차 추가로 108쪽) |
| **7 iPad 검수** | **대기 -- 집에서 (iPad 가 집에 있다)** |
| 8 리스팅 | 원고 초안 `listing-p4.md` (제작과 나란히). 결정 3건 대기 |
| 9 출시 · 10 알리기 | 아직 |

### ★★ 디자인 v1.0 이 최신 (2026-10-01 18:32) -- **이걸로 작업한다**

- **`design/prod4/the-adhd-home-reset-design-v1.0.zip`** (3.8MB, 82개). 아래 v1(18:02)은 옛것
- 안: `README.md`(디자인 인수인계서) · **`pages_turn25.html`**(전체 디자인 HTML) · `reference/`(CLAUDE_prod4.md, background_bake.js, 메모 1개)
  · `assets/` · **`screenshots/p001_cover.jpg` ~ `p107_notes-blank_p107-108.jpg`** -- 쪽 번호가 붙어 있어 108쪽 지도와 바로 짝지어진다
- 진행 (10-01 19시~): **README·reference 2개·HTML 구조 정독 완료.** 요점 --
  정답 그림 = `screenshots/p###` 38장 / `assets/25-*.jpg` = 배경 재료(번짐·유리 탭·켜진 탭·SOS·카드 그림자·배너 번짐을 구운 JPG) /
  정확한 수치 = `pages_turn25.html`(쪽마다 612×792 상자, 배경 JPG 위에 글자·선·체크를 pt 절대 좌표로, 스크립트·그라데이션·그림자 CSS 0) /
  우선순위 README 규칙 > HTML 수치 > 그림. 문구는 확정 원고 그대로(대소문자·줄 나눔만 다름, 39쪽 힌트만 "next slot" 으로 짧아짐).
  HTML 링크는 대부분 `href="#"` 자리표시(일부 #p3 #p37 #p91 #p100 은 쪽 번호가 1씩 어긋남) -- 링크는 우리 페이지 key 로 다시 건다.
  화살표 → ← 112곳은 글자라 Nunito 에 없어 대체 글꼴로 찍힌다 -- 우리 쪽에서 해결(웹 글꼴 지정 또는 SVG).
- 질문 대기: ① 39~90쪽 Reset week 에 "← Previous week" 넣을지(시안은 Next 만) ② 39쪽 힌트 "next slot" vs 확정 "no penalty, just the next slot"
  ③ 흑백 인쇄판 방식(시안은 컬러뿐 -- 그림자·유리 탭이 배경 JPG 에 구워져 있다)
- 다음: 압축 풀기 → README·reference·HTML 정독 → 질문 모아 묻기 → 표본 → v0.10 → 검사 일곱 줄

### (옛것) 디자인 시안 v1 도착 (2026-10-01 18:02, 사용자 "심혈을 기울여 완성")

- 파일: **`design/prod4/the-adhd-home-reset-design-v1.zip`** (git 에 있다 -- 집 PC 는 `git pull` 만). 1.35MB, 44개
  - `design_handoff_adhd_home_reset/README.md` -- **디자인 쪽 인수인계서 (25KB). 이걸 처음부터 끝까지 읽는다**
  - `assets/25-*.jpg` 39장 -- 페이지 종류별 시안 (cover·flow·start·housemap·index·energy·battery·kitchen·deep·myroom·roomslist·
    routinesIdx·daily·rotation·monthly·seasonal·loop·who·kids·weeks·week·toolsIdx·rescue·sprint·guests·doom·declutter·where·restock·
    dopamine·body·wins·timeg·projects·moving·lined·dots·blankp 등) + `card-shadow.png`
- 원본: 회사 PC `Desktop\MyWork\99.Indivisual\2ndJob\Prod 4\The ADHD Home Reset 프로젝트.zip`
- **다음 (3단계 다시 → 4단계 v0.10)**: ① 압축을 풀어 README 를 끝까지 읽는다 ② 시안 39장을 지금 108쪽 페이지 목록과 짝짓는다
  ③ **구현 전에 질문을 모아 한 번에 묻는다**(시안에 없는 페이지, GoodNotes 에서 깨지는 효과, 문구가 달라진 곳) ④ 답을 받고 표본 →
  전체 빌드 v0.10 → 검사 일곱 줄. 확정 문구·108쪽 구조·링크는 README 가 바꾸라고 하지 않는 한 그대로
- 사용자 토큰이 모자라 **받아 두기만** 했다 -- 내용은 아직 안 읽었다

### 집 PC 에서 먼저 할 일 (순서대로)

1. `git pull` → **다시 빌드** (output·src 는 git 밖이라 따라오지 않는다):
   ```bash
   python -c "import pypdfium2, pikepdf, pymupdf, playwright"
   python scripts/p4/build_p4.py full
   ```
   → `output/prod4/planner/v0.9/home-reset_v0.9_color-FINAL.pdf` · `…_BW-FINAL.pdf` (108쪽, 각 3.4~3.5MB).
   번짐·그림자 PNG 는 없으면 스스로 만든다. Chrome 은 `chrome_auto` 로 켠다(계정 잠김 방지).
2. **검사 일곱 줄** (전부 0 / 통과여야 한다 -- 회사 PC 에서 v0.9 는 전부 통과. 마지막 줄은 10-01 추가: 문서와 판의 모순):
   ```bash
   python scripts/p4/check_p4.py v0.9
   python scripts/check_lines.py src/p4_home-reset_v0.9_color.html
   python scripts/check_lines.py src/p4_home-reset_v0.9_BW.html
   python scripts/check_render.py output/prod4/planner/v0.9/home-reset_v0.9_color-FINAL.pdf
   python scripts/p4/dogfood_p4.py v0.9
   python scripts/p4/check_listing_p4.py v0.9
   python scripts/p4/check_docs_p4.py v0.9
   ```
3. **7단계 iPad 확인** -- 컬러판을 GoodNotes 로 열어 사용자가 본다:
   - 아무 쪽이나 빠르게 넘기기: 바둑판처럼 늦게 채워지지 않나
   - 1쪽 제목 → 2쪽 → "Open the planner" → 3쪽 → "Check your battery" → 6쪽
   - 아무 쪽 오른쪽 위 **SOS** → 92쪽 Rescue mode
   - 106쪽 Notes (dot grid): 점이 촘촘하고 또렷한가 (상품 1 에서 깨졌던 곳)
   - 결과는 이 절에 날짜·기기·앱과 함께 적는다

### 사용자 결정 대기

| # | 무엇 | 선택지 / 자료 |
|---|---|---|
| 1 | **디자인 전체 시안** (순서도만이 아님, 10-01 사용자) | 사용자가 claude.ai/design 에서 작업 중 (10-01 "거의 끝나간다"). 색은 **섹션별 4색 한 가지로**(아래 10-01 결정). 인수인계서 `product4-design-handoff.md` **v0.2**, 그림 `output/prod4/handoff/flow-v0.2/`(회사 PC 에만 -- 집에서 필요하면 v0.9 빌드 뒤 컬러판 1·2·3·6·11·29·92쪽을 PNG 로 렌더해서 쓴다. 파일 구성은 인수인계서 6절). 시안 색은 섹션별 4색 한 가지 (10-01 정정 -- 처음엔 두 방식을 요청했었다) |
| ~~2~~ | ~~색: 섹션별 4색 vs 민트 한 색 시리즈~~ | **결정 (10-01): 섹션별 4색 유지.** 시리즈안은 접는다 |
| 3 | 리스팅 런칭 세일 | Etsy 는 정수 % -- **22% = $7.01** / **23% = $6.92**, 기간(상품 3 은 30일) |
| 4 | 리스팅 제목 | 긴 안(14단어) / 짧은 안(9단어) -- `listing-p4.md` |
| 5 | 리스팅 설명 검토 | `listing-p4.md` |
| 6 | 새 문구 2줄 | 29쪽 Routines 목차: "Routines" / "The small repeats that keep it from piling up." |
| 7 | 디렉토리 이름 규칙 | 사용자가 손보겠다고 함(버전 폴더 9개·`-FINAL` 유무가 헷갈림). 다른 방과 같이 쓰는 규칙이라 바꿀 때 알린다 |
| 8 | 상품 1~3 표 위아래 비대칭 | 상품 4 는 고쳤다. 출시본은 버전을 올려야 해서 결정 전 (`LINES.md` 2절) |

### 수익 재점검 (2026-10-01, 사용자 요청 "기획 자체가 수익을 극대화할 메리트가 있는지")

| 점검 | 결정 |
|---|---|
| 맨 끝 1쪽 "리뷰 부탁 + 상품 1·2·3 소개 + 숍 링크" (입구 상품 → 중간 칸 연결) | **넣지 않는다** (사용자). 108쪽 그대로. 다시 꺼낼 때: Etsy 는 리뷰 요청 허용·보상 조건 금지, 디지털 파일 안 자기 숍 링크 공식 문구는 미확인 |
| 색: 섹션별 4색 vs 민트 한 색 "Reset 시리즈"(+ 번들 고가 칸) | **섹션별 4색 유지** (사용자). 시리즈·번들은 나중에 따로 |
| 판매 계획: 시즌 훅 + 가격 시험 | **기획서에 적는다** (사용자) -- 아래 |

**판매 계획 (페이지는 그대로, 핀·가격만)**

| 언제 | 훅 | 쓰는 페이지 | 할 일 |
|---|---|---|---|
| **11~12월** | 연말 손님맞이 (Thanksgiving·Christmas hosting) | 94쪽 Guests in 2 hours | 출시를 **10월 중·하순**으로 -- 핀이 퍼지는 데 몇 주(`pinterest.md`). 손님맞이 핀 |
| **1월** | 새해 home reset | 6쪽 Energy menu · 2쪽 순서도 | 새해 리셋 핀 |
| **3월** | spring cleaning | 33쪽 Seasonal reset · 방 카드 깊은 청소 | 봄맞이 청소 핀 |

태그 교체(시즌 검색어로)는 하지 않는다 -- `CLAUDE.md` "한 번에 하나씩만 바꾼다", 조회 100 전 판단 금지와 부딪힌다. 시즌은 **핀**으로 탄다.

**가격 시험**: 출시가 $8.99(런칭 세일). **리뷰 5개가 쌓이면 $9.99 로 올려 본다** -- 건당 순익 약 +12%(계획값, 근거 없음).
판정은 올리기 전·후 같은 기간 조회·전환을 `forecast.md` 에 적어 비교한다.

### Claude 가 이어서 할 일

- 전체 시안이 오면 **받은 인수인계서를 끝까지 읽고 질문을 먼저 모은다** → 답을 받은 뒤 표본 → 전체 빌드(v0.10) → 검사 일곱 줄
- 리스팅 사진 10장 (`listing-p4.md` 계획) -- 순서도 확정 뒤
- Etsy 재측정 33개 키워드 (`product4-research.md` 0절) -- **한 번에 하나, 350ms 간격** (동시 요청으로 접근이 막혔었다)
- 9단계 전에 `forecast.md` 에 예상치 (판정 기준: 12월 말까지 조회 100)

### 이날 배운 것 (메모리·절차서에 남김)

작업할 때마다 **지금 몇 단계인지 먼저 말한다** · 번호 코드(1-A 등)는 쓰지 않거나 범례부터 · 인수인계서에는 **값이 아니라 규칙**을
· 파일 위치를 물으면 **경로와 탐색기만**(편의용 사본을 만들었다가 지움) · 새 상품은 `LINES.md` 0절을 먼저 읽고 `check_lines` 를 매 빌드.

---

**상태 기록 (2026-09-30):** 구조·결정 6건 확정, 3단계 색 확정. **4절 문구 원고는 사용자 확정 전 -- 이것이 끝나야
2단계 통과**(`PROCESS.md` 2단계: 원고 없이 통과시켰다가 사용자 질문으로 되돌림). 원고: `scripts/p4/p4_content.py`.
확정 뒤 바뀐 것은 날짜와 함께 이 파일에 적는다. *(→ 그 뒤 문구 확인, 2~6단계 통과. 위 "지금 어디까지"가 최신)*
근거: `product4-research.md` (조사·결정). **디자인은 사용자, 내용은 Claude** -- 이 파일은 "무슨 페이지에 무엇이
들어가는가"만 정한다. 색·모양·배치는 3단계에서 사용자가 정한다.

---

## 0. 한 줄 콘셉트

> **The ADHD Home Reset — clean by energy, not by schedule.**
> 오늘 배터리와 남은 시간에 맞는 청소 한 가지를 고르고, 방 하나를 10분 안에 "이 정도면 됐다"까지.
> 탭 한 번이면 **"집이 엉망이다" 구조 페이지**로 간다.

**가격 사다리에서 입구 칸이다**(`CLAUDE.md`). 목적은 리뷰·판매 이력, 그리고 상품 1 과 다른 검색어.
그래서 **작고 바로 쓸 수 있어야 한다** -- 경쟁 리뷰에 "300쪽은 처음에 압도적"이 있었다(조사 2절).
상품 1(502쪽)과 반대로 간다: **108쪽, 표지 다음 순서도 한 장이면 무엇을 할지 보인다.**

### 경쟁작과 다른 점 — 세 가지 장치

상위 리스팅은 인쇄·Canva 체크리스트다(하이퍼링크 PDF 는 24개 중 2개, 조사 1절). 체크리스트는 **무엇을**
할지 적혀 있지만 **지금 무엇을** 할지는 안 알려준다. 우리는 그 "지금"을 판다.

| 장치 | 무엇 | 왜 링크 PDF 라서 되는가 |
|---|---|---|
| **① Energy menu** | 할 일을 요일이 아니라 **배터리(Low / Medium / Full) × 시간(2 / 5 / 10 / 20분)** 격자로 나눈다. 칸의 할 일을 누르면 그 방 카드로 간다 | 격자 12칸 → 방 카드로 가는 링크. 종이에서는 "찾아가기"가 한 단계 더 든다 |
| **② Room reset cards** | 방마다 한 장: 10분 리셋 **순서**(위→아래, 쓰레기→그릇→빨래→제자리), 늘 쌓이는 곳(hotspot), **"Done enough" 선** -- 여기까지 하면 끝 | 집 지도(House map)에서 방을 누르면 카드. 모든 페이지 왼쪽의 `ROOMS` 탭 |
| **③ Rescue mode** | "집이 엉망이다"일 때: 정리 말고 **구조**. 큰 세 가지(쓰레기·그릇·빨래)부터, 15분 스프린트 한 장, 끝나면 Wins log | **표지 빼고** 모든 페이지 오른쪽 위 `SOS` 칩 → 여기. 상품 3 의 SOS 와 같은 방식 |

## 1. 타겟

**집안일이 밀려서 괴로운 ADHD 성인** (미국·영국 중심, 영어). 혼자 살거나, 가족·룸메이트와 나눈다.
상품 1 구매자와 **같은 사람일 수 있지만 검색어가 다르다** -- `adhd cleaning planner` `cleaning schedule` `chore chart`.

이 타겟의 실제 고통 (설계의 축):

1. **어디서부터 할지 모른다** → 집 전체를 보고 얼어붙는다 (① ②)
2. **"오늘은 기운이 없다"** → 요일 체크리스트가 매주 실패 기록이 된다 (①: 요일 대신 배터리)
3. **끝이 없다** → 완벽하게 하거나 아예 안 한다 (②: Done enough 선)
4. **한번 무너지면 다시 시작을 못 한다** → 몇 주 방치 (③ Rescue)
5. **빨래·설거지의 마지막 단계에서 멈춘다** → 개지 않은 빨래 산, 말라붙은 그릇 (Loops 페이지)
6. **같이 사는 사람과 싸운다** → 누가 무엇을 (Who does what · Kids & pets tasks 페이지)

## 2. 형식

| 항목 | 값 | 비고 |
|---|---|---|
| 형식 | **하이퍼링크 PDF** (GoodNotes·Notability) | 상품 1~3 과 같은 파이프라인 |
| 판형 | US Letter 세로 612 × 792pt | A4 는 "맞춤 인쇄" (상품 1 과 같은 안내) |
| 날짜 | **undated** | 연중 판매, 해마다 새로 안 만든다 |
| 인쇄 | **흑백 인쇄판 PDF 를 하나 더** (5절 ②) -- 파일 2개: 링크 PDF + 흑백판 | 경쟁 상위가 인쇄용이다 |
| 디자인 | **상품 1(v8.20) 모양 + 색만 바꿈** (5절 ④) -- iPad 확인된 모양이라 표본 iPad 확인은 권장 | `PROCESS.md` 4단계 |
| 뷰어 안전 | 처음부터 `fast_paint` · `vector_dots` 방식 (그림자·번짐은 공유 PNG, 점은 벡터 원) | `RELEASE.md` 2절 |

## 3. 페이지 지도 (108쪽 -- 쪽 번호는 v0.9 빌드 기준, `check_docs_p4.py` 가 대조)

탭(**왼쪽** 레일) 6개 + **표지 빼고** 모든 페이지 오른쪽 위 `SOS` 칩:
**HOME · ENERGY · ROOMS · ROUTINES · WEEKS · TOOLS**

**NEW** = 새 페이지. **P1** = 상품 1 템플릿을 확장. **P3** = 상품 3 문구 재사용.

> **2026-09-30 변경 (사용자, 4단계 표본을 본 뒤):** 2쪽에 **순서도(How it flows)** 를 넣고 Start here 는 3쪽으로.
> 아래 3-2 이하 표의 쪽 번호는 한 쪽씩 뒤로 밀린다(실제 번호는 빌드가 뽑는다). **총 107쪽.**
> 흑백 인쇄판은 탭 레일과 SOS 를 **그대로 둔다**(사용자). Energy menu 칸의 빈 줄은 칸 맨 아래에 붙이고 `+` 표시
> (표본 v0.1 에서 높이가 들쭉날쭉 -- 사용자 지적, `build_p4.check_energy_align` 이 잰다).

> **2026-09-30 전체 빌드 v0.2** (`python scripts/p4/build_p4.py full`): 컬러 링크판 + 흑백판 각 107쪽,
> `output/prod4/planner/v0.2/home-reset_v0.2_{color,BW}-FINAL.pdf` (3.4MB / 3.4MB). 검사 `scripts/p4/check_p4.py`
> (쪽 수·죽은 링크·고아 페이지·탭 하이라이트·원고 누락·배치 4종) + `check_render.py` 모두 FAILURES 0.
> **v0.5 (같은 날)**: 표 헤더 위에도 선(위아래 대칭, 사용자), 공용 선 검사기 `check_lines.py` 를 처음 돌려
> sprint 괘선 부풀림·Index 와 주간 페이지 좌우 끝 어긋남을 고침. **검사 세 개를 매 빌드 돌린다:**
> `check_p4.py <버전>` · `check_lines.py src/p4_home-reset_<버전>_{color,BW}.html` · `check_render.py <PDF>` -- v0.5 전부 0.
> (LINES.md 0절을 제작 전에 읽지 않고 표를 짰다 -- `PROCESS.md` 4단계 부록 "제작 전 확인 목록"에 넣었다)
> **5단계 검수 v0.7 (같은 날)**: 자동 검사 전부 0. 검수 중 고친 것 -- 박힌 문구 23개를 원고로, 표지→2쪽 링크,
> 화살표 글자를 SVG 로(Nunito 에 없어 맑은 고딕으로 대체되던 129곳). 보고서 `output/prod4/planner/v0.7/qa/report.md`.
> **v0.8 (같은 날, 사용자 결정 3건 반영)**: 30쪽 요일 7칸 순환표(기획서대로), 103쪽 이사 체크리스트 12개, 33·34쪽 루프는
> 2×2 격자 유지(기획서 수정). 검사 세 개 전부 0. **새 문구 119개 확인 대기**: `output/prod4/planner/v0.8/qa/new_copy_for_review.csv`.
> **6단계 써 보기 v0.9 (같은 날)**: `scripts/p4/dogfood_p4.py` -- 링크를 눌러 시나리오 12개(공통 3 + 상품별 6 + 빈틈 3).
> v0.8 에서 5개가 막혔다: Routines 에 목차가 없어 다른 루틴으로 못 감 / Rescue 에서 Sprint·Guests 로 못 감 / 주간에서 방 카드로 못 감.
> 사용자 결정으로 **Routines 목차 페이지 추가(29쪽, 총 108쪽)** + 링크 7곳(Rescue→Sprint·Guests, 주간 "This week's rooms"→House map,
> Energy 배터리→그날 페이지, Guests 줄→방 카드, 루프→Wins). v0.9: **막힌 곳 0**, 검사 세 개 0.
> 새 문구 2줄 확인 대기: Routines 목차 제목·부제 (`PAGE_TEXT["routines"]`).
> 참고(디자인): 배터리 이름·Guests 줄은 링크지만 겉모습은 글자 그대로라 누를 수 있는지 안 보인다 -- 순서도와 함께 디자인 때 볼 것.
> **보류: 2쪽 순서도 디자인** -- 사용자 "너무 촌스럽다"(09-30). 내용·링크는 두고 모양만 다시 짠다.

### 3-1. HOME (5)

| # | 페이지 | 구분 | 내용 | 링크 |
|---|---|---|---|---|
| 1 | 표지 | NEW | `The ADHD Home Reset` / `clean by energy, not by schedule` | → 2 |
| 2 | **How it flows** (순서도) | NEW (09-30) | 배터리 → Energy menu → 방 카드 → Done enough → Wins / All too much? → Rescue → Wins / 매주 Reset week. 문구 `p4_content.FLOW` | 상자마다 그 페이지로 |
| 3 | **Start here** | NEW | 30초 사용법 세 줄: ① 배터리 고르기 → Energy menu ② 방 고르기 → House map ③ 엉망이면 → Rescue. "빈칸은 실패가 아니다" | 세 개 모두 |
| 4 | **House map** | NEW | 집 평면을 **방 타일 9개**로(그림 아님, 칸). 방마다 "마지막 리셋: ___" 칸 | 타일 → 각 방 카드 |
| 5 | Index | NEW | 전 페이지 목록 | 전 페이지 |

### 3-2. ENERGY (4)

| # | 페이지 | 내용 |
|---|---|---|
| 6 | **Energy menu** (허브) | 3 × 4 격자: 배터리 Low / Medium / Full × 2 / 5 / 10 / 20분. 칸마다 할 일 2~3개(미리 채움, 4-1) + 빈 줄 1(`+`). 할 일 → 방 카드, 배터리 이름 → 그날 페이지 |
| 7–9 | **Low / Medium / Full day** | 배터리별 한 장: 오늘 고른 것 3개 / 곁들일 것(음악·팟캐스트·body double) / 끝나고 나에게 줄 것 / "오늘은 이걸로 충분" 체크 |

### 3-3. ROOMS (19)

| # | 페이지 | 내용 |
|---|---|---|
| 10 | Rooms index | 방 9개 → 카드·깊은 청소 (빌드에서 방 앞에 둠 -- 다른 섹션 목차와 같은 자리) |
| 11–28 | **방 9개 × 2장** — 방 카드 + 깊은 청소 | **방 카드**: 10분 리셋 순서 6단계(미리 채움, 4-2) · Hotspots 3칸 · **Done enough** 한 줄 · 필요한 도구 · 마지막 리셋 날짜 5칸. **깊은 청소**: 월·계절 체크리스트(미리 채움) + 빈 줄 |
| | 방 목록 | Kitchen · Bathroom · Bedroom · Living room · Entry & hallway · Laundry · Desk & office · Car · **My room**(이름 비움) |

### 3-4. ROUTINES (9)

| # | 페이지 | 구분 | 내용 |
|---|---|---|---|
| 29 | Routines index | NEW (10-01, 6단계 써 보기) | 루틴 8쪽 목록 -- ROUTINES 탭이 여기로 |
| 30 | **Daily reset** | NEW | 아침 5분 / 저녁 10분 -- 고정 3개씩 + 빈 줄. "하루 한 번, 한 가지" |
| 31 | **Weekly rotation** | P1 확장 | 요일 대신 **구역 순환**: 7칸에 방을 하나씩. 놓친 날은 다음 칸으로 밀 뿐(실패 칸 없음). **v0.7 은 방×요일 격자로 잘못 만들어짐 → v0.8 에서 기획서대로 (09-30 사용자)** |
| 32 | **Monthly deep clean** | NEW | 12칸 × 할 일(냉장고·필터·침구 등 미리 채움) |
| 33 | **Seasonal reset** | NEW | 봄·여름·가을·겨울 네 칸. 계절 옷장·창문·이불 |
| 34 | **Laundry loop** | NEW | 세탁 → 건조 → 개기 → **제자리** 네 칸 **2×2 격자(1→4 번호)** -- 원형에서 변경(09-30 사용자, 5단계 검수). "어디서 멈추나" 체크 + 멈추는 곳 대책 |
| 35 | **Dishes loop** | NEW | 쓰기 → 담그기 → 씻기 → **넣기**. 같은 형식. 두 루프 모두 아래 Wins log 로 |
| 36 | **Who does what** | P1 확장 | 할 일 / 누가 / 얼마나 자주 / 순번 -- 상품 1 `chores` 에 순번(rotation) 칸 추가 |
| 37 | **Kids & pets tasks** | NEW | 나이별로 맡길 수 있는 일 칸(빈칸) + 반려동물 돌봄 체크 |

### 3-5. WEEKS (53)

| # | 페이지 | 내용 |
|---|---|---|
| 38 | Weeks index | Week 1~52 → 각 주 |
| 39–90 | **Reset week 1~52** (undated) | 이번 주 구역 순환 7칸(칸 이름 → House map) · 이번 주 한 가지(깊은 청소에서) · 빨래·설거지 루프 체크 · Wins 한 줄 · "다음 주로 넘기는 것" |

52주로 결정 (2026-09-30 사용자, 5절 ③).

### 3-6. TOOLS (18)

| # | 페이지 | 구분 | 내용 |
|---|---|---|---|
| 91 | Tools index | NEW | |
| 92 | **Rescue mode** | NEW | ③ 허브. 1 쓰레기 2 그릇 3 빨래 4 바닥의 것 제자리(아니면 "나중 상자") 5 표면 하나. 각 단계 → 해당 루프·방. 아래에 Sprint · Guests 로 가는 칸(6단계 추가) |
| 93 | **15-minute sprint** | NEW | 타이머 링 3개(5분씩) + 각 5분에 한 일. 끝나면 Wins log 로 |
| 94 | **Guests in 2 hours** | NEW | 손님 오기 전: 보이는 곳만. 현관·화장실·거실 순서 + 숨길 상자 하나. 방 이름으로 시작하는 줄 → 그 방 카드 |
| 95 | **Doom pile triage** | P3 | 더미 하나 → Keep / Toss / Belongs elsewhere / Needs action + 15분 |
| 96 | **Declutter decisions** | NEW | 버릴까 망설일 때 질문 5개(마지막 사용·다시 살 수 있나·어디에 둘 건가…) |
| 97 | **Where things live** | NEW | 물건 / 제자리 표 -- "제자리가 없으면 치울 수 없다" |
| 98 | **Restock list** | NEW | 세제·휴지·봉투 등 소모품: 남은 양 칸 + 살 것 |
| 99 | **Cleaning dopamine menu** | P3 변형 | 청소에 곁들일 것: 플레이리스트·팟캐스트·전화 통화·body doubling·보상 |
| 100 | **Body doubling log** | NEW | 누구와(온라인 포함) / 무엇을 / 얼마나 |
| 101 | **Wins log** | NEW | 날짜 / 한 것 / 걸린 시간 -- 전·후를 글로. streak 없음 |
| 102 | **Time guess vs actual** | P1 | 할 일 / 예상 / 실제 -- "설거지는 8분이었다" 발견용 |
| 103 | **Projects list** | NEW | 한 번에 안 끝나는 일(차고·옷장): 첫 단계 한 줄씩 |
| 104 | **Moving / big reset** | NEW | 이사·대청소 체크리스트 -- **미리 채운 12개 + 빈 줄** (09-30 사용자, 문구 `p4_content.BIG_RESET` 확인 대기) |
| 105 | **Notes: lined** | P1 | |
| 106 | **Notes: dot grid** | P1 | 벡터 점(`dot_svg`) |
| 107–108 | **Notes: blank × 2** | P1 | |

**합계 108쪽** (HOME 5 + ENERGY 4 + ROOMS 19 + ROUTINES 9 + WEEKS 53 + TOOLS 18). 6단계에서 Routines 목차 +1.

### 3-7. 링크 규칙

- 왼쪽 레일 탭 6개는 전 페이지. **현재 탭 하이라이트는 표지 빼고 전부 정확히 1개**(`CLAUDE.md` 500쪽 절 5)
- `SOS` 칩은 **표지 빼고** 전 페이지 → 92쪽 Rescue mode (표지는 출발점이라 뺀다 -- 10-01 사용자)
- **페이지 본문에서도 눌러 이동한다** -- 경쟁 리뷰 "탭보다 페이지를 눌러 이동하고 싶다"(조사 2절). 목록·타일·격자 칸 자체가 링크
- 모든 페이지에 들어오는 길이 1개 이상(고아 페이지 0)

## 4. 미리 채울 문구 (원고는 3단계 전에 `scripts/p4/p4_content.py` 로)

| § | 데이터 | 개수 |
|---|---|---|
| 4-1 | Energy menu 할 일 (배터리 3 × 시간 4 × 2~3개) | 약 30 |
| 4-2 | 방 카드 리셋 순서 (방 8 × 6단계) + Done enough 한 줄 + 깊은 청소 목록 (방 8 × 8) | 48 + 8 + 64 |
| 4-3 | Daily reset 고정 6 · Monthly 12 · Seasonal 4 × 5 | 38 |
| 4-4 | Rescue 5단계 · Guests 순서 · Declutter 질문 5 | 약 15 |
| 4-5 | 루프 2종의 "멈추는 곳 대책" | 8 |

검사(4단계 전에 만든다): 개수·중복·칸 길이·금지어. `p3_content.check()` 방식.

## 5. 결정 (2026-09-30 사용자 확정)

| # | 질문 | **결정** |
|---|---|---|
| ① | 이름 | **The ADHD Home Reset** -- 부제 `clean by energy, not by schedule`. 이름으로 찾으면 우리 것만 나온다(입소문이 우리에게). 리스팅 제목은 8단계에서 `ADHD Cleaning Planner…` 로 시작 |
| ② | 인쇄 | **흑백 인쇄판 PDF 를 하나 더** |
| ③ | WEEKS | **52주** (쪽 수는 3절 합계) |
| ④ | 디자인 | **상품 1 모양 + 색만 바꿈** (색은 3단계에서 사용자) |
| ④-색 | **섹션마다 한 색** (2026-09-30 사용자, 3단계. 10-01 재확인 -- 민트 한 색 시리즈안은 접음) | 아래 표. 페이지마다 번갈아(사용자 첫 제안)는 비교 그림을 본 뒤 섹션안으로 -- 번갈아는 한 권 16색·위치 단서 상실·52주 넘길 때 번쩍임 |
| ⑤ | 가격 | **정가 $8.99 + 런칭 세일.** 목표가 $6.99 였지만 Etsy 세일은 정수 % 라 **22% = $7.01 / 23% = $6.92** 중 결정 대기(`listing-p4.md`) |
| ⑥ | 방 목록 | **9개 그대로** (3-3) |

**색 확정표 (3단계, 2026-09-30)** -- 값은 `scripts/p4/color_candidates_p4.py` `CANDIDATES` (colors-v0.2).
넘기다가 **섹션이 바뀔 때만** 종이·번짐·강조색이 바뀐다. 왼쪽 탭 색은 전 페이지 같은 4색(각 후보의 1번 강조색).

| 섹션 (탭) | 후보 | 종이 | 번짐 (오른쪽 / 왼쪽) | 탭·강조색 / 글자용 |
|---|---|---|---|---|
| HOME · ENERGY | A Fresh linen | `#F5F8F5` | `#C4E7D2` / `#CFE6EE` | `#7FB59C` / `#537364` |
| ROOMS | B Lemon & sky | `#FBFAF2` | `#FBF0B8` / `#D3E6F5` | `#E2BE3E` / `#7D6A28` |
| ROUTINES · WEEKS | C Lavender soap | `#F8F6FA` | `#E9E0F6` / `#EFC6D8` | `#A393D8` / `#6E6490` |
| TOOLS | D Aqua pop | `#F3F9FA` | `#C9EEF3` / `#FFE0D2` | `#2FB3C6` / `#237581` |

뷰어 검사(`PROCESS.md` 3단계): 섹션 첫 쪽 4장 표본 `output/prod4/preview/mix-v0.2/sec_sample.pdf` 에
`check_render.py` -- A 그라데이션·소프트마스크·타일 0, B 27ms/쪽, C 엔진 차이 0.72, **FAILURES 0**.
새 효과 없음(상품 1 의 구운 번짐·그림자 PNG 방식 그대로) → 표본 iPad 확인은 **권장**(`PROCESS.md` 4단계).
표지는 HOME 민트, 흑백판은 회색(번짐 없음, 탭·SOS 유지) -- 4단계 표본(v0.1~v0.2)에서 보이고 사용자 확인.

### 결정 전 초안의 선택지와 의견 (기록 -- 09-30, 검사가 대조하지 않는다)

| # | 질문 | 선택지 / Claude 의견 |
|---|---|---|
| ① | 이름 | `The ADHD Home Reset` (가칭). 리스팅 제목은 8단계에서 따로 -- `ADHD Cleaning Planner` 가 앞에 와야 검색된다 |
| ② | **인쇄** | (가) 같은 PDF 를 인쇄해도 되게만(상품 1 방식, 추가 작업 0) / (나) **흑백 인쇄판 PDF 를 하나 더**(잉크 절약, `cleaning schedule printable` 검색어). 의견: **(나)** -- 경쟁 상위가 인쇄용이고 파일 하나 더라 비용이 작다 |
| ③ | **WEEKS** | 52장(약 106쪽) / 월간 12장(약 66쪽). 의견: **52장** -- 쪽 수는 리스팅에서 비교되는 숫자이고, 반복 페이지는 "압도적"을 만들지 않는다(처음 여는 사람은 HOME 에서 시작) |
| ④ | **디자인** | 새로 / **상품 1(v8.20) 또는 상품 3 의 모양을 가져와 색만** -- 입구 상품이라 제작 속도가 중요. 디자인은 사용자 몫이라 여쭙는다 |
| ⑤ | 가격 | 정가 $8.99, 런칭 세일 없음 또는 얕게($6.99). 입구 칸 $5~9 안. 8단계에서 확정 |
| ⑥ | 방 목록 | 9개(3-3). `Car` 대신 `Kids room` 등 바꿀 것이 있으면 |

## 6. 직접 써 보기 시나리오 (상품별, `PROCESS.md` 6절)

실제 길은 `scripts/p4/dogfood_p4.py` 가 링크를 눌러 따라간다 (v0.9: 12개 전부 통과).

1. **기운 없는 날**: 표지 → 순서도(2쪽) → Start here → Energy menu → Low · 5분 칸 → 할 일 → 방 카드 → Done enough 체크 → HOME 탭
2. **엉망일 때**: 아무 페이지 → `SOS` → Rescue 1~5 → 15-minute sprint → Wins log
3. **한 주**: WEEKS → Week 7 → "This week's rooms" → House map → 방 카드 → 깊은 청소 목록 / Week 7 아래 Next week → Week 8
4. **빨래 산**: ROUTINES(목차) → Laundry loop → 멈추는 곳(개기) → 대책 → Wins log
5. **손님 온다**: `SOS` → Rescue 아래 Guests in 2 hours → Entry·Bathroom·Living room 줄 → 그 방 카드
6. **같이 산다**: ROUTINES(목차) → Who does what → (목차) → Kids & pets → (목차) → Weekly rotation

## 7. 문구 원칙

1. **한 칸 = 한 가지 일.** 할 일은 **7단어 이내**, **동사로 시작하거나 "무엇 → 어디로" 꼴** (`Clear one surface` · `Keys into their bowl`).
   *(처음엔 "동사로 시작, 6단어"였으나 확정 문구가 이 꼴이라 원칙을 문구에 맞췄다 -- 10-01 사용자. 검사 `p4_content.check()` 는 7단어)*
2. **죄책감 금지.** streak·"실패"·"밀렸다" 없음. 놓친 날은 **다음 칸으로 밀 뿐**이다
3. **"Done enough" 가 기본값.** 완벽 기준을 인쇄하지 않는다
4. **의학적 주장 금지.** 청소가 ADHD 를 낫게 한다는 말 없음. "시도해 보라" 까지
5. **1인칭 당사자 표현 금지** (`CLAUDE.md` 2026-09-30) -- 판매 글에서도 설계 원칙으로만 말한다
6. **남의 틀을 베끼지 않는다.** ADHD 살림 분야에는 저자·코치의 이름 붙은 방법론이 있다. 이름·고유 용어·순서를
   가져오지 않고, 쓰레기·그릇·빨래 같은 **일반적인 일**로만 짠다
7. 미국 영어. 공감 코드: doom pile, body doubling, dopamine menu, "done enough" -- 처음 보는 사람을 위해 한 줄 설명

## 8. 예상치 (9단계 전에 `forecast.md` 로 옮긴다)

| 항목 | 값 | 근거 |
|---|---|---|
| 쪽 수 | **108** (v0.9 실측) | 3절 |
| 용량 | **3.4~3.5MB** (v0.9 실측) | 20MB 상한과 거리가 멀다 |
| 제작 | 예상 2~3일 → **실제 하루**(09-30, v0.1 → v0.9) | 반복 페이지 1종, 고유 템플릿 약 45종 |
| 판정 | 12월 말까지 조회 100 | `product4-research.md` 4절 |
