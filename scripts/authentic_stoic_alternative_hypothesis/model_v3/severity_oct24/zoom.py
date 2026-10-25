import numpy as np, json, rasterio, geopandas as gpd, pandas as pd
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from rasterio.features import geometry_mask
from shapely.geometry import Point, LineString
CP="/home/claude/cfb-wainwright---full-satellite-data---copernicus-/sentinel-2/"
def f(d,b): return CP+f"{d}/L2A_tiff/{d}-00_00_{d}-23_59_Sentinel-2_L2A_{b}.tiff"
scar=gpd.read_file('/home/claude/cfb-wainwright-fire-archive/data/copernicus/burn_scar.geojson').to_crs(3400)
x0,y0,x1,y1=scar.total_bounds; RES=10; x0-=500;y1+=500; W=int((x1+500-x0)/RES); H=int((y1-(y0-500))/RES)
T=from_origin(x0,y1,RES,RES)
def get(path,rs=Resampling.bilinear):
    s=rasterio.open(path); o=np.full((H,W),np.nan,'float32'); reproject(rasterio.band(s,1),o,dst_transform=T,dst_crs="EPSG:3400",resampling=rs); return o
def nbr(d): n=get(f(d,'B8A_(Raw)')); s=get(f(d,'B12_(Raw)')); return (n-s)/(n+s)
def ndvi(d): n=get(f(d,'B08_(Raw)')); r=get(f(d,'B04_(Raw)')); return (n-r)/(n+r)
pre=nbr('2026-10-04'); n19=nbr('2026-10-19'); n24=nbr('2026-10-24'); dn=pre-n24; dn19=pre-n19; prendvi=ndvi('2026-10-04')
ins=~geometry_mask(list(scar.geometry),(H,W),T); ok=ins&np.isfinite(dn)&(np.abs(dn-dn19)<0.12)
# model grids (40 m) -> 10 m
g=np.load('/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/sev24/grids.npz'); mx,my,MR,MH,MW=g['meta']; MT=from_origin(mx,my,MR,MR)
def up(a): o=np.full((H,W),np.nan,'float32'); reproject(a.astype('float32'),o,src_transform=MT,src_crs="EPSG:3400",dst_transform=T,dst_crs="EPSG:3400",resampling=Resampling.nearest); return o
start=up(g['start'])>0.5; med=up(g['med'])-16
PTS={"Range 2":(52.7728,-110.9063),"Road head":(52.7705,-110.8996)}
P=gpd.GeoSeries([Point(lo,la) for la,lo in PTS.values()],crs=4326,index=list(PTS)).to_crs(3400)
ours=LineString([P["Range 2"],P["Road head"]]).buffer(300)
om=~geometry_mask([ours],(H,W),T)
post=ok&~start
A=om&ok; R=ok&~om; Rpost=post&~om; Rwin=post&~om&(med>=0)&(med<=20)
def s(m): v=dn[m]; return dict(km2=round(m.sum()*1e-4,2),median=round(float(np.median(v)),3),mean=round(float(v.mean()),3),share_ge_044=round(float((v>=0.44).mean()),2),share_ge_066=round(float((v>=0.66).mean()),3),pre_nbr=round(float(np.nanmedian(pre[m])),3),pre_ndvi=round(float(np.nanmedian(prendvi[m])),3))
out={'our_area (300 m around Range 2-road head)':s(A),'rest of scar':s(R),'rest, after-shift only':s(Rpost),'rest, after-shift, reached 0-20 min':s(Rwin)}
# percentile rank vs random same-size patches in after-shift zone
rng=np.random.default_rng(1); ys,xs=np.where(post); meds=[]
for _ in range(2000):
    i=rng.integers(len(ys)); cx=x0+(xs[i]+.5)*RES; cy=y1-(ys[i]+.5)*RES
    patch=LineString([(cx-(P['Road head'].x-P['Range 2'].x)/2,cy-(P['Road head'].y-P['Range 2'].y)/2),(cx+(P['Road head'].x-P['Range 2'].x)/2,cy+(P['Road head'].y-P['Range 2'].y)/2)]).buffer(300)
    r0=max(0,int((y1-patch.bounds[3])/RES)); r1=int((y1-patch.bounds[1])/RES); c0=max(0,int((patch.bounds[0]-x0)/RES)); c1=int((patch.bounds[2]-x0)/RES)
    sub=~geometry_mask([patch],(r1-r0,c1-c0),from_origin(x0+c0*RES,y1-r0*RES,RES,RES))
    m=sub&post[r0:r1,c0:c1]
    if m.sum()>0.6*sub.sum(): meds.append(np.median(dn[r0:r1,c0:c1][m]))
meds=np.array(meds); out['rank_vs_random_after-shift_patches']=dict(n=len(meds),percentile=round(float((meds<out['our_area (300 m around Range 2-road head)']['median']).mean()*100),1),patch_median_range_p5_p95=[round(float(v),3) for v in np.percentile(meds,[5,95])])
# fuel control: residual of dNBR after regressing on pre-fire NBR and NDVI within after-shift zone
m=post&np.isfinite(prendvi)&np.isfinite(pre)
Xm=np.c_[np.ones(m.sum()),pre[m],prendvi[m]]; b=np.linalg.lstsq(Xm,dn[m],rcond=None)[0]
res=np.full((H,W),np.nan); res[m]=dn[m]-Xm@b
out['fuel_adjusted_residual']=dict(our_area=round(float(np.nanmedian(res[om&m])),3),rest_after_shift=round(float(np.nanmedian(res[m&~om])),3),coef=[round(float(c),3) for c in b])
json.dump(out,open('/home/claude/cfb-wainwright-fire-archive/data/authentic-stoic-stress-test/model_v3/severity_oct24/our_area_vs_rest.json','w'),indent=1); print(json.dumps(out,indent=1))
np.savez_compressed('/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/sev24/zoom_grids.npz',dn=np.where(ok,dn,np.nan),om=om,start=start,med=med,res=res,meta=np.array([x0,y1,RES,H,W]))
