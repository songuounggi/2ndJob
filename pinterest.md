# 핀터레스트 — 설정과 핀 원고

이미지는 `output/pinterest/` 6장 (1000×1500, 2:3). 생성 스크립트는
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

핀을 담는 폴더다. 3개면 충분하다.

| 보드 | 설명 |
|---|---|
| `ADHD Planner` | Undated digital planners and tools for adult ADHD. |
| `Digital Planning` | GoodNotes, Notability, iPad and Android planning. |
| `Focus & Executive Function` | Tools for starting, deciding, and remembering. |

---

## 3. 핀 올리기

핀 하나당: **이미지 + 제목 + 설명 + 목적지 링크 + 보드**.

> **목적지 링크가 핵심이다.** 안 걸면 그냥 예쁜 그림이고 유입이 0이다.
> Etsy 리스팅 페이지 주소를 그대로 넣는다 (숍 주소가 아니라 **상품 주소**).
> 리스팅을 열고 브라우저 주소창에서 복사하면 된다.

---

## 핀 원고

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
