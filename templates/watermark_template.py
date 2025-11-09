"""Blank A4 with watermark."""
import os
from templates.common import canvas, A4
from templates.common import load_brand_colors, draw_header, draw_footer, add_watermark


def generate(output_path=None):
    brand = load_brand_colors()
    w, h = A4
    if output_path is None:
        output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "watermark_a4.pdf")

    c = canvas.Canvas(output_path, pagesize=A4)
    draw_header(c, brand)
    add_watermark(c, brand)

    # empty body — just ensure footer
    draw_footer(c, brand)
    c.showPage()
    c.save()
