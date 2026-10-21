import io,urllib.request,h5py,numpy as np,pyproj,sys,re,subprocess,json
B=(52.7767,-110.9210)
sat,band,day,hh,mm=sys.argv[1:6]; R=float(sys.argv[6]) if len(sys.argv)>6 else 60
pre=f"ABI-L2-CMIPF/2026/{day}/{hh}/"
import urllib.request
xml=urllib.request.urlopen(f"https://noaa-{sat}.s3.amazonaws.com/?list-type=2&prefix={pre}").read().decode()
keys=[k for k in re.findall(r'<Key>([^<]*)</Key>',xml) if f'M6C{band}_' in k and f'_s2026{day}{hh}{mm}' in k]
k=keys[0]; url=f"https://noaa-{sat}.s3.amazonaws.com/{k}"
class RF(io.RawIOBase):
    BS=2**20
    def __init__(s,u):
        s.u=u; s.pos=0; s.cache={}
        r=urllib.request.urlopen(urllib.request.Request(u,method='HEAD')); s.size=int(r.headers['Content-Length'])
    def readable(s): return True
    def seekable(s): return True
    def tell(s): return s.pos
    def seek(s,o,w=0):
        s.pos={0:o,1:s.pos+o,2:s.size+o}[w]; return s.pos
    def blk(s,i):
        if i not in s.cache:
            a=i*s.BS; b=min(a+s.BS,s.size)-1
            s.cache[i]=urllib.request.urlopen(urllib.request.Request(s.u,headers={'Range':f'bytes={a}-{b}'})).read()
        return s.cache[i]
    def readinto(s,buf):
        n=min(len(buf),s.size-s.pos); out=b''
        while len(out)<n:
            i=(s.pos+len(out))//s.BS; off=(s.pos+len(out))%s.BS; out+=s.blk(i)[off:off+n-len(out)]
        buf[:n]=out; s.pos+=n; return n
f=h5py.File(io.BufferedReader(RF(url),buffer_size=2**20),'r')
pr=f['goes_imager_projection'].attrs; h=float(pr['perspective_point_height'][0])
p=pyproj.Proj(proj='geos',h=h,lon_0=float(pr['longitude_of_projection_origin'][0]),sweep='x',a=float(pr['semi_major_axis'][0]),b=float(pr['semi_minor_axis'][0]))
xs=f['x']; ys=f['y']; x=xs[:]*xs.attrs['scale_factor'][0]+xs.attrs['add_offset'][0]; y=ys[:]*ys.attrs['scale_factor'][0]+ys.attrs['add_offset'][0]
x*=h;y*=h
# bbox
la=np.array([B[0]-R/111,B[0]+R/111,B[0],B[0]]); lo=np.array([B[1],B[1],B[1]-R/67,B[1]+R/67])
bx,by=p(lo,la); ix0=np.argmin(abs(x-bx.min()));ix1=np.argmin(abs(x-bx.max())); iy0=np.argmin(abs(y-by.max())); iy1=np.argmin(abs(y-by.min()))
ix0,ix1=sorted((ix0,ix1)); iy0,iy1=sorted((iy0,iy1))
c=f['CMI']; a=c[iy0:iy1+1,ix0:ix1+1].astype(float); fv=c.attrs['_FillValue'][0]
a=np.where(a==fv,np.nan,a*c.attrs['scale_factor'][0]+c.attrs['add_offset'][0])
bxx,byy=p(B[1],B[0]); cx=np.argmin(abs(x-bxx))-ix0; cy=np.argmin(abs(y-byy))-iy0
np.savez(f"{sat}_C{band}_{day}{hh}{mm}.npz",a=a,cx=cx,cy=cy,x=x[ix0:ix1+1],y=y[iy0:iy1+1])
print(k.split('/')[-1][:60],a.shape,np.nanmin(a),np.nanmax(a),'center',cx,cy)
