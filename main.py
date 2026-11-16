#!/usr/bin/env python3
"""make.fun ai-excited-01 entry (rebuild, session 2).

Draws, from scratch with the standard library only, one 768x768 image:
a colossal wave bursting OUT of a tilted golden picture frame, a tiny boat
riding its crest, a gold sun blazing behind the curl. Deep indigo, white
foam and gold: one diagonal, one focal moment, readable at small size.

Run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
Writes $MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png).
Deterministic: no randomness, no time, no network. Pure zlib+struct PNG.
"""

import math
import os
import struct
import zlib

W = 768
H = 768

# ---- palette ---------------------------------------------------------------
SKY_TOP = (16, 22, 74)
SKY_MID = (30, 48, 120)
SKY_LOW = (58, 84, 158)
GOLD = (255, 190, 60)
GOLD_DEEP = (232, 140, 30)
GOLD_PALE = (255, 226, 140)
WAVE_DEEP = (10, 52, 110)
WAVE_MID = (16, 96, 158)
WAVE_LITE = (38, 150, 196)
HOLLOW = (30, 118, 178)      # lit interior of the curl, not a dark blob
HOLLOW_DARK = (18, 82, 142)
FOAM = (245, 250, 255)
FOAM_SH = (178, 214, 238)
BOAT_RED = (214, 48, 49)
BOAT_DARK = (40, 24, 20)

# ---- canvas ----------------------------------------------------------------
buf = bytearray(W * H * 3)


def set_px(x, y, r, g, b):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = r
        buf[i + 1] = g
        buf[i + 2] = b


def blend_px(x, y, r, g, b, a):
    """Blend colour over canvas with alpha a (0..1)."""
    if 0 <= x < W and 0 <= y < H and a > 0.0:
        i = (y * W + x) * 3
        if a >= 1.0:
            buf[i] = r
            buf[i + 1] = g
            buf[i + 2] = b
        else:
            buf[i] = int(r * a + buf[i] * (1.0 - a))
            buf[i + 1] = int(g * a + buf[i + 1] * (1.0 - a))
            buf[i + 2] = int(b * a + buf[i + 2] * (1.0 - a))


def lerp(a, b, t):
    return int(a + (b - a) * t)


def lerp3(c1, c2, t):
    return (lerp(c1[0], c2[0], t), lerp(c1[1], c2[1], t), lerp(c1[2], c2[2], t))


def fill_poly(points, colour):
    """Scanline-fill a polygon (list of (x, y)). Flat colour, clean edges."""
    if not points:
        return
    ys = [p[1] for p in points]
    y0 = max(0, int(math.ceil(min(ys))))
    y1 = min(H - 1, int(math.floor(max(ys))))
    n = len(points)
    r, g, b = colour
    for y in range(y0, y1 + 1):
        xs = []
        for i in range(n):
            x1, y1p = points[i]
            x2, y2p = points[(i + 1) % n]
            if (y1p <= y < y2p) or (y2p <= y < y1p):
                t = (y - y1p) / (y2p - y1p)
                xs.append(x1 + t * (x2 - x1))
        if len(xs) < 2:
            continue
        xs.sort()
        xa = max(0, int(math.ceil(xs[0])))
        xb = min(W - 1, int(math.floor(xs[-1])))
        base = (y * W + xa) * 3
        for x in range(xa, xb + 1):
            buf[base] = r
            buf[base + 1] = g
            buf[base + 2] = b
            base += 3


def fill_circle(cx, cy, rad, colour, alpha=1.0):
    r0, g0, b0 = colour
    x0 = max(0, int(cx - rad))
    x1 = min(W - 1, int(cx + rad))
    y0 = max(0, int(cy - rad))
    y1 = min(H - 1, int(cy + rad))
    rr = rad * rad
    for y in range(y0, y1 + 1):
        dy = y - cy
        dx = math.sqrt(max(0.0, rr - dy * dy))
        xa = max(x0, int(cx - dx))
        xb = min(x1, int(cx + dx))
        for x in range(xa, xb + 1):
            blend_px(x, y, r0, g0, b0, alpha)


def hash01(n):
    """Deterministic pseudo-random in [0,1) from an integer seed."""
    v = (n * 2654435761) & 0xFFFFFFFF
    v ^= v >> 15
    v = (v * 2246822519) & 0xFFFFFFFF
    v ^= v >> 13
    return (v & 0xFFFFFF) / 16777216.0


# ---- PNG encoder -----------------------------------------------------------
def write_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        raw += buf[y * W * 3:(y + 1) * W * 3]

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        c += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)



# ---- sky, sun, stars -------------------------------------------------------
def draw_sky():
    # Vertical gradient, precomputed per row (fast: one pass, no per-px math).
    for y in range(H):
        t = y / (H - 1)
        if t < 0.45:
            c = lerp3(SKY_TOP, SKY_MID, t / 0.45)
        else:
            c = lerp3(SKY_MID, SKY_LOW, (t - 0.45) / 0.55)
        base = y * W * 3
        r, g, b = c
        for x in range(W):
            buf[base] = r
            buf[base + 1] = g
            buf[base + 2] = b
            base += 3


def draw_sun():
    # Blazing gold sun behind the wave crest: glow disc + solid core + rays.
    cx, cy = 545, 235
    # Wide soft glow (radial falloff, clipped to a box).
    for y in range(30, 460):
        for x in range(330, 768):
            d = math.hypot(x - cx, y - cy)
            if d < 260:
                a = max(0.0, 1.0 - d / 260.0) ** 2 * 0.55
                blend_px(x, y, 255, 200, 90, a)
    # Solid sun disc with a hot core.
    fill_circle(cx, cy, 92, GOLD)
    fill_circle(cx, cy, 62, GOLD_PALE)
    fill_circle(cx, cy, 34, (255, 244, 200))


def draw_stars():
    # Sparse deterministic sparkles in the upper sky only.
    for i in range(90):
        x = int(hash01(i * 3 + 1) * W)
        y = int(hash01(i * 3 + 2) * 300)
        s = hash01(i * 3 + 3)
        if s < 0.55:
            continue
        r = 1 if s < 0.85 else 2
        fill_circle(x, y, r, (255, 255, 255), 0.9 if s > 0.9 else 0.55)


# ---- the broken picture frame ----------------------------------------------
def draw_frame():
    # Only the top and left bars of a tilted golden frame survive, lower-left:
    # the wave has smashed through the other two sides and pours out over
    # them. Drawn AFTER the wave so the bars cut across it in the foreground.
    # Bars are wider and brighter than a plain frame so the twist reads:
    # a thick gold edge, a pale highlight stripe, and a dark inner edge.
    # Top bar: from upper-left corner to upper-right corner.
    fill_poly([(48, 408), (486, 348), (502, 402), (60, 462)], GOLD_DEEP)
    fill_poly([(48, 408), (486, 348), (494, 372), (56, 432)], GOLD)
    fill_poly([(56, 424), (488, 364), (490, 372), (58, 432)], GOLD_PALE)
    # Left bar: from upper-left corner down to the bottom edge.
    fill_poly([(48, 408), (60, 462), (148, 768), (100, 768)], GOLD_DEEP)
    fill_poly([(66, 442), (78, 460), (160, 768), (122, 768)], GOLD)
    fill_poly([(74, 448), (82, 458), (146, 768), (128, 768)], GOLD_PALE)
    # Corner studs where the surviving bars meet, plus a stud mid-bar.
    for cx, cy in [(54, 435), (494, 375)]:
        fill_circle(cx, cy, 11, GOLD_PALE)
    fill_circle(54, 435, 5, GOLD_DEEP)
    fill_circle(118, 640, 8, GOLD_PALE)
    fill_circle(118, 640, 4, GOLD_DEEP)


# ---- the wave ---------------------------------------------------------------
def crest_y(x):
    """Top edge of the wave body: rises steeply left->right, curls at top."""
    t = x / W
    # Base diagonal sweep + a big swell near the crest.
    y = 640 - 430 * t - 70 * math.sin(t * 2.6) - 46 * math.sin(t * 5.1 + 0.7)
    return y


def draw_wave():
    # Main body: fill from crest down to the bottom, vertical gradient.
    for x in range(W):
        cy = crest_y(x)
        y0 = max(0, int(cy))
        for y in range(y0, H):
            t = (y - y0) / max(1, H - y0)
            if t < 0.35:
                c = lerp3(WAVE_LITE, WAVE_MID, t / 0.35)
            else:
                c = lerp3(WAVE_MID, WAVE_DEEP, (t - 0.35) / 0.65)
            i = (y * W + x) * 3
            buf[i], buf[i + 1], buf[i + 2] = c
    # Curling lip: a tube rolling over at the top-right crest, drawn as
    # overlapping discs along a quarter-circle hook so it reads as one
    # continuous rolling tube, not stacked blobs.
    for i in range(17):
        t = i / 16.0
        ang = -0.35 + t * 1.85  # sweep from upper-left to lower-right
        cx = 600 + math.cos(ang) * 62
        cy = 218 + math.sin(ang) * 62
        fill_circle(int(cx), int(cy), 30, WAVE_LITE)
    # Lit inner hollow of the curl: mid-blue discs (not a dark blob), with
    # a thin gold rim where sunlight catches the tube's inner edge, plus
    # foam flecks inside so the hollow reads as water, not shadow.
    for i in range(11):
        t = i / 10.0
        ang = 0.15 + t * 1.45
        cx = 600 + math.cos(ang) * 40
        cy = 218 + math.sin(ang) * 40
        fill_circle(int(cx), int(cy), 17, HOLLOW)
    for i in range(7):
        t = i / 6.0
        ang = 0.15 + t * 1.45
        cx = 600 + math.cos(ang) * 24
        cy = 218 + math.sin(ang) * 24
        fill_circle(int(cx), int(cy), 9, HOLLOW_DARK)
    for i in range(9):
        t = i / 8.0
        ang = 0.3 + t * 1.2
        cx = 600 + math.cos(ang) * 52
        cy = 218 + math.sin(ang) * 52
        fill_circle(int(cx), int(cy), 5, GOLD_PALE, 0.85)
    for i in range(10):
        a = hash01(i * 7 + 3) * 6.28
        d = hash01(i * 7 + 5) * 26
        fill_circle(int(600 + math.cos(a) * d), int(218 + math.sin(a) * d),
                    3, FOAM, 0.9)
    # Smooth foam band hugging the crest edge: a clean band polygon whose
    # thickness swells gently (sine-based), plus sparse round foam bumps.
    top = []
    bot = []
    for x in range(0, W + 1, 8):
        cy = crest_y(x)
        th = 14 + 9 * math.sin(x * 0.021 + 0.8) + 5 * math.sin(x * 0.047)
        top.append((x, cy - th))
        bot.append((x, cy + 6))
    fill_poly(top + bot[::-1], FOAM)
    for i in range(46):
        x = int(hash01(i * 13 + 5) * W)
        cy = crest_y(x)
        r = 4 + int(hash01(i * 13 + 9) * 9)
        fill_circle(x, int(cy) - 8 - int(hash01(i * 13 + 2) * 10), r, FOAM)
    # White foam cap on the curl tube.
    for i in range(9):
        t = i / 8.0
        ang = -0.35 + t * 1.35
        cx = 600 + math.cos(ang) * 62
        cy = 218 + math.sin(ang) * 62
        fill_circle(int(cx), int(cy) - 16, 15, FOAM)
    # Short foam streaks low on the wave body so the big blue face is not
    # one flat sheet: thin diagonal dashes, faint, following the swell.
    for i in range(12):
        x0 = 180 + int(hash01(i * 17 + 1) * 480)
        y0 = 470 + int(hash01(i * 17 + 2) * 260)
        ln = 40 + int(hash01(i * 17 + 3) * 70)
        th = 2 + (i % 2)
        dx, dy = 0.9 * ln, -0.32 * ln
        pts = [(x0, y0 - th), (x0 + dx, y0 + dy - th),
               (x0 + dx, y0 + dy + th), (x0, y0 + th)]
        fill_poly(pts, FOAM_SH)



# ---- spray, speed lines, boat ----------------------------------------------
def draw_spray():
    # Explosive spray bursting off the crest toward the sun: dots + streaks.
    for i in range(240):
        a = hash01(i * 5 + 1) * 1.9 - 0.35  # angle, mostly up-right
        d = 40 + hash01(i * 5 + 2) * 210
        cx = 618 + math.cos(a) * d * 0.9
        cy = 205 - math.sin(a) * d * 0.75
        r = 1 + int(hash01(i * 5 + 3) * 4)
        col = FOAM if hash01(i * 5 + 4) > 0.25 else GOLD_PALE
        fill_circle(int(cx), int(cy), r, col, 0.95)
    # Long spray streaks fanning off the lip.
    for i in range(14):
        a = -0.15 - i * 0.085
        x0, y0 = 640, 190
        x1 = x0 + math.cos(a) * 190
        y1 = y0 + math.sin(a) * 190
        wdt = 3 + (i % 3)
        fill_poly(
            [(x0, y0 - wdt), (x1, y1 - wdt), (x1, y1 + wdt), (x0, y0 + wdt)],
            FOAM,
        )


def draw_speed_lines():
    # Diagonal motion streaks converging on the crest from the lower left.
    for i in range(16):
        x0 = 40 + int(hash01(i * 11 + 1) * 420)
        y0 = 560 + int(hash01(i * 11 + 2) * 200)
        ln = 90 + int(hash01(i * 11 + 3) * 150)
        th = 2 + (i % 3)
        col = FOAM if i % 3 else GOLD_PALE
        # Streak as a thin quad along the -35 degree diagonal.
        dx, dy = 0.82 * ln, -0.57 * ln
        pts = [(x0, y0 - th), (x0 + dx, y0 + dy - th),
               (x0 + dx, y0 + dy + th), (x0, y0 + th)]
        fill_poly(pts, col)


def draw_boat():
    # Tiny boat riding the crest near the curl: hull + red sail + gold flag.
    # Crest point on the wave near x=520.
    bx, by = 520, int(crest_y(520)) - 6
    # Sail: bold red triangle leaning into the wind.
    fill_poly([(bx + 2, by - 58), (bx + 2, by - 6), (bx + 40, by - 6)], BOAT_RED)
    fill_poly([(bx - 2, by - 46), (bx - 2, by - 6), (bx - 30, by - 6)], GOLD_PALE)
    # Mast.
    fill_poly([(bx - 1, by - 60), (bx + 2, by - 60), (bx + 2, by - 2), (bx - 1, by - 2)], BOAT_DARK)
    # Hull: dark crescent boat.
    fill_poly([(bx - 34, by - 6), (bx + 44, by - 6), (bx + 30, by + 12), (bx - 20, by + 12)], BOAT_DARK)
    fill_poly([(bx - 34, by - 6), (bx + 44, by - 6), (bx + 38, by + 2), (bx - 28, by + 2)], (90, 50, 36))
    # Gold flag at the mast top.
    fill_poly([(bx + 2, by - 60), (bx + 20, by - 54), (bx + 2, by - 48)], GOLD)
    # White wake curl under the hull.
    fill_circle(bx - 8, by + 8, 7, FOAM)
    fill_circle(bx + 12, by + 10, 5, FOAM)


def draw_vignette():
    # Gentle darkening at the corners only, to push the eye to the crest.
    cx, cy = W / 2, H / 2
    for y in range(H):
        for x in range(W):
            d = math.hypot((x - cx) / (W / 2), (y - cy) / (H / 2))
            if d > 0.92:
                a = min(0.28, (d - 0.92) * 1.1)
                blend_px(x, y, 4, 6, 24, a)


def main():
    draw_sky()
    draw_stars()
    draw_sun()
    draw_wave()
    draw_frame()
    draw_spray()
    draw_speed_lines()
    draw_boat()
    draw_vignette()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = write_png(path)
    print(f"wrote {path} ({size} bytes)")


if __name__ == "__main__":
    main()
