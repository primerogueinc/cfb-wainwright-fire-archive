import numpy as np, pandas as pd, geopandas as gpd, rasterio, math, itertools, json
from shapely.geometry import Point
SP="/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/"
minx,maxy,RES,H,W=np.load("meta.npy"); H,W=int(H),int(W)
C="EPSG:3400"
PTS={"A":(52.7728,-110.9063),"B":(52.7705,-110.8996),"C":(52.7640,-110.9160),"D":(52.7628,-110.8995),"E":(52.7530,-110.8990)}
P=gpd.GeoSeries([Point(lon,lat) for lat,lon in PTS.values()],crs=4326,index=list(PTS)).to_crs(C)
dem=rasterio.open(SP+"mrdem10.tif"); Z=dem.read(1).astype(float); Z[Z<-9000]=np.nan
dT=dem.transform
def zs(x,y):
    c=((x-dT.c)/dT.a).astype(int); r=((y-dT.f)/dT.e).astype(int)
    ok=(r>=0)&(r<Z.shape[0])&(c>=0)&(c<Z.shape[1]); out=np.full(x.shape,np.nan); out[ok]=Z[r[ok],c[ok]]; return out
def gi(x,y):
    c=((x-minx)//RES).astype(int); r=((maxy-y)//RES).astype(int); return r,c
yy,xx=np.mgrid[0:H,0:W]; GX=minx+(xx+0.5)*RES; GY=maxy-(yy+0.5)*RES
SCHED=["S0_fixed306","S1_stoic","S2_station_veer","S3_fast_veer","S4_fixed315"]
KN={"S0_fixed306":[(16,306),(999,306)],"S1_stoic":[(16,269),(69,288),(80,306),(999,306)],
    "S2_station_veer":[(16,269),(50,305),(60,306),(999,306)],"S3_fast_veer":[(16,269),(30,305),(40,306),(999,306)],"S4_fixed315":[(16,315),(999,315)]}
def wfrom(s,t): ts,ds=zip(*KN[s]); return float(np.interp(t,ts,ds))
GRIDS=[(s,ros,lb) for s in SCHED for ros in (4.4,8.0,12.0) for lb in ("steady","gusty")]
ARR={g:np.load(f"arr_{g[0]}_{g[1]}_{g[2]}.npy").astype(float) for g in GRIDS}
for a in ARR.values(): a[~np.isfinite(a)]=np.nan
# ---- visibility masks (terrain only): eye 1.7 m, flames 4 m
VIS={}
for k,p in P.items():
    d=np.hypot(GX-p.x,GY-p.y); sel=(d<2500)&(d>40)
    ys,xs=np.nonzero(sel); z0=zs(np.array([p.x]),np.array([p.y]))[0]+1.7
    n=60; f=np.linspace(0,1,n)[None,:]
    lx=p.x+(GX[ys,xs][:,None]-p.x)*f; ly=p.y+(GY[ys,xs][:,None]-p.y)*f
    zz=zs(lx,ly); z1=zz[:,-1]+4.0; line=z0+(z1[:,None]-z0)*f
    v=np.all((zz[:,1:-1]<=line[:,1:-1])|np.isnan(zz[:,1:-1]),axis=1)
    m=np.zeros((H,W),bool); m[ys[v],xs[v]]=True; VIS[k]=m
# ---- route profiles
DIRS=np.arange(0,360,5); STEP=20; DS=np.arange(0,3001,STEP)
SPEEDS={"jog in kit (8 km/h)":8.0,"walk (5 km/h)":5.0,"in smoke (3 km/h)":3.0,"helping the injured (2 km/h)":2.0}
prof={}
for k,p in P.items():
    ux=np.sin(np.radians(DIRS))[:,None]; uy=np.cos(np.radians(DIRS))[:,None]
    X=p.x+DS[None,:]*ux; Y=p.y+DS[None,:]*uy
    zz=zs(X,Y); zz=pd.DataFrame(zz.T).ffill().bfill().values.T
    sl=np.diff(zz,axis=1)/STEP
    fac=np.exp(-3.5*np.abs(sl+0.05))/math.exp(-3.5*0.05)
    r,c=gi(X,Y); inb=(r>=0)&(r<H)&(c>=0)&(c<W)
    prof[k]=dict(X=X,Y=Y,r=np.clip(r,0,H-1),c=np.clip(c,0,W-1),inb=inb,fac=fac)
def tcum(k,v):
    t=STEP/(v*prof[k]["fac"]*1000/60); return np.concatenate([np.zeros((len(DIRS),1)),np.cumsum(t,axis=1)],axis=1)
TC={(k,s):tcum(k,v) for k in P.index for s,v in SPEEDS.items()}
def success(fa,tc,t0,margin):
    t=t0+tc
    safe=np.isnan(fa)|((fa<=t-5)&(np.arange(fa.shape[1])[None,:]>0))
    danger=(fa<=t+margin)&~safe
    first_safe=np.where(safe.any(1),safe.argmax(1),10**9)
    first_danger=np.where(danger.any(1),danger.argmax(1),10**9)
    return (first_safe<first_danger)&(first_safe<10**9)
rows=[]
for g in GRIDS:
    a=ARR[g]; s=g[0]
    for k,p in P.items():
        pr=prof[k]; fa=np.where(pr["inb"],a[pr["r"],pr["c"]],np.nan)
        r0,c0=gi(np.array([p.x]),np.array([p.y])); t_arr=a[r0[0],c0[0]]
        if not np.isfinite(t_arr):
            dd=np.hypot(GX-p.x,GY-p.y); t_arr=np.nanmin(np.where(dd<150,a,np.nan))
        vis_new=a[VIS[k]&(a>16.5)]; t_flames=float(np.nanmin(vis_new)) if vis_new.size else t_arr
        dd=np.hypot(GX-p.x,GY-p.y); t_close=float(np.nanmin(np.where(dd<300,a,np.nan)))
        t_close=max(t_close,16.0); t_flames=min(max(t_flames,16.0),t_arr)
        cues={"gust front (3:16)":16.0,"flames in sight":t_flames,"fire within 300 m":t_close}
        for (cn,tc_),dl,(sn,_),mg in itertools.product(cues.items(),(0,2,5,10),SPEEDS.items(),(3.0,0.5)):
            t0=tc_+dl; ok=success(fa,TC[(k,sn)],t0,mg)
            wf=wfrom(s,t0); away=int(round(((wf+180)%360)/5))%72
            res={"optimal (best route)":bool(ok.any()),"crosswind east (90°)":bool(ok[18]),"away from the fire (downwind)":bool(ok[away]),
                 "south along range road (180°)":bool(ok[36]),"north along range road (0°)":bool(ok[0]),"random direction":float(ok.mean())}
            for strat,v in res.items():
                rows.append(dict(schedule=s,ros=g[1],gust=g[2],point=k,cue=cn,cue_time=round(tc_,1),delay=dl,speed=sn,margin=mg,strategy=strat,success=float(v),arrival=round(t_arr,1)))
        # direction fan (cue flames+2, jog, margin 3)
        for sn in ("jog in kit (8 km/h)","in smoke (3 km/h)"):
            ok=success(fa,TC[(k,sn)],t_flames+2,3.0)
            for i,dg in enumerate(DIRS):
                rows.append(dict(schedule=s,ros=g[1],gust=g[2],point=k,cue="FAN",cue_time=round(t_flames,1),delay=2,speed=sn,margin=3.0,strategy=f"dir{dg}",success=float(ok[i]),arrival=round(t_arr,1)))
df=pd.DataFrame(rows); df.to_parquet("perm.parquet") if False else df.to_csv("perm.csv.gz",index=False)
print(len(df))
m=df[(df.cue!="FAN")&(df.margin==3.0)]
pd.set_option('display.width',250)
for k in "ABCDE":
    t=m[(m.point==k)&(m.speed=="jog in kit (8 km/h)")].pivot_table(index="strategy",columns=["cue","delay"],values="success",aggfunc="mean")
    print("\n==",k,"jog"); print((t*100).round(0).to_string())
for k in "AB":
    t=m[(m.point==k)&(m.speed=="in smoke (3 km/h)")].pivot_table(index="strategy",columns=["cue","delay"],values="success",aggfunc="mean")
    print("\n==",k,"smoke"); print((t*100).round(0).to_string())
cues=df[df.cue!="FAN"].groupby(["point","cue"]).cue_time.median(); print(cues)
print(df[df.cue!="FAN"].groupby("point").arrival.describe()[["min","50%","max"]])
