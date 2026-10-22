exec(open('p5/veg.py').read().split('def sees')[0])
print('CHM>=2m share across whole raster %.0f%%, in scar %.0f%%'%(100*(H>=2).mean(), 0))
def sees(px,py,flame,eye,grass,Lg,k=25,step=5):
    d=np.hypot(EX-px,EY-py); idx=np.argsort(d)[:k]
    z0=samp(dem,Z,np.array([px]),np.array([py]))[0]+eye
    for i in idx:
        n=max(3,int(d[i]//step)); t=np.linspace(0,1,n); lx=px+(EX[i]-px)*t; ly=py+(EY[i]-py)*t
        zz=samp(dem,Z,lx,ly); hh=samp(chm,H,lx,ly); line=z0+(zz[-1]+flame-z0)*t
        if np.any(zz[1:-1]>line[1:-1]): continue
        if ((hh[1:-1]>=2)&(zz[1:-1]+hh[1:-1]>line[1:-1])).any(): continue
        if ((zz[1:-1]+grass>line[1:-1]).sum()*d[i]/(n-1))>Lg: continue
        return True
    return False
rows=[]
for eye,el in ((1.7,'standing'),(1.0,'kneeling'),(0.35,'prone')):
  for flame in (2.5,6.0):
    for g,Lg,gl in ((0,0,'no grass'),(0.6,30,'0.6 m cured grass')):
        v=np.array([sees(p.x,p.y,flame,eye,g,Lg) for p in P])
        rows.append(dict(posture=el,flame_m=flame,grass=gl,share_any=round(100*np.average(v,weights=w)),share_core=round(100*np.average(v[w>=12],weights=w[w>=12]))))
o=pd.DataFrame(rows); print(o.to_string()); o.to_csv('p5/posture_visibility.csv',index=False)
