"""Part 4: could they have got out? Latest departure time from each scenario point that still
reaches safe ground on foot before the fire, by straight-line routes in 72 directions.
Safe ground: outside the burn (never burned) or ground that burned >= 5 min earlier ("the black").
Speed: Tobler hiking function scaled to a base pace (walk 5 km/h, loaded jog 8 km/h, run 10 km/h)."""
import sys; sys.path.insert(0,'vis')
import numpy as np, pandas as pd, geopandas as gpd, rasterio, math
from shapely.geometry import Point
C="EPSG:3400"
SC={"A":(52.7728,-110.9063),"B":(52.7705,-110.8996),"C":(52.7640,-110.9160),"D":(52.7628,-110.8995),"E":(52.7530,-110.8990)}
pts=gpd.GeoSeries([Point(lon,lat) for lat,lon in SC.values()],crs=4326,index=list(SC)).to_crs(C)
dem=rasterio.open('mrdem10.tif'); Z=dem.read(1).astype(float); Z[Z<-9000]=np.nan
def z(x,y):
    r,c=dem.index(x,y); 
    try: return Z[r,c]
    except IndexError: return np.nan
SCHED=["S0_fixed306","S1_stoic","S2_station_veer","S3_fast_veer","S4_fixed315"]
PACE={"walk 5 km/h":5.0,"jog in kit 8 km/h":8.0,"run 10 km/h":10.0}
rows=[]
for s in SCHED:
    A=rasterio.open(f'arr_{s}.tif'); a=A.read(1).astype(float); a[a<-9000]=np.nan
    def arr(x,y):
        r,c=A.index(x,y)
        if 0<=r<a.shape[0] and 0<=c<a.shape[1]: return a[r,c]
        return np.nan
    for k,p in pts.items():
        t_here=arr(p.x,p.y)
        if not np.isfinite(t_here):
            # nearest burned within 150 m
            best=np.inf
            for dx in range(-150,151,30):
                for dy in range(-150,151,30):
                    v=arr(p.x+dx,p.y+dy); best=min(best,v) if np.isfinite(v) else best
            t_here=best
        for pn,v0 in PACE.items():
            best_dep=-np.inf; best_dir=None; best_dist=None
            for ang in range(0,360,5):
                ux,uy=math.sin(math.radians(ang)),math.cos(math.radians(ang))
                # route profile: precompute along 0..3000 m in 20 m steps
                ds=np.arange(0,3001,20)
                xs=p.x+ds*ux; ys=p.y+ds*uy
                fa=np.array([arr(x,y) for x,y in zip(xs,ys)])
                zz=np.array([z(x,y) for x,y in zip(xs,ys)])
                if np.isnan(zz).any(): zz=pd.Series(zz).ffill().bfill().values
                slope=np.diff(zz)/20.0
                sp=v0*np.exp(-3.5*np.abs(slope+0.05))/math.exp(-3.5*0.05)  # Tobler, normalised to flat = v0
                tseg=20/(sp*1000/60)  # minutes per segment
                tcum=np.concatenate([[0],np.cumsum(tseg)])
                # binary search latest departure
                def ok(t0):
                    for i in range(len(ds)):
                        t=t0+tcum[i]
                        f=fa[i]
                        if not np.isfinite(f): return True        # unburned ground reached
                        if f <= t-5 and i>0: return True           # the black
                        if f <= t+3.0: return False                # fire arrives first
                    return False
                lo,hi=t_here-60,t_here
                if not ok(lo): continue
                for _ in range(25):
                    mid=(lo+hi)/2
                    if ok(mid): lo=mid
                    else: hi=mid
                if lo>best_dep:
                    best_dep=lo; best_dir=ang
                    # distance to safety on this route
                    for i in range(len(ds)):
                        f=fa[i]; t=lo+tcum[i]
                        if (not np.isfinite(f)) or (f<=t-5 and i>0): best_dist=ds[i]; break
            rows.append(dict(schedule=s,scenario=k,pace=pn,fire_arrives=round(t_here,1),
                             latest_departure=round(best_dep,1) if np.isfinite(best_dep) else None,
                             margin_before_arrival_min=round(t_here-best_dep,1) if np.isfinite(best_dep) else None,
                             best_bearing=best_dir,route_to_safety_m=best_dist))
df=pd.DataFrame(rows); df.to_csv('part4_escape_margin3.csv',index=False)
hm=lambda t: f"{15+int(t//60)}:{int(round(t%60)):02d}" if t is not None and np.isfinite(t) else "-"
pd.set_option('display.width',250)
g=df.groupby(['scenario','pace']).agg(arr_lo=('fire_arrives','min'),arr_hi=('fire_arrives','max'),dep_lo=('latest_departure','min'),dep_hi=('latest_departure','max'),
   bear=('best_bearing',lambda v: ','.join(sorted({str(int(x)) for x in v if x==x}))),dist_lo=('route_to_safety_m','min'),dist_hi=('route_to_safety_m','max')).reset_index()
for c_ in ['arr_lo','arr_hi','dep_lo','dep_hi']: g[c_]=g[c_].map(lambda t: hm(t-0) if t==t else '-')
print(g.to_string(index=False))
