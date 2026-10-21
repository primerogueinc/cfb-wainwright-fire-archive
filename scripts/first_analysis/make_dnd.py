from PIL import Image, ImageDraw, ImageFont
import sys, textwrap

LOGO = "/mnt/user-data/uploads/logo_transparent_prime_rogue_inc_512_by_512_1.png"
F = "/usr/share/fonts/opentype/inter/"
BROWN, BROWN_DK, PANEL, PANEL2 = (44, 32, 24), (28, 20, 15), (40, 29, 22), (34, 25, 19)
GOLD, CREAM, NAVY, MUTED = (212, 175, 104), (238, 230, 214), (30, 52, 82), (176, 162, 138)
GREEN, BLUE, AMBER, RED, GREY = (120, 170, 110), (79, 141, 214), (214, 150, 60), (200, 92, 70), (120, 108, 96)
LANDSAT = (185, 132, 36)
OUT = sys.argv[1]
def font(n, s): return ImageFont.truetype(F + n, int(s))
def wrap(d, text, f, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= width: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines
def footer(img, d, W, H, fh, lines, s=1.0, pad=60):
    fy = H - fh
    d.rectangle([0, fy, W, H], fill=NAVY); d.rectangle([0, fy, W, fy + 5], fill=GOLD)
    fc = font("Inter-Medium.otf", 21)
    y = fy + 24
    for ln in wrap(d, " ".join(lines), fc, W - 2 * pad - 140): d.text((pad, y), ln, font=fc, fill=CREAM); y += 32
    d.text((pad, H - 40), "PRIME ROGUE", font=font("Inter-Black.otf", 24), fill=GOLD, anchor="lm")
    logo = Image.open(LOGO).convert("RGBA").resize((96, 96), Image.LANCZOS)
    img.alpha_composite(logo, (W - 96 - pad, fy + 22))

# ---------------- HEADER ----------------
def header(W, H, out):
    s = W / 1600.0
    img = Image.new("RGBA", (W, H), BROWN_DK + (255,)); d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(BROWN[i] * (1 - t) + BROWN_DK[i] * t) for i in range(3)))
    d.rectangle([0, 0, int(14 * s), H], fill=GOLD)
    pad = int(90 * s)
    fb = font("Inter-Black.otf", 30 * s); lab = "PRIME ROGUE ANALYSIS"
    bw = d.textlength(lab, font=fb); bx, by, bh = pad, int(88 * s), int(56 * s)
    d.rounded_rectangle([bx, by, bx + bw + int(40 * s), by + bh], radius=int(8 * s), fill=GOLD)
    d.text((bx + int(20 * s), by + bh // 2), lab, font=fb, fill=BROWN_DK, anchor="lm")
    d.text((bx + bw + int(66 * s), by + bh // 2), "CFB WAINWRIGHT", font=font("Inter-Bold.otf", 28 * s), fill=GOLD, anchor="lm")
    fh = font("InterDisplay-Black.otf", 82 * s)
    y = int(176 * s)
    for ln, col in [("“IGNITED”", GOLD), ("AT 4 P.M.", GOLD), ("KNOWN FOR", CREAM), ("HOURS", CREAM)]:
        d.text((pad - int(4 * s), y), ln, font=fh, fill=col); y += int(92 * s)
        if ln == "AT 4 P.M.":
            d.text((pad, y + int(4 * s)), "VS.", font=font("Inter-Black.otf", 26 * s), fill=MUTED); y += int(40 * s)
    d.rectangle([pad, y + int(14 * s), pad + int(180 * s), y + int(22 * s)], fill=GOLD)
    fs = font("InterDisplay-Bold.otf", 30 * s)
    d.text((pad, y + int(42 * s)), "National Defence's account vs. the military's own", font=fs, fill=CREAM)

    # right: two quote cards
    cx0, cw = int(860 * s), int(650 * s)
    cards = [
        ("DND NEWS RELEASE · OVERNIGHT, OCT. 18", "At approx. 4:00 p.m., “a fire ignited within the training area”", AMBER),
        ("MILITARY BRIEFING · SUNDAY, OCT. 18", "Range Control “was aware there was a fire for several hours and were monitoring it”", GREEN),
    ]
    cy = int(190 * s)
    for lab, q, col in cards:
        fq = font("InterDisplay-Bold.otf", 34 * s)
        lines = wrap(d, q, fq, cw - int(70 * s))
        ch = int(80 * s) + len(lines) * int(44 * s) + int(30 * s)
        d.rounded_rectangle([cx0, cy, cx0 + cw, cy + ch], radius=int(12 * s), fill=PANEL)
        d.rectangle([cx0, cy, cx0 + int(8 * s), cy + ch], fill=col)
        d.text((cx0 + int(36 * s), cy + int(30 * s)), lab, font=font("Inter-Bold.otf", 20 * s), fill=col)
        yy = cy + int(70 * s)
        for ln in lines: d.text((cx0 + int(36 * s), yy), ln, font=fq, fill=CREAM); yy += int(44 * s)
        cy += ch + int(30 * s)
    d.text((cx0, cy), "Briefing quote: Maj.-Gen. Wade Rutland, as reported by Yahoo News Canada", font=font("Inter-Medium.otf", 17 * s), fill=MUTED)

    fy = H - int(100 * s)
    d.rectangle([0, fy, W, H], fill=NAVY); d.rectangle([0, fy, W, fy + int(5 * s)], fill=GOLD)
    ff = font("Inter-Black.otf", 34 * s)
    d.text((pad, fy + int(50 * s)), "PRIME ROGUE", font=ff, fill=GOLD, anchor="lm")
    fw = d.textlength("PRIME ROGUE", font=ff)
    d.text((pad + fw + int(24 * s), fy + int(52 * s)), "Independent reporting  ·  Strategic transparency", font=font("Inter-Medium.otf", 26 * s), fill=CREAM, anchor="lm")
    logo = Image.open(LOGO).convert("RGBA").resize((int(84 * s), int(84 * s)), Image.LANCZOS)
    img.alpha_composite(logo, (W - int(84 * s) - int(40 * s), fy + int(8 * s)))
    img.convert("RGB").save(out, quality=90, optimize=True)

# ---------------- TIMELINE: afternoon + statements ----------------
def timeline(out):
    W, pad = 1600, 60
    H = 1345
    img = Image.new("RGBA", (W, H), BROWN_DK + (255,)); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 10, H], fill=GOLD)
    d.text((pad, 40), "CFB WAINWRIGHT  ·  OCT. 17–18, 2026  ·  MOUNTAIN TIME", font=font("Inter-Bold.otf", 24), fill=GOLD)
    d.text((pad, 74), "What happened that afternoon, and how", font=font("InterDisplay-Black.otf", 50), fill=CREAM)
    d.text((pad, 134), "National Defence described it", font=font("InterDisplay-Black.otf", 50), fill=CREAM)

    # Panel A
    ay = 222
    d.text((pad, ay), "A.  SATURDAY AFTERNOON, OCT. 17", font=font("Inter-Black.otf", 24), fill=GOLD)
    x0, x1 = pad + 40, W - pad - 40
    t0, t1 = 11.0, 17.0
    X = lambda h: x0 + (h - t0) / (t1 - t0) * (x1 - x0)
    axy = ay + 420
    # "aware for several hours" bar
    by = ay + 320
    bx_end = X(16.0)
    for i in range(int(X(12.0)), int(bx_end)):
        a = min(1.0, (i - X(12.0)) / (X(13.5) - X(12.0)))
        c = tuple(int(BROWN_DK[k] * (1 - a) + GREEN[k] * a) for k in range(3))
        d.line([(i, by), (i, by + 34)], fill=c)
    d.text((X(12.0), by - 30), "Range Control aware of a fire for “several hours” and monitoring it (start time not disclosed)", font=font("Inter-SemiBold.otf", 20), fill=GREEN)
    d.text((X(12.0), by + 42), "Military briefing, Oct. 18, as reported", font=font("Inter-Medium.otf", 17), fill=MUTED)
    # axis
    d.line([(x0, axy), (x1, axy)], fill=(110, 92, 74), width=4)
    for h in range(11, 18):
        lab = f"{h if h <= 12 else h - 12} {'a.m.' if h < 12 else 'p.m.'}"
        d.line([(X(h), axy - 8), (X(h), axy + 8)], fill=(110, 92, 74), width=3)
        d.text((X(h), axy + 30), lab, font=font("Inter-Bold.otf", 20), fill=MUTED, anchor="mm")
    # 4 p.m. line
    d.line([(X(16), by - 40), (X(16), axy + 16)], fill=RED, width=4)
    ev = [
        (11.0, "≈11 a.m.", "Forecast: gusts to 80 km/h", "Environment Canada", MUTED),
        (12.28, "12:17 p.m.", "59 low-confidence fire detections", "Landsat 8, NASA FIRMS", LANDSAT),
        (14.82, "2:49 p.m.", "Fire detected on the range: 8 detections", "NOAA-20 VIIRS, NASA FIRMS", BLUE),
        (15.05, "3:03 p.m.", "Wind warning continued, gusts to 90 km/h", "Environment Canada", MUTED),
        (15.5, "≈3:30 p.m.", "Resident sees a wall of smoke", "The Globe and Mail", AMBER),
        (16.0, "≈4 p.m.", "Wind swings NW, gusts to 69 km/h; fire 1 km away reaches C Company in 30–60 sec.", "Briefing; ECCC base station", RED),
    ]
    n = len(ev); gw = 14; cw6 = (W - 2 * pad - (n - 1) * gw) / n
    cy6, ch6 = ay + 50, 200
    for i, (h, t, txt, src, col) in enumerate(ev):
        cx = pad + i * (cw6 + gw)
        d.rounded_rectangle([cx, cy6, cx + cw6, cy6 + ch6], radius=8, fill=PANEL, outline=col if col == RED else None, width=2)
        d.ellipse([cx + 14, cy6 + 14, cx + 44, cy6 + 44], fill=col)
        d.text((cx + 29, cy6 + 29), str(i + 1), font=font("Inter-Black.otf", 18), fill=BROWN_DK, anchor="mm")
        d.text((cx + 54, cy6 + 29), t, font=font("Inter-Bold.otf", 21), fill=CREAM, anchor="lm")
        yy = cy6 + 58
        fl = font("Inter-SemiBold.otf", 18)
        for ln in wrap(d, txt, fl, cw6 - 28): d.text((cx + 14, yy), ln, font=fl, fill=CREAM); yy += 24
        d.text((cx + 14, cy6 + ch6 - 30), src, font=font("Inter-Medium.otf", 15), fill=col)
        x = X(h)
        d.ellipse([x - 15, axy - 15, x + 15, axy + 15], fill=col, outline=BROWN_DK, width=3)
        d.text((x, axy), str(i + 1), font=font("Inter-Black.otf", 16), fill=BROWN_DK, anchor="mm")
    # Panel B
    py = axy + 90
    d.line([(pad, py), (W - pad, py)], fill=(70, 55, 44), width=2)
    d.text((pad, py + 30), "B.  HOW NATIONAL DEFENCE DESCRIBED IT", font=font("Inter-Black.otf", 24), fill=GOLD)
    cards = [
        ("SAT., OCT. 17", "CAF statement", "Fire “was reported on the range” at approx. 1600", "Consistent with the briefing", GREEN),
        ("OVERNIGHT", "DND news release, dated Oct. 18", "At approx. 4:00 p.m., “a fire ignited within the training area”", "No mention of an earlier fire", AMBER),
        ("SUN., OCT. 18", "DND news release", "Names Exercise APOLLO SHOOTER; fire overtook the unit administrative area", "No mention of an earlier fire", AMBER),
        ("SUN., 3 P.M.", "Military briefing, Edmonton", "Range Control aware of a fire “for several hours” and monitoring it; training continued", "First official account of the earlier fire", GREEN),
    ]
    cw = (W - 2 * pad - 3 * 24) / 4
    cy = py + 80; ch = 300
    for i, (when, who, what, note, col) in enumerate(cards):
        cx = pad + i * (cw + 24)
        d.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=10, fill=PANEL)
        d.rectangle([cx, cy, cx + cw, cy + 8], fill=col)
        d.text((cx + 22, cy + 30), when, font=font("Inter-Black.otf", 22), fill=col)
        yy = cy + 64
        for ln in wrap(d, who, font("Inter-Bold.otf", 19), cw - 44):
            d.text((cx + 22, yy), ln, font=font("Inter-Bold.otf", 19), fill=MUTED); yy += 26
        yy += 12
        for ln in wrap(d, what, font("Inter-SemiBold.otf", 23), cw - 44):
            d.text((cx + 22, yy), ln, font=font("Inter-SemiBold.otf", 23), fill=CREAM); yy += 31
        d.line([(cx + 22, cy + ch - 70), (cx + cw - 22, cy + ch - 70)], fill=(70, 55, 44), width=2)
        ny = cy + ch - 56
        for ln in wrap(d, note, font("Inter-Bold.otf", 19), cw - 44):
            d.text((cx + 22, ny), ln, font=font("Inter-Bold.otf", 19), fill=col); ny += 25
    # arrows
    for i in range(3):
        ax = pad + (i + 1) * (cw + 24) - 12
        d.polygon([(ax - 7, cy + ch / 2 - 10), (ax + 7, cy + ch / 2), (ax - 7, cy + ch / 2 + 10)], fill=GOLD)

    footer(img, d, W, H, 185, [
        "Times approximate where marked (≈). Satellites detect heat, not cause; detections cannot show whether the earlier fire is the fire that",
        "reached the soldiers. DND has not said whether they are the same fire. Briefing wording as reported by Yahoo News Canada and CTV News.",
    ])
    img.convert("RGB").save(out, quality=90, optimize=True)
    print("timeline", img.size)

# ---------------- TWO READINGS ----------------
def readings(out):
    W, pad = 1600, 60
    H = 1000
    img = Image.new("RGBA", (W, H), BROWN_DK + (255,)); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 10, H], fill=GOLD)
    d.text((pad, 40), "CFB WAINWRIGHT  ·  THE UNANSWERED QUESTION", font=font("Inter-Bold.otf", 24), fill=GOLD)
    d.text((pad, 74), "One fire or two? Either way, the first", font=font("InterDisplay-Black.otf", 50), fill=CREAM)
    d.text((pad, 134), "account left something out", font=font("InterDisplay-Black.otf", 50), fill=CREAM)
    cw = (W - 2 * pad - 40) / 2
    cy, ch = 230, 500
    cols = [
        ("READING 1: ONE FIRE", "The fire Range Control was monitoring is the fire that reached C Company.", [
            ("Fire burning for hours", GREEN), ("Wind shift ≈4 p.m.", AMBER), ("Fire reaches soldiers", RED)],
         "The fire did not ignite at 4 p.m. The release gave a start time the military's own account does not support."),
        ("READING 2: TWO FIRES", "A separate grass fire started near the range at about 4 p.m., while another fire was being monitored.", [
            ("Fire A: monitored for hours", GREEN), ("Fire B: starts ≈4 p.m.", AMBER), ("Fire B reaches soldiers", RED)],
         "“Ignited” may be accurate for Fire B, but the release left out a known fire burning on the base, and raises where it was and what started Fire B."),
    ]
    for i, (title, desc, steps, verdict) in enumerate(cols):
        cx = pad + i * (cw + 40)
        d.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=12, fill=PANEL)
        d.rectangle([cx, cy, cx + cw, cy + 8], fill=GOLD)
        d.text((cx + 32, cy + 36), title, font=font("Inter-Black.otf", 28), fill=GOLD)
        yy = cy + 88
        for ln in wrap(d, desc, font("Inter-SemiBold.otf", 24), cw - 64):
            d.text((cx + 32, yy), ln, font=font("Inter-SemiBold.otf", 24), fill=CREAM); yy += 33
        yy += 26
        sw = (cw - 64 - 2 * 30) / 3
        for j, (lab, col) in enumerate(steps):
            sx = cx + 32 + j * (sw + 30)
            d.rounded_rectangle([sx, yy, sx + sw, yy + 120], radius=10, fill=PANEL2, outline=col, width=3)
            ly = yy + 60 - 14 * len(wrap(d, lab, font("Inter-Bold.otf", 21), sw - 24))
            for ln in wrap(d, lab, font("Inter-Bold.otf", 21), sw - 24):
                d.text((sx + sw / 2, ly + 14), ln, font=font("Inter-Bold.otf", 21), fill=CREAM, anchor="mm"); ly += 28
            if j < 2:
                ax = sx + sw + 15
                d.polygon([(ax - 8, yy + 50), (ax + 8, yy + 60), (ax - 8, yy + 70)], fill=GOLD)
        yy += 160
        d.text((cx + 32, yy), "WHAT IT MEANS FOR THE RELEASE", font=font("Inter-Black.otf", 20), fill=AMBER); yy += 40
        for ln in wrap(d, verdict, font("Inter-SemiBold.otf", 23), cw - 64):
            d.text((cx + 32, yy), ln, font=font("Inter-SemiBold.otf", 23), fill=CREAM); yy += 32
    d.text((pad, cy + ch + 34), "DND was asked what “ignited” at 4 p.m. It referred Prime Rogue to Sunday's briefing, which did not say.", font=font("InterDisplay-Bold.otf", 28), fill=GOLD)
    footer(img, d, W, H, 150, [
        "Prime Rogue's characterization of possible readings; neither has been confirmed by National Defence. Sources: DND release, Oct. 18; military briefing, Oct. 18.",
    ])
    img.convert("RGB").save(out, quality=90, optimize=True)
    print("readings", img.size)

header(1600, 900, "/home/claude/cfb-wainwright-dnd-header.jpg")
header(1200, 675, "/home/claude/cfb-wainwright-dnd-header-1200.jpg")
timeline("/home/claude/cfb-wainwright-dnd-timeline.jpg")
readings("/home/claude/cfb-wainwright-two-readings.jpg")
