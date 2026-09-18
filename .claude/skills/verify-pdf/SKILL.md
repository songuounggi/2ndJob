---
name: verify-pdf
description: 완성된 PDF를 검수한다 — 페이지별 PNG 렌더 후 눈으로 확인, 내부 링크 목적지 검증, 문제점 보고. PDF를 새로 만들었거나 수정한 직후에 사용.
---

# PDF 검수 절차

`output/` 의 PDF를 검수한다. 인자로 파일명이 주어지면 그것을, 없으면
`output/` 에서 가장 최근에 수정된 `.pdf` 를 대상으로 한다.

## 1. 페이지 렌더

```bash
python -c "
import pypdfium2 as pdfium, os
os.makedirs('output/preview', exist_ok=True)
pdf = pdfium.PdfDocument('<대상파일>')
for i in range(len(pdf)):
    pdf[i].render(scale=2).to_pil().save(f'output/preview/page{i+1}.png')
print('rendered', len(pdf), 'pages')
"
```

## 2. 눈으로 확인 (생략 금지)

렌더된 PNG를 **Read 도구로 전부 연다.** 이 단계를 건너뛰고 "정상입니다"라고
보고한 적이 있고, 그때 텍스트 잘림·박스 겹침·행 높이 붕괴를 놓쳤다.

확인 항목:

- 텍스트가 카드 밖으로 넘치거나 잘리지 않았는지
- 카드끼리 겹치지 않았는지 (특히 상단 배너와 우측 카드의 y좌표 구간)
- 카드 안에 과도한 빈 공간이 남지 않았는지
- 그리드 행 높이가 콘텐츠에 비해 터무니없이 크지 않은지
- 얇은 선이 배경 틴트와 같은 색이라 사라지지 않았는지

## 3. 내부 링크 검증

```bash
python -c "
from pypdf import PdfReader
r = PdfReader('<대상파일>')
nd = r.named_destinations
idx = {id(p.indirect_reference.get_object()): n+1 for n,p in enumerate(r.pages)}
for i, pg in enumerate(r.pages):
    out = []
    for a in pg.get('/Annots') or []:
        o = a.get_object(); d = o.get('/Dest')
        if isinstance(d, str):
            tgt = nd[d]['/Page'].get_object()
        elif isinstance(d, list):
            tgt = d[0].get_object()
        else:
            out.append('?'); continue
        out.append(f'p{idx[id(tgt)]}')
    print(f'page {i+1}: {len(out)} links -> {out}')
"
```

모든 페이지에서 링크 개수가 같고, 목적지가 의도한 페이지 번호와 맞는지 본다.

## 4. 시각 속성 측정 (해당될 때만)

그림자 농도, 여백처럼 눈으로 애매한 속성이 쟁점이면 픽셀값을 위치별로 찍어서
의도한 기울기가 나오는지 수치로 확인한다.

```bash
python -c "
import pypdfium2 as pdfium
img = pdfium.PdfDocument('<대상파일>')[0].render(scale=8).to_pil().convert('L')
W, H = 612, 792
def px(xp, yp): return img.getpixel((int(xp*8), int((H-yp)*8)))
# 예: 카드 하단 가장자리를 좌→우로 훑어 중앙이 더 진한지 확인
"
```

## 5. 보고

발견한 문제를 **위치와 함께** 구체적으로 적는다. "3페이지 에너지 카드 라벨이
카드 경계를 넘어감" 처럼. 문제가 없으면 없다고 한 줄로 끝낸다.

문제를 발견하면 고치기 전에 원인을 먼저 말한다 (예: "카드 높이를 상수로
박아둬서 내용이 넘침" ). 증상만 가리지 않는다.
