import json,csv,math,rasterio,numpy as np
from shapely.geometry import shape,Point,MultiPoint,LineString
from shapely.ops import transform
from pyproj import Transformer
R='/home/claude/cfb-wainwright-fire-archive/'
T=Transformer.from_crs(4326,3400,always_xy=True).transform
P=lambda g: transform(T,g)
scar=P([shape(f['geometry']) for f in json.load(open(R+'data/infrastructure/scar_patches_revised.geojson'))['features'] if f['properties']['patch']=='main Oct 17 run'][0])
det=list(csv.DictReader(open(R+'data/firms/detections.csv')))
pts=[P(Point(float(d['longitude']),float(d['latitude']))) for d in det if d['acq_date']=='2026-10-17' and 52.7<float(d['latitude'])<52.85]
hull=MultiPoint(pts).convex_hull
osm=json.load(open(R+'data/infrastructure/osm_infrastructure_ODbL.geojson'))['features']
track=[shape(f['geometry']) for f in osm if f['properties']['osm_id']=='way/1570137515'][0]
print('track coords (first 8):',list(track.coords)[:8])
ds=rasterio.open(R+'data/copernicus/dnbr.tif'); Tu=Transformer.from_crs(4326,ds.crs,always_xy=True).transform
def dn(lon,lat,r=1):
    x,y=Tu(lon,lat); c,rw=~ds.transform*(x,y); a=ds.read(1)[int(rw)-r:int(rw)+r+1,int(c)-r:int(c)+r+1]; return round(float(np.nanmean(a)),3)
def up(p,region,wd):
    b=math.radians(wd); ray=LineString([(p.x,p.y),(p.x+8000*math.sin(b),p.y+8000*math.cos(b))])
    if region.contains(p): return 0
    i=ray.intersection(region); return None if i.is_empty else round(p.distance(i))
cands={'Range2 centroid (OSM)':(-110.9063,52.7728),'Range3 centroid (OSM)':(-110.9034,52.7839),'Road dead end (CanVec)':(-110.8996,52.7705),
 'Building (CanVec)':(-110.8963,52.7701),'Track @52.765':None,'Track @52.760':None,'Track @52.755':None,'East lobe @ -110.875,52.755':(-110.875,52.755),
 'East lobe Oct18 VIIRS':(-110.8662,52.7464),'SW lobe N of lake 52.763,-110.915':(-110.915,52.763),'West: pond 52.767,-110.93':(-110.93,52.7675),
 'North: Peterson Pond':(-110.903,52.787),'Range Control (OSM)':(-110.9005,52.8143),'Landsat SW end':(-110.9367,52.7704)}
Ti=Transformer.from_crs(4326,3400,always_xy=True)
# track positions
tl=transform(Transformer.from_crs(4326,4326,always_xy=True).transform,track)
for lat,s in ((52.765,'52.765'),(52.760,'52.760'),(52.755,'52.755')):
    # find lon on track at lat
    best=min(tl.coords,key=lambda c:abs(c[1]-lat)); cands[f'Track @{s}']=best
rows=[]
for k,(lon,lat) in cands.items():
    p=P(Point(lon,lat))
    rows.append(dict(point=k,lat=round(lat,4),lon=round(lon,4),in_scar=scar.contains(p),dist_scar_edge_m=round(scar.exterior.distance(p)),
      dist_to_preshift_hull_m=round(p.distance(hull)),upwind_dist_W269_m=up(p,hull,269),upwind_dist_NW306_m=up(p,hull,306),
      upwind_dist_NW306_hull400_m=up(p,hull.buffer(400),306),dnbr_60m=dn(lon,lat)))
w=csv.DictWriter(open('/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/ach/candidate_points.csv','w'),fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for r in rows: print(r)
