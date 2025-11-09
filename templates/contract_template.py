"""General contract template (placeholder)."""
import os
from templates.common import canvas, A4
from templates.common import load_brand_colors, draw_header, draw_footer, add_watermark


def generate(output_path=None):
    brand = load_brand_colors()
    w, h = A4
    if output_path is None:
        output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "contract.pdf")

    c = canvas.Canvas(output_path, pagesize=A4)
    draw_header(c, brand, title="Contract")
    add_watermark(c, brand)

    c.setFillColor(brand["warm_brown"])  # type: ignore
    try:
        c.setFont("Satoshi", 11)
    except Exception:
        c.setFont("Helvetica", 11)
    c.drawString(40, h - 120, "[General contract placeholder — replace with agreement text]")

    draw_footer(c, brand)
    c.showPage()
    c.save()
