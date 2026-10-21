from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import csv
F="/usr/share/fonts/opentype/inter/"
def font(n,s): return ImageFont.truetype(F+n,int(s))
BROWN_DK=(28,20,15); GOLD=(212,175,104); CREAM=(238,230,214); MUTED=(190,176,152)
YEL=(255,214,0); VI=(79,141,214); C14=(245,240,230); ORG=(240,128,60)
N,S,Ea,W=52.83844698864907,52.52791908000258,-110.47096252441406,-111.21665954589845
w,h=2500,1717; kmpx=0.7457*67.4/w
x0,y0,x1,y1=660,250,1310,700; sc=900/(y1-y0)
base=Image.open('cop/b5/2026-10-04-00_00_2026-10-04-23_59_Sentinel-2_L1C_True_color.jpg').convert('RGB').crop((x0,y0,x1,y1))
base=base.resize((int((x1-x0)*sc),900),Image.LANCZOS); base=ImageEnhance.Brightness(ImageEnhance.Contrast(base).enhance(1.15)).enhance(0.8)
img=Image.new('RGBA',(1600,900),BROWN_DK+(255,)); img.paste(base,(1600-base.width,0))
ov=Image.new('RGBA',img.size,(0,0,0,0)); d=ImageDraw.Draw(ov)
def P(la,lo): return (1600-base.width+((lo-W)/(Ea-W)*w-x0)*sc, ((N-la)/(N-S)*h-y0)*sc)
col={'2026-10-14':C14,'2026-10-17':VI,'2026-10-18':ORG}
for r in csv.DictReader(open('pkg_v2/cfb-wainwright-firms-detections.csv')):
    x,y=P(float(r['latitude']),float(r['longitude']))
    if 'VIIRS' in r['sensor']:
        c=col[r['detection_time_mdt'][:10]]; hx=float(r['scan_km'])/2/kmpx*sc; hy=float(r['track_km'])/2/kmpx*sc
        d.rectangle([x-hx,y-hy,x+hx,y+hy],fill=c+(55,),outline=c+(255,),width=3)
    else: d.rectangle([x-4,y-4,x+4,y+4],fill=YEL+(255,))
img.alpha_composite(ov)
# left gradient
g=Image.new('L',(1600,1)); 
for i in range(1600): g.putpixel((i,0),255 if i<560 else max(0,int(255-(i-560)*0.55)))
grad=Image.new('RGBA',(1600,900),BROWN_DK+(255,)); grad.putalpha(g.resize((1600,900)))
img.alpha_composite(grad)
dd=ImageDraw.Draw(img); dd.rectangle([0,0,10,900],fill=GOLD)
dd.text((60,70),"PRIME ROGUE  ·  FULL ANALYSIS",font=font("Inter-Bold.otf",24),fill=GOLD)
y=120
for l in ["A week of satellite","data on the","Wainwright fire"]:
    dd.text((60,y),l,font=font("InterDisplay-Black.otf",76),fill=CREAM); y+=88
y+=20
for l in ["Every NASA detection near CFB Wainwright,","Oct. 12–18: what it shows, what it can't,","and what the military has said."]:
    dd.text((60,y),l,font=font("Inter-Medium.otf",30),fill=MUTED); y+=42
y+=30
for c,t,sq in [(YEL,"Oct. 17, 12:17 p.m.  Landsat 8",True),(VI,"Oct. 17, 2:49 p.m.  NOAA-20",False),(C14,"Oct. 14, 2:51 p.m.  NOAA-21",False),(ORG,"Oct. 18, 2:12 & 2:32 p.m.",False)]:
    if sq: dd.rectangle([60,y+6,82,y+28],fill=c)
    else: dd.rectangle([60,y+6,82,y+28],outline=c,width=3)
    dd.text((98,y),t,font=font("Inter-Bold.otf",26),fill=c); y+=42
dd.text((60,850),"Imagery: contains modified Copernicus Sentinel data (Oct. 4). Fire data: NASA FIRMS.",font=font("Inter-Medium.otf",18),fill=MUTED)
logo=Image.open("/mnt/user-data/uploads/logo_transparent_prime_rogue_inc_512_by_512_1.png").convert("RGBA").resize((110,110),Image.LANCZOS)
img.alpha_composite(logo,(1600-110-30,900-110-25))
img.convert('RGB').save('/home/claude/cfb-wainwright-full-analysis-header.jpg',quality=90,optimize=True)
img.convert('RGB').resize((1200,675),Image.LANCZOS).save('/home/claude/cfb-wainwright-full-analysis-header-1200.jpg',quality=90,optimize=True)
print(base.size)
