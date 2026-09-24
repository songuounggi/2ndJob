# 다른 PC에서 이어서 작업하기

집 노트북 등에서 이 프로젝트를 받아 똑같은 PDF를 뽑기까지의 전 과정.
**각 단계마다 "어느 디렉토리에서" 치는지 적어뒀다.**

셸이 두 종류라 환경변수 문법이 다르다. 헷갈리면 아래 표만 기억하면 된다.

| | PowerShell | Git Bash |
|---|---|---|
| 환경변수 주고 실행 | `$env:NAME="값"; python x.py` | `NAME=값 python x.py` |

PowerShell에서 `PLANNER_VERSION=v8.18-undated python ...` 를 치면 환경변수가
전달되지 않고 기본값 `v2-warm` 이 빌드된다. **에러 없이 다른 파일명으로
성공 메시지가 뜨기 때문에** 눈치채기 어렵다. (실측 확인함)

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
git clone https://github.com/songuounggi/2ndJob.git 2ndJob
```

`~/AiProject/2ndJob` 이 생긴다. **이후 모든 명령은 이 폴더 안에서 친다.**

> **경로는 회사 PC 와 같을 필요가 없다.** `D:\workndJob` 이든 어디든
> 된다. git 은 폴더 위치를 기억하지 않는다. 회사와 맞추는 것은 순전히
> 사람이 헷갈리지 않기 위해서다.

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

> **`UnicodeDecodeError: 'cp949' codec` 이 나면** — 한국어 Windows 는 pip 이
> `requirements.txt` 의 한글 주석을 cp949 로 읽다 멈춘다(집 PC, 2026-09-24).
> 그래서 이 파일 맨 앞에 **UTF-8 BOM** 을 넣어 두었다. 편집기가 BOM 을
> 지워버렸으면 다시 이 에러가 난다. 그때는 `$env:PYTHONUTF8=1` (PowerShell)
> 또는 `PYTHONUTF8=1` (Git Bash) 을 앞에 붙여 설치한다.

---

## 3. 커밋 신원 (PC마다 한 번, clone 직후)

`2ndJob` 안에서.

**이건 clone으로 따라오지 않는다.** git은 저장소 설정(`.git/config`)을
복제하지 않기 때문에, 새 PC에서는 매번 다시 넣어야 한다. 빠뜨리면 그 PC의
전역 설정(회사 계정일 수 있다)으로 커밋이 찍힌다.

```bash
git config --local user.email "s5worth@gmail.com"
git config --local user.name "ygSong"
```

`--local` 이 핵심이다. `--global` 로 하면 그 PC의 회사 저장소까지 개인
메일로 바뀐다. **이 프로젝트는 개인 프로젝트라 회사 설정과 섞이면 안 된다.**

확인:

```bash
git config --local --get user.email
```

`s5worth@gmail.com` 이 나오면 된다.

---

## 4. Chrome 경로 확인

`2ndJob` 안에서.

```bash
grep -n "^CHROME" scripts/build_planner.py
```

출력된 경로에 chrome.exe 가 실제로 있는지 본다. 없으면
`scripts/build_planner.py` 의 `CHROME` 상수를 자기 PC 경로로 고친다.

---

## 5. 빌드

`2ndJob` 안에서. `output/` 과 `src/` 는 git에 없다 — 생성물이라 여기서
다시 만들어진다.

**PowerShell**

```bash
$env:PLANNER_VERSION="v8.20-undated"; python scripts/build_planner.py
```

**Git Bash**

```bash
PLANNER_VERSION=v8.20-undated python scripts/build_planner.py
```

`Saved: ...\output\planner_v8.20-undated.pdf` 가 찍히면 성공.

> **`v8.20-undated` 가 올릴 판이다**(2026-09-24, GoodNotes 렌더링 + 도트 그리드 수정).
> Etsy 교체 전까지 판매 중인 것은 `v8.18-undated` 이고, 무엇이 언제 올라갔는지는
> `shop.md` 0-1절 업로드 이력표가 기준이다. `v8-undated` 는 2026-09-21
> 출시본(494p). 버전 이름을 틀리면 옛 판을 만들게 된다.

이어서 중복 스트림을 접는다. **이 단계를 빼면 25.9MB라 Etsy 20MB 상한을
넘는다.**

```bash
python scripts/dedupe_pdf.py output/planner_v8.20-undated.pdf output/planner_v8.20-undated-FINAL.pdf
```

기대 출력:

```
... duplicate streams folded into ... unique
21.4 MB -> 15.8 MB (26% smaller)
```

(2026-09-24 집 PC 실측. v8.18 은 `3196 ... 26.4 MB -> 18.7 MB`.)

마지막으로 **Etsy 에 실제로 올린 이름**의 사본을 만든다. 구매자가 받는 파일은
이 이름이다(이유는 `shop.md` 5-5절). 내용은 `-FINAL` 과 바이트까지 같다.

```bash
mkdir -p output/upload/v8.18
cp output/planner_v8.18-undated-FINAL.pdf output/upload/ADHD-Wellness-Planner-Undated-502-pages.pdf
cp output/planner_v8.18-undated-FINAL.pdf output/upload/v8.18/ADHD-Wellness-Planner-Undated-502-pages.pdf
```

`output/upload/` 바로 아래 = **원본(v8.18). 이후 절대 바꾸지 않는다.**
`upload/<버전>/` = Etsy 에 올린 판마다 하나. 이후 올린 판이 생기면
(`shop.md` 0-1절 이력표에 날짜가 적힌 줄) 같은 식으로 `upload/<그 버전>/` 을 만든다.
이력표의 옛 판(#1, #2)이 이 PC 에 없으면 "소스" 칸대로 빌드한다. 다 됐으면
이력표와 대조한다(`FAILURES: 0` 이면 된다):

```bash
python scripts/check_upload.py
```

---

## 6. 검수

`2ndJob` 안에서.

**페이지 수와 링크**

```bash
python -c "import os; from pypdf import PdfReader; p='output/planner_v8.20-undated-FINAL.pdf'; r=PdfReader(p); print(len(r.pages),'pages /',len(r.named_destinations),'destinations / %.2f MB'%(os.path.getsize(p)/1048576))"
```

기대값: `502 pages / 501 destinations / 15.75 MB`

**구조 검사 16항목** — 이것 하나로 위 숫자와 링크·탭까지 다 본다.
마지막 줄이 `FAILURES: 0` 이면 된다.

```bash
python scripts/verify_v8_20.py
```

**눈으로 볼 페이지 뽑기**

```bash
python -c "
import pypdfium2 as pdfium, os
os.makedirs('output/preview', exist_ok=True)
with open('output/planner_v8.20-undated-FINAL.pdf','rb') as fh:
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

## 7. Etsy 리스팅 이미지

`2ndJob` 안에서. **6단계의 PNG 렌더가 먼저 있어야 한다.**

```bash
python scripts/verify_v8_18.py            # 구조 13항목
python scripts/check_lines.py src/planner_v8.18-undated.html   # 선 11항목
python scripts/build_mockups.py           # 리스팅 이미지 10장
```

`output/listing/` 에 2000x2000 PNG 8장이 생긴다.

---

## 8. 다른 버전 뽑기

`2ndJob` 안에서. 버전 이름만 바꾸면 된다. 기존 버전은 지우지 않는다.

```bash
$env:PLANNER_VERSION="v7-bright"; python scripts/build_planner.py
```

쓸 수 있는 값: `v1-admin` `v2-warm` `v3-sunset` `v5-sky` `v6-skyblue`
`v7-bright` `v8-undated`(출시본) `v8.18-undated` `v8.19-undated` `v8.20-undated`(올릴 판)

---

## 회사 PC ↔ 집 노트북 오가기

| PC | 작업 폴더 | 방 이름 예 |
|---|---|---|
| 회사 | `C:\Users\ThinkBook\AiProject\2ndJob` | `... (Office)` |
| 집 | `C:\Users\sBrain\2ndJob` | `Prod 1. ADHD Planners (Home)` |

**PC 를 옮겨 앉으면 이 순서로 한다:**

1. 떠나는 PC 에서 — 각 방이 자기 파일을 커밋·푸시 (`git status` 가 깨끗해질 때까지)
2. 도착한 PC 에서 — `git pull`
3. 필요하면 5단계로 다시 빌드. 이전 PC 의 PDF 는 따라오지 않는다

**1번을 빠뜨리면** 도착한 PC 에서 작업한 뒤 나중에 원래 PC 에서 pull 할 때
충돌이 난다. 긴 연휴 전에는 특히 확인할 것.

### 어느 창에 치는가

**가장 쉬운 방법 — 안 쳐도 된다.** 그 PC 에서 Claude Code 를 이 폴더로 열고
"git pull 해줘" 라고 말하면 된다. Claude 가 올바른 디렉토리에서 실행한다.

직접 치려면 **프로젝트 폴더 안에서** 창을 열어야 한다. 다른 데서 치면
"not a git repository" 가 난다.

1. 탐색기로 `2ndJob` 폴더를 연다
2. 주소창(경로가 적힌 칸)을 클릭하고 `powershell` 이라고 친 뒤 Enter
3. 그 폴더에서 열린 PowerShell 에 아래를 친다

**다른 PC에서 시작할 때:**

```bash
git pull
```

**작업을 끝낼 때:**

```bash
git add <고친 파일> && git commit -m "무엇을 했는지" && git push
```

> **`git add -A` 를 쓰지 말 것.** 이 프로젝트는 방을 나눠 쓴다. `-A` 는
> 다른 방이 만들던 파일까지 전부 담는다 -- 실제로 그렇게 다른 방의
> 작업 중인 파일이 커밋에 섞여 들어간 적이 있다. **고친 파일을 이름으로
> 적는다.** 무엇이 바뀌었는지는 `git status` 로 먼저 본다.

`CLAUDE.md` 도 같이 따라오므로, 어느 쪽에서 Claude Code 를 열든 프로젝트
규칙(그림자 사양, 빌드가 조용히 실패하는 경우 등)을 그대로 알고 시작한다.

**주의** — `output/` 은 git에 없다. 완성 PDF를 집 노트북으로 옮기고 싶으면
파일을 직접 복사하거나, 위 5단계로 다시 뽑으면 된다. 내용은 같지만
**바이트 단위로 같지는 않다** — Chrome이 `/CreationDate` 와 `/ModDate` 에
빌드 시각을 박아넣기 때문이다. 페이지 수·링크 수·용량으로 검증할 것.

Etsy에 이미 올린 파일을 다시 뽑을 필요는 없다. 판매 중인 PDF를 바꿀 때만
다시 빌드하고, 6단계 검수를 통과한 뒤 교체한다.
