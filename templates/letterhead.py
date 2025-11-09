"""Letterhead template generator (Geometric Design)."""
import os
from typing import cast
from datetime import datetime
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.colors import Color
    from reportlab.pdfgen.textobject import PDFTextObject
    from reportlab.lib.units import inch, mm
except Exception:
    # Allow static analysis
    from templates.common import canvas, A4, Color, PDFTextObject, inch, mm  # type: ignore
from templates.common import (
    load_brand_colors,
    add_watermark,
    draw_geometric_header,
    draw_letterhead_dynamic_content,
    draw_geometric_footer,
    _choose_font,
)


def generate(output_path=None):
    """Generate a sophisticated and modern letterhead."""
    brand = load_brand_colors()
    w, h = A4
    if output_path is None:
        output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "letterhead_professional.pdf")

    c = canvas.Canvas(output_path, pagesize=A4)
    
    # === 1. Define Content ===
    company_name = "ACCESS DISCREETKIT LTD"
    logo_icon = "Artboard 2.png" # The teal icon
    watermark_icon = "Artboard 8.png" # The grey icon
    
    subject = "Proposal for Strategic Partnership"
    current_date = datetime.now().strftime("%d %B %Y")
    
    recipient_details = [
        "Mr. John Doe",
        "Chief Executive Officer",
        "Innovate Corp.",
        "123 Innovation Drive, Accra, Ghana"
    ]
    
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

    footer_address = "House No. 57, Kofi Annan East Avenue, Madina, Accra"
    footer_email = "dscreetkit@gmail.com"
    footer_phone = "+233 20 300 1107"
    footer_social = "Twitter: @discreetkit | LinkedIn: /company/discreetkit"
    
    # === 2. Draw Document ===

    # Header
    draw_geometric_header(c, brand, 
        company_name=company_name,
        logo_name=logo_icon
    )
    
    # Watermark (subtle, icon-only)
    add_watermark(c, brand, opacity=0.04)

    # Dynamic content (Date, Recipient, Subject)
    # This function now returns the starting Y position for the body
    body_start_y = draw_letterhead_dynamic_content(c, brand, current_date, recipient_details, subject)

    # Body
    margin = 1 * inch
    
    _choose_font(c, 11)
    c.setFillColor(cast(Color, brand["indigo"]))
    
    body_text = c.beginText(margin, body_start_y)
    _choose_font(c, 11, text_object=body_text)
    body_text.setFillColor(cast(Color, brand["indigo"]))
    body_text.setLeading(15)
    
    for line in body_content:
        body_text.textLine(line)
    
    c.drawText(cast(PDFTextObject, body_text))

    # Footer
    draw_geometric_footer(c, brand, 
        address=footer_address, 
        email=footer_email,
        phone=footer_phone,
        social=footer_social
    )
    
    c.showPage()
    c.save()

if __name__ == '__main__':
    generate()