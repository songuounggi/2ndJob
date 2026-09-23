# Etsy 리스팅 원고

복사해서 붙여넣기용. 영문은 그대로 쓰시면 됩니다.
**v8.18-undated FINAL (502p / 고유 61종 / 19.6MB) 기준으로 실측 검증된 수치입니다.**
(2026-09-23 교체. 그 이전은 v8-undated 494p / 58종)

숍 계정 설정은 `shop.md`, 상품 제작 규칙은 `CLAUDE.md`.

---

## 타겟 (2026-09-21 명문화)

**ADHD 가 있는 성인. 대략 25~45세, 자기 삶을 통째로 굴리는 사람.**

> 이건 새로 정한 게 아니라 **이미 상품에 박혀 있던 것을 뒤늦게 적는 것**이다.
> 상품 1은 타겟을 정하고 만든 게 아니라 만든 뒤에 리스팅을 붙였다. 그래서
> 어느 문서에도 타겟이 없었고, 새 방에서 "이거 학생용인가?" 하는 혼선이
> 실제로 났다(2026-09-21).

근거는 추론이 아니라 출시 파일 자체다:

| 페이지 | 위치 | 무엇을 전제하는가 |
|---|---|---|
| Who does what | p56 | 같이 사는 사람이 있다 (파트너/룸메이트) |
| Monthly budget | p50 | 본인이 돈을 관리한다 |
| Cycle tracker | p45 | 성인 여성 비중이 크다 |
| Meals & groceries | p47 | 본인이 장 보고 요리한다 |
| Subscriptions / Trip checklist | p54 / p55 | 본인 명의의 계약과 일정 |
| Doctor visit / Therapy notes / Medication log | p41 / p42 / p38 | 진단받고 치료 중 |

제목의 `Adult ADHD Tools` 와 태그 `adult adhd` 도 같은 곳을 가리킨다.

**학생이 아니다.** 상품 2(`product2-student.md`)는 같은 조건, 다른 생애 단계다.

### 두 상품의 관계 — 번들이 아니다

교차 판매는 기대하지 않는다. 대학생이 "생리주기 + 월 예산 + 집안일 분담"을
살 이유가 없고, 35살 직장인이 "강의계획서 분해"를 살 이유가 없다. **둘 다 사는
사람이 거의 없다.**

연결고리는 **숍 신호**다 — `adhd planner` 계열 키워드를 두 개 쥐면 Etsy 가 이
숍을 그 분야로 인식하고 리뷰도 한 숍에 쌓인다. `product2-student.md` 가 말한
"경쟁이 덜한 키워드를 하나 더"의 진짜 의미가 이것이다.

> `product2-student.md` 의 "디지털 번들이 6종 $30어치를 $18 식으로 통용된다"는
> 우리 전략이 아니라 **시장 관찰**이다. 번들 근거로 인용하지 말 것.

---

## 제목 (Title)

Etsy 제목은 **140자 제한**이고, 앞 40자가 검색에서 가장 큰 비중을 차지합니다.

```
ADHD Digital Planner Undated, GoodNotes iPad Planner, Hyperlinked PDF Journal, Neurodivergent Planner, Adult ADHD Tools
```

119자 / 대문자 단어 3개.

**Etsy 제목에는 제약이 두 개 있습니다. 둘 다 실제로 걸렸습니다.**

| 규칙 | 겪은 일 |
|---|---|
| 140자 이내 | 첫 안이 144자였습니다 |
| **전부 대문자인 단어는 3개까지** | `ADHD`×3 + `PDF` = 4개라 `Your title can't have more than 3 words in all caps.` 로 막혔습니다 (2026-09-21) |

세 번째 덩어리를 `ADHD Journal Hyperlinked PDF` → `Hyperlinked PDF Journal` 로
바꿔 `ADHD` 하나를 덜어냈습니다. **맨 앞 `ADHD Digital Planner Undated` 는
건드리지 않습니다** — 검색에서 앞 40자가 가장 큰 비중을 차지합니다.

제목을 고칠 때 검사:

```python
import re
t = "..."
caps = [w for w in re.findall(r"[A-Za-z][A-Za-z&']*", t) if len(w) > 1 and w.isupper()]
assert len(t) <= 140 and len(caps) <= 3, (len(t), caps)
```

- 앞쪽에 `ADHD Digital Planner` + `Undated` 배치 — 검색량이 가장 큰 조합
- `GoodNotes`, `iPad`, `Hyperlinked PDF` 는 구매자가 실제로 검색하는 기능어
- `Neurodivergent` 는 경쟁이 덜한 롱테일
- `Executive Function` 은 길이 때문에 뺐습니다. 태그에는 남아 있습니다

---

## 태그 (Tags) — 13개, 각 20자 제한

```
adhd planner
digital planner
goodnotes planner
adhd journal
undated planner
ipad planner
neurodivergent
executive function
adhd tools
hyperlinked pdf
adult adhd
focus planner
adhd gift
```

---

## 상품 설명 (Description)

**문단 안에서 줄바꿈하지 마세요.** Etsy 는 보낸 줄바꿈을 그대로 살린 뒤
자기 칸 너비에 맞춰 한 번 더 접습니다. 원고를 72자로 접어두면 상품
페이지에서 문장이 중간중간 끊겨 보이고, 좁은 모바일에서 특히 심합니다
(2026-09-21 Preview 에서 확인).

한 문단 = 한 줄로 둡니다. 줄을 나누는 것은 **불릿·단계·WHAT'S INSIDE 항목**
처럼 원래 한 줄이 하나의 항목인 경우뿐입니다.

```
Start any day. Skip a week. Nothing to catch up on.

This is an undated ADHD planner. There is not a single date printed anywhere in it, so it never expires and you never open it to a wall of blank days you "missed".

WHAT MAKES IT DIFFERENT

Most big planners are one page copied three hundred times. This one has 61 genuinely different page designs, built around the things that actually get in the way: starting, deciding, remembering, and not beating yourself up about it.

Tools you will not find in a normal planner:
• Guess vs actual – what you thought it would take, what it took
• Why I am avoiding it – six reasons, tick the one that fits
• Stuck on deciding – you do not need the best one, you need one
• Rejection sensitivity – when a small thing lands like a big one
• Talk to yourself kindly – answer the inner critic on paper
• Energy budget – you have less than the calendar suggests
• Hyperfocus log – where the hours went, without the shame
• Working backwards – plan from the deadline, not from today
• Before you buy it – the ten-minute check

WHAT'S INSIDE

Plan – 12 monthly grids, 52 Monday-start weekly spreads, and 372 daily pages: one thing today, a timed day from 7am, meds and water, a mood row, and room to dump your head out
Year – quarterly, goals, vision, project planner, weekly and monthly review
Focus – task breakdown, brain dump, focus sessions, obstacle plan, stuck on deciding, mind map, screen time, hyperfocus, estimating, avoidance, working backwards
Feelings – Stop/Think/Act, the worry loop, rejection sensitivity, the inner critic, D.O.S.E., gratitude, reframing, naming it, boundaries, energy budget
Habits – 31-day tracker, morning and evening routines
Health – medication log, sleep, symptoms, doctor visits, therapy notes, water and food, movement, cycle tracker
Life – meals and groceries, wheel of life, cleaning, budget, impulse check, reading log, dates to remember, subscriptions, trips, who does what
Notes – eight blank pages: dot grid, ruled, plain

FINDING THINGS

Ten tabs run down the side of all 502 pages. You are never more than two taps from any tool, or three from any specific day. Every page but the cover is a link destination. Nothing in it is a dead end.

ABOUT THE MONTH PAGES

Because it is undated, "Month 1" is whichever month you start in. Write the month name in the space at the top.

The month grids are positional rather than weekday-aligned – slot 1 is the 1st, whichever weekday that falls on. That is exactly what lets one grid fit every month. Each grid has thirty-one numbered slots, so in a shorter month you simply leave the spare ones blank.

CALM ON PURPOSE

No neon, no full-colour blocks, no busy borders. Just four muted accent colors and a soft sky wash – because a planner you find visually loud is a planner you stop opening.

It is also a light file, under 20MB for 502 pages, so it scrolls smoothly in GoodNotes instead of stuttering the way big planners often do.

HOW IT WORKS

1. Buy and download – one PDF, instantly, nothing is shipped to you
2. Open it in your note app – GoodNotes, Notability, Noteful, Xodo
3. Write on it with a stylus, or print the pages you want

WHAT YOU NEED

A tablet and a note-taking app that opens PDFs. GoodNotes and Notability are the most common. Works on iPad, Android tablets, and Windows. You can also print it at home – the pages are US Letter, and fit A4 with "scale to fit" turned on.

A NOTE ON THE LINKS

The side tabs and the month grids are real PDF links. They work in GoodNotes, Notability, Xodo, Adobe Acrobat and most tablet readers. Some basic in-browser PDF viewers ignore internal links – open it in a proper note app and they work.

PLEASE NOTE

This is a planner and a set of writing prompts. It is not medical advice and not a substitute for care from a professional.

This is a digital download. No physical item will be shipped. Because the file is delivered instantly, returns and exchanges are not accepted – but if anything is wrong with the file, message me and I will fix it.

For personal use. Please do not resell or redistribute the file.
```

---

## 이 상품의 강점 (구매자에게 무엇을 파는가)

리스팅 문구를 고치거나 문의에 답할 때 기준으로 삼을 내용입니다.
**전부 v8 FINAL 파일에서 실측으로 확인된 사실만 적었습니다.**

**1. 진짜 undated — 재고가 늙지 않는다**
파일 전체에 연도·월 이름이 **0회** 등장합니다(URL 제외 실측). 2026년에 만든 걸
2030년에도 그대로 팔 수 있고, 구매자 입장에선 "3월에 샀는데 1~2월이 이미
버려진" 상황이 없습니다.

> 이건 처음부터 사실이 아니었습니다. Quarterly 페이지가 `Jan – Mar` 처럼 월
> 이름을 박고 있었고, 2026-09-21 검수에서 발견해 `Quarter 1~4` + 직접 쓰는
> 필드로 바꿨습니다. **undated 주장을 건드리는 변경을 할 때는 반드시 월 이름
> 검사를 다시 돌릴 것.**

**2. 고유 페이지 58장 — 경쟁사가 숫자로 이기는 지점을 피한다**
700페이지짜리들은 데일리 한 장을 365번 복제한 겁니다. 조사에서 리뷰 최다
불만이 "너무 많은데 쓸 건 없다"였습니다. 우리는 반복 페이지(436장)와 고유
디자인(58종)을 **분리해서 명시**합니다.

*내부 메모* — 고유 61종 중 10장은 표지·목차·그룹 인덱스라서 **실제로 쓰는
템플릿은 48종**입니다. 영문은 "page designs"라 58로 방어 가능하지만, 경쟁사의
"고유 190페이지"와 비교하는 자리에서는 48을 기준으로 말하는 게 안전합니다.

**3. ADHD 실행기능에 특화 — 일반 플래너에 없는 도구**
"Guess vs actual(시간 감각)", "Why I am avoiding it(회피 이유 6지선다)",
"Stuck on deciding(결정 마비)", "Rejection sensitivity(거절 민감성)" 는
일반 웰니스 플래너에 없습니다. 당사자가 검색하는 단어이기도 합니다.

**4. 길을 잃지 않는다 — #1 불만에 대한 직접적인 답**
502페이지 전부에 10개 탭이 있고, 링크 주석 5,893개 중 **깨진 것 0개**,
커버를 뺀 501페이지 전부가 링크 목적지입니다. 어떤 도구든 2탭 이내,
특정 날짜는 3탭.

**5. 조용한 디자인**
원색 면 채우기 없음, 액센트 색 4개 상한(그 이상은 오히려 기억을 방해한다는
조사 근거), 글자에 쓰는 색은 전부 대비 기준 통과(최저 4.75:1).

**6. 가볍다 — 19.6MB / 502페이지**
경쟁 상품 상당수가 80MB를 넘어 GoodNotes에서 스크롤이 끊깁니다. 우리도 같은
문제를 겪고 고쳤기 때문에 근거가 있는 차별점입니다.

> ⚠️ **Etsy 디지털 파일 상한은 20MB이고 현재 여유가 4%뿐입니다.**
> 페이지를 추가하거나 이미지를 바꾸면 업로드가 막힐 수 있습니다. 재빌드
> 후에는 반드시 바이트 수를 확인하세요(19,227,515 bytes = 19.2MB).

---

## 가격

| 항목 | 값 |
|---|---|
| 정가 | **$16.99** |
| 런칭 세일 | 40% → **$10.19** |

Etsy는 할인 표시가 클릭률에 크게 작용합니다. 정가를 걸고 세일하는 게 처음부터 $10에 거는 것보다 유리합니다.

**근거** — 조사상 중간 티어가 $8~15(300~500페이지), 카테고리 1위 Future ADHD가 $19(고유 190페이지)입니다. 우리는 502페이지 / 고유 61페이지(실사용 템플릿 51종)라 페이지 수는 중간 티어, 고유 수는 그 아래입니다. $10~12 구간이 정직한 위치입니다.

리뷰가 10개 넘게 쌓이면 정가를 $19.99로 올리고 세일가를 $12~13으로 조정하는 걸 권합니다.

---

## 첫 리스팅에서 하지 말 것

- **페이지 수를 제목에 넣지 마세요.** 조사에서 리뷰 최다 불만이 "너무 많아서 못 찾겠다"였습니다. 숫자 경쟁은 이미 700페이지짜리들이 하고 있고, 우리 강점이 아닙니다
- **"ADHD 치료/개선" 같은 표현 금지.** 의료 효과를 주장하면 Etsy 정책 위반이고, 실제로 신고 대상입니다. "도구", "정리", "기록" 수준으로만 표현. 현재 영문 원고는 이 기준을 통과합니다(`treat`/`cure`/`reduce symptoms` 계열 0회)
- **탭 이동이 "2탭"이라고 단정하지 마세요.** 특정 날짜는 3탭입니다(MONTH 탭 → Month N → 날짜). 그래서 영문은 `never more than two taps ... or three from any specific day` 로 씁니다
- **환불 문구를 숍 정책보다 세게 쓰지 마세요.** `non-refundable` 은 EU·영국 구매자의 법정 권리 및 Etsy Purchase Protection 과 충돌할 수 있습니다. `shop.md` 의 정책 문구와 같은 말로 맞췄습니다
- **무료 폰트 라이선스 확인.** 현재 **Nunito(OFL)** 만 사용합니다. Caveat 는 링크만 걸려 있고 어떤 CSS도 참조하지 않아 2026-09-21에 빌드에서 제거했습니다. 나중에 폰트를 바꾸면 반드시 재확인

---

## Shop Home 편집 — 지금 채울 것 / 미룰 것

**숍 계정 쪽 확정값과 발행 순서는 `shop.md` 에 있습니다.** 여기는 요약만.

**발행 전 (10분)**
- **Shop policies** — "Try it now" 템플릿. 디지털 다운로드는 반품 정책을
  명시하지 않으면 분쟁 시 불리합니다. 건너뛰지 마세요
- **Tagline** — `Undated ADHD & wellness planners, iPad & Android`
  (`for iPad` 단독은 쓰지 않습니다 — 안드로이드·윈도우에서도 동작합니다)
- **Location** — 검색 필터에 쓰입니다. 비워두면 걸러집니다

**리스팅 발행 직후**
- **Shop announcement** — 런칭 세일 한 줄. 살 게 없는 상태에서 세일 공지를
  먼저 걸 이유가 없습니다(`shop.md` 발행 순서 5번)

**나중에 (매출 시작 후)**
- About 사진 5장 / 스토리 / 개인 bio — 전환에 도움은 되지만 리스팅 0개인
  지금은 순서가 아닙니다
- Banner, Color theme — 상품이 여러 개 쌓인 뒤에 통일감을 주는 용도
- FAQ — 실제로 같은 질문을 두 번 받으면 그때 추가

**안 해도 되는 것**
- **숍 소개 비디오**(300MB) — 이 카테고리에서 효과가 거의 없습니다.
  단 **리스팅 비디오는 별개** — GoodNotes에서 탭을 눌러 이동하는 10초 녹화는
  효과가 확실합니다(`shop.md` 참조). 이 상품의 핵심 기능이 링크 이동이라
  정지 이미지로는 전달이 안 됩니다
- Seller details — 이미 `Private individual` 로 맞게 되어 있습니다
