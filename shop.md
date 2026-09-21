# Etsy 발행 체크리스트 — SongAndParkStudio

숍 계정 + 리스팅 입력값의 **확정본**. 리스팅 원고(제목/태그/설명 본문)는
`listing.md`, 상품 제작 규칙은 `CLAUDE.md`.

**이 파일은 결정을 남기는 곳이다.** 세션이 바뀌면 대화는 사라지고 파일만 남는다.
설정을 바꾸면 여기도 같이 고칠 것.

최종 점검: 2026-09-21

---

## 0. 현황

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

- [ ] **입금 계좌 (Etsy Payments)** — Settings → Finances → Payment settings.
      한국 은행 계좌 + 본인 명의. 신분증 확인을 요구할 수 있어 **시간이 가장
      오래 걸리는 항목**이다. 제일 먼저 시작할 것
- [ ] **청구 수단** — Settings → Finances → Billing. 리스팅 수수료·거래
      수수료가 여기서 빠진다. 입금 계좌와 별개다
- [ ] **Location** — Shop Home에서 설정. 검색 지역 필터에 쓰이고,
      **비워두면 그 필터에서 통째로 빠진다.** 디지털이라 배송이 없어도 동일
- [ ] **Shop policies** — 아래 2-C 참조. 디지털은 정책이 분쟁의 유일한 근거다

**수수료 감안** — 리스팅 등록 $0.20(4개월), 판매 시 거래 수수료 6.5% +
결제 처리 수수료. $10.19에 팔면 손에 쥐는 건 대략 $8~9 선이다.

---

## 2. 리스팅 입력 항목 — 칸별로 넣을 값

Etsy 리스팅 폼 순서대로. **★ = 필수**

### A. 사진 / 비디오

| 칸 | 값 |
|---|---|
| ★ **Photos** (최대 10장) | `output/listing/` 의 9장을 **01→09 번호 순서대로** 업로드 |
| **Video** (선택, 5~15초) | **만들 것을 권함.** GoodNotes에서 옆 탭을 눌러 페이지가 이동하는 화면 녹화. 이 상품의 핵심 기능이 링크 이동인데 정지 이미지로는 전달이 안 된다 |

첫 번째 사진(`01_hero.png`)이 검색 결과에 나오는 썸네일이다. 여기서 클릭이
갈리므로 다른 건 미뤄도 이건 미루지 말 것.

### B. 기본 정보

| 칸 | 값 | 비고 |
|---|---|---|
| ★ **Title** | `listing.md` 제목 그대로 (124자) | 140자 상한. 예전 144자 안은 잘렸다 |
| ★ **Who made it** | `I did` | |
| ★ **What is it** | `A finished product` | |
| ★ **When did you make it** | `2020 – 2026` (최근 제작) | `Made to order` 아님 — 즉시 다운로드다 |
| ★ **Category** | 검색창에 `planner` 입력 → Paper & Party Supplies 하위의 Calendars & Planners 계열 선택 | 경로명은 Etsy가 수시로 바꾸므로 화면에서 확인할 것 |
| ★ **Type** | **`Digital`** | **가장 중요.** Physical로 두면 배송 설정을 요구하고 파일 업로드 칸이 안 나온다 |
| **Renewal** | `Automatic` | 4개월마다 $0.20 자동 갱신 |
| **Production partners** | 없음 | |
| **Section** | `ADHD Planners` 새로 만들기 | 상품이 늘 때를 대비 |

### C. 설명 / 태그

| 칸 | 값 |
|---|---|
| ★ **Description** | `listing.md` 상품 설명 블록 전체 |
| **Tags** (13개, 각 20자) | `listing.md` 태그 13개 그대로 |
| **Materials** | 비워도 됨 |

### D. 가격 / 재고

| 칸 | 값 |
|---|---|
| ★ **Price** | `16.99` (USD) |
| **Quantity** | 디지털은 무제한이라 신경 쓸 필요 없음 |
| **SKU** | 비워도 됨 |
| **Personalization** | **Off** |

런칭 세일 40%는 리스팅 폼이 아니라 **Marketing → Sales & discounts** 에서
따로 건다. 발행 후에 설정할 것. 정가를 걸고 할인 배지를 띄우는 게
처음부터 $10에 거는 것보다 유리하다.

### E. 디지털 파일 ★

| 칸 | 값 |
|---|---|
| **Upload** | `output/planner_v8-undated-FINAL.pdf` |

> ⚠️ **파일당 20MB 상한. 현재 19,227,515 bytes = 19.2MB로 여유가 약 4%뿐이다.**
> 재빌드 후에는 반드시 바이트 수를 다시 확인할 것. 페이지를 더 넣을 여유는 없다.
> (MiB로 재면 18.3이라 안전해 보이지만 **Etsy 기준은 그 쪽이 아니라고 보고 움직인다.**)

**배송(Shipping) 칸은 나오지 않는다.** 나온다면 Type이 Digital이 아니라는 뜻이다.

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

## 6. 발행 순서

1. **입금 계좌 + 청구 수단** ← 승인에 시간이 걸리므로 제일 먼저
2. Location
3. Shop policies (Returns: Not accepted + 위 문구)
4. Tagline
5. **리스팅 작성 → 발행** (위 2번 표 + `listing.md` 원고)
6. Marketing → Sales & discounts 에서 **40% 런칭 세일**
7. Shop announcement
8. (선택) 리스팅 비디오, Shop icon 교체
