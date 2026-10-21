import json, csv, math, numpy as np, rasterio, sys
from shapely.geometry import shape, Point, MultiPoint, box, LineString
from shapely.ops import transform, unary_union
import shapely
from pyproj import Transformer
R='/home/claude/cfb-wainwright-fire-archive/'
OUT='/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/ach/'
T=Transformer.from_crs(4326,3400,always_xy=True).transform
Ti=Transformer.from_crs(3400,4326,always_xy=True).transform
P=lambda g: transform(T,g)
scar_ll=[shape(f['geometry']) for f in json.load(open(R+'data/infrastructure/scar_patches_revised.geojson'))['features'] if f['properties']['patch']=='main Oct 17 run'][0]
scar=P(scar_ll)
osm=json.load(open(R+'data/infrastructure/osm_infrastructure_ODbL.geojson'))['features']
named={f['properties']['name']:shape(f['geometry']) for f in osm if f['properties']['name']}
base=P(named['CFB Wainwright'])
det=list(csv.DictReader(open(R+'data/firms/detections.csv')))
def pts(src,date,lat=(52.7,52.85)):
    return [P(Point(float(d['longitude']),float(d['latitude']))) for d in det if d['source']==src and d['acq_date']==date and lat[0]<float(d['latitude'])<lat[1]]
L=pts('LANDSAT_NRT','2026-10-17'); V=pts('VIIRS_NOAA20_NRT','2026-10-17')
V18=pts('VIIRS_NOAA20_NRT','2026-10-18')+pts('VIIRS_SNPP_NRT','2026-10-18')
hullA=MultiPoint(L+V).convex_hull
pre={'A_hull':hullA,'B_hull+400m':hullA.buffer(400),'C_hull+800m∩scar':hullA.buffer(800).intersection(scar)}
res={}
res['scar_area_km2']=scar.area/1e6
res['hullA_area_km2']=hullA.area/1e6
res['hullA_in_scar_frac']=hullA.intersection(scar).area/hullA.area
res['landsat_in_scar']=sum(scar.buffer(30).contains(p) for p in L),len(L)
res['viirs_in_scar']=sum(scar.buffer(0).contains(p) for p in V),len(V)
res['viirs_dist_to_scar_m']=[round(scar.distance(p)) for p in V]
# features
feat={k:P(named[k]) for k in ['Range 2 (Grenade)','Range 3','Range 4','Range 5','Range 6','Range 8','Range 13','Range 14','Range 11','Range Control']}
fe={}
for k,g in feat.items():
    fe[k]=dict(in_scar_frac=round(g.intersection(scar).area/g.area,2) if g.area>0 else None,
               dist_to_scar_m=round(g.distance(scar)),
               dist_to_scar_edge_m=round(g.centroid.distance(scar.exterior)),
               centroid_inside=scar.contains(g.centroid),
               dist_to_nearest_landsat_m=round(min(g.distance(p) for p in L)),
               dist_to_nearest_viirs1449_m=round(min(g.distance(p) for p in V)),
               dist_to_hullA_m=round(g.distance(hullA)),
               area_m2=round(g.area))
res['features']=fe
# buildings / roads
res['bldg_52.7701_-110.8963']=dict(inside=scar.contains(P(Point(-110.8963,52.7701))),dist=round(scar.exterior.distance(P(Point(-110.8963,52.7701)))))
res['road_deadend_52.7705_-110.8996']=dict(inside=scar.contains(P(Point(-110.8996,52.7705))),dist=round(scar.exterior.distance(P(Point(-110.8996,52.7705)))))
for nm,ll in {'Peterson Pond':(-110.903,52.787),'Jamieson Lake':(-110.915,52.755),'CZWN station':(-111.0956,52.8294)}.items():
    res[nm+'_dist_to_scar_m']=round(scar.distance(P(Point(*ll))))
res['CZWN_to_scar_centroid_km']=round(P(Point(-111.0956,52.8294)).distance(scar.centroid)/1000,1)
res['oct18_viirs_inside_base']=[base.contains(p) for p in V18]
res['oct18_viirs_dist_base_boundary_m']=[round(base.exterior.distance(p)) for p in V18]
res['oct18_viirs_in_scar']=[scar.contains(p) for p in V18]
res['scar_area_outside_base_km2']=scar.difference(base).area/1e6
# GOES pixels: raw and terrain-parallax corrected (1.4 km toward 211.6 deg)
gp=list(csv.DictReader(open(OUT+'goes_fire_pixels.csv')))
shift=1400; az=math.radians(211.6)
gres=[]
for g in gp:
    c=[tuple(map(float,x.split(','))) for x in g['corners'].split(';')]
    fp=P(shapely.Polygon(c))
    fpc=shapely.affinity.translate(fp,shift*math.sin(az),shift*math.cos(az))
    ctr=P(Point(float(g['lon']),float(g['lat'])))
    ctrc=shapely.affinity.translate(ctr,shift*math.sin(az),shift*math.cos(az))
    cll=transform(Ti,ctrc)
    gres.append(dict(mdt=g['mdt'],mw=round(float(g['power_mw']),1),raw=(g['lat'],g['lon']),corr=(round(cll.y,4),round(cll.x,4)),
        raw_fp_overlap_scar_km2=round(fp.intersection(scar).area/1e6,2),corr_fp_overlap_scar_km2=round(fpc.intersection(scar).area/1e6,2),
        corr_fp_contains_R2=fpc.intersects(feat['Range 2 (Grenade)']),corr_fp_contains_R3=fpc.intersects(feat['Range 3']),fp_area_km2=round(fp.area/1e6,1)))
res['goes']=gres
# --- Hypothesis zones (WGS84 boxes) ---
Z={'H1':box(-110.912,52.760,-110.895,52.778),'H2':box(-110.915,52.778,-110.895,52.795),
   'H3':box(-110.880,52.735,-110.850,52.770),'H4':box(-110.960,52.735,-110.912,52.795),
   'H6':box(-110.912,52.735,-110.880,52.770).difference(box(-110.912,52.760,-110.895,52.778))}
Zp={k:P(v) for k,v in Z.items()}
zstat={}
with rasterio.open(R+'data/copernicus/dnbr.tif') as ds:
    dn=ds.read(1); tr=ds.transform; crs=ds.crs
Tu=Transformer.from_crs(3400,crs,always_xy=True).transform
def dnbr_at(x,y):
    ux,uy=Tu(x,y); c,r=~tr*(ux,uy); r=int(r); c=int(c)
    return dn[r,c] if 0<=r<dn.shape[0] and 0<=c<dn.shape[1] else np.nan
# grid within scar
minx,miny,maxx,maxy=scar.bounds; step=50
xs=np.arange(minx,maxx,step); ys=np.arange(miny,maxy,step)
grid=[(x,y) for x in xs for y in ys if scar.contains(Point(x,y))]
def upwind_dist(x,y,region,bearing_from):
    # distance from point travelling toward the direction the wind comes FROM until hitting region
    b=math.radians(bearing_from)
    ray=LineString([(x,y),(x+6000*math.sin(b),y+6000*math.cos(b))])
    if region.contains(Point(x,y)): return 0.0
    inter=ray.intersection(region)
    if inter.is_empty: return None
    return Point(x,y).distance(inter)
rows=[]
for x,y in grid:
    row=dict(x=x,y=y,dnbr=float(dnbr_at(x,y)))
    for k,z in Zp.items():
        if z.contains(Point(x,y)): row['zone']=k
    row.setdefault('zone','other')
    for pk,reg in pre.items():
        for wd in (269,306):
            row[f'{pk}_{wd}']=upwind_dist(x,y,reg,wd)
    rows.append(row)
cells=len(rows)
summary={}
for pk in pre:
  for wd in (269,306):
    key=f'{pk}_{wd}'
    ok=[r for r in rows if r[key] is not None and 600<=r[key]<=1500]
    tot=len(ok)
    summary[key]={z:round(sum(r['zone']==z for r in ok)/max(tot,1),2) for z in list(Zp)+['other']}
    summary[key]['n_cells_0.6-1.5km']=tot
    summary[key]['area_km2']=round(tot*step*step/1e6,2)
res['ray_summary']=summary
for k,z in Zp.items():
    zr=[r for r in rows if r['zone']==k]
    d=[r['dnbr'] for r in zr if not np.isnan(r['dnbr'])]
    zstat[k]=dict(zone_area_km2=round(z.area/1e6,2),burned_km2=round(z.intersection(scar).area/1e6,2),burned_frac=round(z.intersection(scar).area/z.area,2),
        mean_dnbr=round(float(np.mean(d)),3) if d else None, p90_dnbr=round(float(np.percentile(d,90)),3) if d else None,
        inside_base_frac=round(z.intersection(base).area/z.area,2),
        min_dist_to_hullA_m=round(z.distance(hullA)), max_dist_to_hullA_m=round(max(Point(c).distance(hullA) for c in z.intersection(scar).exterior.coords) if not z.intersection(scar).is_empty and z.intersection(scar).geom_type=='Polygon' else -1))
res['zones']=zstat
# spread-rate check: post-shift run length
far=max((Point(x,y).distance(hullA),x,y) for x,y in grid)
fl=transform(Ti,Point(far[1],far[2]))
res['farthest_burn_from_hullA_m']=(round(far[0]),round(fl.y,4),round(fl.x,4))
for mins in (10,20,30,40):
    res[f'ROS_kmh_if_run_took_{mins}min']=round(far[0]/1000/(mins/60),1)
res['ROS_kmh_rutland_1km_in_30_60s']=(60,120)
# NW lobe vs SE lobe: dnbr comparison
json.dump(res,open(OUT+'geometry_results.json','w'),indent=1,default=str)
with open(OUT+'scar_grid_upwind_distances.csv','w') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader()
    for r in rows:
        ll=transform(Ti,Point(r['x'],r['y'])); r2=dict(r); r2['x']=round(ll.x,5); r2['y']=round(ll.y,5); w.writerow(r2)
print(json.dumps(res,indent=1,default=str))
