"""Procedural animal skins for Battery Cat.

Generates flat vector-style clock-face animal heads that follow the same
layout contract as assets/cat-clock.png:
  - 512x512 canvas, genuine alpha transparency outside the silhouette
  - facial features small and high (above the dial ring)
  - generous blank cream dial circle in the center for the app-rendered
    battery percentage (no baked-in text/numbers)

Run `python skins.py` to (re)generate assets/skins/*.png. 'Kucing' reuses
the original hand-made assets/cat-clock.png and is not generated here.
"""
import os
import sys
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QImage, QPainter, QPen
from PySide6.QtWidgets import QApplication

from core import SKINS

SIZE = 512
INK = QColor('#512B1D')
CREAM = QColor('#FFF8EC')
RING = QColor('#EDB695')
BLUSH = QColor('#F0A08C')
WHITE = QColor('#FFFFFF')

DIAL_C = QPointF(256, 315)
DIAL_R = 132
HEAD_RECT = QRectF(84, 96, 344, 382)


def skin_path(name, root):
    """Filesystem path of a skin image. 'Kucing' is the original artwork."""
    root = Path(root)
    if name == 'Kucing':
        return root / 'assets' / 'cat-clock.png'
    return root / 'assets' / 'skins' / f'{name}.png'


def _canvas():
    img = QImage(SIZE, SIZE, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)
    return img


def _pen(color, width):
    pen = QPen(color)
    pen.setWidth(width)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    return pen


def _disc(p, cx, cy, r, fill, outline=None, outline_w=10):
    p.setBrush(QBrush(fill))
    p.setPen(_pen(outline, outline_w) if outline else Qt.PenStyle.NoPen)
    p.drawEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))


def _ellipse(p, rect, fill, outline=None, outline_w=10):
    p.setBrush(QBrush(fill))
    p.setPen(_pen(outline, outline_w) if outline else Qt.PenStyle.NoPen)
    p.drawEllipse(rect)


def _dial(p):
    """Blank cream clock face with peach rim. Must stay free of features."""
    _disc(p, DIAL_C.x(), DIAL_C.y(), DIAL_R, CREAM)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(_pen(RING, 12))
    p.drawEllipse(QRectF(DIAL_C.x() - DIAL_R, DIAL_C.y() - DIAL_R, DIAL_R * 2, DIAL_R * 2))


def _head(p, fur):
    _ellipse(p, HEAD_RECT, fur, INK, 10)


def _feet(p, fur):
    _ellipse(p, QRectF(122, 436, 70, 44), fur, INK, 8)
    _ellipse(p, QRectF(320, 436, 70, 44), fur, INK, 8)


def _blush(p, x, w=34, h=20, y=158):
    c = QColor(BLUSH)
    c.setAlpha(160)
    p.setBrush(QBrush(c))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QRectF(x, y, w, h))
    p.drawEllipse(QRectF(SIZE - x - w, y, w, h))


def _eyes(p, y=148, dx=50, r=10, color=INK):
    _disc(p, 256 - dx, y, r, color)
    _disc(p, 256 + dx, y, r, color)


def _nose(p, y=166, w=17, h=12, color=INK):
    p.setBrush(QBrush(color))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QRectF(256 - w / 2, y - h / 2, w, h))


def _smile(p, rect, color=INK, width=6):
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(_pen(color, width))
    # Lower-half arc of the rect = smile curve (verified visually).
    p.drawArc(rect, 195 * 16, 150 * 16)


def _whiskers(p, y0=156, gap=11, inner=182, outer=132):
    p.setPen(_pen(INK, 4))
    for i in range(3):
        y = y0 + i * gap
        p.drawLine(int(outer), int(y), int(inner), int(y + (i - 1) * 3))
        p.drawLine(int(SIZE - outer), int(y), int(SIZE - inner), int(y + (i - 1) * 3))


def _round_ear(p, cx, cy, r, fur, inner):
    _disc(p, cx, cy, r, fur, INK, 10)
    _disc(p, cx, cy, r * 0.48, inner)


def _bear_like(p, fur, inner_ear, dark=None):
    """Shared base for Beruang and Panda (round ears + round head)."""
    ear = dark or fur
    _round_ear(p, 132, 104, 50, ear, inner_ear if dark is None else ear)
    _round_ear(p, 380, 104, 50, ear, inner_ear if dark is None else ear)
    _head(p, fur)
    _dial(p)
    _feet(p, fur)


def _beruang(p):
    fur = QColor('#C89B6D')
    _bear_like(p, fur, QColor('#F0C49C'))
    _blush(p, 168)
    _eyes(p)
    _nose(p)
    _smile(p, QRectF(226, 166, 60, 30))
    _whiskers(p)


def _kelinci(p):
    fur = QColor('#F1ECE3')
    pink = QColor('#F3B7C4')
    for cx, tilt in ((178, -14), (334, 14)):
        for w, h, fill in ((72, 225, fur), (32, 148, pink)):
            p.save()
            p.translate(cx, 128)
            p.rotate(tilt)
            p.setBrush(QBrush(fill))
            p.setPen(_pen(INK, 9))
            p.drawEllipse(QRectF(-w / 2, -h / 2, w, h))
            p.restore()
    _head(p, fur)
    _dial(p)
    _feet(p, fur)
    _blush(p, 168)
    _eyes(p)
    _nose(p, color=QColor('#C96F7E'))
    _smile(p, QRectF(228, 164, 56, 28))
    _whiskers(p)


def _katak(p):
    fur = QColor('#82B566')
    for cx in (168, 344):
        _disc(p, cx, 108, 48, fur, INK, 10)
        _disc(p, cx, 108, 21, WHITE)
        _disc(p, cx + (4 if cx < 256 else -4), 110, 10, INK)
    _head(p, fur)
    _dial(p)
    _feet(p, fur)
    _blush(p, 150, y=164)
    p.setBrush(QBrush(INK))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QRectF(242, 136, 8, 8))
    p.drawEllipse(QRectF(262, 136, 8, 8))
    _smile(p, QRectF(198, 128, 116, 56), width=7)


def _panda(p):
    fur = QColor('#F6F3ED')
    dark = QColor('#38322E')
    _bear_like(p, fur, fur, dark=dark)
    for cx, tilt in ((208, -20), (304, 20)):
        p.save()
        p.translate(cx, 150)
        p.rotate(tilt)
        p.setBrush(QBrush(dark))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QRectF(-32, -22, 64, 44))
        p.restore()
        _disc(p, cx, 148, 9, WHITE)
        _disc(p, cx, 148, 4, dark)
    _blush(p, 168)
    _nose(p, color=dark)
    _smile(p, QRectF(228, 166, 56, 28))


BUILDERS = {
    'Beruang': _beruang,
    'Kelinci': _kelinci,
    'Katak': _katak,
    'Panda': _panda,
}


def render(name):
    img = _canvas()
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    BUILDERS[name](p)
    p.end()
    return img


def main():
    # Offscreen rendering is only needed when running this module as a
    # script. It must NOT leak into importers: app.py imports skin_path
    # from here, and a top-level QT_QPA_PLATFORM would force the shipped
    # app onto the offscreen platform (invisible ghost process).
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    app = QApplication([])
    root = Path(__file__).resolve().parent
    outdir = root / 'assets' / 'skins'
    outdir.mkdir(parents=True, exist_ok=True)
    for name in SKINS:
        if name not in BUILDERS:
            continue
        path = outdir / f'{name}.png'
        render(name).save(str(path), 'PNG')
        print(f'{path.relative_to(root)}  {path.stat().st_size} bytes')
    app.quit()


if __name__ == '__main__':
    sys.exit(main())
