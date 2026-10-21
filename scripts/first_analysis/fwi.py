import math
def hffmc(Fo,T,H,W,ro=0.0,t=1.0):
    # Van Wagner 1977 hourly FFMC
    mo=147.27723*(101-Fo)/(59.5+Fo)
    Ed=0.942*H**0.679+11*math.exp((H-100)/10)+0.18*(21.1-T)*(1-math.exp(-0.115*H))
    Ew=0.618*H**0.753+10*math.exp((H-100)/10)+0.18*(21.1-T)*(1-math.exp(-0.115*H))
    if mo>Ed:
        ko=0.424*(1-(H/100)**1.7)+0.0694*W**0.5*(1-(H/100)**8); kd=ko*0.0579*math.exp(0.0365*T)
        m=Ed+(mo-Ed)*math.exp(-2.303*kd*t)
    elif mo<Ew:
        k1=0.424*(1-((100-H)/100)**1.7)+0.0694*W**0.5*(1-((100-H)/100)**8); kw=k1*0.0579*math.exp(0.0365*T)
        m=Ew-(Ew-mo)*math.exp(-2.303*kw*t)
    else: m=mo
    return 59.5*(250-m)/(147.27723+m)
def isi(F,W):
    m=147.2*(101-F)/(59.5+F); fF=91.9*math.exp(-0.1386*m)*(1+m**5.31/4.93e7)
    return 0.208*math.exp(0.05039*W)*fF
def fwi(I,U):
    fD=0.626*U**0.809+2 if U<=80 else 1000/(25+108.64*math.exp(-0.023*U))
    B=0.1*I*fD
    return math.exp(2.72*(0.434*math.log(B))**0.647) if B>1 else B
BUI=77.6
print('check noon: ISI %.1f FWI %.1f (CWFIS 11.6/30.8)'%(isi(91.8,14.7),fwi(isi(91.8,14.7),BUI)))
F=91.8
for hr,T,H,W in [('1 p.m. MDT',20.2,23,15),('2 p.m. MDT',22.8,16,30),('3 p.m. MDT',23.3,17,32),('4 p.m. MDT (post-front)',12.9,43,48)]:
    if hr!='1 p.m. MDT': F=hffmc(F,T,H,W)
    I=isi(F,W); print(f'{hr}: T {T} RH {H} wind {W} km/h -> FFMC {F:.1f} ISI {I:.1f} FWI {fwi(I,BUI):.1f}')
for g in (50,60,69):
    I=isi(F,g); print(f'  4 p.m. with gust {g} km/h: ISI {I:.1f} FWI {fwi(I,BUI):.1f}')
