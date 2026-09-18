# 다른 PC에서 이어서 작업하기

집 노트북 등에서 이 프로젝트를 받아 그대로 빌드하는 순서.

## 1. 받기

```bash
git clone <저장소 주소> 2ndJob
cd 2ndJob
```

## 2. 필요한 것

- **Python 3.10+**
- **Google Chrome** — PDF를 뽑는 엔진이다. 없으면 아무것도 안 나온다
- 패키지: `pip install -r requirements.txt`

Chrome 경로가 기본값과 다르면 `scripts/build_planner.py` 의 `CHROME`
상수를 고친다. 기본값은 Windows 경로다.

```
C:\Program Files\Google\Chrome\Application\chrome.exe
```

## 3. 빌드

`output/` 과 `src/` 는 git에 없다. 생성물이라 아래 두 줄로 복원된다.

```bash
PLANNER_VERSION=v8-undated python scripts/build_planner.py
python scripts/dedupe_pdf.py output/planner_v8-undated.pdf output/planner_v8-undated-FINAL.pdf
```

494페이지 / 약 18.3MB 가 나오면 정상이다.

## 4. 검수

```bash
python -c "
from pypdf import PdfReader
r = PdfReader('output/planner_v8-undated-FINAL.pdf')
print(len(r.pages), 'pages /', len(r.named_destinations), 'destinations')
"
```

`494 pages / 493 destinations` 가 기대값이다.
자세한 검사 항목은 `CLAUDE.md` 를 볼 것.

## 5. Etsy 리스팅 이미지

```bash
python scripts/build_mockups.py
```

`output/preview/v8_p*.png` 를 먼저 만들어 둬야 한다(`CLAUDE.md` 참고).

---

## 회사 PC ↔ 집 노트북 오가기

작업을 끝낼 때마다:

```bash
git add -A && git commit -m "무엇을 했는지" && git push
```

다른 PC에서 시작할 때:

```bash
git pull
```

`CLAUDE.md` 도 같이 따라오므로, 어느 쪽에서 Claude Code 를 열든 프로젝트
규칙(그림자 사양, 빌드가 조용히 실패하는 경우 등)을 그대로 알고 시작한다.
