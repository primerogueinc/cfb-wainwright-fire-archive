"""Label the orbit frames and encode the test video.

Run: python3 assemble_orbit.py RENDERDIR OUT.mp4
"""
import sys, os, json, glob, subprocess
from PIL import Image, ImageDraw, ImageFont

Rd, out = sys.argv[1], sys.argv[2]
F = '/usr/share/fonts/opentype/inter/'
fb = lambda s: ImageFont.truetype(F + 'Inter-Bold.otf', s)
fr = lambda s: ImageFont.truetype(F + 'Inter-Regular.otf', s)
meta = {}
for m in glob.glob(os.path.join(Rd, 'orbit_meta_*.json')):
    meta.update(json.load(open(m))['frames'])
frames = sorted(glob.glob(os.path.join(Rd, 'orbit_[0-9]*.png')))
lab = os.path.join(Rd, 'lab'); os.makedirs(lab, exist_ok=True)
INK = (14, 16, 20)
for f in frames:
    n = int(os.path.basename(f)[6:10])
    im = Image.open(f).convert('RGB'); W, H = im.size; d = ImageDraw.Draw(im)
    for k, (x, y, z) in meta.get(str(n), {}).items():
        if k.startswith('Fire line'):
            continue
        # dot at the ground point; Range 2 and the roadhead are ~500 m apart, so split their labels
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(255, 255, 255), outline=INK, width=2)
        if k == 'Range 2':
            d.text((x - 10, y - 8), k, font=fb(22), fill=(255, 255, 255), stroke_width=3, stroke_fill=INK, anchor='rb')
        else:
            d.text((x + 10, y + 4), k, font=fb(22), fill=(255, 255, 255), stroke_width=3, stroke_fill=INK, anchor='lt')
    band = Image.new('RGBA', (W, 64), (*INK, 200)); im.paste(band, (0, H - 64), band)
    d = ImageDraw.Draw(im)
    d.text((24, H - 56), 'CFB Wainwright, Oct. 17, 2026: the burn scar (red line) and the fire Landsat recorded at 12:17 p.m. (orange)',
           font=fb(19), fill=(255, 255, 255))
    d.text((24, H - 28), 'Height exaggerated 3x. Lighting as at 3:16 p.m. Terrain NRCan MRDEM-30 · imagery Copernicus Sentinel-2 (Oct 4) · '
           'scar Sentinel-2 dNBR · Prime Rogue Inc., working model v4', font=fr(15), fill=(200, 205, 212))
    im.save(os.path.join(lab, f'{n:04d}.png'))
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '24', '-i', os.path.join(lab, '%04d.png'),
                '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out],
               check=True)
print('wrote', out, len(frames), 'frames')
