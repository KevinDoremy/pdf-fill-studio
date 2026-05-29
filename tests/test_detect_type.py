from pdf_fill_studio.detect_type import detect_type

def test_flat_pdf_detected():
    info = detect_type("tests/fixtures/flat_form.pdf")
    assert info["type"] == "flat"
    assert info["page_count"] == 1
    assert info["field_count"] == 0
    assert info["has_xfa"] is False
