"""Common utilities for templates: load brand colors, header/footer drawing helpers.

Also handles Satoshi font registration with Helvetica fallback.
Includes graceful fallbacks if ReportLab is not installed to avoid import errors
during static analysis or partial environments.
"""
from typing import Dict, Any
import os
import json
import re
try:  # Attempt real ReportLab imports (assign to local names first to avoid Final reassign warnings)
    from reportlab.pdfgen import canvas as _canvas_mod
    from reportlab.lib import colors as _colors_mod
    from reportlab.lib.pagesizes import A4 as _A4
    from reportlab.pdfbase import pdfmetrics as _pdfmetrics_mod
    from reportlab.pdfbase.ttfonts import TTFont as _TTFont
    canvas = _canvas_mod  # type: ignore
    colors = _colors_mod  # type: ignore
    A4 = _A4  # type: ignore
    pdfmetrics = _pdfmetrics_mod  # type: ignore
    TTFont = _TTFont  # type: ignore
except Exception:  # Fallback lightweight stubs (non-rendering) to satisfy tooling
    class _StubColors:
        white = (1, 1, 1)
        def Color(self, r, g, b):  # mimic callable interface
            return (r, g, b)
    colors = _StubColors()  # type: ignore
    A4 = (595.275590551, 841.88976378)  # type: ignore
    class _StubPdfMetrics:
        def registerFont(self, *a, **k):
            pass
        def getFont(self, name):
            return None
    pdfmetrics = _StubPdfMetrics()  # type: ignore
    class TTFont:  # type: ignore
        def __init__(self, *a, **k):
            pass
    class _StubText:
        def setFont(self, *a, **k): pass
        def setFillColor(self, *a, **k): pass
        def textLine(self, *a, **k): pass
        def setLeading(self, *a, **k): pass

    class _StubCanvas:
        def __init__(self, *a, **k): pass
        def setFillColor(self, *a, **k): pass
        def rect(self, *a, **k): pass
        def drawImage(self, *a, **k): pass
        def setFont(self, *a, **k): pass
        def drawString(self, *a, **k): pass
        def drawRightString(self, *a, **k): pass
        def drawCentredString(self, *a, **k): pass
        def saveState(self): pass
        def translate(self, *a, **k): pass
        def restoreState(self): pass
        def showPage(self): pass
        def save(self): pass
        def setStrokeColor(self, *a, **k): pass
        def setLineWidth(self, *a, **k): pass
        def line(self, *a, **k): pass
        def beginText(self, *a, **k): return _StubText()
        def drawText(self, *a, **k): pass
        def stringWidth(self, *a, **k): return 0

    class canvas:  # type: ignore
        Canvas = _StubCanvas

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "assets"))

# --- Font registration -----------------------------------------------------
_SATOSHI_REGISTERED = False


def register_satoshi_font():
    """Attempt to register Satoshi Regular/Bold if font files exist.

    Search locations:
      - assets/fonts/Satoshi-Regular.ttf
      - assets/fonts/Satoshi-Bold.ttf
      - assets/Satoshi.ttf (regular)
      - project root Satoshi.ttf (fallback)
    """
    global _SATOSHI_REGISTERED
    if _SATOSHI_REGISTERED:
        return

    candidates_regular = [
        os.path.join(ASSETS_DIR, "fonts", "Satoshi-Regular.ttf"),
        os.path.join(ASSETS_DIR, "Satoshi.ttf"),
        os.path.abspath(os.path.join(ASSETS_DIR, "..", "Satoshi.ttf")),
    ]
    candidates_bold = [
        os.path.join(ASSETS_DIR, "fonts", "Satoshi-Bold.ttf"),
    ]

    registered_any = False
    for path in candidates_regular:
        if os.path.isfile(path):
            try:
                pdfmetrics.registerFont(TTFont("Satoshi", path))
                registered_any = True
                break
            except Exception:
                pass

    # Bold is optional
    for path in candidates_bold:
        if os.path.isfile(path):
            try:
                pdfmetrics.registerFont(TTFont("Satoshi-Bold", path))
                break
            except Exception:
                pass

    _SATOSHI_REGISTERED = registered_any


def load_brand_colors() -> Dict[str, object]:
    """Load brand colors from JSON, ignoring any non-hex or invalid values.

    Ensures that the commonly used keys exist; falls back to sensible defaults
    derived from the new palette if missing.
    """
    path = os.path.abspath(os.path.join(ASSETS_DIR, "brand_colors.json"))
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    hex_re = re.compile(r"^#([0-9a-fA-F]{6})$")

    def hex_to_color(h: str):
        h = h.strip()
        if not hex_re.match(h):
            raise ValueError("Invalid hex color")
        h = h.lstrip("#")
        r = int(h[0:2], 16) / 255.0
        g = int(h[2:4], 16) / 255.0
        b = int(h[4:6], 16) / 255.0
        return colors.Color(r, g, b)

    brand: Dict[str, object] = {}
    for k, v in (data or {}).items():
        if isinstance(v, str):
            try:
                brand[k] = hex_to_color(v)
            except Exception:
                # Skip non-hex or invalid mappings
                pass

    # Ensure legacy keys (used by templates) are present using new palette fallbacks
    # Provide deterministic fallback colors as tuples if Color factory missing
    def _fallback_color(r, g, b):
        try:
            return colors.Color(r, g, b)  # type: ignore[attr-defined]
        except Exception:
            return (r, g, b)
    brand.setdefault("neutral_white", colors.white)

    return brand


def _choose_font(c: Any, size: int = 10, bold: bool = False, text_object: Any = None):
    """Prefer Satoshi (bold/regular) if registered; else Helvetica variants."""
    # Ensure we attempted registration once
    register_satoshi_font()

    font_name = "Helvetica"
    if bold and pdfmetrics.getFont("Helvetica-Bold"):
        font_name = "Helvetica-Bold"

    try:
        if bold and pdfmetrics.getFont("Satoshi-Bold"):
            font_name = "Satoshi-Bold"
        elif _SATOSHI_REGISTERED:
            font_name = "Satoshi"
    except KeyError:
        pass  # Fallback to Helvetica

    target = text_object if text_object is not None else c
    target.setFont(font_name, size)


def draw_header(c: Any, brand: Dict[str, Any], title: str | None = None):
    """Draw a sophisticated, minimal header with logo and optional title."""
    w, h = A4
    
    # Draw the logo
    logo_path = os.path.abspath(os.path.join(ASSETS_DIR, "logos", "logo_small.png"))
    try:
        # Use a smaller, more refined logo if available
        c.drawImage(logo_path, 40, h - 60, width=120, height=40, mask='auto')
    except Exception:
        # Fallback for the original logo
        logo_path_orig = os.path.abspath(os.path.join(ASSETS_DIR, "logo.png"))
        try:
            c.drawImage(logo_path_orig, 40, h - 55, width=80, height=32, mask='auto')
        except Exception:
            c.setFillColor(brand.get("light_silver"))
            c.rect(40, h - 55, 80, 32, fill=1, stroke=0)

    # Document title (if provided)
    if title:
        c.setFillColor(brand.get("indigo"))
        _choose_font(c, 18, bold=True)
        c.drawRightString(w - 40, h - 55, title)

    # Subtle separator line
    c.setStrokeColor(brand.get("light_silver"))
    c.setLineWidth(0.5)
    c.line(40, h - 80, w - 40, h - 80)


def draw_letterhead_dynamic_content(c: Any, brand: Dict[str, Any], date: str, recipient: list[str], subject: str):
    """Draw dynamic elements like date, recipient, and subject."""
    w, h = A4
    
    _choose_font(c, 10)
    c.setFillColor(brand.get("indigo"))

    # Date
    c.drawRightString(w - 40, h - 110, date)

    # Recipient details
    text = c.beginText(40, h - 140)
    _choose_font(c, 11, text_object=text)
    text.setFillColor(brand.get("indigo"))
    for line in recipient:
        text.textLine(line)
    c.drawText(text)

    # Subject line
    subject_font_bold = "Satoshi-Bold" if pdfmetrics.getFont("Satoshi-Bold") else "Helvetica-Bold"
    _choose_font(c, 11, bold=True)
    c.drawString(40, h - 220, "Subject: ")
    _choose_font(c, 11)
    c.drawString(40 + c.stringWidth("Subject: ", subject_font_bold, 11), h - 220, subject)


def draw_footer(c: Any, brand: Dict[str, Any]):
    """Draw a sophisticated footer with comprehensive contact details."""
    w, h = A4
    
    c.setFillColor(brand.get("indigo"))
    _choose_font(c, 8)

    # Footer content
    line1 = "Access DiscreetKit Ltd | Registered in Ghana"
    line2 = "www.discreetkit.com | info@discreetkit.com | +233 12 345 6789"
    
    c.drawCentredString(w / 2.0, 45, line1)
    c.drawCentredString(w / 2.0, 30, line2)

    # Subtle separator line above footer
    c.setStrokeColor(brand.get("light_silver"))
    c.setLineWidth(0.5)
    c.line(40, 65, w - 40, 65)


def _set_transparency(c: Any, alpha: float) -> None:
    """Attempt to set drawing transparency; silently ignore if unsupported."""
    try:
        # Newer ReportLab (>=3.5) exposes setFillAlpha / setStrokeAlpha
        if hasattr(c, "setFillAlpha"):
            c.setFillAlpha(alpha)
        # Low-level PDF ExtGState fallback
        elif hasattr(c, "_doc"):
            # Create an ExtGState only once per alpha value
            gs_name = f"Gs{int(alpha*100)}"
            if not getattr(c._doc, "_extgstates", None):  # type: ignore[attr-defined]
                c._doc._extgstates = {}  # type: ignore[attr-defined]
            if alpha not in c._doc._extgstates:  # type: ignore[attr-defined]
                # Define a transparency state; ReportLab internal API (best-effort)
                c._doc._extgstates[alpha] = ("/GS{} << /ca {} /CA {} >>".format(gs_name, alpha, alpha), gs_name)  # type: ignore[attr-defined]
            # If direct application not possible we silently ignore.
    except Exception:
        pass


def add_watermark(c: Any, brand: Dict[str, Any], opacity: float = 0.12):
    """Draw the watermark image semi-transparently in the center of the page.

    opacity: 0 (invisible) .. 1 (fully opaque). Default is a subtle 12%.
    Provide a PNG with transparent background in assets/watermark.png.
    """
    w, h = A4
    watermark_path = os.path.abspath(os.path.join(ASSETS_DIR, "watermark.png"))
    try:
        c.saveState()
        _set_transparency(c, max(0.0, min(opacity, 1.0)))
        c.translate(w / 2.0 - 150, h / 2.0 - 150)
        c.drawImage(watermark_path, 0, 0, width=300, height=300, mask='auto')
        c.restoreState()
    except Exception:
        # no-op if watermark not available
        pass


def draw_modern_header(c: Any, brand: Dict[str, Any], title: str | None = None, subtitle: str | None = None, logo_name: str = "logo.png"):
    """Draw a modern, minimal header inspired by the provided art direction.

    Design notes:
    - Left accent bar using `cyan_turquoise` for personality.
    - Large, bold title on the left area and optional subtitle.
    - Small logo placed top-right.
    - Keeps spacing generous and minimal.
    """
    w, h = A4

    # Left accent bar
    try:
        c.setFillColor(brand.get("cyan_turquoise"))
        c.rect(0, h - 140, 18, 140, fill=1, stroke=0)
    except Exception:
        pass

    # Title block
    if title:
        try:
            c.setFillColor(brand.get("indigo"))
            _choose_font(c, 28, bold=True)
            # shift right from the accent bar
            c.drawString(40, h - 70, title)
        except Exception:
            try:
                c.setFillColor(brand.get("indigo"))
                c.setFont("Helvetica-Bold", 28)
                c.drawString(40, h - 70, title)
            except Exception:
                pass

    # Subtitle (smaller, muted)
    if subtitle:
        try:
            c.setFillColor(brand.get("light_silver"))
            _choose_font(c, 11)
            c.drawString(40, h - 92, subtitle)
        except Exception:
            pass

    # Logo on the right (small)
    logo_path = os.path.abspath(os.path.join(ASSETS_DIR, logo_name))
    try:
        c.drawImage(logo_path, w - 140, h - 90, width=100, height=40, mask='auto')
    except Exception:
        # try a logos/ subpath
        logo_path2 = os.path.abspath(os.path.join(ASSETS_DIR, "logos", logo_name))
        try:
            c.drawImage(logo_path2, w - 140, h - 90, width=100, height=40, mask='auto')
        except Exception:
            # fallback neutral box
            try:
                c.setFillColor(brand.get("light_silver"))
                c.rect(w - 140, h - 90, 100, 40, fill=1, stroke=0)
            except Exception:
                pass


def draw_contact_strip(c: Any, brand: Dict[str, Any], contact_lines: list[str], social: list[str] | None = None):
    """Draw a slim contact strip (often placed near the bottom or header area).

    This keeps contact and social details visible without creating a heavy footer.
    """
    w, h = A4
    y = 72  # vertical position for the strip

    try:
        # light separator above the strip
        c.setStrokeColor(brand.get("light_silver"))
        c.setLineWidth(0.5)
        c.line(40, y + 28, w - 40, y + 28)

        # contact text (left)
        left_x = 40
        _choose_font(c, 9)
        c.setFillColor(brand.get("indigo"))
        contact_text = " | ".join(contact_lines)
        c.drawString(left_x, y + 8, contact_text)

        # social (right)
        if social:
            social_text = " ".join(social)
            text_width = c.stringWidth(social_text, c._fontname, 9) if hasattr(c, 'stringWidth') else 0
            c.drawRightString(w - 40, y + 8, social_text)
    except Exception:
        # graceful no-op
        pass
