"""Generate the home screen icons.

Kept as a script rather than committing only the PNGs, so the icons can be changed
without a graphics editor and without wondering where the binaries came from.

Usage: python3 make_icon.py
"""

import pathlib
import struct
import zlib

ROOT = pathlib.Path(__file__).parent
BACKGROUND = (0x8D, 0x20, 0x27)
FOREGROUND = (0xFF, 0xFF, 0xFF)
SIZES = (180, 512)

# 5x7 glyphs, one string per row, '#' is ink
GLYPHS = {
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "M": ["#...#", "##.##", "#.#.#", "#...#", "#...#", "#...#", "#...#"],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
}
WORD = "COMPI"
GLYPH_W, GLYPH_H, GAP = 5, 7, 1
CELLS_W = len(WORD) * GLYPH_W + (len(WORD) - 1) * GAP
TEXT_WIDTH_RATIO = 0.80


def render(size):
    cell = max(1, round(size * TEXT_WIDTH_RATIO / CELLS_W))
    text_w, text_h = CELLS_W * cell, GLYPH_H * cell
    origin_x, origin_y = (size - text_w) // 2, (size - text_h) // 2

    rows = [bytearray(BACKGROUND * size) for _ in range(size)]
    for index, letter in enumerate(WORD):
        left = origin_x + index * (GLYPH_W + GAP) * cell
        for gy, line in enumerate(GLYPHS[letter]):
            for gx, mark in enumerate(line):
                if mark != "#":
                    continue
                for py in range(origin_y + gy * cell, origin_y + (gy + 1) * cell):
                    start = (left + gx * cell) * 3
                    rows[py][start:start + cell * 3] = bytes(FOREGROUND) * cell
    return rows


def write_png(path, rows):
    size = len(rows)
    raw = b"".join(b"\x00" + bytes(row) for row in rows)

    def chunk(tag, payload):
        body = tag + payload
        return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body))

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def main():
    for size in SIZES:
        path = ROOT / f"icon-{size}.png"
        write_png(path, render(size))
        print(f"wrote {path.name} ({path.stat().st_size // 1024 or 1} KB)")


if __name__ == "__main__":
    main()
