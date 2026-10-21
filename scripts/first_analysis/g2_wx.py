import sys,csv,numpy as np; sys.path.insert(0,'.')
from style import *
rows=[r for r in csv.DictReader(open('../eccc/wain_hourly_2026-10.csv',encoding='utf-8-sig'))]
def get(day,hl):  # hl = LST hour
    for r in rows:
        if r['Day']==f'{day:02d}' and r['Time (LST)']==f'{hl:02d}:00': return r
H_=[];T=[];RH=[];WS=[];WD=[]
for hm in range(6,21):  # MDT hour
    r=get(17,hm-1); H_.append(hm)
    f=lambda k: float(r[k]) if r[k] not in ('',None) else np.nan
    T.append(f('Temp (°C)'));RH.append(f('Rel Hum (%)'));WS.append(f('Wind Spd (km/h)'));WD.append(f('Wind Dir (10s deg)')*10)
print(list(zip(H_,T,RH,WS,WD)))
G={6+5/60:16.9,7+6/60:21.3,8+58/60:23.2,10+52/60:26.5,11+1/60:29.8,12+54/60:23.6,13+34/60:45.7,14+48/60:50.8,15+16/60:82.0,16+9/60:72.2}  # max gust in hour ENDING at MDT hour (SWOB)
W,Hh=1600,1250
fig=frame(W,Hh,"CFB WAINWRIGHT WEATHER STATION  ·  OCT. 17, 2026  ·  MOUNTAIN TIME","The afternoon at the base's own weather station",
   "Hot, dry and windy by early afternoon. Then a west gust of 82 km/h at 3:16 p.m., and a swing to the northwest.")
ax1=fig.add_axes([0.07,0.46,0.86,0.30]); ax2=fig.add_axes([0.07,0.17,0.86,0.25])
for ax in (ax1,ax2):
    ax.set_facecolor(PANEL); [s.set_color(GRID) for s in ax.spines.values()]
    ax.tick_params(colors=CREAM,labelsize=13); ax.grid(color=GRID,lw=1); ax.set_xlim(5.6,20.4)
    for x,c in [(12.28,YEL),(14.82,YEL),(14.23,RED),(15.27,RED),(16,CREAM)]:
        ax.axvline(x,color=c,lw=1.6,ls=(0,(4,3)),alpha=.85)
xt=list(range(6,21,2)); lab=lambda h:f"{(h-1)%12+1} {'a.m.' if h<12 else 'p.m.'}"
ax1.set_xticks(xt); ax1.set_xticklabels([]); ax2.set_xticks(xt); ax2.set_xticklabels([lab(h) for h in xt])
ax1.plot(H_,T,color=RED,lw=3.5,marker='o'); ax1.set_ylabel("Temperature (°C)",color=RED,fontsize=14); ax1.set_ylim(0,30)
b=ax1.twinx(); b.plot(H_,RH,color=BLUE,lw=3.5,marker='o'); b.set_ylim(0,70); b.set_ylabel("Relative humidity (%)",color=BLUE,fontsize=14); b.tick_params(colors=CREAM,labelsize=13); [s.set_color(GRID) for s in b.spines.values()]
ax1.annotate("23.3 °C, 17% RH at 3 p.m.",(15,23.3),(16.4,27),color=CREAM,fontsize=13,arrowprops=dict(arrowstyle='->',color=CREAM))
ax1.annotate("12.9 °C, 43% at 4 p.m.",(16,12.9),(17.0,5),color=CREAM,fontsize=13,arrowprops=dict(arrowstyle='->',color=CREAM))
ax2.bar(H_,WS,width=0.55,color=LAND,label="Hourly wind speed")
gx=list(G); ax2.plot(gx,list(G.values()),color=YEL,lw=0,marker='D',ms=10,label="Peak gust in each available hourly report, at the time it occurred")
ax2.set_ylim(0,105); ax2.set_ylabel("km/h",color=CREAM,fontsize=14)
ax2.annotate("82 km/h gust\nfrom the west, 3:16 p.m.",(15.27,82),(16.55,88),color=YEL,fontsize=14,fontweight='bold',va='center',arrowprops=dict(arrowstyle='->',color=YEL))
for h,ws,wd in zip(H_,WS,WD):
    if np.isnan(wd): continue
    th=np.deg2rad(wd); u,v=-np.sin(th),-np.cos(th)
    ax2.annotate("",xy=(h+0.28*u,97+5.5*v),xytext=(h-0.28*u,97-5.5*v),arrowprops=dict(arrowstyle='-|>',color=CREAM,lw=2))
ax2.text(5.75,88,"Arrows: direction the wind blew toward",color=MUTED,fontsize=11)
ax2.legend(loc='upper left',bbox_to_anchor=(0,0.82),facecolor=PANEL,edgecolor=GRID,labelcolor=CREAM,fontsize=12)
tops=[(12.28,"1",YEL,"12:17 p.m. Landsat 8 detects fire"),(14.23,"2",RED,"2:14 p.m. ECCC wind warning for Wainwright"),(14.82,"3",YEL,"2:49 p.m. NOAA-20 detects fire"),(15.27,"4",RED,"3:16 p.m. peak gust, 82 km/h"),(16,"5",CREAM,"~4 p.m. DND: fire \"ignited\"")]
for x,n,c,t in tops:
    fig.text(0.07+0.86*(x-5.6)/14.8,0.772,n,color=BG,fontsize=13,ha='center',va='bottom',fontweight='black',bbox=dict(boxstyle='circle,pad=0.3',fc=c,ec='none'))
pos=[(0.07,0.848),(0.36,0.848),(0.66,0.848),(0.07,0.818),(0.36,0.818)]
for (x,n,c,t),(px,py) in zip(tops,pos):
    fig.text(px,py,n,color=BG,fontsize=11,ha='center',va='center',fontweight='black',bbox=dict(boxstyle='circle,pad=0.25',fc=c,ec='none'))
    fig.text(px+0.013,py,t,color=CREAM,fontsize=13,va='center')
footer(fig,Hh,["Hourly observations: ECCC, Wainwright CFB Airfield 21 (climate ID 301S001), converted from standard to daylight time. Gusts: ECCC SWOB records for CZWN.",
 "Arrows show wind direction (pointing downwind). Observations may be revised in quality control. Contains information licensed under the Open Government Licence – Canada."])
save(fig,'g2.png','/home/claude/cfb-wainwright-weather-oct17.jpg',W,Hh)
