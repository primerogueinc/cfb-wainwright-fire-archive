import json,csv,math,numpy as np,rasterio
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from rasterio.warp import reproject, Resampling, calculate_default_transform
from shapely.geometry import shape, Point, MultiPoint, box, Polygon
import shapely
R='/home/claude/cfb-wainwright-fire-archive/'; O='/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/ach/'
ext=(-110.955,-110.85,52.735,52.80)
with rasterio.open(R+'data/copernicus/dnbr.tif') as s:
    tr,w,h=calculate_default_transform(s.crs,'EPSG:4326',s.width,s.height,*s.bounds)
    a=np.full((h,w),np.nan,'float32'); reproject(rasterio.band(s,1),a,dst_transform=tr,dst_crs='EPSG:4326',resampling=Resampling.nearest)
    left,top=tr.c,tr.f; right=left+tr.a*w; bottom=top+tr.e*h
fig,ax=plt.subplots(figsize=(13,10))
im=ax.imshow(a,extent=(left,right,bottom,top),cmap='YlOrBr',vmin=0,vmax=0.7,interpolation='nearest')
plt.colorbar(im,ax=ax,shrink=0.6,label='dNBR (Sentinel-2, Oct 4 vs Oct 19)')
for f in json.load(open(R+'data/infrastructure/scar_patches_revised.geojson'))['features']:
    g=shape(f['geometry']); x,y=g.exterior.xy; ax.plot(x,y,'r-',lw=1.6 if f['properties']['patch']=='main Oct 17 run' else 0.8)
osm=json.load(open(R+'data/infrastructure/osm_infrastructure_ODbL.geojson'))['features']
for f in osm:
    p=f['properties']; g=shape(f['geometry'])
    if not g.intersects(box(ext[0],ext[2],ext[1],ext[3])): continue
    if p['kind']=='road': x,y=g.xy; ax.plot(x,y,color='grey',lw=1,ls='--')
    elif p['kind']=='water': x,y=g.exterior.xy; ax.fill(x,y,color='#7fb3d5',alpha=.6)
    elif p['kind']=='military' and p['military']=='range':
        x,y=g.exterior.xy; ax.plot(x,y,'b-',lw=1.2); ax.text(g.centroid.x,g.centroid.y,p['name'],color='b',fontsize=8,ha='center')
    elif p['name']=='CFB Wainwright': x,y=g.exterior.xy; ax.plot(x,y,'k-',lw=2,alpha=.6,label='CFB Wainwright boundary (OSM)')
det=list(csv.DictReader(open(R+'data/firms/detections.csv')))
L=[(float(d['longitude']),float(d['latitude'])) for d in det if d['source']=='LANDSAT_NRT' and d['acq_date']=='2026-10-17' and 52.7<float(d['latitude'])<52.85]
V=[(float(d['longitude']),float(d['latitude'])) for d in det if d['source']=='VIIRS_NOAA20_NRT' and d['acq_date']=='2026-10-17']
V18=[(float(d['longitude']),float(d['latitude'])) for d in det if d['acq_date']=='2026-10-18' and 52.7<float(d['latitude'])<52.85]
hull=MultiPoint(L+V).convex_hull; x,y=hull.exterior.xy; ax.plot(x,y,'c-',lw=1.5,label='Hull of 12:17 + 14:49 detections (min. pre-shift fire)')
ax.scatter(*zip(*L),s=10,c='cyan',ec='k',lw=.3,label='Landsat 12:17 MDT',zorder=5)
ax.scatter(*zip(*V),s=40,marker='s',c='gold',ec='k',label='VIIRS NOAA-20 14:49 MDT',zorder=5)
ax.scatter(*zip(*V18),s=40,marker='s',c='none',ec='k',label='VIIRS Oct 18',zorder=5)
gp=list(csv.DictReader(open(O+'goes_fire_pixels.csv'))); seen=set()
dx,dy=-1.4*math.sin(math.radians(31.6))/(111.32*math.cos(math.radians(52.77))),-1.4*math.cos(math.radians(31.6))/111.32
for g in gp:
    c=[tuple(map(float,s.split(','))) for s in g['corners'].split(';')]
    if g['corners'] in seen: continue
    seen.add(g['corners'])
    poly=Polygon(c); x,y=poly.exterior.xy; ax.plot(x,y,color='m',lw=.8,ls=':')
    pc=shapely.affinity.translate(poly,dx,dy); x,y=pc.exterior.xy; ax.plot(x,y,color='m',lw=1.4)
    ax.text(pc.centroid.x,pc.centroid.y,f"GOES {g['mdt']}\n{float(g['power_mw']):.0f} MW",color='m',fontsize=8,ha='center')
ax.plot([],[],color='m',ls=':',label='GOES-18 fire pixel footprint (raw)'); ax.plot([],[],color='m',label='same, shifted 1.4 km SW (terrain parallax est.)')
# downwind band
g=list(csv.DictReader(open(O+'scar_grid_upwind_distances.csv')))
band=[(float(r['x']),float(r['y'])) for r in g if r['A_hull_306'] not in ('','None') and 600<=float(r['A_hull_306'])<=1500]
ax.scatter(*zip(*band),s=2,c='lime',alpha=.5,label='Burned cells 0.6-1.5 km downwind (306 deg) of pre-shift hull')
Z={'H1':box(-110.912,52.760,-110.895,52.778),'H2':box(-110.915,52.778,-110.895,52.795),'H3':box(-110.880,52.735,-110.850,52.770),'H4':box(-110.955,52.735,-110.912,52.795)}
for k,z in Z.items():
    x,y=z.exterior.xy; ax.plot(x,y,'k:',lw=1); ax.text(z.bounds[0]+.001,z.bounds[3]-.002,k,fontsize=12,weight='bold')
ax.annotate('',xy=(-110.86,52.792),xytext=(-110.867,52.797),arrowprops=dict(arrowstyle='->',lw=2,color='navy'))
ax.text(-110.874,52.7985,'Wind after 3:16 p.m.\n(306 deg, NW)',fontsize=8,color='navy')
ax.annotate('',xy=(-110.874,52.79),xytext=(-110.881,52.785),arrowprops=dict(arrowstyle='->',lw=2,color='darkred'))
ax.text(-110.895,52.783,'Wind before (235 deg, SW)',fontsize=8,color='darkred')
ax.set_xlim(ext[0],ext[1]); ax.set_ylim(ext[2],ext[3]); ax.set_aspect(1/math.cos(math.radians(52.77)))
ax.legend(loc='lower left',fontsize=7); ax.set_title('ACH geometry: burn severity, detections, OSM ranges, hypothesis zones (WGS84)')
plt.tight_layout(); plt.savefig(O+'ach_map.png',dpi=110)
