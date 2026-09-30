# 상품 4 디자인 인수인계서 — 2쪽 순서도 "How it flows" 다시 그리기

**보내는 쪽:** Claude Code (`Prod 4. Something` 방, 2026-09-30) → **받는 쪽:** claude.ai/design
**같이 올릴 그림:** `output/prod4/handoff/flow-v0.1/` 의 7장 (아래 6절 목록)

---

## 1. 한 줄 요청

**디지털 플래너 2쪽의 순서도를 다시 디자인해 주세요.** 지금 판(그림 01)은 사용자가 "너무 촌스럽다"고 했습니다.
내용(상자 9개·화살표·문구)은 그대로 두고 **모양만** 새로 잡습니다. 플래너의 나머지 106쪽 모양(그림 02~06)과
한 식구로 보여야 합니다.

## 2. 이 상품이 무엇인가

| 항목 | 값 |
|---|---|
| 이름 | **The ADHD Home Reset** — *clean by energy, not by schedule* |
| 무엇 | ADHD 성인용 청소·집안 루틴 **디지털 플래너**(하이퍼링크 PDF). Etsy 판매, $8.99 |
| 구매자 | 미국·영국의 ADHD 성인. **iPad + GoodNotes** 에서 손글씨로 쓴다 |
| 쪽 수 | 107쪽, 날짜 없음(undated) |
| 판형 | US Letter 세로 **612 × 792 pt** |
| 핵심 기능 | PDF 내부 링크 -- 상자·탭을 누르면 그 페이지로 간다. **GoodNotes 에서 되는 상호작용은 이것 하나뿐** |

## 3. 2쪽의 역할과 내용 (바꾸지 않는 것)

**표지 바로 다음 쪽.** 사용설명서를 읽기 전에 "이 플래너를 어떻게 쓰는지"를 한눈에 보여 주고,
**상자마다 그 페이지로 가는 링크**라서 출발점 역할도 한다.

### 상자 9개 (문구는 확정 -- 바꾸려면 사용자 확인이 필요)

| # | 제목 | 한 줄 | 누르면 가는 곳 | 섹션 색 |
|---|---|---|---|---|
| 1 | Open the planner | — | 3쪽 Start here | 없음(중립) |
| 2 | Check your battery | Low, medium, or full | 6쪽 Energy menu | A 민트 |
| 3 | All too much? | Tap SOS on any page | 91쪽 Rescue mode | D 아쿠아 |
| 4 | Energy menu | Pick by minutes | 6쪽 Energy menu | A 민트 |
| 5 | Rescue mode | Five steps, then stop | 91쪽 Rescue mode | D 아쿠아 |
| 6 | Room card | Ten-minute reset | 4쪽 House map | B 레몬 |
| 7 | Done enough | Stop there | 4쪽 House map | B 레몬 |
| 8 | Wins log | It counts | 100쪽 Wins log | D 아쿠아 |
| 9 | Once a week | Reset week: one room a day | 37쪽 Weeks | C 라벤더 |

페이지 제목 `How it flows`, 부제 `Tap any box to go there.`

### 흐름 (화살표)

```
Open the planner ─┬─> Check your battery ─> Energy menu ─> Room card ─> Done enough ─┐
                  │                                                                   ├─> Wins log
                  └─> All too much? ─────> Rescue mode ───────────────────────────────┘
Once a week (별도 줄): Reset week -- 한 주에 방 하나씩
```

두 갈래(평소 / 벅찰 때)가 **Wins log 에서 만난다**는 게 이 상품의 메시지입니다. 청소를 조금만 해도, 구조만 해도
"했다"로 센다. 이 점이 보이면 좋겠습니다.

## 4. 지켜야 할 틀 (나머지 106쪽과 같은 것)

그림 02~06 을 보면 됩니다. 수치로 적으면 이렇습니다.

| 요소 | 값 |
|---|---|
| 글꼴 | **Nunito** (400·600·700·800). 제목 23pt/800, 부제 9.5pt, 본문 9~11pt. 최소 7pt |
| 왼쪽 탭 레일 | 폭 58pt, 탭 6개(HOME·ENERGY·ROOMS·ROUTINES·WEEKS·TOOLS). 2쪽은 HOME 이 켜져 있다 |
| 본문 영역 | x = 84pt ~ 584pt (**폭 500pt**), 위쪽에 섹션 표시·제목·부제, 오른쪽 위 `SOS` 칩 |
| 카드 | 흰색, 모서리 14pt, 0.4pt 헤어라인. 아래 그림자는 **이미지 한 장**(CSS 그림자 아님) |
| 종이 | 2쪽은 HOME 섹션 = 종이 `#F5F8F5` + 위쪽에 민트·하늘 번짐(미리 합성한 이미지) |
| 섹션 색 (탭·강조) | A 민트 `#7FB59C`(글자용 `#537364`) · B 레몬 `#E2BE3E`(`#7D6A28`) · C 라벤더 `#A393D8`(`#6E6490`) · D 아쿠아 `#2FB3C6`(`#237581`) |
| 글자색 | 본문 `#34403A`, 흐린 글자 `#5F6B65`·`#78837D`. **색이 들어간 글자는 반드시 "글자용" 진한 톤** (대비 4.5:1 이상) |
| 색 개수 | 한 권에 강조색 **4개가 상한**(조사 근거). 새 색을 더하지 않는다 |

## 5. 반드시 피해야 할 것 — iPad GoodNotes 에서 깨지는 것 (실제로 겪었다)

상품 1 에서 **PC 에서는 멀쩡한데 iPad 에서만** 페이지가 바둑판처럼 늦게 그려지고, 점무늬가 4배로 벌어졌습니다.
원인은 아래 효과들이었습니다. 이 페이지에도 **쓰지 않습니다.**

| 금지 | 대신 |
|---|---|
| CSS 그라데이션(linear/radial) | 단색 면. 번짐이 꼭 필요하면 **미리 합성한 이미지 한 장** |
| 반투명(opacity < 1, rgba 면 겹치기) | 불투명 단색(배경색에 미리 섞은 색) |
| box-shadow, blur, filter | 0.4pt 헤어라인 + 그림자 이미지 |
| 반복 배경 무늬(background-repeat) | 벡터 도형(SVG 원·선) |
| 눌러야 하는 영역이 사각형이 아닌 것 | **상자마다 사각형 링크 영역** (PDF 링크는 사각형이다) |

선·화살표·도형은 **SVG 벡터**면 안전합니다. 글자는 모두 실제 텍스트여야 합니다(이미지 글자 금지 -- 검색·접근성).

## 6. 같이 올릴 그림 (`output/prod4/handoff/flow-v0.1/`)

| 파일 | 무엇 |
|---|---|
| `01_current_flow_page2.png` | **지금 2쪽** -- "촌스럽다"고 한 판. 무엇이 아쉬운지 보는 기준 |
| `02_start_here_page3.png` | 바로 다음 쪽(글로 된 사용법). 2쪽과 역할이 이어진다 |
| `03_energy_menu_page6.png` | 같은 상품의 격자형 페이지 |
| `04_kitchen_card_page11.png` | 방 카드 -- 카드·번호·체크 상자 모양 |
| `05_rescue_mode_page91.png` | 번호 달린 단계 카드 -- 순서도 상자와 가장 가까운 모양 |
| `06_cover_page1.png` | 표지 |
| `07_section_colors.png` | 섹션마다 색이 바뀌는 방식(아래 줄이 확정안) |

## 7. 돌려받고 싶은 것

1. **2쪽 시안 1~3개** -- 612 × 792pt 한 장. 가능하면 HTML/CSS(+인라인 SVG)로. 이미지만이면 상자 좌표·크기·색 값을 같이
2. 상자 9개가 각각 어디 있는지(링크 영역) 알 수 있을 것
3. 문구를 바꾸고 싶으면 **따로 목록으로** -- 사용자 확인 뒤 원고 파일(`scripts/p4/p4_content.py` `FLOW`)에 반영한다

받으면 Claude Code 가 `scripts/p4/build_p4.py` 의 `p_flow()` 로 옮기고, 검사 세 개(`check_p4` 링크·배치,
`check_lines` 선, `check_render` GoodNotes 위험)를 다시 돌린 뒤 사용자에게 보여 준다.

## 8. 참고 — 지금 판을 만든 방식 (그대로 따를 필요는 없음)

상자는 절대 위치 `<a>` 카드(왼쪽 3pt 색 띠 = 가는 곳의 섹션 색), 화살표는 인라인 SVG 꺾은선 + 삼각 화살촉.
좌표계는 본문 영역 500 × 560pt. 코드: `scripts/p4/build_p4.py` `FLOW_BOX` · `FLOW_ARROWS` · `p_flow()`.
