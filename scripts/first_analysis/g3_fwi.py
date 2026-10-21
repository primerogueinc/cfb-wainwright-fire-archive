import sys,numpy as np; sys.path.insert(0,'.')
from style import *
W,H=1600,1150
fig=frame(W,H,"FIRE WEATHER INDEX  ·  CFB WAINWRIGHT AND AREA  ·  OCT. 2026","\"Fire index was low.\" Federal data put it at Extreme.",
   "Natural Resources Canada's Fire Weather Index for the base's weather station, rated on Alberta's danger classes.")
cls=[(0,4.5,"Low","#3E6B3A"),(4.5,10.5,"Moderate","#5B7A2E"),(10.5,18.5,"High","#8A7A22"),(18.5,29.5,"Very High","#9A5A1E"),(29.5,200,"Extreme","#8E2A1E")]
def bands(ax,top):
    for a,b,n,c in cls:
        ax.axhspan(a,min(b,top),color=c,alpha=.45,lw=0)
def sty(ax):
    ax.set_facecolor(PANEL); [s.set_color(GRID) for s in ax.spines.values()]; ax.tick_params(colors=CREAM,labelsize=13)
# panel A
a=fig.add_axes([0.06,0.20,0.40,0.56]); sty(a); top=45; bands(a,top); a.set_ylim(0,top)
d=[10,11,12,13,14,15,16,17,18]; v=[5.0,3.3,np.nan,6.5,15.6,11.3,16.3,30.8,37.4]
cols=[CREAM if x!=17 else YEL for x in d]
a.bar(d,[0 if np.isnan(x) else x for x in v],color=cols,width=0.62,edgecolor=BG)
for x,y in zip(d,v):
    a.text(x,(0 if np.isnan(y) else y)+0.8,"n/a" if np.isnan(y) else f"{y:.1f}",ha='center',color=CREAM if x!=17 else YEL,fontsize=13,fontweight='bold' if x==17 else 'normal')
a.set_xticks(d); a.set_xticklabels([f"Oct.\n{x}" for x in d]); a.set_ylabel("Fire Weather Index (noon)",color=CREAM,fontsize=14)
for lo,hi,n,c in cls:
    if lo<top: a.text(8.65,(lo+min(hi,top))/2,n,color=CREAM,fontsize=12,va='center',fontweight='semibold')
a.set_xlim(8.55,18.6)
a.set_title("CFB Wainwright station, daily",color=GOLD,fontsize=16,loc='left',fontweight='bold',pad=12)
a.annotate("Day of the fire: 30.8\nExtreme",(17,30.8),(13.9,38),color=YEL,fontsize=14,fontweight='bold',arrowprops=dict(arrowstyle='->',color=YEL))
# panel B
b=fig.add_axes([0.55,0.20,0.40,0.56]); sty(b); top=75; bands(b,top); b.set_ylim(0,top)
st=["Wainwright\n(base)","Vermilion","Lloydminster","Stettler","Vegreville","Coronation"]; sv=[30.8,31.9,39.2,55.9,58.1,67.2]
b.bar(range(6),sv,color=[YEL]+[CREAM]*5,width=0.62,edgecolor=BG)
for i,y in enumerate(sv): b.text(i,y+1.2,f"{y:.1f}",ha='center',color=YEL if i==0 else CREAM,fontsize=13,fontweight='bold' if i==0 else 'normal')
b.set_xticks(range(6)); b.set_xticklabels(st,fontsize=12); b.set_ylabel("Fire Weather Index (noon), Oct. 17",color=CREAM,fontsize=14)
b.axhline(29.5,color=RED,lw=2,ls='--'); b.text(-0.42,72,"Dashed line: Extreme begins at 29.5",color=CREAM,fontsize=12,va="top")
b.set_title("Oct. 17: every nearby station was Extreme",color=GOLD,fontsize=16,loc='left',fontweight='bold',pad=12)
fig.text(0.03,0.80,"Noon understates the afternoon: from ECCC hourly data, Prime Rogue calculates about 54 at 2 p.m., 59 at 3 p.m. and 91 at 4 p.m.",color=CREAM,fontsize=14)
footer(fig,H,["Fire Weather Index: Natural Resources Canada, Canadian Wildland Fire Information System, daily station files (noon standard time). No value published for Oct. 12.",
 "Classes: Alberta's thresholds as listed by CWFIS. Hourly figures: Prime Rogue calculation (Van Wagner 1977), which reproduces the CWFIS noon value."])
save(fig,'g3.png','/home/claude/cfb-wainwright-fire-danger.jpg',W,H)
