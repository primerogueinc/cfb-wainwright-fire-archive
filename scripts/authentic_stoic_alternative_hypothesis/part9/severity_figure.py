import os
import json, numpy as np, rasterio
from shapely.geometry import shape
from pyproj import Transformer
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.colors import ListedColormap, BoundaryNorm
R=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../data/")
dn=rasterio.open(R+"copernicus/severity_matched_10m/dnbr_10m_oct04_oct19.tif"); D=dn.read(1).astype(float)
tf=Transformer.from_crs(4326,dn.crs,always_xy=True).transform
W,S,E,N=-110.9135,52.7655,-110.8925,52.7775
x0,y0=tf(W,S); x1,y1=tf(E,N)
i0,j0=dn.index(x0,y1); i1,j1=dn.index(x1,y0)
sub=D[i0:i1,j0:j1]; ext=list(dn.transform*(j0,i0))[:1]+list(dn.transform*(j1,i1))[:1]+[ (dn.transform*(j0,i1))[1], (dn.transform*(j0,i0))[1]]
cmap=ListedColormap(['#f2f2f2','#fde4a8','#f6a04d','#d6452f','#7a1020']); norm=BoundaryNorm([-1,0.10,0.20,0.27,0.44,2],cmap.N)
fig,ax=plt.subplots(figsize=(10,7.6))
im=ax.imshow(sub,extent=ext,cmap=cmap,norm=norm,interpolation='nearest')
for f in json.load(open(R+"reference/aer_pipelines_near_site.geojson"))['features']:
    p=f['properties']; g=shape(f['geometry'])
    for gg in getattr(g,'geoms',[g]):
        xs,ys=zip(*[tf(*c) for c in gg.coords])
        op=p['SEG_STATUS']=='Operating' and p['SUBSTANCE1']=='Natural Gas'
        ax.plot(xs,ys,color='#1f4e9c' if op else '#888',lw=2.4 if op else 1.2,ls='-' if op else '--',zorder=5)
P={"Well 1-11 (AER registered surface location)":(-110.898943,52.773642,(-110,30)),"Mapped west end of line 58333-78":(-110.90429,52.77186,(-150,-30)),"A: Range 2 point":(-110.90632,52.77279,(-125,18)),"B: road head":(-110.89965,52.77045,(12,-22))}
for k,(lo,la,off) in P.items():
    x,y=tf(lo,la); ax.scatter([x],[y],s=55,c='k',zorder=7)
    ax.annotate(k,(x,y),xytext=off,textcoords='offset points',fontsize=9,weight='bold',zorder=8,bbox=dict(boxstyle='round,pad=0.2',fc='white',ec='none',alpha=0.85))
x,y=tf(-110.898943,52.773642)
for r in (50,100): ax.add_patch(plt.Circle((x,y),r,fill=False,ls=':',lw=1.2,color='k',zorder=6))
ax.set_xlim(ext[0],ext[1]); ax.set_ylim(ext[2],ext[3]); ax.set_xticks([]); ax.set_yticks([])
ax.plot([ext[1]-450,ext[1]-150],[ext[2]+60]*2,'k',lw=3); ax.text(ext[1]-300,ext[2]+80,'300 m',ha='center',fontsize=9)
cb=plt.colorbar(im,ax=ax,shrink=0.75,ticks=[-0.45,0.15,0.235,0.355,1.2]); cb.ax.set_yticklabels(['unburned','low','moderate-low','moderate','high']); cb.set_label('Burn severity (dNBR, Sentinel-2, Oct. 4 vs Oct. 19)')
ax.legend(handles=[Line2D([],[],color='#1f4e9c',lw=2.4,label='Gas line, operating (AER)'),Line2D([],[],color='#888',lw=1.2,ls='--',label='Other / abandoned line'),Line2D([],[],color='k',ls=':',label='50 m and 100 m from the well')],loc='lower left',fontsize=8.5,framealpha=0.92)
ax.set_title("7. Burn severity at the gas lines: the well's registered site did not burn; no blast-shaped spot on the lines",fontsize=12,weight='bold',loc='left')
fig.text(0.01,0.01,"Burn severity: dNBR from Sentinel-2 L2A, 20 m bands resampled to 10 m, seasonal offset removed (contains modified Copernicus Sentinel data [2026]).\nPipelines: Alberta Energy Regulator; positions mapped, not surveyed.",fontsize=7,color='#444')
plt.tight_layout(rect=(0,0.045,1,1)); plt.savefig("fig7_severity_at_lines.png",dpi=130); plt.close()
