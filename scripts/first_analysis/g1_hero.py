import sys,textwrap; sys.path.insert(0,'.')
from style import *
from matplotlib.patches import FancyBboxPatch
W,H=1600,1340
fig=frame(W,H,"CFB WAINWRIGHT FIRE  ·  OCT. 17, 2026  ·  ALL TIMES MOUNTAIN","What they said vs. what the records show",
          "National Defence's written account, set against Government of Canada, NASA and NOAA records.")
rows=[
 ('"A fire ignited within the training area … at approximately 4:00 p.m."',"National Defence news release",
  ["Fire detected at the site at 12:17 p.m. (NASA Landsat 8) and 2:49 p.m. (NOAA-20).",
   "Likely fire at the site from 3:10 p.m., growing through about 3:40 p.m. (NOAA GOES-18).",
   "Maj.-Gen. Wade Rutland, Oct. 18: range control knew of a fire for several hours and was monitoring it."],
  "NASA FIRMS; NOAA GOES-18 (Prime Rogue analysis); Oct. 18 military briefing"),
 ('"Fire index was low"',"Internal CAF memo, as reported by Global News",
  ["Fire Weather Index 30.8 at the CFB Wainwright station: Extreme on Alberta's scale (29.5 and up).",
   "Up from 16.3 (High) the day before. Five nearby stations were also Extreme.",
   "Humidity 16–17% at 2 and 3 p.m. No rain since Oct. 12."],
  "Natural Resources Canada CWFIS; Environment and Climate Change Canada"),
 ('"Unexpected and sudden wind change"',"Internal CAF memo, as reported by Global News",
  ["5 a.m. forecast: wind becoming \"west 50 gusting to 80 this afternoon\", risk of a thunderstorm.",
   "2:14 p.m. wind warning: a line of showers and weak thunderstorms \"is moving east. Strong wind gusts can be expected.\"",
   "3:16 p.m.: 82 km/h gust from the west at the base's weather station. By 4 p.m., wind from the NW and 10 °C colder."],
  "Environment and Climate Change Canada forecasts, warnings and CFB Wainwright station"),
]
top=1-215/H; rh=310/H; gap=22/H; LX,LW,RX,RW=0.03,0.33,0.38,0.59
fig.text(LX,top+8/H,"WHAT THEY SAID",color=RED,fontsize=14,fontweight="black")
fig.text(RX,top+8/H,"WHAT THE RECORDS SHOW",color=GREEN,fontsize=14,fontweight="black")
for i,(q,qs,recs,rs) in enumerate(rows):
    y1=top-14/H-i*(rh+gap); y0=y1-rh
    fig.patches.append(FancyBboxPatch((LX,y0),LW,rh,boxstyle="round,pad=0,rounding_size=0.006",transform=fig.transFigure,facecolor=PANEL,edgecolor=RED,lw=1.5))
    fig.patches.append(FancyBboxPatch((RX,y0),RW,rh,boxstyle="round,pad=0,rounding_size=0.006",transform=fig.transFigure,facecolor=PANEL,edgecolor=GREEN,lw=1.5))
    fig.text(LX+0.015,y1-28/H,"\n".join(textwrap.wrap(q,30)),color=CREAM,fontsize=21,fontweight="bold",va="top",linespacing=1.3)
    fig.text(LX+0.015,y0+22/H,"— "+qs,color=MUTED,fontsize=12,va="bottom")
    yy=y1-28/H
    for r in recs:
        lines=textwrap.wrap(r,72); fig.text(RX+0.015,yy,"•",color=GREEN,fontsize=15,va="top",fontweight="bold")
        fig.text(RX+0.03,yy,"\n".join(lines),color=CREAM,fontsize=15,va="top",linespacing=1.35); yy-=(len(lines)*27+20)/H
    fig.text(RX+0.015,y0+22/H,"Source: "+rs,color=MUTED,fontsize=12,va="bottom")
footer(fig,H,["Satellite times are Prime Rogue analysis of NASA FIRMS and NOAA GOES-18 data. Memo quotes as reported by Global News; the memo has not been published.",
              "Fire Weather Index from NRCan's Canadian Wildland Fire Information System (station value, noon). Contains information licensed under the Open Government Licence – Canada."])
save(fig,'g1.png','/home/claude/cfb-wainwright-said-vs-records.jpg',W,H)
