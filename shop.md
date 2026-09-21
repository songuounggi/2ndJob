# Etsy 숍 설정 — SongAndParkStudio

숍 계정 쪽 확정값. 리스팅 원고는 `listing.md`, 상품 제작은 `CLAUDE.md`.

**이 파일은 결정을 남기는 곳이다.** 세션이 바뀌면 대화는 사라지고 이 파일만 남는다.
숍 설정을 바꾸면 여기도 같이 고칠 것.

## 계정 현황 (2026-09-21 기준)

| 항목 | 값 |
|---|---|
| 숍 이름 | `SongAndParkStudio` |
| 개설 | 2026 |
| 리스팅 | 0개 — **아직 발행 전** |
| 판매 | 0 / Admirers 0 |
| 판매자 상태 | `Private individual` (사업자 아님, 맞게 설정됨) |
| 지역 | South Korea |

## Shop Home — 지금 채울 5개

숍 홈은 **이미 리스팅을 클릭한 사람**이 보는 2차 페이지다. 첫 매출까지는
리스팅(사진·제목·태그)이 훨씬 중요하다. 아래 5개만 하고 나머지는 미룬다.

### 1. Tagline (55자 제한)

```
Undated ADHD & wellness planners for iPad
```

41자. `Undated` / `ADHD` / `planner` / `iPad` 네 키워드가 전부 들어간다.
숍 이름 밑 + 검색 결과 숍 카드에 같이 노출된다.
"Handmade with love" 류 감성 문구는 검색에 기여 0이라 쓰지 않는다.

### 2. Location

**비워두면 안 된다.** Etsy 검색에 지역 필터가 있고, 미설정이면 그 필터에서
통째로 빠진다. 디지털 상품이라 배송이 없어도 마찬가지다.

### 3. Shop policies — 이 화면에서 제일 중요

디지털 다운로드는 환불 정책을 명시하지 않으면 분쟁(케이스) 시 판매자가 불리하다.
"Try it now" 템플릿에서:

- **Returns & exchanges** → **Not accepted**
- **Cancellations** → 발송 전 취소만 (디지털은 즉시 전달이라 사실상 해당 없음)

사유 설명란:

```
Because this is an instant digital download, I can't accept returns or
exchanges. If the file doesn't open, a link doesn't work, or anything is
wrong with it, message me — I'll fix the file and send you the corrected
version at no charge.
```

### 4. Shop announcement

**리스팅 발행 후에** 건다. 지금 세일 공지를 걸어봤자 살 게 없다.
앞 ~160자만 펼쳐 보이고 나머지는 "Read more"로 접힌다.

```
Launch week: 40% off the Undated ADHD Planner. Instant download, works in
GoodNotes and Notability, no dates to expire. Questions? Just message me —
I usually reply within a day.
```

### 5. Shop icon

현재 가족 + 강아지 사진. 검색 결과에서는 **지름 약 75px 원형**으로 줄어서
얼굴 셋 + 강아지가 뭉개진다 — "무슨 가게인지"가 안 읽힌다.

- 아이콘 → 단색 배경 + 이니셜(`S&P`) 또는 단순 심볼 하나
- 판매자 얼굴 → About 섹션 사진으로 이동

신뢰감 vs 가독성 취향 문제라 강제는 아님. **미결정.**

## 미루는 것 (첫 매출 이후)

| 항목 | 왜 지금 아닌가 |
|---|---|
| About 사진 5장 / Story / Headline | 도움은 되지만 리스팅 0개면 볼 사람이 없다. 발행 후 1순위 |
| Shop members 개인 bio | 위와 동일. **"ADHD 당사자가 자기가 쓰려고 만들었다"** 는 이 카테고리에서 꽤 강한 설득 포인트라 나중에 꼭 채울 것 |
| Banner / Color theme | 리스팅이 여러 개 쌓여야 통일감이라는 게 생긴다 |
| Featured area | 최소 4개는 있어야 "골라서 강조"의 의미가 생긴다 |
| FAQ | 미리 지어내지 말 것. **같은 질문을 실제로 두 번 받으면** 그때 추가. 후보: 인쇄 가능 여부 / 안드로이드 / 링크가 안 눌림 |

## 안 하는 것

- **Add Video (최대 300MB)** — 숍 소개 영상은 이 카테고리에서 전환 기여가 거의 없다.
  영상 만들 시간이 있으면 **리스팅 쪽 동영상**에 쓸 것 —
  GoodNotes에서 탭 눌러 이동하는 화면 녹화 10초. 그건 효과가 확실하다
- **Seller details 변경** — 이미 `Private individual` 로 맞다

## 확인 필요

- [ ] Shop Home 하단 **"Add more details for buyers"** — EU 소비자 보호법(DSA)
      연락처 칸. 개인 판매자도 EU 판매 시 이름·주소·연락처를 요구받을 수 있다.
      열어서 **필수 표시(빨간 별표)가 있는지** 확인할 것. 필수면 채워야 EU 노출이 막히지 않는다

## 발행 순서

1. Location 설정
2. Shop policies (Returns: Not accepted + 위 문구)
3. Tagline
4. **리스팅 발행** ← `listing.md` 원고 사용
5. Shop announcement
6. (선택) Shop icon 교체
