import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Rectangle, FancyBboxPatch
from PIL import Image
F="/usr/share/fonts/opentype/inter/"
for n in ["Inter-Medium.otf","Inter-SemiBold.otf","Inter-Bold.otf","Inter-Black.otf","InterDisplay-Black.otf"]: fm.fontManager.addfont(F+n)
plt.rcParams["font.family"]="Inter"
BG="#1C140F"; PANEL="#251A14"; GOLD="#D4AF68"; CREAM="#EEE6D6"; MUTED="#A99B84"; GRID="#352820"; NAVY="#1E3452"
RED="#E0603C"; BLUE="#4F8DD6"; YEL="#FFD600"; LAND="#B98424"; GREEN="#6FBF73"
LOGO="/mnt/user-data/uploads/logo_transparent_prime_rogue_inc_512_by_512_1.png"
def frame(w,h,kicker,title,sub=None):
    fig=plt.figure(figsize=(w/100,h/100),dpi=100,facecolor=BG)
    fig.patches.append(Rectangle((0,0),0.007,1,transform=fig.transFigure,facecolor=GOLD))
    fig.text(0.03,1-48/h,kicker,color=GOLD,fontsize=14,fontweight="bold",va="top")
    fig.text(0.03,1-78/h,title,color=CREAM,fontsize=30,fontweight="black",va="top")
    if sub: fig.text(0.03,1-128/h,sub,color=MUTED,fontsize=14,va="top")
    return fig
def footer(fig,h,lines,fh=110):
    fig.patches.append(Rectangle((0,0),1,fh/h,transform=fig.transFigure,facecolor=NAVY))
    fig.patches.append(Rectangle((0,fh/h),1,4/h,transform=fig.transFigure,facecolor=GOLD))
    for i,l in enumerate(lines): fig.text(0.03,(fh-30-i*24)/h,l,color=CREAM,fontsize=11.5,va="center")
    fig.text(0.03,14/h,"PRIME ROGUE",color=GOLD,fontsize=13,fontweight="black",va="bottom")
def save(fig,png,jpg,w,h,fh=110):
    fig.savefig(png,facecolor=BG,dpi=100); im=Image.open(png).convert("RGBA")
    lg=Image.open(LOGO).convert("RGBA").resize((84,84),Image.LANCZOS); im.alpha_composite(lg,(w-84-28,h-84-(fh-84)//2))
    im.convert("RGB").save(jpg,quality=90,optimize=True); print(jpg,im.size)
