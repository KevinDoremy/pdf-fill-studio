"""Read and fill native AcroForm fields with pypdf."""
from pypdf import PdfReader, PdfWriter

_FT = {"/Tx": "text", "/Btn": "checkbox", "/Ch": "choice", "/Sig": "signature"}

def extract_acroform_fields(pdf_path):
    reader = PdfReader(pdf_path)
    raw = reader.get_fields() or {}
    # map field name -> page number via widget annotations
    page_of = {}
    for pidx, page in enumerate(reader.pages, start=1):
        for annot in (page.get("/Annots") or []):
            obj = annot.get_object()
            name = obj.get("/T")
            if name is not None:
                page_of[str(name)] = pidx
    fields = []
    for name, spec in raw.items():
        fields.append({
            "id": name,
            "label": name,
            "type": _FT.get(spec.get("/FT"), "text"),
            "page": page_of.get(name, 1),
        })
    return fields
