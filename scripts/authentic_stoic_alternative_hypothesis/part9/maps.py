import os
import json, glob, numpy as np, pandas as pd, rasterio
from shapely.geometry import shape
from shapely.ops import unary_union
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_bounds
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
R=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../data/"); DR=os.environ.get("COPERNICUS_REPO", "../cfb-wainwright---full-satellite-data---copernicus-").rstrip("/")+"/"  # clone of the Copernicus data repo
scar=unary_union([shape(x['geometry']) for x in json.load(open(R+"infrastructure/scar_patches_revised.geojson"))['features']])
aer=json.load(open(R+"reference/aer_pipelines_near_site.geojson"))['features']
osm=json.load(open(R+"infrastructure/osm_infrastructure_ODbL.geojson"))['features']
d=pd.read_csv(R+"firms/detections.csv"); L=d[d.acq_datetime_mdt=="2026-10-17 12:17 MDT"]; V=d[d.acq_datetime_mdt=="2026-10-17 14:49 MDT"]
P={"Airfield 21":(-111.0956,52.8294),"Range 11 (AGL)":(-110.9577,52.7678),"Range 2":(-110.9063,52.7728),"Road head":(-110.89965,52.77045)}
K=1/np.cos(np.radians(52.78))
def lines(ax, lw=1.0, label_sel=False):
    for f in aer:
        p=f['properties']; g=shape(f['geometry']); op=p.get('SEG_STATUS')=='Operating'; gas='Gas' in str(p.get('SUBSTANCE1'))
        col='#c0392b' if (op and gas) else ('#7f8c8d' if not op else '#2471a3')
        for gg in getattr(g,'geoms',[g]):
            xs,ys=gg.xy; ax.plot(xs,ys,color=col,lw=lw*(1.6 if op else 1.0),zorder=3,ls='-' if op else (0,(3,2)))
def burn(ax, a=0.45):
    for g in getattr(scar,'geoms',[scar]):
        xs,ys=g.exterior.xy; ax.fill(xs,ys,color='#e67e22',alpha=a,lw=0,zorder=1)
def pts(ax, offs, s=50):
    for k,(x,y) in P.items():
        if k in offs: ax.scatter([x],[y],s=s,c='k',zorder=6); ax.annotate(k,(x,y),xytext=offs[k],textcoords='offset points',fontsize=9.5,weight='bold',zorder=7,bbox=dict(boxstyle='round,pad=0.2',fc='white',ec='none',alpha=0.8))
def scale(ax,x0,y0,km):
    ax.plot([x0,x0+km/(111.32/K)],[y0,y0],'k',lw=3,zorder=8); ax.text(x0+km/(111.32/K)/2,y0+0.0012*km/1,f'{km:g} km',ha='center',fontsize=9,zorder=8)
LEG=[Line2D([],[],color='#c0392b',lw=1.8,label='Gas line, operating (AER)'),Line2D([],[],color='#2471a3',lw=1.8,label='Other substance, operating (AER)'),
     Line2D([],[],color='#7f8c8d',lw=1.2,ls=(0,(3,2)),label='Abandoned / discontinued (AER)'),plt.Rectangle((0,0),1,1,fc='#e67e22',alpha=0.45,label='Burned, Oct. 17')]
FOOT="Pipelines: Alberta Energy Regulator licensed pipeline dataset (mapped positions; accuracy tens of metres). Burn: Copernicus Sentinel-2. Fire detections: NASA FIRMS. Ranges: OpenStreetMap."
# ---- Map 1: overview
fig,ax=plt.subplots(figsize=(11,8.5),dpi=130); burn(ax); lines(ax,0.7)
for f in osm:
    p=f['properties']
    if p.get('kind')=='pipeline' and p.get('name'):
        g=shape(f['geometry'])
        for gg in getattr(g,'geoms',[g]): xs,ys=gg.xy; ax.plot(xs,ys,color='k',lw=2.6,alpha=0.6,zorder=2)
        c=g.interpolate(0.5,normalized=True)
        if -111.25<c.x<-110.6 and 52.62<c.y<52.95: ax.annotate(p['name'],(c.x,c.y),fontsize=8,style='italic',zorder=7)
pts(ax,{"Airfield 21":(6,6),"Range 11 (AGL)":(-80,-16),"Range 2":(-30,10),"Road head":(8,-14)})
ax.set_xlim(-111.25,-110.62); ax.set_ylim(52.64,52.94); ax.set_aspect(K); ax.set_xticks([]); ax.set_yticks([])
ax.legend(handles=LEG+[Line2D([],[],color='k',lw=2.6,alpha=0.6,label='Named transmission line (OpenStreetMap)')],loc='lower left',fontsize=8.5,framealpha=0.9)
scale(ax,-110.72,52.65,5); ax.set_title("1. Licensed pipelines around the burn: small gathering lines; no transmission line near",fontsize=12,weight='bold',loc='left')
fig.text(0.01,0.01,FOOT,fontsize=7,color='#444'); plt.tight_layout(rect=(0,0.03,1,1)); plt.savefig("map1_overview.png"); plt.close()
# ---- Map 2: close-up on Range 2 / road head over Sentinel-2 10 m true colour (Oct. 19)
W,E,S,N=-110.918,-110.884,52.763,52.783
f19=glob.glob(DR+"sentinel-2/2026-10-19/L2A_tiff/*True_color.tiff")[0]; s=rasterio.open(f19)
h,w=700,int(700*(E-W)/(N-S)/K); img=np.zeros((3,h,w),'float32')
for b in range(3): reproject(s.read(b+1).astype('float32'),img[b],src_transform=s.transform,src_crs=s.crs,dst_transform=from_bounds(W,S,E,N,w,h),dst_crs='EPSG:4326',resampling=Resampling.bilinear)
img=np.moveaxis(img,0,-1); img=np.clip(img/np.percentile(img,99.5),0,1)
fig,ax=plt.subplots(figsize=(11,8),dpi=130); ax.imshow(img,extent=(W,E,S,N))
for g in getattr(scar,'geoms',[scar]): xs,ys=g.exterior.xy; ax.plot(xs,ys,color='#ff7f0e',lw=1.5,zorder=2)
lines(ax,1.6)
for f in aer:
    p=f['properties']; g=shape(f['geometry'])
    if g.intersects(shape({'type':'Polygon','coordinates':[[(W,S),(E,S),(E,N),(W,N),(W,S)]]})) and p.get('SEG_STATUS')=='Operating':
        c=g.interpolate(0.35,normalized=True) if g.length>0.01 else g.interpolate(0.5,normalized=True)
        off={'58333-125':(8,-40),'58333-78':(-20,10)}.get(p['LIC_LI_NO'],(6,6))
        if W<c.x<E and S<c.y<N: ax.annotate(f"{p['LIC_LI_NO']}\n{float(p['OUT_DIAMET'])/25.4:.1f}-in gas, {int(float(p['PIPE_MAOP']))} kPa",(c.x,c.y),xytext=off,textcoords='offset points',fontsize=8,color='white',weight='bold',zorder=7,bbox=dict(boxstyle='round,pad=0.2',fc='#c0392b',ec='none',alpha=0.85))
for x,y in [(-110.90429,52.77186)]:
    ax.scatter([x],[y],marker='s',s=70,facecolors='none',edgecolors='yellow',lw=2,zorder=6); ax.annotate("Mapped west end of line 58333-78",(x,y),xytext=(-150,-30),textcoords='offset points',fontsize=8.5,color='yellow',weight='bold',arrowprops=dict(arrowstyle='-',color='yellow'))
ax.scatter([-110.898943],[52.773642],marker='D',s=60,facecolors='none',edgecolors='#1f4e9c',lw=2,zorder=6); ax.annotate("Well 1-11 (AER registered location)",(-110.898943,52.773642),xytext=(10,12),textcoords='offset points',fontsize=8.5,color='white',weight='bold',bbox=dict(boxstyle='round,pad=0.2',fc='#1f4e9c',ec='none',alpha=0.9))
ax.scatter(L.longitude,L.latitude,s=10,c='#ff2a00',zorder=5)
pts(ax,{"Range 2":(-60,12),"Road head":(10,-16)},s=60)
ax.set_xlim(W,E); ax.set_ylim(S,N); ax.set_aspect(K); ax.set_xticks([]); ax.set_yticks([])
ax.legend(handles=[Line2D([],[],color='#c0392b',lw=2.5,label='Gas line, operating (AER)'),Line2D([],[],color='#ff7f0e',lw=1.5,label='Burn edge'),Line2D([],[],marker='o',ls='',color='#ff2a00',ms=4,label='Fire at 12:17 p.m. (Landsat)')],loc='lower left',fontsize=8.5,framealpha=0.9)
scale(ax,E-0.012,S+0.0012,0.5); ax.set_title("2. Gas gathering lines cross the Range 2 / road head area",fontsize=12,weight='bold',loc='left')
fig.text(0.01,0.01,"Base image: Sentinel-2, Oct. 19, 10 m (contains modified Copernicus Sentinel data [2026]). "+FOOT.split('. Burn')[0]+".",fontsize=7,color='#444')
plt.tight_layout(rect=(0,0.03,1,1)); plt.savefig("map2_range2_closeup.png"); plt.close()
# ---- Map 3: where the fire started vs the lines, and when it reached them
arr=rasterio.open(R+"authentic-stoic-stress-test/part8b_ignition/arrival_C_2x_line_0715.tif")
W,E,S,N=-110.975,-110.865,52.748,52.795; h,w=700,int(700*(E-W)/(N-S)/K)
A=np.full((h,w),np.nan,'float32'); reproject(arr.read(1),A,src_transform=arr.transform,src_crs=arr.crs,dst_transform=from_bounds(W,S,E,N,w,h),dst_crs='EPSG:4326',resampling=Resampling.nearest)
fig,ax=plt.subplots(figsize=(11,7.5),dpi=130); burn(ax,0.25)
im=ax.imshow(np.ma.masked_invalid(A),extent=(W,E,S,N),cmap='YlOrRd',vmin=7,vmax=15.3,alpha=0.85,zorder=2)
lines(ax,1.5); ax.scatter(L.longitude,L.latitude,s=8,c='k',zorder=5,label='Fire at 12:17 p.m. (Landsat)')
from pyproj import Geod; G=Geod(ellps='WGS84'); R11=P["Range 11 (AGL)"]
xs,ys=zip(*[G.fwd(*R11,80,dd)[:2] for dd in (1400,2200)]); ax.plot(xs,ys,color='#17a589',lw=5,zorder=6,label='Modelled start (AGL rounds, 1.4-2.2 km out)')
pts(ax,{"Range 11 (AGL)":(-40,-18),"Range 2":(-50,14),"Road head":(10,-16)})
ax.annotate("Nearest operating gas line to the start: ~1.4 km\nto the fire at 12:17 p.m.: ~0.9 km",(-110.935,52.758),fontsize=9,weight='bold',zorder=8,bbox=dict(boxstyle='round,pad=0.3',fc='white',ec='none',alpha=0.9))
ax.annotate("Fire reaches the lines here\nabout 3:24-3:26 p.m., after the wind shift",(-110.8999,52.7719),xytext=(25,-60),textcoords='offset points',fontsize=9,weight='bold',zorder=8,arrowprops=dict(arrowstyle='->',color='k'),bbox=dict(boxstyle='round,pad=0.3',fc='white',ec='none',alpha=0.9))
cb=plt.colorbar(im,ax=ax,fraction=0.025,pad=0.01); cb.set_label('Modelled time fire arrived, before 3:16 p.m. (hour, MDT)')
ax.set_xlim(W,E); ax.set_ylim(S,N); ax.set_aspect(K); ax.set_xticks([]); ax.set_yticks([])
ax.legend(loc='lower left',fontsize=8.5,framealpha=0.9); scale(ax,E-0.03,S+0.002,1)
ax.set_title("3. The fire started ~1.4 km from the nearest gas line and reached the lines after the wind shift",fontsize=12,weight='bold',loc='left')
fig.text(0.01,0.01,"Modelled progression: working model, start ~7:15 a.m. (central case). Pipelines: Alberta Energy Regulator. Burn: Sentinel-2. Detections: NASA FIRMS.",fontsize=7,color='#444')
plt.tight_layout(rect=(0,0.03,1,1)); plt.savefig("map3_start_vs_lines.png"); plt.close()
print("ok")
