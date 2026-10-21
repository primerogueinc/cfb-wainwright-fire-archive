import tifffile,glob,numpy as np
from PIL import Image,ImageDraw,ImageFont
SITE=(52.7767,-110.921); LAKE=(52.755,-110.915)
D={'2026-10-04':'461672e1-Browser_images_11','2026-10-16':'07ee7e4a-Browser_images_10','2026-10-17':'f599aa34-Browser_images_9','2026-10-18':'9f3cd561-Browser_images_8'}
def load(date,band):
    f=glob.glob(f'{D[date]}/*_{band}*.tiff')[0]; t=tifffile.TiffFile(f); p=t.pages[0]
    dx,dy,_=p.tags[33550].value; tp=p.tags[33922].value; return p.asarray().astype(float),(tp[3],tp[4],dx,dy)
# common output grid: lat/lon box
la0,la1,lo0,lo1=52.68,52.86,-111.10,-110.72; ny,nx=120,160
LA=np.linspace(la1,la0,ny); LO=np.linspace(lo0,lo1,nx)
def regrid(a,g):
    W,N,dx,dy=g; iy=np.clip(((N-LA)/dy).astype(int),0,a.shape[0]-1); ix=np.clip(((LO-W)/dx).astype(int),0,a.shape[1]-1)
    return a[np.ix_(iy,ix)]
out={}
for d in D:
    tc,g=load(d,'True_color'); out[d]={'tc':np.dstack([regrid(tc[...,i],g) for i in range(3)])}
    b8,g=load(d,'B08'); b12,g=load(d,'B12'); out[d]['b8']=regrid(b8,g); out[d]['b12']=regrid(b12,g)
np.save('grid.npy',np.array([la0,la1,lo0,lo1,ny,nx]))
import pickle; pickle.dump(out,open('s3grid.pkl','wb'))
