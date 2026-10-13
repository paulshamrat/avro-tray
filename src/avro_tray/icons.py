"""
Icon generation module for Avro Tray Indicator.
Procedurally renders crisp, high-DPI badges for system tray top-panels.
"""

from PyQt5 import QtGui, QtCore


def create_badge_icon(text: str, font_family: str, font_size: int,
                      bg_color: str, fg_color: str,
                      border_color: str = None,
                      dot_color: str = None,
                      size: int = 64) -> QtGui.QIcon:
    """
    Renders a high-resolution rounded badge icon.

    Args:
        text: Badge label (e.g. 'EN' or 'বাং')
        font_family: Font family name
        font_size: Point size of the font
        bg_color: Hex color string for background badge
        fg_color: Hex color string for label text
        border_color: Optional hex color for badge border
        dot_color: Optional accent dot color (e.g. red dot for BD / Avro branding)
        size: Pixel dimension (square)
    """
    pix = QtGui.QPixmap(size, size)
    pix.fill(QtCore.Qt.transparent)

    p = QtGui.QPainter(pix)
    p.setRenderHint(QtGui.QPainter.Antialiasing)
    p.setRenderHint(QtGui.QPainter.TextAntialiasing)

    # Outer rounded rectangle
    margin = 2.0
    rect = QtCore.QRectF(margin, margin, size - 2 * margin, size - 2 * margin)
    radius = size * 0.22

    p.setBrush(QtGui.QColor(bg_color))
    if border_color:
        p.setPen(QtGui.QPen(QtGui.QColor(border_color), 2.0))
    else:
        p.setPen(QtCore.Qt.NoPen)
    p.drawRoundedRect(rect, radius, radius)

    # Optional top-right indicator dot
    if dot_color:
        dot_radius = size * 0.08
        dot_x = size - margin - dot_radius - 4
        dot_y = margin + dot_radius + 4
        p.setBrush(QtGui.QColor(dot_color))
        p.setPen(QtCore.Qt.NoPen)
        p.drawEllipse(QtCore.QPointF(dot_x, dot_y), dot_radius, dot_radius)

    # Text rendering
    p.setPen(QtGui.QColor(fg_color))
    font = QtGui.QFont(font_family, font_size, QtGui.QFont.Bold)
    p.setFont(font)
    p.drawText(rect, QtCore.Qt.AlignCenter, text)
    p.end()

    return QtGui.QIcon(pix)


def get_english_icon() -> QtGui.QIcon:
    """Returns the English [EN] badge icon."""
    return create_badge_icon(
        text="EN",
        font_family="Sans",
        font_size=24,
        bg_color="#1D4ED8",  # Royal Blue
        fg_color="#FFFFFF",
        border_color="#60A5FA"
    )


def get_bangla_icon() -> QtGui.QIcon:
    """Returns the Bangla [বাং] badge icon with Avro red accent dot."""
    return create_badge_icon(
        text="বাং",
        font_family="Noto Sans Bengali",
        font_size=24,
        bg_color="#047857",  # Emerald Green
        fg_color="#FFFFFF",
        border_color="#34D399",
        dot_color="#EF4444"   # Crimson Red Dot
    )
