import io
from pypdf import PdfReader
from pdf_fill_studio.bake_overlay import bake_overlay

def test_values_are_written_and_signature_skipped(tmp_path):
    job = {
        "pdf": "tests/fixtures/flat_form.pdf",
        "type": "flat",
        "pages": [{"page": 1, "width": 612, "height": 792}],
        "fields": [
            {"id": "f1", "page": 1, "label": "Nom:", "x": 130, "y": 95, "w": 250, "h": 16,
             "value": "Kevin Doremy", "type": "text", "font_size": 11},
            {"id": "f2", "page": 1, "label": "Signature:", "x": 150, "y": 255, "w": 250, "h": 16,
             "value": "SHOULD_NOT_APPEAR", "type": "signature", "font_size": 11},
        ],
    }
    out = tmp_path / "filled.pdf"
    bake_overlay(job, str(out))
    text = "".join(p.extract_text() or "" for p in PdfReader(str(out)).pages)
    assert "Kevin Doremy" in text
    assert "SHOULD_NOT_APPEAR" not in text
