import numpy as np, rasterio, glob, json, pandas as pd, geopandas as gpd
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from shapely.geometry import Point
SP="/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/"
CP="/home/claude/cfb-wainwright---full-satellite-data---copernicus-/sentinel-2/"
LS="/home/claude/cfb-wainwright-landsat-8-9/analysis/2026-10-17/burned_1217_classes.tif"
case="v3b_2x_lb1.5_0630"; W_=SP+f"p4_v3_{case}/"
minx,maxy,RES,H,W=np.load(W_+"meta.npy"); H,W=int(H),int(W)
T=from_origin(minx,maxy,RES,RES); CRS="EPSG:3400"
def f(d,b): return CP+f"{d}/L2A_tiff/{d}-00_00_{d}-23_59_Sentinel-2_L2A_{b}.tiff"
def get(path,rs=Resampling.average):
    s=rasterio.open(path); o=np.full((H,W),np.nan,'float32')
    reproject(rasterio.band(s,1),o,dst_transform=T,dst_crs=CRS,resampling=rs); return o
def nbr(d): n=get(f(d,'B8A_(Raw)')); s=get(f(d,'B12_(Raw)')); return (n-s)/(n+s)
pre=nbr('2026-10-04'); dn=pre-nbr('2026-10-24'); dn19=pre-nbr('2026-10-19')
scar=gpd.read_file('/home/claude/cfb-wainwright-fire-archive/data/copernicus/burn_scar.geojson').to_crs(CRS)
from rasterio.features import geometry_mask
inscar=~geometry_mask(list(scar.geometry),(H,W),T)
# cloud/shadow guard for Oct 24: drop pixels where Oct24 and Oct19 disagree by >0.12
ok=inscar&np.isfinite(dn)&(np.abs(dn-dn19)<0.12)
ls=get(LS,Resampling.nearest); A1217=ls>=2  # central class (0.08) and above
start=np.load(W_+"start316.npy").astype(bool)
arrs=np.stack([np.load(p) for p in sorted(glob.glob(W_+"arr_*.npy"))])
med=np.nanmedian(np.where(np.isfinite(arrs),arrs,np.nan),axis=0)  # minutes after 15:00
zoneA=A1217&ok; zoneB=start&~A1217&ok; zoneC=ok&~start
out={}
def st(m): v=dn[m]; return dict(km2=round(m.sum()*RES*RES/1e6,2),median=round(float(np.median(v)),3),p90=round(float(np.percentile(v,90)),3),share_mod_high=round(float((v>=0.44).mean()),2))
out['A_burned_by_1217']=st(zoneA); out['B_1217_to_316_prefront']=st(zoneB); out['C_after_316_shift']=st(zoneC)
# post-front: severity by model arrival time
bins=[16,25,35,50,70,100,140,200,400]; rows=[]
for a,b in zip(bins[:-1],bins[1:]):
    m=zoneC&(med>=a)&(med<b)
    if m.sum()>20: rows.append((f"{a-16}-{b-16} min after 3:16",round(m.sum()*RES*RES/1e6,2),round(float(np.median(dn[m])),3)))
out['C_by_model_arrival']=rows
# model local spread rate (m/min) across 30 fires' median arrival -> head vs flank
gy,gx=np.gradient(med,RES); g=np.hypot(gx,gy); ros=np.where(g>0,1/g,np.nan)  # m per minute
mC=zoneC&np.isfinite(ros)&(ros<400)
q=np.nanpercentile(ros[mC],[33,67])
out['C_by_model_spread_rate']=[(lab,round(float(np.median(dn[m])),3),int(m.sum())) for lab,m in (("slowest third (flank/backing)",mC&(ros<q[0])),("middle third",mC&(ros>=q[0])&(ros<q[1])),("fastest third (head)",mC&(ros>=q[1])))]
out['spearman_dnbr_vs_model_rate']=round(float(pd.Series(dn[mC]).corr(pd.Series(ros[mC]),method='spearman')),3)
out['spearman_dnbr_vs_arrival']=round(float(pd.Series(dn[zoneC&np.isfinite(med)]).corr(pd.Series(med[zoneC&np.isfinite(med)]),method='spearman')),3)
PTS={"Range 2 point":(52.7728,-110.9063),"Road head":(52.7705,-110.8996),"C":(52.7640,-110.9160),"D":(52.7628,-110.8995),"E":(52.7530,-110.8990)}
P=gpd.GeoSeries([Point(lo,la) for la,lo in PTS.values()],crs=4326,index=list(PTS)).to_crs(CRS)
yy,xx=np.mgrid[0:H,0:W]; X=minx+(xx+.5)*RES; Y=maxy-(yy+.5)*RES
pt={}
for k,p in P.items():
    m=(np.hypot(X-p.x,Y-p.y)<=200)&ok
    r_,c_=int((maxy-p.y)//RES),int((p.x-minx)//RES)
    pt[k]=dict(median_dnbr_200m=round(float(np.median(dn[m])),3) if m.sum() else None,model_arrival_min_after_316=round(float(med[r_,c_]-16),1) if np.isfinite(med[r_,c_]) else None,in_start_fire=bool(start[r_,c_]))
out['points']=pt
out['scar_excluded_cloud_px_km2']=round((inscar&~ok).sum()*RES*RES/1e6,2)
json.dump(out,open("/home/claude/cfb-wainwright-fire-archive/data/authentic-stoic-stress-test/model_v3/severity_oct24/sev_vs_model.json","w"),indent=1); print(json.dumps(out,indent=1))
np.savez_compressed("/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/sev24/grids.npz",dn=dn,ok=ok,A=A1217,start=start,med=med,ros=ros,meta=np.array([minx,maxy,RES,H,W]))
