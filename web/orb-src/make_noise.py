"""Write a tileable grayscale Perlin-style noise PNG for the Orb shader. Standard library only."""
import math, random, struct, sys, zlib

SIZE, OCTAVES = 256, 4
random.seed(2026)


def lattice(period):
    return [[random.random() for _ in range(period)] for _ in range(period)]


def smooth(t):
    return t * t * (3 - 2 * t)


def sample(grid, period, x, y):
    x0, y0 = int(x) % period, int(y) % period
    x1, y1 = (x0 + 1) % period, (y0 + 1) % period
    fx, fy = smooth(x - int(x)), smooth(y - int(y))
    top = grid[y0][x0] + (grid[y0][x1] - grid[y0][x0]) * fx
    bottom = grid[y1][x0] + (grid[y1][x1] - grid[y1][x0]) * fx
    return top + (bottom - top) * fy


grids = [(lattice(4 * 2 ** o), 4 * 2 ** o, 0.5 ** o) for o in range(OCTAVES)]
total = sum(weight for _, _, weight in grids)
rows = bytearray()
for y in range(SIZE):
    rows.append(0)
    for x in range(SIZE):
        value = sum(sample(g, p, x * p / SIZE, y * p / SIZE) * w for g, p, w in grids) / total
        rows.append(max(0, min(255, round((0.5 + (value - 0.5) * 1.6) * 255))))


def chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))


png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", SIZE, SIZE, 8, 0, 0, 0, 0)) \
    + chunk(b"IDAT", zlib.compress(bytes(rows), 9)) + chunk(b"IEND", b"")
open(sys.argv[1], "wb").write(png)
