# Etsy 발행 체크리스트 — SongAndParkStudio

숍 계정 + 리스팅 입력값의 **확정본**. 리스팅 원고(제목/태그/설명 본문)는
`listing.md`, 상품 제작 규칙은 `CLAUDE.md`.

**이 파일은 결정을 남기는 곳이다.** 세션이 바뀌면 대화는 사라지고 파일만 남는다.
설정을 바꾸면 여기도 같이 고칠 것.

최종 점검: 2026-09-21

---

## 0. 현황

**발행 전 준비 완료 (2026-09-21)** — Payoneer 승인 / Etsy-Payoneer 연결 /
Billing 카드+Autobilling / Currency USD / Policy 4개 탭 / Location `Seoul,
South Korea` / Tagline. 남은 것은 **리스팅 작성과 발행**뿐이다.

| 항목 | 값 |
|---|---|
| 숍 이름 | `SongAndParkStudio` |
| 개설 | 2026 |
| 리스팅 | **0개 — 아직 발행 전** |
| 판매 / Admirers | 0 / 0 |
| 판매자 상태 | `Private individual` (사업자 아님, 맞게 설정됨) |
| 지역 | South Korea |
| 상품 파일 | `output/planner_v8-undated-FINAL.pdf` |
| 리스팅 이미지 | `output/listing/01~09_*.png` (2000x2000, 9장) |

---

## 1. 계정 필수 — 이게 없으면 발행 버튼이 안 눌린다

리스팅 원고보다 먼저 확인할 것. **미설정이면 리스팅을 다 써놓고 막힌다.**

- [x] **입금 수단 — 한국은 Payoneer 경유다** (2026-09-21 승인 완료)

      한국 셀러는 Etsy Payments 로 은행계좌를 직접 연결하는 방식이 아니라
      **Payoneer 계정을 거쳐** 입금받는다. 순서는:

      1. Payoneer 가입 → 심사 → **"계정이 승인되었습니다"**
      2. Payoneer 가 한국 계좌로 **소액 입금(100원)** 을 보내 계좌를 인증
      3. Payoneer 에 USD / EUR / GBP 수취 계좌가 열린다
      4. Etsy → Finances → Payment settings 에서 이 Payoneer 가 입금 수단으로
         잡혀 있는지 확인

      심사에 시간이 걸리므로 **제일 먼저 시작할 것.** 판매 대금은
      Etsy → Payoneer(USD) → 원화 출금 순으로 오고, 마지막 단계에서
      환전 수수료가 붙는다.
- [x] **청구 수단 (Billing)** — Finances → Payment settings → Billing.
      카드 등록 + Default 지정 + Autobilling ON. 2026-09-21 완료.
      **입금 계좌와 완전히 별개 칸이다** — 리스팅 등록비와 수수료가 여기서 나간다
- [x] **Shop currency = USD** — Finances → Payment settings → Currency.
      2026-09-21 확인. `$16.99 / $10.19` 가격 전략이 USD 기준이라 KRW 로
      두면 환산된 어정쩡한 숫자가 되어 심리적 가격대가 깨진다
- [x] **Payment Methods** — Etsy Payments 활성, Payoneer 가 입금 계정으로
      연결됨(Payee ID / Payoneer Customer ID 발급). 구매자 결제수단은
      Visa·Mastercard·Amex·Apple Pay·Google Pay·Klarna·PayPal 등 기본값 전부
      켜진 상태로 **그대로 둔다** — 쓰던 수단이 없어서 이탈하는 걸 막아준다.
      입금 주기 `Once per week` 도 그대로. 2026-09-21 확인
- [x] **Location** — Shop Home. `Seoul, South Korea`. 검색 지역 필터에 쓰이고
      **비워두면 그 필터에서 통째로 빠진다.** 디지털이라 배송이 없어도 동일.
      입력 방법은 3-2 참조 (국가가 아니라 도시다)
- [x] **Shop policies** — 4개 탭 전부. 3-3 참조. 디지털은 정책이 분쟁의
      유일한 근거다
- [x] **Tagline** — 3-1 참조

> **수수료가 붙는 구간을 헷갈리지 말 것.**
> `Etsy → Payoneer` 주간 입금은 자동이고 보통 수수료가 없다.
> 수수료·환전이 걸리는 건 `Payoneer → 원화 계좌` 출금이고, 이건 직접 누를
> 때만 일어난다. **건건이 빼지 말고 모아서 한 번에 뺄 것.**

**수수료 감안** — 리스팅 등록 $0.20(4개월) + 거래 수수료 + 결제 처리 수수료.

리스팅 폼의 **Estimated earnings** 가 실측값을 준다(2026-09-21):

| 판매가 | Etsy 추정 수령액 | 차감 |
|---|---|---|
| $16.99 | **$14.28** | $2.71 (약 16%) |
| $10.19 (세일가) | 약 $8.5 | 같은 비율 적용 |

> 개별 수수료율은 화면마다 다르게 보인다(Currency 화면은 `5%`, 널리 알려진
> 값은 `6.5%`). **합계로 보는 게 맞다 — 약 16%.** 첫 판매 후
> Finances → Monthly statements 에서 실제 청구 내역을 확인할 것.

---

## 2. 리스팅 입력 항목 — 칸별로 넣을 값

**2026-09-21에 실제로 작성하며 확인한 화면 기준.** 폼은 한 페이지에 전부
펼쳐져 있고 위쪽 탭(Photo & Video / Item Details / Item Options /
Pricing & Shipping / How It's Made / Settings)은 같은 페이지의 앵커다.

**★ = 필수**

### A. Photo and video

| 칸 | 값 |
|---|---|
| ★ **Photos** | **최대 20장** (10장이 아니다). `output/listing/` 의 9장을 01→09 순서로 |
| **Videos** | 최대 2개. 지금은 생략. GoodNotes에서 탭을 눌러 이동하는 10초 녹화는 효과가 확실하므로 나중에 추가할 것 |

첫 번째 사진(`01_hero.png`)이 검색 결과 썸네일이다.

### B. Item details

| 칸 | 값 |
|---|---|
| ★ **Category** | `planner` 검색 → **`Planner Templates`** 선택. 드롭다운의 `Physical or digital` / `Digital` 배지는 **그 카테고리가 디지털을 허용하는지**를 뜻한다 |
| ★ **What type of item is it?** | **`Digital`** ← 카테고리를 고르면 바로 아래 나타난다 |
| ★ **Title** | `listing.md` 제목 (119자). **대문자 단어 3개 제한**에 걸린 이력 있음 |
| ★ **Digital files** | `output/planner_v8-undated-FINAL.pdf`. 최대 5개 |
| ★ **Description** | `listing.md` 의 상품 설명 블록 전체 (약 4,100자) |

> **Title 위에 뜨는 "Suggested" 배너는 `Dismiss`.** `Apply suggestion` 을
> 누르면 Etsy 가 제안하는 짧은 제목으로 덮어쓰는데, 우리 제목이 키워드가
> 더 많고 대문자 규칙까지 맞춰둔 것이다.

> **`This digital item is made to order` 체크박스는 비워둔다.** 체크하면
> 즉시 다운로드가 아니라 제작 대기 상품이 된다.

**Digital 로 바뀌면 화면이 이렇게 변한다** — 셋 다 확인되어야 제대로 된 것:
1. `Digital files` 섹션이 생긴다
2. Shipping 섹션이 `Buyers will download your uploaded files immediately
   after purchase.` 한 줄로 바뀐다 (배송 설정 사라짐)
3. Variations 가 `Variations are unavailable for digital items.` 가 된다

### C. Item options / Attributes

| 칸 | 값 |
|---|---|
| Variations | 디지털은 불가. 건너뜀 |
| Custom options | 건너뜀 |
| **Tags** | `listing.md` 태그 13개. **Description 칸과 헷갈리지 말 것** |

> 2026-09-21에 **태그 목록을 Description 칸에 붙여넣는 실수**를 했다.
> 그대로 발행하면 상품 설명란이 검색어 나열이 되고, 키워드 스터핑으로
> 보일 수 있다. 두 칸은 화면에서 멀리 떨어져 있다 —
> Description 은 **Item details** 안, Tags 는 **Attributes** 안이다.

### D. Price and inventory

| 칸 | 값 |
|---|---|
| ★ **Price** | `16.99` (USD) |
| ★ **Quantity** | `999` — 디지털은 차감되지 않는다. 범위는 1~999 |
| SKU | 비워둠 |
| Add estimated US tariff cost | 디지털은 관세 없음. 건너뜀 |

가격을 넣으면 **Estimated earnings** 가 바로 뜬다. 이게 수수료 실측값이다.

런칭 세일 40%는 리스팅 폼이 아니라 **Marketing → Sales & discounts →
`Run a sale`** 에서 따로 건다. 발행 후에 설정한다.

**2026-09-21 설정한 값**

| 칸 | 값 |
|---|---|
| Discount amount | `Percentage off` / **40** |
| Where valid | `Everywhere` |
| Sale duration | `2026-09-21 ~ 2026-10-20` (Etsy 상한 30일) |
| Terms and conditions | 비움 — 상품 페이지에 그대로 노출되는데 걸 조건이 없다 |
| Sale name | `LAUNCH40` (영문·숫자만, 구매자에겐 안 보임) |
| Which listings | **`Select listings`** → 플래너 1개만 |

> **`All listings` 를 고르지 않는다.** "includes all current **and future**
> listings" 라서, 세일 기간에 새 상품을 올리면 그것도 자동으로 40% 가 된다.
> 할인은 매번 의식적으로 결정해야 한다.

> 화면은 25% 를 권하지만 40% 로 간다. **지금 목표는 마진이 아니라 첫 리뷰다.**
> 리뷰 0개가 전환율의 최대 병목이고 $10 아래가 "일단 질러볼까" 문턱을 넘는다.
> 25%(=$12.74, 수령 약 $10.7) 대비 건당 $2 남짓 손해지만, 그걸로 첫 리뷰를
> 몇 주 앞당기면 남는 장사다. 리뷰 10개 뒤 정가 $19.99 / 세일가 $12~13 으로 조정.

**세일 중에는 다른 프로모션을 켜지 않는다** — Promo code 는 구매자가 코드를
입력해야 하고 배지도 안 붙는다. Interested shopper / Abandoned cart /
Favorited item 류는 기존 트래픽이 있어야 발동하므로 조회 0 인 지금은 대상이 없다.

**Cyber Specials (2026-11-23 ~ 12-01)** — Etsy 공식 세일 이벤트. 연말은
플래너 최대 성수기다. 달력에 적어둘 것.

### E. GPSR manufacturer and safety information

**건너뜀.** "trader" 로 EU·북아일랜드에 파는 사업자용이다. 우리는
`Private individual` 이다.

### F. How it's made

| 칸 | 값 |
|---|---|
| ★ **Who made it?** | `I did` |
| ★ **What is it?** | `A finished product` |
| ★ **How is this digital content created?** | **`With an AI generator`** |
| Production partners | 없음 |

> `When was it made?` 는 **디지털 상품에는 나오지 않는다.** 대신 위의
> AI 고지 질문이 뜬다.

> **AI 고지를 `Created by me` 로 하지 않은 이유** — 페이지 문구(도구 이름과
> 안내문), 레이아웃 설계, 생성 스크립트를 AI 가 실질적으로 만들었다.
> 방향 설정·판단·반려·검수·상품화는 전부 사람이 했지만, Etsy 가 이 질문을
> 넣은 목적은 그 관여 여부를 아는 것이다. Etsy 는 AI 활용 자체가 아니라
> **숨기는 것**을 문제 삼는다. 고지하고 파는 셀러가 많다.

### G. Settings

| 칸 | 값 |
|---|---|
| **Shop section** | `ADHD Planners` 새로 만들기 |
| Feature this listing | 꺼둠 |
| ★ **Renewal options** | `Automatic` (4개월마다 $0.20) |

---

## 3. Shop Home — 채울 5개

숍 홈은 **이미 리스팅을 클릭한 사람**이 보는 2차 페이지다. 아래 5개만 하고
나머지는 미룬다.

### 3-1. Tagline (55자 제한)

```
Undated ADHD & wellness planners, iPad & Android
```

48자. **`for iPad` 단독은 쓰지 않는다** — 이 상품은 iPad 전용이 아니다.
안드로이드 태블릿·윈도우에서 동작하고 인쇄도 된다. `iPad` 키워드는 검색량
때문에 남기되, 그 한 줄만 보고 안드로이드 사용자가 지나가지 않게 한다.

감성 문구("Handmade with love" 류)는 검색 기여가 0이라 쓰지 않는다.

### 3-2. Location

필수. 위 1번 참조.

**국가가 아니라 도시를 넣는다.** `South Korea` 를 치면 드롭다운에 South
Moravian / South Africa / South Carolina 같은 것만 뜨고 저장하면
`Must select city from suggestions.` 로 막힌다(2026-09-21에 실제로 겪음).

```
Seoul
```

부산 `Busan`, 인천 `Incheon`, 성남 `Seongnam`, 대전 `Daejeon`,
대구 `Daegu`, 수원 `Suwon`, 고양 `Goyang`, 용인 `Yongin`.

- 타이핑만 하고 Save 를 누르면 같은 에러가 난다. **드롭다운 항목을
  클릭해서 선택**해야 한다
- 내 동네가 목록에 없으면 가장 가까운 큰 도시를 고른다(다이얼로그 안내대로)
- 이 값은 숍 페이지에 **공개**된다. 동네를 드러내기 싫으면 근처 광역시로
- 화면 하단의 `South Korea` 는 계정 지역(통화·세금)이라 이것과 별개다

### 3-3. Shop policies — 이 화면에서 제일 중요

디지털 다운로드는 환불 정책을 명시하지 않으면 분쟁(케이스) 시 판매자가 불리하다.
"Try it now" 템플릿에서:

- **Returns & exchanges** → **Not accepted**
- **Cancellations** → 발송 전 취소만 (즉시 전달이라 사실상 해당 없음)

사유 설명란:

```
Because this is an instant digital download, I can't accept returns or
exchanges. If the file doesn't open, a link doesn't work, or anything is
wrong with it, message me — I'll fix the file and send you the corrected
version at no charge.
```

> `non-refundable` 처럼 더 센 표현은 쓰지 않는다. EU·영국 구매자의 법정
> 권리 및 Etsy Purchase Protection 과 충돌할 수 있다. `listing.md` 의 영문
> 설명도 같은 말로 맞춰져 있다 — **한쪽만 고치지 말 것.**

Policy settings 화면은 탭이 **4개**다. 2026-09-21에 Privacy 를 빠뜨린 채
"정책 완료"로 넘어갈 뻔했다.

| 탭 | 상태 |
|---|---|
| Returns & exchanges | ✅ `No returns or exchanges` + 문의 안내 |
| Cancellations | ✅ `before item has shipped` (즉시 전달이라 실질적으로 취소 창 없음) |
| **Privacy** | ✅ 아래 원문으로 등록 (2026-09-21) |
| Fixed policies | ✅ 수정 불가. 배송·관세 문구가 보이지만 디지털 리스팅에는 표시 안 됨 |

> 저장 후 목록 카드에서는 소제목과 빈 줄이 **한 덩어리로 뭉쳐 보인다.**
> 카드가 미리보기라 공백을 접는 것뿐이고, 연필(Edit)로 열면 원문 그대로다.
> 놀라서 다시 쓰지 말 것.

### 3-3-1. Privacy policy — EU 구매자가 있으면 필수

Etsy 화면이 직접 명시한다: *"If you ship to the European Union or offer your
listings to EU buyers, you're required to have a GDPR-compliant privacy
policy."* 디지털 다운로드는 기본이 전 세계 판매라 **해당된다.**

Privacy 탭 → `Create policy`:

```
WHAT I COLLECT

To fulfil your order I receive information from Etsy: your name, email
address, and billing or delivery details. I do not collect anything beyond
what Etsy passes to me, and I do not ask you for extra information.

WHY I NEED IT

I use it only to deliver your order, to reply to messages you send me, and
to keep the records that tax and accounting law require.

WHO I SHARE IT WITH

Nobody, for marketing purposes. I never sell your information. Etsy
processes the order and the payment. I may disclose information only where
the law requires it.

HOW LONG I KEEP IT

I keep order records for as long as tax and accounting law requires, then
delete them.

YOUR RIGHTS

If you are in the European Union or the United Kingdom you can ask me to
see, correct, or delete the personal information I hold about you, or to
restrict how it is used. Message me through Etsy and I will respond. You
also have the right to complain to your local data protection authority.

CONTACT

The fastest way to reach me is an Etsy message. I usually reply within a day.
```

> 법률 자문이 아니다. 개인이 디지털 상품만 파는 전형적인 경우에 맞춘
> 출발점이며, 실제와 다른 부분(별도 메일링 리스트 운영 등)이 생기면 고칠 것.
>
> **집 주소를 여기 적지 않는다.** 연락 수단은 Etsy 메시지로 충분하다.
> 주소가 걸리는 곳은 Shop Home 하단의 "Add more details for buyers"(EU DSA)
> 이고, `Private individual` 이면 필수가 아닐 가능성이 높다(4번 참조).

### 3-4. Shop announcement — 발행 직후

앞 ~160자만 펼쳐 보이고 나머지는 "Read more"로 접힌다.

```
Launch week: 40% off the Undated ADHD Planner. Instant download, works in
GoodNotes and Notability, no dates to expire. Questions? Just message me —
I usually reply within a day.
```

### 3-5. Shop icon — **미결정**

현재 가족 + 강아지 사진. 검색 결과에서는 **지름 약 75px 원형**으로 줄어
얼굴 셋 + 강아지가 뭉개진다 — "무슨 가게인지"가 안 읽힌다.

- 아이콘 → 단색 배경 + 이니셜(`S&P`) 또는 단순 심볼
- 판매자 얼굴 → About 섹션 사진으로 이동

신뢰감 vs 가독성 취향 문제라 강제는 아님. 정하면 이 줄을 고칠 것.

---

## 4. 미루는 것 / 안 하는 것

**첫 매출 이후로 미룸**

| 항목 | 왜 지금 아닌가 |
|---|---|
| About 사진 5장 / Story / Headline | 도움은 되지만 리스팅 0개면 볼 사람이 없다. 발행 후 1순위 |
| Shop members 개인 bio | **"ADHD 당사자가 자기가 쓰려고 만들었다"** 는 이 카테고리에서 꽤 강한 설득 포인트다. 나중에 꼭 채울 것 |
| Banner / Color theme | 리스팅이 여러 개 쌓여야 통일감이라는 게 생긴다 |
| Featured area | 최소 4개는 있어야 "골라서 강조"의 의미가 생긴다 |
| FAQ | 미리 지어내지 말 것. **같은 질문을 실제로 두 번 받으면** 그때 추가. 후보: 인쇄 가능 여부 / 안드로이드 / 링크가 안 눌림 |

**안 함**

- **숍 소개 비디오**(최대 300MB) — 이 카테고리에서 전환 기여가 거의 없다.
  **리스팅 비디오는 별개이고 권장**(위 2-A)
- **Seller details 변경** — 이미 `Private individual` 로 맞다

**확인만 할 것**

- [ ] Shop Home 하단 **"Add more details for buyers"** — EU 소비자 보호법(DSA)
      연락처 칸. 개인 판매자도 EU 판매 시 이름·주소·연락처를 요구받을 수 있다.
      **필수 표시(빨간 별표)가 있는지**만 열어서 확인. 필수면 채워야 EU 노출이 막히지 않는다

---

## 5. 상품 실측값 (2026-09-21 재검증)

리스팅에 숫자를 쓸 때 이 표를 근거로 삼는다. 전부 FINAL 파일에서 직접 측정.

| 항목 | 값 |
|---|---|
| 페이지 | 494 |
| 고유 디자인 | **58** (= 전체 패턴 61 − 반복 3종) |
| 반복 페이지 | 436 (데일리 372 + 위클리 52 + 먼스 12) |
| 링크 주석 | 5,805 / **깨진 것 0** |
| 링크 목적지가 되는 페이지 | 493 (도달 불가는 커버 1장뿐) |
| 파일 크기 | 19,227,515 bytes = **19.2MB** |

> 고유 58종 중 10장은 표지·목차·그룹 인덱스라서 **실제 쓰는 템플릿은 48종**이다.
> 영문 "page designs"로는 58이 방어되지만, 경쟁사의 "고유 190페이지"와 비교하는
> 자리에서는 48을 기준으로 말하는 게 안전하다.

---

## 5-0. 한국에서 보면 가격이 10% 비싸 보인다 (정상)

발행 후 숍 화면에서 `USD 11.21` / 원가 `USD 18.69` 로 떴다. 설정값은
`$16.99 → $10.19` 인데 **정확히 10%** 가 더 붙은 값이다.

**한국 부가세다.** 상품 페이지 모바일 화면이 상품명 바로 아래에
`VAT Included` 라고 직접 표시한다. 디지털 상품은 보는 사람의 국가 기준으로
세금이 붙어서, 한국에서 보면 10% 가 포함되어 보인다.

```
16.99 × 1.10 = 18.69
10.19 × 1.10 = 11.21
```

미국 구매자에게는 `$16.99 → $10.19` 로 보인다. **가격을 고치지 말 것.**
확인하려면 페이지 하단 `Regions` 를 United States 로 바꿔보면 된다.

---

## 5-3. 검색 순위 기준선 (2026-09-22 실측)

Claude 브라우저로 Etsy 검색을 직접 돌려 리스팅 `4579443848` 이 나오는지
확인했다. **9/28 에 다시 재서 움직였는지 비교할 기준선이다.**

### 나온다

| 검색어 | 위치 |
|---|---|
| `adhd journal hyperlinked pdf undated` | 1페이지 2번째 |
| `hyperlinked pdf journal neurodivergent planner` | 1페이지 2번째 |
| `hyperlinked pdf neurodivergent` | 1페이지 3번째 |
| `adhd digital planner undated goodnotes ipad neurodivergent` | 1페이지 3번째 |

### 안 나온다

```
adhd planner                     25페이지까지 확인, 없음
adhd digital planner
undated adhd planner
undated adhd planner goodnotes
neurodivergent planner
hyperlinked pdf journal
```

### 읽는 법 — 이 결과는 좋은 소식이 아니다

패턴은 **`hyperlinked` + `neurodivergent` 가 동시에 들어간 질의에서만
나온다**는 것이다. 둘 중 하나만으로는 사라진다.

**그런 검색어를 치는 사람은 없다.** 5단어짜리에 `hyperlinked` 같은 단어를
굳이 넣는 구매자는 존재하지 않는다. 즉 **검색량이 있는 말로는 안 나오고,
안 나오는 말로만 나온다.**

> 이 결과를 "롱테일에서 1위"로 읽으면 안 된다. 경쟁자가 0인 구석에서
> 1위인 것이고, 트래픽 가치는 0에 가깝다.

**건진 것은 하나** — SEO 자체는 망가지지 않았다. `hyperlinked` /
`neurodivergent` / `undated` 가 전부 색인에 제대로 등록돼 있다. **제목과
태그의 문제가 아니라 숍 권위가 0인 문제다.** 그러므로 제목을 만지작거릴
이유가 없다. `shop.md` 5-1 의 "제목 제안을 받지 않는다"는 결정도 이걸로
뒷받침된다.

### 다시 잴 때

같은 검색어 목록으로 재고, **`adhd planner` 에서 몇 페이지에 나오는지**가
유일하게 의미 있는 지표다. 롱테일 순위는 변해도 의미가 없다.

---

## 5-5. 디지털 파일명은 구매자에게 보이고, 올린 뒤엔 못 고친다

Etsy 공식 문서 원문:

> The file names you see will be the same ones your buyers see. We don't
> have a way of editing the name after uploading, so be sure to name your
> files appropriately first.

`planner_v8.18-undated-FINAL.pdf` 같은 내부 이름을 그대로 올리면 구매자
다운로드 폴더에 버전 번호가 남는다. 업로드용 사본을 따로 만든다:

```
output/upload/ADHD-Wellness-Planner-Undated-502-pages.pdf
```

제약: **70자 이내**, 영숫자와 `.` `_` `-` 만. 공백 불가.

### 파일을 교체하면 기존 구매자는 어느 버전을 받는가 — **확인 못 했다**

공식 문서는 접근 권한만 말한다("Canceling an order is the only way to
revoke a buyer's access"). 어느 버전이 나가는지는 안 밝힌다.

→ **"업데이트 무료 제공" 같은 문구는 쓰지 않는다.** 검증 못 한 약속이다.
구매자가 생긴 뒤 파일을 고치면 Etsy Messages 로 직접 알린다.

구매자 재다운로드 경로: Your account -> Purchases -> Download Files.
횟수·기간 제한은 없다(공식 문서 확인).

---

## 6. v8.18 교체 — **아직 올리지 않았다** (2026-09-23)

현재 Etsy 에서 팔리는 파일은 **v8-undated (494p)** 다. 아래는 준비만 된
상태이고, 업로드 전까지 리스팅 문구는 494/58 그대로 두어야 한다.

| 올릴 것 | 경로 |
|---|---|
| PDF | `output/planner_v8.18-undated-FINAL.pdf` (502p, 19,599,557B) |
| 이미지 10장 | `output/listing_v815/01_hero.png` ~ `10_mosaic.png` |

> `listing_v815/` 에 `10_closeup.png` 가 같이 있다. 그건 **옛 파일**이고
> 올릴 것은 `10_mosaic.png` 다.

### 바뀌는 숫자

```
494 pages  -> 502 pages
고유 58종  -> 61종      (비반복은 66장이지만 노트 8장의 디자인은 3종뿐)
493 linked -> 501 linked
```

### 순서 (이 순서를 지킬 것)

1. Etsy 디지털 파일 교체 → v8.18
2. 이미지 10장 교체
3. Etsy 본문 숫자 수정
4. `listing.md` · `pinterest.md` · `CLAUDE.md` · `.claude/agents/etsy-research.md` 수정
5. 게시된 핀 3개 설명 수정

**4번을 먼저 하면 문서와 실제 판매 파일이 어긋난다.**

---

## 5-4. 리스팅을 수정하면 순위가 초기화되는가

**지금은 신경 쓰지 않아도 되는 걱정이다.**

수정하면 재평가된다는 얘기가 셀러들 사이에 있고 Etsy 는 리스팅 나이와
품질 점수가 유지된다고 한다. **어느 쪽이 맞는지 확인하지 못했다.**

다만 2026-09-22 현재 우리 상태는:

```
조회 0 / 판매 0 / 리뷰 0 / 찜 0 / adhd planner 25페이지 밖
```

**초기화될 신호가 0이다.** 잃을 것이 없으므로 지금은 자유롭게 고친다.

> **반대로, 조회와 판매가 붙기 시작하면 그때부터는 조심한다.** 그 시점부터
> 리스팅 수정은 한 번에 하나씩, 그리고 바꾼 날짜를 여기 적는다.

---

## 5-2. 앱의 Shop stats 는 믿지 말 것 (숫자가 줄어든다)

2026-09-22, 발행 이틀째에 겪은 일. **같은 `Last 7 days` 기간인데 조회수가
6 에서 0 으로 줄었다.** 누적 지표는 줄어들 수 없으므로 이건 버그가 아니라
집계 방식의 문제다.

| 시각 | Views (7일) | Visits (7일) |
|---|---|---|
| 18:10 | 6 | 0 |
| 15:43 (다음날) | 6 | 0 |
| 16:51 | **0** | 0 |

**해석 (추정)** — Etsy 가 1차로 전부 센 뒤, 2차 배치에서 **본인·봇 조회를
걸러내는** 것으로 보인다. 즉 그 6 은 전부 우리 자신이 들여다본 것이었고,
외부 방문자는 0 이었다. `Visits` 가 내내 0 이었던 것과 이제 앞뒤가 맞는다.

**같은 화면에서 지표마다 갱신 시각이 다른 것**도 같은 원인이다:

```
Views    "Just now"
Visits   "5 hours ago"   ← 얘만 5시간 전
Revenue  "Just now"
```

미리 계산해둔 집계 테이블(rollup)을 읽는 구조라, 배치 주기가 달라서
일시적으로 서로 안 맞는 구간이 생긴다. 수백만 셀러 대시보드를 싸게
서빙하기 위한 트레이드오프지 허술한 게 아니다.

### 그래서 어디를 봐야 하는가

**앱 홈의 Shop stats 총계는 판단 근거로 쓰지 않는다.**

```
데스크탑 → Shop Manager → Stats → Traffic sources
```

여기서 `Etsy search` / `Direct` / `Social` 로 나뉜 것을 본다.
**`Etsy search` 가 0 이 아니게 되는 순간이 전환점**이다 — 검색 색인과
랭킹이 실제로 우리를 잡기 시작했다는 뜻이다.

총 조회수가 6 이냐 7 이냐는 아무 의미가 없다.

### 확인 주기

**하루에 여러 번 보지 않는다.** 2026-09-22 에 세 번 봤고, 볼 때마다 숫자가
달랐고, 아무것도 배우지 못했다. 표본이 한 자릿수인 구간에서 나오는 변동은
전부 노이즈다.

`forecast.md` 의 관찰 규칙대로 **일주일 뒤에 한 번**, 대조는 **2026-10-21**.

---

## 5-1. Etsy search visibility 의 빨간 배지 (무시해도 됨)

발행 직후 좌측 `Etsy search visibility` 에 빨간 `1` 이 떴다. 열어보면
**오류가 아니라 제목 제안**이다 — 리스팅 에디터에서 Dismiss 했던 그
"Suggested" 배너가 여기로 옮겨온 것뿐이다.

Etsy 제안: `ADHD Wellness Digital Planner, Undated GoodNotes Journal (PDF)`

짧고 읽기 쉽지만 **`iPad` / `Hyperlinked` / `Neurodivergent` /
`Adult ADHD Tools` 를 전부 버린다.** 특히 `iPad` 는 구매자가 가장 많이
치는 단어다.

**결정: 2026-09-21 기준 우리 제목을 유지한다.** 다만 확신은 아니다 —
최근 Etsy 는 "사람이 읽기 좋은 제목"을 밀고 있고, 어느 쪽이 실제로 더
팔리는지는 데이터 없이 알 수 없다.

**검증 방법**
1. 2~3주간 현재 제목으로 두고 `Stats → Views` 를 모은다
2. 조회가 안 나오면 그때 Etsy 제안으로 바꿔본다. 되돌릴 수 있는 실험이다
3. **한 번에 하나씩만 바꾼다.** 제목·사진·가격을 동시에 건드리면 무엇이
   원인인지 영영 알 수 없다

나머지 항목(`Your shop`, `Service standards`)은 초록불이다.

---

## 6. 발행 순서

1. **입금 계좌 + 청구 수단** ← 승인에 시간이 걸리므로 제일 먼저
2. Location
3. Shop policies (Returns: Not accepted + 위 문구)
4. Tagline
5. **리스팅 작성 → 발행** (위 2번 표 + `listing.md` 원고)
6. Marketing → Sales & discounts 에서 **40% 런칭 세일**
7. Shop announcement
8. (선택) 리스팅 비디오, Shop icon 교체
