from pypdf import PdfReader
def test_fixture_has_acroform_fields():
    fields = PdfReader("tests/fixtures/acroform_form.pdf").get_fields() or {}
    assert set(fields) == {"full_name", "email", "consent"}
    assert fields["full_name"]["/FT"] == "/Tx"
    assert fields["consent"]["/FT"] == "/Btn"
