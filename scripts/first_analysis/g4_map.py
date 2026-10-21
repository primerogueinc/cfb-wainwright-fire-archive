import sys,csv,numpy as np; sys.path.insert(0,'.')
from style import *
from PIL import ImageEnhance
from matplotlib.patches import Rectangle
N,S,E_,Wl=52.83844698864907,52.52791908000258,-110.47096252441406,-111.21665954589845
img=Image.open('../cop/b5/2026-10-04-00_00_2026-10-04-23_59_Sentinel-2_L1C_True_color.jpg').convert('RGB')
img=ImageEnhance.Contrast(img).enhance(1.15); a=np.asarray(img)
lo0,lo1,la0,la1=-111.02,-110.80,52.715,52.832
W,H=1600,1230
fig=frame(W,H,"SATELLITE MAP  ·  CFB WAINWRIGHT TRAINING AREA  ·  OCT. 17–18, 2026","Fire on the range, hours before 4 p.m.",
  "Fire detections on Oct. 17 and the new burned area seen Oct. 18, on a cloud-free Sentinel-2 image from Oct. 4.")
ax=fig.add_axes([0.03,0.115,0.62,0.76])
kx=np.cos(np.deg2rad(52.77))
ax.imshow(a,extent=[Wl,E_,S,N],aspect=1/kx)
ax.set_xlim(lo0,lo1); ax.set_ylim(la0,la1); ax.set_xticks([]); ax.set_yticks([])
[s.set_color(GOLD) for s in ax.spines.values()]
# S3 scar
g=np.load('../s3/grid.npy'); p=np.load('../s3/patch_0.8.npy')
ny,nx=p.shape; lats=np.linspace(g[1],g[0],ny); lons=np.linspace(g[2],g[3],nx)
# check orientation: assume row0 = north
ax.contour(lons,lats,p.astype(float),levels=[0.5],colors=[RED],linewidths=3,linestyles='--')
rows=list(csv.DictReader(open('/home/claude/firms-raw-package/cfb-wainwright-firms-detections.csv')))
dkm=lambda km_lon,km_lat:(km_lon/(111.32*kx),km_lat/110.57)
for r in rows:
    t=r['detection_time_mdt']; la,lo=float(r['latitude']),float(r['longitude'])
    if 'VIIRS' in r['sensor'] and t.startswith('2026-10-17'):
        dx,dy=dkm(float(r['scan_km']),float(r['track_km']))
        ax.add_patch(Rectangle((lo-dx/2,la-dy/2),dx,dy,fc=BLUE+'40',ec=BLUE,lw=2.2,zorder=4))
for r in rows:
    if 'Landsat' in r['sensor']:
        ax.plot(float(r['longitude']),float(r['latitude']),'s',color=YEL,ms=5,zorder=6)
# GOES pixel centres
gp=[(52.792,-110.906,"3:10"),(52.794,-110.867,"3:30"),(52.754,-110.896,"3:30–3:40")]
for la,lo,tt in gp:
    ax.plot(lo,la,'o',ms=22,mfc='none',mec=CREAM,mew=2.5,zorder=7); ax.plot(lo,la,'+',ms=14,color=CREAM,mew=2.5,zorder=7)
def lab(lo,la,t,c=CREAM,ha='left',fs=13):
    ax.text(lo,la,t,color=c,fontsize=fs,fontweight='bold',ha=ha,va='center',zorder=9,bbox=dict(boxstyle='round,pad=0.3',fc=BG,ec='none',alpha=.85))
lab(-110.913,52.797,"GOES-18, 3:10 p.m.",CREAM,"right")
lab(-110.862,52.803,"GOES-18, 3:30 p.m.","#FFFFFF","center")
lab(-110.883,52.748,"GOES-18, 3:30–3:40 p.m.")
lab(-110.915,52.758,"Jamieson Lake",'#BFD9F2','center',12)
lab(-110.903,52.7835,"Peterson Pond",'#BFD9F2','center',12)
lab(-111.012,52.775,"Landsat 8, 12:17 p.m.",YEL)
ax.annotate("",xy=(-110.942,52.772),xytext=(-110.972,52.775),arrowprops=dict(arrowstyle='->',color=YEL,lw=2),zorder=9)
lab(-111.012,52.808,"NOAA-20, 2:49 p.m.",BLUE)
ax.annotate("",xy=(-110.925,52.787),xytext=(-110.975,52.806),arrowprops=dict(arrowstyle='->',color=BLUE,lw=2),zorder=9)
lab(-110.872,52.770,"New burned area, Oct. 18\n(Sentinel-3, preliminary)",RED)
lab(-110.905,52.722,"Older scar, already\nthere Oct. 4",MUTED,"center",11)
# wind arrows
ax.annotate("",xy=(-110.985,52.738),xytext=(-111.008,52.725),arrowprops=dict(arrowstyle='-|>',color=CREAM,lw=4,mutation_scale=28))
ax.text(-111.012,52.721,"SW wind\nuntil ~3 p.m.",color=CREAM,fontsize=12,fontweight='bold',va='top')
ax.annotate("",xy=(-110.947,52.725),xytext=(-110.970,52.738),arrowprops=dict(arrowstyle='-|>',color=RED,lw=4,mutation_scale=28))
ax.text(-110.965,52.721,"NW wind\nby 4 p.m.",color=RED,fontsize=12,fontweight='bold',va='top')
# scale bar 2 km
x0=-110.835; L=2/(111.32*kx); ax.plot([x0,x0+L*0.999],[52.82,52.82],color=CREAM,lw=5); ax.text(x0+L/2,52.8235,"2 km",color=CREAM,ha='center',fontsize=13,fontweight='bold')
ax.annotate("N",xy=(-110.81,52.829),xytext=(-110.81,52.815),color=CREAM,ha='center',fontsize=15,fontweight='bold',arrowprops=dict(arrowstyle='-|>',color=CREAM,lw=2.5))
# legend panel
X=0.675; y=0.845
items=[(YEL,"s","Landsat 8 · 12:17 p.m.","59 detections, 30 m pixels, in a band about\n1.9 km long, running SW to NE."),
 (BLUE,"b","NOAA-20 · 2:49 p.m.","8 detections, 5.8–11.5 MW. Boxes are sensor\npixels; they overstate the area burning."),
 (CREAM,"o","GOES-18 · 3:10–3:40 p.m.","Fire pixels every 10 min. Each covers several\nkm, so the marks are centres, not locations.\nPrime Rogue analysis; rated \"likely\"."),
 (RED,"d","Burned area · Oct. 18","Darkened since Oct. 4 on Sentinel-3 (300 m).\nAbout 7.5–8.3 km², SE of the detections.\nPreliminary until a sharper image."),]
for c,k,h,b in items:
    if k=="s": fig.patches.append(Rectangle((X,y-0.009),0.012,0.012,transform=fig.transFigure,fc=c))
    if k=="b": fig.patches.append(Rectangle((X,y-0.009),0.012,0.012,transform=fig.transFigure,fc=c+'40',ec=c,lw=2))
    if k=="o": fig.text(X+0.006,y-0.003,"⊕",color=c,fontsize=18,ha='center',va='center')
    if k=="d": fig.lines.append(plt.Line2D([X,X+0.014],[y-0.003,y-0.003],transform=fig.transFigure,color=c,lw=3,ls='--'))
    fig.text(X+0.022,y,h,color=c,fontsize=16,fontweight='black',va='center')
    fig.text(X+0.022,y-0.022,b,color=CREAM,fontsize=13,va='top',linespacing=1.45); y-=0.022+0.022*len(b.split("\n"))+0.045
fig.text(X,y,"What the map does not show",color=GOLD,fontsize=16,fontweight='black',va='center')
fig.text(X,y-0.022,"Where C Company was. What started the fire.\nThe fire's edge between 2:49 and 4 p.m.\nSatellites detect heat, not cause.",color=CREAM,fontsize=13,va='top',linespacing=1.45)
footer(fig,H,["Imagery: Copernicus Sentinel-2 (Oct. 4) and Sentinel-3 (Oct. 4 vs Oct. 18); contains modified Copernicus Sentinel data 2026. Fire data: NASA FIRMS; NOAA GOES-18 ABI fire product.",
 "Wind: ECCC, CFB Wainwright station. Lake names: Canadian Geographical Names Database. Positions accurate to roughly 100–375 m (Landsat, VIIRS)."])
save(fig,'g4.png','/home/claude/cfb-wainwright-detection-map.jpg',W,H)
