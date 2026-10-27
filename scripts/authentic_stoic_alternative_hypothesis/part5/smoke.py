"""Rough ground-level smoke and visibility downwind of the head fire after the 3:16 p.m. shift.
Line source (fire front) in a uniform wind; Gaussian vertical spread with Briggs rural neutral (class D)
sigma_z; ground reflection. Two plume cases bracket the answer:
  low  - plume stays at the ground (H = 0), as expected when Byram's convection number Nc < 1 (wind-driven fire)
  lofted - Briggs bent-over line-plume rise, H = sqrt(3 F_L / (2 beta^2 u^3)) * x, beta = 0.6
Visibility = K / (MEE * C): MEE = 4.5 m2/g (fresh smoke); K = 3 for dark objects (Koschmieder), 8 for
light-emitting objects such as flames (Jin 1978)."""
import numpy as np, pandas as pd, json
u=48/3.6            # m/s
w=0.35              # kg/m2 fuel consumed (FBP O-1b grass fuel load)
EF=8.0              # g PM2.5 per kg fuel (grassland/savanna, Akagi et al. 2011 ~7.2; Andreae 2019 ~8)
MEE=4.5
rows=[]
for ros_kmh in (4.4,8.0,12.0):
    R=ros_kmh/3.6
    q=w*R*EF                      # g/m/s per metre of front
    I=18000*w*R                   # kW/m  (H = 18,000 kJ/kg)
    FL=9.81*I*1000/(1.2*1005*290) # m3/s3
    Nc=2*9.81*I*1000/(1.2*1005*290*(u-R)**3)
    for x in (100,200,300,500,750,1000,1500):
        sz=0.06*x*(1+0.0015*x)**-0.5
        for case in ("low","lofted"):
            H=0.0 if case=="low" else np.sqrt(3*FL/(2*0.36*u**3))*x
            C=2*q/(np.sqrt(2*np.pi)*sz*u)*np.exp(-H**2/(2*sz**2))   # g/m3 at ground
            sig=MEE*C
            rows.append(dict(ros_kmh=ros_kmh,intensity_kWm=round(I),Nc=round(Nc,2),x_m=x,case=case,pm_ugm3=round(C*1e6),
                             vis_dark_m=round(3/sig) if sig>1e-9 else None, vis_flames_m=round(8/sig) if sig>1e-9 else None,
                             smoke_travel_s=round(x/u)))
df=pd.DataFrame(rows); df.to_csv("smoke_visibility.csv",index=False)
pd.set_option("display.width",200)
print(df[df.case=="low"].pivot_table(index="x_m",columns="ros_kmh",values=["vis_dark_m","vis_flames_m"]).to_string())
print(df[["ros_kmh","intensity_kWm","Nc"]].drop_duplicates().to_string(index=False))
print(df[df.case=="lofted"].groupby("ros_kmh").vis_dark_m.min())
