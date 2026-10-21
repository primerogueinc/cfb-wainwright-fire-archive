import netCDF4, glob, numpy as np, pyproj, math, sys, json, datetime as dt
B=(52.7767,-110.9210); R=float(sys.argv[2]) if len(sys.argv)>2 else 25
def hav(la1,lo1,la2,lo2):
    p1,p2=np.radians(la1),np.radians(la2); dl=np.radians(lo2-lo1); dp=p2-p1
    return 2*6371*np.arcsin(np.sqrt(np.sin(dp/2)**2+np.cos(p1)*np.cos(p2)*np.sin(dl/2)**2))
cache={}; out=[]
for f in sorted(glob.glob(sys.argv[1]+'/*.nc')):
    d=netCDF4.Dataset(f); key=(d['x'].shape,d['y'].shape,float(d['x'][0]),float(d['y'][0]))
    if key not in cache:
        pr=d['goes_imager_projection']; h=pr.perspective_point_height
        p=pyproj.Proj(proj='geos',h=h,lon_0=pr.longitude_of_projection_origin,sweep=pr.sweep_angle_axis,a=pr.semi_major_axis,b=pr.semi_minor_axis)
        x=d['x'][:]*h; y=d['y'][:]*h
        # coarse locate
        bx,by=p(B[1],B[0]); ix=np.argmin(abs(x-bx)); iy=np.argmin(abs(y-by))
        sl=(slice(max(iy-15,0),iy+16),slice(max(ix-15,0),ix+16))
        X,Y=np.meshgrid(x[sl[1]],y[sl[0]]); lo,la=p(X,Y,inverse=True)
        cache[key]=(sl,la,lo,hav(B[0],B[1],la,lo),(iy,ix))
    sl,la,lo,dist,c=cache[key]
    m=d['Mask'][sl].filled(0); pw=d['Power'][sl].filled(np.nan) if hasattr(d['Power'][sl],'filled') else d['Power'][sl]
    t=f.split('_s')[1][:13]; T=dt.datetime.strptime(t[:11],'%Y%j%H%M')-dt.timedelta(hours=6)
    fire=[(int(m[i]),round(float(dist[i]),1),round(float(la[i]),3),round(float(lo[i]),3),None if np.isnan(pw[i]) else round(float(pw[i]),1)) for i in zip(*np.where(((m>=10)&(m<=15))|((m>=30)&(m<=35)))) if dist[i]<R]
    near=np.unravel_index(np.argmin(dist),dist.shape)
    out.append((T.strftime('%m-%d %H:%M'),int(m[near]),round(float(dist[near]),1),fire))
for o in out: 
    if o[3] or '--all' in sys.argv: print(o)
print('files',len(out),'nearest-pixel mask counts',{k:sum(1 for o in out if o[1]==k) for k in set(o[1] for o in out)})
