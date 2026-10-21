import urllib.request,datetime as dt,concurrent.futures as cf,sys,os,time
K='YOUR_FIRMS_MAP_KEY'; A='-111.10,52.67,-110.74,52.88'
jobs=[]
def add(src,a,b,step):
    d=dt.date.fromisoformat(a); e=dt.date.fromisoformat(b)
    while d<=e:
        n=min(step,(e-d).days+1); jobs.append((src,d.isoformat(),n)); d+=dt.timedelta(days=n)
for spec in sys.argv[1:]:
    s,a,b,st=spec.split(':'); add(s,a,b,int(st))
def get(j):
    src,d,n=j; fn=f'raw/{src}_{d}_{n}.csv'
    if os.path.exists(fn): return 0
    for t in range(200):
        try:
            import subprocess; r=subprocess.run(['curl','-s','-m','90',f'https://firms.modaps.eosdis.nasa.gov/api/area/csv/{K}/{src}/{A}/{n}/{d}'],capture_output=True,text=True).stdout
            if not r.startswith('latitude') and not r.startswith('Invalid'): print('bad',j,r[:100]); time.sleep(3); continue
            if r.startswith('Invalid') or 'exceed' in r.lower(): time.sleep(60); continue
            open(fn,'w').write(r); return 1
        except Exception as e: time.sleep(3)
    print('fail',j); return 0
os.makedirs('raw',exist_ok=True)
with cf.ThreadPoolExecutor(3) as ex: print(sum(ex.map(get,jobs)),'of',len(jobs))
