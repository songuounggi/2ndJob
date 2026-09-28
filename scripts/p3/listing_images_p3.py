# -*- coding: utf-8 -*-
"""상품 3 Etsy 리스팅 이미지 **시안** -- 실제 판매 파일 페이지를 렌더해 2000x2000 정사각형에 배치한다. Prod 3 방 소유.

    python scripts/p3/listing_images_p3.py            # -> output/prod3/listing/draft-v0.1/

디자인은 사용자 것(Lifted Paper 핸드오프). 여기서는 핸드오프의 종이색·잉크·청록·Source Serif 4 만 쓴다.
이미지 속 문구는 listing-p3.md 에서 check_listing_p3.py 를 통과한 주장만 쓴다(구매자 글 규칙).
이미 있는 시안 폴더면 멈춘다(덮어쓰지 않는다) -- 고치면 DRAFT 를 올린다.
"""
import pathlib
import re
import sys

import numpy as np
import pypdfium2 as pdfium

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[2]
VER = "v0.23"
DRAFT = "draft-v0.43"   # v0.43: v0.42 와 같음 -- v0.42 는 IPAD_CSS 중괄호 이중 이스케이프로 CSS 가 깨져 01 에서 멈춤(자르기 검사가 잡았다) / v0.42: iPad·펜슬 그림자·유리 반사·테두리 대비 옅게(devices_p3), 07 장면 v0.11. 스티커 그림자는 그대로 (사용자: 과해서 그림판 같다, 스티커는 깊어서 좋다) / v0.41: 07 장면 v0.10(KEEP 스티커가 펜슬에 가렸다) / v0.40: 07 스티커 장면 v0.9(01 과 같은 펜슬·iPad) / v0.39: 펜슬 회전 부호 -- PIL rotate 는 반시계가 + 라 -62 가 펜슬을 화면 아래 밖으로 보냈다(v0.38) / v0.38: 01 시안 2 -- 종이 두 장 -> iPad 두 대(알루미늄 테두리·유리 베젤) + 3D 음영 Apple Pencil(devices_p3.py) + 배지 알약 4개. iPad 는 4:3·4:5 검색 자르기 안(사용자: 경쟁작처럼 iPad 가 보이게, 펜슬은 사진처럼) / v0.37: 01 띠를 부제 글자와 종이 사이 딱 중간(726px)으로 내리고 전환 70->130px 로 부드럽게 -- 검사를 상자가 아니라 렌더 픽셀로(상자엔 여백이 있어 32px 위였다, 사용자) / v0.36: v0.35 의 스티커 자리 (1650,70,200) 도 04 와 9px -> (1650,55,195). v0.35 폴더는 03 까지만 -- 04 에서 멈춤 / v0.35: 오른쪽 위 스티커 자리 (1600,150,230)->(1650,70,200) 10장 공통 -- 04 제목 끝이 SORT OF 스티커와 103px 겹쳤다 + 글자-스티커 16px 검사. 06 제목 "4 PDFs." 뒤 줄바꿈(balance 가 "Pick" 뒤에서 끊었다) / v0.34: 01 청록 띠를 제목과 페이지 사이로 올림 -- 전환 660->730px(부제 아래 652 · 페이지 위 737 사이 안에서 끝난다). 띠가 너무 커서 상품이 묻혔다(사용자) / v0.33: v0.32 + 08 펼침 높이 900->870·간격 268->259 (제목이 커져 안전 영역 1750 을 24px 넘었다. v0.32 폴더는 07 까지만 -- 08 에서 멈춤) / v0.32: 제목 키움 A안 -- .k 34->40, h1 104->150(01 hero 176), p.s 42->48, 제목·부제 text-wrap:balance (폰 Etsy 앱에서 제목이 너무 작았다, 사용자: 상품 1·2 와 일관되게 전부 A) / v0.31: 01 청록 띠 V1 -- 종이 위 1/3 에서 끝, 청록->바탕을 OKLab 으로 직접 잇고 ease 12단(마스크 투명은 중간이 탁했다 -- 사용자) / v0.30: v0.30: 01 청록 띠를 종이 중간까지 늘리고 경계 짧게(흐림이 종이 윗가장자리와 겹쳐 어색했다 -- 사용자) / v0.29: v0.29: 페이지 그림의 책상(회색 네모)을 투명하게 -- 색 배경 위에서 네모 모서리가 드러났다. 종이 그림자는 알파로 남긴다, CSS 네모 그림자 뺌 / v0.28: v0.28: 07 장면 투명 배경(장면 v0.8) / v0.27: v0.27: 배경에 색 -- 01 은 청록 띠(C) + 스티커, 나머지는 리소 원(B2, 팔레트 색) + 스티커, 원·띠 경계 흐림 (사용자: 경쟁작보다 썰렁하다) / v0.26: v0.26: 플래너 v0.23 페이지(모서리 하이라이트 고침)·장면 v0.7 로 다시 찍음. 구성·문구 그대로 / v0.25: v0.25: 10 Works anywhere 뺌, 스티커를 7번째로(사용자), 파일 번호 = 올릴 순서. 09 의 15일 고리 작게·정확히(3월 달력 잘라낸 그림 속 15 글자 가운데) / v0.24: v0.24: 09 페이지 크게(아래가 비었다), 15 고리 가운데로 / v0.23: v0.23: 09 선을 그림이 다 들어온 뒤에 잰다(v0.22 는 엉뚱한 곳), 점선 정리 / v0.22: v0.22: 09 허공 화살표(사용자: 아마추어 같다) -> 누르는 자리에 번호 표시(탭 물결), 3월 달력 확대 카드, 그날 페이지 제목으로 곡선 연결 / v0.21: v0.21: 11 장면 그림자 잘림 경계선 없앰(장면 v0.6) / v0.20: v0.20: 11 스티커 장면을 iPad 세로 통째로(잘라 넣어 가로 모드처럼 보였다 -- 사용자), 배경색 같게 / v0.19: v0.19: v0.22 페이지(종이 W1)로 다시 찍음, 06 에 스티커 키트 한 줄(판매 파일 5번째 ZIP), 11 스티커 실사용 장면 후보(10장 중 하나와 바꿀 것, 사용자 선택) / v0.18: v0.17: 영문 교정된 v0.8 페이지로 다시 찍음 / v0.16: 09 화살표·TAP 에 그림자(사용자: 썰렁하다) / v0.15: 배지를 페이지 밖으로 올린 것보다 v0.14(페이지 윗가장자리에 걸침, 본문은 안 가림)가 낫다(사용자) -> v0.14 위치로 / v0.14: 07 배지가 페이지 머리글을 가렸다 -> 페이지 바로 위(밖), 계단 따라 / v0.13: 07 배지를 각 페이지 왼쪽 위로, 페이지 계단을 따라(사용자). 08 은 그대로 / v0.11: 07 만 라벨을 06 처럼 청록 배경 + 흰 글자, 기울이지 않음(사용자). 08 은 그대로 (v0.12 는 08 까지 바꾸다 간격 검사에서 멈춤) / v0.10: 07 BRAIN WEATHER 배지가 REVIEW 배지에 붙었다 -> 배지 글자 22px / v0.9: 07·08 배지가 페이지 어긋남을 따라 높이가 제각각 -> 한 줄로 / v0.8: 07·08 페이지가 작고 아래가 비었다 -> 크게 겹쳐 펼침 / v0.7: 10장으로(사용자: 기존 두 상품 10장) -- 07 한 달, 08 12월, 09 2탭, 10 어디서나 / v0.6: 안전 영역 검사가 06 마지막 배지(오른쪽 1754px)에서 멈춤 -> 배지를 표지 안쪽으로 (v0.6 폴더는 01-05 만 있다) / v0.5: 배지 5도, 안전 영역(글자가 왼쪽 120px 에서 시작 -> 검색 목록에서 잘림) / v0.4: 15도는 너무 기울었다 -> 8도(사용자) / v0.3: 배지 시계방향 15도(사용자) / v0.1: 05 썸네일 3줄이 아래로 잘림, 06 아래가 비었다 / v0.2: 06 표지 네 장이 멀리서 구분 안 됨 -> 배지
PDF = ROOT / "output" / "prod3" / "planner" / VER / "ADHD-Year-Planner-2027-mon.pdf"
HTML = ROOT / "src" / "prod3" / "planner" / VER / "ADHD-Year-Planner-2027-mon.html"
OUT = ROOT / "output" / "prod3" / "listing" / DRAFT
if OUT.exists():
    raise SystemExit(f"{OUT} 는 이미 있다. 덮어쓰지 않는다 -- DRAFT 를 올릴 것.")
OUT.mkdir(parents=True)
PAGES = OUT / "_pages"
PAGES.mkdir()
SCENE = ROOT / "output" / "prod3" / "preview" / "sticker_scene" / "draft-v0.11" / "sticker_scene_full.png"   # scripts/p3/sticker_scene_p3.py
(OUT / "scene.png").write_bytes(SCENE.read_bytes())

ids = re.findall(r'<section class="pg" id="([^"]+)"', HTML.read_text(encoding="utf-8"))
WANT = ["cover", "sos", "year", "experiments", "m3", "d3-15", "d3-16", "w12", "q1", "bw3", "admin",
        "rsd", "budget", "dopamine", "mailbox", "playbook", "mp3", "mr3", "yearreview", "myhol",
        "note1", "note2", "note3", "note4"]
with open(PDF, "rb") as fh:
    doc = pdfium.PdfDocument(fh.read())
def cut_desk(im):
    """페이지 그림에서 책상을 뺀다 -- 종이(시트)는 그대로, 탭은 불투명, 책상 위 그림자는 검정 + 알파(= 책상색 위에 얹었을 때 원래와 같다)."""
    import numpy as np
    from PIL import Image
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    h, w, _ = a.shape
    desk = a[4:12, 4:12].reshape(-1, 3).mean(0)                    # 왼쪽 위 구석 = 평평한 책상
    k = w / 768                                                    # 페이지 768px 기준
    x0, x1, y0, y1 = round(25 * k), round((25 + 692) * k), round(38 * k), round((38 + 948) * k)   # 시트 (핸드오프 38px - 탭 이동 13px)
    lum, dl = a.mean(2), desk.mean()
    chroma = a.max(2) - a.min(2)
    alpha = np.ones((h, w), np.float32)
    out = a.copy()
    outside = np.ones((h, w), bool); outside[y0:y1, x0:x1] = False
    keep = (lum > dl + 2) | (chroma > 14) | (lum < dl * .6)          # 탭(밝다)·켜진 탭(색)·탭 글자(아주 어둡다)
    flat = outside & ~keep & (lum >= dl - 1.5)
    shade = outside & ~keep & ~flat
    alpha[flat] = 0
    alpha[shade] = np.clip(1 - lum[shade] / dl, 0, 1)
    out[shade] = 0
    rgba = np.dstack([out, alpha * 255]).clip(0, 255).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


for k in WANT:
    cut_desk(doc[ids.index(k)].render(scale=2.2).to_pil()).save(PAGES / f"{k}.png")
# 09 확대 카드: Year at a glance 의 3월 달력 (15일에 고리) -- 좌표는 PDF pt
_yp = doc[ids.index("year")]
import pymupdf as _mu  # noqa: E402  (잘라 찍기는 pymupdf 가 간단하다)
_md = _mu.open(PDF)
_md[ids.index("year")].get_pixmap(matrix=_mu.Matrix(6, 6), clip=_mu.Rect(282, 150, 394, 238)).save(str(PAGES / "mag_march.png"))
_md.close()
doc.close()
# 06 에 네 판 표지 -- 월/일 시작, 연도가 표지에 찍혀 있다
for y in ("2026", "2027"):
    for w in ("mon", "sun"):
        with open(ROOT / "output" / "prod3" / "planner" / VER / f"ADHD-Year-Planner-{y}-{w}.pdf", "rb") as fh:
            d = pdfium.PdfDocument(fh.read())
        cut_desk(d[0].render(scale=1.4).to_pil()).save(PAGES / f"cover-{y}-{w}.png")
        d.close()
# 01 기기 목업 (v0.38 사용자 시안 2): iPad 화면 = PDF 페이지 그대로(GoodNotes 에서 보이는 모습 -- 책상 포함), 펜슬 = 3D 음영 계산
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from devices_p3 import IPAD_CSS, ipad, pencil_png  # noqa: E402
_md = _mu.open(PDF)
for _k in ("cover", "d3-15"):
    _md[ids.index(_k)].get_pixmap(matrix=_mu.Matrix(2.2, 2.2)).save(str(PAGES / f"scr_{_k}.png"))
_md.close()
_pen, (_tx, _ty) = pencil_png(600, 62)   # 반시계 62도 -- 펜촉이 왼쪽 아래, 뒤끝이 오른쪽 위
_pen.save(PAGES / "pencil.png")

PAPER, INK, N700, CYAN = "#fdfcfa", "#201e1d", "#605d5d", "#006786"   # 종이 W1 (플래너 v0.22)
CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=block');
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:2000px;height:2000px;overflow:hidden;background:#e9e6e3;color:{INK};font-family:'Source Serif 4',Georgia,serif}}
.wrap{{position:absolute;inset:0;padding:250px 260px;display:flex;flex-direction:column}}   /* 안전 영역: Etsy 검색은 양옆 ~140px 을 자르고 4:3 자리는 가운데만 -- product2-student.md 목업 안전 영역 */
.k{{font-size:40px;letter-spacing:.14em;text-transform:uppercase;color:{CYAN}}}
h1{{font-size:150px;font-weight:600;line-height:1.0;margin:22px 0 26px;letter-spacing:-.01em;text-wrap:balance}}
p.s{{font-size:48px;font-style:italic;color:{N700};line-height:1.3;text-wrap:balance}}   /* balance: 제목·부제 끝에 한 단어만 떨어지지 않게 (v0.32) */
.row{{flex:1;min-height:0;display:flex;gap:50px;align-items:flex-end;justify-content:center;margin-top:50px}}
.pg{{height:100%;max-height:1000px;max-width:48%;object-fit:contain}}
.pg.t{{transform:rotate(-2deg)}} .pg.u{{transform:rotate(1.5deg)}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:30px;margin-top:50px}}
.grid img{{width:100%}}
.list{{font-size:38px;line-height:1.55;margin-top:34px}}
.list b{{color:{CYAN};font-weight:600}}
.pill{{display:inline-block;border:2px solid {N700};border-radius:999px;padding:8px 28px;font-size:34px;margin:0 14px 16px 0}}
.cv{{position:relative}}.cv img{{width:100%}}
.bdg{{position:absolute;top:-22px;right:8px;border-radius:22px;padding:12px 20px 10px;text-align:center;color:#fff;box-shadow:0 8px 18px rgba(0,0,0,.22);transform:rotate(5deg)}}
.bdg b{{display:block;font-size:52px;font-weight:600;line-height:1}}.bdg span{{display:block;font-size:24px;margin-top:6px;letter-spacing:.04em}}
.bdg.mon{{background:{CYAN}}}.bdg.sun{{background:{INK}}}
.trio{{flex:1;min-height:0;display:flex;gap:34px;justify-content:center;align-items:flex-start;margin-top:50px}}
.fig{{flex:1;min-width:0;display:flex;flex-direction:column;align-items:center}}
.fig img{{width:100%}}
.cap{{margin-top:22px;font-size:30px;letter-spacing:.1em;text-transform:uppercase;color:{N700};text-align:center}}
.cap b{{color:{CYAN};font-weight:600}}
.arrow{{flex:none;align-self:center;display:flex;flex-direction:column;align-items:center;gap:14px;color:{CYAN};font-size:30px;letter-spacing:.08em;text-transform:uppercase}}
.arrow svg{{filter:drop-shadow(0 6px 8px rgba(0,0,0,.28)) drop-shadow(0 2px 2px rgba(0,0,0,.18))}}
.arrow span{{font-weight:600;text-shadow:0 4px 8px rgba(0,0,0,.25),0 1px 2px rgba(0,0,0,.18)}}
.steps{{display:flex;gap:22px;margin-top:34px}}.step{{display:flex;align-items:center;gap:16px;font-size:38px}}
.step i{{font-style:normal;width:58px;height:58px;border-radius:50%;background:{CYAN};color:#fff;display:flex;align-items:center;justify-content:center;font-size:32px}}
.fan{{position:relative;flex:1;min-height:0;margin-top:44px}}
.fan .fp{{position:absolute;top:0}}
.fan .fp img{{display:block;height:100%}}
.fan .tag{{position:absolute;background:{PAPER};border:2px solid {N700};border-radius:999px;padding:5px 16px;font-size:22px;letter-spacing:.08em;text-transform:uppercase;color:{INK};white-space:nowrap}}
.fan .tag.solid{{background:{CYAN};border:0;border-radius:16px;padding:7px 16px;color:#fff;box-shadow:0 8px 18px rgba(0,0,0,.22)}}
.tt{{position:relative;flex:1;min-height:0;display:flex;gap:200px;justify-content:center;align-items:flex-start;margin-top:50px}}
.tt .fig{{flex:none;width:610px}} .pw{{position:relative;width:100%}} .pw img{{width:100%;display:block}}
.tap{{position:absolute;width:62px;height:62px;margin:-31px 0 0 -31px;border-radius:50%;background:{CYAN};color:#fff;font-size:32px;font-weight:600;
  display:flex;align-items:center;justify-content:center;border:4px solid #fff;box-shadow:0 8px 18px rgba(0,0,0,.28);z-index:3}}
.tap::before,.tap::after{{content:"";position:absolute;border-radius:50%;border:3px solid {CYAN};inset:-16px;opacity:.35}}
.tap::after{{inset:-32px;opacity:.15}}
.mag{{position:absolute;width:330px;border-radius:26px;background:#fff;padding:14px;box-shadow:0 26px 50px rgba(0,0,0,.22),0 4px 10px rgba(0,0,0,.1);z-index:4}}
.mag img{{width:100%;display:block;border-radius:12px}}
.mag .ring{{position:absolute;width:44px;height:44px;margin:-22px 0 0 -22px;border-radius:50%;border:4px solid {CYAN}}}
.land{{position:absolute;width:0;height:0}}
svg.link{{position:absolute;inset:0;width:100%;height:100%;overflow:visible;pointer-events:none;z-index:5;filter:drop-shadow(0 3px 4px rgba(0,0,0,.18))}}
.notes{{display:grid;grid-template-columns:1fr 1fr;gap:26px}}
.scene{{flex:1;min-height:0;margin-top:30px;background:url('scene.png') 50% 100%/contain no-repeat}}   /* 자르지 않는다 -- iPad 세로 전체가 보여야 한다 */
.foot{{font-size:34px;color:{N700};margin-top:40px;letter-spacing:.04em}}
"""

CSS += IPAD_CSS + """
.dev{position:relative;flex:1;min-height:0;margin-top:125px}
.pencil{position:absolute;z-index:3}
.pills{display:flex;flex-wrap:wrap;gap:16px;margin-top:34px}
.pills span{font-size:34px;letter-spacing:.04em;color:#fdfcfa;border:2.5px solid rgba(253,252,250,.75);border-radius:999px;padding:8px 26px 10px;white-space:nowrap}
"""
# iPad 두 대(뒤 표지, 앞 3월 15일) + 펜슬 -- 펜촉 끝이 앞 iPad 화면 아래쪽에 닿는다. 자리는 .dev 기준 px
HERO_DEV = (ipad("_pages/scr_cover.png", 500, 150, 70, -3, 1) + ipad("_pages/scr_d3-15.png", 590, 560, 0, 2, 2)
            + f'<img class="pencil" src="_pages/pencil.png" style="left:{1015 - _tx:.0f}px;top:{830 - _ty:.0f}px">')
# 배지 문구는 대조표를 통과한 주장만: 2026·2027 두 해, 한 해 598쪽, 링크, 스티커 253개
HERO_PILLS = ('<div class="pills"><span>2026 + 2027</span><span>598 pages a year</span>'
              '<span>Hyperlinked</span><span>+ 253 stickers</span></div>')


def img(k, cls="pg"):
    return f'<img class="{cls}" src="_pages/{k}.png">'


def fan(items, h, step, drop, tag="", top=False):
    """페이지를 크게 겹쳐 펼친다 -- 뒤 페이지가 위에 온다. h = 페이지 높이(px), step = 가로 간격, drop = 세로 어긋남"""
    w = round(h * 3 / 4)
    # 아래 배지는 펼침 전체 기준 한 줄(첫 페이지 바닥 위), 위 배지(top=True)는 페이지마다 왼쪽 위 가장자리에 걸친다(본문은 안 가린다, 사용자 확정) -- 계단을 따른다
    out = "".join(f'<div class="fp" style="left:{i * step}px;top:{i * drop}px;height:{h}px;width:{w}px;z-index:{i}">'
                  f'<img src="_pages/{k}.png"></div>' for i, (k, c) in enumerate(items))
    out += "".join(f'<span class="tag {tag}" style="left:{i * step + 18}px;top:{(i * drop + 18) if top else (h - 72)}px;z-index:{len(items) + 1}">{c}</span>'
                   for i, (k, c) in enumerate(items))
    return f'<div class="fan" style="width:{w + step * (len(items) - 1)}px;""">{out}</div>'


# ---- 배경 장식 (사용자 2026-09-27: B2·C·D). 색은 핸드오프·스티커 팔레트만
STK = (ROOT / "output" / "prod3" / "stickers" / "draft-v0.8" / "png").as_uri()
DECO_CSS = """.wrap{z-index:1}.deco{position:absolute;border-radius:50%;filter:blur(26px)}
.pp{position:absolute;filter:drop-shadow(0 14px 18px rgba(40,30,20,.25));z-index:2}
.band{position:absolute;left:-60px;right:-60px;top:-60px;height:1300px;background:#006786;
  -webkit-mask-image:linear-gradient(to bottom,#000 calc(100% - 70px),transparent);mask-image:linear-gradient(to bottom,#000 calc(100% - 70px),transparent)}"""
# 리소 원 두 쌍 -- 판이 어긋난 인쇄처럼 두 색을 조금 비껴 겹친다. 오른쪽 위 = 청록(C 띠 색) + 하늘, 왼쪽 아래 = 분홍 + 노랑
B2 = ('<div class="deco" style="width:900px;height:900px;right:-330px;top:-420px;background:#95c9d9"></div>'
      '<div class="deco" style="width:900px;height:900px;right:-300px;top:-440px;background:#006786;mix-blend-mode:multiply;opacity:.92"></div>'
      '<div class="deco" style="width:720px;height:720px;left:-300px;bottom:-330px;background:#efc9d7"></div>'
      '<div class="deco" style="width:720px;height:720px;left:-270px;bottom:-350px;background:#edbb00;mix-blend-mode:multiply;opacity:.55"></div>')
def _oklab_band(end, span=300, a=(0, 103, 134), b=(239, 235, 230)):
    """청록 -> 바탕을 OKLab 에서 ease(코사인) 12단으로 잇는 세로 그라데이션. 투명 마스크로 빼면 중간이 회청색으로 탁해졌다(v0.30)"""
    import math

    def s2l(c):
        c /= 255
        return c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4

    def l2s(c):
        c = max(0, min(1, c))
        return round(255 * (12.92 * c if c <= .0031308 else 1.055 * c ** (1 / 2.4) - .055))

    def lab(rgb):
        r, g, bb = [s2l(x) for x in rgb]
        l_ = (.4122214708 * r + .5363325363 * g + .0514459929 * bb) ** (1 / 3)
        m_ = (.2119034982 * r + .6806995451 * g + .1073969566 * bb) ** (1 / 3)
        s_ = (.0883024619 * r + .2817188376 * g + .6299787005 * bb) ** (1 / 3)
        return (.2104542553 * l_ + .7936177850 * m_ - .0040720468 * s_, 1.9779984951 * l_ - 2.4285922050 * m_ + .4505937099 * s_,
                .0259040371 * l_ + .7827717662 * m_ - .8086757660 * s_)

    def rgb(L):
        l_, m_, s_ = L[0] + .3963377774 * L[1] + .2158037573 * L[2], L[0] - .1055613458 * L[1] - .0638541728 * L[2], L[0] - .0894841775 * L[1] - 1.2914855480 * L[2]
        l_, m_, s_ = l_ ** 3, m_ ** 3, s_ ** 3
        return tuple(l2s(x) for x in (4.0767416621 * l_ - 3.3077115913 * m_ + .2309699292 * s_, -1.2684380046 * l_ + 2.6097574011 * m_ - .3413193965 * s_,
                                      -.0041960863 * l_ - .7034186147 * m_ + 1.7076147010 * s_))
    A, B = lab(a), lab(b)
    stops = [f"rgb{a} 0px", f"rgb{a} {end - span / 2:.0f}px"]
    for i in range(1, 12):
        t = i / 12
        e = (1 - math.cos(math.pi * t)) / 2
        stops.append(f"rgb{rgb(tuple(A[k] + (B[k] - A[k]) * e for k in range(3)))} {end - span / 2 + span * t:.0f}px")
    stops.append(f"rgb{b} {end + span / 2:.0f}px")
    return f"linear-gradient(to bottom,{','.join(stops)})"


HERO_BAND_END, HERO_BAND_SPAN = 812, 90   # v0.38: 배지 알약 아래(~755px)와 iPad 위(~869px) 가운데 -- 간격이 114px 라 전환 90px (양쪽 12px)
# v0.37: 726, 130 -- v0.37: 띠 끝 = 부제 글자 아래(649px)와 종이 위(802px)의 딱 중간, 전환 661~791px (사용자: 조금 더 부드럽게, 딱 중간)
# 렌더 픽셀에서 잰다 -- 글자·그림 상자에는 줄 간격·종이 그림자 여백이 있어 v0.34~v0.36 의 '가운데'(695)는 눈으로 보면 32px 위였다.
# 전환이 글자·종이에 닿거나(각 8px 안) 가운데에서 6px 넘게 벗어나면 멈춘다. 흐림을 종이에 겹치지 않는다(v0.30 사용자).
# (v0.34~v0.36: 695, 70 -- 상자 기준 / v0.31~v0.33: 1080, 300 -- 띠 끝 = 페이지 위 1/3, 띠가 너무 커서 상품을 가렸다)
C_BAND = ('<style>body{background:#efebe6}.k{color:#95c9d9}h1{color:#fdfcfa;font-size:176px}p.s{color:#d7e8ee}'
          '.band{-webkit-mask-image:none;mask-image:none;top:0;left:0;right:0;height:2000px;background:' + _oklab_band(HERO_BAND_END, HERO_BAND_SPAN) + '}</style>'
          '<div class="band"></div>')


def props(*items):
    """스티커 소품 -- 네 모서리 자리 (왼쪽 위 알약, 오른쪽 위 원, 왼쪽 아래 알약, 오른쪽 아래 네모). 글자 안전 영역 밖"""
    slots = [(60, 110, 80, -10), (1650, 55, 195, 12),   # 오른쪽 위: v0.34 까지 (1600, 150, 230) -- 04 제목과 겹쳤다
             (40, 1800, 90, -8), (1760, 1560, 190, 9)]
    return "".join(f'<img class="pp" src="{STK}/{r}" style="left:{x}px;top:{y}px;height:{h}px;transform:rotate({a}deg)">'
                   for r, (x, y, h, a) in zip(items, slots) if r)


SET1 = props("Small-wins/tiny-step_blush.png", "Experiments/helped_paper.png", "Energy/recharge_deep.png", "Brain-weather/great_ink.png")
SET2 = props("Small-wins/did-the-thing_paper.png", "Experiments/sort-of_stone.png", "Experiments/in-my-playbook_deep.png", "Brain-weather/good_mist.png")
DECO = {"01_hero": C_BAND + SET1, "02_experiments": B2 + SET2, "03_time_links": B2 + SET1, "04_sos": B2 + SET2, "05_inside": B2 + SET1,
        "06_files": B2 + SET2, "07_stickers": B2, "08_month": B2 + SET1, "09_december": B2 + SET2, "10_two_taps": B2 + SET1}

SHOTS = {
    "01_hero": f"""<div class="k">Dated ADHD planner · 2026 &amp; 2027</div>
      <h1>The ADHD Year</h1>
      <p class="s">One small experiment a week. By December, a user manual for your own brain.</p>
      {HERO_PILLS}<div class="dev">{HERO_DEV}</div>""",
    "02_experiments": f"""<div class="k">52 experiments</div>
      <h1>One strategy a week.<br>Keep what works.</h1>
      <p class="s">Printed on that week's page. Mark it on Friday. Keep or drop it each quarter.</p>
      <div class="row">{img("experiments")}{img("w12")}</div>""",
    "03_time_links": f"""<div class="k">Time links</div>
      <h1>Today links to tomorrow.</h1>
      <p class="s">Write a note to future you – it links to the day it arrives, 30 days later.</p>
      <div class="row">{img("d3-15", "pg t")}{img("d3-16", "pg u")}</div>""",
    "04_sos": f"""<div class="k">SOS page</div>
      <h1>Pick what is happening.<br>Tap straight to the tool.</h1>
      <p class="s">"I can't start" · "I'm overwhelmed" · "Someone's words stung"</p>
      <div class="row">{img("sos")}{img("rsd")}</div>""",
    "05_inside": f"""<div class="k">What's inside · 598 pages a year</div>
      <h1>Year, months, weeks, every day – and 45 tools.</h1>
      <div class="grid">{"".join(img(k, "") for k in ["year", "m3", "w12", "d3-15", "admin", "rsd", "budget", "dopamine"])}</div>""",
    "06_files": f"""<div class="k">What you get</div>
      <h1>4 PDFs.<br>Pick your start day.</h1>
      <div class="list"><span class="pill">2026 · Monday start</span><span class="pill">2026 · Sunday start</span><br>
        <span class="pill">2027 · Monday start</span><span class="pill">2027 · Sunday start</span></div>
      <div class="list"><b>Ten tabs</b> on every page · every day <b>two taps</b> away<br>
        For GoodNotes, Notability and other PDF note apps · shaped for a tablet (3:4)<br>
        <b>+ Sticker kit</b> (253 stickers) and a setup guide</div>
      <div class="grid" style="margin-top:70px;gap:56px">{"".join(
          f'<div class="cv">{img(f"cover-{y}-{w}", "")}<div class="bdg {w}"><b>{y}</b><span>{"Monday" if w == "mon" else "Sunday"} start</span></div></div>'
          for y in ("2026", "2027") for w in ("mon", "sun"))}</div>
      <div class="foot">Digital download – nothing is shipped.</div>""",
    "07_stickers": f"""<div class="k">Sticker kit · 253 stickers</div>
      <h1>Stickers made<br>for these pages.</h1>
      <p class="s">Mark Friday's verdict, a low-battery day, a good-brain day.</p>
      <div class="scene"></div>""",
    "08_month": f"""<div class="k">Every month · four pages that work together</div>
      <h1>Plan it. Track it.<br>Look back.</h1>
      <p class="s">A calendar, a plan, a brain weather tracker and a review – linked to each other.</p>
      {fan([("m3", "Calendar"), ("mp3", "Plan"), ("bw3", "Brain weather"), ("mr3", "Review")], 870, 259, 18, "solid", top=True)}""",
    "09_december": f"""<div class="k">By December</div>
      <h1>A user manual for<br>your own brain.</h1>
      <p class="s">Keep the experiments that worked. Notes you wrote to future you wait in a year-end mailbox.</p>
      {fan([("playbook", "My ADHD playbook"), ("yearreview", "Year review"), ("mailbox", "Year-end mailbox")], 880, 372, 22)}""",
    "10_two_taps": f"""<div class="k">Hyperlinked · ten tabs on every page</div>
      <h1>Any day of the year,<br>two taps away.</h1>
      <div class="steps"><div class="step"><i>1</i>Tap YEAR</div><div class="step"><i>2</i>Tap the date</div></div>
      <div class="tt" id="tt">
        <div class="fig"><div class="pw">{img("year", "")}<span class="tap" id="t1" style="left:95.1%;top:28.2%">1</span>
          <span class="tap" id="t2" style="left:51%;top:26.7%">2</span></div><div class="cap">Year at a glance</div></div>
        <div class="fig"><div class="pw">{img("d3-15", "")}<span class="land" id="land" style="left:9%;top:11.9%"></span></div><div class="cap">That day's page</div></div>
        <div class="mag" id="mag" style="left:440px;top:370px;transform:rotate(-3deg)"><img src="_pages/mag_march.png"><span class="ring" style="left:calc(14px + 302px * {(290.1 + 297.3) / 2 - 282} / 112);top:calc(14px + 302px * 88 / 112 * {(200.8 + 210.0) / 2 - 150} / 88)"></span></div>
        <svg class="link" id="link"></svg>
      </div>
      <script>
      window.addEventListener('load', () => {{      // 그림이 다 들어온 뒤에 잰다 (v0.22 는 먼저 재서 선이 엉뚱한 곳에 그려졌다)
        const R = e => (typeof e === 'string' ? document.getElementById(e) : e).getBoundingClientRect();
        const T = R('tt'), m = R('mag'), rg = R(document.querySelector('#mag .ring')), ld = R('land'), t2 = R('t2');
        const X = v => v - T.left, Y = v => v - T.top;
        const rx = X((rg.left + rg.right) / 2), ry = Y((rg.top + rg.bottom) / 2);
        const qx = X((t2.left + t2.right) / 2), qy = Y(t2.bottom) + 18;           // 2 표시 바로 아래
        const sx = X(m.right) - 8, sy = ry;                                        // 확대 카드 오른쪽, 15 높이
        const ex = X(ld.left) - 16, ey = Y(ld.top);                                // 그날 페이지 제목 왼쪽
        const col = '{CYAN}';
        document.getElementById('link').innerHTML =
          `<path d="M${{qx}} ${{qy}} Q ${{qx - 10}} ${{(qy + Y(m.top)) / 2}} ${{rx}} ${{Y(m.top) + 6}}" fill="none" stroke="${{col}}" stroke-width="4" stroke-dasharray="1 11" stroke-linecap="round"/>` +
          `<path d="M${{sx}} ${{sy}} C ${{sx + 170}} ${{sy}}, ${{ex - 190}} ${{ey}}, ${{ex}} ${{ey}}" fill="none" stroke="${{col}}" stroke-width="6" stroke-linecap="round"/>` +
          `<path d="M${{ex - 22}} ${{ey - 15}} L ${{ex}} ${{ey}} L ${{ex - 22}} ${{ey + 15}}" fill="none" stroke="${{col}}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>`;
      }});
      </script>""",
}

MIN_PX = {".k": 40, "h1": 150, "p.s": 48}   # v0.32: 폰 Etsy 앱(상세 폭 ~390pt, 목록 ~200pt)에서 읽히는 하한 -- v0.31(104px)은 너무 작았다
# 글자 크기 하한 + 마지막 줄 한 단어(외톨이) -- 단어마다 Range 로 줄(top)을 모아 센다
CHECK_JS = """(min) => {
  const bad = [];
  for (const [sel, px] of Object.entries(min))
    for (const e of document.querySelectorAll(sel))
      if (parseFloat(getComputedStyle(e).fontSize) < px) bad.push(`${sel} ${getComputedStyle(e).fontSize} < ${px}px`);
  for (const e of document.querySelectorAll('h1,p.s')) {
    const tops = [];
    const w = document.createTreeWalker(e, NodeFilter.SHOW_TEXT);
    for (let n; (n = w.nextNode());)
      for (const m of n.textContent.matchAll(/\\S+/g)) {
        const r = document.createRange(); r.setStart(n, m.index); r.setEnd(n, m.index + m[0].length);
        tops.push(Math.round(r.getClientRects()[0].top));
      }
    const lines = [...new Set(tops)];
    if (lines.length > 1 && tops.filter(t => t === lines[lines.length - 1]).length === 1)
      bad.push(`외톨이 단어: ${e.textContent.trim().slice(-30)}`);
  }
  return bad;
}"""

def hero_ink(lum):
    """01 렌더(회색조 배열)에서 청록 띠 위 마지막 글자(부제·배지 알약 테두리)의 아래 끝(px) -- 청록 줄(가운데값 < 130)의 밝은 점"""
    return max(y for y in range(480, 1000) if np.median(lum[y, 260:1300]) < 130 and (lum[y, 260:1300] > 170).any())


# 01 기기(iPad·펜슬)가 검색 자르기 안인가 -- 폰 검색은 4:5 로 양옆(가로 200-1800 만), PC 검색은 4:3 으로 위아래(세로 250-1750 만).
# 스티커는 잘려도 된다(사용자). 펜슬은 소품이라 가로만 본다. v0.38 시안 2(iPad 아래 1832px)가 걸린다.
DEVICE_JS = """() => {
  const bad = [];
  for (const e of document.querySelectorAll('.ipad, .pencil')) {
    const r = e.getBoundingClientRect(), dev = e.classList.contains('ipad');
    if (r.left < 200 || r.right > 1800 || (dev && (r.top < 250 || r.bottom > 1750))) bad.push(`${e.className} ${[r.left|0, r.top|0, r.right|0, r.bottom|0]}`);
  }
  return bad;
}"""


# 글자 줄(줄 상자)과 스티커 소품(.pp) 사이 16px 이상 -- v0.34 에서 04 제목 끝이 오른쪽 위 스티커와 겹쳤다
PROP_GAP_JS = """() => {
  const pp = [...document.querySelectorAll('.pp')].map(e => e.getBoundingClientRect()), bad = [];
  for (const e of document.querySelectorAll('.k,h1,p.s,.pills span')) {
    const w = document.createTreeWalker(e, NodeFilter.SHOW_TEXT);
    for (let n; (n = w.nextNode());) {
      const r = document.createRange(); r.selectNodeContents(n);
      for (const t of r.getClientRects()) for (const p of pp) {
        const gap = Math.max(p.left - t.right, t.left - p.right, p.top - t.bottom, t.top - p.bottom);
        if (gap < 16) bad.push(`${n.textContent.trim().slice(0, 24)} ${Math.round(gap)}px`);
      }
    }
  }
  return bad;
}"""

from playwright.sync_api import sync_playwright  # noqa: E402
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))   # scripts/ -- chrome_auto
from chrome_auto import launch  # noqa: E402

with sync_playwright() as p:
    br = launch(p)   # chrome_auto: 새 Chrome 마다 Windows 로그온 실패가 쌓여 계정이 잠겼다(2026-09-28)
    pg = br.new_page(viewport={"width": 2000, "height": 2000})
    for name, body in SHOTS.items():
        f = OUT / f"{name}.html"
        f.write_text(f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}{DECO_CSS}</style></head>'
                     f'<body>{DECO.get(name, "")}<div class="wrap">{body}</div></body></html>', encoding="utf-8")
        pg.goto(f.as_uri())
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(500)
        out_of = pg.evaluate("""() => [...document.querySelectorAll('.k,h1,p.s,.pill,.pills span,.list,.foot,.bdg,.cap,.step,.arrow,.tag,.fp')].map(e => {
            const r = e.getBoundingClientRect();
            return (r.left < 260 || r.right > 1740 || r.top < 250 || r.bottom > 1750) ? e.textContent.trim().slice(0, 30) + ' ' + JSON.stringify([r.left|0, r.top|0, r.right|0, r.bottom|0]) : null;
        }).filter(Boolean)""")
        tags = pg.evaluate("""() => [...document.querySelectorAll('.fan .tag')].map(e => { const r = e.getBoundingClientRect(); return [r.left, r.right]; })""")
        close = [i for i in range(1, len(tags)) if tags[i][0] - tags[i - 1][1] < 16]
        if close:
            raise SystemExit(f"{name}: 배지 사이가 16px 보다 좁다 {close}")
        if out_of:
            raise SystemExit(f"{name}: 안전 영역(가로 260-1740, 세로 250-1750) 밖 글자 {out_of}")
        near = pg.evaluate(PROP_GAP_JS)
        if near:
            raise SystemExit(f"{name}: 글자와 스티커 소품 사이가 16px 보다 좁다 {near}")
        small = pg.evaluate(CHECK_JS, MIN_PX)
        if small:
            raise SystemExit(f"{name}: 제목·부제 {small}")
        if name == "01_hero":   # 띠 전환이 마지막 글자와 iPad 사이 딱 중간인가 -- 글자는 렌더 픽셀, iPad 는 테두리 상자 (v0.37·v0.38 사용자)
            import io
            from PIL import Image
            bad = pg.evaluate(DEVICE_JS)
            if bad:
                raise SystemExit(f"01: iPad·펜슬이 검색 자르기 밖 (iPad 가로 200-1800·세로 250-1750, 펜슬 가로) {bad}")
            shot = pg.screenshot()
            ink = hero_ink(np.asarray(Image.open(io.BytesIO(shot)).convert("L")).astype(int))
            paper = round(pg.evaluate("() => Math.min(...[...document.querySelectorAll('.ipad')].map(e => e.getBoundingClientRect().top))"))
            b0, b1, mid = HERO_BAND_END - HERO_BAND_SPAN / 2, HERO_BAND_END + HERO_BAND_SPAN / 2, (ink + paper) / 2
            if not (ink + 8 <= b0 and b1 <= paper - 8 and abs(HERO_BAND_END - mid) <= 6):
                raise SystemExit(f"01: 띠 전환 {b0:.0f}~{b1:.0f}px (끝 {HERO_BAND_END}) -- 글자 아래 {ink} · iPad 위 {paper} · 가운데 {mid:.0f}")
        pg.screenshot(path=str(OUT / f"{name}.png"))
        print(OUT / f"{name}.png")
    br.close()
