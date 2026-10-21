import netCDF4 as nc, numpy as np, glob, os, sys, csv
from pyproj import Proj
root='/home/claude/cfb-wainwright-fire-archive/data/goes/fdc_raw'
out=[]
def geo(d):
    p=d['goes_imager_projection']; H=p.perspective_point_height
    pr=Proj(proj='geos',h=H,lon_0=p.longitude_of_projection_origin,sweep=p.sweep_angle_axis,a=p.semi_major_axis,b=p.semi_minor_axis)
    return pr,H
for sat in ['goes18','goes19']:
  files=sorted(glob.glob(f'{root}/{sat}/ABI-L2-FDCF/*.nc'))
  pr=None
  for f in files:
    s=os.path.basename(f).split('_s')[1][:11]  # yyyydddhhmm
    hh=int(s[7:9]); mm=int(s[9:11])
    if not (19<=hh<=23 or hh<=1): continue
    d=nc.Dataset(f)
    if pr is None:
        pr,H=geo(d); x=d['x'][:]*H; y=d['y'][:]*H
        tx,ty=pr(-110.91,52.77)
        ix=int(np.argmin(abs(x-tx))); iy=int(np.argmin(abs(y-ty)))
        sl=(slice(iy-12,iy+13),slice(ix-12,ix+13))
        X,Y=np.meshgrid(x[sl[1]],y[sl[0]])
        LON,LAT=pr(X,Y,inverse=True)
        dx=abs(x[1]-x[0]); dy=abs(y[1]-y[0])
    m=d['Mask'][sl]; pw=d['Power'][sl]
    fire=np.isin(np.asarray(m),[10,11,12,13,14,15,30,31,32,33,34,35])
    for (r,c) in zip(*np.where(fire)):
        # footprint corners
        cx=X[r,c]; cy=Y[r,c]
        cs=[pr(cx+sx*dx/2,cy+sy*dy/2,inverse=True) for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
        out.append(dict(sat=sat,utc=f'{s[7:9]}:{s[9:11]}',mdt=f'{(hh-6)%24:02d}:{mm:02d}',mask=int(m[r,c]),
          power_mw=float(pw[r,c]) if not np.ma.is_masked(pw[r,c]) else '',lat=round(float(LAT[r,c]),4),lon=round(float(LON[r,c]),4),
          corners=';'.join(f'{a:.4f},{b:.4f}' for a,b in cs)))
    d.close()
w=csv.DictWriter(open(sys.argv[1],'w'),fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
for o in out: print(o)
