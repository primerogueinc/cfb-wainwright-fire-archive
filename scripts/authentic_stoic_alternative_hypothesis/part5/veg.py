import sys; sys.path.insert(0,'vis')
from pr import preshift_hull, scar_main, REPO
import numpy as np, pandas as pd, geopandas as gpd, rasterio
from shapely.geometry import Point
C="EPSG:3400"; V=REPO+'data/visibility/'
dem=rasterio.open('mrdem10.tif'); Z=dem.read(1).astype(float)
chm=rasterio.open(V+'meta_wri_chm_3400_10m.tif'); H=chm.read(1).astype(float); H[~np.isfinite(H)|(H<0)|(H>60)]=0
wc=rasterio.open(V+'esa_worldcover2021_3400_10m.tif'); WC=wc.read(1)
def samp(src,A,x,y):
    T=~src.transform; c,r=T*(x,y); r=np.clip(r.astype(int),0,A.shape[0]-1); c=np.clip(c.astype(int),0,A.shape[1]-1); return A[r,c]
hull=gpd.GeoSeries([preshift_hull()],crs=4326).to_crs(C).iloc[0]
b=hull.exterior; ed=[b.interpolate(d) for d in np.arange(0,b.length,40)]
EX=np.array([q.x for q in ed]); EY=np.array([q.y for q in ed])
f=pd.read_csv(REPO+'data/authentic-stoic-stress-test/part2/part2_core_frequency.csv'); f=f[f.n_scenarios_in_core>0].copy()
P=gpd.GeoSeries(gpd.points_from_xy(f.x,f.y),crs=4326).to_crs(C)
# land cover in zone
lc=samp(wc,WC,P.x.values,P.y.values); ch=samp(chm,H,P.x.values,P.y.values)
names={10:'trees',20:'shrub',30:'grass',40:'crop',50:'built',60:'bare',80:'water',90:'wetland',100:'moss'}
w=f.n_scenarios_in_core.values
print('zone landcover (weighted %):',{names.get(k,k):round(100*w[lc==k].sum()/w.sum()) for k in np.unique(lc)})
print('zone cells with canopy>=2m: %.0f%%'%(100*np.average(ch>=2,weights=w)))
def sees(px,py,flame,L,k=25,step=5):
    d=np.hypot(EX-px,EY-py); idx=np.argsort(d)[:k]
    z0=samp(dem,Z,np.array([px]),np.array([py]))[0]+1.7
    for i in idx:
        n=max(3,int(d[i]//step)); t=np.linspace(0,1,n); lx=px+(EX[i]-px)*t; ly=py+(EY[i]-py)*t
        zz=samp(dem,Z,lx,ly); hh=samp(chm,H,lx,ly)
        line=z0+(zz[-1]+flame-z0)*t
        if np.any(zz[1:-1]>line[1:-1]): continue
        inside=(hh[1:-1]>=2)&(zz[1:-1]+hh[1:-1]>line[1:-1])
        if inside.sum()*d[i]/(n-1)<=L: return True
    return False
rows=[]
for flame in (2.5,6.0):
    for L,lab in ((1e9,'terrain only'),(100,'leaf-off aspen (100 m see-through)'),(30,'dense (30 m)'),(0,'opaque canopy')):
        v=np.array([sees(p.x,p.y,flame,L) for p in P])
        for kk,kl in ((1,'any'),(12,'>=12 of 20')):
            m=w>=kk; rows.append(dict(flame_m=flame,canopy=lab,zone=kl,share_sees_edge=round(100*np.average(v[m],weights=w[m]))))
        f[f'sees_f{flame}_L{int(min(L,9999))}']=v
out=pd.DataFrame(rows); print(out.pivot_table(index=['flame_m','canopy'],columns='zone',values='share_sees_edge',sort=False).to_string())
f['landcover']=[names.get(k,k) for k in lc]; f['canopy_m']=ch
f.to_csv('p5/zone_visibility_vegetation.csv',index=False); out.to_csv('p5/zone_visibility_vegetation_summary.csv',index=False)
# scenarios A-E
S={"A Range 2":(52.7728,-110.9063),"B Road's end":(52.7705,-110.8996),"C Strip N of Jamieson Lake":(52.7640,-110.9160),"D Range road south":(52.7628,-110.8995),"E South-central run":(52.7530,-110.8990)}
pts=gpd.GeoSeries([Point(lo,la) for la,lo in S.values()],crs=4326,index=list(S)).to_crs(C)
for k,p in pts.items():
    x=np.array([p.x]);y=np.array([p.y])
    # canopy within 100/250 m
    yy,xx=np.mgrid[-250:251:10,-250:251:10]; rr=np.hypot(xx,yy)
    hc=samp(chm,H,p.x+xx.ravel(),p.y+yy.ravel()).reshape(xx.shape)
    print(f"{k}: canopy here {samp(chm,H,x,y)[0]:.0f} m, {names.get(samp(wc,WC,x,y)[0])}; tree cover within 100 m {100*(hc[rr<=100]>=2).mean():.0f}%, 250 m {100*(hc[rr<=250]>=2).mean():.0f}%; sees edge terrain {sees(p.x,p.y,2.5,1e9)}, leaf-off {sees(p.x,p.y,2.5,100)}, opaque {sees(p.x,p.y,2.5,0)}")
