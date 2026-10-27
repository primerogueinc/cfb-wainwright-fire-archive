import sys, math; sys.path.insert(0,'..'); sys.path.insert(0,'../vis')
from pr import *
from pr import _LOGO
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.colors import LinearSegmentedColormap, LightSource
for n in ["Inter-Medium.otf","Inter-Bold.otf"]: fm.fontManager.addfont(F+n)
plt.rcParams["font.family"]="Inter"
hx=lambda c:"#%02x%02x%02x"%c
CM=LinearSegmentedColormap.from_list("rg",["#7a1f1f","#e0603c","#e8c15a","#40e0d0"])
df=pd.read_csv("perm.csv.gz"); m=df[(df.cue!="FAN")&(df.margin==3.0)]
ORDER=["optimal (best route)","crosswind east (90°)","away from the fire (downwind)","south along range road (180°)","north along range road (0°)","random direction"]
LAB={"optimal (best route)":"Best possible route","crosswind east (90°)":"Crosswind, east","away from the fire (downwind)":"Away from the fire (downwind)",
     "south along range road (180°)":"South along the range road","north along range road (0°)":"North along the range road","random direction":"Random direction (disoriented)"}
CUES=["gust front (3:16)","flames in sight","fire within 300 m"]; CL={"gust front (3:16)":"Move at the\n3:16 gust","flames in sight":"Move when flames\ncome into sight","fire within 300 m":"Move when fire is\nwithin 300 m"}
# ---------- G1 heatmaps
fig,axs=plt.subplots(2,2,figsize=(17,11),facecolor=hx(BG))
for i,k in enumerate("AB"):
    for j,sp in enumerate(["jog in kit (8 km/h)","in smoke (3 km/h)"]):
        ax=axs[i,j]; ax.set_facecolor(hx(BG))
        t=m[(m.point==k)&(m.speed==sp)].pivot_table(index="strategy",columns=["cue","delay"],values="success",aggfunc="mean").reindex(ORDER)
        t=t[[(c,d) for c in CUES for d in (0,2,5,10)]]*100
        ax.imshow(t.values,cmap=CM,vmin=0,vmax=100,aspect="auto")
        for (r,c),v in np.ndenumerate(t.values):
            ax.text(c,r,f"{v:.0f}",ha="center",va="center",color="#111" if v>45 else "white",fontsize=11,fontweight="bold")
        ax.set_yticks(range(len(ORDER))); ax.set_yticklabels([LAB[o] for o in ORDER] if j==0 else []); ax.tick_params(colors=hx(CREAM),labelsize=11,length=0)
        ax.set_xticks(range(12)); ax.set_xticklabels([f"+{d}" for c in CUES for d in (0,2,5,10)],color=hx(MUTED),fontsize=10)
        for x in (3.5,7.5): ax.axvline(x,color=hx(BG),lw=4)
        for ci,c in enumerate(CUES): ax.text(ci*4+1.5,-0.95,CL[c],ha="center",va="bottom",color=hx(GOLD),fontsize=11,fontweight="bold")
        nm={"A":"A  Range 2 (on the rise)","B":"B  Road's end (in the hollow)"}[k]
        ax.set_title(f"{nm}   ·   {'jogging in kit, 8 km/h' if j==0 else 'slowed by smoke, 3 km/h'}",color=hx(CREAM),fontsize=13.5,fontweight="bold",loc="left",pad=48)
        for s_ in ax.spines.values(): s_.set_visible(False)
        ax.set_xlabel("minutes of delay after the cue (milling, gathering people, awaiting orders)",color=hx(MUTED),fontsize=10)
plt.subplots_adjust(left=0.17,right=0.99,top=0.9,bottom=0.07,hspace=0.55,wspace=0.04)
fig.savefig("_heat.png",dpi=100,facecolor=hx(BG)); plt.close(fig)
im,d=canvas(1800,250+1100+150,"THE AUTHENTIC STOIC STRESS TEST  ·  PART 4  ·  COULD THEY HAVE GOT OUT?","When they moved mattered more than which way",
 "Share of 30 fire scenarios (5 winds x 3 spread rates x steady or gusty flanks) in which someone on foot reaches unburned or already-burned ground\nwith at least 3 minutes to spare. Numbers are percentages.")
h=Image.open("_heat.png").convert("RGBA"); im.alpha_composite(h,(54,210))
footer(im,["Model: FBP grass spread on the mapped burn; escape on foot along straight routes, slope-adjusted (Tobler); safe = never burned, or burned 5+ min earlier. Best case:",
           "no embers or spotting; smoke modelled only as slower walking. Locations are estimates. Data: github.com/primerogueinc/cfb-wainwright-fire-archive. Graphic: Kevin Duska Jr. (Prime Rogue Inc.)"])
im.convert("RGB").save("../vis/cfb-wainwright-escape-matrix.jpg",quality=92,optimize=True); print("heat",im.size)
# ---------- G3 decision clock
c=pd.read_csv("clock.csv")
fig,axs=plt.subplots(1,2,figsize=(17,6.6),facecolor=hx(BG))
cues=df[df.cue!="FAN"].groupby(["point","cue"]).cue_time.median()
for ax,k in zip(axs,"AB"):
    ax.set_facecolor(hx(BG))
    for sp,ls_ in (("jog in kit (8 km/h)","-"),("in smoke (3 km/h)","--")):
        q=c[(c.point==k)&(c.speed==sp)].groupby("t0")[["optimal","away","random"]].mean()*100
        ax.plot(q.index,q.optimal,color=hx(TEAL),lw=3,ls=ls_,label=f"Best route, {sp.split(' (')[0]}")
        ax.plot(q.index,q.away,color=hx(GOLD),lw=2.2,ls=ls_,label=f"Away from the fire, {sp.split(' (')[0]}")
        ax.plot(q.index,q.random,color=hx(RED),lw=1.8,ls=ls_,label=f"Random direction, {sp.split(' (')[0]}")
    for (cn,col),yy_ in zip((("flames in sight",CREAM),("fire within 300 m",RED)),(88,79)):
        t=cues[(k,cn)]; ax.axvline(t,color=hx(col),lw=1.2,ls=":"); ax.text(t+0.2,yy_,{"flames in sight":"flames in sight\n(median)","fire within 300 m":"fire within\n300 m (median)"}[cn],color=hx(col),fontsize=10,va="top")
    ax.axvline(16,color=hx(CREAM),lw=1.2,ls=":"); ax.text(16.2,97,"3:16 gust",color=hx(CREAM),fontsize=10,va="top")
    ax.set_xlim(16,36); ax.set_ylim(0,102)
    ax.set_xticks(range(16,37,2)); ax.set_xticklabels([f"3:{t:02d}" for t in range(16,37,2)])
    ax.tick_params(colors=hx(MUTED),labelsize=10); ax.grid(color=hx(GRIDC))
    for s_ in ax.spines.values(): s_.set_visible(False)
    ax.set_title({"A":"A  Range 2 (on the rise)","B":"B  Road's end (in the hollow)"}[k],color=hx(CREAM),fontsize=14,fontweight="bold",loc="left")
    ax.set_xlabel("time they start moving (p.m.)",color=hx(MUTED),fontsize=11)
axs[0].set_ylabel("chance of reaching safe ground (%)",color=hx(MUTED),fontsize=11)
axs[0].legend(loc="lower right",bbox_to_anchor=(1.0,0.12),fontsize=9.5,facecolor=hx(BG),edgecolor="#35281f",labelcolor=hx(CREAM))
plt.subplots_adjust(left=0.06,right=0.99,top=0.9,bottom=0.13,wspace=0.12)
fig.savefig("_clock.png",dpi=100,facecolor=hx(BG)); plt.close(fig)
im,d=canvas(1800,250+660+140,"THE AUTHENTIC STOIC STRESS TEST  ·  PART 4  ·  THE DECISION CLOCK","Every minute after 3:16 cut the odds",
 "Chance of reaching safe ground on foot by the minute they start moving, across 30 fire scenarios. Solid: jogging in kit. Dashed: slowed by smoke.")
im.alpha_composite(Image.open("_clock.png").convert("RGBA"),(54,200))
footer(im,["Same model as the escape matrix. Safe = never burned, or burned 5+ min earlier, reached with 3+ minutes to spare. Best case: no embers or spotting.",
           "Locations are estimates. Data: github.com/primerogueinc/cfb-wainwright-fire-archive. Graphic: Kevin Duska Jr. (Prime Rogue Inc.)"])
im.convert("RGB").save("../vis/cfb-wainwright-decision-clock.jpg",quality=92,optimize=True); print("clock",im.size)
