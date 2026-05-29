import json
from pdf_fill_studio.serve_editor import handle_export

def test_handle_export_bakes_pdf(tmp_path):
    job = {
        "pdf": "tests/fixtures/flat_form.pdf",
        "type": "flat",
        "pages": [{"page": 1, "width": 612, "height": 792}],
        "fields": [],
    }
    posted = {"fields": [
        {"id": "f1", "page": 1, "label": "Nom:", "x": 130, "y": 95, "w": 250, "h": 16,
         "value": "Kevin Doremy", "type": "text", "font_size": 11},
    ]}
    out = tmp_path / "filled.pdf"
    handle_export(job, posted, str(out))
    from pypdf import PdfReader
    text = "".join(p.extract_text() or "" for p in PdfReader(str(out)).pages)
    assert "Kevin Doremy" in text
