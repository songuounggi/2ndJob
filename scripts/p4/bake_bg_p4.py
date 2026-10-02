# -*- coding: utf-8 -*-
"""상품 4 -- 디자인의 배경 굽기(reference/background_bake.js 의 bake())를 헤드리스 Chrome 에서 그대로 돌린다.

시안 배경 JPG(assets/25-*.jpg)는 대표 쪽 것뿐이다. 대표 쪽과 그림자 자리가 다른 쪽(예: Reset week 2~52 에 더한
"← Previous week" 알약, 52주의 Next 알약 빼기)은 같은 방식으로 새로 구워야 흰 알약이 배경에 묻히지 않는다.
번짐·유리 탭·켜진 탭·SOS·카드/알약 그림자 수치는 background_bake.js 와 같다(아래 BAKE_JS 는 그 함수를 옮긴 것).

검증: 대표 쪽 그림자 자리로 구운 결과가 시안 원본 JPG 와 거의 같아야 한다 (`verify`).
"""
import base64
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

# README §4 섹션 색 (c 대표, d 진한, t 옅은, paper 종이, w1/w2 번짐)
COLORS = {
    "mint": dict(c="#7FB59C", d="#537364", t="#E4F0EA", paper="#F3F7F4", w1="#CFE4EE", w2="#C4E6D0"),
    "lemon": dict(c="#E2BE3E", d="#7D6A28", t="#F8F0D0", paper="#F9F8F0", w1="#D6E7EE", w2="#F8ECB8"),
    "lavender": dict(c="#A393D8", d="#6E6490", t="#ECE8F8", paper="#F7F6FA", w1="#F1D3E5", w2="#DFD8F4"),
    "aqua": dict(c="#2FB3C6", d="#237581", t="#DAF1F4", paper="#F2F7F8", w1="#F6DCCB", w2="#C9ECF2"),
}

BAKE_JS = r"""async ({C, pg}) => {
 const K=2,W=612*K,H=792*K,c=document.createElement('canvas');c.width=W;c.height=H;const x=c.getContext('2d');
 const hex=(h,a)=>{const n=parseInt(h.slice(1),16);return `rgba(${n>>16},${(n>>8)&255},${n&255},${a})`;};
 x.fillStyle=C.paper;x.fillRect(0,0,W,H);
 const blob=(cx,cy,r,col,a)=>{const g=x.createRadialGradient(cx*K,cy*K,0,cx*K,cy*K,r*K);g.addColorStop(0,hex(col,a));g.addColorStop(1,hex(col,0));x.fillStyle=g;x.fillRect(0,0,W,H);};
 blob(170,0,300,C.w1,0.95);blob(470,40,340,C.w2,0.95);blob(0,560,260,C.w2,0.55);blob(40,860,240,C.w1,0.6);
 const snap=document.createElement('canvas');snap.width=W;snap.height=H;snap.getContext('2d').drawImage(c,0,0);
 const rr=(X,Y,w,h,r)=>{x.beginPath();x.roundRect(X*K,Y*K,w*K,h*K,r*K);};
 x.save();x.shadowColor='rgba(40,60,55,0.08)';x.shadowBlur=24*K;x.shadowOffsetY=8*K;rr(10,12,40,768,20);x.fillStyle='rgba(255,255,255,0.4)';x.fill();x.restore();
 x.save();rr(10,12,40,768,20);x.clip();x.filter='blur(14px)';x.drawImage(snap,0,0);x.filter='none';x.fillStyle='rgba(255,255,255,0.46)';x.fillRect(0,0,W,H);x.restore();
 const top=12+pg.tab*128, px=14,py=top+10,pw=32,ph=108,pr=16;
 x.save();x.shadowColor=hex(C.d,0.18);x.shadowBlur=6*K;x.shadowOffsetY=2*K;rr(px,py,pw,ph,pr);x.fillStyle=C.t;x.fill();x.restore();
 x.save();rr(px,py,pw,ph,pr);x.clip();
 const cx=(px+pw/2)*K, cy=(py+ph/2)*K, ry=(ph/2-5)*K, sx=(pw/2-3)/(ph/2-5);
 x.translate(cx,cy);x.scale(sx,1);x.translate(-cx,-cy);
 const g=x.createRadialGradient(cx,cy,0,cx,cy,ry);
 g.addColorStop(0,hex(C.d,0.07));g.addColorStop(0.55,hex(C.d,0.04));g.addColorStop(0.84,hex(C.d,0.012));g.addColorStop(0.93,'rgba(255,255,255,0.22)');g.addColorStop(1,'rgba(255,255,255,0)');
 x.fillStyle=g;x.beginPath();x.arc(cx,cy,ry,0,Math.PI*2);x.fill();x.restore();
 if(pg.sos){x.save();x.shadowColor=hex(C.d,0.18);x.shadowBlur=6*K;x.shadowOffsetY=2*K;rr(548,30,36,18,9);x.fillStyle=C.t;x.fill();x.restore();}
 pg.rects.forEach(q=>{x.fillStyle=q.ban?C.w2:'#FFFFFF';
  const pth=()=>{x.beginPath();if(q.rot){const cx=(q.x+q.w/2)*K,cy=(q.y+q.h/2)*K;x.translate(cx,cy);x.rotate(q.rot*Math.PI/180);x.translate(-cx,-cy);}
   x.roundRect(q.x*K,q.y*K,q.w*K,q.h*K,q.r*K);};
  (q.s||[[0.07,34,14],[0.07,4,1]]).forEach(s=>{x.save();x.shadowColor='rgba(40,60,55,'+s[0]+')';x.shadowBlur=s[1]*K;x.shadowOffsetY=s[2]*K;pth();x.fill();x.restore();});
  if(q.ban){x.save();pth();x.clip();const lg=x.createLinearGradient(q.x*K,0,(q.x+q.w)*K,0);lg.addColorStop(0,C.w1);lg.addColorStop(1,C.w2);x.fillStyle=lg;x.fillRect(q.x*K,q.y*K,q.w*K,q.h*K);
    const rg=x.createRadialGradient((q.x+q.w*0.8)*K,q.y*K,0,(q.x+q.w*0.8)*K,q.y*K,160*K);rg.addColorStop(0,'rgba(255,255,255,0.45)');rg.addColorStop(1,'rgba(255,255,255,0)');x.fillStyle=rg;x.fillRect(q.x*K,q.y*K,q.w*K,q.h*K);x.restore();}
 });
 return c.toDataURL('image/jpeg',0.85);
}"""


def rects_of(page_html):
    """틀 HTML 에서 그림자를 받는 사각형: 카드(모서리 16, 흰/투명=배너) + 흰 알약(모서리 12 · 14)"""
    out = []
    for m in re.finditer(r'style="position:absolute;left:([\d.]+)px;top:([\d.]+)px;width:([\d.]+)px;height:([\d.]+)px;'
                         r'border-radius:(\d+(?:\.\d+)?)px;background:(#FFFFFF|transparent)', page_html):
        x, y, w, h, r, bg = m.groups()
        if float(r) in (16, 12, 14):
            out.append(dict(x=float(x), y=float(y), w=float(w), h=float(h), r=float(r), ban=bg == "transparent"))
    # 쪽 아래 알약(링크): HTML 에는 흰 바탕이 없다 -- 흰 알약과 그림자가 배경에 구워져 있다 (top 754, 모서리 12)
    for m in re.finditer(r'style="position:absolute;left:([\d.]+)px;top:754px;width:([\d.]+)px;height:24px;'
                         r'border-radius:12px;(?![^"]*background)', page_html):
        out.append(dict(x=float(m.group(1)), y=754.0, w=float(m.group(2)), h=24.0, r=12.0, ban=False))
    return out


def bake(jobs):
    """jobs: [(path, colors, tab, rects)] -> JPG 들"""
    from chrome_auto import launch
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = launch(p)
        pg = br.new_page()
        pg.set_content("<html><body></body></html>")
        for path, col, tab, rects in jobs:
            url = pg.evaluate(BAKE_JS, {"C": col, "pg": {"tab": tab, "sos": True, "rects": rects}})
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, "wb").write(base64.b64decode(url.split(",", 1)[1]))
        br.close()


def masked_diff(a, b, rects, pad=34):
    """두 배경의 평균 차이 -- rects(새로 넣은 카드·알약)와 그 그림자 범위(pad pt)는 빼고. 그림 2배(1pt = 2px)"""
    from PIL import Image, ImageChops, ImageDraw
    A, B = Image.open(a).convert("L"), Image.open(b).convert("L")
    mask = Image.new("L", A.size, 255)
    dr = ImageDraw.Draw(mask)
    for r in rects:
        dr.rectangle([(r["x"] - pad) * 2, (r["y"] - pad) * 2, (r["x"] + r["w"] + pad) * 2, (r["y"] + r["h"] + pad) * 2], fill=0)
    d = ImageChops.difference(A, B)
    h = d.histogram(mask)
    n = sum(h)
    return sum(i * c for i, c in enumerate(h)) / max(n, 1)


def mean_diff(a, b):
    from PIL import Image, ImageChops
    A, B = Image.open(a).convert("L"), Image.open(b).convert("L")
    d = ImageChops.difference(A, B)
    h = d.histogram()
    return sum(i * n for i, n in enumerate(h)) / (A.width * A.height)
