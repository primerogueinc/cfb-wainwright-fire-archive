import sys, math
sys.path.insert(0,"vis")
from pr import *
from pr import _LOGO
OUT="vis/"; P6=REPO+"data/authentic-stoic-stress-test/part6_edge/"
E=gpd.read_file(P6+"edge_at_front.geojson"); hull=preshift_hull(); scar=scar_main()
m=Map(-110.952,-110.862,52.741,52.796,200)
base=m.base().convert("RGBA"); base=Image.blend(base,Image.new("RGBA",base.size,(0,0,0,255)),0.4)
ov=Image.new("RGBA",base.size,(0,0,0,0)); od=ImageDraw.Draw(ov)
m.outline(od,scar,CREAM+(150,),2)
CASES=[(8.0,(150,150,150),"8 km/h (the post-front pace)"),(4.0,RED,"4 km/h"),(1.5,(255,150,60),"1.5 km/h"),(0.45,TEAL,"0.45 km/h (its measured pace)")]
for ros,col,_ in CASES:
    g=E[(E.minutes==27)&(E.head_ros_kmh==ros)].geometry.iloc[0]; m.poly(od,g,fill=col+(45,)); m.outline(od,g,col+(255,),4)
m.poly(od,hull,fill=YEL+(70,)); m.outline(od,hull,YEL+(255,),3,dash=(12,8))
base.alpha_composite(ov); md=ImageDraw.Draw(base)
S={"A":(52.7728,-110.9063),"B":(52.7705,-110.8996),"C":(52.7640,-110.9160),"D":(52.7628,-110.8995),"E":(52.7530,-110.8990)}
for k,(la,lo) in S.items():
    x,y=m.P(la,lo); md.ellipse([x-12,y-12,x+12,y+12],fill=INK,outline=(255,255,255),width=3); md.text((x,y),k,font=B(15),fill=(255,255,255),anchor="mm")
label(md,(m.P(52.7728,-110.9063)[0]+18,m.P(52.7728,-110.9063)[1]-14),"Range 2",CREAM,16)
hx,hy=m.P(52.7905,-110.947); label(md,(hx,hy),"Edge at the last satellite pass\n(Landsat 12:17, VIIRS 2:49)",YEL,16)
to=math.radians(66); q0=m.P(52.7895,-110.893)
arrow(md,q0,(q0[0]+0.9*m.pxkm*math.sin(to),q0[1]-0.9*m.pxkm*math.cos(to)),(220,220,220),6,22)
label(md,(q0[0]-120,q0[1]+20),"Wind before 3:16: SW, 30-32 km/h",CREAM,16)
lx,ly=30,base.size[1]-36*len(CASES)-50
label(md,(lx,ly-34),"Where the edge could be at 3:16, if the fire's head ran at:",CREAM,16)
for i,(ros,col,t) in enumerate(CASES):
    md.rectangle([lx,ly+i*34,lx+22,ly+i*34+22],fill=col); label(md,(lx+32,ly+i*34-2),t,CREAM,16)
W=1800; mh=base.size[1]; Hh=250+mh+150
im,d=canvas(W,Hh,"THE AUTHENTIC STOIC STRESS TEST  ·  PART 6  ·  CFB WAINWRIGHT, OCT. 17, 2026",
            "Where was the fire when the wind turned?",
            "The last satellite pass was at 2:49. Parts 1-5 assumed the fire stood still for the next 27 minutes. We tested that:\nhow fast was it moving, and what changes if it moved?")
im.alpha_composite(base,(54,214))
X0=54+base.size[0]+44; y=226
def txt(lines,col=CREAM,f=M(18)):
    global y
    for l in lines: d.text((X0,y),l,font=f,fill=col); y+=25
d.text((X0,y),"Its measured pace",font=K(24),fill=GOLD); y+=38
d.text((X0,y),"~0.45 km/h",font=D(44),fill=TEAL); y+=58
txt(["Its head moved about 1 km north-","east between 12:17 and 2:49."]); y+=16
d.text((X0,y),"Fire power agrees",font=K(24),fill=GOLD); y+=38
# mini bar chart
bars=[("VIIRS 2:49",74.6,YEL),("GOES 3:10",76.5,TEAL),("If 1.5 km/h",338,(255,150,60)),("If 4 km/h",900,RED),("GOES 3:30",1215,(220,220,220))]
mx=1300; bw=240
for lab,v,col in bars:
    d.text((X0,y+2),lab,font=M(16),fill=CREAM); d.rectangle([X0+120,y,X0+120+int(bw*v/mx),y+20],fill=col)
    d.text((X0+128+int(bw*v/mx),y),f"{v:.0f} MW",font=B(16),fill=CREAM); y+=30
y+=4; txt(["Before the front, the fire gave off","what a slow fire would. After, 16x."],MUTED,M(17)); y+=16
d.text((X0,y),"What changes",font=K(24),fill=GOLD); y+=38
txt(["At its measured pace, the edge","came 100-150 m closer to Range 2,","and the likely ground slides","about 100-230 m south-east.","Range 2 stays in it."]); y+=16
d.text((X0,y),"Where it breaks",font=K(24),fill=GOLD); y+=38
txt(["Triple the pace and the edge is","within 250 m of Range 2. At 4 km/h,","Range 2 burned before the wind","turned. Fire power doesn't support","either, but cloud weakens that test."],MUTED,M(17))
footer(im,["Sources: NASA FIRMS (Landsat 12:17, VIIRS NOAA-20 2:49); NOAA GOES-18 FDC; ECCC CZWN; Sentinel-2 scar. Edges: elliptical growth for 27 min, wind 246°, LB 5.4. Expected fire power:",
           "Byram intensity, 0.3 kg/m² grass, 15% radiative, 1 km front. Method and data: github.com/primerogueinc/cfb-wainwright-fire-archive. Graphic: Kevin Duska Jr. (Prime Rogue Inc.)"])
im.convert("RGB").save(OUT+"cfb-wainwright-stress-test-part6.jpg",quality=92,optimize=True); print(im.size)
# card
Sx=Image.new("RGBA",(1200,675),BG+(255,)); sd=ImageDraw.Draw(Sx); sd.rectangle([0,0,10,675],fill=GOLD)
mp=base.copy(); mp=mp.resize((int(mp.size[0]*675/mp.size[1]),675),Image.LANCZOS); Sx.alpha_composite(mp.crop((0,0,600,675)),(10,0))
X1=650; sd.text((X1,50),"THE AUTHENTIC STOIC STRESS TEST",font=B(19),fill=GOLD); sd.text((X1,80),"Part 6",font=D(56),fill=CREAM)
sd.text((X1,156),"Where was the fire",font=K(32),fill=CREAM); sd.text((X1,194),"when the wind turned?",font=K(32),fill=CREAM)
yy=262
for big,col,t in (("~0.45 km/h",TEAL,"its measured pace before the front"),("100-150 m",CREAM,"closer to Range 2 than we assumed"),("Holds",TEAL,"unless it tripled its pace, which\nits fire power doesn't show")):
    sd.text((X1,yy),big,font=D(34),fill=col); yy+=44; sd.multiline_text((X1,yy),t,font=M(20),fill=CREAM,spacing=6); yy+=34+28*t.count("\n")+14
sd.rectangle([600,580,1200,675],fill=NAVY); sd.rectangle([600,580,1200,585],fill=GOLD)
sd.text((X1,612),"Thanks to @AuthenticStoic",font=B(20),fill=GOLD); sd.text((X1,660),"PRIME ROGUE",font=K(20),fill=GOLD,anchor="lb"); Sx.paste(_LOGO,(1200-84-30,588))
Sx.convert("RGB").save(OUT+"cfb-wainwright-stress-test-part6-card.jpg",quality=92,optimize=True)
