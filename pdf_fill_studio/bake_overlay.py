"""Burn text values onto a flat PDF at final coordinates, then write the output.

Reads job coordinates as PDF points, top-left origin. Signature fields are skipped.
"""
import io
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter
from pdf_fill_studio.coords import topleft_box_to_baseline


def _overlay_for_page(page_fields, width, height):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(width, height))
    for f in page_fields:
        if f.get("type") == "signature":
            continue
        value = (f.get("value") or "").strip()
        if not value:
            continue
        size = f.get("font_size", 10)
        x, baseline = topleft_box_to_baseline(f["x"], f["y"], f["w"], f["h"], height, size)
        c.setFont("Helvetica", size)
        c.drawString(x, baseline, value)
    c.showPage()
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


def bake_overlay(job, out_path):
    reader = PdfReader(job["pdf"])
    writer = PdfWriter()
    page_dims = {p["page"]: (p["width"], p["height"]) for p in job["pages"]}
    for pidx, page in enumerate(reader.pages, start=1):
        fields = [f for f in job["fields"] if f["page"] == pidx]
        if fields:
            width, height = page_dims.get(pidx, (float(page.mediabox.width), float(page.mediabox.height)))
            overlay_page = _overlay_for_page(fields, width, height)
            page.merge_page(overlay_page)
        writer.add_page(page)
    with open(out_path, "wb") as fh:
        writer.write(fh)
    return out_path
