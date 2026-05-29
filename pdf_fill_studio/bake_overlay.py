"""Burn text values onto a flat PDF at final coordinates, then write the output.

Reads job coordinates as PDF points, top-left origin. Signature fields are skipped.
"""
import io
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter
from pdf_fill_studio.coords import topleft_box_to_baseline


# Note: clone into the writer first, then merge onto the writer-owned pages, so
# pypdf does not warn about merging pages that are not attached to a writer.


def _draw_comb(c, field, value, page_height):
    """Draw one character centered in each successive cell (spaces skipped)."""
    size = field.get("font_size", 10)
    chars = [ch for ch in value if not ch.isspace()]
    for ch, cell in zip(chars, field.get("cells", [])):
        char_w = c.stringWidth(ch, "Helvetica", size)
        cx = cell["x"] + cell["w"] / 2 - char_w / 2
        center_y = page_height - cell["y"] - cell["h"] / 2  # cell center, bottom-left origin
        baseline = center_y - 0.35 * size                   # lower baseline so glyph is centered
        c.drawString(cx, baseline, ch)


def _overlay_for_page(page_fields, width, height):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(width, height))
    for f in page_fields:
        ftype = f.get("type")
        if ftype == "signature":
            continue
        value = (f.get("value") or "").strip()
        if not value:
            continue
        size = f.get("font_size", 10)
        c.setFont("Helvetica", size)
        if ftype == "comb":
            _draw_comb(c, f, value, height)
            continue
        x, baseline = topleft_box_to_baseline(f["x"], f["y"], f["w"], f["h"], height, size)
        c.drawString(x, baseline, value)
    c.showPage()
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


def bake_overlay(job, out_path):
    writer = PdfWriter(clone_from=job["pdf"])
    page_dims = {p["page"]: (p["width"], p["height"]) for p in job["pages"]}
    for pidx, page in enumerate(writer.pages, start=1):
        fields = [f for f in job["fields"] if f["page"] == pidx]
        if fields:
            width, height = page_dims.get(pidx, (float(page.mediabox.width), float(page.mediabox.height)))
            overlay_page = _overlay_for_page(fields, width, height)
            page.merge_page(overlay_page)
    with open(out_path, "wb") as fh:
        writer.write(fh)
    return out_path
