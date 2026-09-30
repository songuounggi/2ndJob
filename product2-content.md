# 상품 2 — 내용 계획 (ADHD Student Planner)

**작성일:** 2026-09-30
**대상 판:** `student-v1.1` — 437쪽 / 15,464,001 B / 2026-09-24 발행
(`listing/4581765488`, `shop.md` 업로드 이력 #4)

> ## 이 문서의 성격 — 반은 사전 기획, 반은 사후 기록
>
> 상품 2 는 **기획서 없이 만들어 출시했다.** `PROCESS.md` 2단계가 요구하는
> `product<N>-content.md`(페이지 지도·문구 원고)가 없었고, 그래서 검수
> **5-1 기획서 대조를 한 번도 돌리지 못했다.** `product2-student.md` 는
> 75KB 짜리 **작업 일지**다 — 앞 5절만 기획이고 나머지는 시간순 기록이다.
>
> 이 문서는 그 구멍을 메운다. 다만 **빌드에서 베껴 쓴 지도로 빌드를
> 검사하면 무조건 통과한다.** 그래서 출처를 구분해 적는다:
>
> | 표시 | 뜻 | 검사의 의미 |
> |---|---|---|
> | **[기획]** | 만들기 전에 `product2-student.md` 에 적혀 있던 것 | **진짜 대조.** 어긋나면 결함이다 |
> | **[사후]** | v1.1 실물에서 읽어 적은 것 | 지금은 자명하게 통과. **앞으로의 변경**을 잡는 기준선 |
>
> 4절이 [기획] 대조 결과다. **거기서 나온 불일치는 아직 판정 전이다** —
> 기획을 고칠지 빌드를 고칠지는 사용자가 정한다(5절).

---

## 0. 한 줄 콘셉트  [기획]

> ADHD 가 있는 **대학생·대학원생**을 위한, 날짜 없는 하이퍼링크 PDF 플래너.
> 날짜가 아니라 **과목·과제 단위**로 쓴다. 4년(8학기)이 파일 하나에 들어간다.

**타겟의 실제 고통 다섯 가지** — 페이지는 여기에 대응해야 한다.

| # | 고통 | 대응 페이지 |
|---|---|---|
| 1 | 강의계획서를 받고 아무것도 옮겨 적지 않는다 | **Syllabus unpack** (핵심 셀링 포인트) |
| 2 | 마감을 역산하지 못한다 | Working backwards |
| 3 | 시험 공부 범위를 쪼개지 못한다 | Exam study plan |
| 4 | 조별과제에서 자기 몫이 흐려진다 | Group project |
| 5 | 걸릴 시간을 항상 과소평가한다 | Guess vs actual |

**페이지를 더하거나 뺄 때 이 대응이 깨지지 않는지 먼저 본다.**

---

## 1. 문구 원칙  [사후 — v1.1 문구에서 귀납]

1. **영어. 미국식 표기.** Etsy 주 시장이 미국이고 `adhd student planner`
   검색도 미국 중심이다 (`optimize`, `class schedule`)
2. **2인칭 명령형, 짧게.** "Start any week. Skip a week."
3. **판단하지 않는다.** 빈 칸을 남긴 것에 벌을 주는 문구를 쓰지 않는다 —
   "The page is not keeping score."
4. **의학적 주장 금지.** 진단·치료·효능을 말하지 않는다
5. **칸 이름은 무엇을 적는지로 짓는다.** "Steps, in reverse" 처럼
   행동을 적고, 추상명사("Planning")를 쓰지 않는다
6. **표 머리글은 대문자 한 단어~두 단어.** `DUE` `DONE` `BY WHEN`
7. **부제는 그 페이지를 쓰는 이유 한 줄.** "Split the scope first.
   Then give each piece a day."

---

## 2. 페이지 지도  [사후 — v1.1 실측]

탭 레일 10개가 모든 페이지에 있고, 탭 목차(허브)가 그 아래를 묶는다.
**반복 세트는 학기(8) 단위**이며 제목은 학기 내 번호, eyebrow 가 `Term N` 이다.

### 2-0. 앞 (2쪽)

| 쪽 | id | 내용 |
|---|---|---|
| 1 | `cover` | 표지. 카드 4줄 = Syllabus unpack / Assignment tracker / Working backwards / Term at a glance |
| 2 | `index` | "Where to?" — 9개 탭으로 가는 링크 + Anything else |

### 2-1. SEMESTER (26쪽)

| id | 쪽수 | 제목 | 칸 |
|---|---|---|---|
| `semester` | 1 | 허브 | Term at a glance / Term goals / Term review 칩 + Anything else |
| `terms` | 1 | All eight terms | 표 `TERM / WHAT IT IS FOR / CREDITS / DONE` × 8 + Notes on the four years |
| `t1`~`t8` | 8 | Term N | 표 `WEEK / WHAT IS DUE / EXAMS / DONE` × 16 + What this term is really about |
| `o1`~`o8` | 8 | Term goals | This term 표 `GOAL / HOW I WILL KNOW / BY WHEN / DONE` × 5 + Why these |
| `r1`~`r8` | 8 | Term review | What actually happened / What I will do differently / What worked |

### 2-2. WEEK (129쪽)

| id | 쪽수 | 제목 | 칸 |
|---|---|---|---|
| `week` | 1 | 허브 | 학기별 칩 격자(16×8) + Anything else |
| `w1`~`w128` | 128 | Week 1~16 (학기당) | Due this week 표 `WHAT / CLASS / DAY / DONE` × 6 / Reading / One thing I will not drop |

### 2-3. DAY (113쪽)

| id | 쪽수 | 제목 | 칸 |
|---|---|---|---|
| `day` | 1 | 허브 | 학기별 칩 격자(14×8) + Anything else |
| `d1`~`d112` | 112 | Day 1~14 (학기당) | Just one thing today / Due soon 표 `ASSIGNMENT / CLASS / DUE / DONE` × 5 / Brain dump |

### 2-4. CLASSES (57쪽)

| id | 쪽수 | 제목 | 칸 |
|---|---|---|---|
| `classes` | 1 | 허브 | Class schedule / Who to ask / Class pages 칩 + Anything else |
| `h1`~`h8` | 8 | Class schedule | 시간표 `MON~FRI` × 08~20시(13행) + Notes |
| `k1`~`k8` | 8 | Who to ask | 표 `NAME / CLASS / OFFICE HOURS / ASKED` × 22 |
| `c1`~`c40` | 40 | Class 1~5 (학기당) | Class / Professor & TA / Room & time / 성적 비중 표 `PIECE / WEIGHT / DUE / DONE` × 5 / Things to remember |

### 2-5. WORK (53쪽)

| id | 쪽수 | 제목 | 칸 |
|---|---|---|---|
| `work` | 1 | 허브 | Syllabus unpack / Assignment tracker 칩 + Anything else |
| `s1`~`s40` | 40 | **Syllabus unpack** | Class / Assignments 표 `WHAT/TYPE/DUE/DONE`×5 / Exams & quizzes 표 `WHAT/COVERS/DATE/DONE`×3 / Reading 표 `READING/FOR WEEK/PAGES/DONE`×4 |
| `a1`~`a8` | 8 | Assignment tracker | This term 표 `ASSIGNMENT / CLASS / DUE / DONE` × 22 |
| `backwards` | 1 | Working backwards | Due / Steps, in reverse 표 `STEP/NEEDS/BY WHEN/DONE`×16 / So I start on |
| `group` | 1 | Group project | The project / 표 `PIECE/WHO/BY WHEN/DONE`×7 / My part |
| `estimate` | 1 | Guess vs actual | 표 `TASK / I GUESSED / IT TOOK / DONE` × 22 |
| `obstacle` | 1 | Obstacle plan | The goal / 표 `OBSTACLE/WHEN/WHAT I WILL DO/READY`×6 / If it all falls apart |

### 2-6. STUDY (37쪽)

| id | 쪽수 | 제목 | 칸 |
|---|---|---|---|
| `study` | 1 | 허브 | Exam study plan / Grade tracker 칩 + Anything else |
| `e1`~`e24` | 24 | Exam study plan | Exam / The scope, in pieces 표 `PIECE/SOURCE/DAY/DONE`×12 / What I keep getting wrong |
| `g1`~`g8` | 8 | Grade tracker | Class / Pieces 표 `PIECE/WEIGHT/SCORE/DONE`×16 / Where I stand |
| `cornell` | 1 | Lecture notes | Class & date / Cue / Notes / Summary (코넬 3단) |
| `reading` | 1 | Reading log | 표 `READING / CLASS / BY WHEN / READ` × 22 |
| `session` | 1 | Study session log | 표 `WHAT I STUDIED / WHERE / HOW LONG / IT WORKED` × 22 |
| `office` | 1 | Office hours | Who & when / What I want to ask / What they said |

### 2-7. FOCUS (6쪽)

`focus` 허브 + `braindump` · `focus-session` · `deciding` · `avoiding` · `energy`

### 2-8. LIFE (4쪽)

`life` 허브 + `meds`(표 ×22) · `sleep`(표 ×22) · `mood`(표 ×7 + Anything else)

### 2-9. NOTES (10쪽)

`notes` 허브 + `n1`~`n9` = **Ruled 3 / Dot grid 3 / Plain 3**
점지는 상품 1 의 `bp.dot_svg()` 를 그대로 쓴다(v8.20, 벡터 원).

### 2-10. 링크 규칙  [사후]

| 규칙 | |
|---|---|
| 탭 레일 10개 | **모든 페이지**에 있고 목적지가 같다. 켜진 탭은 정확히 1개(표지 제외) |
| 목차(p2) | 9개 탭 전부로 간다. **자기 페이지로 가는 링크를 두지 않는다** |
| 허브 | 자기 탭의 모든 반복 세트로 칩 링크 |
| 반복 페이지 | 레일 10개만. 서로를 가리키지 않는다 |

---

## 3. 페이지 수 · 용량  [사후 실측]

| | 값 |
|---|---|
| 총 쪽 | **437** (고유 28 + 반복 409) |
| 디자인 종류 | 고유 28 + 반복 템플릿 13 = **41** |
| 파일 | 15,464,001 B (**15.46 MB**) — 상한 20MB 대비 여유 22.7% |
| 링크 | 탭 4,370 + 내용 (허브 칩) |

---

## 4. 원래 기획과의 대조  [기획] ← **여기가 5-1 의 본론**

`product2-student.md` 의 "구성안"·"확정 사항" 절과 v1.1 실물을 맞춰본 결과.

### 4-1. 새로 만들 것 12종 — **12/12 있다** ✅

| 기획 | 실물 | 장수 |
|---|---|---|
| Syllabus unpack | `s1`~`s40` | 40 |
| Semester at a glance | `t1`~`t8` (목차 라벨 `Term at a glance`) | 8 |
| Class schedule | `h1`~`h8` | 8 |
| Per-class page | `c1`~`c40` | 40 |
| Assignment tracker | `a1`~`a8` | 8 |
| Exam study plan | `e1`~`e24` | 24 |
| Lecture notes | `cornell` | 1 |
| Reading log | `reading` | 1 |
| Group project | `group` | 1 |
| Questions for office hours | `office` | 1 |
| Grade tracker | `g1`~`g8` | 8 |
| Study session log | `session` | 1 |

> 기획의 "Semester at a glance" 는 v0.8 에서 **`Term at a glance`** 로
> 통일했다(`THEMES` 주석). 이름이 바뀐 것은 기록돼 있다.

### 4-2. v8 에서 재사용 12종 — **12/12 있다** ✅

Brain dump · Focus session · Obstacle plan · Stuck on deciding ·
Why I am avoiding it · Guess vs actual · Working backwards ·
Energy budget · Medication log · Sleep · Mood · **Notes(dot grid)**

> Notes 는 v0.1 에서 가로 괘선 한 장뿐이었다가 `NOTE_KINDS` 로
> **Ruled / Dot grid / Plain 각 3장**이 됐다. 기획의 "dot grid" 충족.

### 4-3. 규모 — **어긋난다** ⚠️

| | 기획 (확정 사항, 2026-09-21) | v1.1 실물 |
|---|---|---|
| 총 쪽 | 434 | **437** |
| 고유 템플릿 | 약 50 | **41** |
| 학기 개요 | 8 | 8 ✅ |
| 주간 | 128 | 128 ✅ |
| **일간** | **248** (학기당 31) | **112** (학기당 14) |
| 용량 | 약 17 MB | 15.46 MB |

**일간 248 → 112 는 2026-09-23 에 근거를 갖고 재배분한 것이다** — 페이지
예산의 88%가 날짜에 쏠려 Syllabus unpack 이 1장, 시간표가 1장이던 문제를
고치면서 그 예산을 과목·학기 단위로 옮겼다. 이유는
`product2-student.md` "진행 중 — 반복 세트 재배분" 절에 있다.

**그런데 "확정 사항" 절은 아직 248 로 남아 있다.** 문서만 보면 어느 쪽이
맞는지 알 수 없다 — **5절 결정 1.**

### 4-4. 기획에 없다가 생긴 것 ⚠️

| 추가된 것 | 장수 | 왜 |
|---|---|---|
| Term goals `o1`~`o8` | 8 | 재배분 때 학기 단위로 승격 |
| Term review `r1`~`r8` | 8 | 같음 |
| Who to ask `k1`~`k8` | 8 | 기획의 "Per-class page" 에서 분리 |
| All eight terms `terms` | 1 | 4년 개관 |
| 탭 허브 9장 | 9 | 내비게이션 |
| Notes 종류 3종 × 3 | 9 | 기획 "Notes(dot grid)" 확장 |

전부 **타겟 고통 5가지를 해치지 않는 추가**다. 다만 기획서에 없던 것이
37장 들어간 셈이라 기록해 둔다.

### 4-5. 고통 5가지 대응 — **5/5 유지** ✅

| 고통 | 페이지 | 장수 | 판정 |
|---|---|---|---|
| 1 강의계획서 | Syllabus unpack | 40 | ✅ 학기당 5과목 |
| 2 마감 역산 | Working backwards | **1** | ⚠️ 4년에 한 장 |
| 3 시험 범위 | Exam study plan | 24 | ✅ 학기당 3 |
| 4 조별과제 | Group project | **1** | ⚠️ 4년에 한 장 |
| 5 시간 과소평가 | Guess vs actual | 1 (22행) | 표라서 반복 사용 가능 |

**2번·4번이 한 장씩이다** — 5절 결정 2.

---

## 5. 결정 필요 (사용자)

| # | 결정할 것 | 선택지 |
|---|---|---|
| **1** | 일간 248 vs 112 | (a) 112 가 맞다 → `product2-student.md` "확정 사항" 절을 112 로 고친다 (b) 248 로 되돌린다 |
| **2** | Working backwards · Group project 가 4년에 한 장 | (a) 그대로 (표를 재사용) (b) 학기당 1장(8장)으로 늘린다 — 용량 여유 22.7% 라 가능 |
| **3** | 고유 템플릿 "약 50" 목표 | (a) 41 로 확정하고 기획서를 고친다 (b) 9종을 더 만든다 |

**결정 전에는 빌드를 고치지 않는다.** 판매 중인 판(v1.1)이고,
`CLAUDE.md` "지금 병목은 트래픽" 에 따라 조회 100 전에는 리스팅도 손대지
않는다.

---

## 6. 써 보기 시나리오  [사후]

`PROCESS.md` 6단계에서 끝까지 가야 하는 경로.

1. **학기 첫날** — 표지 → 목차 → CLASSES → Class schedule(h) 에 시간표를
   적고 → Class pages(c) 5장에 과목을 적는다
2. **강의계획서를 받았다** — WORK → Syllabus unpack(s) 에서 과제·시험·읽기를
   분해 → 마감을 Assignment tracker(a) 로 옮긴다
3. **과제가 무겁다** — WORK → Working backwards 로 마감에서 역산 →
   시작일을 Day 페이지에 적는다
4. **시험 2주 전** — STUDY → Exam study plan(e) 에서 범위를 쪼개 날짜 배분
5. **주가 시작** — WEEK → 그 주 페이지에 이번 주 마감을 옮긴다
6. **막혔다** — FOCUS → Stuck on deciding / Why I am avoiding it
7. **학기 끝** — SEMESTER → Term review(r) → 다음 학기 Term goals(o)

각 단계에서 **링크만으로 도달 가능해야 한다.** 검사는
`scripts/check_plan_student.py`.
