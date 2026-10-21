from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import csv, sys
F="/usr/share/fonts/opentype/inter/"
def font(n,s): return ImageFont.truetype(F+n,int(s))
BROWN_DK=(28,20,15); GOLD=(212,175,104); CREAM=(238,230,214); NAVY=(30,52,82); MUTED=(176,162,138)
LAND=(185,132,36); VI=(79,141,214); YEL=(255,214,0); C14=(245,240,230); ORG=(240,128,60)
N,S,Ea,W=52.83844698864907,52.52791908000258,-110.47096252441406,-111.21665954589845
w,h=2500,1717; kmpx=0.7457*67.4/w
x0,y0,x1,y1=850,230,1290,670; sc=1000/(x1-x0)
im=Image.open('cop/b5/2026-10-04-00_00_2026-10-04-23_59_Sentinel-2_L1C_True_color.jpg').convert('RGB').crop((x0,y0,x1,y1)).resize((1000,1000),Image.LANCZOS)
im=ImageEnhance.Contrast(im).enhance(1.15)
ov=Image.new('RGBA',im.size,(0,0,0,0)); d=ImageDraw.Draw(ov)
rows=list(csv.DictReader(open('/home/claude/cfb-wainwright-firms-detections.csv')))
def P(la,lo): return (((lo-W)/(Ea-W)*w-x0)*sc, ((N-la)/(N-S)*h-y0)*sc)
def vcol(r):
    t=r['detection_time_mdt'][:10]
    return {'2026-10-14':C14,'2026-10-17':VI,'2026-10-18':ORG}[t]
for r in rows:
    if 'VIIRS' in r['sensor']:
        x,y=P(float(r['latitude']),float(r['longitude'])); hx=float(r['scan_km'])/2/kmpx*sc; hy=float(r['track_km'])/2/kmpx*sc; c=vcol(r)
        d.rectangle([x-hx,y-hy,x+hx,y+hy],fill=c+(60,),outline=c+(255,),width=3)
for r in rows:
    if 'Landsat' in r['sensor']:
        x,y=P(float(r['latitude']),float(r['longitude'])); d.rectangle([x-4,y-4,x+4,y+4],fill=YEL+(255,))
img=Image.new('RGBA',(1600,1330),BROWN_DK+(255,)); dd=ImageDraw.Draw(img)
dd.rectangle([0,0,10,1330],fill=GOLD)
dd.text((50,36),"SATELLITE MAP  ·  CFB WAINWRIGHT TRAINING AREA  ·  OCT. 2026",font=font("Inter-Bold.otf",22),fill=GOLD)
dd.text((50,68),"Where NASA saw fire around the Oct. 17 fire",font=font("InterDisplay-Black.otf",44),fill=CREAM)
dd.text((50,124),"Every NASA fire detection within the map, Oct. 12–18, on a cloud-free Sentinel-2 image taken Oct. 4.",font=font("Inter-Medium.otf",21),fill=MUTED)
img.paste(im,(50,170)); img.alpha_composite(ov,(50,170))
dd=ImageDraw.Draw(img)
# scale bar 1 km
L=1/kmpx*sc; dd.rectangle([80,1120,80+L,1130],fill=CREAM); dd.text((80,1088),"1 km",font=font("Inter-Bold.otf",22),fill=CREAM)
# north arrow
dd.polygon([(1000,200),(988,236),(1012,236)],fill=CREAM); dd.text((1000,248),"N",font=font("Inter-Bold.otf",22),fill=CREAM,anchor="mt")
# callouts on map
def call(xy,txt,tx,ty,col=CREAM):
    x,y=xy; dd.line([(x+50,y+170),(tx+50,ty+170)],fill=col,width=2)
    lines=txt.split("\n"); fw=max(dd.textlength(l,font=font("Inter-Bold.otf",19)) for l in lines)
    dd.rounded_rectangle([tx+50-8,ty+170-6,tx+50+fw+10,ty+170+len(lines)*25+4],radius=6,fill=(20,14,10))
    for i,l in enumerate(lines): dd.text((tx+50,ty+170+i*25),l,font=font("Inter-Bold.otf",19),fill=col)
call(P(52.7533,-110.93),"Saline lake",560,600)
call(P(52.728,-110.92),"Older burn scar, already\nvisible Oct. 4 (date unknown)",560,820)
x,y=P(52.7885,-110.902); call((x,y),"Fire detections, Oct. 17",620,60,YEL)
call(P(52.75486,-110.93891),"Oct. 14 detection",20,400,C14)
call(P(52.7464,-110.8658),"Oct. 18 detections",790,700,ORG)
# right panel
X=1090
def blk(y,head,col,body):
    dd.text((X,y),head,font=font("Inter-Black.otf",22),fill=col)
    for i,l in enumerate(body.split("\n")): dd.text((X,y+34+i*28),l,font=font("Inter-Medium.otf",19),fill=CREAM)
BL=[("sq",YEL,"      Oct. 17, 12:17 p.m.  Landsat 8","59 detections (30 m pixels) in a\nband about 1.9 km long, SW to NE.\nConfidence low or medium,\ndepending on the FIRMS file."),
("box",VI,"      Oct. 17, 2:49 p.m.  NOAA-20","8 detections. Squares are the\nsensor pixels, which overstate\nthe area burning."),
("box",C14,"      Oct. 14, 2:51 p.m.  NOAA-21","1 detection on the lake's west\nshore, three days earlier. Any link\nto the Oct. 17 fire is unknown."),
("box",ORG,"      Oct. 18, 2:12 & 2:32 p.m.","1 detection each (Suomi-NPP,\nNOAA-20), about 5 km SE, near the\nbase boundary. Source unknown."),
(None,GOLD,"The older scar","About 5 x 2 km, south of the lake,\nbounded by a straight road or fire\nguard. It predates Oct. 4."),
(None,MUTED,"Not yet available","No Sentinel-2 image was captured\nOct. 17 or 18. The new burn scar\nwill show on the next clear pass.")]
y=184
for k,c,hd,bd in BL:
    if k=="sq": dd.rectangle([X,y+6,X+20,y+26],fill=c)
    if k=="box": dd.rectangle([X,y+6,X+20,y+26],outline=c,width=3)
    blk(y,hd,c,bd); y+=34+28*len(bd.split("\n"))+30
print("panel end",y)
fy=1190; dd.rectangle([0,fy,1600,1330],fill=NAVY); dd.rectangle([0,fy,1600,fy+5],fill=GOLD)
fc=font("Inter-Medium.otf",19)
dd.text((50,fy+22),"Imagery: Copernicus Sentinel-2, Oct. 4, 2026 (contains modified Copernicus Sentinel data). Fire data: NASA FIRMS. Positions accurate to",font=fc,fill=CREAM)
dd.text((50,fy+50),"roughly 100–200 m. Satellites detect heat, not cause. This map does not show where C Company was. Graphic: Prime Rogue Inc.",font=fc,fill=CREAM)
dd.text((50,fy+100),"PRIME ROGUE",font=font("Inter-Black.otf",24),fill=GOLD,anchor="lm")
logo=Image.open("/mnt/user-data/uploads/logo_transparent_prime_rogue_inc_512_by_512_1.png").convert("RGBA").resize((96,96),Image.LANCZOS)
img.alpha_composite(logo,(1600-96-50,fy+22))
img.convert('RGB').save(sys.argv[1],quality=90,optimize=True); print(img.size)
