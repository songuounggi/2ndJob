# 상품 3 — 내용 계획 (2026-09-25)

**디자인은 사용자, 내용은 Claude.** 이 파일은 "무슨 페이지에 무엇이 들어가는가"만 정한다.
색·모양·배치는 사용자 몫이다. 문구 원본은 `scripts/p3_content.py` (검사·CSV 내보내기 포함).

사용자 요청: **"내용을 아주 알차게, 뻔하지 않고 아이디어가 돋보이게."**

---

## 0. 한 줄 콘셉트

> **The ADHD Year — 52 experiments to find what works for your brain.**
> 날짜가 박힌 1년 플래너. 매주 전략 하나를 실험하고, 연말엔 **나에게 통한 것만 모은 사용설명서**가 남는다.

경쟁작(Manifestable 709p 등)이 파는 것은 "페이지 수 + 스티커"다. 우리는 **1년 동안 진행되는 이야기**를 판다.
뻔한 것(연간·월간·주간·일간·트래커)은 다 갖추되, 아래 세 장치가 차별점이다.

| 장치 | 무엇 | 왜 우리만 가능한가 |
|---|---|---|
| **① 52 Experiments** | 1주 = 전략 1개. 주간 페이지에 "이번 주 실험", 금요일에 ✓ 도움됨 / ~ 조금 / ✗ 아님. 분기마다 Keep/Drop, 12월에 **My Playbook** | 날짜형이라 주 번호가 고정 → 실험이 달력에 박힌다. undated(상품 1)는 못 한다 |
| **② Time Links** | 일간 "내일 첫 단계" ↔ 다음 날 "어제의 나에게서" / "30일 뒤의 나에게" ↔ 30일 뒤 "도착한 메모". 서로 링크 | PDF 내부 링크(GoodNotes 에서 유일하게 되는 기능)를 **시간 이동**에 쓴다. 날짜가 고정돼야 짝을 지을 수 있다 |
| **③ 보이는 시간** | 일간 머리에 `Day 68 · 297 left` + 연 진행 막대 + 월 진행 막대. 예상 vs 실제 칸 | 시간맹(time blindness). 날짜를 알아야 남은 날을 인쇄할 수 있다 |

## 1. 문구 원칙 (전 페이지)

1. **한 칸 = 한 가지 일.** 질문은 한 문장, 70자 이내
2. **죄책감 금지.** streak·"실패"·"놓쳤다" 없음. 빈칸은 정상이다
3. **의학적 주장 금지.** cure / treat / diagnose / 용량 조언 없음. "시도해 보라"는 제안만.
   약은 "복용 체크"와 "다음 진료 때 물어볼 것" 기록까지만 (상품 1 과 같은 선)
4. 영어(미국 표기). 구매자 대다수가 미국
5. **공감 코드**는 ADHD 커뮤니티가 실제로 쓰는 말: ADHD tax, doom pile, dopamine menu, body doubling,
   waiting mode, hobby graveyard, time blindness. 설명 한 줄을 붙여 처음 보는 사람도 알게 한다

## 2. 페이지 지도 (연도별 PDF 1개 기준)

**NEW** = 상품 1 에 없는 페이지. **P1** = 상품 1 템플릿 재사용(문구는 그대로, 모양은 새 디자인).

### 2-1. 앞부분 — 한 해를 여는 페이지

| # | 페이지 | 구분 | 내용 |
|---|---|---|---|
| 1 | 표지 | NEW 문구 | `{YEAR} ADHD Year Planner` / `52 experiments · every day linked` |
| 2 | **How this planner works** | NEW | 세 장치 설명(①②③) + 3탭 이동법 + "빈칸은 실패가 아니다". §4-1 |
| 3 | Index | P1 | 목차 |
| 4 | **SOS — I'm stuck** | NEW | 증상 → 도구 링크 허브. 상품 1 의 도구 61종을 **카테고리가 아니라 증상으로** 다시 묶는다. §4-2. 모든 페이지 구석에 `SOS` 칩 → 여기 |
| 5 | Year at a glance | 있음 | 미니 달력 12개, 날짜마다 링크 |
| 6 | **Year kickoff: systems, not resolutions** | NEW | 작년에 통한 것 / 안 통한 것 / 올해 만들 시스템 3개 / "3월에도 쓰고 있을 것" |
| 7 | **The 52 experiments** | NEW | 52주 실험 목록 한 장(두 장). 줄마다 주 링크 + ✓ ~ ✗ 칸. 연말에 이 표가 곧 성적표 |
| 8 | **Year in pixels — brain weather** | NEW | 12 × 31 격자, 칸 = 하루. 기분 5색 범례. 존재하지 않는 날(2/30 등)은 막아 둔다 |
| 9 | **Life admin radar** | NEW | 12달 × 미리 채운 "어른 일" 제안(§4-4) + 빈 줄. 월 계획 페이지에 그 달 것이 다시 뜬다 |
| 10–11 | **Birthdays & gift radar** | NEW | 달마다 칸: 이름 / 날짜 / **buy-by**(10일 전) / 아이디어. 상품 1 `dates` 의 확장 |
| 12 | **Where I put it** | NEW | 여권·예비 열쇠·보증서·비밀번호 힌트 위치를 적는 지도형 표. "어디 뒀더라"를 한 번에 |

### 2-2. 분기 (4장, NEW — 상품 1 `quarterly` 한 장을 대체)

Q1–Q4 각 1장, 달 이름 박힘: 이번 분기 한 가지 / 달별 목표 3칸 /
**실험 Keep · Drop**(지난 13주 중 남길 것 3, 버릴 것 3 — 해당 주로 링크) / **Hobby check**(시작한 것·그만둔 것, 부끄러움 없이).

### 2-3. 매달 (12달 × 4장)

| 페이지 | 구분 | 내용 |
|---|---|---|
| 월 달력 | 있음 | 날짜 → 일간, 주 번호 → 주간. 공휴일 표시(§4-6, 결정 필요) |
| **Month plan** | NEW | 이달의 테마 + 한 줄(§4-3) / 이달의 한 가지 / 날짜·마감 / 청구서·갱신 / 생일(→ gift radar) / 진료·약 리필 / **Admin radar 이달 제안** 체크리스트 / 내려놓을 것 |
| **Brain weather** | NEW | 날짜 박힌 31칸 × 4줄: 기분 · 에너지 · 집중 · 수면. + 복용 체크 한 줄. (상품 1 습관 격자와 달리 **요일 머리글이 실제 요일**) |
| **Month review** | NEW(P1 review 확장) | 상품 1 질문 4개 + 테마 질문 1개 + **ADHD tax**(연체료·재구매·깜빡한 구독 — 금액 합계, 연 합계로 링크) + **Hyperfocus harvest**(이달 몰입한 것: 쓸모 있었나 / 재밌었나) + 이달 실험 결과 요약 |

### 2-4. 매주 (53주)

| 페이지 | 구분 | 내용 |
|---|---|---|
| Weekly spread | 있음 + 칸 추가 | **This week's experiment** 카드(이름 · Try · Why) + 금요일 칸 `Did it help? ✓ ~ ✗` + 7일 칩 |
| **Weekly reset** | NEW (§5 용량 참고) | Sunday setup 체크리스트(고정 6개) + 다음 주 가장 무거운 날 + 이번 주 done list + 실험 한 줄 소감 |

### 2-5. 매일 (365일) — 칸 목록

| 칸 | 내용 | 비고 |
|---|---|---|
| 머리 | 요일·날짜 / `Day 68 · 297 left` / 연 진행 막대 / 월 진행 막대 / 월·주 칩 / 공휴일 라벨 | ③ |
| **From yesterday ←** | 어제 페이지의 "Tomorrow starts with" 로 가는 칩 | ② 1월 1일은 없음 |
| Battery check | 에너지 1–5 | |
| **To-do by energy** | 세 칸: Low battery / Medium / Full — 오늘 배터리에 맞는 줄에서 고른다 | 뻔한 to-do 대신 |
| **Not today** | 오늘 안 할 것 (허락 목록) | |
| Schedule | 시간 칸 + 일정 뒤 buffer 칸 | 실험 #16 과 연결 |
| **Guess vs actual** | 2줄: 할 일 / 예상 / 실제 | ③ |
| Meds · water · mood | 상품 1 과 같음 | |
| **Question of the day** | 요일별 7갈래 × 53 = 371개(§4-5). 같은 요일끼리 그 해 몇 번째인지로 고른다 → 계절이 맞는다 | |
| **Tomorrow starts with** | 한 줄 + `Tomorrow →` 칩 | ② |
| **Note to future me** | 두세 줄 + `Arrives {+30일 날짜} →` 칩. 받는 쪽 일간엔 `A note from {날짜} ←` | ② 12월 2일~ 쓴 메모는 **Year-end mailbox** 로 배달 |

### 2-6. 연말 (12월 뒤, NEW)

| 페이지 | 내용 |
|---|---|
| **My ADHD Playbook** | ✓ 받은 실험을 옮겨 적는 표(각 주로 링크) + "나에게 통하는 것 5가지" + "나에게 안 통하는 것" |
| **Year-end mailbox** | 12월에 쓴 "30일 뒤의 나에게" 메모가 도착하는 곳 — 새해 첫날 읽기 |
| **Year review** | 올해의 승리 10개 / ADHD tax 연 합계 / 가장 좋았던 달 / 내년에 가져갈 3가지 |

### 2-7. 도구함 — 상품 1 템플릿 61종 + NEW 4

P1 그대로: Focus 11 · Feelings 10 · Habits 2 · Health 8 · Life 10 · Notes 8 + 인덱스들.
NEW (상품 1 에 없던 ADHD 공감 코드):

| 페이지 | 내용 |
|---|---|
| **Dopamine menu** | 식당 메뉴판 형식. Starters(5분 기분전환) / Mains(시간 드는 즐거움) / Sides(지루한 일에 곁들일 것) / Desserts(가끔) / Specials(특별한 날). 칸마다 빈 줄 + 예시 한 줄 |
| **Doom pile triage** | "Didn't Organize, Only Moved" 더미 정리: 한 더미 → Keep / Toss / Belongs elsewhere / Needs action 네 칸 + 타이머 15분 |
| **Hobby graveyard** | 그만둔 취미·프로젝트: 무엇 / 얼마나 / 거기서 얻은 것 / 되살릴까? — 수치심 없이 |
| **Waiting-mode kit** | 약속 있는 날 온종일 아무것도 못 하는 현상. 약속 전 짧게 할 일 목록 + "몇 시에 출발" 역산 칸 |

## 3. 페이지 수 — 와이어프레임 실측 (2026-09-25)

`python scripts/p3_wireframe.py 2027 mon` → `output/p3_wireframe_2027-mon.pdf`

| 부분 | 장 |
|---|---|
| 앞부분(표지·사용법·목차·SOS·연간·킥오프·52실험·픽셀·admin·생일 2·어디뒀지 + P1 Goals·Project·Vision) | 16 |
| 분기 | 4 |
| 월 목차 + 매달 4장(달력·계획·Brain weather·리뷰) × 12 | 49 |
| 매일 | 365 |
| 주 목차 + 매주 2장(spread·reset) × 53 | 107 |
| 연말(Playbook·Mailbox·Year review) | 3 |
| 도구함(그룹 4 + P1 41 + NEW 4) + 노트(목차 + 4) | 54 |
| **합계** | **597** (2026·2027 같음) |

**용량:** 와이어프레임(글자·선뿐)도 18.1MB → dedupe 후 **8.8MB**. 링크 주석 1만여 개와 접근성
태그(StructElem 6만여 개)가 바닥 용량이다. 실제 판은 이 위에 디자인 무게가 얹힌다 — 상품 1 모양(1p ≈ 33KB)이면
약 20MB 로 상한 근처. **디자인할 때 페이지당 무게를 의식할 것.**

**자동 검사 (빌드할 때마다):** 죽은 링크 0 / Time links 양방향(내일↔어제 364쌍, 30일 메모 365쌍 —
12/2 이후는 Year-end mailbox) / 모든 주가 어느 분기 Keep·Drop 에 나오는가.
검사기 자체 확인: 3/8→3/9 연결 하나를 틀면 `handoff d3-8->d3-9`, 1주차 링크를 지우면 `[1]` 로 잡힌다.
(1주차는 2026-12-28 에 시작해 처음엔 1분기에서 빠졌다 → 해를 넘는 주는 1월/12월에 붙인다: `home_month()`)

## 4. 문구 데이터 (`scripts/p3_content.py`)

| § | 데이터 | 개수 |
|---|---|---|
| 4-1 | How this planner works 본문 | 1 |
| 4-2 | SOS: 증상 → 도구 키 | 14 |
| 4-3 | 달 테마(이름·한 줄·리뷰 질문) | 12 |
| 4-4 | Life admin radar 제안(달마다 4개) | 48 |
| 4-5 | Question of the day (요일 7갈래 × 53) | 371 |
| 4-6 | 공휴일·기념일 (연도별 계산) | 17/년 |
| 4-7 | 52 Experiments (이름·Try·Why) | 53 |
| — | Pattern detective 질문(Brain weather) | 3 |
| 4-8 | Weekly reset 고정 체크리스트 | 6 |
| 4-9 | NEW 도구 4종 칸 문구 | 4 |

검사: `python scripts/p3_content.py` → 개수·중복·길이·금지어(의학 주장) 검사 +
`output/p3_content_<연도>.csv` (날짜별로 그날 들어갈 문구 전부 — 엑셀로 검수).

## 5. 결정 필요 (사용자)

| # | 질문 | 선택지 / Claude 의견 |
|---|---|---|
| 1 | **용량.** 약 613p. 지금 모양(v8.20 계열)이면 1p ≈ 33KB → **약 20.2MB, Etsy 상한 20MB 초과 위험** | 디자인이 가벼우면 괜찮다. 아니면 Weekly reset 53장을 주간 spread 안의 칸으로 접어 넣기(→ 약 560p) |
| 2 | 공휴일 표시 | 미국 공휴일 + 몇 개 기념일 / 없음. 첫 구매자는 브라질이었다. 제안: 미국 공휴일 11개 + 발렌타인·어머니날·아버지날·핼러윈·크리스마스이브·새해 전날 + ADHD Awareness Month(10월)·World Mental Health Day(10/10) |
| 3 | 2026 판 | 2026 은 10~12월만 쓸 수 있다. 같은 구성으로 가되 실험 목록은 그대로(13주만 쓰게 됨) — 괜찮은가 |
| 4 | 제목 | `ADHD Year Planner 2026-2027` + 부제 `52 Experiments` — 리스팅 단계에서 확정 |
