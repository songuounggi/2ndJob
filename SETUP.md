# 다른 PC에서 이어서 작업하기

집 노트북 등에서 이 프로젝트를 받아 똑같은 PDF를 뽑기까지의 전 과정.
**각 단계마다 "어느 디렉토리에서" 치는지 적어뒀다.**

셸이 두 종류라 환경변수 문법이 다르다. 헷갈리면 아래 표만 기억하면 된다.

| | PowerShell | Git Bash |
|---|---|---|
| 환경변수 주고 실행 | `$env:NAME="값"; python x.py` | `NAME=값 python x.py` |

PowerShell에서 `PLANNER_VERSION=v8-undated python ...` 를 치면
**조용히 기본 버전이 빌드된다.** 실제로 겪을 수 있는 함정이다.

---

## 0. 사전 준비 (PC마다 한 번)

디렉토리 상관없이, 아무 데서나.

**Python 3.10 이상**

```bash
python --version
```

없으면 <https://www.python.org/downloads/> 에서 설치.
설치할 때 **"Add Python to PATH" 체크**를 빠뜨리지 말 것.

**Google Chrome** — PDF를 뽑는 엔진이다. 없으면 아무것도 안 나온다.

```bash
ls "/c/Program Files/Google/Chrome/Application/chrome.exe"
```

경로가 다르면 나중에 4단계에서 고친다.

**Git**

```bash
git --version
```

---

## 1. 받기

받고 싶은 **상위 폴더**에서. 회사 PC와 같은 구조로 맞추고 싶다면:

```bash
mkdir -p ~/AiProject
cd ~/AiProject
```

그 다음:

```bash
git clone <저장소 주소> 2ndJob
```

`~/AiProject/2ndJob` 이 생긴다. **이후 모든 명령은 이 폴더 안에서 친다.**

```bash
cd ~/AiProject/2ndJob
```

---

## 2. 패키지 설치

`2ndJob` 안에서.

```bash
pip install -r requirements.txt
```

확인:

```bash
python -c "import PIL, numpy, pikepdf, pypdf, pypdfium2; print('ok')"
```

`ok` 가 찍히면 된다.

---

## 3. Chrome 경로 확인

`2ndJob` 안에서.

```bash
grep -n "^CHROME" scripts/build_planner.py
```

출력된 경로에 chrome.exe 가 실제로 있는지 본다. 없으면
`scripts/build_planner.py` 의 `CHROME` 상수를 자기 PC 경로로 고친다.

---

## 4. 빌드

`2ndJob` 안에서. `output/` 과 `src/` 는 git에 없다 — 생성물이라 여기서
다시 만들어진다.

**PowerShell**

```bash
$env:PLANNER_VERSION="v8-undated"; python scripts/build_planner.py
```

**Git Bash**

```bash
PLANNER_VERSION=v8-undated python scripts/build_planner.py
```

`Saved: ...\output\planner_v8-undated.pdf` 가 찍히면 성공.

이어서 중복 스트림을 접는다. **이 단계를 빼면 25.9MB라 Etsy 20MB 상한을
넘는다.**

```bash
python scripts/dedupe_pdf.py output/planner_v8-undated.pdf output/planner_v8-undated-FINAL.pdf
```

기대 출력:

```
3173 duplicate streams folded into 19084 unique
25.9 MB -> 18.3 MB (29% smaller)
```

---

## 5. 검수

`2ndJob` 안에서.

**페이지 수와 링크**

```bash
python -c "import os; from pypdf import PdfReader; p='output/planner_v8-undated-FINAL.pdf'; r=PdfReader(p); print(len(r.pages),'pages /',len(r.named_destinations),'destinations / %.2f MB'%(os.path.getsize(p)/1048576))"
```

기대값: `494 pages / 493 destinations / 18.33 MB`

**눈으로 볼 페이지 뽑기**

```bash
python -c "
import pypdfium2 as pdfium, os
os.makedirs('output/preview', exist_ok=True)
with open('output/planner_v8-undated-FINAL.pdf','rb') as fh:
    d = pdfium.PdfDocument(fh.read())
for n in [1,2,12,13,14,16,20,21,24,25,26,27,28,31,35,38,39,47,50,51,54,58]:
    d[n-1].render(scale=2).to_pil().save(f'output/preview/v8_p{n}.png')
d.close(); print('ok')
"
```

`output/preview/` 에 PNG가 생긴다. **반드시 열어서 눈으로 확인할 것.**

전체 검사 항목(죽은 앵커, 고아 페이지, 탭 하이라이트 등)은 `CLAUDE.md` 의
"500페이지 규모에서 터진 것들" 절을 볼 것.

---

## 6. Etsy 리스팅 이미지

`2ndJob` 안에서. **5단계의 PNG 렌더가 먼저 있어야 한다.**

```bash
python scripts/build_mockups.py
```

`output/listing/` 에 2000x2000 PNG 8장이 생긴다.

---

## 7. 다른 버전 뽑기

`2ndJob` 안에서. 버전 이름만 바꾸면 된다. 기존 버전은 지우지 않는다.

```bash
$env:PLANNER_VERSION="v7-bright"; python scripts/build_planner.py
```

쓸 수 있는 값: `v1-admin` `v2-warm` `v3-sunset` `v5-sky` `v6-skyblue`
`v7-bright` `v8-undated`

---

## 회사 PC ↔ 집 노트북 오가기

**작업을 끝낼 때** — `2ndJob` 안에서:

```bash
git add -A && git commit -m "무엇을 했는지" && git push
```

**다른 PC에서 시작할 때** — `2ndJob` 안에서:

```bash
git pull
```

`CLAUDE.md` 도 같이 따라오므로, 어느 쪽에서 Claude Code 를 열든 프로젝트
규칙(그림자 사양, 빌드가 조용히 실패하는 경우 등)을 그대로 알고 시작한다.

**주의** — `output/` 은 git에 없다. 완성 PDF를 집 노트북으로 옮기고 싶으면
파일을 직접 복사하거나, 위 4단계로 다시 뽑으면 된다. 같은 스크립트라
바이트 단위로 같은 결과가 나온다.
