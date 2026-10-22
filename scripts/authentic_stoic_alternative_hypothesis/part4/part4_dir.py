exec(open('part4_escape.py').read().split("rows=[]")[0])
def route(s,p,ang,v0,t_here,A,a):
    def arr(x,y):
        r,c=A.index(x,y)
        return a[r,c] if 0<=r<a.shape[0] and 0<=c<a.shape[1] else np.nan
    ux,uy=math.sin(math.radians(ang)),math.cos(math.radians(ang)); ds=np.arange(0,4001,20)
    xs=p.x+ds*ux; ys=p.y+ds*uy; fa=np.array([arr(x,y) for x,y in zip(xs,ys)])
    zz=pd.Series([z(x,y) for x,y in zip(xs,ys)]).ffill().bfill().values
    sp=v0*np.exp(-3.5*np.abs(np.diff(zz)/20+0.05))/math.exp(-3.5*0.05); tcum=np.concatenate([[0],np.cumsum(20/(sp*1000/60))])
    def ok(t0):
        for i in range(len(ds)):
            t=t0+tcum[i]; f=fa[i]
            if not np.isfinite(f): return True
            if f<=t-5 and i>0: return True
            if f<=t+0.5: return False
        return False
    lo,hi=t_here-90,t_here
    if not ok(lo): return None
    for _ in range(25):
        mid=(lo+hi)/2
        if ok(mid): lo=mid
        else: hi=mid
    return t_here-lo
out=[]
for s in SCHED:
    A=rasterio.open(f'arr_{s}.tif'); a=A.read(1).astype(float); a[a<-9000]=np.nan
    for k in ["A","B"]:
        p=pts[k]; r,c=A.index(p.x,p.y); t_here=a[r,c]
        if not np.isfinite(t_here):
            vals=[a[A.index(p.x+dx,p.y+dy)] for dx in range(-150,151,30) for dy in range(-150,151,30)]; t_here=np.nanmin(vals)
        for lab,ang in [("crosswind east (90)",90),("crosswind NE (45)",45),("downwind / away from fire (126)",126),("into the black, NW (306)",306),("south along the range road (180)",180)]:
            m=route(s,p,ang,8.0,t_here,A,a)
            out.append(dict(schedule=s,scenario=k,route=lab,min_needed_before_arrival=None if m is None else round(m,1)))
df=pd.DataFrame(out)
print(df.pivot_table(index=['scenario','route'],columns='schedule',values='min_needed_before_arrival',aggfunc='first').to_string())
df.to_csv('part4_routes.csv',index=False)
