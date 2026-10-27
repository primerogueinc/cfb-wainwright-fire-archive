import sys, math; sys.path.insert(0,'..'); sys.path.insert(0,'../vis')
from pr import *
from pr import _LOGO
import rasterio
from rasterio.warp import reproject, Resampling as RS
from rasterio.transform import from_bounds as tfb
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.colors import LinearSegmentedColormap, LightSource
from matplotlib.patches import Wedge
from shapely.geometry import box as _box
for n in ["Inter-Medium.otf","Inter-Bold.otf"]: fm.fontManager.addfont(F+n)
plt.rcParams["font.family"]="Inter"
hx=lambda c:"#%02x%02x%02x"%c
CM=LinearSegmentedColormap.from_list("rg",["#7a1f1f","#e0603c","#e8c15a","#40e0d0"])
df=pd.read_csv("perm.csv.gz"); f=df[df.cue=="FAN"].copy(); f["dir"]=f.strategy.str[3:].astype(int)
W_,E_,S_,N_=-110.918,-110.889,52.763,52.780; lat0=52.7715; kx=111320*math.cos(math.radians(lat0)); ky=111200
nx=600; ny=int(nx*(N_-S_)*ky/((E_-W_)*kx))
dem=rasterio.open('../mrdem10.tif'); z=np.full((ny,nx),np.nan,'float32'); T=tfb(W_,S_,E_,N_,nx,ny)
reproject(rasterio.band(dem,1),z,src_transform=dem.transform,src_crs=dem.crs,src_nodata=-9999,dst_transform=T,dst_crs='EPSG:4326',dst_nodata=np.nan,resampling=RS.bilinear)
hs=LightSource(azdeg=315,altdeg=35).hillshade(z,vert_exag=8,dx=(E_-W_)/nx*kx,dy=(N_-S_)/ny*ky)
PT={"A":(52.7728,-110.9063),"B":(52.7705,-110.8996)}
fig,axs=plt.subplots(1,2,figsize=(17,8.4),facecolor=hx(BG))
for ax,sp in zip(axs,["jog in kit (8 km/h)","in smoke (3 km/h)"]):
    ext=(W_,E_,S_,N_); ax.imshow(z,extent=ext,cmap='gist_earth',vmin=645,vmax=695); ax.imshow(hs,extent=ext,cmap='gray',alpha=0.5)
    xs=np.linspace(W_,E_,nx); ys=np.linspace(N_,S_,ny); ax.contour(xs,ys,z,levels=np.arange(645,700,5),colors='#2a1d15',linewidths=0.5,alpha=0.7)
    gpd.GeoSeries([scar_main()],crs=4326).boundary.plot(ax=ax,color=hx(RED),linewidth=2.2)
    gpd.GeoSeries([preshift_hull()],crs=4326).plot(ax=ax,color=hx(YEL),alpha=0.25,edgecolor=hx(YEL),linewidth=1.5)
    o=osm(); o=o[o.intersects(_box(W_,S_,E_,N_))]
    for _,r in o[o.kind=='road'].iterrows(): gpd.GeoSeries([r.geometry],crs=4326).plot(ax=ax,color='#f2ecdf',linewidth=1.3,alpha=0.9)
    # wedges in lon/lat with aspect correction: draw in a metric-ish frame by scaling lon
    for k,(lat,lon) in PT.items():
        q=f[(f.point==k)&(f.speed==sp)].groupby("dir").success.mean()
        for dg,v in q.items():
            Rm=245
            th1=90-dg-2.5; th2=90-dg+2.5
            pts=[(lon,lat)]+[(lon+Rm*math.cos(math.radians(t))/kx, lat+Rm*math.sin(math.radians(t))/ky) for t in np.linspace(th1,th2,6)]
            ax.add_patch(plt.Polygon(pts,closed=True,facecolor=CM(v),edgecolor='none',alpha=0.88,zorder=5))
        ax.plot(lon,lat,'o',ms=20,mfc='#111',mec='white',mew=2.2,zorder=6); ax.text(lon,lat,k,color='white',fontsize=12,fontweight='bold',ha='center',va='center',zorder=7)
    ax.set_xlim(W_,E_); ax.set_ylim(S_,N_); ax.set_aspect(1/math.cos(math.radians(lat0))); ax.axis('off')
    ax.set_title(("Jogging in kit, 8 km/h" if sp.startswith("jog") else "Slowed by smoke, 3 km/h"),color=hx(CREAM),fontsize=15,fontweight="bold",loc="left")
    # wind arrow
    ax.annotate('',xy=(-110.9135,52.7752),xytext=(-110.9168,52.7772),arrowprops=dict(arrowstyle='-|>',color=hx(RED),lw=3,mutation_scale=22))
    ax.text(-110.9172,52.7779,"wind after the shift",color=hx(CREAM),fontsize=10.5,fontweight='bold')
plt.subplots_adjust(left=0.01,right=0.99,top=0.93,bottom=0.02,wspace=0.03)
fig.savefig("_fan.png",dpi=100,facecolor=hx(BG)); plt.close(fig)
# colorbar strip
cb=Image.new("RGBA",(700,70),BG+(255,)); cd=ImageDraw.Draw(cb)
for i in range(600):
    c=tuple(int(255*x) for x in CM(i/599)[:3]); cd.line([(50+i,10),(50+i,34)],fill=c)
for v,x in ((0,50),(50,350),(100,650)): cd.text((x,40),f"{v}%",font=M(16),fill=CREAM,anchor="ma")
im,d=canvas(1800,250+840+90+150,"THE AUTHENTIC STOIC STRESS TEST  ·  PART 4  ·  WHICH WAY TO RUN","The way out was east. North and west led back into the fire",
 "Each wedge: share of 30 fire scenarios in which heading that way from A (Range 2) or B (the road's end) reaches safe ground, starting 2 minutes after flames\ncame into sight. East, across the wind, reaches unburned ground most often; southeast, with the wind, less often; north and west almost never.")
im.alpha_composite(Image.open("_fan.png").convert("RGBA"),(54,200)); im.alpha_composite(cb,(54,200+850))
d.text((54+720,200+858),"chance of reaching safe ground with 3+ minutes to spare",font=M(17),fill=MUTED)
footer(im,["Elevation: NRCan MRDEM-30. Roads: (c) OpenStreetMap contributors (ODbL). Burn scar: Copernicus Sentinel-2. Model as in the escape matrix; best case, no embers or spotting.",
           "Locations are estimates. Data: github.com/primerogueinc/cfb-wainwright-fire-archive. Graphic: Kevin Duska Jr. (Prime Rogue Inc.)"])
im.convert("RGB").save("../vis/cfb-wainwright-escape-directions.jpg",quality=92,optimize=True); print(im.size)
