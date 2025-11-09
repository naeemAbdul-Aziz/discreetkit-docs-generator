"""Board resolution generator (placeholder)."""
import os
from templates.common import canvas, A4  # use common stubs/real
from templates.common import load_brand_colors, draw_header, draw_footer, add_watermark


def generate(output_path=None):
    brand = load_brand_colors()
    w, h = A4
    if output_path is None:
        output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "board_resolution.pdf")

    c = canvas.Canvas(output_path, pagesize=A4)
    draw_header(c, brand, title="Board Resolution")
    add_watermark(c, brand)

    c.setFillColor(brand["warm_brown"])  # guaranteed by loader
    try:
        c.setFont("Satoshi", 11)
    except Exception:
        c.setFont("Helvetica", 11)
    c.drawString(40, h - 120, "[Board resolution content placeholder]")

    draw_footer(c, brand)
    c.showPage()
    c.save()
