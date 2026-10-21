import sys,csv,datetime as dt,numpy as np; sys.path.insert(0,'.')
from style import *
r=list(csv.DictReader(open('/home/claude/cfb-wainwright-firms-history-3km-2012-2026.csv')))
days={}
for x in r:
    d=x['acq_date']; days.setdefault(d,[]).append(float(x['km_from_oct17_site']))
print(len(days), len({d[:4] for d in days}))
W,H=1600,980
fig=frame(W,H,"NASA FIRE DETECTIONS WITHIN 3 KM OF THE OCT. 17 SITE  ·  2012–2026","Fire on this part of the range is a regular event",
  f"Days with a satellite fire detection within 3 km. Fire was detected every year from 2012 to 2026 except 2015: {len(days)} fire-days.")
ax=fig.add_axes([0.08,0.19,0.86,0.62]); ax.set_facecolor(PANEL); [s.set_color(GRID) for s in ax.spines.values()]
for d,k in days.items():
    t=dt.date.fromisoformat(d); y=t.year; doy=t.timetuple().tm_yday
    near=min(k)<=0.5; c=RED if near else LAND
    if d=='2026-10-17': c=YEL
    ax.plot(doy,y,'o',ms=13 if d!='2026-10-17' else 20,color=c,mec=BG,mew=1.2,zorder=3)
ms=[1,32,60,91,121,152,182,213,244,274,305,335]
ax.set_xticks([m+14 for m in ms]); ax.set_xticklabels(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])
for m in ms: ax.axvline(m,color=GRID,lw=1)
ax.set_xlim(1,366); ax.set_ylim(2026.7,2011.3); ax.set_yticks(range(2012,2027)); ax.tick_params(colors=CREAM,labelsize=13)
ax.axvspan(244,335,color=GOLD,alpha=.06)
ax.annotate("Oct. 17, 2026",(290,2026),(318,2024.6),color=YEL,fontsize=14,fontweight='bold',arrowprops=dict(arrowstyle='->',color=YEL))
fig.text(0.08,0.135,"●",color=LAND,fontsize=18,va='center'); fig.text(0.1,0.135,"Fire detected 0.5–3 km from the site",color=CREAM,fontsize=13,va='center')
fig.text(0.34,0.135,"●",color=RED,fontsize=18,va='center'); fig.text(0.36,0.135,"Within 0.5 km of the site",color=CREAM,fontsize=13,va='center')
fig.text(0.54,0.135,"●",color=YEL,fontsize=22,va='center'); fig.text(0.565,0.135,"Oct. 17, 2026",color=CREAM,fontsize=13,va='center')
footer(fig,H,["Source: NASA FIRMS archive (MODIS, VIIRS and Landsat), queried by Prime Rogue for a 3 km radius around 52.7767 N, 110.9210 W. Landsat coverage is partial for 2022–25.",
 "Detections show heat, not cause. Many are likely prescribed burns or range fires; the records do not say which."])
save(fig,'g5.png','/home/claude/cfb-wainwright-fire-history.jpg',W,H)
