import numpy as np,glob,pyproj,sys
from PIL import Image,ImageDraw,ImageFont
h=35786023.0; p=pyproj.Proj(proj='geos',h=h,lon_0=-137.0,sweep='x',a=6378137.0,b=6356752.31414)
TOWN=(52.8395,-110.857); B=(52.7767,-110.921)
F="/usr/share/fonts/opentype/inter/"
def load(b,t): return np.load(f'goes18_C{b}_290{t}.npz')
def resamp(src,dst):
    ix=np.clip(np.searchsorted(src['x'],dst['x']),0,len(src['x'])-1)
    yy=src['y']; iy=np.clip(np.searchsorted(-yy,-dst['y']),0,len(yy)-1)
    return src['a'][np.ix_(iy,ix)]
def frame(t,scale=3):
    r=load('02',t); R=r['a']; Bl=resamp(load('01',t),r); N=resamp(load('03',t),r); T7=load('07',t)
    G=0.45*R+0.1*N+0.45*Bl
    rgb=np.dstack([R,G,Bl]); rgb=np.clip(rgb,0,1)**(1/2.2)
    im=Image.fromarray((np.nan_to_num(rgb)*255).astype(np.uint8)).resize((R.shape[1]*scale,R.shape[0]*scale),Image.LANCZOS).convert('RGBA')
    d=ImageDraw.Draw(im)
    def px(la,lo):
        X,Y=p(lo,la); return ((X-r['x'][0])/(r['x'][1]-r['x'][0])*scale, (Y-r['y'][0])/(r['y'][1]-r['y'][0])*scale)
    # band7 hot pixels
    a=T7['a']; med=np.nanmedian(a)
    from scipy.ndimage import median_filter
    an=a-median_filter(a,size=9)
    for j in range(a.shape[0]):
        for i in range(a.shape[1]):
            if an[j,i]>10 and abs(j-int(T7['cy']))<=6 and abs(i-int(T7['cx']))<=8:
                X0,X1=T7['x'][i]-1002,T7['x'][i]+1002; Y0,Y1=T7['y'][j]+1002,T7['y'][j]-1002
                x0=(X0-r['x'][0])/(r['x'][1]-r['x'][0])*scale; x1=(X1-r['x'][0])/(r['x'][1]-r['x'][0])*scale
                y0=(Y0-r['y'][0])/(r['y'][1]-r['y'][0])*scale; y1=(Y1-r['y'][0])/(r['y'][1]-r['y'][0])*scale
                d.rectangle([min(x0,x1),min(y0,y1),max(x0,x1),max(y0,y1)],outline=(255,60,30,255),width=3)
    for (la,lo),lab in [(TOWN,'Wainwright'),(B,'')]:
        x,y=px(la,lo); d.ellipse([x-5,y-5,x+5,y+5],outline=(255,255,255,255),width=2)
        if lab: d.text((x+8,y-10),lab,fill=(255,255,255,255),font=ImageFont.truetype(F+'Inter-Bold.otf',16))
    x,y=px(*B); d.line([x-14,y,x-7,y],fill=(255,214,0,255),width=2); d.line([x+7,y,x+14,y],fill=(255,214,0,255),width=2); d.line([x,y-14,x,y-7],fill=(255,214,0,255),width=2); d.line([x,y+7,x,y+14],fill=(255,214,0,255),width=2)
    hh=int(t[:2])-6; lab=f"{hh-12 if hh>12 else hh}:{t[2:]} p.m. MT"
    d.rectangle([0,0,190,30],fill=(0,0,0,170)); d.text((8,5),lab,fill=(255,255,255,255),font=ImageFont.truetype(F+'Inter-Bold.otf',18))
    return im,med
if __name__=='__main__':
    for t in sys.argv[1:]:
        im,med=frame(t); im.convert('RGB').save(f'f_{t}.jpg',quality=90); print(t,im.size,round(float(med),1))
