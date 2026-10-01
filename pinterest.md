# 핀터레스트 — 설정과 핀 원고

이미지는 `output/prod1/pinterest/` 6장 (1000×1500, 2:3). 생성 스크립트는
`scripts/build_pinterest.py`.

**왜 하는가** — Etsy 콜드 스타트를 끊기 위해서다. 조회가 0이면 Etsy 랭킹
피처도 0이고, 그러면 계속 검색에 안 뜨는 자기강화 루프에 갇힌다. 밖에서
사람을 밀어넣는 것이 그 루프를 끊는 유일한 방법이다.

> 아래 내용은 **일반적으로 알려진 방식**이고 우리 숍에서 측정한 것이 아니다.
> 핀터레스트 UI 는 자주 바뀌므로 버튼 이름은 화면에서 확인할 것.

---

## 계정 유형은 "기타" 로 둔다 — Etsy 는 인증이 안 된다 (2026-09-23 확인)

비즈니스 계정 온보딩에서 유형을 고르라고 한다. **`기타` 를 고른다.**

`온라인 판매점 또는 마켓플레이스` 가 맞아 보이지만 **(웹사이트 필수)** 다.
그리고 Pinterest 공식 문서가 이렇게 말한다:

> To claim a website, you must own the domain, subdomain or subpath, and you
> need to be able to edit the source code. As a result, you're unable to
> claim most social accounts and online stores hosted on marketplaces like
> **Etsy**, eBay and Amazon.

**Etsy 숍 주소는 "내 웹사이트" 로 인증할 수 없다.** 소스코드를 고칠 수
없기 때문이다. 인증 방법 네 가지(Google Merchant Center / HTML 태그 /
HTML 파일 / DNS TXT) 전부 도메인 소유가 필요하다.

Pinterest 자신이 "일반 Business 계정을 만들고 나중에 업데이트할 수
있습니다" 라고 안내하므로 `기타` 로 두고 진행한다.

> 언젠가 자체 도메인을 갖게 되면 그때 인증한다. 인증하면 내 핀에 프로필
> 사진이 붙고, 다른 사람이 내 사이트 이미지를 저장해도 내 프로필로 연결된다.

---

## 1. 계정

`pinterest.com` → 가입. **비즈니스 계정**으로 (무료).

개인 계정이 이미 있으면 설정에서 비즈니스로 전환하거나 비즈니스 계정을
따로 추가할 수 있다. 비즈니스여야 **애널리틱스**가 나오고, 그게 있어야
어느 핀이 먹히는지 알 수 있다.

프로필:

| 칸 | 값 |
|---|---|
| 이름 | `Song & Park Studio` |
| 사용자명 | `songandparkstudio` (Etsy 숍명과 통일) |
| 소개 | `Undated ADHD & wellness planners for iPad, Android and print. Instant download.` |
| 프로필 사진 | Etsy 숍 아이콘과 같은 것 |
| 웹사이트 | Etsy 숍 주소 |

**Etsy 숍 연결(claim) — 있는지 확인 못 했다.**

예전 Pinterest 에는 `설정 → 클레임한 계정(Claimed accounts)` 에서 Etsy 를
연결하는 항목이 있었다. **지금도 있는지 확인하지 못했다** — 공식 문서를
찾으려 했으나 해당 페이지가 404 이고, 도움말이 JS 로 렌더돼 링크를 뽑지
못했다.

확실한 것은 위 절의 내용뿐이다: **Etsy 숍 주소를 "내 웹사이트" 로는 인증할
수 없다.** 그것과 "Etsy 계정 연결" 은 다른 기능이다.

> 설정에 들어갈 일이 있으면 `클레임한 계정` 항목이 실제로 있는지 보고
> 여기에 적는다. **없으면 없다고 적는다.** 있는 척 남겨두면 다음에 또
> 찾아 헤매게 된다.

---

## 2. 보드 만들기

보드는 핀을 담는 폴더다. **핀 하나에 보드 하나가 아니라, 보드 하나에 핀
여러 개**가 들어간다.

### 지금은 보드 하나로 간다 (2026-09-29 정정)

`ADHD Planner` 하나에 여섯 장을 전부 넣는다.

아래 3개 안은 핀이 수십 장으로 늘어난다는 전제로 짠 것이다. 6장을 셋으로
나누면 3 / 2 / **1** 이 되어 한 보드는 핀 한 장짜리가 된다. **방문자에게
허전하고 Pinterest 에 줄 신호도 적다.**

핀이 20~30장쯤 되면 그때 나눈다. 핀 수정 화면에 `보드` 칸이 있어 **나중에
옮길 수 있다** -- 지금 나누지 않아도 잃는 것이 없다.

| 나중에 나눌 때 | 설명 |
|---|---|
| `ADHD Planner` | Undated digital planners and tools for adult ADHD. |
| `Digital Planning` | GoodNotes, Notability, iPad and Android planning. |
| `Focus & Executive Function` | Tools for starting, deciding, and remembering. |

### 이 계정은 2019년에 만든 개인 계정이다 -- 옛 보드 4개가 공개로 남아 있다 (2026-09-30 확인)

프로필 생성일 `2019-01-08`. 새로 판 계정이 아니라 **쓰던 개인 계정을 비즈니스로
전환한 것**이다. 그래서 공개 보드가 이렇게 섞여 있다:

| 보드 | |
|---|---|
| `ADHD Planner` | 상품용. 2026-09 에 만듦 |
| `약국 디자인` `약국 인테리어` `배경화면` `그림` | **개인 보드. 2019년 것** |

핀을 본 미국·영국 구매자가 프로필을 눌러 들어오면 **한국어 약국 인테리어
보드가 같이 보인다.** 치명적이지는 않지만 "ADHD 플래너 파는 곳" 이라는 인상이
흐려진다.

**정리한다면 지우지 말고 비공개(Secret)로 돌린다** -- 이 프로젝트 규칙이
"아무것도 지우지 않는다" 이고, 비공개 보드는 나만 보이되 그대로 남는다.

**아직 결정하지 않았다 (사용자에게 다시 물을 것, 2026-10-03 쯤).** 지금 순위는
핀 5장 올리기가 먼저다. 프로필 유입이 실제로 생긴 뒤에 판단해도 늦지 않다.

프로필: https://www.pinterest.com/songandparkstudio/
보드:   https://www.pinterest.com/songandparkstudio/adhd-planner/
**로그아웃 상태로는 보드 안이 안 보인다** -- Pinterest 가 막는다. 확인은 로그인해서.

---

---

## 3. 핀 올리기

핀 하나당: **이미지 + 제목 + 설명 + 목적지 링크 + 보드**.

> **목적지 링크가 핵심이다.** 안 걸면 그냥 예쁜 그림이고 유입이 0이다.
> Etsy 리스팅 페이지 주소를 그대로 넣는다 (숍 주소가 아니라 **상품 주소**).
> 리스팅을 열고 브라우저 주소창에서 복사하면 된다.

---

### 핀에 보이는 설명은 **Etsy 설명이다** -- 내가 쓴 설명이 아니다 (2026-09-30 확인)

올린 핀을 열어 보면 설명 자리에 **Etsy 리스팅 설명**이 떠 있다. 입력한 핀 설명이
아니다. 6장 전부 같은 글이 뜬다.

**원인:** Etsy 리스팅 페이지가 `schema.org/Product` 구조화 데이터를 내보내고, 그
`description` 이 리스팅 설명 원문이다(`listing.md` 118~120 줄과 글자까지 일치).
Pinterest 가 그것을 읽어 설명 자리에 대신 띄운다(리치 핀). Etsy 의 일반
`og:description` 은 `"This Planner Templates item is sold by ..."` 같은 밋밋한
문장이라 그쪽이 아니다 -- **상품 구조화 데이터 쪽**을 읽는다.

| 자리 | 실제 출처 |
|---|---|
| 제목 | **내가 쓴 핀 제목** (그대로 나온다) |
| 설명 | **Etsy 리스팅 설명** (6장 전부 동일) |
| 내가 쓴 핀 설명 | 저장은 된다. 알고리즘이 쓰는지는 **확인 못 함** |

**그래도 핀 설명은 지금처럼 정성껏 쓴다** (2026-09-30 사용자). 어디서 어떻게
노출될지 모르기 때문이다 -- Pinterest 공식 문서는 `Descriptions are used by our
algorithm` 이라고만 말하고, 리치 핀이 표시를 덮을 때 입력한 설명을 알고리즘이
쓰는지 안 쓰는지는 밝히지 않았다. 링크 없는 핀, 리치 핀이 안 잡히는 경우,
Pinterest 가 사양을 바꾸는 경우에는 그대로 노출된다. **확인 안 된 것을 근거로
품을 빼지 않는다.**

**따라가는 결론 두 개**

1. **Etsy 설명을 고치면 핀 설명도 따라 바뀐다.** 한 군데만 관리하면 된다
2. **핀마다 다른 것은 이미지와 제목 둘뿐이다.** 그래서 제목이 생각보다 중요하다 --
   6장의 각도를 서로 다르게 잡는다(날짜 없음 / 특이한 페이지 / 규모 / 탐색 /
   일상 / 이유). Pinterest 피드에는 **제목 앞 40자만** 보이므로 거기서 말이
   끊기지 않게 쓴다

---

### 게시 상태 -- **상품 1 여섯 장 전부 올림 (2026-09-30)**

| 핀 | 보드 | 링크 | 태그 |
|---|---|---|---|
| `01_hero` | ADHD Planner | 상품 1 리스팅 | 6개. **`에버노트` 가 섞여 있다**(게시 후 수정 불가) |
| `02_tools` `03_pages` `04_navigation` `05_everyday` `06_undated` | ADHD Planner | 상품 1 리스팅 | 아래 검증된 6개 |

이미지는 `output/prod1/pinterest_v815/` (옛 폴더 `output/prod1/pinterest/` 는 502p 이전
판이라 **쓰지 않는다**). **상품 2·3 핀은 아직 만들지 않았다** -- `output/prod2`·`prod3` 에
핀 폴더가 없다. `build_pinterest.py` 가 상품 1 전용이라 상품별로 손봐야 하고, 리스팅
이미지는 비율이 달라(핀은 1000x1500, 2:3) 그대로 못 쓴다.

**01 의 통계를 지금 믿지 않는다.** 2026-09-30 기준 노출 6 / 핀 클릭 3 인데, 그 클릭은
대부분 사용자 본인이 확인하려고 연 것이다. 핀터레스트는 Etsy 와 달리 전환율로 순위를
매기지 않아 **순위가 깎이지는 않지만 숫자를 읽을 수 없다.** 며칠 두고 6장을 합쳐서 본다.

**볼 지표는 `아웃바운드 클릭` 하나다** -- 내 Etsy 로 나간 클릭. `노출수`·`핀 클릭수` 는
핀터레스트 안에서 일어난 일이라 매출과 무관하다. 그리고 **Etsy Stats 의
`How buyers found you → Social` 과 같이 움직이는지 대조한다**(2026-09-29 기준 0%).

---

## 핀 원고

> 아래 `→ 보드 ...` 는 **나중에 나눌 때**의 배정이다. 지금은 전부
> `ADHD Planner` 에 넣는다(2절).

### 01_hero → 보드 `ADHD Planner`

**Title**
```
Undated ADHD Planner for GoodNotes — no dates to fall behind on
```

**Description**
```
An undated ADHD planner with no dates printed anywhere, so it never expires and you never open it to a wall of blank days you missed. 502 pages, 61 unique page designs, ten tabs on every page. Works in GoodNotes and Notability on iPad, on Android tablets, and prints at home. Instant download.
```

### 02_tools → 보드 `Focus & Executive Function`

**Title**
```
Six ADHD planner pages you will not find in a normal planner
```

**Description**
```
Guess vs actual for time blindness. Why I am avoiding it, with six reasons to tick. Stuck on deciding. Rejection sensitivity. Talk to yourself kindly. Energy budget. Built around executive function, not around pretty layouts. Part of an undated hyperlinked PDF planner for GoodNotes and Notability.
```

### 03_pages → 보드 `ADHD Planner`

**Title**
```
61 genuinely different planner pages, not one page copied 300 times
```

**Description**
```
Most big digital planners are one daily page repeated hundreds of times. This one has 61 unique page designs across focus, feelings, habits, health and life admin, plus monthly grids, weekly spreads and daily pages. Undated hyperlinked PDF for iPad and Android.
```

### 04_navigation → 보드 `Digital Planning`

**Title**
```
Ten tabs on every page — never lose your place in a big planner
```

**Description**
```
The most common complaint about big digital planners is not being able to find anything. Ten side tabs run down all 502 pages, and every page but the cover is a link destination. Real PDF links that work in GoodNotes, Notability, Xodo and Acrobat.
```

### 05_everyday → 보드 `Digital Planning`

**Title**
```
Daily and weekly planner pages for ADHD — timed day, meds, mood
```

**Description**
```
424 daily and weekly pages. One thing today, a timed day from 7am, meds and water, a mood row, and room to dump your head out. Weekly spreads start on Monday. Undated, so start any day and skip a week without guilt.
```

### 06_undated → 보드 `ADHD Planner`

**Title**
```
Why an undated planner works better when you have ADHD
```

**Description**
```
It never expires, so you buy it once and use it for years. There is no wall of missed days sitting there blank and accusing. And you can start in the middle — March, a Wednesday, whenever you actually feel like starting. Not a single date printed anywhere.
```

---

## 상품 4 The ADHD Home Reset 핀 원고 (**초안** 2026-10-02 -- 출시 뒤 리스팅 링크를 걸어 올린다)

그림: `output/prod4/pinterest/draft-v0.2/01_guests.png ~ 06_undated.png` (`python scripts/p4/pinterest_p4.py`, 1000x1500).
각도 6개를 서로 다르게: 손님맞이 · 기운 없는 날 · 엉망일 때 · 10분 방 · 인쇄 · 날짜 없음. **01 손님맞이를 먼저** -- 11~12월
연말 손님맞이 시즌(`product4-content.md` 판매 계획)에 맞추려면 출시 직후 바로 올려야 한다(핀은 몇 주에 걸쳐 퍼진다).
보드는 지금 규칙대로 전부 `ADHD Planner`. 문구는 `listing-p4.md` 설명·원고에 있는 말만, 1인칭 당사자 표현 없음.
제목은 피드에 보이는 **앞 40자** 안에서 말이 끝나게.

### P4-01_guests
**Title** `Guests in 2 hours? Clean what they see`
**Description**
```
A cleaning planner for ADHD brains with a "guests in 2 hours" page: entry, bathroom, living room, kitchen, and one box for everything else. Each room links to a ten-minute reset card. Hyperlinked PDF for Goodnotes and Notability, plus a printable black-and-white version.
```

### P4-02_energy
**Title** `Low battery? Pick a 2-minute task`
**Description**
```
Clean by energy, not by schedule. The energy menu sorts 31 tasks by battery (low, medium, full) and time (2, 5, 10, 20 minutes), and every task links to the page it belongs to. An undated ADHD cleaning planner for Goodnotes and Notability.
```

### P4-03_rescue
**Title** `House all too much? Try Rescue mode`
**Description**
```
Rescue mode for ADHD cleaning: trash first, gather the dishes, one basket of clothes, clear a path, one surface. Then stop. An SOS button on every page after the cover takes you there. Hyperlinked PDF planner for Goodnotes and Notability.
```

### P4-04_rooms
**Title** `10-minute room resets, then stop`
**Description**
```
Ten room reset cards, each with a six-step, ten-minute order and a "done enough" line so you know when to stop. A deep clean list for every room. Undated ADHD home reset planner, hyperlinked for Goodnotes, printable in black and white.
```

### P4-05_print
**Title** `Printable ADHD home reset checklist`
**Description**
```
The same pages as the hyperlinked planner in grayscale, easy on ink. US Letter size; prints on A4 with "fit to page". Energy menu, room reset cards, rescue mode, 52 undated reset weeks, and cleaning tools.
```

### P4-06_undated
**Title** `Skip a week. Nothing to catch up on.`
**Description**
```
52 undated reset weeks. Start on any week; blank boxes are normal and there is nothing to catch up on. Missed a day? Slide it to the next slot. An ADHD cleaning and home routine planner for Goodnotes, Notability, and print.
```

### 핀 올릴 때 실제로 막히는 것들 (2026-09-30, 상품 1 핀 5장 올리며 확인)

**태그(`태그된 주제`) 는 영어 키워드가 안 먹는다.** 검색 키워드를 받는 칸이 아니라
Pinterest 가 미리 정해둔 **관심사 목록에서 고르는** 칸이고, 계정 UI 가 한국어라
**한글 이름으로 쳐야 뜬다.** `adhd` `goodnotes` `ipad planner` 같은 건 하나도 안 뜬다
(`ADHD` 는 진단명이라 관심사 목록에서 빠진 것으로 보이나 **확인 못 함**).
태그는 사람들에게 안 보이고 알고리즘에만 쓰인다.

**게시한 뒤에는 태그를 못 고친다.** 반드시 `게시` 누르기 전에 넣는다.

**검증된 태그 6개** -- 상품 1 핀 5장에 이대로 넣었다. 다시 찾지 말고 그대로 쓴다:

```
데일리 플래너 템플릿
Therapy Worksheets
관리 팁
시간 관리
개인 플래너
라이프 플래너
```

여유가 있으면 `플래너` `디지털 플래너` `생산성` `자기관리` 도 쳐본다.

**넣지 않는 것:** `에버노트`(다른 앱 -- 봐도 안 산다), `디지털 종이`(스크랩북용
배경 무늬지, 플래너가 아니다). 기준은 **"봐도 안 살 사람이 있는 곳인가"** 다.
전환율이 순위 지표라 엉뚱한 노출은 손해다.

**토글 3개** (기본값이 우리에게 맞지 않는다):

| 토글 | 어떻게 | 왜 |
|---|---|---|
| **AI 수정으로 표시** | **끔** | 핀 이미지는 HTML/CSS 를 Chrome 이 렌더한 것이지 생성형 AI 이미지가 아니다. 불필요한 AI 라벨은 노출을 깎을 수 있다 |
| **비슷한 상품 표시하기** | **끔** | 켜면 내 핀 위에 "유사 상품"(= 경쟁 플래너)이 붙는다. Etsy 로 보내려는 트래픽이 샌다 |
| 댓글 달기 허용 | 켬 | 질문 대응 + 참여 신호 |

`상품 태그`·`추가 옵션`·`대체 텍스트` 는 건너뛴다. `나중에 게시` 는 끈다.

**핀마다 바뀌는 것은 이미지·제목·설명 셋뿐이다.** 링크·보드·태그·토글은 전부 같다.

**화면에서 헷갈리는 두 가지**

1. **`변경 사항이 저장되었습니다!` 는 초안 저장이지 게시가 아니다.** 왼쪽
   `핀 초안 (n)` 목록에 남아 있으면 아직 안 올라간 것이다
2. **올린 핀은 프로필 `저장됨(Saved)` 탭 아래 보드에 있다.** `생성됨(Created)` 은
   핀 낱개를 보는 곳이고 갱신이 느리다. 갓 올린 핀이 프로필 첫 화면에 안 보여도
   게시는 된 것일 수 있다
3. **로그아웃 상태로는 보드 내용이 안 보인다** -- Pinterest 가 막는다. 확인은 로그인해서

---

## 4. 올리는 속도

**6장을 한 번에 다 올리지 않는다.** 하루 한두 개씩 나눠서 올린다. 꾸준한
활동을 선호한다고 알려져 있다(검증된 건 아니다).

같은 이미지를 다른 보드에 다시 핀하는 것도 가능하지만, 간격을 두고 한다.

---

## 5. 기대치

**즉효가 아니다.** 핀이 검색에 자리 잡는 데 몇 주 걸린다. 대신 한 번
자리 잡으면 몇 달씩 유입이 이어진다 — 인스타·X 는 몇 시간이면 묻히는데
핀터레스트는 축적된다. 그게 이 채널을 고른 이유다.

**며칠 단위로 확인하지 않는다.** `forecast.md` 대조일(2026-10-21)에 Etsy
Stats 의 Traffic sources 와 함께 본다. 거기서 핀터레스트 유입이 잡히는지가
이 시도의 성패다.
