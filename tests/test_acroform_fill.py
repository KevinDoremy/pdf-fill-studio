from pypdf import PdfReader
from pdf_fill_studio.acroform import fill_acroform
def test_fill(tmp_path):
    out = tmp_path / "filled.pdf"
    fill_acroform("tests/fixtures/acroform_form.pdf",
                  {"full_name": "Marie Tremblay", "consent": "/Yes"}, str(out))
    ff = PdfReader(str(out)).get_fields() or {}
    assert ff["full_name"]["/V"] == "Marie Tremblay"
    assert ff["consent"]["/V"] == "/Yes"
