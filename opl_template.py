
import os
import time

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from PIL import Image


def _draw_wrapped_text(c, text, x, y, max_width, font="Helvetica", size=10, leading=13):
    """Simple word-wrap text drawer for ReportLab."""
    c.setFont(font, size)
    words = text.split()
    line = ""
    lines = []
    for word in words:
        test_line = (line + " " + word).strip()
        if c.stringWidth(test_line, font, size) <= max_width:
            line = test_line
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)

    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    return y


def _fit_image(path, max_w, max_h):
    """Return (draw_w, draw_h) preserving aspect ratio within max box."""
    with Image.open(path) as img:
        iw, ih = img.size
    ratio = min(max_w / iw, max_h / ih)
    return iw * ratio, ih * ratio


def generate_pdf(data, output_dir=None):
    """
    data = {
        "theme": str,
        "prepared_by": str,
        "classification": str,
        "highlight": str,
        "pqcdsm": [list of letters],
        "no_good_photo": path,
        "good_photo": path,
    }
    Returns path to generated PDF.
    """
    if output_dir is None:
        output_dir = os.path.expanduser("~")

    filename = f"OPL_{data['theme'][:20].replace(' ', '_')}_{int(time.time())}.pdf"
    filepath = os.path.join(output_dir, filename)

    width, height = A4
    c = canvas.Canvas(filepath, pagesize=A4)

    margin = 15 * mm
    top = height - margin

    # --- Title ---
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, top, "TPM: One Point Lesson_OPL")
    top -= 12 * mm

    # --- Theme / Prepared By ---
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, top, "Theme:")
    c.setFont("Helvetica", 11)
    c.drawString(margin + 25 * mm, top, data["theme"])
    top -= 8 * mm

    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, top, "Prepared By:")
    c.setFont("Helvetica", 11)
    c.drawString(margin + 30 * mm, top, data["prepared_by"])
    top -= 10 * mm

    # --- Classification ---
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, top, "Classification:")
    top -= 7 * mm

    c.setFont("Helvetica", 10)
    options = ["Basic Knowledge", "Improvement Cases", "Troubleshooting Cases"]
    x = margin
    for opt in options:
        box_size = 4 * mm
        c.rect(x, top - 3, box_size, box_size)
        if data["classification"] == opt:
            c.setFont("Helvetica-Bold", 10)
            c.drawString(x + 1, top - 2, "X")
            c.setFont("Helvetica", 10)
        c.drawString(x + box_size + 2, top, opt)
        x += 55 * mm
    top -= 12 * mm

    # --- Photos ---
    photo_max_w = (width - 2 * margin - 10 * mm) / 2
    photo_max_h = 60 * mm

    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, top, "No Good")
    c.drawString(margin + photo_max_w + 10 * mm, top, "Good")
    top -= 5 * mm

    photo_top = top

    if data.get("no_good_photo"):
        w, h = _fit_image(data["no_good_photo"], photo_max_w, photo_max_h)
        c.drawImage(data["no_good_photo"], margin, photo_top - h, width=w, height=h, preserveAspectRatio=True)

    if data.get("good_photo"):
        w, h = _fit_image(data["good_photo"], photo_max_w, photo_max_h)
        c.drawImage(data["good_photo"], margin + photo_max_w + 10 * mm, photo_top - h, width=w, height=h, preserveAspectRatio=True)

    top = photo_top - photo_max_h - 10 * mm

    # --- Highlight / Learning ---
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, top, "Highlight / Learning:")
    top -= 6 * mm

    top = _draw_wrapped_text(
        c, data.get("highlight", ""), margin, top, width - 2 * margin,
        font="Helvetica", size=10, leading=5 * mm
    )
    top -= 8 * mm

    # --- PQCDSM ---
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, top, "PQCDSM:")
    top -= 7 * mm

    c.setFont("Helvetica", 10)
    x = margin
    selected = data.get("pqcdsm", [])
    for letter in ["P", "Q", "C", "D", "S", "M"]:
        box_size = 4 * mm
        c.rect(x, top - 3, box_size, box_size)
        if letter in selected:
            c.setFont("Helvetica-Bold", 10)
            c.drawString(x + 1, top - 2, "X")
            c.setFont("Helvetica", 10)
        c.drawString(x + box_size + 2, top, letter)
        x += 20 * mm

    c.showPage()
    c.save()

    return filepath
