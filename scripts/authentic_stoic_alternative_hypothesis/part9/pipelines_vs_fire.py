import os
import json, numpy as np, pandas as pd, rasterio
from shapely.geometry import shape, Point, LineString
from shapely.ops import unary_union, nearest_points
from pyproj import Geod, Transformer
G=Geod(ellps='WGS84'); R=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../data/")
scar=unary_union([shape(x['geometry']) for x in json.load(open(R+"infrastructure/scar_patches_revised.geojson"))['features']])
main=max(getattr(scar,'geoms',[scar]),key=lambda g:g.area)
a=json.load(open(R+"reference/aer_pipelines_near_site.geojson"))['features']
def gl(g):
    L=0
    for gg in getattr(g,'geoms',[g]):
        if gg.geom_type=='LineString':
            xs,ys=gg.xy; L+=sum(G.inv(xs[i],ys[i],xs[i+1],ys[i+1])[2] for i in range(len(xs)-1))
    return L
def dm(g1,g2):
    p,q=nearest_points(g1,g2); return G.inv(p.x,p.y,q.x,q.y)[2], p
R11=(-110.9577,52.7678); A=Point(-110.9063,52.7728); B=Point(-110.89965,52.77045)
start=Point(-110.92626,52.77079)  # best single-point fit
d=pd.read_csv(R+"firms/detections.csv"); L=d[d.acq_datetime_mdt=="2026-10-17 12:17 MDT"]
Lp=unary_union([Point(x,y) for x,y in zip(L.longitude,L.latitude)])
# start zone: line 1.4-2.2 km at 80 deg
pts=[G.fwd(*R11,80,dd)[:2] for dd in np.arange(1400,2201,50)]; startline=LineString(pts)
# modelled arrival (central case) for pre-front; GeoTIFF in EPSG:3400, hours since midnight
arr=rasterio.open(R+"authentic-stoic-stress-test/part8b_ignition/arrival_C_2x_line_0715.tif"); AR=arr.read(1); tf=Transformer.from_crs(4326,arr.crs,always_xy=True).transform
post=rasterio.open(R+"authentic-stoic-stress-test/part8_range11/arrival_S2_station_veer_scar_limited_8kmh_front316.tif"); PR=post.read(1); tfp=Transformer.from_crs(4326,post.crs,always_xy=True).transform
def arrival_at(p):
    x,y=tf(p.x,p.y); i,j=arr.index(x,y)
    v=AR[i,j] if 0<=i<AR.shape[0] and 0<=j<AR.shape[1] else np.nan
    if np.isfinite(v): return f"{int(v):02d}:{int(round((v%1)*60))%60:02d} (pre-front model)"
    x,y=tfp(p.x,p.y); i,j=post.index(x,y)
    v=PR[i,j] if 0<=i<PR.shape[0] and 0<=j<PR.shape[1] else np.nan
    if np.isfinite(v) and v<1e5: m=15*60+v; return f"{int(m//60):02d}:{int(m%60):02d} (after the wind shift)"
    return "not reached in model"
rows=[]
for f in a:
    g=shape(f['geometry']); p=f['properties']
    dist,_=dm(g,main)
    if dist>1000: continue
    inside=gl(g.intersection(main)) if g.intersects(main) else 0
    near_pt=nearest_points(g,main)[0] if not g.intersects(main) else g.intersection(main).representative_point()
    rows.append(dict(licence_line=p.get('LIC_LI_NO'),licensee=p.get('COMP_NAME'),status=p.get('SEG_STATUS'),substance=p.get('SUBSTANCE1'),
        diameter_mm=p.get('OUT_DIAMET'),maop_kpa=p.get('PIPE_MAOP'),material=p.get('PIP_MATERL'),from_=f"{p.get('FROM_FAC')} {p.get('FROM_LOC')}",to=f"{p.get('TO_FAC')} {p.get('TO_LOC')}",
        seg_km=p.get('SEG_LENGTH'),m_inside_burn=round(inside),m_to_burn=round(dist),
        m_to_start_zone=round(dm(g,startline)[0]),m_to_best_start_point=round(dm(g,start)[0]),m_to_noon_fire=round(dm(g,Lp)[0]),
        m_to_range2=round(dm(g,A)[0]),m_to_road_head=round(dm(g,B)[0]),
        fire_reached=arrival_at(near_pt) if (inside>0 or dist<50) else "",
        lat=round(near_pt.y,5),lon=round(near_pt.x,5)))
df=pd.DataFrame(rows).sort_values(['m_to_burn','m_to_start_zone'])
df.to_csv("pipelines_vs_fire.csv",index=False)
print(len(df),'segments within 1 km of main burn'); print(df.status.value_counts().to_dict(), df.substance.value_counts().to_dict())
print(df[['licence_line','status','substance','diameter_mm','maop_kpa','m_inside_burn','m_to_burn','m_to_start_zone','m_to_noon_fire','m_to_range2','m_to_road_head','fire_reached']].head(25).to_string(index=False))
print('nearest operating gas to start zone', df[(df.status=='Operating')&(df.substance=='Natural Gas')].m_to_start_zone.min(),'to noon fire',df[(df.status=='Operating')&(df.substance=='Natural Gas')].m_to_noon_fire.min())
print('max diameter within 1km', df.diameter_mm.astype(float).max(), 'any NEB', [f['properties'].get('IS_NEB') for f in a if f['properties'].get('IS_NEB')=='Y'][:3])
