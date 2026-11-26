# Render "The World in One Day" — Thursday 26 November 2026.
# A one-page newspaper front page, 1024x1024, drawn entirely with PIL
# primitives and real OFL fonts (Playfair Display + EB Garamond).
# Style: worn-paper realism — grain, mottle, rust, haze, textured scenes.
# Every small story icon gets its own scene backdrop; no uniform wash.
import math
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
MARGIN = 28
INK = (32, 26, 22)
RED = (172, 32, 26)
PAPER = (246, 238, 220)
RULE = (40, 32, 26)

random.seed(20261126)


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


F_TITLE = font("PlayfairDisplay.ttf", 62)
F_DATE = font("EBGaramond.ttf", 24)
F_SUB = font("EBGaramond-Italic.ttf", 16)
F_KICK = font("EBGaramond.ttf", 15)
F_HEAD = font("EBGaramond.ttf", 27)
F_DECK = font("EBGaramond.ttf", 15)
F_SECT = font("EBGaramond.ttf", 17)
F_TILE_T = font("EBGaramond.ttf", 17)
F_TILE_B = font("EBGaramond.ttf", 13)
F_LIST = font("EBGaramond.ttf", 13)
F_FOOT = font("EBGaramond.ttf", 12)
F_FOOT_I = font("EBGaramond-Italic.ttf", 12)
F_BADGE = font("EBGaramond.ttf", 13)


def wrap(text, fnt, maxw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if fnt.getlength(trial) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(dr, lines, x, y, fnt, fill, lh):
    for ln in lines:
        dr.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def vgrad(size, top, bottom):
    w, h = size
    img = Image.new("RGB", size)
    dr = ImageDraw.Draw(img)
    for yy in range(h):
        t = yy / max(1, h - 1)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        dr.line([(0, yy), (w, yy)], fill=c)
    return img


def grain(img, strength=0.10, sigma=26):
    noise = Image.effect_noise(img.size, sigma).convert("RGB")
    return Image.blend(img, ImageChops.screen(img, noise), strength)


def mottle(img, n=26, alpha=26):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    for _ in range(n):
        x = random.randint(0, img.width)
        y = random.randint(0, img.height)
        rx = random.randint(30, 160)
        ry = random.randint(12, 60)
        tone = random.choice([(120, 90, 60), (255, 250, 235), (90, 70, 55), (200, 180, 140)])
        dr.ellipse([x - rx, y - ry, x + rx, y + ry], fill=tone + (alpha,))
    ov = ov.filter(ImageFilter.GaussianBlur(18))
    out = Image.alpha_composite(img.convert("RGBA"), ov)
    return out.convert("RGB")


def haze(img, alpha=26):
    ov = Image.new("RGBA", img.size, (235, 228, 210, alpha))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def vignette(img, strength=52):
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    dr = ImageDraw.Draw(mask)
    dr.ellipse([-w * 0.28, -h * 0.35, w * 1.28, h * 1.35], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(24))
    dark = Image.new("RGB", (w, h), (25, 18, 12))
    return Image.composite(img, Image.blend(img, dark, strength / 255.0 * 2.2), mask)


def soft_disc(dr, cx, cy, r, colour, rings=5):
    for i in range(rings, 0, -1):
        a = int(255 * (1 - i / (rings + 1)) ** 1.5)
        rr = r * i / rings
        dr.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=colour + (a,))


def fireball(img, cx, cy, r):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    soft_disc(dr, cx, cy, r, (255, 170, 40))
    soft_disc(dr, cx, cy, r * 0.62, (255, 220, 110))
    soft_disc(dr, cx, cy, r * 0.34, (255, 245, 200))
    for _ in range(9):
        a = random.uniform(0, math.pi * 2)
        d = random.uniform(0.3, 0.95) * r
        rr = random.uniform(2, r * 0.22)
        ex, ey = cx + math.cos(a) * d, cy + math.sin(a) * d * 0.7
        dr.ellipse([ex - rr, ey - rr, ex + rr, ey + rr],
                   fill=(255, random.randint(120, 200), 30, 220))
    out = Image.alpha_composite(img.convert("RGBA"), ov)
    return out.convert("RGB")


def smoke(img, x, y, wdt, hgt, n=14, base=(70, 62, 58)):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    for i in range(n):
        t = i / max(1, n - 1)
        cx = x + t * wdt + random.randint(-8, 8)
        cy = y - t * hgt + random.randint(-6, 6)
        r = 7 + t * 15 + random.randint(-3, 3)
        a = int(150 * (1 - t * 0.55))
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=base + (a,))
    ov = ov.filter(ImageFilter.GaussianBlur(5))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def finish_scene(img):
    img = mottle(img, n=10, alpha=16)
    img = grain(img, 0.12)
    img = vignette(img, 34)
    return img


# ---- depth helpers: layered skies, glow, haze, volumetric puffs, shadows
def multi_grad(size, stops):
    # stops: list of (pos 0..1, colour); smooth multi-stop vertical gradient
    w, h = size
    img = Image.new("RGB", size)
    dr = ImageDraw.Draw(img)
    for yy in range(h):
        t = yy / max(1, h - 1)
        c = stops[-1][1]
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                f = 0 if p1 == p0 else (t - p0) / (p1 - p0)
                c = tuple(int(c0[j] + (c1[j] - c0[j]) * f) for j in range(3))
                break
        dr.line([(0, yy), (w, yy)], fill=c)
    return img


def glow(img, cx, cy, r, colour, alpha=200):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    for i in range(6, 0, -1):
        a = int(alpha * (1 - i / 7.0) ** 1.6)
        rr = r * i / 6.0
        dr.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=colour + (a,))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def haze_band(img, y0, y1, colour=(232, 222, 200), alpha=46):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    dr.rectangle([0, y0, img.width, y1], fill=colour + (alpha,))
    ov = ov.filter(ImageFilter.GaussianBlur(4))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def puff(img, cx, cy, r, colour, alpha=150, n=7, squash=0.62):
    # volumetric cloud / smoke cluster: soft overlapping discs, blurred
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    for _ in range(n):
        a = random.uniform(0, math.pi * 2)
        d = random.uniform(0, 0.75) * r
        ex = cx + math.cos(a) * d
        ey = cy + math.sin(a) * d * squash
        rr = random.uniform(0.35, 0.7) * r
        dr.ellipse([ex - rr, ey - rr, ex + rr, ey + rr], fill=colour + (alpha,))
    ov = ov.filter(ImageFilter.GaussianBlur(3))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def soft_shadow(img, box, alpha=90, blur=3):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    dr.ellipse(box, fill=(10, 8, 6, alpha))
    ov = ov.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def water(img, y0, y1, deep, light):
    dr = ImageDraw.Draw(img)
    dr.rectangle([0, y0, img.width, y1], fill=deep)
    for yy in range(y0 + 4, y1, 7):
        for xx in range(0, img.width, 24):
            off = (xx * 7 + yy * 3) % 13
            dr.arc([xx + off - 9, yy - 3, xx + off + 10, yy + 4], 200, 340,
                   fill=light, width=2)
    return img


# ---------------------------------------------------------------- big scenes
def scene_gulf():
    w, h = 307, 150
    img = multi_grad((w, h), [(0.0, (22, 14, 36)), (0.42, (88, 40, 52)),
                              (0.62, (198, 100, 44)), (1.0, (238, 148, 58))])
    # low sun glow on the horizon
    img = glow(img, 78, 92, 52, (255, 140, 40), 210)
    img = glow(img, 78, 92, 22, (255, 210, 120), 220)
    dr = ImageDraw.Draw(img)
    # far refinery, hazed by dusk
    for x0, x1, top in [(4, 30, 64), (36, 56, 70), (148, 172, 66), (196, 214, 72), (242, 262, 68)]:
        dr.rectangle([x0, top, x1, 94], fill=(74, 52, 62))
    for x in (62, 118, 222, 282):
        dr.rectangle([x, 58, x + 3, 94], fill=(74, 52, 62))
    img = haze_band(img, 58, 96, (232, 190, 150), 40)
    dr = ImageDraw.Draw(img)
    # near refinery, dark against the glow
    for x0, x1, top in [(10, 36, 56), (44, 62, 64), (152, 178, 58), (198, 216, 66), (244, 264, 60)]:
        dr.rectangle([x0, top, x1, 96], fill=(12, 14, 24))
        for wx in range(x0 + 4, x1 - 2, 7):
            dr.rectangle([wx, top + 5, wx + 2, top + 9], fill=(255, 190, 80))
    for x in (66, 122, 224, 284):
        dr.rectangle([x, 50, x + 3, 96], fill=(12, 14, 24))
    # flare stacks with volumetric smoke
    img = fireball(img, 60, 46, 13)
    img = fireball(img, 216, 54, 9)
    img = smoke(img, 60, 44, 22, 40, n=12)
    img = smoke(img, 216, 52, 16, 30, n=9)
    # sea, dark, with orange reflection lanes under the sun and fires
    img = water(img, 96, h, (12, 20, 36), (120, 150, 180))
    dr = ImageDraw.Draw(img)
    for cx, cw in [(78, 60), (84, 34), (240, 26)]:
        for yy in range(100, h, 8):
            dr.line([cx - cw // 2 + (yy % 5), yy, cx + cw // 2 - (yy % 7), yy],
                    fill=(220, 130, 50), width=2)
    # foreground tanker, close and large, hull shaded
    dr.polygon([(10, 112), (168, 112), (158, 130), (20, 130)], fill=(16, 18, 26))
    dr.rectangle([10, 112, 168, 117], fill=(52, 56, 66))
    dr.rectangle([10, 126, 168, 130], fill=(122, 26, 22))
    # bridge tower with lit windows
    dr.rectangle([140, 92, 158, 112], fill=(30, 34, 44))
    for wy in (96, 102):
        dr.rectangle([142, wy, 156, wy + 3], fill=(255, 200, 110))
    # deck fire
    img = fireball(img, 84, 104, 15)
    img = smoke(img, 84, 100, 24, 42, n=12)
    dr = ImageDraw.Draw(img)
    # bow wave foam
    for xx in range(4, 26, 5):
        dr.ellipse([xx, 130, xx + 8, 134], fill=(200, 215, 225))
    # second tanker, distant and hazed
    dr.rectangle([200, 118, 292, 128], fill=(20, 24, 34))
    img = fireball(img, 244, 114, 9)
    img = smoke(img, 244, 110, 16, 26, n=8)
    dr = ImageDraw.Draw(img)
    # missile streaks with glow trails
    for x0, y0, x1, y1 in [(250, 18, 268, 40), (272, 10, 284, 34), (228, 26, 244, 46)]:
        dr.line([x0, y0, x1, y1], fill=(255, 200, 120), width=4)
        dr.line([x0, y0, x1, y1], fill=(255, 240, 200), width=2)
        dr.ellipse([x1 - 2, y1 - 2, x1 + 2, y1 + 2], fill=(255, 220, 120))
    # price chip
    dr.rounded_rectangle([206, 6, 301, 26], radius=10, fill=(20, 16, 14))
    dr.text((214, 9), "BRENT $94.71", font=F_BADGE, fill=(255, 214, 120))
    return finish_scene(img)


def scene_tariffs():
    w, h = 307, 150
    img = multi_grad((w, h), [(0.0, (146, 158, 170)), (0.55, (178, 184, 190)),
                              (0.72, (196, 198, 200)), (1.0, (150, 158, 166))])
    # drifting clouds
    img = puff(img, 60, 22, 26, (235, 238, 240), 130, n=8)
    img = puff(img, 210, 16, 30, (228, 232, 236), 120, n=8)
    img = puff(img, 150, 40, 20, (220, 224, 228), 100, n=6)
    # distant port cranes, hazed
    dr = ImageDraw.Draw(img)
    for x in (20, 90, 250):
        dr.rectangle([x, 78, x + 4, 108], fill=(140, 148, 156))
        dr.line([x, 80, x + 34, 88], fill=(140, 148, 156), width=3)
        dr.line([x + 34, 88, x + 34, 100], fill=(140, 148, 156), width=2)
    img = haze_band(img, 74, 110, (220, 224, 228), 46)
    # sea
    img = water(img, 108, h, (46, 68, 88), (150, 175, 195))
    dr = ImageDraw.Draw(img)
    # container ship hull with sunlit top edge and dark waterline
    dr.polygon([(14, 96), (292, 96), (282, 112), (26, 112)], fill=(122, 26, 22))
    dr.polygon([(14, 96), (292, 96), (292, 100), (14, 100)], fill=(178, 60, 48))
    dr.rectangle([14, 108, 292, 114], fill=(70, 14, 12))
    # bow wave foam
    for xx in range(282, 304, 4):
        dr.ellipse([xx, 110, xx + 7, 115], fill=(220, 230, 236))
    # container stacks: top highlight, side shade, ribs, bottom shadow
    stacks = [
        (30, [(196, 70, 52), (52, 96, 140), (214, 150, 52)]),
        (96, [(52, 120, 86), (178, 96, 44), (96, 96, 130)]),
        (162, [(214, 150, 52), (140, 52, 52), (60, 110, 130)]),
        (228, [(52, 96, 140), (196, 70, 52)]),
    ]
    for x0, cols in stacks:
        for i, c in enumerate(cols):
            y0 = 96 - (i + 1) * 15
            dr.rectangle([x0, y0, x0 + 60, y0 + 14], fill=c, outline=(30, 26, 22))
            light = tuple(min(255, v + 60) for v in c)
            dr.line([x0, y0, x0 + 60, y0], fill=light, width=2)
            dr.line([x0, y0 + 13, x0 + 60, y0 + 13], fill=(20, 18, 16), width=1)
            for vx in range(x0 + 8, x0 + 56, 10):
                dr.line([vx, y0 + 2, vx, y0 + 12], fill=(0, 0, 0), width=1)
    # bridge tower with lit windows and shaded side
    dr.rectangle([246, 44, 272, 96], fill=(228, 228, 224))
    dr.rectangle([264, 44, 272, 96], fill=(180, 182, 178))
    dr.rectangle([248, 48, 270, 56], fill=(40, 60, 80))
    dr.rectangle([248, 60, 270, 62], fill=(120, 130, 140))
    dr.line([259, 44, 259, 36], fill=(90, 90, 86), width=2)
    # red tariff badge
    dr.ellipse([232, 8, 296, 72], fill=(172, 32, 26), outline=(246, 238, 220), width=3)
    dr.text((256, 16), "%", font=font("PlayfairDisplay.ttf", 40),
            fill=(246, 238, 220), anchor="ma")
    # falling arrows
    for x, y0, ln in [(36, 12, 22), (120, 6, 26), (196, 14, 20)]:
        dr.line([x, y0, x, y0 + ln], fill=(172, 32, 26), width=4)
        dr.polygon([(x - 6, y0 + ln - 2), (x + 6, y0 + ln - 2), (x, y0 + ln + 8)],
                   fill=(172, 32, 26))
    return finish_scene(img)


def scene_spacex():
    w, h = 307, 150
    img = multi_grad((w, h), [(0.0, (4, 6, 18)), (0.6, (12, 20, 46)), (1.0, (20, 32, 64))])
    # nebula veils
    img = puff(img, 60, 40, 46, (70, 60, 140), 46, n=10, squash=0.5)
    img = puff(img, 240, 70, 52, (40, 70, 120), 40, n=10, squash=0.5)
    img = puff(img, 150, 20, 36, (90, 70, 130), 36, n=8, squash=0.5)
    dr = ImageDraw.Draw(img)
    for _ in range(110):
        x = random.randint(0, w - 1)
        y = random.randint(0, 118)
        r = random.choice([1, 1, 1, 2])
        b = random.randint(150, 255)
        dr.ellipse([x - r, y - r, x + r, y + r], fill=(b, b, 255))
    # a few bright stars with cross sparkle
    for x, y in [(52, 30), (180, 18), (268, 52), (120, 88)]:
        dr.line([x - 4, y, x + 4, y], fill=(255, 255, 255), width=1)
        dr.line([x, y - 4, x, y + 4], fill=(255, 255, 255), width=1)
    # constellation: linked satellites, panels shaded light/dark
    pts = [(40, 26), (92, 44), (150, 22), (208, 40), (262, 24),
           (66, 62), (124, 78), (186, 60), (240, 76)]
    for i in range(len(pts) - 1):
        dr.line([pts[i], pts[i + 1]], fill=(120, 160, 220), width=1)
    for (x, y) in pts:
        dr.rectangle([x - 9, y - 2, x - 2, y + 2], fill=(210, 220, 245))
        dr.rectangle([x + 2, y - 2, x + 9, y + 2], fill=(140, 155, 190))
        dr.rectangle([x - 2, y - 2, x + 2, y + 2], fill=(255, 235, 160))
    # rocket streak with glowing exhaust
    img = glow(img, 98, 44, 16, (255, 180, 80), 160)
    dr = ImageDraw.Draw(img)
    dr.line([36, 132, 96, 44], fill=(255, 190, 90), width=3)
    img = fireball(img, 98, 42, 9)
    dr = ImageDraw.Draw(img)
    dr.polygon([(94, 34), (102, 46), (90, 48)], fill=(230, 230, 225))
    dr.polygon([(98, 38), (102, 46), (94, 46)], fill=(170, 170, 165))
    # Earth curve with atmosphere halo
    img = glow(img, 150, 210, 120, (90, 150, 255), 80)
    dr = ImageDraw.Draw(img)
    dr.ellipse([-60, 118, 367, 320], fill=(38, 92, 158))
    dr.ellipse([-60, 118, 367, 320], outline=(150, 200, 255), width=2)
    # ocean shading near the limb
    dr.arc([-60, 118, 367, 320], 200, 340, fill=(120, 180, 235), width=6)
    for cx, cy, rx, ry in [(30, 150, 46, 16), (150, 168, 60, 18), (250, 148, 40, 14)]:
        dr.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(64, 140, 90))
        dr.ellipse([cx - rx, cy - ry, cx - rx + 18, cy - ry + 7], fill=(96, 170, 110))
    # cloud swirls over the ocean
    img = puff(img, 90, 158, 22, (235, 242, 250), 120, n=6, squash=0.4)
    img = puff(img, 210, 172, 26, (235, 242, 250), 110, n=6, squash=0.4)
    dr = ImageDraw.Draw(img)
    # night terminator shading on the right limb
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.ellipse([220, 118, 367, 320], fill=(6, 10, 30, 70))
    ov = ov.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    dr = ImageDraw.Draw(img)
    dr.arc([-60, 118, 367, 320], 180, 360, fill=(190, 220, 255), width=3)
    # "1,000,000" tag
    dr.rounded_rectangle([8, 6, 128, 26], radius=10, fill=(12, 16, 30))
    dr.text((16, 9), "1M SATELLITES", font=F_BADGE, fill=(180, 210, 255))
    return finish_scene(img)


# ---------------------------------------------------------------- small icons
def icon_base(size, top, bottom):
    return vgrad(size, top, bottom)


def icon_finish(img):
    img = mottle(img, n=4, alpha=14)
    img = grain(img, 0.10)
    img = vignette(img, 26)
    return img


def icon_nk():
    img = multi_grad((62, 62), [(0.0, (10, 14, 26)), (0.7, (30, 44, 40)), (1.0, (52, 66, 48))])
    dr = ImageDraw.Draw(img)
    for _ in range(14):
        x = random.randint(0, 61)
        y = random.randint(0, 30)
        dr.ellipse([x, y, x + 1, y + 1], fill=(220, 220, 255))
    # distant ridge
    dr.polygon([(0, 46), (12, 34), (24, 42), (38, 32), (50, 40), (62, 34), (62, 62), (0, 62)],
               fill=(22, 30, 26))
    # ground
    dr.rectangle([0, 46, 62, 62], fill=(14, 18, 12))
    img = soft_shadow(img, [14, 48, 48, 54], 110, 2)
    dr = ImageDraw.Draw(img)
    # launcher base with lit top edge
    dr.rectangle([16, 44, 46, 48], fill=(44, 44, 40))
    dr.rectangle([16, 44, 46, 46], fill=(80, 80, 72))
    # missile body, shaded light left / dark right
    dr.rectangle([26, 12, 36, 46], fill=(205, 205, 198))
    dr.rectangle([31, 12, 36, 46], fill=(150, 150, 144))
    dr.polygon([(26, 12), (36, 12), (31, 4)], fill=(220, 60, 50))
    dr.polygon([(31, 4), (36, 12), (31, 12)], fill=(160, 40, 34))
    # flame glow at the base
    img = fireball(img, 31, 50, 7)
    return icon_finish(img)


def icon_bogor():
    img = multi_grad((62, 62), [(0.0, (110, 82, 52)), (0.55, (70, 50, 30)), (1.0, (40, 28, 18))])
    img = glow(img, 31, 12, 20, (255, 190, 90), 120)
    dr = ImageDraw.Draw(img)
    # pit walls, layered strata
    dr.polygon([(0, 62), (0, 26), (20, 16), (42, 22), (62, 12), (62, 62)],
               fill=(44, 30, 18))
    for y0, c in [(26, (66, 46, 26)), (36, (52, 36, 20)), (46, (40, 28, 16))]:
        dr.polygon([(0, 62), (0, y0 + 8), (62, y0 - 4), (62, 62)], fill=c)
    # water pool at the bottom
    dr.rectangle([0, 48, 62, 62], fill=(30, 58, 88))
    for yy in (52, 57):
        dr.arc([-6, yy - 3, 68, yy + 4], 200, 340, fill=(150, 190, 220), width=2)
    # headlamps glowing in the dark pit
    img = glow(img, 26, 34, 8, (255, 230, 140), 200)
    img = glow(img, 38, 38, 8, (255, 230, 140), 200)
    dr = ImageDraw.Draw(img)
    dr.ellipse([24, 32, 28, 36], fill=(255, 240, 180))
    dr.ellipse([36, 36, 40, 40], fill=(255, 240, 180))
    return icon_finish(img)


def icon_eu():
    img = multi_grad((62, 62), [(0.0, (24, 52, 110)), (0.6, (60, 92, 152)), (1.0, (96, 126, 176))])
    img = puff(img, 12, 12, 14, (220, 228, 238), 90, n=5)
    dr = ImageDraw.Draw(img)
    # ring of stars above the building
    for i in range(12):
        a = i * math.pi / 6
        x = 31 + 15 * math.cos(a)
        y = 14 + 15 * math.sin(a) * 0.6
        dr.ellipse([x - 1, y - 1, x + 1, y + 1], fill=(255, 220, 60))
    # facade, lit left / shaded right
    dr.rectangle([10, 20, 52, 52], fill=(216, 218, 214))
    dr.rectangle([40, 20, 52, 52], fill=(180, 182, 178))
    for yy in (26, 34, 42):
        for xx in (16, 26, 36):
            dr.rectangle([xx, yy, xx + 4, yy + 5], fill=(60, 90, 140))
    # sunlit roofline
    dr.rectangle([10, 20, 52, 23], fill=(240, 240, 236))
    img = soft_shadow(img, [8, 52, 54, 58], 100, 2)
    return icon_finish(img)


def icon_poland():
    img = multi_grad((62, 62), [(0.0, (110, 150, 195)), (0.6, (190, 205, 222)), (1.0, (222, 228, 234))])
    img = puff(img, 14, 12, 12, (245, 247, 250), 130, n=5)
    img = puff(img, 48, 20, 12, (240, 243, 247), 120, n=5)
    dr = ImageDraw.Draw(img)
    # contrail
    dr.line([(2, 22), (20, 22)], fill=(255, 255, 255), width=2)
    # radar dome, sunlit top
    dr.ellipse([18, 14, 44, 26], fill=(235, 235, 230))
    dr.ellipse([18, 14, 44, 20], fill=(250, 250, 246))
    dr.rectangle([22, 26, 40, 30], fill=(190, 50, 50))
    # fuselage, shaded underside
    dr.polygon([(10, 34), (52, 34), (46, 40), (16, 40)], fill=(205, 205, 200))
    dr.polygon([(34, 34), (52, 34), (46, 40), (34, 40)], fill=(160, 160, 155))
    dr.rectangle([28, 40, 34, 46], fill=(120, 120, 115))
    # flag band at the base
    dr.rectangle([0, 52, 62, 56], fill=(205, 45, 45))
    dr.rectangle([0, 56, 62, 62], fill=(245, 245, 240))
    return icon_finish(img)


def icon_spain():
    img = multi_grad((62, 62), [(0.0, (160, 70, 55)), (0.55, (225, 150, 70)), (1.0, (245, 200, 95))])
    img = glow(img, 10, 10, 14, (255, 220, 90), 160)
    dr = ImageDraw.Draw(img)
    # ballot paper with a cast shadow
    dr.rectangle([27, 16, 37, 32], fill=(200, 195, 185))
    dr.rectangle([26, 18, 36, 32], fill=(250, 248, 240), outline=(120, 20, 16))
    dr.line([30, 22, 34, 26], fill=(172, 32, 26), width=2)
    # ballot box, gold slot band, shaded side
    dr.rectangle([14, 30, 48, 52], fill=(172, 32, 26))
    dr.rectangle([14, 30, 48, 36], fill=(240, 200, 60))
    dr.rectangle([40, 30, 48, 52], fill=(120, 20, 18))
    img = soft_shadow(img, [10, 52, 52, 57], 110, 2)
    return icon_finish(img)


def icon_china():
    img = multi_grad((62, 62), [(0.0, (150, 36, 30)), (0.6, (110, 26, 22)), (1.0, (70, 16, 14))])
    img = glow(img, 51, 13, 12, (255, 220, 120), 150)
    dr = ImageDraw.Draw(img)
    # tiered golden roof
    dr.polygon([(20, 18), (42, 18), (31, 10)], fill=(205, 165, 45))
    dr.polygon([(31, 10), (42, 18), (31, 18)], fill=(165, 125, 32))
    dr.rectangle([18, 18, 44, 21], fill=(180, 140, 35))
    # hall, shaded side
    dr.rectangle([8, 34, 54, 52], fill=(125, 26, 22))
    dr.rectangle([44, 34, 54, 52], fill=(90, 18, 16))
    dr.rectangle([24, 18, 38, 34], fill=(155, 32, 26))
    for xx in (14, 44):
        dr.rectangle([xx, 38, xx + 4, 44], fill=(255, 220, 120))
    dr.rectangle([28, 40, 34, 52], fill=(30, 12, 10))
    img = soft_shadow(img, [6, 52, 56, 57], 110, 2)
    return icon_finish(img)


def icon_nvidia():
    img = multi_grad((62, 62), [(0.0, (12, 26, 20)), (0.6, (22, 44, 30)), (1.0, (36, 60, 40))])
    img = glow(img, 31, 33, 20, (60, 180, 90), 90)
    dr = ImageDraw.Draw(img)
    # chip, 3D: sunlit top face, dark side face, pins
    dr.polygon([(14, 22), (48, 22), (44, 50), (18, 50)], fill=(46, 118, 66))
    dr.polygon([(14, 22), (48, 22), (46, 18), (16, 18)], fill=(90, 190, 110))
    dr.polygon([(48, 22), (46, 18), (42, 46), (44, 50)], fill=(28, 74, 42))
    for xx in (20, 28, 36, 44):
        dr.line([xx, 50, xx, 56], fill=(160, 200, 170), width=2)
    dr.rectangle([24, 26, 38, 40], fill=(20, 60, 34))
    dr.text((26, 27), "NV", font=font("EBGaramond.ttf", 11), fill=(190, 240, 190))
    # red down-trend arrow
    dr.line([(10, 12), (24, 20), (34, 12), (52, 8)], fill=(255, 80, 60), width=3)
    dr.polygon([(52, 8), (46, 8), (52, 14)], fill=(255, 80, 60))
    return icon_finish(img)


def icon_aus():
    img = multi_grad((62, 62), [(0.0, (55, 85, 135)), (0.6, (120, 150, 190)), (1.0, (170, 190, 215))])
    img = puff(img, 50, 10, 10, (230, 236, 242), 110, n=4)
    dr = ImageDraw.Draw(img)
    # screen, lit top, shaded frame
    dr.rectangle([10, 12, 52, 40], fill=(245, 247, 243), outline=(40, 60, 90), width=2)
    dr.rectangle([14, 16, 48, 36], fill=(70, 110, 170))
    dr.rectangle([14, 16, 48, 22], fill=(100, 140, 195))
    dr.polygon([(24, 22), (31, 46), (38, 22), (31, 18)], fill=(255, 220, 90))
    dr.polygon([(26, 24), (31, 34), (36, 24)], fill=(255, 220, 90))
    # stand and base
    dr.rectangle([28, 42, 34, 50], fill=(60, 60, 58))
    dr.rectangle([18, 50, 44, 53], fill=(40, 40, 38))
    img = soft_shadow(img, [14, 52, 48, 57], 100, 2)
    # checkmark
    dr = ImageDraw.Draw(img)
    dr.line([(20, 24), (28, 32), (42, 18)], fill=(255, 255, 255), width=3)
    return icon_finish(img)


def icon_football(bg_top, bg_bot, accent, score):
    img = multi_grad((62, 62), [(0.0, bg_top), (0.55, bg_bot), (1.0, (30, 60, 36))])
    dr = ImageDraw.Draw(img)
    # stadium stands with crowd dots
    dr.rectangle([0, 18, 62, 34], fill=(30, 34, 44))
    for yy in (22, 27, 32):
        for xx in range(2, 62, 5):
            c = random.choice([(220, 220, 210), (200, 90, 70), (90, 140, 220), (240, 200, 90)])
            dr.ellipse([xx, yy, xx + 2, yy + 2], fill=c)
    # floodlight glow
    img = glow(img, 6, 6, 10, (255, 245, 200), 120)
    img = glow(img, 56, 6, 10, (255, 245, 200), 120)
    dr = ImageDraw.Draw(img)
    # pitch with mowing stripes
    dr.rectangle([0, 40, 62, 62], fill=(46, 110, 58))
    for i, xx in enumerate(range(0, 62, 12)):
        if i % 2 == 0:
            dr.rectangle([xx, 40, xx + 12, 62], fill=(56, 126, 66))
    # ball with cast shadow and sunlit top
    img = soft_shadow(img, [24, 42, 42, 47], 110, 2)
    dr = ImageDraw.Draw(img)
    dr.ellipse([22, 24, 40, 42], fill=(245, 245, 240), outline=(30, 30, 28), width=1)
    dr.ellipse([22, 24, 40, 32], fill=(255, 255, 255))
    dr.polygon([(28, 28), (32, 30), (30, 35), (27, 33)], fill=(30, 30, 28))
    dr.polygon([(34, 36), (37, 38), (33, 41), (30, 38)], fill=(30, 30, 28))
    # score label
    dr.rectangle([6, 8, 56, 20], fill=(20, 16, 14))
    dr.text((31, 9), score, font=font("EBGaramond.ttf", 11),
            fill=(255, 230, 120), anchor="ma")
    return icon_finish(img)


def icon_nfl():
    img = multi_grad((62, 62), [(0.0, (96, 64, 42)), (0.55, (52, 66, 40)), (1.0, (28, 48, 26))])
    img = glow(img, 8, 8, 10, (255, 240, 190), 130)
    img = glow(img, 54, 8, 10, (255, 240, 190), 130)
    dr = ImageDraw.Draw(img)
    # goalpost silhouette
    dr.line([(48, 10), (48, 30)], fill=(220, 220, 210), width=2)
    dr.line([(40, 10), (56, 10)], fill=(220, 220, 210), width=2)
    # pitch with mowing stripes and yard lines
    dr.rectangle([0, 38, 62, 62], fill=(46, 100, 52))
    for i, xx in enumerate(range(0, 62, 16)):
        if i % 2 == 0:
            dr.rectangle([xx, 38, xx + 16, 62], fill=(56, 116, 60))
    for xx in (8, 24, 40, 56):
        dr.line([xx, 38, xx, 62], fill=(245, 245, 240), width=2)
    # ball with shading, cast shadow and sunlit top
    img = soft_shadow(img, [16, 38, 46, 44], 110, 2)
    dr = ImageDraw.Draw(img)
    dr.ellipse([14, 16, 48, 40], fill=(120, 70, 34), outline=(240, 220, 190), width=2)
    dr.ellipse([14, 16, 48, 26], fill=(150, 95, 50))
    dr.line([(20, 28), (42, 28)], fill=(245, 245, 240), width=2)
    for yy in (22, 25, 31, 34):
        dr.line([(31, yy), (31, yy + 2)], fill=(245, 245, 240), width=1)
    return icon_finish(img)


def icon_tube():
    img = multi_grad((62, 62), [(0.0, (26, 24, 28)), (0.6, (54, 46, 44)), (1.0, (78, 68, 62))])
    dr = ImageDraw.Draw(img)
    # tunnel wall ribs
    for xx in range(4, 62, 14):
        dr.line([xx, 0, xx, 62], fill=(40, 36, 34), width=2)
    # platform with edge line
    dr.rectangle([0, 46, 62, 62], fill=(24, 22, 20))
    dr.rectangle([0, 46, 62, 48], fill=(200, 200, 190))
    # train front, sunlit top, shaded side
    dr.rectangle([16, 34, 46, 58], fill=(205, 35, 35))
    dr.rectangle([16, 34, 46, 38], fill=(230, 70, 70))
    dr.rectangle([38, 34, 46, 58], fill=(150, 22, 22))
    dr.rectangle([20, 38, 42, 46], fill=(185, 225, 245))
    dr.rectangle([20, 38, 42, 41], fill=(220, 240, 250))
    # headlights
    img = glow(img, 20, 54, 6, (255, 240, 180), 200)
    img = glow(img, 42, 54, 6, (255, 240, 180), 200)
    dr = ImageDraw.Draw(img)
    # roundel
    dr.ellipse([18, 8, 44, 34], outline=(205, 35, 35), width=5)
    dr.rectangle([8, 18, 54, 24], fill=(30, 90, 160))
    return icon_finish(img)


def icon_court():
    img = multi_grad((62, 62), [(0.0, (190, 180, 158)), (0.6, (150, 138, 118)), (1.0, (110, 100, 86))])
    img = glow(img, 50, 10, 14, (255, 235, 180), 130)
    dr = ImageDraw.Draw(img)
    # pediment, shaded right half
    dr.polygon([(10, 22), (52, 22), (31, 10)], fill=(215, 205, 185))
    dr.polygon([(31, 10), (52, 22), (31, 22)], fill=(180, 168, 145))
    # columns with capitals and shaded right edge
    for xx in (14, 24, 34, 44):
        dr.rectangle([xx, 24, xx + 4, 46], fill=(238, 231, 214))
        dr.rectangle([xx + 2, 24, xx + 4, 46], fill=(200, 190, 168))
    dr.rectangle([10, 46, 52, 50], fill=(215, 205, 185))
    # steps with shadow
    dr.rectangle([6, 50, 56, 54], fill=(165, 145, 120))
    dr.rectangle([2, 54, 60, 58], fill=(140, 122, 100))
    img = soft_shadow(img, [10, 56, 52, 60], 90, 2)
    return icon_finish(img)


def icon_pr():
    img = multi_grad((62, 62), [(0.0, (210, 130, 65)), (0.55, (240, 180, 100)), (1.0, (120, 90, 50))])
    img = glow(img, 48, 14, 16, (255, 220, 120), 170)
    dr = ImageDraw.Draw(img)
    # sun
    dr.ellipse([40, 6, 56, 22], fill=(255, 225, 130))
    # ground with lit top edge
    dr.rectangle([0, 44, 62, 62], fill=(42, 92, 72))
    dr.rectangle([0, 44, 62, 47], fill=(70, 130, 90))
    # pylon lattice with cross braces
    dr.line([(10, 44), (31, 16), (52, 44)], fill=(28, 24, 20), width=3)
    dr.line([(31, 16), (31, 44)], fill=(28, 24, 20), width=3)
    dr.line([(4, 22), (58, 22)], fill=(28, 24, 20), width=1)
    dr.line([(8, 32), (54, 32)], fill=(28, 24, 20), width=1)
    dr.line([(16, 38), (46, 38)], fill=(28, 24, 20), width=1)
    dr.line([(18, 26), (44, 40)], fill=(28, 24, 20), width=1)
    dr.line([(44, 26), (18, 40)], fill=(28, 24, 20), width=1)
    # transformer box
    dr.rectangle([46, 40, 56, 48], fill=(60, 60, 58))
    return icon_finish(img)


ICONS = {
    4: icon_nk, 5: icon_bogor, 6: icon_eu, 7: icon_poland, 8: icon_spain,
    9: icon_china, 10: icon_nvidia, 11: icon_aus,
    12: lambda: icon_football((40, 70, 120), (20, 40, 70), None, "2-1"),
    13: lambda: icon_football((120, 30, 30), (60, 20, 20), None, "3-0"),
    14: lambda: icon_football((90, 60, 140), (40, 30, 80), None, "4-1"),
    15: icon_nfl, 16: icon_tube, 17: icon_court, 18: icon_pr,
}

BIG = [
    ("GULF ESCALATION", "Houthis hit Ras Tanura; US tells citizens: leave Iran",
     "Saudi defences say missiles intercepted; two tankers hit mines in Hormuz; Brent ~$94.71.",
     scene_gulf),
    ("TARIFFS", "US proposes tariffs on 14 partners; China hit hardest",
     "Extra 20% on China; EU, Japan and Korea capped at 15%. Nasdaq down 2%; Asia bounces.",
     scene_tariffs),
    ("SPACEX", "FCC clears SpaceX \u2018Starmind\u2019 \u2014 1M satellites",
     "First US authorisation of its kind; first satellite by 2033, full fleet by 2040.",
     scene_spacex),
]

TILES = [
    (4, "North Korea goes nuclear", "Kim says deploy tactical nuclear weapons across domains; expand material output."),
    (5, "Bogor mine flood kills 13", "13 miners dead, 13 trapped ~100m down in Pongkor; search resumes after rain floods pits."),
    (6, "EU leaders clash in Brussels", "Split over a \u20ac45bn Ukraine loan for 2027 and the 2028\u201334 budget; Costa seeks a deal."),
    (7, "Poland plans eastern no-fly zone", "Late-December zone after Russian incursions; NATO AWACS deployment approved."),
    (8, "Spain votes on Sunday", "Snap election puts Sanchez\u2019s eight-year government at stake; right favoured in polls."),
    (9, "Shanghai party chief probed", "Chen Jining under investigation \u2014 the fourth sitting Politburo member to fall since 2025."),
    (10, "Nvidia slides 3.9%", "Shares at $149.30, $2.3tn off October peak; S&P puts credit rating on watch."),
    (11, "Australia passes tech duty law", "Big Tech must prevent foreseeable harms or face fines up to 5% of global revenue."),
    (12, "Lille stun Bayern 2-1", "Ueda 62\u2019, Pavlovic own goal 65\u2019 \u2014 Champions League shock in France."),
    (13, "Liverpool 3-0 Club Brugge", "Isak brace and Wirtz seal a comfortable Champions League win."),
    (14, "Barca 4-1 Sabah; Utd draw", "Gordon twice for Barcelona; Sporting 2-2 Man Utd in a chaotic Lisbon night."),
    (15, "Rams beat Packers 26-13", "Corum runs for a career-high 184 yards and a TD on his birthday."),
    (16, "London Tube strike bites", "RMT 24-hour walkout; no Piccadilly or Circle line; journeys down 43%."),
    (17, "Judge blocks birthright order", "Second judge halts Trump\u2019s newest order curtailing birthright citizenship."),
    (18, "Puerto Rico scraps Luma deal", "Supreme Court cancels power contract 5-4; one-year transition to a new operator."),
]

ALSO = [
    "ISIL suicide attack kills two and wounds five at a Hasakah checkpoint, Syria.",
    "Zambia bans a protest against removing presidential term limits.",
    "North Korea expels the Swiss diplomat in a sanctions row; 48 hours to leave.",
    "Raytheon wins a US Navy contract for the nuclear sea-launched missile SLCM-N.",
    "Palo Alto Networks patches Linux flaw Fragnesia, already exploited.",
    "FedEx plane overshoots a Miami runway; flights briefly suspended.",
    "California warns of flooding as King Tides peak over Thanksgiving.",
    "UK military chiefs write to 100,000 reservists: prepare for a war call-up.",
    "OPEC+ meets 29 Nov on 2027 output; UAE out, Iraq and Kazakhstan seek more.",
    "UK-EU treaty has a 10-year termination clause, BBC understands.",
    "Angelina Jolie and Brad Pitt settle their fight over the French winery.",
    "Eurostar cancels seven services after a staff strike; London-Paris hit.",
]


def paper():
    img = Image.new("RGB", (W, H), PAPER)
    img = mottle(img, n=34, alpha=20)
    img = grain(img, 0.07)
    return img


def main():
    page = paper()
    dr = ImageDraw.Draw(page)

    # ---- masthead
    dr.line([(MARGIN, 14), (W - MARGIN, 14)], fill=RULE, width=3)
    title = "THE WORLD IN ONE DAY"
    tw = F_TITLE.getlength(title)
    dr.text(((W - tw) / 2, 18), title, font=F_TITLE, fill=INK)
    date = "THURSDAY  26  NOVEMBER  2026"
    dw = F_DATE.getlength(date)
    dr.text(((W - dw) / 2, 92), date, font=F_DATE, fill=INK)
    sub = "Thirty stories from one day \u2014 reported by Reuters, AP, BBC and others"
    sw = F_SUB.getlength(sub)
    dr.text(((W - sw) / 2, 120), sub, font=F_SUB, fill=(90, 78, 66))
    dr.line([(MARGIN, 142), (W - MARGIN, 142)], fill=RULE, width=2)
    dr.line([(MARGIN, 146), (W - MARGIN, 146)], fill=RULE, width=1)

    # ---- big 3
    colw = 307
    gap = (W - 2 * MARGIN - 3 * colw) // 2
    xs = [MARGIN + i * (colw + gap) for i in range(3)]
    y_img = 154
    big_bottom = 0
    for (kicker, head, deck, painter), x in zip(BIG, xs):
        sc = painter()
        page.paste(sc, (x, y_img))
        dr.rectangle([x, y_img, x + colw - 1, y_img + 149], outline=(60, 50, 40), width=1)
        y = y_img + 158
        dr.text((x, y), kicker, font=F_KICK, fill=RED)
        y += 19
        y = draw_lines(dr, wrap(head, F_HEAD, colw), x, y, F_HEAD, INK, 27)
        y += 2
        y = draw_lines(dr, wrap(deck, F_DECK, colw), x, y, F_DECK, (70, 62, 52), 17)
        big_bottom = max(big_bottom, y)
    y = big_bottom + 8
    dr.line([(MARGIN, y), (W - MARGIN, y)], fill=RULE, width=1)

    # ---- more from thursday
    y += 8
    dr.text((MARGIN, y), "MORE FROM THURSDAY", font=F_SECT, fill=INK)
    dr.line([(MARGIN + 190, y + 10), (W - MARGIN, y + 10)], fill=(120, 105, 88), width=1)
    y += 24
    tile_h = 62
    for row in range(5):
        for col in range(3):
            n, t, b = TILES[row * 3 + col]
            x = xs[col]
            yy = y + row * tile_h
            icon = ICONS[n]()
            page.paste(icon, (x, yy))
            dr = ImageDraw.Draw(page)
            dr.rectangle([x, yy, x + 61, yy + 61], outline=(60, 50, 40), width=1)
            # number badge
            dr.ellipse([x - 8, yy + 20, x + 14, yy + 42], fill=RED)
            dr.text((x + 3, yy + 22), str(n), font=F_BADGE, fill=(246, 238, 220), anchor="ma")
            tx = x + 70
            ty = yy + 2
            ty = draw_lines(dr, wrap(t, F_TILE_T, colw - 70), tx, ty, F_TILE_T, INK, 18)
            draw_lines(dr, wrap(b, F_TILE_B, colw - 70), tx, ty + 1, F_TILE_B, (70, 62, 52), 14)
    y = y + 5 * tile_h + 4
    dr.line([(MARGIN, y), (W - MARGIN, y)], fill=RULE, width=1)

    # ---- also today
    y += 7
    dr.text((MARGIN, y), "ALSO TODAY", font=F_SECT, fill=INK)
    dr.line([(MARGIN + 120, y + 10), (W - MARGIN, y + 10)], fill=(120, 105, 88), width=1)
    y += 22
    colw2 = (W - 2 * MARGIN - 24) // 2
    for i, item in enumerate(ALSO):
        col = i % 2
        row = i // 2
        x = MARGIN + col * (colw2 + 24)
        yy = y + row * 24
        dr.polygon([(x + 2, yy + 2), (x + 8, yy + 7), (x + 2, yy + 12), (x - 4, yy + 7)],
                   fill=RED)
        draw_lines(dr, wrap(item, F_LIST, colw2 - 14), x + 14, yy, F_LIST, (52, 44, 36), 14)
    y = y + 6 * 24 + 3
    dr.line([(MARGIN, y), (W - MARGIN, y)], fill=RULE, width=2)

    # ---- footer
    y += 5
    dr.text((MARGIN, y),
            "Sources: Reuters, AP, BBC, Xinhua, KCNA via Reuters, Bloomberg Law, Fox Sports, NBC Sports.",
            font=F_FOOT, fill=(90, 78, 66))
    y += 14
    dr.text((MARGIN, y), "Scenes are illustrations drawn for this page, not photographs.",
            font=F_FOOT_I, fill=(90, 78, 66))
    y += 14
    datecheck = ("DATE CHECK: Chen Jining probe and Raytheon contract were Tue 24 Nov; tariff proposal, "
                 "FCC-SpaceX approval, US Iran alert, Australia tech law, Luma ruling, UCL matches and "
                 "Rams-Packers were Wed 25 Nov \u2014 everything else happened Thu 26 Nov 2026.")
    y = draw_lines(dr, wrap(datecheck, F_FOOT, W - 2 * MARGIN), MARGIN, y, F_FOOT, RED, 13)
    print("layout bottom y =", y)

    page.save(OUT, "PNG")
    print("wrote", OUT, page.size)


if __name__ == "__main__":
    main()
