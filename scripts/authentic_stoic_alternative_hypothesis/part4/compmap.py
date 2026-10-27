import sys, math; sys.path.insert(0,'..'); sys.path.insert(0,'../vis')
from pr import *
from pr import _LOGO
import rasterio
from rasterio.warp import reproject, Resampling as RS
from rasterio.transform import from_bounds as tfb
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.colors import LinearSegmentedColormap, LightSource
from shapely.geometry import box as _box
from scipy.spatial import cKDTree
for n in ["Inter-Medium.otf","Inter-Bold.otf"]: fm.fontManager.addfont(F+n)
plt.rcParams["font.family"]="Inter"
hx=lambda c:"#%02x%02x%02x"%c
CM=LinearSegmentedColormap.from_list("rg",["#7a1f1f","#e0603c","#e8c15a","#40e0d0"])
s=pd.read_csv("surface.csv")
ll=gpd.GeoSeries(gpd.points_from_xy(s.x,s.y),crs=3400).to_crs(4326); s["lon"]=ll.x; s["lat"]=ll.y
import shapely as _sh
_h=preshift_hull(); s=s[~_sh.contains_xy(_h.buffer(0.0004),s.lon.values,s.lat.values)].reset_index(drop=True)
z2=pd.read_csv(REPO+"data/authentic-stoic-stress-test/part2/part2_core_frequency.csv"); z2=z2[z2.n_scenarios_in_core>0]
zp=gpd.GeoSeries(gpd.points_from_xy(z2.x,z2.y),crs=4326).to_crs(3400)
tree=cKDTree(np.c_[s.x,s.y]); _,idx=tree.query(np.c_[zp.x,zp.y]); w=z2.n_scenarios_in_core.values
W_,E_,S_,N_=-110.928,-110.884,52.754,52.783; lat0=52.768; kx=111320*math.cos(math.radians(lat0)); ky=111200
nx=520; ny=int(nx*(N_-S_)*ky/((E_-W_)*kx))
dem=rasterio.open('../mrdem10.tif'); z=np.full((ny,nx),np.nan,'float32'); T=tfb(W_,S_,E_,N_,nx,ny)
reproject(rasterio.band(dem,1),z,src_transform=dem.transform,src_crs=dem.crs,src_nodata=-9999,dst_transform=T,dst_crs='EPSG:4326',dst_nodata=np.nan,resampling=RS.bilinear)
hs=LightSource(azdeg=315,altdeg=35).hillshade(z,vert_exag=8,dx=(E_-W_)/nx*kx,dy=(N_-S_)/ny*ky)
scar=scar_main(); hull=preshift_hull()
o=osm(); o=o[o.intersects(_box(W_,S_,E_,N_))]
zone=gpd.GeoSeries([p.buffer(0.00045,cap_style=3) for p in gpd.points_from_xy(z2.x,z2.y)],crs=4326).unary_union.buffer(0.0002).buffer(-0.0002)
COLS=[("gust","Moved at the 3:16 gust"),("within500","Moved when the fire was 500 m away"),("within200","Moved when the fire was 200 m away")]
ROWS=[("jog","Clear air, jogging in kit (8 km/h)"),("smoke","In smoke (3 km/h)")]
PT={"A":(52.7728,-110.9063),"B":(52.7705,-110.8996)}
fig,axs=plt.subplots(2,3,figsize=(18,13.2),facecolor=hx(BG))
stats={}
for i,(rk,rl) in enumerate(ROWS):
    for j,(ck,cl) in enumerate(COLS):
        ax=axs[i,j]; col=f"{ck}_{rk}"
        ext=(W_,E_,S_,N_); ax.imshow(hs,extent=ext,cmap='gray',alpha=1.0); ax.imshow(z,extent=ext,cmap='gist_earth',vmin=645,vmax=695,alpha=0.35)
        ax.scatter(s.lon,s.lat,c=s[col],cmap=CM,vmin=0,vmax=1,s=92,marker='s',linewidths=0,alpha=0.92)
        gpd.GeoSeries([scar],crs=4326).boundary.plot(ax=ax,color='white',linewidth=1.4,alpha=0.8)
        gpd.GeoSeries([hull],crs=4326).boundary.plot(ax=ax,color=hx(YEL),linewidth=1.6,linestyle='--')
        gpd.GeoSeries([zone],crs=4326).boundary.plot(ax=ax,color='white',linewidth=2.4,linestyle=(0,(5,3)))
        for _,r in o[o.kind=='road'].iterrows(): gpd.GeoSeries([r.geometry],crs=4326).plot(ax=ax,color='#f2ecdf',linewidth=1,alpha=0.8)
        for k,(la,lo) in PT.items():
            ax.plot(lo,la,'o',ms=15,mfc='#111',mec='white',mew=1.8,zorder=6); ax.text(lo,la,k,color='white',fontsize=9.5,fontweight='bold',ha='center',va='center',zorder=7)
        v=np.average(s[col].values[idx]>=0.5,weights=w)*100; stats[(rk,ck)]=v
        ax.text(0.03,0.04,f"{v:.0f}%",transform=ax.transAxes,color='white',fontsize=30,fontweight='bold',va='bottom',bbox=dict(facecolor='#111',edgecolor='none',alpha=0.8,pad=6))
        ax.text(0.03,0.155,"of the likely zone had\nbetter-than-even odds",transform=ax.transAxes,color='white',fontsize=11,va='bottom',bbox=dict(facecolor='#111',edgecolor='none',alpha=0.8,pad=4))
        ax.set_xlim(W_,E_); ax.set_ylim(S_,N_); ax.set_aspect(1/math.cos(math.radians(lat0))); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel('')
        if j>0: ax.set_ylabel('')
        for s_ in ax.spines.values(): s_.set_color('#35281f')
        if i==0: ax.set_title(cl,color=hx(GOLD),fontsize=15,fontweight='bold',pad=10)
        if j==0: ax.set_ylabel(rl,color=hx(CREAM),fontsize=14,fontweight='bold',labelpad=10)
        if i==0 and j==0:
            ax.annotate('',xy=(-110.9215,52.7785),xytext=(-110.9262,52.7812),arrowprops=dict(arrowstyle='-|>',color=hx(RED),lw=3,mutation_scale=20))
            ax.text(-110.9268,52.7818,"wind after the shift",color='white',fontsize=10,fontweight='bold')
plt.subplots_adjust(left=0.04,right=0.995,top=0.95,bottom=0.01,wspace=0.03,hspace=0.07)
fig.savefig("_comp.png",dpi=100,facecolor=hx(BG)); plt.close(fig)
cb=Image.new("RGBA",(700,70),BG+(255,)); cd=ImageDraw.Draw(cb)
for k_ in range(600):
    c_=tuple(int(255*x) for x in CM(k_/599)[:3]); cd.line([(50+k_,10),(50+k_,34)],fill=c_)
for v_,x_ in ((0,50),(50,350),(100,650)): cd.text((x_,40),f"{v_}%",font=M(16),fill=CREAM,anchor="ma")
cp=Image.open("_comp.png").convert("RGBA"); cp=cp.resize((1692,int(cp.size[1]*1692/cp.size[0])),Image.LANCZOS)
im,d=canvas(1800,250+cp.size[1]+90+150,"THE AUTHENTIC STOIC STRESS TEST  ·  PART 4  ·  COULD THEY HAVE GOT OUT?","Where you could have survived depended on when you moved",
 "Each square: chance that someone starting there reaches safe ground on foot, by the best route, with 3+ minutes to spare, across 30 fire scenarios.\nAll leave 2 minutes after the cue. White dashed: the likely zone from part 2. Yellow dashed: the fire before the wind turned.")
im.alpha_composite(cp,(54,200)); im.alpha_composite(cb,(54,200+cp.size[1]+8))
d.text((54+720,200+cp.size[1]+16),"chance of reaching unburned or already-burned ground",font=M(17),fill=MUTED)
footer(im,["Model: FBP grass spread on the mapped burn (5 winds x 3 spread rates x steady/gusty flanks); escape on foot, slope-adjusted, 72 straight routes. Best case: no embers,",
           "spot fires or smoke inhalation. Locations are estimates. Elevation: NRCan MRDEM-30. Data: github.com/primerogueinc/cfb-wainwright-fire-archive. Graphic: Kevin Duska Jr. (Prime Rogue Inc.)"])
im.convert("RGB").save("../vis/cfb-wainwright-escape-comparison.jpg",quality=92,optimize=True); print(im.size, {k:round(v) for k,v in stats.items()})
