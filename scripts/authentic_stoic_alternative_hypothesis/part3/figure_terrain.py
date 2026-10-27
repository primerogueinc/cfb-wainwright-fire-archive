import sys; sys.path.insert(0,'vis')
from pr import *
from pr import _LOGO
import rasterio
from rasterio.warp import reproject, Resampling as RS
from rasterio.transform import from_bounds as tfb
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.colors import LightSource
for n in ["Inter-Medium.otf","Inter-Bold.otf"]: fm.fontManager.addfont(F+n)
plt.rcParams["font.family"]="Inter"
hx=lambda c:"#%02x%02x%02x"%c
W_,E_,S_,N_=-110.950,-110.866,52.743,52.792
# reproject DEM to lon/lat grid ~10 m
nx,ny=570,545
dst=np.full((ny,nx),np.nan,'float32'); T=tfb(W_,S_,E_,N_,nx,ny)
with rasterio.open('mrdem10.tif') as r:
    reproject(rasterio.band(r,1),dst,src_transform=r.transform,src_crs=r.crs,src_nodata=-9999,dst_transform=T,dst_crs='EPSG:4326',dst_nodata=np.nan,resampling=RS.bilinear)
z=dst
ls=LightSource(azdeg=315,altdeg=35)
dx=(E_-W_)/nx*111320*np.cos(np.radians(52.77)); dy=(N_-S_)/ny*111200
hs=ls.hillshade(z,vert_exag=6,dx=dx,dy=dy)
fig=plt.figure(figsize=(12.0,11.5),dpi=150,facecolor=hx(BG))
ax=fig.add_axes([0,0,1,1]); ax.set_facecolor(hx(BG))
ext=(W_,E_,S_,N_)
ax.imshow(z,extent=ext,cmap='gist_earth',vmin=640,vmax=700,alpha=1.0)
ax.imshow(hs,extent=ext,cmap='gray',alpha=0.55)
xs=np.linspace(W_,E_,nx); ys=np.linspace(N_,S_,ny)
cs=ax.contour(xs,ys,z,levels=np.arange(640,705,5),colors='#2a1d15',linewidths=[1.4 if l%10==0 else 0.6 for l in np.arange(640,705,5)],alpha=0.8)
ax.clabel(cs,levels=[l for l in cs.levels if l%10==0],fmt='%d m',fontsize=9,colors='#2a1d15')
scar=scar_main(); hull=preshift_hull()
gpd.GeoSeries([scar],crs=4326).boundary.plot(ax=ax,color=hx(RED),linewidth=2.6)
gpd.GeoSeries([hull],crs=4326).plot(ax=ax,color=hx(YEL),alpha=0.25,edgecolor=hx(YEL),linewidth=2,linestyle='--')
c=pd.read_csv(REPO+'data/location_analysis/candidate_points.csv').set_index('point')
for nm,lab,dx_,dy_ in [('Range2 centroid (OSM)','Range 2',-0.0105,0.0012),('Road dead end (CanVec)',"Road's end",0.0015,-0.0016)]:
    r=c.loc[nm]; ax.plot(r.lon,r.lat,'o',ms=11,mfc='white',mec='#111',mew=2)
    ax.text(r.lon+dx_,r.lat+dy_,lab,color='white',fontsize=13,fontweight='bold',bbox=dict(facecolor='#111',edgecolor='none',pad=4,alpha=0.85))
ax.set_xlim(W_,E_); ax.set_ylim(S_,N_); ax.set_aspect(1/np.cos(np.radians(52.77))); ax.axis('off')
fig.savefig('_terrain.png',dpi=150,facecolor=hx(BG),bbox_inches='tight',pad_inches=0)
mp=Image.open('_terrain.png').convert('RGBA')
mp=mp.resize((1150,int(mp.size[1]*1150/mp.size[0])),Image.LANCZOS)
H=250+mp.size[1]+150
im,d=canvas(1800,H,"THE AUTHENTIC STOIC STRESS TEST  ·  PART 3  ·  TERRAIN","The ground the fire crossed",
 "Elevation (NRCan MRDEM, 30 m) with 5 m contours and hillshade. Red: burn scar. Yellow: the fire before the wind turned.")
im.alpha_composite(mp,(54,214))
X=54+mp.size[0]+44; y=230
d.text((X,y),"What the ground shows",font=K(26),fill=GOLD); y+=50
for h,ls_ in [("Gentle and rolling",["About 40 m of relief across the","scar (650-690 m). Typical slopes","2-3°; 95% under 6-7°."]),
              ("No steep draws",["Nothing like the steep ground","behind eruptive 'blow-up' fires.","Slope adds little to spread here."]),
              ("Rises can still hide a fire",["40 m of relief is enough to block","a view along the ground. Could","anyone at Range 2 see the fire?","That's the next test."])]:
    d.text((X,y),h,font=B(21),fill=CREAM); y+=32
    for l in ls_: d.text((X,y),l,font=M(18),fill=MUTED); y+=25
    y+=20
d.text((X,y),"Limits",font=B(19),fill=GOLD); y+=30
for l in ["30 m model: small hollows and","berms under ~30 m don't show.","NRCan lidar doesn't cover the base."]:
    d.text((X,y),l,font=M(17),fill=MUTED); y+=24
footer(im,["Elevation: NRCan MRDEM-30 (Open Government Licence - Canada), checked against Copernicus GLO-30. Burn scar: Sentinel-2 (Copernicus). Fire: NASA FIRMS.",
           "Hillshade lit from the northwest, 6x vertical exaggeration. Data: github.com/primerogueinc/cfb-wainwright-fire-archive. Graphic: Kevin Duska Jr. (Prime Rogue Inc.)"])
im.convert('RGB').save('vis/cfb-wainwright-terrain.jpg',quality=92,optimize=True); print(im.size)
