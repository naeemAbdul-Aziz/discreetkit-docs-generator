"""Cover page / investor pack cover template."""
import os
from templates.common import load_brand_colors, draw_header, draw_footer, add_watermark
from templates.common import canvas, A4


def generate(output_path=None):
    brand = load_brand_colors()
    w, h = A4
    if output_path is None:
        output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "cover_page.pdf")

    c = canvas.Canvas(output_path, pagesize=A4)
    # Strong cover—big title
    draw_header(c, brand)
    c.setFillColor(brand["warm_brown"])  # type: ignore
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(w / 2.0, h / 2.0 + 20, "Access DiscreetKit")
    c.setFont("Helvetica", 14)
    c.drawCentredString(w / 2.0, h / 2.0 - 10, "Investor Pack")

    add_watermark(c, brand)
    draw_footer(c, brand)
    c.showPage()
    c.save()
