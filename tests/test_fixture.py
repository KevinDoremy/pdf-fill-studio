from pypdf import PdfReader

def test_fixture_is_flat_single_page():
    reader = PdfReader("tests/fixtures/flat_form.pdf")
    assert len(reader.pages) == 1
    assert reader.get_fields() in (None, {})  # no AcroForm fields
