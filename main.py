#!/usr/bin/env python3
"""Front page of Friday 20 November 2026, drawn as one 1024x1024 PNG.

Pure Python standard library only (zlib + struct for the PNG writer),
so it runs in the grading sandbox with no network and no installs.
All text is set in a tiny 5x7 bitmap font defined below; all pictures
(cyclone spiral, flags, bridge) are drawn with the raster helpers.
Deterministic: no randomness, no clock, no network, no file reads
outside this program, so two runs write byte-identical files.

Stories (verified against Reuters / IMD / Sotheby's reporting):
  - Severe Cyclonic Storm Akvan makes landfall on India's east coast
    (Odisha-Andhra Pradesh) around noon, winds 90-100 km/h gusting 110.
  - Trump, Xi and Putin hold the first three-way summit of the three
    biggest nuclear powers in Shenzhen; a five-paragraph peace
    declaration; Trump says a nuclear-arms deal will be hard.
  - A Ukrainian strike on the Crimean Bridge disrupts rail traffic.
  - Van Gogh's "Chataigniers en fleurs" sells for a record $190.4m.
  - Nicholls' unbeaten 113 lifts New Zealand to 243-5 vs India.
"""

import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (246, 241, 230)
INK = (22, 22, 22)
RED = (166, 25, 46)
BLUE = (31, 78, 121)
TEAL = (15, 110, 110)
WHITE = (255, 255, 255)
SKY = (174, 205, 225)
GOLD = (232, 185, 32)

# ---------------------------------------------------------------- font ----
# A 5x7 bitmap font. Each glyph is 7 rows of 5 cells, '#' = ink.
# Lowercase letters sit on rows 2-6 (x-height) with descenders to row 6.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    "a": (".....", ".....", ".####", "....#", ".####", "#...#", ".###."),
    "b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    "c": (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    "d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    "e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    "f": ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
    "g": (".....", ".####", "#...#", "#...#", ".####", "....#", ".###."),
    "h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "i": ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
    "j": ("...#.", ".....", "..##.", "...#.", "...#.", "...#.", ".##.."),
    "k": ("#....", "#....", "#.#..", "#.#..", "##...", "#.#..", "#..#."),
    "l": (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    "n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    "p": (".....", "####.", "#...#", "#...#", "####.", "#....", "#...."),
    "q": (".....", ".####", "#...#", "#...#", ".####", "....#", "....#"),
    "r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    "s": (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    "t": (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    "u": (".....", ".....", "#...#", "#...#", "#...#", "#...#", ".###."),
    "v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "w": (".....", ".....", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    "y": (".....", "#...#", "#...#", "#...#", ".####", "....#", ".###."),
    "z": (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "...#.", "...#.", "..#..", "..#..", ".#...", "#...."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    "*": (".....", ".#.#.", ".###.", "#####", ".###.", ".#.#.", "....."),
    "°": (".###.", "#...#", "#...#", ".###.", ".....", ".....", "....."),
}

# Normalise fancy punctuation to glyphs we have.
NORMALISE = {
    "’": "'", "‘": "'", "“": '"', "”": '"',
    "—": "-", "–": "-", "·": ".", "•": "*",
}

for _ch, _rows in FONT.items():
    assert len(_rows) == 7, _ch
    for _row in _rows:
        assert len(_row) == 5, (_ch, _row)

BLANK = (".....",) * 7


def text_width(s, scale):
    """Pixel width of s at the given integer scale."""
    return len(s) * 6 * scale


def wrap(s, scale, max_width):
    """Greedy word wrap; returns a list of lines fitting max_width."""
    lines, cur = [], ""
    for word in s.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------ raster ------
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        self.rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def hline(self, x0, x1, y, c, thick=1):
        for yy in range(y, y + thick):
            for xx in range(x0, x1 + 1):
                self.set(xx, yy, c)

    def vline(self, x, y0, y1, c, thick=1):
        for xx in range(x, x + thick):
            for yy in range(y0, y1 + 1):
                self.set(xx, yy, c)

    def line(self, x0, y0, x1, y1, c, thick=1):
        """Bresenham line with a square brush of side `thick`."""
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err, x, y = dx - dy, x0, y0
        r = thick // 2
        while True:
            self.rect(x - r, y - r, thick, thick, c)
            if x == x1 and y == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def ring(self, cx, cy, r, c, thick=2):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - thick) ** 2 < d2 <= r * r:
                    self.set(xx, yy, c)

    def frame(self, x, y, w, h, c, thick=1):
        self.rect(x, y, w, thick, c)
        self.rect(x, y + h - thick, w, thick, c)
        self.rect(x, y, thick, h, c)
        self.rect(x + w - thick, y, thick, h, c)

    # -- text -------------------------------------------------------------
    def text(self, s, x, y, scale, c, align="left"):
        s = "".join(NORMALISE.get(ch, ch) for ch in s)
        w = text_width(s, scale)
        if align == "center":
            x -= w // 2
        elif align == "right":
            x -= w
        cx = x
        for ch in s:
            rows = FONT.get(ch, BLANK)
            for ry, row in enumerate(rows):
                for rx, cell in enumerate(row):
                    if cell == "#":
                        self.rect(cx + rx * scale, y + ry * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return w

    def para(self, s, x, y, scale, c, max_width, lh=None):
        if lh is None:
            lh = 7 * scale + 4
        for line in wrap(s, scale, max_width):
            self.text(line, x, y, scale, c)
            y += lh
        return y


# ------------------------------------------------------------- pictures ---
def draw_spiral(cv, cx, cy, max_r):
    """A cyclone seen from above: banded spiral arms around a red eye."""
    import math
    prev = None
    steps = 3 * 360 + 180
    for deg in range(steps + 1):
        a = math.radians(deg)
        r = 7 + deg * (max_r - 7) / steps
        x = int(cx + r * math.cos(a))
        y = int(cy + r * math.sin(a) * 0.92)
        col = BLUE if (deg // 180) % 2 == 0 else TEAL
        if prev is not None:
            cv.line(prev[0], prev[1], x, y, col, thick=5)
        prev = (x, y)
    cv.disc(cx, cy, 11, RED)
    cv.ring(cx, cy, 15, WHITE, thick=2)


def draw_flag_usa(cv, x, y, w, h):
    cv.rect(x, y, w, h, WHITE)
    for i in range(7):
        cv.rect(x, y + i * (h // 7), w, 2, RED)
    cw, ch = w * 2 // 5, h * 7 // 13
    cv.rect(x, y, cw, ch, BLUE)
    for dx in range(3, cw - 2, 8):
        for dy in range(3, ch - 2, 5):
            cv.rect(x + dx, y + dy, 2, 2, WHITE)


def draw_flag_china(cv, x, y, w, h):
    cv.rect(x, y, w, h, RED)
    cv.disc(x + 16, y + h // 2, 6, GOLD)
    for dx, dy in ((34, 4), (44, 9), (46, 18), (38, 24)):
        cv.disc(x + dx, y + dy, 2, GOLD)


def draw_flag_russia(cv, x, y, w, h):
    cv.rect(x, y, w, h // 3, WHITE)
    cv.rect(x, y + h // 3, w, h // 3, BLUE)
    cv.rect(x, y + 2 * h // 3, w, h - 2 * (h // 3), RED)


def draw_bridge(cv, x, y, w, h):
    """A bridge deck with a burst where the span is broken."""
    mid = x + w // 2
    cv.hline(x, mid - 12, y + h - 6, INK, thick=3)
    cv.hline(mid + 12, x + w, y + h - 6, INK, thick=3)
    cv.vline(x + 18, y + 4, y + h - 6, INK, thick=3)
    cv.vline(x + w - 20, y + 4, y + h - 6, INK, thick=3)
    cv.line(x + 18, y + h - 6, mid, y + 10, INK, thick=2)
    cv.line(x + w - 20, y + h - 6, mid, y + 10, INK, thick=2)
    for ang in range(0, 360, 45):
        import math
        r = 13
        a = math.radians(ang)
        cv.line(mid, y + 14,
                int(mid + r * math.cos(a)), int(y + 14 + r * math.sin(a)),
                RED, thick=2)
    cv.disc(mid, y + 14, 4, RED)


# ---------------------------------------------------------------- page ----
def build():
    cv = Canvas(W, H, PAPER)
    cv.frame(8, 8, W - 16, H - 16, INK, thick=2)
    cv.frame(16, 16, W - 32, H - 32, INK, thick=1)

    # Masthead.
    cv.text("THE WORLD TODAY", 512, 30, 10, INK, align="center")
    cv.hline(36, 988, 112, INK, thick=2)
    cv.text("FRIDAY, 20 NOVEMBER 2026", 512, 122, 4, INK, align="center")
    cv.text("THE DAY'S NEWS IN ONE IMAGE", 512, 156, 3, RED, align="center")
    cv.hline(36, 988, 188, INK, thick=2)

    # Lead story: Cyclone Akvan.
    cv.text("INDIA - SEVERE CYCLONE", 36, 202, 3, RED)
    cv.text("AKVAN SLAMS INTO", 36, 232, 5, INK)
    cv.text("INDIA'S EAST COAST", 36, 270, 5, INK)
    cv.para(
        "Severe Cyclonic Storm Akvan crosses the Odisha-Andhra Pradesh "
        "coast by noon, winds of 90-100 km/h gusting to 110. Heavy rain "
        "is forecast, schools shut, 1,000-plus teams deployed.",
        36, 320, 3, INK, 620)
    # Cyclone art, right of the lead.
    cv.frame(664, 202, 324, 268, INK, thick=1)
    draw_spiral(cv, 826, 322, 108)
    cv.text("ODISHA", 676, 212, 2, INK)
    cv.text("LANDFALL BY NOON", 978, 212, 2, RED, align="right")
    cv.text("BAY OF BENGAL", 826, 448, 2, BLUE, align="center")
    cv.hline(36, 988, 482, INK, thick=2)

    # Second story: the Shenzhen summit.
    cv.text("SHENZHEN - THE SUMMIT", 36, 494, 3, RED)
    cv.text("THREE LEADERS, ONE TABLE", 36, 524, 5, INK)
    cv.para(
        "Trump, Xi and Putin hold a first three-way summit in Shenzhen "
        "and issue a five-paragraph peace declaration. Trump says a "
        "nuclear-arms deal will be hard - but he will keep at it.",
        36, 568, 3, INK, 824)
    draw_flag_usa(cv, 872, 568, 116, 30)
    draw_flag_china(cv, 872, 608, 116, 30)
    draw_flag_russia(cv, 872, 648, 116, 30)
    cv.hline(36, 988, 705, INK, thick=2)

    # Third story: the Crimean Bridge.
    cv.text("UKRAINE - WAR", 36, 717, 3, RED)
    cv.text("RAIL LINK TO CRIMEA CUT", 36, 747, 5, INK)
    draw_bridge(cv, 790, 742, 198, 40)
    cv.para(
        "A Ukrainian strike on the Crimean Bridge disrupts railway "
        "traffic to the peninsula, as the war grinds on into another "
        "winter.",
        36, 791, 3, INK, 952)
    cv.hline(36, 988, 878, INK, thick=2)

    # Also today.
    cv.text("ALSO TODAY", 36, 890, 3, RED)
    cv.para(
        "A record Van Gogh fetches $190.4m at Sotheby's. Nicholls' 113* "
        "lifts New Zealand to 243-5.",
        36, 919, 3, INK, 952)
    cv.text("Compiled from Reuters, the India Meteorological Department "
            "and Sotheby's", 512, 982, 2, INK, align="center")
    return cv


def png_bytes(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    cv = build()
    data = png_bytes(cv)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()
