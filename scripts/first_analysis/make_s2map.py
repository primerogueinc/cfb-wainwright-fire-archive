from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import csv, sys
F="/usr/share/fonts/opentype/inter/"
def font(n,s): return ImageFont.truetype(F+n,int(s))
BROWN_DK=(28,20,15); GOLD=(212,175,104); CREAM=(238,230,214); NAVY=(30,52,82); MUTED=(176,162,138)
LAND=(185,132,36); VI=(79,141,214); YEL=(255,214,0)
N,S,Ea,W=52.83844698864907,52.52791908000258,-110.47096252441406,-111.21665954589845
w,h=2500,1717; kmpx=0.7457*67.4/w
x0,y0,x1,y1=850,230,1290,670; sc=1000/(x1-x0)
im=Image.open('cop/b5/2026-10-04-00_00_2026-10-04-23_59_Sentinel-2_L1C_True_color.jpg').convert('RGB').crop((x0,y0,x1,y1)).resize((1000,1000),Image.LANCZOS)
im=ImageEnhance.Contrast(im).enhance(1.15)
ov=Image.new('RGBA',im.size,(0,0,0,0)); d=ImageDraw.Draw(ov)
rows=list(csv.DictReader(open('/home/claude/cfb-wainwright-firms-detections.csv')))
def P(la,lo): return (((lo-W)/(Ea-W)*w-x0)*sc, ((N-la)/(N-S)*h-y0)*sc)
for r in rows:
    if 'VIIRS' in r['sensor']:
        x,y=P(float(r['latitude']),float(r['longitude'])); hh=0.1875/kmpx*sc
        d.rectangle([x-hh,y-hh,x+hh,y+hh],fill=VI+(70,),outline=VI+(255,),width=3)
for r in rows:
    if 'Landsat' in r['sensor']:
        x,y=P(float(r['latitude']),float(r['longitude'])); d.rectangle([x-4,y-4,x+4,y+4],fill=YEL+(255,))
img=Image.new('RGBA',(1600,1330),BROWN_DK+(255,)); dd=ImageDraw.Draw(img)
dd.rectangle([0,0,10,1330],fill=GOLD)
dd.text((50,36),"SATELLITE MAP  ·  CFB WAINWRIGHT TRAINING AREA  ·  OCT. 2026",font=font("Inter-Bold.otf",22),fill=GOLD)
dd.text((50,68),"Where NASA saw fire on Oct. 17, before the wind turned",font=font("InterDisplay-Black.otf",44),fill=CREAM)
dd.text((50,124),"NASA fire detections plotted on a cloud-free Sentinel-2 image of the same ground, taken Oct. 4.",font=font("Inter-Medium.otf",21),fill=MUTED)
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
# right panel
X=1090
def blk(y,head,col,body):
    dd.text((X,y),head,font=font("Inter-Black.otf",22),fill=col)
    for i,l in enumerate(body.split("\n")): dd.text((X,y+34+i*28),l,font=font("Inter-Medium.otf",19),fill=CREAM)
dd.rectangle([X,190,X+20,210],fill=YEL); blk(184,"      12:17 p.m.  Landsat 8",YEL,"59 low-confidence detections\n(30 m), in a band about 1.9 km\nlong, southwest to northeast.")
dd.rectangle([X,350,X+20,370],outline=VI,width=3); blk(344,"      2:49 p.m.  NOAA-20 VIIRS",VI,"8 detections. Squares are the\n375 m sensor pixels, which\noverstate the area burning.")
blk(510,"The ground",GOLD,"Detections sit in unburned\ngrassland and scrub just north\nof a saline lake. The area had\nnot burned as of Oct. 16.")
blk(690,"The older scar",GOLD,"A burn scar of about 5 x 2 km\nlies south of the lake, bounded\nby a straight road or fire guard.\nIt predates Oct. 4 and is not\nfrom the Oct. 17 fire.")
blk(900,"Not yet available",MUTED,"No Sentinel-2 image of the area\nwas captured Oct. 17 or 18. The\nOct. 17 burn scar will appear on\nthe next clear pass.")
fy=1190; dd.rectangle([0,fy,1600,1330],fill=NAVY); dd.rectangle([0,fy,1600,fy+5],fill=GOLD)
fc=font("Inter-Medium.otf",19)
dd.text((50,fy+22),"Imagery: Copernicus Sentinel-2, Oct. 4, 2026 (contains modified Copernicus Sentinel data). Fire data: NASA FIRMS. Positions accurate to",font=fc,fill=CREAM)
dd.text((50,fy+50),"roughly 100–200 m. Satellites detect heat, not cause. This map does not show where C Company was. Graphic: Prime Rogue Inc.",font=fc,fill=CREAM)
dd.text((50,fy+100),"PRIME ROGUE",font=font("Inter-Black.otf",24),fill=GOLD,anchor="lm")
logo=Image.open("/mnt/user-data/uploads/logo_transparent_prime_rogue_inc_512_by_512_1.png").convert("RGBA").resize((96,96),Image.LANCZOS)
img.alpha_composite(logo,(1600-96-50,fy+22))
img.convert('RGB').save(sys.argv[1],quality=90,optimize=True); print(img.size)
