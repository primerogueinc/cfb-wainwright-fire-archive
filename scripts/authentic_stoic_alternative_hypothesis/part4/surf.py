exec(open('perm.py').read().split("# ---- visibility masks")[0])
def success(fa,tc,t0,margin):
    t=t0+tc
    safe=np.isnan(fa)|((fa<=t-5)&(np.arange(fa.shape[1])[None,:]>0))
    danger=(fa<=t+margin)&~safe
    first_safe=np.where(safe.any(1),safe.argmax(1),10**9)
    first_danger=np.where(danger.any(1),danger.argmax(1),10**9)
    return (first_safe<first_danger)&(first_safe<10**9)
import geopandas as gpd
sys_scar=gpd.read_file("/home/claude/cfb-wainwright-fire-archive/data/infrastructure/scar_patches_revised.geojson").to_crs(C)
scar=max(sys_scar.geometry,key=lambda g:g.area).buffer(100)
# start points every 70 m across the Range 2 neighbourhood
from shapely.geometry import box
bb=gpd.GeoSeries([box(-110.928,52.754,-110.884,52.783)],crs=4326).to_crs(C).iloc[0]
xs=np.arange(bb.bounds[0],bb.bounds[2],70); ys=np.arange(bb.bounds[1],bb.bounds[3],70)
XX,YY=np.meshgrid(xs,ys); XX=XX.ravel(); YY=YY.ravel()
import shapely
ins=shapely.contains_xy(scar,XX,YY); XX,YY=XX[ins],YY[ins]
print("points",len(XX))
DIRS=np.arange(0,360,5); STEP=20; DS=np.arange(0,2501,STEP)
ux=np.sin(np.radians(DIRS))[:,None]; uy=np.cos(np.radians(DIRS))[:,None]
SP={"jog":8.0,"smoke":3.0}
COND=[("gust",None),("within500",500),("within200",200)]
res={(c,s):np.zeros(len(XX)) for c,_ in COND for s in SP}
for i,(px,py) in enumerate(zip(XX,YY)):
    X=px+DS[None,:]*ux; Y=py+DS[None,:]*uy
    r,c=gi(X,Y); inb=(r>=0)&(r<H)&(c>=0)&(c<W); r=np.clip(r,0,H-1); c=np.clip(c,0,W-1)
    zz=zs(X,Y); zz=pd.DataFrame(zz.T).ffill().bfill().values.T
    fac=np.exp(-3.5*np.abs(np.diff(zz,axis=1)/STEP+0.05))/math.exp(-3.5*0.05)
    TCs={sn:np.concatenate([np.zeros((len(DIRS),1)),np.cumsum(STEP/(v0*fac*1000/60),axis=1)],axis=1) for sn,v0 in SP.items()}
    for g in GRIDS:
        fa=np.where(inb,ARR[g][r,c],np.nan)
        for cn,R in COND:
            if R is None: t0=16.0
            else:
                v=fa[:,:int(R//STEP)+1]; t0=max(16.0,float(np.nanmin(v))) if np.isfinite(v).any() else np.nan
            for sn in SP:
                if not np.isfinite(t0): res[(cn,sn)][i]+=1; continue
                res[(cn,sn)][i]+=float(success(fa,TCs[sn],t0+2,3.0).any())
    if i%200==0: print(i,flush=True)
out=pd.DataFrame({"x":XX,"y":YY})
for (cn,sn),v in res.items(): out[f"{cn}_{sn}"]=v/len(GRIDS)
out.to_csv("surface.csv",index=False); print(out.describe().T[["mean"]])
