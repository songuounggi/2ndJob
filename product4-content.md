# 상품 4 — 기획서 (2026-09-30 사용자 확정)

## ▶ 지금 어디까지 — 인계 (2026-10-01, 회사 PC `Prod 4. The ADHD Home Reset` -- 옛 이름 `Prod 4. Something`)

방 이름: 회사 `Prod 4. The ADHD Home Reset` / 집 **`Prod 4. The ADHD Home Reset (Home)`** (10-01 사용자, 상품 이름 확정으로)

**다른 방·다른 PC 는 여기부터 읽는다.** 이 절 아래의 긴 기록은 그날 무슨 일이 있었는지이고, 할 일은 여기에만 모았다.

### 단계 (`PROCESS.md` 10단계)

| 단계 | 상태 |
|---|---|
| 1 시장 조사 | **통과** -- 사용자가 H-a(청소·루틴, 입구 가격) 선택 (`product4-research.md`) |
| 2 기획서 | **통과** -- 구조·결정 6건 + 문구 원고(`scripts/p4/p4_content.py`) 사용자 확인 |
| 3 디자인 | **통과** -- claude.ai/design 전체 시안 v1.0 (10-01, `design/prod4/the-adhd-home-reset-design-v1.0.zip`) |
| **4 제작** | **v0.12 (디자인 시안 판, 109쪽) 전체 빌드·자동 검사 통과** -- v0.12 노트 세 종류 한 장씩, v0.11 은 110쪽, v0.10 은 108쪽, v0.1 → v0.9 는 옛 모양 |
| **5 검수** | **v0.12 자동 검수 5-1~5-6 통과** (10-01) -- 남은 것: 사용자 눈 검수 |
| **6 직접 써 보기** | **통과 (10-01)** -- 구매자 역할 7명 자유 탐색 2번(v0.10 · v0.11) → 반드시 고침 0, 자동 검사 FAIL 0. 남은 것은 "나중에" 목록(아래). `PROCESS.md` 6절 "끝나는 조건" |
| **7 iPad 검수** | **대기 -- 집에서 (iPad 가 집에 있다)** |
| 8 리스팅 | 원고 초안 `listing-p4.md` (제작과 나란히). 결정 3건 대기 |
| 9 출시 · 10 알리기 | 아직 |

### 출시까지 남은 일 (2026-10-01 -- PDF 는 1~6단계 통과, **아직 올리지 않는다**)

| 순서 | 할 일 | 누가 · 어디서 |
|---|---|---|
| 1 | **7단계 iPad 확인 (필수)** -- GoodNotes 에서 v0.12 컬러판 넘기기(바둑판 렌더링·링크·탭), 흑백판 **한 장 실제 인쇄**(위쪽 쪽 번호·연한 선·체크 칸). 사용자 눈 검수도 이때 | 사용자, 집 (`Prod 4 ... (Home)`, `git pull` 후 `python scripts/p4/build_v2_p4.py full`) |
| 2 | 7단계에서 나온 결함 고치기 + 그 결함을 재는 검사 붙이기(`PROCESS.md` 7절 "실기기에서만 보이는 결함") | Claude |
| 3 | 8단계 리스팅 결정: 세일 22%($7.01)냐 23%($6.92)냐와 기간 · 제목 길이 · 설명 최종 확인 | 사용자 결정 |
| 4 | **리스팅 사진 10장** -- 시안 draft-v0.6 완료(10-01, v0.12 109쪽), **사용자 확인 대기**. 폰 크기 점검 완료(10-02: 검색 썸네일 제목 16~19pt 읽힘 -- `listing-p4.md` 사진 절, `_phone_preview.png`) | Claude → 사용자 확인 |
| 5 | 9단계 출시: `forecast.md` 에 예상치 먼저(초안 #4 있음) · `RELEASE.md` 절차 · `output/prod4/upload/v0.12/` 에 Etsy 파일 이름으로(`listing-p4.md` 파일 이름 표) · **올릴 파일 그 자체로 `check_scroll_speed` · `check_render` 최종 재검**(고친 뒤 다시 느려지는 회귀 방지) | Claude + 사용자 |
| 6 | 10단계 알리기: 핀터레스트 핀 -- **시안 6장 draft-v0.2 + 원고 초안 완료(10-02, `pinterest.md` 상품 4 절)**. 11월 손님맞이(96쪽 Guests) 시즌 대비 01_guests 를 출시 직후 먼저 | Claude + 사용자 |

### ★★ 디자인 v1.0 이 최신 (2026-10-01 18:32) -- **이걸로 작업한다**

- **`design/prod4/the-adhd-home-reset-design-v1.0.zip`** (3.8MB, 82개). 아래 v1(18:02)은 옛것
- 안: `README.md`(디자인 인수인계서) · **`pages_turn25.html`**(전체 디자인 HTML) · `reference/`(CLAUDE_prod4.md, background_bake.js, 메모 1개)
  · `assets/` · **`screenshots/p001_cover.jpg` ~ `p107_notes-blank_p107-108.jpg`** -- 쪽 번호가 붙어 있어 108쪽 지도와 바로 짝지어진다
- 진행 (10-01 19시~): **README·reference 2개·HTML 구조 정독 완료.** 요점 --
  정답 그림 = `screenshots/p###` 38장 / `assets/25-*.jpg` = 배경 재료(번짐·유리 탭·켜진 탭·SOS·카드 그림자·배너 번짐을 구운 JPG) /
  정확한 수치 = `pages_turn25.html`(쪽마다 612×792 상자, 배경 JPG 위에 글자·선·체크를 pt 절대 좌표로, 스크립트·그라데이션·그림자 CSS 0) /
  우선순위 README 규칙 > HTML 수치 > 그림. 문구는 확정 원고 그대로(대소문자·줄 나눔만 다름, Reset week 힌트만 "next slot" 으로 짧아짐).
  HTML 링크는 대부분 `href="#"` 자리표시(일부 #p3 #p37 #p91 #p100 은 쪽 번호가 1씩 어긋남) -- 링크는 우리 페이지 key 로 다시 건다.
  화살표 → ← 112곳은 글자라 Nunito 에 없어 대체 글꼴로 찍힌다 -- 우리 쪽에서 해결(웹 글꼴 지정 또는 SVG).
- **결정 (10-01 사용자)**: ① Reset week 왼쪽에 "← Previous week" 알약 추가 ② 41쪽 힌트는 **"no penalty"** 로 줄임
  (처음엔 원고대로 → 카드 오른쪽 끝을 넘어 다시 결정) ③ 흑백판 = 배경 없이(흰 종이) + 카드 회색 테두리 + **쓰는 칸 회색 테두리 · 선 한 단계 진하게 · 쪽 번호**(뒤의 셋은 6단계 써 보기 뒤 추가)
  ④ **시안에 화살표가 없다고 기획서 링크를 빼지 않는다.** 6쪽 배터리 Low/Medium/Full(→ 7~9쪽)·10쪽 방 이름(→ 방 카드)은
  **→ 를 붙여 보이게**, 나머지 기획서 링크(1쪽 제목 → 2쪽, 6쪽 할 일 → 그 일이 있는 쪽, 41~92쪽 "This week's rooms" → House map,
  94쪽 단계 → 루프·방, 96쪽 방 이름 줄 → 방 카드)는 **모양은 시안 그대로, 글자 위에 보이지 않는 링크**
  ⑤ 101쪽 "Something to listen to" 힌트 "podcasts, audiobooks" → **"podcasts"** (카드 오른쪽 끝을 넘었다, 시안에서도 같음)
  ⑥ 가로선 색은 **시안 값 유지**(0.6pt #E3E9E5 -- PDF 값은 시안과 같고, 축소해 볼수록 뷰어가 진하게 그린다. iPad 한 쪽 보기 +8%).
  iPad 에서 보고 다시 판단
  README 미결 4건은 기획서로 판단: 7·11쪽 배너 순서 시안대로 / 98쪽 질문 줄 링크 아님 / 98쪽 질문 카드 제목 없음 / 라디오 불필요
- **제작 v0.10 (10-01 전체 빌드, 검사 통과)**: `scripts/p4/build_v2_p4.py full` -- 시안의 대표 쪽 HTML(38개)을 **그대로 틀로**,
  110쪽에 내용·링크만 갈아 끼운다. `scripts/p4/bake_bg_p4.py` -- 디자인의 배경 굽기 코드를 헤드리스 Chrome 에서 그대로 돌려
  Reset week 변형 배경(Previous 알약 그림자)을 굽는다(원본과 차이 0.195 단계).
  결과: `output/prod4/planner/v0.10/home-reset_v0.10_color-FINAL.pdf`(5,005,637 B) · `…_BW-FINAL.pdf`(3,454,254 B), 108쪽.
  검사: `check_v2_p4.py v0.10` 0 (대표 쪽이 정답 그림과 평균 차이 최대 3.14 · 중앙 1.07 단계) · `check_render.py` 0
  (49 ms/쪽) · `dogfood_p4.py v0.10` 막힌 곳 0 · `check_listing_p4.py v0.10` 0 (설명 용량 "under 6 MB" 로 고침).
  고친 것: 쪽 크기(px→pt, 459→612pt), 화살표를 SVG 로·앞 단어와 묶기, flex 상자 공백 사라짐, **시안에 `<a>` 가 드물어
  v0.9 보다 링크가 빠진 쪽이 57개였던 것**(→ 붙은 글자·Weeks 칸을 링크로, 기획서 링크 복원 -- check_v2 에 "기획서 링크 빠짐" 검사,
  고치기 전 판에서 FAIL(57개 쪽) 확인)
- **5단계 검수 v0.10 (10-01, 자동 전부 0)** -- 매 빌드 돌리는 검사 다섯:
  `check_plan_p4.py v0.10`(5-1·5-4: 원고 464개가 제 쪽에 있나 · 목차 쪽 번호 131개 = 링크 목적지 · 표지 알약 = 섹션 첫 쪽 ·
  판 글자의 금지·1인칭·영국식 표현) / `check_design_p4.py v0.10`(5-2: README §11 을 108쪽에 -- 글꼴 로드 후 1배 실측,
  같은 틀 = 대표 쪽과 같은 배치 · 글자 넘침·겹침 · 체크 14·4.5 · 알약 y754 · 링크 → · 선 0.6·세 색) /
  `check_v2_p4.py v0.10`(5-3: + HTML 링크 1,146 = PDF 링크 · 주 번호·앞뒤 주) / `check_render.py`(5-5) / `check_docs_p4.py`(5-6).
  각 검사는 일부러 틀린 사본에서 FAIL 확인. 고친 것: 41~92쪽 "← Previous week" 화살표가 글자색 → 섹션 진한색(Next 와 같게).
  예외(이유는 검사 파일에): 100쪽 Restock 머리 = 시안 README 9절 Full/Half/Low 체크 / 1쪽 표지 목차 구분선 #E9EEEB = 시안 원본 /
  2쪽 "Check your battery →" 두 줄 = README §7-2 사례
- **6단계 써 보기 v0.10 (10-01)** -- 구매자 역할 에이전트 7명(기운 없는 첫날 · 집 폭발 · 주간 루틴 · 가족 · 종이 인쇄 ·
  깐깐한 리뷰어 · 아무거나 눌러보기)이 `scripts/p4/tap_p4.py`(그림을 보고 좌표로 누른다, 링크 목록 없이)로 써 봄.
  **고친 것**: 흑백판 42~92쪽 컬러 배경 혼입 · 흑백판 바탕 회색(전 쪽) · 리스팅 예시(fridge 는 Medium 칸) ·
  96쪽 Guests 체크 상자 옆 숨은 링크 → 줄 끝 → · 94쪽 Rescue 단계 링크 2·3단계만 · 6쪽 할 일 7개 → 깊은 청소 쪽 ·
  리스팅 "links to the room card" → "the page" · 4쪽 방 타일 · 3쪽 카드 전체 링크 · 3·94·96쪽 탭 위치 ·
  흑백판 쓰는 칸 테두리 · 선 진하게 · 쪽 번호. 검사: check_v2 8 · check_design H·I · check_listing 2줄(전부 고치기 전 판에서 FAIL 확인)
  **문구 결정 (10-01 사용자)**: 34쪽 "Once a month." · 32쪽 "Two small resets a day." · 33쪽 "Slide it to tomorrow." ·
  7~9쪽 "one is enough, three at most"(6쪽 "one is enough" 와 맞춤) · 1쪽 표지 알약 = 섹션 첫 쪽(6 · 10 · 31 · 93, 쪽 수로 읽히던 것) ·
  2쪽 "Done enough" → 103쪽 Wins log · 영어 13쪽 "Hang towels or toss in the hamper"(제안 9단어 → 7단어 규칙으로 줄임) ·
  25쪽 "steering wheel" · 20쪽 "Put back the umbrella and bags" · 95쪽 "the last timer goes off" · 2쪽 "Tap any step" ·
  리스팅 "Rescue mode". 시안에 박힌 옛 문구는 `build_v2_p4.COPY_FIX` 가 원고로 바꾼다(원고에 없으면 빌드가 멈춤)
  **구조 결정 (10-01 사용자) → v0.11 (110쪽)**: 주간 Wins 칸 옆 "this week"(103쪽 Wins log 는 언제든) · 주간 "This week's
  rooms" 카드 안 "WEEK OF ____" · 7~9쪽 "FROM THE ENERGY MENU" 카드(그 배터리 할 일, 누르면 그 일이 있는 쪽) · 방 카드 10장
  아래 왼쪽 "← Energy menu" · **빈 방 카드 둘째(29·30쪽 My room 2)** -- 4쪽 집 지도 9번째 타일 "My rooms" 에 Room 1 · Room 2,
  10쪽 방 목록 10줄, 5쪽 목차, 표지 "ten rooms", 인쇄된 쪽 번호는 `renumber` 가 실제 쪽에서 다시 쓴다(29쪽 뒤 +2).
  그림자 자리가 바뀐 배경은 `variant_bg` 가 디자인 굽기 코드로 다시 굽고 새 자리 밖이 원본과 같은지 재서 다르면 빌드를 멈춘다
  (하루 0.015 · 방 0.001 · My room 0.211 · 방 목록 0.190 · 주간 0.191). 검사: check_plan_p4 6·7 (고치기 전 판에서 FAIL 확인)
  결과: `output/prod4/planner/v0.11/home-reset_v0.11_color-FINAL.pdf`(5.1MB) · `…_BW-FINAL.pdf`(3.6MB), 110쪽
- **6단계 재시험 v0.11 (10-01, 구매자 역할 7명)** -- 막힘 0 · 쓰는 칸 눌러 넘어감 0 · 탭 문제 0 · 리뷰어 별점 3 → 4.
  **규칙대로 고친 것**: 94쪽 Rescue mode 의 2·3단계 카드 전체(→ 하나만 눌렸다) · 할 일 cabinet → 부엌 깊은 청소, mail pile → 거실 깊은 청소,
  clear the desk → 책상 깊은 청소 · 흑백판 쪽 번호 아래 772 → 위쪽 가운데 35(종이 끝 4~6mm 라 프린터 여백에 걸림) · 리스팅 "two rooms".
  **결정 (10-01 사용자)**: 33쪽 부제 "Slide it to the next slot."(같은 쪽 카드 "just the next slot" 과 같게) · 17쪽 03 "Fold blankets,
  fluff the pillows", 19쪽 06 "Shake the mat, sweep the floor" + 리스팅 "Every task links to the room card, deep clean list, or loop it
  belongs to." · 6쪽 부제 끝 "Tap a task to open it.", 7~9쪽 라벨 "… · TAP ONE" · 흑백판 SOS 옆 "p.94", 10쪽 "Each deep clean list is
  the page after its room card.", 40쪽 "Week N is on page 40 + N." 검사: check_plan_p4 8(할 일이 그 쪽에 있다, 고치기 전 원고 3건 FAIL),
  check_v2 8(흑백판 SOS 쪽 번호·규칙 줄·규칙이 판과 맞나, 쪽 번호 끝에서 18pt·겹침 0), check_listing(빈 방 개수)
  **남은 것(낮음 -- 다음에 사용자 확인)**: 방 카드에서 Guests·주간으로 돌아가는 길 · Wins 칸과 Wins log 관계 안내 · Kids & pets 표에
  WHO·체크 칸 · My room 카드 Last reset 5칸(다른 방 10칸)·Hotspots 부제 · 33쪽 방 줄 8개(방 10개) · 106쪽 "Moving or big reset"
  항목이 전부 이사용 · 107쪽 Notes 제목 두 번 · 96쪽 같은 말 두 번 · 97쪽 "Timer set for" · "vs." · 2쪽 "Pick by minutes"
- **다음**: 7단계 iPad(집). 쪽 번호를 말할 때는 v0.12 기준(v0.10 보다 29쪽 뒤 +2: Routines 31 · Weeks 40 · Reset week 41~92 · Tools 93 ·
  Rescue 94 · Guests 96 · Wins log 103 · Notes 107~109). v0.12(10-01): 노트 세 종류 한 장씩 -- 빈 노트 둘째 장을 뺐다(이유 없이 두 장이었다), 109쪽
  **함정**: 이 PC 의 셸 도구는 명령을 넘길 때 `\\` 를 `\` 하나로 줄인다 -- heredoc 안 파이썬 `"\\1"` 이 제어 문자 `\x01` 이
  되어 정규식이 두 번 깨졌다(10-01). 백슬래시가 든 고침은 Edit 도구로, 또는 `chr(92)` 로 만든다. 검사: 파일의 제어 문자 0

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
   - 1쪽 제목 → 2쪽 → "Open the planner" → 3쪽 → "By battery" → 6쪽
   - 아무 쪽 오른쪽 위 **SOS** → 94쪽 Rescue mode
   - 108쪽 Notes (dot grid): 점이 촘촘하고 또렷한가 (상품 1 에서 깨졌던 곳)
   - **스크롤이 첫 손짓에 바로 반응하나** (10-01 사용자 -- PC 에서 "두 번째에 반응" 을 겪음, PDF 쪽 원인은 못 찾음):
     가장 무거운 쪽 **5쪽(Index), 1쪽(표지), 2쪽(순서도)**(pdf.js 처음 넘기기 121, 67, 66ms, 나머지 중앙 17ms),
     링크가 넓은 쪽 **40쪽(Weeks), 5쪽(Index), 93쪽(Tools), 4쪽(House map)**(쪽의 30~44% 가 링크 -- 링크 위에서 시작한 스크롤),
     그리고 보통 쪽 몇 장(예: 47쪽 Reset week 7, 11쪽 Kitchen)과 비교. 측정 `scripts/check_scroll_speed.py` (v0.12 통과)
   - 결과는 이 절에 날짜·기기·앱과 함께 적는다
   - **2026-10-02 사용자 iPad 확인 (v0.12)**: 넘기기·스크롤 양호 -- 40쪽(Weeks) 양옆 39, 41쪽에서 아주 살짝 지연, 47쪽이 11쪽보다 살짝 무겁지만
     괜찮은 수준. 링크: HOME → 5쪽(Index) 의도대로 유지 · 2쪽(How it flows)의 Done enough → 103쪽, All too much? → 94쪽 확인 · 순서도 "Room card" → "Pick a room"
     으로 바꿈 · 질문 상자와 행동 상자가 같은 쪽으로 가는 것은 그대로

### 5-7 구조 논리 검토 (2026-10-02, v0.12 판 -- 2쪽은 새 순서도로 바뀐다고 가정) -- 사용자 결정 대기

`PROCESS.md` 5-7 L1~L10 으로 109쪽을 읽은 결과. L1~L4 는 반드시 고침, 나머지는 결정. 성인 눈높이(L11) 검토는 다음에 따로.

| # | 구분 | 쪽 | 무엇이 안 맞나 |
|---|---|---|---|
| S1 | L1 순서 | 3쪽 Start here | 1 Check your battery · 2 Pick one room · 3 All too much? 를 **번호로** -- 1·2 는 둘 중 하나, 3 은 벅찬 날 갈래. 2쪽에서 고친 결함과 같다. 2쪽과 역할도 겹친다(L9) -- **반영 v0.13** -- 번호 대신 그림 + "Doable today? Pick one way in." (사용자 10-02) |
| S2 | L4 길 없음 | 11~29쪽 방 카드 10장, 7~9쪽 배터리 날 | 새 순서도는 "Ten minutes → Wins log" 인데 방 카드·배터리 날 쪽에 Wins log(103쪽)로 가는 길이 없다(루프·구조 모드·스프린트에는 있다) -- **반영 v0.13** -- 방 카드 10장 · 7~9쪽에 "Wins log →" 알약 (사용자 10-02) |
| S3 | L3 글자≠도착 | 6, 8쪽 "Vacuum one room" | 아무 방이라는 말인데 17쪽 Living room 카드로 간다 -- **반영 v0.13** -- "Vacuum the living room" (사용자 10-02) |
| S4 | L6 약속≠칸 | 2쪽 새 순서도 "Once a week -- Reset week: one room a day" | "한 주에 한 번" 과 "하루에 방 하나" 가 한 상자에. 인수인계서 v0.3 문구라 design 에 정정 필요 -- **반영** -- "Every week" (사용자 10-02, 인수인계서 v0.4) |
| S5 | L5 두 곳 기록 | 4쪽 House map 타일 "LAST RESET" ↔ 방 카드 "Last reset" | 같은 방의 마지막 리셋을 두 쪽에 적는다 |
| S6 | L5 두 곳 기록 | 12쪽 Kitchen deep clean ↔ 34쪽 Monthly (fridge · microwave · dishwasher filter), 26쪽 Car deep clean ↔ 35쪽 Seasonal (car kit), 41~92쪽 주마다 "One deep clean" | 깊은 청소가 네 곳. 같은 일이 두 목록에 LAST DONE / MONTH 칸을 따로 가짐 |
| S7 | L5 두 곳 기록 | 41~92쪽 "Wins this week" ↔ 103쪽 Wins log | 이긴 것을 어디에 적나 |
| S8 | L9 겹침 | 33쪽 Weekly rotation ↔ 41~92쪽 Reset week | 같은 "방 × 요일" 표. 33쪽이 한 번 정하는 계획이고 주마다 쪽이 체크인지 쪽에 안 적혀 있다 |
| S9 | L7 수량 | 32쪽 Daily reset, 39쪽 Kids & pets tasks(Pet care 표) | 요일 체크 칸이 한 주치 한 장뿐 -- 52주 플래너 |
| S10 | L7 수량 | 7~9쪽 배터리 날 | "Today I'll do" 쪽이 배터리마다 한 장 -- 날마다 지우고 쓰는 쪽인지 안 적혀 있다 |
| S11 | L8 순서 | 5쪽 Index | Weeks(40쪽)가 Routines(31쪽)보다 먼저 -- 탭 순서·쪽 순서와 다르다 |
| S12 | L6 약속≠칸 | 97쪽 Doom pile triage | "One pile, fifteen minutes" 인데 "Timer set for ___" 칸 (나중에 목록에 있던 것) |
| S13 | L5 중복 | 96쪽 Guests | "Everything else into one box" 가 줄과 아래 문장에 두 번 (나중에 목록에 있던 것) |
| S14 | L1 순서 | 2쪽 새 순서도 | Energy menu 에서 고른 일이 루프(36, 37쪽)·깊은 청소 쪽으로 가면 "Stop at Done enough" 가 그 쪽에 없다 -- **반영** -- 시간을 갈래 상자로, 합친 뒤 "Do that one thing, then stop" (사용자 10-02) |

### 사용자 결정 대기

| # | 무엇 | 선택지 / 자료 |
|---|---|---|
| 1 | **디자인 전체 시안** (순서도만이 아님, 10-01 사용자) | 사용자가 claude.ai/design 에서 작업 중 (10-01 "거의 끝나간다"). 색은 **섹션별 4색 한 가지로**(아래 10-01 결정). 인수인계서 `product4-design-handoff.md` **v0.2**, 그림 `output/prod4/handoff/flow-v0.2/`(회사 PC 에만 -- 집에서 필요하면 v0.9 빌드 뒤 컬러판 1·2·3·6·11·29·92쪽을 PNG 로 렌더해서 쓴다. 파일 구성은 인수인계서 6절). 시안 색은 섹션별 4색 한 가지 (10-01 정정 -- 처음엔 두 방식을 요청했었다) |
| ~~2~~ | ~~색: 섹션별 4색 vs 민트 한 색 시리즈~~ | **결정 (10-01): 섹션별 4색 유지.** 시리즈안은 접는다 |
| 3 | 리스팅 런칭 세일 | Etsy 는 정수 % -- **22% = $7.01** / **23% = $6.92**, 기간(상품 3 은 30일) |
| 4 | 리스팅 제목 | 긴 안(14단어) / 짧은 안(9단어) -- `listing-p4.md` |
| 5 | 리스팅 설명 검토 | `listing-p4.md` |
| 6 | 새 문구 2줄 | 31쪽 Routines 목차: "Routines" / "The small repeats that keep it from piling up." |
| 7 | 디렉토리 이름 규칙 | 사용자가 손보겠다고 함(버전 폴더 9개·`-FINAL` 유무가 헷갈림). 다른 방과 같이 쓰는 규칙이라 바꿀 때 알린다 |
| 8 | 상품 1~3 표 위아래 비대칭 | 상품 4 는 고쳤다. 출시본은 버전을 올려야 해서 결정 전 (`LINES.md` 2절) |
| 9 | **2쪽 순서도 다시 짜기** (10-02 사용자) | **구조는 결정: 갈림 순서도.** 지금 판은 질문 상자와 답 상자가 같은 쪽으로 가는 쌍이 셋이고, 둘 중 하나인 "기운으로 / 방으로"를 한 줄로 이어 순서도가 성립하지 않는다(09-30 첫 초안부터 같은 논리, 디자인은 모양만 바꿈). 새 구조: 플래너를 연다 → ◇지금 어때? → 할 만하다: ◇어떻게 고를까? → 기운·시간으로 6쪽 / 방으로 4쪽 → 10분 하고 "이만하면 됐다"에서 멈춤 → 103쪽 Wins log · 너무 벅차다: 94쪽 구조 모드 → 103쪽 · 매주 40쪽. 질문(◇)은 링크 없음, 상자 하나 = 쪽 하나. **남은 결정:** 디자인 방법(claude.ai/design 또는 지금 틀 안에서), "왜 힘든지 돌아보기" 칸을 둘지·어디에(권장: 103쪽 뒤에서) |

### 수익 재점검 (2026-10-01, 사용자 요청 "기획 자체가 수익을 극대화할 메리트가 있는지")

| 점검 | 결정 |
|---|---|
| 맨 끝 1쪽 "리뷰 부탁 + 상품 1·2·3 소개 + 숍 링크" (입구 상품 → 중간 칸 연결) | **넣지 않는다** (사용자). 109쪽 그대로. 다시 꺼낼 때: Etsy 는 리뷰 요청 허용·보상 조건 금지, 디지털 파일 안 자기 숍 링크 공식 문구는 미확인 |
| 색: 섹션별 4색 vs 민트 한 색 "Reset 시리즈"(+ 번들 고가 칸) | **섹션별 4색 유지** (사용자). 시리즈·번들은 나중에 따로 |
| 판매 계획: 시즌 훅 + 가격 시험 | **기획서에 적는다** (사용자) -- 아래 |

**판매 계획 (페이지는 그대로, 핀·가격만)**

| 언제 | 훅 | 쓰는 페이지 | 할 일 |
|---|---|---|---|
| **11~12월** | 연말 손님맞이 (Thanksgiving·Christmas hosting) | 96쪽 Guests in 2 hours | 출시를 **10월 중·하순**으로 -- 핀이 퍼지는 데 몇 주(`pinterest.md`). 손님맞이 핀 |
| **1월** | 새해 home reset | 6쪽 Energy menu · 2쪽 순서도 | 새해 리셋 핀 |
| **3월** | spring cleaning | 35쪽 Seasonal reset · 방 카드 깊은 청소 | 봄맞이 청소 핀 |

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
상품 1(502쪽)과 반대로 간다: **109쪽, 표지 다음 순서도 한 장이면 무엇을 할지 보인다.**

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

## 3. 페이지 지도 (109쪽 -- 쪽 번호는 v0.12 빌드 기준, `check_docs_p4.py` 가 대조)

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
| 2 | **How it flows** (순서도) | NEW (09-30), **구조 바꿈 (10-02 사용자)** | 갈림 순서도: Open the planner → ◇How's today? → Doable: ◇How to pick? → Energy menu(6쪽, "By battery, 2 to 20 minutes") / House map(4쪽, "One room, ten minutes") → Do that one thing, then stop → Wins log / All too much: Rescue mode(94쪽) → Wins log · 따로 Every week(40쪽). 시간은 갈래마다 달라 갈래 상자에(10-02 사용자). 문구 `p4_content.FLOW`. 디자인은 claude.ai/design 에 맡김(인수인계서 `product4-design-handoff.md` v0.4). v0.13 판 2쪽은 구조만 맞춘 임시 배치 -- 시안이 오면 그 쪽만 바꾼다 | 링크 상자 6개 = 쪽 6개(3, 6, 4, 94, 103, 40쪽). 질문·갈래 이름·"Do that one thing" 은 링크 없음. 같은 쪽으로 가는 상자 금지 |
| 3 | **Start here** | NEW, **번호 뺌 (10-02 사용자)** | 30초 사용법: 라벨 "Doable today? Pick one way in." 아래 By battery → Energy menu / By room → House map (둘 중 하나), 그리고 All too much? → Rescue. 번호(1, 2, 3) 자리는 그림(배터리 · 집 · 구명환) -- 차례가 아니라 갈림(2쪽 순서도와 같은 구조). "빈칸은 실패가 아니다" | 세 개 모두 |
| 4 | **House map** | NEW | 집 평면을 **방 타일 9개**로(그림 아님, 칸). 방마다 "마지막 리셋: ___" 칸 | 타일 → 각 방 카드 (타일 위쪽 전체를 누른다, LAST RESET 쓰는 줄은 빼고 -- 10-01) |
| 5 | Index | NEW | 전 페이지 목록 | 전 페이지 |

### 3-2. ENERGY (4)

| # | 페이지 | 내용 |
|---|---|---|
| 6 | **Energy menu** (허브) | 3 × 4 격자: 배터리 Low / Medium / Full × 2 / 5 / 10 / 20분. 칸마다 할 일 2~3개(미리 채움, 4-1) + 빈 줄 1(`+`). 할 일 → **그 일이 있는 쪽**(방 카드 · 깊은 청소 · 빨래/설거지 루프 -- 10-01, 깊은 청소 목록에 있는 7개는 깊은 청소 쪽으로), 배터리 이름 → 그날 페이지 |
| 7–9 | **Low / Medium / Full day** | 배터리별 한 장: 오늘 고른 것 3개 / 곁들일 것(음악·팟캐스트·body double) / 끝나고 나에게 줄 것 / "오늘은 이걸로 충분" 체크 |

### 3-3. ROOMS (21)

| # | 페이지 | 내용 |
|---|---|---|
| 10 | Rooms index | 방 10개 → 카드·깊은 청소 (빌드에서 방 앞에 둠 -- 다른 섹션 목차와 같은 자리) |
| 11–30 | **방 10개 × 2장** — 방 카드 + 깊은 청소 (빈 방 둘째 29·30쪽 -- v0.11, 10-01 사용자) | **방 카드**: 10분 리셋 순서 6단계(미리 채움, 4-2) · Hotspots 3칸 · **Done enough** 한 줄 · 필요한 도구 · 마지막 리셋 날짜 5칸. **깊은 청소**: 월·계절 체크리스트(미리 채움) + 빈 줄 |
| | 방 목록 | Kitchen · Bathroom · Bedroom · Living room · Entry & hallway · Laundry · Desk & office · Car · **My room 1 · My room 2**(이름 비움 -- 4쪽 집 지도는 9번째 타일 "My rooms" 에 Room 1 · Room 2 두 링크) |

### 3-4. ROUTINES (9)

| # | 페이지 | 구분 | 내용 |
|---|---|---|---|
| 31 | Routines index | NEW (10-01, 6단계 써 보기) | 루틴 8쪽 목록 -- ROUTINES 탭이 여기로 |
| 32 | **Daily reset** | NEW | 아침 5분 / 저녁 10분 -- 고정 3개씩 + 빈 줄. "하루 한 번, 한 가지" |
| 33 | **Weekly rotation** | P1 확장 | 요일 대신 **구역 순환**: 7칸에 방을 하나씩. 놓친 날은 다음 칸으로 밀 뿐(실패 칸 없음). **v0.7 은 방×요일 격자로 잘못 만들어짐 → v0.8 에서 기획서대로 (09-30 사용자)** |
| 34 | **Monthly deep clean** | NEW | 12칸 × 할 일(냉장고·필터·침구 등 미리 채움) |
| 35 | **Seasonal reset** | NEW | 봄·여름·가을·겨울 네 칸. 계절 옷장·창문·이불 |
| 36 | **Laundry loop** | NEW | 세탁 → 건조 → 개기 → **제자리** 네 칸 **2×2 격자(1→4 번호)** -- 원형에서 변경(09-30 사용자, 5단계 검수). "어디서 멈추나" 체크 + 멈추는 곳 대책 |
| 37 | **Dishes loop** | NEW | 쓰기 → 담그기 → 씻기 → **넣기**. 같은 형식. 두 루프 모두 아래 Wins log 로 |
| 38 | **Who does what** | P1 확장 | 할 일 / 누가 / 얼마나 자주 / 순번 -- 상품 1 `chores` 에 순번(rotation) 칸 추가 |
| 39 | **Kids & pets tasks** | NEW | 나이별로 맡길 수 있는 일 칸(빈칸) + 반려동물 돌봄 체크 |

### 3-5. WEEKS (53)

| # | 페이지 | 내용 |
|---|---|---|
| 40 | Weeks index | Week 1~52 → 각 주 |
| 41–92 | **Reset week 1~52** (undated) | 이번 주 구역 순환 7칸(칸 이름 → House map) · 이번 주 한 가지(깊은 청소에서) · 빨래·설거지 루프 체크 · Wins 한 줄 · "다음 주로 넘기는 것" |

52주로 결정 (2026-09-30 사용자, 5절 ③).

### 3-6. TOOLS (17)

| # | 페이지 | 구분 | 내용 |
|---|---|---|---|
| 93 | Tools index | NEW | |
| 94 | **Rescue mode** | NEW | ③ 허브. 1 쓰레기 2 그릇 3 빨래 4 바닥의 것 제자리(아니면 "나중 상자") 5 표면 하나. **2 그릇 · 3 빨래 단계 끝 → 설거지 · 빨래 루프**(1·4·5 단계는 링크 없음 -- 내용이 맞는 곳이 없다, 10-01). 아래에 Sprint · Guests 로 가는 칸(6단계 추가) |
| 95 | **15-minute sprint** | NEW | 타이머 링 3개(5분씩) + 각 5분에 한 일. 끝나면 Wins log 로 |
| 96 | **Guests in 2 hours** | NEW | 손님 오기 전: 보이는 곳만. 현관·화장실·거실 순서 + 숨길 상자 하나. 방 이름으로 시작하는 줄 끝 → 로 그 방 카드(글자 전체가 아니라 → 만 -- 체크 상자와 떨어지게, 10-01) |
| 97 | **Doom pile triage** | P3 | 더미 하나 → Keep / Toss / Belongs elsewhere / Needs action + 15분 |
| 98 | **Declutter decisions** | NEW | 버릴까 망설일 때 질문 5개(마지막 사용·다시 살 수 있나·어디에 둘 건가…) |
| 99 | **Where things live** | NEW | 물건 / 제자리 표 -- "제자리가 없으면 치울 수 없다" |
| 100 | **Restock list** | NEW | 세제·휴지·봉투 등 소모품: 남은 양 칸 + 살 것 |
| 101 | **Cleaning dopamine menu** | P3 변형 | 청소에 곁들일 것: 플레이리스트·팟캐스트·전화 통화·body doubling·보상 |
| 102 | **Body doubling log** | NEW | 누구와(온라인 포함) / 무엇을 / 얼마나 |
| 103 | **Wins log** | NEW | 날짜 / 한 것 / 걸린 시간 -- 전·후를 글로. streak 없음 |
| 104 | **Time guess vs actual** | P1 | 할 일 / 예상 / 실제 -- "설거지는 8분이었다" 발견용 |
| 105 | **Projects list** | NEW | 한 번에 안 끝나는 일(차고·옷장): 첫 단계 한 줄씩 |
| 106 | **Moving / big reset** | NEW | 이사·대청소 체크리스트 -- **미리 채운 12개 + 빈 줄** (09-30 사용자, 문구 `p4_content.BIG_RESET` 확인 대기) |
| 107 | **Notes: lined** | P1 | |
| 108 | **Notes: dot grid** | P1 | 벡터 점(`dot_svg`) |
| 109 | **Notes: blank** | P1 | 한 장 (v0.12 -- 노트 세 종류 한 장씩, 10-01 사용자) |

**합계 109쪽** (HOME 5 + ENERGY 4 + ROOMS 21 + ROUTINES 9 + WEEKS 53 + TOOLS 17). 6단계에서 Routines 목차 +1, v0.11 에서 빈 방 둘째 +2, v0.12 에서 빈 노트 -1.

### 3-7. 링크 규칙

- 왼쪽 레일 탭 6개는 전 페이지. **현재 탭 하이라이트는 표지 빼고 전부 정확히 1개**(`CLAUDE.md` 500쪽 절 5)
- **HOME 탭 → 5쪽(Index)** -- 109쪽 전체가 한 장에 있는 목록이라 어디서든 HOME 한 번으로 다시 고른다(상품 1 INDEX 탭과 같은 역할). v0.9 부터, 10-02 사용자 확인
- `SOS` 칩은 **표지 빼고** 전 페이지 → 94쪽 Rescue mode (표지는 출발점이라 뺀다 -- 10-01 사용자)
- **페이지 본문에서도 눌러 이동한다** -- 경쟁 리뷰 "탭보다 페이지를 눌러 이동하고 싶다"(조사 2절). 목록·타일·격자 칸 자체가 링크
- 모든 페이지에 들어오는 길이 1개 이상(고아 페이지 0)
- **쓰는 칸 옆에는 링크를 두지 않는다** -- 체크 상자·동그라미에서 12pt 안(손끝 오차 6pt + 여유). 쓰는 줄에 링크가 필요하면 글자 끝 → 만
  링크로(10-01, 6단계 써 보기에서 96쪽이 체크하다 넘어감). 검사 `check_design_p4.py` I
- 카드처럼 생긴 것이 링크면 **카드 전체를 누른다**(3쪽 단계 카드, 4쪽 방 타일 -- "Tap a room." 인데 Go 만 눌리던 것, 10-01)
- 왼쪽 탭 위치는 전 쪽 같다(12 + 128 × 순서). 검사 `check_design_p4.py` H

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
표지는 HOME 민트, 흑백판은 흰 종이(번짐 없음, 탭·SOS 유지, 쓰는 칸 테두리·쪽 번호) -- 4단계 표본(v0.1~v0.2)에서 보이고 사용자 확인, 10-01 인쇄용 보강.

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
