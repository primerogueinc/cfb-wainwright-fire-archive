from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import csv
F="/usr/share/fonts/opentype/inter/"
def font(n,s): return ImageFont.truetype(F+n,int(s))
BG=(28,20,15); GOLD=(212,175,104); CREAM=(238,230,214); MUTED=(190,176,152); YEL=(255,214,0); VI=(79,141,214); RED=(224,96,60)
N,S,Ea,W=52.83844698864907,52.52791908000258,-110.47096252441406,-111.21665954589845
w,h=2500,1717; kmpx=0.7457*67.4/w
x0,y0,x1,y1=700,170,1300,610; sc=900/(y1-y0)
base=Image.open('cop/b5/2026-10-04-00_00_2026-10-04-23_59_Sentinel-2_L1C_True_color.jpg').convert('RGB').crop((x0,y0,x1,y1))
base=base.resize((int((x1-x0)*sc),900),Image.LANCZOS); base=ImageEnhance.Brightness(ImageEnhance.Contrast(base).enhance(1.15)).enhance(0.8)
img=Image.new('RGBA',(1600,900),BG+(255,)); img.paste(base,(1600-base.width,0))
ov=Image.new('RGBA',img.size,(0,0,0,0)); d=ImageDraw.Draw(ov)
def P(la,lo): return (1600-base.width+((lo-W)/(Ea-W)*w-x0)*sc, ((N-la)/(N-S)*h-y0)*sc)
for r in csv.DictReader(open('/home/claude/firms-raw-package/cfb-wainwright-firms-detections.csv')):
    if not r['detection_time_mdt'].startswith('2026-10-17'): continue
    x,y=P(float(r['latitude']),float(r['longitude']))
    if 'VIIRS' in r['sensor']:
        hx=float(r['scan_km'])/2/kmpx*sc; hy=float(r['track_km'])/2/kmpx*sc
        d.rectangle([x-hx,y-hy,x+hx,y+hy],fill=VI+(55,),outline=VI+(255,),width=3)
    else: d.rectangle([x-4,y-4,x+4,y+4],fill=YEL+(255,))
img.alpha_composite(ov)
g=Image.new('L',(1600,1))
for i in range(1600): g.putpixel((i,0),255 if i<640 else max(0,int(255-(i-640)*0.6)))
grad=Image.new('RGBA',(1600,900),BG+(255,)); grad.putalpha(g.resize((1600,900))); img.alpha_composite(grad)
dd=ImageDraw.Draw(img); dd.rectangle([0,0,10,900],fill=GOLD)
dd.text((60,64),"PRIME ROGUE  ·  CFB WAINWRIGHT FIRE",font=font("Inter-Bold.otf",24),fill=GOLD)
dd.text((60,120),"National Defence:",font=font("Inter-Bold.otf",34),fill=MUTED)
dd.text((60,165),"“ignited” at 4 p.m.",font=font("InterDisplay-Black.otf",78),fill=RED)
dd.text((60,300),"The records:",font=font("Inter-Bold.otf",34),fill=MUTED)
y=350
for c,t in [(YEL,"12:17 p.m.  fire seen by Landsat 8"),(CREAM,"2:14 p.m.  wind warning for Wainwright"),(VI,"2:49 p.m.  fire seen by NOAA-20"),(CREAM,"Fire Weather Index: Extreme")]:
    dd.text((60,y),t,font=font("Inter-Black.otf",40),fill=c); y+=62
dd.text((60,y+30),"DND's account doesn't match the",font=font("Inter-Medium.otf",30),fill=MUTED)
dd.text((60,y+72),"government's own records.",font=font("Inter-Medium.otf",30),fill=MUTED)
dd.text((60,850),"Imagery: contains modified Copernicus Sentinel data (Oct. 4). Fire data: NASA FIRMS. Times MT, Oct. 17.",font=font("Inter-Medium.otf",18),fill=MUTED)
logo=Image.open("/mnt/user-data/uploads/logo_transparent_prime_rogue_inc_512_by_512_1.png").convert("RGBA").resize((110,110),Image.LANCZOS)
img.alpha_composite(logo,(1600-110-30,900-110-25))
img.convert('RGB').save('/home/claude/cfb-wainwright-dnd-records-header.jpg',quality=90,optimize=True)
img.convert('RGB').resize((1200,675),Image.LANCZOS).save('/home/claude/cfb-wainwright-dnd-records-header-1200.jpg',quality=90,optimize=True)
