import json, datetime as dt, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.dates as md
from matplotlib import font_manager as fm
from matplotlib.patches import Rectangle
from PIL import Image
F="/usr/share/fonts/opentype/inter/"
for n in ["Inter-Medium.otf","Inter-SemiBold.otf","Inter-Bold.otf","Inter-Black.otf","InterDisplay-Black.otf"]: fm.fontManager.addfont(F+n)
plt.rcParams["font.family"]="Inter"
BG="#1C140F"; PANEL="#251A14"; GOLD="#D4AF68"; CREAM="#EEE6D6"; MUTED="#A99B84"; GRID="#352820"; NAVY="#1E3452"
YEL="#FFD600"; VI="#4F8DD6"; C14="#F5F0E6"; ORG="#F0803C"; NONE="#6E6252"
P=json.load(open("passlist.json"))
for p in P: p["t0"]=dt.datetime.fromisoformat(p["t0"]); p["t1"]=dt.datetime.fromisoformat(p["t1"])
ROWS=[("NOAA-20 VIIRS","NOAA-20 · VIIRS 375 m"),("NOAA-21 VIIRS","NOAA-21 · VIIRS 375 m"),("Suomi-NPP VIIRS","Suomi-NPP · VIIRS 375 m"),("MODIS","Aqua / Terra · MODIS 1 km")]
HITS={("NOAA-21 VIIRS","2026-10-14"):(dt.datetime(2026,10,14,14,51),C14,"1"),("NOAA-20 VIIRS","2026-10-17"):(dt.datetime(2026,10,17,14,49),VI,"8"),
      ("Suomi-NPP VIIRS","2026-10-18"):(dt.datetime(2026,10,18,14,12),ORG,"1"),("NOAA-20 VIIRS","2026-10-18"):(dt.datetime(2026,10,18,14,32),ORG,"1")}
def rowof(s): return "MODIS" if "MODIS" in s else s
fig=plt.figure(figsize=(16,11.6),dpi=100,facecolor=BG)
fig.patches.append(Rectangle((0,0),0.007,1,transform=fig.transFigure,facecolor=GOLD))
fig.text(0.03,0.952,"NASA FIRMS  ·  EVERY SATELLITE PASS OVER THE REGION  ·  CFB WAINWRIGHT  ·  OCT. 12–18, 2026",color=GOLD,fontsize=14,fontweight="bold")
fig.text(0.03,0.905,"A week of satellite passes: fire near the base on three days",color=CREAM,fontsize=31,fontweight="black")
fig.text(0.03,0.872,"Each mark is one pass. Grey: no fire detected within 8 km of the base. Colour: fire detected there. Mountain Time.",color=MUTED,fontsize=14)
def panel(ax,x0,x1,major,fmt,minor=None,label_hits=True):
    ax.set_facecolor(PANEL)
    for s in ax.spines.values(): s.set_visible(False)
    # night shading (approx sunset 6:45 p.m., sunrise 8:00 a.m. MDT)
    d=x0.replace(hour=0,minute=0)-dt.timedelta(days=1)
    while d<x1:
        ax.axvspan(d+dt.timedelta(hours=18,minutes=45),d+dt.timedelta(days=1,hours=8),color="#140E0A",zorder=0,lw=0); d+=dt.timedelta(days=1)
    for i,(k,lab) in enumerate(ROWS):
        y=len(ROWS)-i
        ax.axhline(y,color=GRID,lw=1,zorder=1)
        for p in P:
            if rowof(p["s"])!=k or not (x0<=p["t0"]<=x1): continue
            hit=HITS.get((k if k!="MODIS" else "",p["t0"].strftime("%Y-%m-%d"))) if p["base"] else None
            if p["base"] and k!="MODIS":
                t,c,n=HITS[(k,p["t0"].strftime("%Y-%m-%d"))]
                ax.scatter([t],[y],s=260,color=c,zorder=4,edgecolor=BG,lw=1.5)
            else:
                ax.scatter([p["t0"]],[y],s=60,facecolor="none",edgecolor=NONE,lw=1.6,zorder=3)
    ax.set_yticks(range(1,len(ROWS)+1)); ax.set_yticklabels([l for _,l in ROWS][::-1],color=CREAM,fontsize=12.5)
    ax.set_ylim(0.3,len(ROWS)+1.0); ax.set_xlim(x0,x1)
    ax.xaxis.set_major_locator(major); ax.xaxis.set_major_formatter(md.DateFormatter(fmt))
    if minor: ax.xaxis.set_minor_locator(minor)
    ax.tick_params(axis="x",colors=MUTED,labelsize=12,length=0); ax.tick_params(axis="y",length=0)
    ax.grid(axis="x",color=GRID,lw=1,which="major")
# Panel 1: week
a1=fig.add_axes([0.20,0.50,0.77,0.32])
x0,x1=dt.datetime(2026,10,12),dt.datetime(2026,10,18,23,59)
panel(a1,x0,x1,md.DayLocator(),"%a %b %d")
for lab in a1.get_xticklabels(): lab.set_horizontalalignment("left")
# Landsat row markers manually (row 0.55)
a1.scatter([dt.datetime(2026,10,17,12,17)],[0.75],s=220,marker="s",color=YEL,zorder=4,edgecolor=BG)
a1.text(dt.datetime(2026,10,17,12,17)-dt.timedelta(hours=3),0.75,"Landsat 8, 59 detections",color=YEL,fontsize=11.5,fontweight="bold",ha="right",va="center")
def ann(ax,t,y,txt,c,dx,dy,ha="left"):
    ax.annotate(txt,(t,y),xytext=(t+dx,y+dy),color=c,fontsize=12,fontweight="bold",ha=ha,va="center",arrowprops=dict(arrowstyle="-",color=c,lw=1.2))
ann(a1,dt.datetime(2026,10,14,14,51),3,"Oct. 14, 2:51 p.m.\n1 detection, 2.7 km SW",C14,dt.timedelta(hours=-30),0.55)
ann(a1,dt.datetime(2026,10,17,14,49),4,"Oct. 17, 2:49 p.m.\n8 detections",VI,dt.timedelta(hours=-34),0.45)
ann(a1,dt.datetime(2026,10,18,14,20),2.6,"Oct. 18, 2:12 & 2:32 p.m.\n1 each, ~5 km SE",ORG,dt.timedelta(hours=-58),-1.05)
a1.plot([dt.datetime(2026,10,18,14,12),dt.datetime(2026,10,18,14,20)],[2,2.6],color=ORG,lw=1.2)
a1.plot([dt.datetime(2026,10,18,14,32),dt.datetime(2026,10,18,14,20)],[4,2.6],color=ORG,lw=1.2)
fig.text(0.03,0.835,"OCT. 12 TO 18",color=GOLD,fontsize=13,fontweight="bold")
# Panel 2: zoom
fig.text(0.03,0.425,"ZOOM: MIDNIGHT OCT. 16–17 TO 6 A.M. OCT. 18",color=GOLD,fontsize=13,fontweight="bold")
a2=fig.add_axes([0.20,0.115,0.77,0.29])
z0,z1=dt.datetime(2026,10,17,0),dt.datetime(2026,10,18,6)
panel(a2,z0,z1,md.HourLocator(byhour=[0,4,8,12,16,20]),"%-I %p")
labs=a2.get_xticklabels()
a2.scatter([dt.datetime(2026,10,17,12,17)],[0.75],s=220,marker="s",color=YEL,zorder=4,edgecolor=BG)
a2.text(dt.datetime(2026,10,17,11,50),0.75,"Landsat 8, 12:17 p.m.",color=YEL,fontsize=11.5,fontweight="bold",ha="right",va="center")
g0,g1=dt.datetime(2026,10,17,14,49),dt.datetime(2026,10,17,16,0)
a2.axvspan(g0,g1,color="#5A2A1A",alpha=0.55,zorder=0.5,lw=0)
a2.axvline(g1,color=CREAM,lw=2,zorder=2)
a2.text(g1+dt.timedelta(minutes=12),3.6,"≈ 4 p.m.: wind turns NW;\na fire reaches C Company",color=CREAM,fontsize=11.5,fontweight="bold",va="top")
a2.text(g1-dt.timedelta(minutes=4),0.42,"last detection\n2:49 p.m.",color="#E8A37C",fontsize=10.5,fontweight="bold",ha="right",va="bottom")
a2.text(dt.datetime(2026,10,17,4,0),4.75,"Overnight passes, Oct. 17:\nno fire at the base",color=MUTED,fontsize=11.5,va="top",ha="center")
a2.text(dt.datetime(2026,10,18,3,30),4.75,"Overnight passes, Oct. 18:\nno fire at the base",color=MUTED,fontsize=11.5,va="top",ha="center")
a2.text(dt.datetime(2026,10,17,15,45),4.75,"Other daytime passes, incl. 3:15 & 3:33 p.m.:\nno detection at the base (cloudy nearby)",color=MUTED,fontsize=11,va="top",ha="right")
# footer
fy=0.0; fig.patches.append(Rectangle((0,0),1,0.075,transform=fig.transFigure,facecolor=NAVY))
fig.patches.append(Rectangle((0,0.075),1,0.004,transform=fig.transFigure,facecolor=GOLD))
fig.text(0.03,0.048,"Data: NASA FIRMS 7-day files, all sensors, downloaded 10:09 p.m. MT Oct. 18. Passes shown are those that detected fire within 1,000 km;",color=CREAM,fontsize=11.3)
fig.text(0.03,0.025,"coverage of the base is inferred. Cloud or smoke can hide fire; MODIS misses small fires. Landsat shown for Oct. 17 only. Shaded = night. Graphic: Prime Rogue Inc.",color=CREAM,fontsize=11.3)
fig.savefig(sys.argv[1],facecolor=BG,dpi=100)
im=Image.open(sys.argv[1]).convert("RGBA")
logo=Image.open("/mnt/user-data/uploads/logo_transparent_prime_rogue_inc_512_by_512_1.png").convert("RGBA").resize((80,80),Image.LANCZOS)
im.alpha_composite(logo,(1600-80-30,1160-80-3)); im.convert("RGB").save(sys.argv[2],quality=90,optimize=True); print(im.size)
