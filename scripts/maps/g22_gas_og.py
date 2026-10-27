import sys; sys.path.insert(0, "vis")
from pr import *
W, H = 1200, 630
im = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(im)
d.rectangle([0, 0, 12, H], fill=GOLD)
d.text((54, 44), "CFB WAINWRIGHT FIRE · WORKING MODEL V2.1", font=B(20), fill=GOLD)
d.text((54, 80), "Another sign pointing", font=D(62), fill=CREAM); d.text((54, 150), "away from gas", font=D(62), fill=CREAM)
stats = [("0", "gas lines or wells in the grenade\nlauncher range's firing sector"), ("~1.4 km", "from the fire's start to\nthe nearest gas line"), ("0", "hot spots overnight; no\nmethane leak next day")]
for k, (n, t) in enumerate(stats):
    x = 54 + k * 370; d.text((x, 262), n, font=D(64), fill=TEAL)
    for i, l in enumerate(t.split("\n")): d.text((x, 350 + i * 28), l, font=M(21), fill=CREAM)
d.text((54, 440), "Not ruled out: a brief release as the fire crossed the lines.", font=B(23), fill=GOLD)
d.rectangle([0, H - 96, W, H], fill=NAVY); d.rectangle([0, H - 96, W, H - 91], fill=GOLD)
d.text((54, H - 70), "Satellite and regulatory test · primerogueinc.com", font=M(19), fill=CREAM)
d.text((54, H - 22), "PRIME ROGUE", font=K(19), fill=GOLD, anchor="lb")
from pr import _LOGO
im.paste(_LOGO, (W - 84 - 36, H - 96 + 8))
im.convert("RGB").save("vis/cfb-wainwright-gas-og.jpg", quality=92)
