exec(open('perm.py').read().split("rows=[]")[0])
out=[]
for g in GRIDS:
    a=ARR[g]; s=g[0]
    for k in ("A","B"):
        p=P[k]; pr=prof[k]; fa=np.where(pr["inb"],a[pr["r"],pr["c"]],np.nan)
        for t0 in np.arange(16,40.01,0.5):
            wf=wfrom(s,t0); away=int(round(((wf+180)%360)/5))%72
            for sn in ("jog in kit (8 km/h)","in smoke (3 km/h)"):
                ok=success(fa,TC[(k,sn)],t0,3.0)
                out.append(dict(point=k,t0=t0,speed=sn,grid=str(g),optimal=float(ok.any()),away=float(ok[away]),east=float(ok[18]),random=float(ok.mean())))
pd.DataFrame(out).to_csv("clock.csv",index=False); print("ok")
