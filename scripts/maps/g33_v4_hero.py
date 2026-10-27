"""v4 header image (1600x900), social card (1200x630) and video thumbnail (1280x720). Usage: python3 scripts/maps/g33_v4_hero.py "TITLE LINE 1|TITLE LINE 2" """
import sys; sys.path.insert(0, "scripts/maps")
from pr import *
from pr import _LOGO
lines = (sys.argv[1] if len(sys.argv) > 1 else "Monitored for hours,|beyond control in minutes").split("|")
ph = Image.open(REPO + "data/authentic-stoic-stress-test/model_v3/severity_oct24/raw_views/sentinel2-20261024-true-colour-zoomed-out.png").convert("RGBA")
OUT = REPO + "data/graphics_published/oct25_model_v4/"
def make(W, H, out, ts, ss, foot=True):
    im = Image.new("RGBA", (W, H), BG + (255,))
    crop = ph.resize((int(H * 1.05 * ph.size[0] / ph.size[1]), int(H * 1.05))); im.paste(crop, (W - crop.size[0] + int(W * 0.12), -int(H * 0.02)))
    grad = Image.new("L", (W, H), 0); gd = ImageDraw.Draw(grad)
    for x in range(W): gd.line([(x, 0), (x, H)], fill=int(255 * max(0, min(1, (W * 0.70 - x) / (W * 0.28)))))
    im.paste(Image.new("RGBA", (W, H), BG + (255,)), (0, 0), grad)
    d = ImageDraw.Draw(im); d.rectangle([0, 0, 14, H], fill=GOLD)
    d.text((58, int(H * 0.08)), "CFB WAINWRIGHT FIRE · OCT. 17, 2026", font=B(int(ts * 0.36)), fill=GOLD)
    y = int(H * 0.08) + int(ts * 0.75)
    for l in lines: d.text((54, y), l, font=D(ts), fill=CREAM); y += int(ts * 1.08)
    y += int(ss * 0.8)
    for t in ("Satellites: the fire crept all day at a sixth of its potential,", "then ran at full speed minutes after the 3:16 p.m. wind shift"):
        d.text((58, y), t, font=M(ss), fill=CREAM); y += int(ss * 1.4)
    bx, by = 58, H - int(H * 0.16); bw = d.textlength("WORKING MODEL v4", font=K(int(ss * 1.05))) + 40
    d.rounded_rectangle([bx, by, bx + bw, by + int(ss * 2.1)], radius=10, fill=YEL); d.text((bx + 20, by + int(ss * 1.05)), "WORKING MODEL v4", font=K(int(ss * 1.05)), fill=INK, anchor="lm")
    d.text((W - 40, H - 34), "Sentinel-2, Oct. 24 · Prime Rogue", font=B(int(ss * 0.8)), fill=CREAM, anchor="rs")
    im.paste(_LOGO, (W - 84 - 40, 40))
    im.convert("RGB").save(OUT + out, quality=92)
make(1600, 900, "cfb-wainwright-v4-header.jpg", 92, 28)
make(1200, 630, "cfb-wainwright-v4-og.jpg", 66, 22)
make(1280, 720, "cfb-wainwright-v4-thumbnail.jpg", 80, 26)
print("ok")
