"""Common utilities for templates: load brand colors, header/footer drawing helpers.

Also handles Satoshi font registration with Helvetica fallback.
Includes graceful fallbacks if ReportLab is not installed to avoid import errors
during static analysis or partial environments.
"""
from typing import Dict, Any, List
import os
import json
import re
try:  # Attempt real ReportLab imports
    from reportlab.pdfgen import canvas as _canvas_mod
    from reportlab.lib import colors as _colors_mod
    from reportlab.lib.pagesizes import A4 as _A4
    from reportlab.pdfbase import pdfmetrics as _pdfmetrics_mod
    from reportlab.pdfbase.ttfonts import TTFont as _TTFont
    from reportlab.lib.units import inch, mm
    canvas = _canvas_mod  # type: ignore
    colors = _colors_mod  # type: ignore
    A4 = _A4  # type: ignore
    pdfmetrics = _pdfmetrics_mod  # type: ignore
    TTFont = _TTFont  # type: ignore
except Exception:  # Fallback lightweight stubs
    class _StubColors:
        white = (1, 1, 1)
        def Color(self, r, g, b): return (r, g, b)
    colors = _StubColors()  # type: ignore
    A4 = (595.275590551, 841.88976378)  # type: ignore
    inch = 72.0  # type: ignore
    mm = 2.834645669  # type: ignore
    class _StubPdfMetrics:
        def registerFont(self, *a, **k): pass
        def getFont(self, name): return None
    pdfmetrics = _StubPdfMetrics()  # type: ignore
    class TTFont:  # type: ignore
        def __init__(self, *a, **k): pass
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
    """Attempt to register Satoshi Regular/Bold if font files exist."""
    global _SATOSHI_REGISTERED
    if _SATOSHI_REGISTERED:
        return

    candidates_regular = [
        os.path.join(ASSETS_DIR, "fonts", "Satoshi-Regular.ttf"),
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
    for path in candidates_bold:
        if os.path.isfile(path):
            try:
                pdfmetrics.registerFont(TTFont("Satoshi-Bold", path))
                break
            except Exception:
                pass
    _SATOSHI_REGISTERED = registered_any


def load_brand_colors() -> Dict[str, object]:
    """Load brand colors from JSON."""
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
                pass

    # Ensure required keys are present
    brand.setdefault("neutral_white", colors.white)
    brand.setdefault("indigo", hex_to_color("#1e3a5f"))
    brand.setdefault("cyan_turquoise", hex_to_color("#187f76"))
    brand.setdefault("light_silver", hex_to_color("#d7d9db"))
    brand.setdefault("warm_brown", brand.get("indigo")) # Fallback for old templates

    return brand


def _choose_font(c: Any, size: int = 10, bold: bool = False, text_object: Any = None):
    """Prefer Satoshi (bold/regular) if registered; else Helvetica variants."""
    register_satoshi_font()
    font_name = "Helvetica"
    if bold:
        font_name = "Helvetica-Bold"

    try:
        if bold and pdfmetrics.getFont("Satoshi-Bold"):
            font_name = "Satoshi-Bold"
        elif not bold and pdfmetrics.getFont("Satoshi"):
            font_name = "Satoshi"
    except KeyError:
        pass  # Fallback to Helvetica

    target = text_object if text_object is not None else c
    target.setFont(font_name, size)


def draw_modern_header(c: Any, brand: Dict[str, Any], title: str, subtitle: str, logo_name: str = "Artboard 1.png"):
    """Draw a modern, typography-led header.

    - `title`: The main, large title (e.g., "Proposal for Partnership").
    - `subtitle`: The smaller text above the title (e.g., "ACCESS DISCREETKIT LTD").
    - `logo_name`: The logo file to use from `assets/logos/`.
    """
    w, h = A4
    margin_left = 1.25 * inch
    margin_top = 1 * inch

    # === Left Accent Bar ===
    try:
        c.setFillColor(brand.get("cyan_turquoise"))
        c.rect(0, 0, 18 * mm, h, fill=1, stroke=0) # Full-height bar
    except Exception:
        pass

    # === Logo (Top-Left, above title) ===
    logo_path = os.path.abspath(os.path.join(ASSETS_DIR, "logos", logo_name))
    try:
        # Using Artboard 1: Color logo, blue text
        c.drawImage(logo_path, margin_left, h - (margin_top - 10*mm), width=100, height=40, mask='auto')
    except Exception:
        # Fallback neutral box
        try:
            c.setFillColor(brand.get("light_silver"))
            c.rect(margin_left, h - (margin_top - 10*mm), 100, 40, fill=1, stroke=0)
        except Exception:
            pass
    
    # === Title Block (Inverted Hierarchy) ===
    
    # Subtitle (Company Name)
    try:
        c.setFillColor(brand.get("indigo"))
        _choose_font(c, 10, bold=False)
        c.drawString(margin_left, h - (margin_top + 10*mm), subtitle.upper())
    except Exception:
        pass

    # Main Title (Document Purpose)
    try:
        c.setFillColor(brand.get("indigo"))
        _choose_font(c, 28, bold=True)
        # Position title below subtitle
        c.drawString(margin_left, h - (margin_top + 20*mm), title)
    except Exception:
        pass
    
    # Separator Line
    try:
        c.setStrokeColor(brand.get("light_silver"))
        c.setLineWidth(0.5)
        c.line(margin_left, h - (margin_top + 25*mm), w - margin_left, h - (margin_top + 25*mm))
    except Exception:
        pass


def draw_letterhead_dynamic_content(c: Any, brand: Dict[str, Any], date: str, recipient: list[str]):
    """Draw dynamic elements: date and recipient block."""
    w, h = A4
    margin_left = 1.25 * inch
    margin_top_body = 1 * inch + 35*mm # Start below the header area

    _choose_font(c, 10)
    c.setFillColor(brand.get("indigo"))

    # Date (Top right, aligned with body)
    c.drawRightString(w - margin_left, h - (margin_top_body - 10*mm), date)

    # Recipient details
    text = c.beginText(margin_left, h - margin_top_body)
    _choose_font(c, 11, text_object=text)
    text.setFillColor(brand.get("indigo"))
    text.setLeading(14)
    for line in recipient:
        text.textLine(line)
    c.drawText(text)


def draw_footer_block(c: Any, brand: Dict[str, Any], address_lines: List[str], contact_lines: List[str], social_lines: List[str]):
    """Draw a sophisticated, multi-column footer block."""
    w, h = A4
    margin = 1.25 * inch
    bottom_y = 1 * inch # Position of the text
    
    col_1_x = margin
    col_2_x = margin + 170
    col_3_x = margin + 340
    
    c.setFillColor(brand.get("indigo"))

    try:
        # Column 1: Address
        text = c.beginText(col_1_x, bottom_y)
        _choose_font(c, 9, bold=True, text_object=text)
        text.textLine("Address")
        _choose_font(c, 9, bold=False, text_object=text)
        text.setLeading(12)
        text.textLine("") #
        for line in address_lines:
            text.textLine(line)
        c.drawText(text)

        # Column 2: Contact
        text = c.beginText(col_2_x, bottom_y)
        _choose_font(c, 9, bold=True, text_object=text)
        text.textLine("Contact")
        _choose_font(c, 9, bold=False, text_object=text)
        text.setLeading(12)
        text.textLine("") #
        for line in contact_lines:
            text.textLine(line)
        c.drawText(text)

        # Column 3: Social
        text = c.beginText(col_3_x, bottom_y)
        _choose_font(c, 9, bold=True, text_object=text)
        text.textLine("Follow Us")
        _choose_font(c, 9, bold=False, text_object=text)
        text.setLeading(12)
        text.textLine("") #
        for line in social_lines:
            text.textLine(line)
        c.drawText(text)
    except Exception:
        pass # Fail gracefully

    # === Bottom Accent Bar ===
    try:
        c.setFillColor(brand.get("cyan_turquoise"))
        c.rect(0, 0, w, 5*mm, fill=1, stroke=0) # Full-width bottom bar
    except Exception:
        pass


def add_watermark(c: Any, brand: Dict[str, Any], opacity: float = 0.06):
    """Draw the watermark image semi-transparently in the center of the page."""
    w, h = A4
    watermark_path = os.path.abspath(os.path.join(ASSETS_DIR, "watermark.png"))
    try:
        c.saveState()
        # Use low-level PDF ExtGState for reliable transparency
        gs_name = f"GsAlpha{int(opacity*100)}"
        c.setPageMark(f"/GS {gs_name} <</ca {opacity} /CA {opacity}>> BDC")
        
        c.translate(w / 2.0, h / 2.0)
        c.drawImage(watermark_path, -150, -150, width=300, height=300, mask='auto')
        
        c.restoreState()
    except Exception:
        # Fallback if transparency state fails
        try:
            c.restoreState() # Ensure state is restored even on error
        except:
            pass
        # no-op if watermark not available or transparency fails
        pass


# Deprecated functions (kept for compatibility with other templates until refactored)
def draw_header(c: Any, brand: Dict[str, Any], title: str | None = None):
    pass
def draw_footer(c: Any, brand: Dict[str, Any]):
    pass
def draw_contact_strip(c: Any, brand: Dict[str, Any], *args, **kwargs):
    pass