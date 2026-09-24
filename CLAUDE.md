# 2ndJob — Etsy 디지털 상품 제작

Etsy에 판매할 디지털 다운로드 상품을 만드는 프로젝트.

## 현황과 문서 지도 (2026-09-21)

**세션을 방별로 나눠 쓴다.** 제품 제작 / 숍 관리 / 두 번째 상품이 각각 다른
방이다. **방이 다르면 대화가 넘어가지 않는다. 파일만 넘어간다.**
그래서 결정은 반드시 파일에 적는다 — 대화에만 남긴 결정은 다음 방에서 사라진다.

| 파일 | 담는 것 |
|---|---|
| **`CLAUDE.md`** (이 파일) | 제작 파이프라인·디자인 규칙·함정. 모든 방이 자동으로 읽는다 |
| **`RELEASE.md`** | **Etsy 에 올리거나 바꾸기 전 반드시.** 2026-09-24 사고 목록, 검수 순서(자동 + **iPad 실기기**), 스크롤·렌더 최적화, **버저닝·파일 규칙**, Etsy 교체 사실, 구매자 글·보고 규칙 |
| **`LINES.md`** | **선의 일관성 규칙과 검사 11항목. 새 상품을 만들면 0절부터 읽는다** |
| **`shop.md`** | Etsy 숍 계정 설정과 발행 절차의 확정값. **0-1절 업로드 이력표** — Etsy 에 올릴 때마다 한 줄 추가, `scripts/check_upload.py` 로 대조 |
| **`listing.md`** | 상품 1의 제목·태그·영문 설명·가격 |
| **`forecast.md`** | 예상치와 실제의 대조. **다음 대조일 2026-10-21** |
| **`product2-student.md`** | 상품 2(ADHD 학생용 플래너) 기획과 제작 배치 |
| **`pinterest.md`** | 핀터레스트 계정 설정과 핀 문구 |
| **`SETUP.md`** | 다른 PC 에서 clone 해서 빌드하는 전 과정 |

**상품 1 — 출시 완료.** ADHD & Wellness Digital Planner (v8-undated).
502페이지 / 고유 61종 / 19.6MB. $16.99, 40% 런칭 세일(~10/20).
2026-09-23 에 v8.18-undated 로 교체(노트 8장 추가, 선 규칙 정리).
2026-09-24 에 v8.20-undated 로 교체(GoodNotes 렌더링 속도, 도트 그리드). 16.5MB.
Etsy 숍 `SongAndParkStudio`, 2026-09-21 발행.

> **모든 방: 출시·교체 전에 `RELEASE.md` 를 처음부터 따른다.** 2026-09-24 에
> iPad 에서 바둑판 렌더링·도트 그리드 결함이 나왔고, 둘 다 PC 검사로는 안 보였다.
> `scripts/check_render.py` 로 확인하고, 사용자의 iPad 확인 없이 올리지 않는다.

**상품 2 — 제작 중.** ADHD 학생용 플래너(v9-student). 기획·규모·테마 확정,
1차(테마) 착수 전. 상세는 `product2-student.md`.

## 방이 여럿, 저장소는 하나 (중요)

```
저장소     1개   github.com/songuounggi/2ndJob
작업 폴더  PC 마다 1개
  회사 PC   C:\Users\ThinkBook\AiProject\2ndJob
  집 PC     C:\Users\sBrain\2ndJob
```

**Python 도 PC 마다 정해 둔다** (2026-09-24). 집 PC 에는 3.10·3.11 이 둘 다
있어 PATH 순서가 바뀌자 패키지 없는 쪽이 잡혔다(`No module named pypdfium2`).

| PC | Python | 고정 방법 |
|---|---|---|
| 집 `DESKTOP-0UH3004` | **3.10.11** (`...\Programs\Python\Python310`) | `~/.bashrc` 가 PC 이름을 보고 PATH 맨 앞에 넣는다. PowerShell 은 실행 정책상 프로필이 안 돌므로 `py -3.10` |
| 회사 | **미기록** -- 복귀하면 `python --version` 을 여기 적는다 | |

버전 차이는 산출물에 영향이 없다. PDF 는 Chrome 이 만든다. 같은 코드를
3.10/3.11 로 빌드해 1바이트 차이(생성 ID). 문제는 **패키지가 없는 쪽이
잡히는 것**뿐이다 -- 빌드 전에 `python -c "import pypdfium2, pikepdf"`.

**한 PC 안에서는 방이 나뉘어도 폴더는 하나다.** Prod 1 과 Prod 2 는 같은
파일을 본다. 방 이름 끝의 `(Home)` / `(Office)` 가 어느 PC 의 방인지 나타낸다.

**스크립트에 절대경로를 박지 않는다.** 폴더 위치가 PC 마다 다르다. 루트는
스크립트 위치에서 구한다:

```python
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
```

2026-09-24 에 `verify_v8*.py` 14개가 회사 경로를 박고 있어 집에서 안 돌았다.
새 스크립트를 만들면 이걸로 확인한다(아무것도 안 나와야 한다):

```bash
grep -rn -i "C:\\\\Users\|/c/Users" scripts
```

PC 를 옮기면 `git pull` 후 **그 PC 에서 다시 빌드**한다. `output/`·`src/` 는
git 에 없어서 따라오지 않는다. 절차는 `SETUP.md`.

**다시 뽑을 수 있는 것과 없는 것** (2026-09-24 집 PC 에서 확인)

| 결과물 | 다른 PC 에서 |
|---|---|
| `v8.18-undated` 판매본 | 현재 코드로 빌드. 19,599,557 B, 검증 13항목 통과 |
| **올린 판** `output/upload/<버전>/ADHD-...pdf` | 해당 버전 `-FINAL` 을 Etsy 이름으로 복사한 것. 빌드만 하고 끝내면 빠진다(`SETUP.md` 5단계) |
| `v8-undated` 출시본 | 커밋 `07cc59e` 로 worktree 를 떠서 빌드. **19,227,515 B 로 바이트 수까지 일치** |
| `v8.1`~`v8.17` | **재현 불가.** 이름만 다르고 지금 코드로는 전부 v8.18 이 나온다. 필요하면 각 커밋으로 빌드 |
| `v2`~`v7` 시안 | 현재 코드로 빌드됨. `v1-admin` 은 `KeyError: 'tasks'` 로 깨져 있다 |
| 리스팅 이미지 `output/listing_v815/` | **회사 PC 에만 있다.** 소스 `rail_strip_v815.png` 만드는 법이 기록에 없다 |

**회사 PC 복귀 후 할 일:** `output/listing_v815/` 와 `output/preview/rail_strip_v815.png`
를 커밋한다. 앞의 것은 `.gitignore` 에 예외를 열어 두었고, 뒤의 것은 한 장이라
`git add -f output/preview/rail_strip_v815.png` 로 넣는다. 그리고 rail_strip 을 어떻게
잘랐는지 `build_mockups.py` 에 적는다.

| | 무엇이 오가는가 |
|---|---|
| **방 ↔ 방** (같은 PC) | git 이 필요 없다. **파일을 이미 공유한다.** 한쪽이 저장하면 다른 쪽 디스크에도 그 순간 반영된다. 커밋은 기록용이다 |
| **PC ↔ PC** | git 이 유일한 통로다. 회사 PC ↔ 집 노트북 |

### git 이 막아주지 못하는 것

**두 방이 같은 파일을 동시에 고치면 나중에 저장한 쪽이 앞을 덮는다.**
git 충돌이 아니라 파일 자체가 사라지는 것이라 경고도 없다.

두 방이 공유하는 파일:

```
scripts/build_planner.py     Prod 2 가 student_pages 를 여기로 import 한다
scripts/student_pages.py
scripts/check_lines.py       선 검사기는 버전 중립이라 둘 다 쓴다
LINES.md   CLAUDE.md
```

**같은 파일을 만질 일이 생기면 먼저 다른 방에 알린다.** 한쪽이 끝낸 뒤
다른 쪽이 시작한다.

### 커밋 규칙

각 방이 **자기가 고친 파일만 이름으로 적어** 커밋한다.

```bash
git status                                   # 먼저 무엇이 바뀌었는지 본다
git add scripts/build_planner.py LINES.md    # 이름으로
git commit -m "..." && git push
```

**`git add -A` 금지.** 다른 방이 만들던 파일까지 담는다 -- 실제로 그렇게
다른 방의 작업 중인 파일이 커밋에 섞여 들어간 적이 있다.

## 판매 환경 제약 (중요)

구매자 대다수는 **iPad + GoodNotes/Notability**. 이 환경에서 동작하는 인터랙션은
**PDF 내부 링크(GoTo) 하나뿐**이다.

| 기능 | Acrobat | GoodNotes | 브라우저 |
|---|---|---|---|
| 내부 링크 | O | **O** | 대부분 O |
| Rollover(hover) | O | X | X |
| JavaScript | O | X | X |

→ hover·JS·폼 필드에 공들이지 말 것. 탭 이동 링크가 상품의 핵심 기능이다.

## 제작 파이프라인

**HTML/CSS → 헤드리스 Chrome print-to-PDF** 를 사용한다.

```bash
"/c/Program Files/Google/Chrome/Application/chrome.exe" --headless --disable-gpu \
  --no-pdf-header-footer --print-to-pdf="output/x.pdf" "file:///절대경로/x.html"
```

- `<div id="p2">` + `<a href="#p2">` 형태의 내부 앵커가 **PDF named destination +
  Link 주석으로 보존됨** (이 프로젝트에서 실측 검증 완료)
- `@page { size: 612pt 792pt; margin: 0 }` + `page-break-after` 로 페이지 분할

reportlab으로 캔버스에 직접 그리는 방식은 쓰지 않는다. 그림자 하나에 반투명
사각형 수십 겹을 쌓아야 하고, 카드 폭이 바뀔 때마다 수치를 다시 맞춰야 한다.
기존 reportlab 구현은 `scripts/build_planner_prototype.py` 에 남아 있다(참고용).

## 버전과 테마

`scripts/build_planner.py` 하나가 `THEMES` 딕셔너리로 세 시안을 뽑는다.

```bash
PLANNER_VERSION=v3-sunset python scripts/build_planner.py
```

| 버전 | 방향 |
|---|---|
| `v1-admin` | 그린 단일 액센트, Inter. 최초안 |
| `v2-warm` | 크림 배경, 4색 코딩, Nunito |
| `v3-sunset` | 피치 배경, 선셋 4색, Quicksand |
| `v5-sky` / `v6-skyblue` / `v7-bright` | 하늘 사진 + 빛 번짐. v7이 최종 톤 |
| `v8-undated` | 2026-09-21 출시본. 494p |
| `v8.18-undated` | 2026-09-23 교체본. 노트 8장 + 선 규칙 정리. 502p |
| `v8.19-undated` | GoodNotes 바둑판 렌더링 수정(`fast_paint`). 올리지 않음 |
| **`v8.20-undated`** | **판매 중 (2026-09-24 교체).** v8.19 + 도트 그리드 벡터화(`vector_dots`). 16,517,551 B |

**파일 규칙** (2026-09-24 사용자 확정):

| 위치 | 담는 것 |
|---|---|
| `output/planner_<버전>-FINAL.pdf` | 작업본. 버전을 올려 가며 고친다(v8.20 → v8.21). 지우지 않는다 |
| `output/upload/<버전>/<Etsy 이름>` | Etsy 에 올린 판. 최종 확인이 나면 **버전 이름으로 폴더를 새로 만들어** 넣는다(`upload/v8.18/`, `upload/v8.20/` …). 한 번 넣은 파일은 건드리지 않는다. 가장 새 버전 폴더가 지금 마켓 판. `upload/` 바로 아래에는 파일을 두지 않는다 |

언제 무엇을 올렸는지는 `shop.md` 0-1절. 대조는 `scripts/check_upload.py`.
**2026-09-24 에 확인 전인 v8.20 으로 마켓 판을 덮어썼다가 되돌렸다.**

v8은 테마가 아니라 **구조**가 다르다(`undated` 플래그). 달력 페이지가 위치 기반
(Month N → 1~31 → 해당 일간)으로 바뀌고 데일리 372 + 위클리 52가 붙는다.

빌드 후 **반드시** 중복 제거를 돌린다. Etsy 디지털 파일은 **20MB 상한**이다.

```bash
PLANNER_VERSION=v8-undated python scripts/build_planner.py
python scripts/dedupe_pdf.py output/planner_v8-undated.pdf output/planner_v8-undated-FINAL.pdf
```

**기존 버전은 지우지 않는다.** 각 버전은 자기 파일명으로 출력되고
`archive/`에 생성 스크립트 사본이 있다.

### 출시본을 고칠 때는 버저닝한다

출시된 상품을 수정하면 **새 버전 이름과 새 출력 파일**을 준다. 구매자가 이미
받아간 파일은 절대 덮어쓰지 않는다 — 수정이 잘못됐을 때 비교할 원본이 있어야
하고, `output/` 은 gitignore 라 git 이 되돌려주지 못한다.

```python
THEMES["v8.1-undated"] = dict(THEMES["v8-undated"])   # 구조는 그대로
```

| 버전 | 날짜 | 내용 |
|---|---|---|
| `v8-undated` | 2026-09-21 | 출시본. Etsy 에 올라간 것. 19,227,515 B |
| `v8.1-undated` | 2026-09-23 | 선 일관성 수정. 19,250,791 B |

검증 스크립트도 버전별로 둔다(`verify_v8.py` / `verify_v8_1.py`).

## 실행 환경 — 어디서 돌릴 수 있고 없는가 (2026-09-23 확인)

| 방식 | 주체 | 이 프로젝트에서 |
|---|---|---|
| **Git 연결** | 각 PC | 파일만 오간다. **대화·맥락은 안 넘어간다** |
| **Remote Control** | 회사 PC 의 Claude 앱 프로세스 | 앱 종료·재부팅이면 끊긴다. 백그라운드 에이전트는 프로세스와 함께 죽는다 |
| **Cloud** | 클라우드 컨테이너 | **빌드는 지금 불가.** 조사·기획·문서만 |

CLAUDE.md·`.claude/agents/*`·`.claude/skills/*` 는 전부 git 에 있으므로 클라우드가
clone 하면 그대로 읽는다. **따로 옮길 것은 없다.** 막는 건 다음 둘이다:

1. **Chrome 경로가 Windows 로 박혀 있다** — 6개 스크립트 전부
   `C:\Program Files\Google\Chrome\...`. 리눅스엔 없고, 파이프라인 자체가
   헤드리스 Chrome 이라 PDF 를 한 장도 못 뽑는다
2. **결과물을 꺼낼 길이 없다** — `output/` 이 gitignore 라 19MB PDF 는 커밋이
   안 되고 컨테이너 안에 갇힌다

고치려면 `CHROME` 을 환경변수 + 탐색으로 바꾸고 결과물을 릴리스로 빼면 된다.
다만 19MB PDF 검수를 모바일로 하는 건 현실적이지 않다.

## 공통 디자인 규칙

- **섹션 헤더** = 폭 2.6pt 세로 바 + 볼드 라벨
- **면을 통째로 원색으로 칠하지 않는다.** 색은 점·세로바·칩에만
- 입력 영역은 회색 필드 박스, 필기 영역은 얇은 괘선
- **점선 양 끝 흐림 = "셀페이드"** (`/cellfade`, `scripts/dashfade.py`). 칸마다,
  그라데이션 없이. 새로 짜지 말고 부른다
- **점지(도트 그리드) = 상품 1 `build_planner.dot_svg()`** (벡터 원, 14pt). 반복
  배경 금지. 검수는 check_render A-3 + 점 간격 측정(`verify_student.dot_pitch`)
- **선에 관한 것은 전부 `LINES.md` 에 있다.** 괘선 높이·줄 수·섹션
  높이 고정·표 마감선·검사 11항목. 페이지를 새로 만들기 전에 읽는다
- 카테고리 색은 **4개가 상한**. 넘으면 오히려 기억을 방해한다(조사 근거)
- 테두리 선 없이 그림자만으로 층을 표현한다

### 그림자 (이 프로젝트에서 가장 예민한 항목)

요구 조건 세 가지. 네 번 반려된 이력이 있으니 건드릴 때 전부 재확인할 것.

1. **방향성** — 위는 거의 없고, 좌우 약간, 하단이 가장 깊고 넓게
2. **하단 중앙 집중** — 좌우 끝에서 옅고 가운데로 갈수록 깊게
3. **한 줄** — 밝아졌다 다시 어두워지는 두 번째 띠가 없을 것

4. **농도는 얕게** — 중앙 최대 깊이가 배경 대비 약 22단계. 이보다 진하면
   "너무 깊다"는 피드백을 받는다

구현은 `box-shadow` 하나로는 불가능하다. 두 층으로 나눈다:

- `box-shadow`는 **오프셋 없이 좁게**(`0 0 2pt / 0 0 6pt`) — 경계 정의용
- 실제 드롭 섀도는 `.card::after`의 타원 그라데이션
  (`top:100%`, `height:13pt`, `radial-gradient(ellipse 62% 100% at 50% 0%,
  rgba(0,0,0,.07), transparent 72%)`)

**`top`은 반드시 정확히 `100%`.** 단 1pt라도 내리면 카드 경계에 이음매가 생기고,
서브픽셀 반올림 때문에 **일부 카드에서만** 드러난다(인덱스 페이지에서 Focus
카드만 밝은 줄이 보이고 이웃 카드는 멀쩡했던 사례). 100%에서는 모든 카드가
동일하게 측정된다.

`box-shadow`에 y오프셋을 주는 것도 금지 — 두 그림자의 최대 농도 지점이 달라져
사이에 골이 생기고, 그게 "두 줄"로 보인다.

### 그림자 검사법 (판정식을 두 번 틀렸으니 주의)

값이 **커지는 것은 밝아지는 것**이고 정상적인 감쇠다. 이음매는 **비단조** 패턴,
즉 어두워졌다 밝아졌다 다시 어두워지는 구간이다. 단조 증가를 결함으로 오판한
적이 두 번 있다.

```python
seam = any(p[i] > p[i-1]+1 and any(p[j] < p[i]-1 for j in range(i+1, len(p)))
           for i in range(1, 6))
```

**한 카드만 재고 끝내지 말 것.** 페이지·카드·x좌표를 여러 곳 찍어야 한다.
카드 폭과 위치에 따라 다르게 나타난다.

`radial-gradient`에 **`ellipse` 키워드를 빠뜨리면** Chrome이 파싱을 거부하고
배경을 통째로 버린다. 조용히 실패하므로 눈치채기 어렵다.

## 500페이지 규모에서 터진 것들 (v8에서 전부 겪음)

**1. `box-shadow`는 요소마다 이미지로 래스터화된다.** 60페이지에서는 안 보이다가
494페이지에서 56MB가 됐다(전체 86MB 중). 카드 그림자는 `box-shadow` 대신
**0.4pt 헤어라인 + `::after` 타원 그라데이션**으로 낸다. 후자는 벡터 패턴으로 남는다.

**2. CSS 그라데이션 번짐은 렌더링을 34배 느리게 만든다.** 9겹 radial-gradient를
배경에 깔면 페이지당 **2,973ms**가 걸린다(워시 없으면 88ms). 뷰어에서 스크롤이
멈춘 것처럼 보인다. 번짐은 **PNG 한 장을 전 페이지가 공유**하는 방식으로 쓴다
(49ms/page). PNG가 용량도 더 작다 — 공유 이미지라 494페이지가 같은 걸 참조한다.

**3. 목적지 없는 `<a href="#x">`는 Chrome이 조용히 버린다.** 링크는 사라지고
글자만 남아서, 탭이나 목록 항목이 **눌러도 아무 일이 안 일어나는 상태**가 된다.
구조를 바꾸면 반드시 이걸 검사한다:

```python
hrefs = set(re.findall(r'href="#([^"]+)"', html))
dead  = hrefs - set(k.lstrip('/') for k in PdfReader(pdf).named_destinations)
```

**4. 링크 검사는 "있는 링크가 유효한가"로 끝내지 마라.** 있어야 할 링크가
빠졌는지도 봐야 한다. v8에서 DAY 탭이 494페이지 전부에서 죽어 있었는데
"링크 493개 전부 정상"으로 통과했었다.

**5. 탭 하이라이트도 검사 대상이다.** 링크가 전부 살아 있어도 현재 위치
표시가 꺼져 있으면 "앱에서 튕겨나온" 느낌을 준다. `rail_key()`가 모든
페이지를 탭 하나에 매핑해야 한다 — 반복 페이지(`m*`/`w*`/`d*`)뿐 아니라
`GROUPS` 하위 48페이지도 포함이다(Mind map에서 FOCUS가 꺼져 있던 사례).
커버 한 장만 예외여야 한다:

```python
for m in re.finditer(r'<section class="page" id="([^"]+)".*?</nav>', html, re.S):
    assert len(re.findall(r'<a class="on"', m.group(0))) == 1 or m.group(1) == "cover"
```

**6. GoodNotes 에서 페이지가 바둑판처럼 늦게 채워진다 — `v8.19-undated` 에서 수정,
iPad 확인 대기 (2026-09-24).** 테마 플래그 `fast_paint`. v8.19: 502p, 16,091,246 B
(v8.18 보다 3.5MB 작다), 198 → 68 ms/page, 502장 픽셀 차이 평균 0.086 / 최대 10
(노트 페이지 맨 아래 탭 그림자 한 줄). `verify_v8_19.py` 가 "셰이딩·소프트마스크
있는 페이지 0" 을 잰다 — v8.18 에 돌리면 501장 FAIL. 상품 2 는 아직 안 켰다.

**7. GoodNotes 가 CSS 도트 그리드를 4배 넓게, 흐릿한 네모로 그린다 — `v8.20-undated`
에서 수정 (2026-09-24).** v8.19 를 iPad 에서 보던 사용자가 찾았다(v8.18 부터 있던
결함). `.dots` 의 radial-gradient 타일을 Chrome 이 **이미지를 담은 타일 패턴**으로
넣고, pdfium 은 14pt 로 그리지만 GoodNotes 는 약 58pt 간격으로 그렸다. 테마 플래그
`vector_dots` 가 `dot_svg()` 로 진짜 원을 그린다 — 위치·간격 동일, 벡터라 더
또렷하다. `verify_v8_20.py` 의 "이미지 타일 패턴 페이지 0" 이 v8.19 에서 3장 FAIL.
**교훈: pdfium 에서 맞게 보여도 GoodNotes 에서 다를 수 있다.** 새로운 CSS 효과
(그라데이션·패턴·반복 배경)는 PDF 에 무엇으로 들어갔는지 pikepdf 로 확인한다.
상품 2 에 `.dots` 가 있으면 같은 결함이 있다.
사용자가 iPad 에서 판매본 v8.18 을 넘길 때마다 발견. 원인은 전 페이지에 깔린
두 효과다: 카드·탭 `::after` 그라데이션 그림자(함수형 shading + 소프트마스크,
페이지당 5~6개)와 `.bg-bloom` 의 opacity .55 반투명 합성. 모양을 유지한 채
**그림자를 공유 PNG 로, bloom 을 배경색에 미리 합성한 불투명 이미지로** 바꾸면
248 → 63 ms/page, 픽셀 차이 평균 0.08 단계. 측정은 `scripts/perf_probe.py`.
**남은 일:** ① iPad 에서 `output/ipad-test/` A/B 5장 비교 (PC 수치는 pdfium 이라
GoodNotes 와 다를 수 있다) ② Prod 2 가 `build_planner.py` 작업을 끝낸 뒤
`v8.19-undated` 로 반영. 상품 2 도 같은 그림자·bloom 을 쓴다.

## 빌드가 조용히 실패하는 두 가지 (둘 다 겪음)

**1. 출력 PDF가 잠겨 있으면 Chrome은 종료 코드 0으로 아무것도 쓰지 않는다.**
한 시간 동안 낡은 PDF를 측정하며 "수정 완료"라고 보고한 적이 있다. 그래서
`to_pdf()`는 빌드 후 mtime이 갱신됐는지 확인하고 아니면 예외를 던진다. 이
가드를 절대 제거하지 말 것.

**2. 잠그는 것은 둘이다 — `pypdfium2`, 그리고 Acrobat.**
2026-09-23 에 사용자가 Acrobat 으로 열어둔 `v8.1-FINAL` 을 덮어쓰려다
`PermissionError: [Errno 13]` 이 났다. Chrome 내장 뷰어와 앱 미리보기는
잠그지 않으므로 **검수는 그쪽으로 연다**(사용자와 합의됨). 재빌드가
막히면 먼저 무엇이 그 파일을 열고 있는지 묻는다.

코드 쪽 주범은 `pypdfium2` 다. `PdfDocument(path)`는 파일
핸들을 유지한다. 같은 프로세스에서 측정 후 재빌드하면 반드시 막힌다. 측정은
바이트로 읽어서 열 것:

```python
with open(path, 'rb') as fh:
    doc = pdfium.PdfDocument(fh.read())
...
doc.close()
```

## 작업 규칙

### 고친 것에는 **그 자리에서 검사를 붙인다**

새로 고친 것은 정의상 검사가 없는 것이다. 수정만 하고 넘어가면 다음에
같은 게 돌아와도 자동으로 안 걸리고, 사용자가 또 눈으로 찾아야 한다.
2026-09-23 에 지적받았다 -- 그때까지 검사 항목은 전부 **사용자가 찾은 뒤에**
추가됐다.

**수정 한 건당 검사 한 줄.** 순서는 이렇다:

1. 고친다
2. `scripts/check_lines.py` 의 `PROBE` 에 그 결함을 재는 항목을 넣는다
3. **고치기 전 버전에 그 검사를 돌려 실제로 걸리는지 본다.** 안 걸리면
   엉뚱한 곳을 재고 있는 것이다 -- 줄 부족 검사를 처음 짰을 때 v8.6 이
   통과해버렸다. 구멍은 카드 안이 아니라 행과 그 아래 카드 **사이**에
   있었다
4. 고친 버전에서 통과하는지 본다

검사할 수 없는 것이면(주관적 판단 등) 그렇다고 보고에 적는다.

### 작업이 끝나면 **무엇을 어디서 고쳤는지 목록으로** 보고한다

사용자는 눈으로 검수한다. 페이지 번호가 없으면 502장에서 찾아야 한다.
"고쳤습니다"로 끝내지 말고 반드시 아래를 적는다:

| 항목 | 내용 |
|---|---|
| **파일** | 검수할 PDF 의 정확한 이름 (버전이 여럿이라 헷갈린다) |
| **페이지** | 바뀐 곳의 **번호와 페이지 이름**. 우선순위 순으로 |
| **볼 것** | 각 페이지에서 무엇이 어떻게 달라졌는지 한 줄 |
| **범위** | 그 페이지만인지, 전 페이지에 걸린 변경인지 |

전 페이지에 걸린 변경이면 **표본 페이지 번호**를 뽑아준다 -- 고유 템플릿
몇 장, 반복 페이지(데일리·위클리·먼슬리) 몇 장.

페이지 번호는 짐작하지 말고 뽑는다:

```python
ids = re.findall(r'<section class="page" id="([^"]+)"', html)
ids.index("vision") + 1        # -> 9
```


**만든 PDF는 반드시 렌더해서 눈으로 확인한 뒤 전달한다.** 확인 없이 넘겨서
텍스트 잘림·박스 겹침·행 높이 붕괴를 놓친 적이 있다.

**색을 글자에 쓸 때는 대비를 계산한다.** 장식용 파스텔을 글자색으로 쓰면
2.2~3.1:1로 기준 미달이다. 각 테마의 `sections`는
`(장식용 파스텔, 틴트, 글자용 진한 톤)` 3원소이며, 색이 들어간 **단어**는
반드시 세 번째 값을 쓴다.

```bash
python -c "
import pypdfium2 as pdfium
pdf = pdfium.PdfDocument('output/x.pdf')
for i in range(len(pdf)):
    pdf[i].render(scale=2).to_pil().save(f'output/preview/page{i+1}.png')
"
```

그림자 농도·간격처럼 눈으로 애매한 속성은 **픽셀값을 위치별로 측정해서**
의도한 기울기가 나오는지 확인한다(`.convert('L')` 후 `getpixel`).

링크 검증:

```bash
python -c "
from pypdf import PdfReader
r = PdfReader('output/x.pdf'); nd = r.named_destinations
idx = {id(p.indirect_reference.get_object()): n+1 for n,p in enumerate(r.pages)}
for i,pg in enumerate(r.pages):
    print(i+1, [f\"{a.get_object()['/Dest']}->p{idx[id(nd[a.get_object()['/Dest']]['/Page'].get_object())]}\" for a in pg['/Annots']])
"
```

## 디렉토리

```
scripts/   생성 스크립트
output/    완성 PDF
output/preview/   검수용 페이지 렌더 PNG
```

## 참고

- `design` 스킬(Claude Design 캔버스)은 `disable-model-invocation` 이라 Claude가
  호출할 수 없다. 사용자가 `/design` 을 직접 입력해야 열린다. 2026-09-17 기준
  이 세션에서는 Artifact 도구에 `quickstart`/`type_url` 파라미터가 없어 생성 실패
- 폰트는 아직 미해결 과제. 현재 기본 산세리프. 무료 상업용 폰트(Pretendard,
  Inter 등) 적용이 다음 개선 항목
