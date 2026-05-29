from pdf_fill_studio.xfa import extract_xfa_fields


def test_extract_xfa_fields():
    fields = extract_xfa_fields("tests/fixtures/xfa_form.pdf")
    assert "full_name" in [f["id"] for f in fields]
