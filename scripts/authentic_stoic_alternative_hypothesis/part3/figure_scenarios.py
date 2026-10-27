import sys, math; sys.path.insert(0,'vis')
from pr import *
from pr import _LOGO
import rasterio, shapely
from shapely.geometry import Point, LineString
from rasterio.warp import reproject, Resampling as RS
from rasterio.transform import from_bounds as tfb
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.colors import LightSource
for n in ["Inter-Medium.otf","Inter-Bold.otf"]: fm.fontManager.addfont(F+n)
plt.rcParams["font.family"]="Inter"
hx=lambda c:"#%02x%02x%02x"%c
C="EPSG:3400"
SC={"A":("Range 2 (on the rise)",52.7728,-110.9063),"B":("Road's end (in the hollow)",52.7705,-110.8996),
    "C":("Strip north of Jamieson Lake",52.7640,-110.9160),"D":("Range road, south",52.7628,-110.8995),"E":("South-central run",52.7530,-110.8990)}
scar=scar_main(); hull=preshift_hull()
s3=gpd.GeoSeries([scar],crs=4326).to_crs(C).iloc[0]; h3=gpd.GeoSeries([hull],crs=4326).to_crs(C).iloc[0]
dem=rasterio.open('mrdem10.tif'); Zd=dem.read(1).astype(float); Zd[Zd<-9000]=np.nan
def z3(x,y): r,c=dem.index(x,y); return Zd[r,c]
# scenario numbers
sv=pd.read_csv('scenario_visibility.csv'); sv['key']=sv.scenario.str[0]
rows={}
for k,(nm,lat,lon) in SC.items():
    p=gpd.GeoSeries([Point(lon,lat)],crs=4326).to_crs(C).iloc[0]
    q=sv[sv.key==k]
    arr=q.arrival_min_after_3pm; sw=q.sight_warning_min
    du=0 if not s3.contains(p) else s3.exterior.distance(p)
    rows[k]=dict(name=nm,arr=(int(arr.min()),int(arr.max())),sw=(int(sw.min()),int(sw.max())),unb=int(round(du)),edge=int(round(h3.exterior.distance(p))),elev=int(round(z3(p.x,p.y))),p=p)
    print(k,rows[k]['arr'],rows[k]['sw'],rows[k]['unb'],rows[k]['edge'],rows[k]['elev'])
# ---- map
W_,E_,S_,N_=-110.940,-110.880,52.746,52.788
nx,ny=600,int(600*(N_-S_)*111.2/((E_-W_)*111.32*math.cos(math.radians(52.767))))
z=np.full((ny,nx),np.nan,'float32'); T=tfb(W_,S_,E_,N_,nx,ny)
reproject(rasterio.band(dem,1),z,src_transform=dem.transform,src_crs=dem.crs,src_nodata=-9999,dst_transform=T,dst_crs='EPSG:4326',dst_nodata=np.nan,resampling=RS.bilinear)
ls=LightSource(azdeg=315,altdeg=35); dx=(E_-W_)/nx*111320*math.cos(math.radians(52.767)); dy=(N_-S_)/ny*111200
hs=ls.hillshade(z,vert_exag=8,dx=dx,dy=dy)
zv=pd.read_csv('zone_visibility.csv')
fig=plt.figure(figsize=(11,11*ny/nx),dpi=150,facecolor=hx(BG)); ax=fig.add_axes([0,0,1,1])
ext=(W_,E_,S_,N_)
ax.imshow(z,extent=ext,cmap='gist_earth',vmin=645,vmax=695); ax.imshow(hs,extent=ext,cmap='gray',alpha=0.5)
xs=np.linspace(W_,E_,nx); ys=np.linspace(N_,S_,ny)
cs=ax.contour(xs,ys,z,levels=np.arange(645,700,5),colors='#2a1d15',linewidths=[1.3 if l%10==0 else 0.5 for l in np.arange(645,700,5)],alpha=0.75)
ax.clabel(cs,levels=[l for l in cs.levels if l%10==0],fmt='%d m',fontsize=8,colors='#2a1d15')
gpd.GeoSeries([scar],crs=4326).boundary.plot(ax=ax,color=hx(RED),linewidth=2.4)
gpd.GeoSeries([hull],crs=4326).plot(ax=ax,color=hx(YEL),alpha=0.28,edgecolor=hx(YEL),linewidth=2,linestyle='--')
m=zv.n_scenarios_in_core>=1
ax.scatter(zv.x[m&zv.sees_fire_edge],zv.y[m&zv.sees_fire_edge],s=9,marker='s',c=hx(TEAL),alpha=0.85,linewidths=0)
ax.scatter(zv.x[m&~zv.sees_fire_edge],zv.y[m&~zv.sees_fire_edge],s=9,marker='s',c='#ff4fa3',alpha=0.85,linewidths=0)
# profile line
PA=rows['A']['p']; PB=rows['B']['p']
v=np.array([PB.x-PA.x,PB.y-PA.y]); v/=np.linalg.norm(v)
# start where line backwards meets hull
st=None
for s in range(0,3000,10):
    q=Point(PA.x-s*v[0],PA.y-s*v[1])
    if h3.contains(q): st=q; break
en=Point(PB.x+500*v[0],PB.y+500*v[1])
prof=gpd.GeoSeries([LineString([st,en])],crs=C).to_crs(4326).iloc[0]
ax.plot(*prof.xy,color='white',lw=2.2,ls=(0,(6,4)))
for k,r in rows.items():
    ll=gpd.GeoSeries([r['p']],crs=C).to_crs(4326).iloc[0]
    ax.plot(ll.x,ll.y,'o',ms=24,mfc='#111',mec='white',mew=2.5,zorder=5)
    ax.text(ll.x,ll.y,k,color='white',fontsize=14,fontweight='bold',ha='center',va='center',zorder=6)
from shapely.geometry import box as _box
_o=osm(); _o=_o[_o.intersects(_box(W_,S_,E_,N_))]
for _,f in _o[_o.kind=='road'].iterrows():
    gpd.GeoSeries([f.geometry],crs=4326).plot(ax=ax,color='#f2ecdf',linewidth=1.6 if f.highway!='track' else 1.0,linestyle='-' if f.highway!='track' else (0,(4,3)),alpha=0.9,zorder=3)
for _,f in _o[(_o.military=='range')].iterrows():
    gpd.GeoSeries([f.geometry],crs=4326).boundary.plot(ax=ax,color='#4f8dd6',linewidth=2.2,zorder=4)
    c=f.geometry.representative_point()
    if W_<c.x<E_ and S_<c.y<N_:
        ax.text(c.x+0.0012,c.y+0.0009,f['name'],color='white',fontsize=10.5,fontweight='bold',zorder=7,bbox=dict(facecolor='#1e3a5f',edgecolor='none',pad=2.5,alpha=0.9))
ax.text(-110.9155,52.7535,'Jamieson Lake',color='#dfe9f5',fontsize=12,style='italic',ha='center',zorder=7)
ax.text(-110.9035,52.7868,'Peterson Pond',color='#dfe9f5',fontsize=10,style='italic',ha='center',zorder=7)
# scale bar and north arrow
_kx=111320*math.cos(math.radians(52.767)); _x0=E_-0.0185; _y0=S_+0.0022
for i,(a,b) in enumerate([(0,250),(250,500),(500,1000)]):
    ax.add_patch(plt.Rectangle((_x0+a/_kx,_y0),(b-a)/_kx,0.00045,facecolor='white' if i%2==0 else '#111',edgecolor='white',lw=1,zorder=8))
for d_,t_ in [(0,'0'),(500,'500'),(1000,'1 km')]:
    ax.text(_x0+d_/_kx,_y0+0.0009,t_,color='white',fontsize=10.5,fontweight='bold',ha='center',zorder=8,bbox=dict(facecolor='#111',edgecolor='none',pad=1.5,alpha=0.6))
_nx,_ny=E_-0.0035,N_-0.0055
ax.annotate('',xy=(_nx,_ny+0.0035),xytext=(_nx,_ny),arrowprops=dict(arrowstyle='-|>',color='white',lw=2.5,mutation_scale=22),zorder=8)
ax.text(_nx,_ny+0.0042,'N',color='white',fontsize=14,fontweight='bold',ha='center',zorder=8)
ax.set_xlim(W_,E_); ax.set_ylim(S_,N_); ax.set_aspect(1/math.cos(math.radians(52.767))); ax.axis('off')
fig.savefig('_scen_map.png',dpi=150,facecolor=hx(BG),bbox_inches='tight',pad_inches=0); plt.close(fig)
# ---- profile chart
L=st.distance(en); dd=np.arange(0,L,10)
pz=np.array([z3(st.x+d*v[0],st.y+d*v[1]) for d in dd])
dA=st.distance(PA); dB=st.distance(PB)
fig=plt.figure(figsize=(11,3.4),dpi=150,facecolor=hx(BG)); ax=fig.add_axes([0.07,0.2,0.9,0.72]); ax.set_facecolor(hx(BG))
ax.fill_between(dd,640,pz,color='#5a4636'); ax.plot(dd,pz,color=hx(CREAM),lw=1.5)
zB=z3(PB.x,PB.y)+1.7
for fh,ls_,lab in [(2.5,'-','flames 2.5 m'),(6,'--','flames 6 m')]:
    ax.plot([0,dB],[pz[0]+fh,zB],color=hx(GOLD),lw=1.6,ls=ls_)
ax.plot([0],[pz[0]+6],marker='^',ms=14,color=hx(RED)); ax.text(20,pz[0]+7.5,"Fire's edge, 3:16 p.m.",color=hx(RED),fontsize=11,fontweight='bold')
for k,dk in (("A",dA),("B",dB)):
    zk=np.interp(dk,dd,pz); ax.plot(dk,zk+1.7,'o',ms=16,mfc='#111',mec='white',mew=2); ax.text(dk,zk+1.7,k,color='white',fontsize=10,fontweight='bold',ha='center',va='center')
ax.text(dB+30,zB+3,"Sightlines from a standing\nperson at B, in gold",color=hx(GOLD),fontsize=10)
ax.set_ylim(655,max(pz)+12); ax.set_xlim(0,L)
ax.set_ylabel("Elevation (m)",color=hx(MUTED),fontsize=10); ax.set_xlabel("Distance along the dashed line (m), 8x vertical exaggeration",color=hx(MUTED),fontsize=10)
ax.tick_params(colors=hx(MUTED),labelsize=9); [s_.set_color('#35281f') for s_ in ax.spines.values()]
fig.savefig('_scen_prof.png',dpi=150,facecolor=hx(BG)); plt.close(fig)
# ---- compose
mp=Image.open('_scen_map.png').convert('RGBA'); mp=mp.resize((1100,int(mp.size[1]*1100/mp.size[0])),Image.LANCZOS)
pf=Image.open('_scen_prof.png').convert('RGBA'); pf=pf.resize((1100,int(pf.size[1]*1100/pf.size[0])),Image.LANCZOS)
Wt=1800; Ht=250+mp.size[1]+20+pf.size[1]+150
im,d=canvas(Wt,Ht,"THE AUTHENTIC STOIC STRESS TEST  ·  PART 3  ·  TERRAIN AND SIGHTLINES","Behind a low rise: five places C Company could have been",
 "Shaded relief with 5 m contours. Blue: ranges as mapped in OpenStreetMap (not verified by DND); white: roads and tracks. Squares: ground our 20 readings point to. Teal: a standing\nperson could see the fire's edge at 3:16 p.m. Pink: a rise of about 10 m hid it. Red: burn scar. Yellow: the fire before the wind turned.")
im.alpha_composite(mp,(54,214)); im.alpha_composite(pf,(54,214+mp.size[1]+20))
X=54+1100+40; y=230
d.text((X,y),"The five scenarios",font=K(25),fill=GOLD); y+=44
for k,r in rows.items():
    d.ellipse([X,y+2,X+30,y+32],fill=INK,outline=(255,255,255),width=2); d.text((X+15,y+17),k,font=B(16),fill=CREAM,anchor="mm")
    d.text((X+42,y+2),r['name'],font=B(19),fill=CREAM); y+=32
    a0,a1=r['arr']; s0,s1=r['sw']
    hm=lambda t: f"{3+(15*60+t)//60-15}:{(15*60+t)%60:02d}"
    lines=[f"Fire arrives about {hm(a0)}-{hm(a1)} p.m.",
           f"Flames in sight {s0}-{s1} min before",
           ("Unburned ground: next to it" if r['unb']<40 else f"Unburned ground: {r['unb']} m")]
    for l in lines: d.text((X+42,y),l,font=M(17),fill=MUTED); y+=24
    y+=14
y+=6
d.text((X,y),"What it means",font=K(22),fill=GOLD); y+=36
for l in ["Most of the likeliest ground sat","behind the rise: 46-63% of it could","not see the fire's edge, depending","on flame height. Nothing hid the","smoke, or the 82 km/h gust at 3:16."]:
    d.text((X,y),l,font=M(17),fill=CREAM); y+=24
y+=12
for l in ["Arrival and warning times span five","wind schedules at 8 km/h spread.","30 m terrain model; vegetation, vehicles","and berms are not included."]:
    d.text((X,y),l,font=M(15),fill=MUTED); y+=21
footer(im,["Elevation: NRCan MRDEM-30 (OGL - Canada). Ranges, roads: (c) OpenStreetMap contributors (ODbL). Burn scar: Sentinel-2 (Copernicus). Fire: NASA FIRMS.",
           "Spread: FBP grass ellipse, CZWN winds. Sightlines: eye 1.7 m, flames 2.5 m (6 m dashed). Locations are estimates, not confirmed by DND.",
           "Data: github.com/primerogueinc/cfb-wainwright-fire-archive. Graphic: Kevin Duska Jr. (Prime Rogue Inc.)"],fh=128)
im.convert('RGB').save('vis/cfb-wainwright-scenarios-terrain.jpg',quality=92,optimize=True); print(im.size)
