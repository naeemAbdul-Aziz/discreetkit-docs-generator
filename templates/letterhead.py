"""Letterhead template generator."""
import os
from typing import cast
from datetime import datetime
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.colors import Color
    from reportlab.pdfgen.textobject import PDFTextObject
except Exception:
    # Allow static analysis without reportlab installed
    from templates.common import canvas, A4, Color, PDFTextObject  # type: ignore
from templates.common import (
    load_brand_colors,
    draw_header,
    draw_footer,
    add_watermark,
    draw_letterhead_dynamic_content,
    draw_modern_header,
    draw_contact_strip,
    _choose_font,
)


def generate(output_path=None):
    """Generate a sophisticated and minimal letterhead."""
    brand = load_brand_colors()
    w, h = A4
    if output_path is None:
        output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "letterhead.pdf")

    c = canvas.Canvas(output_path, pagesize=A4)
    
    # Draw modern header and watermark
    draw_modern_header(c, brand, title="ACCESS DISCREETKIT LTD", subtitle="Official Communication")
    add_watermark(c, brand, opacity=0.06)

    # Dynamic content
    current_date = datetime.now().strftime("%d %B %Y")
    recipient_details = [
        "Mr. John Doe",
        "Chief Executive Officer",
        "Innovate Corp.",
        "123 Innovation Drive, Accra, Ghana"
    ]
    subject = "Proposal for Strategic Partnership"
    
    draw_letterhead_dynamic_content(c, brand, current_date, recipient_details, subject)

    # Body placeholder
    _choose_font(c, 11)
    c.setFillColor(cast(Color, brand["indigo"]))
    
    body_text = c.beginText(40, h - 280)
    _choose_font(c, 11, text_object=body_text)
    body_text.setFillColor(cast(Color, brand["indigo"]))
    body_text.setLeading(15)
    
    body_content = [
        "Dear Mr. Doe,",
        "",
        "We are writing to propose a strategic partnership between Access DiscreetKit Ltd and Innovate Corp. Our goal is to leverage our combined strengths to drive innovation and create mutually beneficial opportunities.",
        "",
        "Our analysis indicates that a collaboration could unlock significant value in the market. We have attached a detailed proposal for your review and would be pleased to discuss this further at your convenience.",
        "",
        "Thank you for considering our proposal. We look forward to the possibility of working together.",
        "",
        "Sincerely,",
        "",
        "Jane Smith",
        "Director of Business Development",
        "Access DiscreetKit Ltd"
    ]

    for line in body_content:
        body_text.textLine(line)
    
    c.drawText(cast(PDFTextObject, body_text))

    # Contact strip (compact footer-like area)
    contact_lines = [
        "House No. 57, Kofi Annan East Avenue, Madina, Accra",
        "Email: dscreetkit@gmail.com",
        "Phone: +233 20 300 1107",
    ]
    social = ["Twitter: @discreetkit", "LinkedIn: /company/discreetkit"]
    draw_contact_strip(c, brand, contact_lines, social=social)
    
    c.showPage()
    c.save()

if __name__ == '__main__':
    generate()
