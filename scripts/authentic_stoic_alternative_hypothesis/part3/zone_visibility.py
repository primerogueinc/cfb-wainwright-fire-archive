import sys; sys.path.insert(0,'vis')
from pr import preshift_hull, REPO
import numpy as np, pandas as pd, geopandas as gpd, rasterio
C="EPSG:3400"
hull=gpd.GeoSeries([preshift_hull()],crs=4326).to_crs(C).iloc[0]
f=pd.read_csv(REPO+'data/authentic-stoic-stress-test/part2/part2_core_frequency.csv'); f=f[f.n_scenarios_in_core>0].copy()
P=gpd.GeoSeries(gpd.points_from_xy(f.x,f.y),crs=4326).to_crs(C)
dem=rasterio.open('mrdem10.tif'); Z=dem.read(1).astype(float)
def z(x,y): r,c=dem.index(x,y); return Z[r,c]
b=hull.exterior; ed=[b.interpolate(d) for d in np.arange(0,b.length,40)]
EX=np.array([q.x for q in ed]); EY=np.array([q.y for q in ed])
vis=[]; elev=[]
for p in P:
    d=np.hypot(EX-p.x,EY-p.y); idx=np.argsort(d)[:25]; z0=z(p.x,p.y)+1.7; ok=False
    for i in idx:
        n=max(3,int(d[i]//15)); lx=np.linspace(p.x,EX[i],n); ly=np.linspace(p.y,EY[i],n)
        zz=np.array([z(a,b_) for a,b_ in zip(lx,ly)]); line=z0+(zz[-1]+2.5-z0)*np.linspace(0,1,n)
        if np.all(zz[1:-1]<=line[1:-1]): ok=True; break
    vis.append(ok); elev.append(z(p.x,p.y))
f['sees_fire_edge']=vis; f['elev']=elev
for k,lab in [(1,'any reading'),(8,'>=8 of 20'),(12,'>=12 of 20')]:
    m=f.n_scenarios_in_core>=k
    w=f.n_scenarios_in_core[m]
    print(f"{lab}: cells {m.sum()}, can see pre-shift fire edge (standing): {100*f.sees_fire_edge[m].mean():.0f}%  weighted {100*np.average(f.sees_fire_edge[m],weights=w):.0f}%  elev {f.elev[m].min():.0f}-{f.elev[m].max():.0f}")
f.to_csv('zone_visibility.csv',index=False)
