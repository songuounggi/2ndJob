# 상품 4 디자인 인수인계서 v0.3 — 2쪽 순서도 "How it flows" **구조를 바꿔** 다시 그리기

**보내는 쪽:** Claude Code (`Prod 4. The ADHD Home Reset` 방, 2026-10-02) → **받는 쪽:** claude.ai/design
**같이 올릴 파일:** `output/prod4/handoff/flow-v0.3/` (아래 7절) -- 묶음 `flow-v0.3.zip`

> **v0.3 이 v0.2 와 다른 점 (정정):** v0.2 는 "내용(상자 9개·화살표·문구)은 그대로 두고 **모양만**" 이었다. 그 내용이 틀렸다.
> 질문 상자와 답 상자가 같은 쪽으로 가는 쌍이 셋(Check your battery·Energy menu → 6쪽, All too much?·Rescue mode → 94쪽,
> Done enough·Wins log → 103쪽)이고, 둘 중 하나를 고르는 "기운으로 / 방으로"를 한 줄로 이어 순서도가 성립하지 않았다
> (사용자 10-02, 7단계 iPad 확인 뒤). 이번에는 **구조가 바뀐다.** 모양 언어(노선도)는 지금 2쪽(v1.0 시안) 그대로.
> v0.2 의 상자 9개 표·흐름 그림은 쓰지 않는다(git 기록에만 남김).

---

## 1. 한 줄 요청

**2쪽 순서도를 아래 구조로 다시 그려 주세요.** 선 그림 `flow_wireframe.png`(.svg) 가 구조의 정답입니다.
모양은 지금 2쪽(`02_current_page2_v0.12.png`, 여러분이 만든 v1.0 노선도)의 언어 -- 굵은 색 선, 둥근 꺾임, 흰 테 점,
굵은 제목 + 섹션 진한색 한 줄 -- 를 그대로 쓰고, **배치만 새 구조로** 잡아 주세요.

## 2. 구조 (바꾸면 안 되는 것)

```
Open the planner → 3쪽
      │
  ◇ How's today?
   ├─ Doable ──── ◇ How to pick?
   │                ├─ By energy & time → [Energy menu → 6쪽]   (왼쪽으로 갈라짐)
   │                └─ By room          → [House map → 4쪽]     (오른쪽으로 갈라짐)
   │                      (두 갈래가 다시 합쳐짐)
   │              [Ten minutes · Stop at Done enough]  (링크 없음)
   └─ All too much ── [Rescue mode → 94쪽]
                        (두 갈래가 합쳐짐)
                  [Wins log → 103쪽]

  따로 한 줄: [Once a week → 40쪽]
```

**규칙 세 개 -- 이것 때문에 다시 그린다**

1. **질문(◇)에서만 길이 갈라진다.** 갈래는 둘 중 하나다. "How to pick?" 의 두 갈래(Energy menu / House map)는
   **좌우로 벌어져야** 두 갈래로 읽힌다(사용자 10-02: "Energy menu 도 좌측으로 튀어나와야 두 갈래라고 인식")
2. **누르는 상자 하나 = 쪽 하나.** 같은 쪽으로 가는 상자가 둘이면 안 된다. 링크 상자는 아래 6개뿐
3. **질문 · 갈래 이름 · Ten minutes 는 링크가 아니다** -- → 를 붙이지 않는다(README §7-2 "링크가 걸린 곳은 →")

## 3. 문구 (확정 -- 바꾸려면 따로 목록으로, 사용자 확인 뒤 원고 `scripts/p4/p4_content.py` `FLOW` 에 반영)

| 무엇 | 제목 | 한 줄 | 누르면 | 섹션 색 |
|---|---|---|---|---|
| 시작 (링크) | Open the planner | — | 3쪽 Start here | 중립 |
| 질문 1 | How's today? | — | 링크 없음 | 중립 |
| 갈래 | Doable / All too much | — | 링크 없음 | 민트 / 아쿠아 |
| 질문 2 | How to pick? | — | 링크 없음 | 민트 |
| 링크 | Energy menu | By battery and minutes | 6쪽 | A 민트 |
| 링크 | House map | By room | 4쪽 | B 레몬 |
| 할 일 (링크 없음) | Ten minutes | Stop at Done enough | — | B 레몬 |
| 링크 | Rescue mode | Five steps, then stop · (작게) Or tap SOS on any page | 94쪽 | D 아쿠아 |
| 링크 | Wins log | It counts | 103쪽 | D 아쿠아 |
| 링크 | Once a week | Reset week: one room a day | 40쪽 | C 라벤더 |

페이지 제목 `How it flows` · 부제 `Start at the top. Tap a page name to go there.`
"How to pick?" 의 갈래 이름(By energy & time / By room)은 선 그림에만 적었다 -- 상자 한 줄(By battery and minutes / By room)과
겹치면 빼도 된다.

## 4. 지키는 틀 (지금 2쪽과 같은 것)

- 왼쪽 탭 레일 · 섹션 표시 `Home` · 제목 · 부제 · 오른쪽 위 `SOS` 칩 위치 그대로. 본문은 x 84 ~ 584pt, 부제 아래부터 쪽 아래 여백까지
- 섹션 색 4개(README §4)만. 색 글자는 진한 톤(대비 4.5:1)
- **iPad GoodNotes 안전** (README §5와 같음): CSS 그라데이션 · 반투명 · box-shadow · blur · 반복 배경 금지.
  그림자는 **배경 JPG 에 굽는다**(`bake()`). 링크 영역은 사각형. 글자는 실제 텍스트
- **◇ 는 새 도형이다.** 그림자를 주려면 배경에 구워야 한다 -- Claude Code 쪽 굽기 코드(`scripts/p4/bake_bg_p4.py`)는
  지금 **둥근 사각형 · 원 · 45도 돌린 정사각형(◇)** 을 구울 수 있다. 다른 도형이면 그림자 없이 평면으로 두거나 굽는 법을 같이 주세요
- 점 그림자는 시안 2쪽 배경을 픽셀로 잰 값 = `rgba(40,60,55,0.10)` · blur 8 · 아래로 2 (카드 그림자와 다르다, 10-02 실측)

## 5. 돌려받고 싶은 것

1. **2쪽 한 장** -- v1.0 과 같은 형식(`pages_turn25.html` 의 2쪽 덩어리 + 2쪽 배경 JPG 또는 굽는 값). 다른 37쪽은 그대로
2. 링크 상자 6개의 위치(링크 영역)를 알 수 있을 것
3. 문구를 바꾸고 싶으면 따로 목록으로

## 6. 받은 뒤 Claude Code 가 하는 일

`scripts/p4/build_v2_p4.py` 2쪽에 옮기고 새 버전으로 빌드 → 검사(링크 6개 = 쪽 6개, **같은 쪽으로 가는 상자 금지**, 글자 넘침·겹침,
흑백판, GoodNotes 위험 효과, 속도) → 사용자에게 보여 준다.

## 7. 같이 올릴 파일 (`output/prod4/handoff/flow-v0.3/`)

| 파일 | 무엇 |
|---|---|
| `flow_wireframe.png` / `.svg` | **구조의 정답** -- 빈 페이지에 선으로만. 실선 상자 = 링크, 점선 = 링크 없음, ◇ = 질문 |
| `02_current_page2_v0.12.png` | **지금 2쪽** -- 모양 언어(선·점·글씨)는 이것을 따른다. 구조는 틀렸다 |
| `00_HANDOFF.md` | 이 문서 |
