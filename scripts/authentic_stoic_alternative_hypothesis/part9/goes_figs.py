import os
import json, numpy as np, pandas as pd
from shapely.geometry import shape, Polygon
from shapely.ops import unary_union
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, matplotlib.dates as mdates
R=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../data/")
d=pd.read_csv(R+"goes/oct17-18_extended/fire_timeline.csv"); d=d[d.satellite=="GOES-18"].copy()
d["t"]=pd.to_datetime(d.scan_start_mdt.str.replace(" MDT","")); d=d[(d.t>="2026-10-17 06:00")&(d.t<="2026-10-18 12:00")].sort_values("t")
# --- Fig 4: timeline
fig,ax=plt.subplots(3,1,figsize=(11,7.5),dpi=130,sharex=True,gridspec_kw=dict(height_ratios=[1,1.3,1.3]))
ax[0].fill_between(d.t,d.cloud_pct,color="#95a5a6",step="mid"); ax[0].set_ylabel("Cloud flag\n(% of area)"); ax[0].set_ylim(0,105)
ax[1].plot(d.t,d.c07_max_c,color="#d35400",lw=1.6); ax[1].set_ylabel("Hottest 3.9 µm\nreading (°C)")
ax[2].bar(d.t,d.fdc_power_mw,width=0.006,color="#c0392b"); ax[2].set_ylabel("Fire power\ndetected (MW)")
for t,lab in [(pd.Timestamp("2026-10-17 15:10"),"3:10 p.m.\n76.5 MW"),(pd.Timestamp("2026-10-17 15:30"),"3:30 p.m.\n1,215 MW"),(pd.Timestamp("2026-10-17 15:40"),"3:40\n336 MW")]:
    v=float(d[d.t==t].fdc_power_mw.iloc[0]); ax[2].annotate(lab,(t,v),xytext=(8,-6 if v>500 else 6),textcoords="offset points",fontsize=8.5)
for a in ax:
    a.axvspan(pd.Timestamp("2026-10-17 15:24"),pd.Timestamp("2026-10-17 15:26"),color="#8e44ad",alpha=0.35)
    a.axvline(pd.Timestamp("2026-10-17 15:16"),color="k",lw=0.8,ls="--")
    a.axvspan(pd.Timestamp("2026-10-17 19:30"),pd.Timestamp("2026-10-18 09:00"),color="#2980b9",alpha=0.07)
ax[0].text(pd.Timestamp("2026-10-17 15:20"),92,"3:16 front",fontsize=8,ha="right")
ax[1].text(pd.Timestamp("2026-10-17 15:30"),48,"model: fire reaches\nthe lines 3:24-3:26",fontsize=8,color="#6c3483")
ax[1].text(pd.Timestamp("2026-10-17 23:00"),40,"Clear night: no hot spot,\nno fire pixels",fontsize=9,color="#1f618d",weight="bold")
ax[2].xaxis.set_major_formatter(mdates.DateFormatter("%a %H:%M")); ax[2].xaxis.set_major_locator(mdates.HourLocator(interval=3))
fig.suptitle("4. What GOES-18 saw over the fire, 6 a.m. Oct. 17 to noon Oct. 18 (MDT, every 10 minutes)",x=0.01,ha="left",fontsize=12,weight="bold")
fig.text(0.01,0.01,"NOAA GOES-18 ABI full disk: cloud mask (ACM), band 7 brightness temperature, Fire Detection and Characterization (FDC).",fontsize=7.5,color="#444")
plt.tight_layout(rect=(0,0.03,1,0.96)); plt.savefig("fig4_goes_timeline.png"); plt.close()
# --- Fig 5: GOES pixels at 3:10, 3:30, 3:40 with gas lines
px=pd.read_csv(R+"location_analysis/goes_fire_pixels.csv")
scar=unary_union([shape(x['geometry']) for x in json.load(open(R+"infrastructure/scar_patches_revised.geojson"))['features']])
aer=json.load(open(R+"reference/aer_pipelines_near_site.geojson"))['features']
K=1/np.cos(np.radians(52.77)); W,E,S,N=-110.97,-110.82,52.72,52.83
fig,axs=plt.subplots(1,3,figsize=(13,5.2),dpi=130)
for ax,t in zip(axs,["15:10","15:30","15:40"]):
    for g in getattr(scar,'geoms',[scar]): xs,ys=g.exterior.xy; ax.fill(xs,ys,color="#e67e22",alpha=0.3,lw=0)
    for f in aer:
        p=f['properties']
        if p['SEG_STATUS']=='Operating' and 'Gas' in str(p['SUBSTANCE1']):
            g=shape(f['geometry'])
            for gg in getattr(g,'geoms',[g]): xs,ys=gg.xy; ax.plot(xs,ys,color="#c0392b",lw=1.1)
    sub=px[px.mdt==t]
    for _,r in sub.iterrows():
        xy=[tuple(map(float,c.split(","))) for c in r.corners.split(";")]
        poly=Polygon(xy); xs,ys=poly.exterior.xy; ax.fill(xs,ys,color="#f1c40f",alpha=0.35,lw=1.5,ec="#7d6608")
        c=poly.centroid; ax.text(c.x,c.y,f"{r.power_mw:.0f} MW",ha="center",fontsize=9,weight="bold")
    ax.scatter([-110.90429],[52.77186],marker="s",s=60,facecolors="none",edgecolors="k",lw=2,zorder=5)
    ax.scatter([-110.9063,-110.89965],[52.7728,52.77045],s=20,c="k",zorder=5)
    ax.set_xlim(W,E); ax.set_ylim(S,N); ax.set_aspect(K); ax.set_xticks([]); ax.set_yticks([]); ax.set_title(f"{t[:2].lstrip('0') if False else int(t[:2])-12}:{t[3:]} p.m.",fontsize=11)
axs[0].annotate("end of line 58333-78",(-110.90429,52.77186),xytext=(-60,-30),textcoords="offset points",fontsize=8.5,arrowprops=dict(arrowstyle="-"))
fig.suptitle("5. GOES-18 fire pixels (2 km) vs the gas lines: heat spread along the fire front, not centred on the lines",x=0.01,ha="left",fontsize=12,weight="bold")
fig.text(0.01,0.02,"Yellow: GOES-18 fire pixels with fire radiative power. Red: operating gas lines (AER). Square: mapped west end of line 58333-78. Dots: Range 2 point, road head. Orange: final burn.",fontsize=7.5,color="#444")
plt.tight_layout(rect=(0,0.05,1,0.93)); plt.savefig("fig5_goes_pixels.png"); plt.close()
# --- Fig 6: expected rupture signature vs observed (schematic, order of magnitude)
t=np.arange(0,270.1,1)  # minutes after 15:00
def rupture(t0, peak, tau_min, tail):
    y=np.zeros_like(t,dtype=float); m=t>=t0; y[m]=peak*np.exp(-(t[m]-t0)/tau_min)+tail; return y
fig,ax=plt.subplots(figsize=(11,5),dpi=130)
lo=rupture(25,400,1.5,10); hi=rupture(25,2000,2.5,60)
ax.fill_between(t,lo,hi,color="#8e44ad",alpha=0.25,label="Expected: 4.5-in gas line rupture at ~3:25 p.m.\n(blowdown spike, then jet fire fed by wells until shut in)")
obs=d[(d.t>="2026-10-17 15:00")&(d.t<="2026-10-17 19:00")]
ax.scatter((obs.t-pd.Timestamp("2026-10-17 15:00")).dt.total_seconds()/60,obs.fdc_power_mw,color="#c0392b",zorder=5,label="Observed (GOES-18, every 10 min)")
ax.set_yscale("symlog",linthresh=10); ax.set_ylim(0,3000)
ax.set_xticks(range(0,271,30)); ax.set_xticklabels([f"{3+m//60}:{m%60:02d}" for m in range(0,271,30)]); ax.set_xlabel("p.m., Oct. 17 (MDT)"); ax.set_ylabel("Fire radiative power (MW, log scale)")
ax.axvline(16,color="k",lw=0.8,ls="--"); ax.text(17,1500,"3:16 front",fontsize=8.5)
ax.axvspan(50,270,ymin=0,ymax=1,color="#95a5a6",alpha=0.15); ax.text(95,30,"No detections after 3:40 p.m., but thick cloud\nuntil ~7:30 p.m. limits this window.\nFrom ~7:30 p.m. skies were clear all night:\nno hot spot. A well-fed jet fire still\nburning then would have shown.",fontsize=9)
ax.legend(loc="upper right",fontsize=8.5)
ax.set_title("6. Expected signature of a gas-line rupture vs what GOES saw (order-of-magnitude estimate)",loc="left",fontsize=12,weight="bold")
fig.text(0.01,0.01,"Estimate assumes a full-bore rupture of a 114 mm line at 4,140 kPa: initial release 40-130 kg/s, 15-30% radiated, most inventory gone in minutes. Not a site-specific engineering model.",fontsize=7.5,color="#444")
plt.tight_layout(rect=(0,0.03,1,1)); plt.savefig("fig6_rupture_vs_observed.png"); plt.close()
print("ok")
