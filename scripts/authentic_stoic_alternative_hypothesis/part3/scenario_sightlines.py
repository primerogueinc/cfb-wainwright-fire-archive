import sys; sys.path.insert(0,'vis')
from pr import scar_main
import numpy as np, pandas as pd, geopandas as gpd, rasterio
from shapely.geometry import Point
C="EPSG:3400"
scar=gpd.GeoSeries([scar_main()],crs=4326).to_crs(C).iloc[0]
S={"A Range 2 (OSM)":(52.7728,-110.9063),"B Road's end hollow":(52.7705,-110.8996),"C Strip N of Jamieson Lake":(52.7640,-110.9160),
   "D Range road south":(52.7628,-110.8995),"E South-central run":(52.7530,-110.8990)}
pts=gpd.GeoSeries([Point(lon,lat) for lat,lon in S.values()],crs=4326,index=list(S)).to_crs(C)
print({k:scar.contains(p) for k,p in pts.items()})
dem=rasterio.open('mrdem10.tif'); Z=dem.read(1).astype(float); Z[Z<-9000]=np.nan
def zxy(x,y):
    r,c=dem.index(x,y); return Z[r,c]
zv=np.vectorize(zxy)
out=[]
for s in ["S0_fixed306","S1_stoic","S2_station_veer","S3_fast_veer","S4_fixed315"]:
    A=rasterio.open(f'arr_{s}.tif'); a=A.read(1).astype(float); a[a<-9000]=np.nan
    H,W=a.shape; yy,xx=np.mgrid[0:H,0:W]; X=A.transform.c+(xx+0.5)*A.transform.a; Y=A.transform.f+(yy+0.5)*A.transform.e
    for k,p in pts.items():
        r0,c0=A.index(p.x,p.y); t_here=a[r0,c0]
        if not np.isfinite(t_here):
            # nearest burned cell within 150 m
            d=np.hypot(X-p.x,Y-p.y); m=np.isfinite(a)&(d<150)
            t_here=np.nanmin(np.where(m,a,np.nan)) if m.any() else np.nan
        d=np.hypot(X-p.x,Y-p.y); sel=np.isfinite(a)&(d<2500)&(d>60)
        ys,xs=np.nonzero(sel); vis=np.zeros(len(ys),bool)
        z0=zxy(p.x,p.y)+1.7
        for i,(r,c) in enumerate(zip(ys,xs)):
            n=max(3,int(d[r,c]//15)); lx=np.linspace(p.x,X[r,c],n); ly=np.linspace(p.y,Y[r,c],n)
            zz=zv(lx,ly); z1=zz[-1]+2.5; line=z0+(z1-z0)*np.linspace(0,1,n)
            vis[i]=np.all(zz[1:-1]<=line[1:-1])
        tv=a[ys[vis],xs[vis]]
        # first time flames are in view: earliest arrival (after the front, t>=16) among visible cells; also pre-front fire visible?
        pre_vis=bool(np.any(tv<=16.5))
        post=tv[tv>16.5]
        first=float(post.min()) if post.size else np.nan
        out.append(dict(schedule=s,scenario=k,arrival_min_after_3pm=round(t_here,1),fire_in_view_before_shift=pre_vis,
                        first_new_flames_in_view=round(first,1),sight_warning_min=round(t_here-first,1) if np.isfinite(first) else None,
                        share_of_nearby_burn_visible=round(vis.mean()*100)))
df=pd.DataFrame(out); df.to_csv('scenario_visibility.csv',index=False)
pd.set_option('display.width',250)
print(df.pivot_table(index='scenario',columns='schedule',values=['arrival_min_after_3pm','sight_warning_min']).round(0).to_string())
print(df.groupby('scenario')[['fire_in_view_before_shift','share_of_nearby_burn_visible']].first())
