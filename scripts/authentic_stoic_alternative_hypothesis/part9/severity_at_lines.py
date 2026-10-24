import os
import json, numpy as np, rasterio
from shapely.geometry import shape, Point, LineString
from shapely.ops import unary_union, transform as stf
from pyproj import Transformer
R=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../data/")
dn=rasterio.open(R+"copernicus/severity_matched_10m/dnbr_10m_oct04_oct19.tif"); D=dn.read(1).astype(float)
dv=rasterio.open(R+"copernicus/severity_matched_10m/dndvi_10m_oct04_oct19.tif"); V=dv.read(1).astype(float)
print(dn.crs, dn.res, D.shape, np.nanpercentile(D,[5,50,95]))
tf=Transformer.from_crs(4326,dn.crs,always_xy=True).transform
feats=[f for f in json.load(open(R+"reference/aer_pipelines_near_site.geojson"))['features'] if f['properties']['LIC_LI_NO'] in ('58333-78','58333-113')]
yy,xx=np.mgrid[0:D.shape[0],0:D.shape[1]]
X,Y=dn.transform*(xx+0.5,yy+0.5)
burn=D>=0.10
out={}
for f in feats:
    g=stf(tf,shape(f['geometry'])); name=f['properties']['LIC_LI_NO']
    print(name, g.geom_type, round(g.length), 'start',[round(c) for c in list(g.coords)[0]] if g.geom_type=='LineString' else '')
    # distance of each pixel to line
    from shapely import vectorized
    dist=np.full(D.shape,np.inf)
    # approximate: sample line every 5 m, KD distance
    from scipy.spatial import cKDTree
    pts=np.array([g.interpolate(s).coords[0] for s in np.arange(0,g.length,5)])
    t=cKDTree(pts); d,_=t.query(np.c_[X.ravel(),Y.ravel()]); dist=d.reshape(D.shape)
    # severity profile vs distance from line, only near burn (within 300 m of line and in box)
    prof=[]
    for a,b in [(0,15),(15,30),(30,60),(60,100),(100,200),(200,300)]:
        m=(dist>=a)&(dist<b)&np.isfinite(D)
        prof.append((f"{a}-{b} m",int(m.sum()),round(float(np.nanmedian(D[m])),3),round(float(np.nanpercentile(D[m],90)),3),round(float((D[m]>=0.27).mean()),2)))
    out[name]=prof
    for p in prof: print('  ',p)
    # along-line sampling inside burn at 10 m: local maxima
    s=np.arange(0,g.length,10); vals=[]
    for si in s:
        x,y=g.interpolate(si).coords[0]; i,j=dn.index(x,y)
        if 0<=i<D.shape[0] and 0<=j<D.shape[1]: vals.append((si,D[i,j],V[i,j]))
    vals=np.array(vals)
    if len(vals):
        inb=vals[:,1]>=0.10
        print('   along line: n',len(vals),'burned frac',inb.mean().round(2),'max',vals[:,1].max().round(3),'at m',vals[vals[:,1].argmax(),0])
        np.savetxt(f"profile_{name}.csv",vals,delimiter=",",header="m_along,dnbr,dndvi",fmt="%.3f")
json.dump(out,open("sev_lines.json","w"),indent=1)


f78=[f for f in feats if f['properties']['LIC_LI_NO']=='58333-78'][0]; c=shape(f78['geometry'])
coords=list(c.coords) if c.geom_type=='LineString' else list(c.geoms[0].coords)
print('58333-78 endpoints lonlat',coords[0],coords[-1])

# ---- radial and sector test around points of interest
R=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../data/")
dn=rasterio.open(R+"copernicus/severity_matched_10m/dnbr_10m_oct04_oct19.tif"); D=dn.read(1).astype(float)
tf=Transformer.from_crs(4326,dn.crs,always_xy=True).transform
yy,xx=np.mgrid[0:D.shape[0],0:D.shape[1]]; X,Y=dn.transform*(xx+0.5,yy+0.5)
for name,(lo,la) in {"well 1-11 registered surface location":(-110.898943,52.773642),"line 58333-78 mapped west end":(-110.90429,52.77186),"line 78 x range road (~B)":(-110.90015,52.77186),"A Range 2":(-110.90632,52.77279),"B road head":(-110.89965,52.77045)}.items():
    x0,y0=tf(lo,la); r=np.hypot(X-x0,Y-y0); az=(np.degrees(np.arctan2(X-x0,Y-y0))+360)%360
    i,j=dn.index(x0,y0); print(f"\n{name}: pixel {D[i,j]:.3f}")
    print(np.round(D[i-4:i+5,j-4:j+5],2))
    for a,b in [(0,20),(20,50),(50,100),(100,200)]:
        m=(r>=a)&(r<b); print(f"  ring {a}-{b} m: median {np.median(D[m]):.3f}  frac>=0.27 {(D[m]>=0.27).mean():.2f}")
    sect=[]
    for s in range(0,360,45):
        m=(r<100)&(r>=20)&(((az-s)%360)<45); sect.append(f"{s}:{np.median(D[m]):.2f}")
    print("  sectors 20-100 m (az start:median):"," ".join(sect))
