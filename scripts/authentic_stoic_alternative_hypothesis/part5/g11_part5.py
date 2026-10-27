import sys, math
sys.path.insert(0, "vis")
exec(open('p5/prone.py').read().split('rows=[]')[0])
from pr import *
from pr import _LOGO
stand=np.array([sees(p.x,p.y,2.5,1.7,0.6,30) for p in P]); prone=np.array([sees(p.x,p.y,2.5,0.35,0.6,30) for p in P])
f['sees_standing']=stand; f['sees_prone']=prone; f.to_csv('p5/zone_visibility_vegetation.csv',index=False)
cls=np.where(prone,2,np.where(stand,1,0))
print('weighted shares prone/standing-only/none', [round(100*w[cls==k].sum()/w.sum()) for k in (2,1,0)])
OUT="vis/"
m = Map(-110.950, -110.866, 52.743, 52.792, 205)
scar = scar_main(); hull = preshift_hull()
HALF = 0.000225
base = m.base().convert("RGBA"); base = Image.blend(base, Image.new("RGBA", base.size, (0,0,0,255)), 0.35)
ov = Image.new("RGBA", base.size, (0,0,0,0)); od = ImageDraw.Draw(ov)
COL={2:TEAL,1:GOLD,0:(196,128,255)}
for (x,y),k,n in zip(zip(f.x,f.y),cls,w):
    p0=m.P(y+HALF,x-HALF*1.65); p1=m.P(y-HALF,x+HALF*1.65)
    od.rectangle([p0[0],p0[1],p1[0]+1,p1[1]+1],fill=COL[k]+(int(110+120*min(n,12)/12),))
m.poly(od,hull,fill=YEL+(40,)); m.outline(od,hull,YEL+(255,),3,dash=(14,9)); m.outline(od,scar,CREAM+(200,),3)
base.alpha_composite(ov); md=ImageDraw.Draw(base)
hx,hy=m.P(52.785,-110.926); label(md,(hx,hy),"Fire's edge before\nthe wind turned",YEL,17)
to=math.radians(126); q0=m.P(52.7885,-110.9445)
arrow(md,q0,(q0[0]+1.1*m.pxkm*math.sin(to),q0[1]-1.1*m.pxkm*math.cos(to)),(200,200,200),7,24)
label(md,(q0[0]-6,q0[1]-54),"Smoke and fire travel this way",CREAM,17)
lx,ly=40,base.size[1]-120
for i,(k,t) in enumerate(((2,"Flames visible even lying prone"),(1,"Visible standing, lost when prone"),(0,"Hidden by the ground, even standing"))):
    md.rectangle([lx,ly+i*34,lx+22,ly+i*34+22],fill=COL[k]); label(md,(lx+34,ly+i*34-2),t,CREAM,17)
W=1800; mh=base.size[1]; Hh=250+mh+150
im,d=canvas(W,Hh,"THE AUTHENTIC STOIC STRESS TEST  ·  PART 5  ·  CFB WAINWRIGHT, OCT. 17, 2026",
            "What could they see?",
            "Three things could have hidden the fire: dust, trees and smoke. We tested each against the likely ground from part 2.\nMap: could someone see 2.5 m flames at the fire's edge, through 0.6 m of cured grass?")
im.alpha_composite(base,(54,214))
X0=54+base.size[0]+44; y=226
def blk(head,big,col,lines):
    global y
    d.text((X0,y),head,font=K(24),fill=GOLD); y+=38
    d.text((X0,y),big,font=D(40),fill=col); y+=54
    for l in lines: d.text((X0,y),l,font=M(18),fill=CREAM); y+=25
    y+=20
blk("1  Dust","Not recorded",CREAM,["No airport reported blowing dust.","Dust warnings named counties to the","west, not Wainwright. Can't rule out","local dust at the fire itself."])
blk("2  Trees","No cover",CREAM,["The likely ground is 89% grass,","10% cropland, no tree canopy.","Trees change nothing. The ground","does: it hid the fire from about half."])
blk("3  Smoke","Tens of metres",RED,["The likely ground sat downwind,","in the smoke's path. If smoke hugged","the ground, visibility fell to about","15-75 m; flames to about 40-200 m."])
d.text((X0,y),"Lying prone, the fire's edge was hidden",font=B(18),fill=CREAM); y+=25
d.text((X0,y),"from about two-thirds of the ground.",font=B(18),fill=CREAM)
footer(im,["Sources: NRCan MRDEM-30; Meta/WRI 1 m canopy height; ESA WorldCover 2021; IEM METAR archive; ECCC alerts; NASA FIRMS; Sentinel-2. Smoke is a model (Gaussian line source,",
           "Briggs class D), not an observation. Method and data: github.com/primerogueinc/cfb-wainwright-fire-archive. Graphic: Kevin Duska Jr. (Prime Rogue Inc.)"])
im.convert("RGB").save(OUT+"cfb-wainwright-stress-test-part5.jpg",quality=92,optimize=True); print(im.size)
