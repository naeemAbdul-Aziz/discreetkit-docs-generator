"""Letterhead template generator (modern / typography-led).

This template was previously wired to a different set of helpers; the
project's shared utilities live in `templates.common` so we import the
helpers that actually exist there.
"""
import os
from datetime import datetime
from typing import Any

from templates.common import (
    load_brand_colors,
    add_watermark,
    draw_modern_header,
    draw_letterhead_dynamic_content,
    draw_footer_block,
    _choose_font,
    canvas,
    A4,
    inch,
    mm,
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

    # Header (modern helper from templates.common)
    # draw_modern_header expects: (c, brand, title, subtitle, logo_name)
    draw_modern_header(c, brand, subject, company_name, logo_icon)
    
    # Watermark (subtle, icon-only)
    add_watermark(c, brand, opacity=0.04)

    # Dynamic content (Date, Recipient)
    # `draw_letterhead_dynamic_content` draws the date and recipient block
    # but does not return a Y position. Compute an approximate start Y for
    # the body based on the recipient block height and spacing.
    draw_letterhead_dynamic_content(c, brand, current_date, recipient_details)
    # compute body start Y: start below recipient block and keep it reasonable
    w, h = A4
    margin_top_body = 1 * inch + 35 * mm
    recipient_leading = 14
    recipient_lines = len(recipient_details)
    bottom_of_recipient = h - margin_top_body - (recipient_lines * recipient_leading)
    # small gap between recipient block and body (reduced to avoid excessive whitespace)
    body_start_y = bottom_of_recipient - (6 * mm)

    # Body — consistent margins and spacing
    # Use the same left margin used by `templates.common` helpers (1.25in)
    left_margin = 1.25 * inch
    right_margin = 1 * inch
    top_margin = 1.25 * inch
    # Reserve enough space for the footer block and bottom accent bar.
    # `draw_footer_block` places its text around 1in above bottom and draws
    # a small accent bar at the bottom. Reserve ~1.4in to avoid overlap.
    bottom_reserved = 1.4 * inch

    # Set and use a predictable font for measurement and drawing
    font_size = 11
    _choose_font(c, font_size)
    font_name = "Helvetica"  # safe fallback for measuring text width

    available_width = w - left_margin - right_margin
    leading = 14

    # Ensure body start isn't above the writable area
    max_start = h - top_margin
    y = min(body_start_y, max_start)

    def wrap_paragraph(paragraph: str):
        words = paragraph.split()
        if not words:
            return [""]
        lines = []
        cur = words[0]
        for wrd in words[1:]:
            test = cur + " " + wrd
            # measure width using canvas.stringWidth
            try:
                width = c.stringWidth(test, font_name, font_size)
            except Exception:
                # Fallback: naive char-based split
                max_chars = int(available_width / (font_size * 0.5))
                if len(test) > max_chars:
                    lines.append(cur)
                    cur = wrd
                else:
                    cur = test
                continue

            if width <= available_width:
                cur = test
            else:
                lines.append(cur)
                cur = wrd
        lines.append(cur)
        return lines

    text_obj = c.beginText(left_margin, y)
    _choose_font(c, font_size, text_object=text_obj)
    text_obj.setFillColor(brand["indigo"])  # type: ignore
    text_obj.setLeading(leading)

    for paragraph in body_content:
        wrapped = wrap_paragraph(paragraph)
        for ln in wrapped:
            # paginate if we're about to run into footer
            if y - leading < bottom_reserved:
                # draw current buffer and start a new page
                c.drawText(text_obj)
                # draw footer on finished page
                draw_footer_block(c, brand,
                    address_lines=[footer_address],
                    contact_lines=[footer_email, footer_phone],
                    social_lines=[footer_social],
                )
                c.showPage()
                # start new page
                add_watermark(c, brand, opacity=0.04)
                # On subsequent pages, start text below top margin
                y = h - top_margin
                text_obj = c.beginText(left_margin, y)
                _choose_font(c, font_size, text_object=text_obj)
                text_obj.setFillColor(brand["indigo"])  # type: ignore
                text_obj.setLeading(leading)

            text_obj.textLine(ln)
            y -= leading

        # add a blank line between paragraphs
        if paragraph != body_content[-1]:
            if y - leading < bottom_reserved:
                c.drawText(text_obj)
                draw_footer_block(c, brand,
                    address_lines=[footer_address],
                    contact_lines=[f"Email: {footer_email}", f"Phone: {footer_phone}"],
                    social_lines=[footer_social],
                )
                c.showPage()
                add_watermark(c, brand, opacity=0.04)
                y = h - top_margin
                text_obj = c.beginText(left_margin, y)
                _choose_font(c, font_size, text_object=text_obj)
                text_obj.setFillColor(brand["indigo"])  # type: ignore
                text_obj.setLeading(leading)
            text_obj.textLine("")
            y -= leading

    # draw any remaining text
    c.drawText(text_obj)

    # Footer (use project's footer block helper)
    # Split social string into multiple lines if it contains separators
    social_lines_list = [s.strip() for s in footer_social.split("|")] if isinstance(footer_social, str) else footer_social
    draw_footer_block(c, brand, 
        address_lines=[footer_address],
        contact_lines=[f"Email: {footer_email}", f"Phone: {footer_phone}"],
        social_lines=social_lines_list,
    )
    
    c.showPage()
    c.save()

if __name__ == '__main__':
    generate()