import sys; sys.path.insert(0, "vis")
from pr import *
from pr import _LOGO
def make(W, H, out, pad_title=62):
    im = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(im)
    ph = Image.open("vis/_landsat_clean_crop.png").convert("RGBA")
    crop = ph.resize((int(H * ph.size[0] / ph.size[1]), H))
    im.paste(crop, (W - crop.size[0], 0))
    grad = Image.new("L", (W, H), 0); gd = ImageDraw.Draw(grad)
    for x in range(W): gd.line([(x, 0), (x, H)], fill=int(255 * max(0, min(1, (W * 0.78 - x) / (W * 0.3)))))
    im.paste(Image.new("RGBA", (W, H), BG + (255,)), (0, 0), grad)
    d = ImageDraw.Draw(im); d.rectangle([0, 0, 12, H], fill=GOLD)
    d.text((54, 44), "CFB WAINWRIGHT FIRE · LANDSAT 8 · 12:17 P.M., OCT. 17", font=B(20), fill=GOLD)
    y = 84
    for l in ["The noon", "photograph"]: d.text((54, y), l, font=D(pad_title), fill=CREAM); y += pad_title + 8
    for k, t in enumerate(["Start: grenade launcher range's impact area", "Gas lines cold at noon; no sign of a gas fire", "C Company findings essentially unchanged"]):
        d.text((54, y + 30 + k * 40), "• " + t, font=M(24), fill=CREAM)
    d.rectangle([0, H - 96, W, H], fill=NAVY); d.rectangle([0, H - 96, W, H - 91], fill=GOLD)
    d.text((54, H - 70), "Working model v3 · primerogueinc.com", font=M(19), fill=CREAM)
    d.text((54, H - 22), "PRIME ROGUE", font=K(19), fill=GOLD, anchor="lb"); im.paste(_LOGO, (W - 84 - 36, H - 96 + 8))
    im.convert("RGB").save(out, quality=92)
make(1200, 630, "v3kit/images/cfb-wainwright-noon-photograph-og.jpg")
make(1280, 720, "v3kit/images/cfb-wainwright-noon-photograph-thumbnail.jpg", pad_title=80)
