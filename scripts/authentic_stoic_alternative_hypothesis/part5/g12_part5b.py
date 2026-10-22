import sys; sys.path.insert(0,"vis")
from pr import *
from pr import _LOGO
import pandas as pd
OUT="vis/"
po=pd.read_csv('p5/posture_visibility.csv'); sm=pd.read_csv('p5/smoke_visibility.csv'); sm=sm[sm.case=='low']
# ---- social card
S=Image.new("RGBA",(1200,675),BG+(255,)); sd=ImageDraw.Draw(S); sd.rectangle([0,0,10,675],fill=GOLD)
mp=Image.open(OUT+"cfb-wainwright-stress-test-part5.jpg").convert("RGBA").crop((54+380,440,54+1000,440+800))
mp=mp.resize((int(mp.size[0]*675/mp.size[1]),675),Image.LANCZOS); S.alpha_composite(mp.crop((0,0,600,675)),(10,0))
X1=650
sd.text((X1,50),"THE AUTHENTIC STOIC STRESS TEST",font=B(19),fill=GOLD)
sd.text((X1,80),"Part 5",font=D(56),fill=CREAM)
sd.text((X1,156),"What could they see?",font=K(32),fill=CREAM)
y=222
for big,col,txt in (("No trees",CREAM,"Open grass. Trees hid nothing."),("2 in 3",TEAL,"places hid the fire's edge from\nsomeone lying prone."),("Tens of metres",RED,"modelled visibility if the smoke\nstayed low.")):
    sd.text((X1,y),big,font=D(36),fill=col); y+=46
    sd.multiline_text((X1,y),txt,font=M(20),fill=CREAM,spacing=6); y+=34+28*txt.count("\n")+18
sd.rectangle([600,580,1200,675],fill=NAVY); sd.rectangle([600,580,1200,585],fill=GOLD)
sd.text((X1,612),"Thanks to @AuthenticStoic",font=B(20),fill=GOLD)
sd.text((X1,660),"PRIME ROGUE",font=K(20),fill=GOLD,anchor="lb")
S.paste(_LOGO,(1200-84-30,588))
S.convert("RGB").save(OUT+"cfb-wainwright-stress-test-part5-card.jpg",quality=92,optimize=True)
# ---- chart: posture bars + smoke lines
W,Hh=1800,1050
im,d=canvas(W,Hh,"THE AUTHENTIC STOIC STRESS TEST  ·  PART 5  ·  CFB WAINWRIGHT, OCT. 17, 2026",
            "The ground and the smoke, not the trees",
            "Left: share of the likely ground with a line of sight to 2.5 m flames at the fire's edge. Right: modelled visibility inside a ground-hugging plume.")
# left panel
x0,y0,pw,ph=90,300,760,520
d.text((x0,y0-50),"Could they see the flames?",font=K(26),fill=GOLD)
rows=po[po.flame_m==2.5]
for i,post in enumerate(['standing','kneeling','prone']):
    r=rows[rows.posture==post]; a=int(r[r.grass=='no grass'].share_any.iloc[0]); g=int(r[r.grass!='no grass'].share_any.iloc[0])
    yy=y0+40+i*160
    d.text((x0,yy),post.capitalize(),font=B(24),fill=CREAM)
    for j,(v,col,lab) in enumerate(((a,MUTED,"bare ground"),(g,TEAL,"through 0.6 m cured grass"))):
        by=yy+40+j*48; d.rectangle([x0,by,x0+pw,by+36],fill=GRIDC); d.rectangle([x0,by,x0+int(pw*v/100),by+36],fill=col)
        d.text((x0+int(pw*v/100)+12,by+4),f"{v}%",font=B(24),fill=CREAM); d.text((x0+10,by+7),lab,font=M(17),fill=INK)
# right panel: smoke
x1,y1,cw,ch=1000,300,700,520
d.text((x1,y1-50),"How far could they see in the smoke?",font=K(26),fill=GOLD)
d.rectangle([x1,y1,x1+cw,y1+ch],fill=PANEL)
xmax,ymax=1500,450
def P(x,y): return (x1+cw*x/xmax, y1+ch-ch*y/ymax)
for gy in (100,200,300,400):
    d.line([P(0,gy),P(xmax,gy)],fill=GRIDC,width=2); d.text((x1-60,P(0,gy)[1]-11),f"{gy} m",font=M(16),fill=MUTED)
for gx in (500,1000,1500):
    d.text((P(gx,0)[0]-40,y1+ch+10),f"{gx/1000:g} km",font=M(16),fill=MUTED)
d.text((x1+cw/2-120,y1+ch+40),"distance downwind of the fire",font=M(17),fill=MUTED)
s8=sm[sm.ros_kmh==8.0].sort_values('x_m')
lo=sm.groupby('x_m').vis_dark_m.min(); hi=sm.groupby('x_m').vis_dark_m.max()
flo=sm.groupby('x_m').vis_flames_m.min(); fhi=sm.groupby('x_m').vis_flames_m.max()
ov=Image.new("RGBA",im.size,(0,0,0,0)); od=ImageDraw.Draw(ov)
od.polygon([P(x,v) for x,v in fhi.items()]+[P(x,v) for x,v in list(flo.items())[::-1]],fill=YEL+(70,))
od.polygon([P(x,v) for x,v in hi.items()]+[P(x,v) for x,v in list(lo.items())[::-1]],fill=RED+(110,))
im.alpha_composite(ov); d=ImageDraw.Draw(im)
d.line([P(x,v) for x,v in zip(s8.x_m,s8.vis_flames_m)],fill=YEL,width=4)
d.line([P(x,v) for x,v in zip(s8.x_m,s8.vis_dark_m)],fill=RED,width=4)
label(d,P(820,int(s8[s8.x_m==1000].vis_flames_m.iloc[0])+70),"Flames",YEL,18)
label(d,P(1050,int(s8[s8.x_m==1000].vis_dark_m.iloc[0])-15),"A person or vehicle",RED,18)
d.multiline_text((x1,y1+ch+76),"Bands: fire spreading 4.4-12 km/h. Line: 8 km/h.\nIf the smoke rose instead, ground visibility was unaffected.",font=M(16),fill=MUTED,spacing=6)
footer(im,["Sources: NRCan MRDEM-30; Meta/WRI 1 m canopy height; ESA WorldCover 2021. Smoke: Gaussian line-source model (Briggs class D, Koschmieder), not an observation.",
           "Method and data: github.com/primerogueinc/cfb-wainwright-fire-archive. Graphic: Kevin Duska Jr. (Prime Rogue Inc.)"])
im.convert("RGB").save(OUT+"cfb-wainwright-stress-test-part5-chart.jpg",quality=92,optimize=True); print('ok')
