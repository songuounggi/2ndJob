# -*- coding: utf-8 -*-
"""Lifted Paper 에디션 PDF 빌드 (디자인 핸드오프 README 대로). Prod 3 방 소유.

    python scripts/p3/editions_build.py            # 4개 PDF -> output/editions/

레퍼런스 `design/Admin Tables v17.dc.html` 을 Playwright(설치된 Chrome)로 연 뒤,
페이지마다 DOM 을 고쳐서 떼어낸다:

  - 종이 효과 레이어(box-shadow 그림자, filter:blur 모서리 그림자, 하이라이트 그라데이션,
    종이색 면)를 버리고, 페이지 밑에 배경 이미지 한 장(Sheet A/B)을 깐다
  - 잉크의 CSS 그라데이션(괘선·세로선·점지·하프톤)을 명시적 SVG 벡터로 바꾼다.
    패턴 타일은 쓰지 않는다 -- GoodNotes 가 타일 배율을 잘못 읽은 적이 있다(상품 1, 2026-09-24)
  - 탭 레일은 README 의 탭 세트로 새로 만든다(페이지 없는 탭 -> 그 에디션 Home)
  - 캡션(Sheet A · Daily 등)은 떼어낸 페이지 밖이라 따라오지 않는다

그 다음 에디션마다 HTML 한 장 -> page.pdf -> dedupe(같은 스트림 합치기).
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]      # scripts/p3/ -> 저장소
HAND = ROOT / "ADHD Planner 디자인 컨셉_v0.1" / "design_handoff_adhd_planner_pdf"
REF = HAND / "design" / "Admin Tables v17.dc.html"
CSS = next((HAND / "design" / "_ds").glob("*/styles.css"))
OUT = ROOT / "output" / "editions"
SRC = ROOT / "src" / "editions"

# 에디션: (파일명, 탭 세트[(라벨, 키)], 페이지[(새 id, 레퍼런스 id, 활성 탭 라벨)])
# 키가 None 이면 페이지가 없는 탭 -> Home 으로 (README "Tabs")
EDITIONS = {
    "focus": ("ADHD-Planner-Focus-Edition", [
        ("Home", "pg-fe-home"), ("Guide", "pg-fe-guide"), ("Dump", "pg-fe-dump"), ("Day", "pg-fe-day"),
        ("Week", "pg-fe-week"), ("Month", "pg-fe-month"), ("Track", "pg-fe-track"),
        ("Habits", "pg-fe-habits"), ("Menu", "pg-fe-menu")], [
        ("pg-fe-home", "pg-fe-home", "Home"), ("pg-fe-guide", "pg-fe-guide", "Guide"),
        ("pg-fe-dump", "pg-fe-dump", "Dump"), ("pg-fe-day", "pg-fe-day", "Day"),
        ("pg-fe-week", "pg-fe-week", "Week"), ("pg-fe-month", "pg-fe-month", "Month"),
        ("pg-fe-track", "pg-fe-track", "Track"), ("pg-fe-habits", "pg-fe-habits", "Habits"),
        ("pg-fe-menu", "pg-fe-menu", "Menu")]),
    "admin": ("ADHD-Planner-Admin-Edition", [
        ("Home", "pg-ae-home"), ("Bills", "pg-ae-bills"), ("Subs", "pg-ae-subs"),
        ("Projects", "pg-ae-projects"), ("Tables", "pg-ae-tables")], [
        ("pg-ae-home", "pg-ae-home", "Home"),
        ("pg-ae-bills", "7b", "Bills"),            # README: Bills 는 7b
        ("pg-ae-subs", "pg-ae-subs", "Subs"),
        ("pg-ae-projects", "pg-ae-projects", "Projects"),
        ("pg-ae-tables", "7f", "Tables")]),        # README: 7f 를 범용 Table 페이지로
    "evening": ("ADHD-Planner-Evening-Edition", [
        ("Home", "pg-ee-home"), ("Shutdown", "pg-ee-shutdown"), ("Sleep", "pg-ee-sleep"),
        ("Wind-down", None), ("Notes", None)], [
        ("pg-ee-home", "pg-ee-home", "Home"), ("pg-ee-shutdown", "pg-ee-shutdown", "Shutdown"),
        ("pg-ee-sleep", "pg-ee-sleep", "Sleep")]),
}
# Directions sampler: 방향(3a/3b/3c)마다 표지+일간. 탭 Home/Day 는 그 방향의 두 장, 나머지는 그 방향 표지로.
DD_TABS = ["Home", "Dump", "Day", "Week", "Month", "Habits", "Meds", "Menu"]
EDITIONS["directions"] = ("ADHD-Planner-Directions-Sampler", None, [
    (f"pg-dd-{d}-{k}", f"pg-dd-{d}-{k}", "Home" if k == "home" else "Day")
    for d in ("3a", "3b", "3c") for k in ("home", "day")])
COVER_OR_DIVIDER = {"pg-fe-home", "pg-fe-track", "pg-ae-home", "pg-ee-home",
                    "pg-dd-3a-home", "pg-dd-3b-home", "pg-dd-3c-home"}


def tabs_for(edition, new_id):
    if edition == "directions":
        d = new_id.split("-")[2]
        home, day = f"pg-dd-{d}-home", f"pg-dd-{d}-day"
        return [(t, day if t == "Day" else home) for t in DD_TABS]
    _, tabs, _ = EDITIONS[edition]
    home = tabs[0][1]
    return [(t, k or home) for t, k in tabs]


STATIC_FONT_UA = "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko"

TRANSFORM_JS = r"""
({srcId, tabs, active, SHADOW_M}) => {
  const rep = {grad: 0, unconverted: [], textInConverted: 0, sheet: null};
  const wrap = document.getElementById(srcId);
  const cap = wrap.children[1] ? wrap.children[1].textContent : '';
  rep.sheet = /Sheet B/.test(cap) ? 'B' : 'A';
  rep.caption = cap.trim().replace(/\s+/g, ' ');
  const pageDiv = wrap.children[0];
  const sheet = pageDiv.children[0];
  const kids = [...sheet.children];
  const ink = kids.find(k => (k.getAttribute('style') || '').includes('padding: 40px 44px 30px'));
  if (!ink) throw new Error('ink not found in ' + srcId);
  kids.forEach(k => { if (k !== ink) k.remove(); });   // 탭, 그림자, 블러, 종이면

  const probe = document.createElement('span'); document.body.appendChild(probe);
  const col = c => { probe.style.color = ''; probe.style.color = c.trim(); return getComputedStyle(probe).color; };
  const NS = 'http://www.w3.org/2000/svg';
  const svgIn = (el, w, h) => {
    const cs = getComputedStyle(el);
    if (cs.position === 'static') el.style.position = 'relative';
    const s = document.createElementNS(NS, 'svg');
    s.setAttribute('width', w); s.setAttribute('height', h);
    s.setAttribute('viewBox', `0 0 ${w} ${h}`);
    s.style.cssText = 'position:absolute;left:0;top:0;pointer-events:none;overflow:hidden';
    el.insertBefore(s, el.firstChild);
    if (el.textContent.trim()) rep.textInConverted++;
    return s;
  };
  const path = (s, d, fill) => {
    const p = document.createElementNS(NS, 'path'); p.setAttribute('d', d); p.style.fill = fill; s.appendChild(p);
  };

  ink.querySelectorAll('[style]').forEach(el => {
    const st = el.getAttribute('style');
    if (!/gradient\(/.test(st)) return;
    const r = el.getBoundingClientRect(), W = r.width, H = r.height;
    let m;
    if ((m = st.match(/repeating-linear-gradient\(to bottom,\s*transparent 0 ([\d.]+)px,\s*(.+?) ([\d.]+)px ([\d.]+)px\)/))) {
      // 괘선: A 부터 B 까지 한 줄, 주기 B
      const a = +m[1], b = +m[4], c = col(m[2]); let d = '';
      for (let y = a; y < H - 0.01; y += b) d += `M0 ${y}H${W}V${Math.min(y + (b - a), H)}H0Z`;
      el.style.background = 'none'; path(svgIn(el, W, H), d, c); rep.grad++;
    } else if ((m = st.match(/linear-gradient\(to right,\s*transparent calc\(([\d.]+)% - \.5px\),\s*(.+?) calc\(/))) {
      // 세로선 하나 (X%)
      const x = W * (+m[1]) / 100 - 0.5, c = col(m[2]);
      el.style.background = 'none'; path(svgIn(el, W, H), `M${x} 0H${x + 1}V${H}H${x}Z`, c); rep.grad++;
    } else if ((m = st.match(/background-image:\s*radial-gradient\(circle,\s*(.+?) ([\d.]+)(px|%),\s*transparent ([\d.]+)(px|%)\);\s*background-size:\s*([\d.]+)px ([\d.]+)px(?:;\s*background-position:\s*([-\d.]+)px ([-\d.]+)px)?/))) {
      // 점지·하프톤: 타일(S) 중심마다 점. % 반경은 farthest-corner(= S/2*sqrt2) 기준
      const c = col(m[1]), S = +m[6], S2 = +m[7], ox = +(m[8] || 0), oy = +(m[9] || 0);
      const rad = v => m[3] === 'px' ? v : v / 100 * Math.hypot(S / 2, S2 / 2);
      const R = (rad(+m[2]) + (m[5] === 'px' ? +m[4] : +m[4] / 100 * Math.hypot(S / 2, S2 / 2))) / 2;
      let d = '';
      for (let y = oy % S2 - S2; y < H + S2; y += S2)
        for (let x = ox % S - S; x < W + S; x += S) {
          const cx = x + S / 2, cy = y + S2 / 2;
          if (cx + R < 0 || cy + R < 0 || cx - R > W || cy - R > H) continue;
          d += `M${(cx - R).toFixed(2)} ${cy.toFixed(2)}a${R.toFixed(2)} ${R.toFixed(2)} 0 1 0 ${(2 * R).toFixed(2)} 0a${R.toFixed(2)} ${R.toFixed(2)} 0 1 0 ${(-2 * R).toFixed(2)} 0`;
        }
      el.style.backgroundImage = 'none';
      if (getComputedStyle(el).borderRadius !== '0px') el.style.overflow = 'hidden';
      path(svgIn(el, W, H), d, c); rep.grad++;
    } else {
      rep.unconverted.push(st.slice(0, 120));
    }
  });

  // inset box-shadow 선 -> border / outline (README "Replace effects").
  // PDF 에서는 칸마다 클립 + even-odd 채우기가 되어 표 페이지(7f) 렌더가 267ms 였다.
  // 모양이 1px 이라도 달라지면 되돌린다 -- 자기 상자와 부모 상자의 크기·위치를 전후 비교.
  rep.bs = {converted: 0, dropped: 0, reverted: 0, kept: 0};
  const splitTop = v => { const out = []; let d = 0, cur = '';
    for (const ch of v) { if (ch === '(') d++; if (ch === ')') d--; if (ch === ',' && !d) { out.push(cur.trim()); cur = ''; } else cur += ch; }
    if (cur.trim()) out.push(cur.trim()); return out; };
  const box = e => { const r = e.getBoundingClientRect(); return [r.x, r.y, r.width, r.height].map(v => Math.round(v * 100)).join(','); };
  ink.querySelectorAll('[style*="box-shadow"]').forEach(el => {
    const cs = getComputedStyle(el);
    if (cs.boxShadow === 'none') return;
    const parts = splitTop(cs.boxShadow);
    const ops = []; let ok = true;
    for (const part of parts) {
      const m = part.match(/^(.*?\))\s+(-?[\d.]+)px\s+(-?[\d.]+)px\s+([\d.]+)px\s+(-?[\d.]+)px\s+inset$/);
      if (!m) { ok = false; break; }
      const [, c, x, y, blur, spr] = [m[0], m[1], +m[2], +m[3], +m[4], +m[5]];
      if (blur !== 0) { ok = false; break; }
      if (/rgba\(0, 0, 0, 0\)|transparent/.test(c) || /\/ 0\)$/.test(c)) { ops.push(['drop']); continue; }
      if (x === 0 && y === 0 && spr > 0) ops.push(['outline', spr, c]);
      else if (spr === 0 && (x === 0) !== (y === 0))
        ops.push(['side', x > 0 ? 'Left' : x < 0 ? 'Right' : y > 0 ? 'Top' : 'Bottom', Math.abs(x || y), c]);
      else { ok = false; break; }
    }
    if (!ok || ops.filter(o => o[0] === 'outline').length > 1) { rep.bs.kept++; return; }
    const before = [box(el), el.parentElement ? box(el.parentElement) : ''];
    const saved = el.getAttribute('style');
    el.style.boxShadow = 'none';
    for (const o of ops) {
      if (o[0] === 'outline') { el.style.outline = `${o[1]}px solid ${o[2]}`; el.style.outlineOffset = `${-o[1]}px`; }
      if (o[0] === 'side') {
        const [, side, w, c] = o;
        const pad = parseFloat(cs['padding' + side]) || 0;
        const bw = parseFloat(cs['border' + side + 'Width']) || 0;
        if (bw) { ok = false; break; }                       // 이미 테두리가 있으면 건드리지 않는다
        el.style['border' + side] = `${w}px solid ${c}`;
        if (pad >= w) el.style['padding' + side] = `${pad - w}px`;
      }
    }
    const after = [box(el), el.parentElement ? box(el.parentElement) : ''];
    if (!ok || before.join('|') !== after.join('|')) { el.setAttribute('style', saved); rep.bs.reverted++; return; }
    if (ops.every(o => o[0] === 'drop')) rep.bs.dropped++; else rep.bs.converted++;
  });

  // Source Serif 4 에 없는 글자 -> 벡터. 없으면 Chrome 이 시스템 폰트(맑은 고딕)로 채운다.
  // Focus 일간 "low → high" 의 → 하나가 그랬다(2026-09-25).
  const ARROW = '<svg viewBox="0 0 14 8" style="width:0.95em;height:0.55em;vertical-align:0.12em;overflow:visible" aria-hidden="true"><path d="M0.5 4H12.5M9.5 1l3 3-3 3" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  const walker = document.createTreeWalker(ink, NodeFilter.SHOW_TEXT);
  const hits = [];
  while (walker.nextNode()) if (walker.currentNode.nodeValue.includes('→')) hits.push(walker.currentNode);
  for (const t of hits) {
    const span = document.createElement('span');
    span.innerHTML = t.nodeValue.split('→').map(x => x.replace(/&/g, '&amp;').replace(/</g, '&lt;')).join(ARROW);
    t.replaceWith(...span.childNodes);
    rep.arrows = (rep.arrows || 0) + 1;
  }

  // 탭 레일 (README "Tabs"): 시트 오른쪽 가장자리, top 64, 간격 6, 폭 26(활성 30) x 높이 70(6자 넘으면 84).
  // 원래는 탭이 시트 밑으로 4px 들어가 종이면에 가려진다. 종이면을 배경 이미지로 바꿨으니
  // 겹치는 4px 를 빼고(보이는 부분은 같다) 그림자도 시트 쪽으로 번지지 않게 자른다.
  const nav = document.createElement('nav');
  nav.style.cssText = 'position:absolute;left:100%;top:64px;display:flex;flex-direction:column;gap:6px;z-index:-1;clip-path:inset(-20px -40px -20px 0)';
  for (const [label, href] of tabs) {
    const on = label === active;
    const a = document.createElement('a');
    a.href = '#' + href; a.textContent = label;
    const w = on ? 26 : 22, h = label.length > 6 ? 84 : 70, M = SHADOW_M;
    a.style.cssText = `position:relative;display:flex;align-items:center;justify-content:center;width:${w}px;height:${h}px;box-sizing:border-box;writing-mode:vertical-rl;text-decoration:none;font-size:10px;letter-spacing:0.12em;text-transform:uppercase;background:${on ? 'var(--color-accent)' : 'var(--color-neutral-100)'};color:${on ? 'var(--color-bg)' : 'var(--color-neutral-800)'};border-radius:0 var(--radius-md) var(--radius-md) 0`;
    // 블러 box-shadow 는 PDF 에서 소프트 마스크가 된다(페이지당 10개) -> GoodNotes 바둑판.
    // 같은 그림자를 PNG 로 한 번 구워 모든 탭이 공유한다(상품 1 v8.19 와 같은 해법).
    const img = document.createElement('img');
    img.src = `bg/tabshadow-${w}x${h}.png`; img.alt = '';
    img.style.cssText = `position:absolute;left:${-M}px;top:${-M}px;width:${w + 2 * M}px;height:${h + 2 * M}px;z-index:-1;pointer-events:none`;
    a.appendChild(img);
    nav.appendChild(a);
  }
  sheet.insertBefore(nav, sheet.firstChild);
  probe.remove();
  pageDiv.style.background = 'none';
  return {html: pageDiv.outerHTML, rep};
}
"""


SHADOW_M = 12
TAB_SHADOW = ("0 1px 2px color-mix(in srgb,#2d2b2b 8%,transparent),"
              "0 3px 8px color-mix(in srgb,#2d2b2b 7%,transparent)")   # README "Tabs" 그대로


def bake_tab_shadows(br):
    """탭 크기 4종(폭 22/26 x 높이 70/84)의 그림자만 투명 PNG 로 (2x). 탭 몸통은 투명이라
    box-shadow 의 바깥 그림자만 찍힌다."""
    ctx = br.new_context(device_scale_factor=2)
    pg = ctx.new_page()
    for w in (22, 26):
        for h in (70, 84):
            M = SHADOW_M
            pg.set_content(f'<html><body style="margin:0;background:transparent">'
                           f'<div style="position:absolute;left:{M}px;top:{M}px;width:{w}px;height:{h}px;'
                           f'border-radius:0 2px 2px 0;box-shadow:{TAB_SHADOW}"></div></body></html>')
            pg.screenshot(path=str(SRC / "bg" / f"tabshadow-{w}x{h}.png"), omit_background=True,
                          clip={"x": 0, "y": 0, "width": w + 2 * M, "height": h + 2 * M})
    ctx.close()


# 종이+탭 묶음을 페이지 가운데로 (2026-09-25 사용자: "탭이 우측에 쏠려 누르기 어렵다").
# 레퍼런스는 종이(692)만 가운데라 탭 오른쪽 여백이 12px 였다. 묶음 = 종이 692 + 활성 탭 26 = 718
# -> 좌우 25px. 종이·탭·배경 이미지를 함께 왼쪽으로 13px 옮기고, 오른쪽에 드러나는 띠는 책상색.
TAB_MAX = 26
SHIFT = TAB_MAX // 2          # 13
DESK = "#eae7e7"


def shift_background(src_png, dst_jpg):
    """배경을 SHIFT 만큼 왼쪽으로 옮긴 새 배경(2x). 오른쪽에 드러나는 띠는 맨 오른쪽 열을 늘려 채운다.

    처음엔 이미지를 옮기고 빈 띠를 책상색으로 칠했는데, 오른쪽 아래는 들린 모서리 그림자가
    페이지 끝까지 깔려 있어서 x=755px 에서 밝기가 5~6 단계 끊겼다(세로 이음매).
    PNG 마스터에서 만들어 JPEG 을 두 번 압축하지 않는다. 품질은 원본처럼 q90."""
    from PIL import Image
    im = Image.open(src_png).convert("RGB")
    w, h = im.size
    d = SHIFT * 2                                   # 2x 이미지
    out = Image.new("RGB", (w, h))
    out.paste(im.crop((d, 0, w, h)), (0, 0))
    edge = im.crop((w - 1, 0, w, h)).resize((d, h))
    out.paste(edge, (w - d, 0))
    out.save(dst_jpg, quality=90, optimize=True)


def page_html(inner, sheet, new_id):
    bg = f"bg/sheet-{sheet.lower()}-2x.jpg"
    # 레퍼런스의 페이지 div 는 768x1024 relative. 섹션이 그 자리를 대신한다.
    inner = re.sub(r'^<div[^>]*>', f'<div style="position:absolute;top:0;bottom:0;left:{-SHIFT}px;width:768px">',
                   inner, count=1)
    inner = re.sub(r'\sdata-dc-tpl="\d+"', "", inner)
    return (f'<section class="page" id="{new_id}">'
            f'<img class="bg" src="{bg}" alt="">{inner}</section>')


DOC = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>{title}</title>
<link rel="stylesheet" href="styles.css">
<style>
@page{{size:768px 1024px;margin:0}}
html,body{{margin:0;padding:0;background:none}}
.page{{position:relative;width:768px;height:1024px;overflow:hidden;break-after:page;background:{desk}}}
.page:last-child{{break-after:auto}}
.page>img.bg{{position:absolute;inset:0;width:768px;height:1024px;display:block}}
a{{color:inherit}}
</style></head><body>{body}</body></html>"""


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    SRC.mkdir(parents=True, exist_ok=True)
    (SRC / "bg").mkdir(exist_ok=True)
    for s in ("a", "b"):
        shift_background(HAND / "backgrounds" / f"sheet-{s}-2x.png", SRC / "bg" / f"sheet-{s}-2x.jpg")
    shutil.copy(CSS, SRC / "styles.css")
    report = {}
    with sync_playwright() as p:
        br = p.chromium.launch(channel="chrome")
        bake_tab_shadows(br)
        ref = br.new_page(viewport={"width": 1600, "height": 1200})
        ref.goto(REF.as_uri())
        ref.wait_for_timeout(3000)
        ref.evaluate("document.fonts.ready")
        for ed, (fname, _, pages) in EDITIONS.items():
            body, reps = [], {}
            for new_id, src_id, active in pages:
                ref.goto(REF.as_uri())              # 페이지마다 새로 -- 앞 페이지의 DOM 수정이 남지 않게
                ref.wait_for_timeout(1500)
                res = ref.evaluate(TRANSFORM_JS, {"srcId": src_id, "tabs": tabs_for(ed, new_id), "active": active, "SHADOW_M": SHADOW_M})
                body.append(page_html(res["html"], res["rep"]["sheet"], new_id))
                reps[new_id] = res["rep"]
            html_path = SRC / f"{fname}.html"
            html_path.write_text(DOC.format(title=fname.replace("-", " "), body="".join(body), desk=DESK), encoding="utf-8")
            # Google Fonts 는 최신 브라우저에 가변 폰트(VF)를 준다. Chrome 은 VF 의 400/600 인스턴스를
            # PDF 에 Type3(글자를 도형으로)으로 넣어서, pdffonts 에 Source Serif 4 로 안 잡힌다.
            # 옛 브라우저라고 하면 두께별 정적 WOFF 를 준다 -> Type0 서브셋으로 들어간다.
            ctx = br.new_context(user_agent=STATIC_FONT_UA)
            pg = ctx.new_page()
            pg.goto(html_path.as_uri())
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(500)
            raw = OUT / f"{fname}.raw.pdf"
            pg.pdf(path=str(raw), width="768px", height="1024px", print_background=True,
                   prefer_css_page_size=False, margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
            ctx.close()
            final = OUT / f"{fname}.pdf"
            subprocess.run([sys.executable, str(ROOT / "scripts" / "dedupe_pdf.py"), str(raw), str(final)],
                           check=True, capture_output=True)
            import pikepdf
            with pikepdf.open(final, allow_overwriting_input=True) as pdf:
                pdf.save(final, object_stream_mode=pikepdf.ObjectStreamMode.generate,
                         recompress_flate=True, compress_streams=True)
            raw.unlink()
            report[ed] = {"file": str(final), "pages": reps}
            print(f"{ed:10s} {len(pages)}p  {final.stat().st_size:,} B")
        br.close()
    (OUT / "build_report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    return report


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    rep = build()
    for ed, r in rep.items():
        for pid, x in r["pages"].items():
            flag = []
            if x["unconverted"]:
                flag.append(f"UNCONVERTED {x['unconverted']}")
            if x["textInConverted"]:
                flag.append(f"text-in-converted {x['textInConverted']}")
            print(f"  {pid:18s} sheet {x['sheet']} grad->svg {x['grad']:3d}  box-shadow {x['bs']}  {' '.join(flag)}")
