"""สร้างไอคอนเว็บ (favicon / ไอคอนหน้าจอโฮม) ลงโฟลเดอร์ icons/

ไม่ต้องลงไลบรารีเพิ่ม: วาดรูปทรงเองแบบ supersampling แล้วเขียน PNG ด้วย zlib
รัน: python tools/make_icons.py
แก้สีหรือรูปทรงที่ SHAPES แล้วรันใหม่ (favicon.svg สร้างจากข้อมูลชุดเดียวกัน)
"""
import math
import struct
import zlib
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "icons"
BG = "#5f3c1f"  # น้ำตาลไม้ สีเดียวกับปุ่มชั้นคู่มือ

# รูปทรงในกรอบ 24x24 แบบเดียวกับไอคอนปุ่ม "ชั้นคู่มือ": (x, y, w, h, rx, สี, หมุนกี่องศา)
SHAPES = [
    (3, 6, 5, 10, 1, "#d9653b", 0),      # กล่องเกมสีส้มอิฐ
    (9.5, 9, 5, 7, 1, "#f0c869", 0),     # กล่องเตี้ยสีทอง
    (16, 4, 5, 12, 1, "#5fa39a", 8),     # กล่องเอียงสีเขียวหัวเป็ด
    (1, 17, 22, 3, 1, "#f6ecd9", 0),     # ไม้ชั้นสีครีม
]
# แถบฉลากบนกล่อง (สีครีมโปร่ง) ให้ดูเป็นกล่องเกม
LABELS = [(3, 8, 5, 1.4, 0), (9.5, 10.6, 5, 1.2, 0), (16, 6, 5, 1.4, 8)]


def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def layout(size, pad):
    """แปลงพิกัดกรอบ 24 → พิกเซล ให้ภาพกลางอยู่ในพื้นที่ปลอดภัย (pad = สัดส่วนขอบ)"""
    s = size * (1 - 2 * pad) / 22
    ox = (size - 22 * s) / 2 - 1 * s
    oy = (size - 16 * s) / 2 - 4 * s
    return s, ox, oy


def items():
    for x, y, w, h, rx, c, rot in SHAPES:
        yield x, y, w, h, rx, hex_rgb(c), 1.0, rot
    for x, y, w, h, rot in LABELS:
        yield x, y, w, h, 0, (246, 236, 217), 0.55, rot


def inside(px, py, x, y, w, h, rx, rot):
    if rot:
        cx, cy = 18.5, 10  # หมุนรอบจุดเดียวกับ SVG rotate(8 18.5 10)
        a = -math.radians(rot)
        dx, dy = px - cx, py - cy
        px, py = cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a)
    if not (x <= px <= x + w and y <= py <= y + h):
        return False
    if rx:
        qx = min(px - x, x + w - px)
        qy = min(py - y, y + h - py)
        if qx < rx and qy < rx:
            return (rx - qx) ** 2 + (rx - qy) ** 2 <= rx * rx
    return True


def render(size, pad, ss=4):
    s, ox, oy = layout(size, pad)
    bg = hex_rgb(BG)
    shapes = list(items())
    rows = []
    for j in range(size):
        row = bytearray([0])
        for i in range(size):
            acc = [0.0, 0.0, 0.0]
            for sj in range(ss):
                for si in range(ss):
                    gx = ((i + (si + .5) / ss) - ox) / s
                    gy = ((j + (sj + .5) / ss) - oy) / s
                    col = list(bg)
                    for x, y, w, h, rx, c, alpha, rot in shapes:
                        if inside(gx, gy, x, y, w, h, rx, rot):
                            col = [col[k] * (1 - alpha) + c[k] * alpha for k in range(3)]
                    for k in range(3):
                        acc[k] += col[k]
            row += bytes(round(v / (ss * ss)) for v in acc)
        rows.append(bytes(row))
    raw = b"".join(rows)

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def svg():
    s, ox, oy = layout(64, 0.08)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">',
             f'<rect width="64" height="64" rx="14" fill="{BG}"/>',
             f'<g transform="translate({ox:.2f} {oy:.2f}) scale({s:.4f})">']
    for x, y, w, h, rx, c, alpha, rot in items():
        fill = "#%02x%02x%02x" % c
        t = ' transform="rotate(8 18.5 10)"' if rot else ""
        op = f' fill-opacity="{alpha}"' if alpha < 1 else ""
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{op}{t}/>')
    parts.append("</g></svg>\n")
    return "".join(parts)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "favicon.svg").write_text(svg(), encoding="utf-8")
    # ไอคอนหน้าจอโฮมเว้นขอบ 18% ให้รอดการตัดมุมของ iOS/Android (maskable)
    for name, size, pad in [("favicon-32.png", 32, 0.04), ("apple-touch-icon.png", 180, 0.18),
                            ("icon-192.png", 192, 0.18), ("icon-512.png", 512, 0.18)]:
        (OUT / name).write_bytes(render(size, pad, ss=4 if size <= 192 else 3))
        print("ok", name)
