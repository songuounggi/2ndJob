# 2ndJob — Etsy 디지털 상품 제작

Etsy에 판매할 디지털 다운로드 상품을 만드는 프로젝트. 현재 작업 중인 상품은
ADHD/웰니스 특화 디지털 플래너.

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
| **`v8-undated`** | **판매용.** v7 톤 + 완전 undated + 반복 세트 494p |

v8은 테마가 아니라 **구조**가 다르다(`undated` 플래그). 달력 페이지가 위치 기반
(Month N → 1~31 → 해당 일간)으로 바뀌고 데일리 372 + 위클리 52가 붙는다.

빌드 후 **반드시** 중복 제거를 돌린다. Etsy 디지털 파일은 **20MB 상한**이다.

```bash
PLANNER_VERSION=v8-undated python scripts/build_planner.py
python scripts/dedupe_pdf.py output/planner_v8-undated.pdf output/planner_v8-undated-FINAL.pdf
```

**기존 버전은 지우지 않는다.** 각 버전은 자기 파일명으로 출력되고
`archive/`에 생성 스크립트 사본이 있다.

## 공통 디자인 규칙

- **섹션 헤더** = 폭 2.6pt 세로 바 + 볼드 라벨
- **면을 통째로 원색으로 칠하지 않는다.** 색은 점·세로바·칩에만
- 입력 영역은 회색 필드 박스, 필기 영역은 얇은 괘선
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

## 빌드가 조용히 실패하는 두 가지 (둘 다 겪음)

**1. 출력 PDF가 잠겨 있으면 Chrome은 종료 코드 0으로 아무것도 쓰지 않는다.**
한 시간 동안 낡은 PDF를 측정하며 "수정 완료"라고 보고한 적이 있다. 그래서
`to_pdf()`는 빌드 후 mtime이 갱신됐는지 확인하고 아니면 예외를 던진다. 이
가드를 절대 제거하지 말 것.

**2. 잠그는 주범은 뷰어가 아니라 `pypdfium2`다.** `PdfDocument(path)`는 파일
핸들을 유지한다. 같은 프로세스에서 측정 후 재빌드하면 반드시 막힌다. 측정은
바이트로 읽어서 열 것:

```python
with open(path, 'rb') as fh:
    doc = pdfium.PdfDocument(fh.read())
...
doc.close()
```

## 작업 규칙

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
