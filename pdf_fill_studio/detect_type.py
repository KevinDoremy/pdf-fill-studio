"""Detect how a PDF form is built: flat | acroform | xfa-static | xfa-dynamic."""
from pypdf import PdfReader


def detect_type(path):
    reader = PdfReader(path)
    page_count = len(reader.pages)

    root = reader.trailer["/Root"]
    acro = root.get("/AcroForm")
    fields = reader.get_fields() or {}
    field_count = len(fields)

    has_xfa = False
    xfa_dynamic = False
    if acro is not None:
        acro_obj = acro.get_object()
        if "/XFA" in acro_obj:
            has_xfa = True
            # Heuristic: a /NeedsRendering flag at the catalog level marks dynamic XFA.
            xfa_dynamic = bool(root.get("/NeedsRendering", False))

    if has_xfa:
        form_type = "xfa-dynamic" if xfa_dynamic else "xfa-static"
    elif field_count > 0:
        form_type = "acroform"
    else:
        form_type = "flat"

    return {
        "type": form_type,
        "page_count": page_count,
        "field_count": field_count,
        "has_xfa": has_xfa,
        "xfa_dynamic": xfa_dynamic,
    }
