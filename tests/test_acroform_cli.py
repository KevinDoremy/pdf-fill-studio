import json
from pypdf import PdfReader
from pdf_fill_studio.cli import main
def test_cli_acroform_autofill(tmp_path):
    prof = tmp_path / "p.json"
    prof.write_text(json.dumps({"full_name": "Marie Tremblay", "email": "m@x.com"}))
    out = tmp_path / "o.pdf"
    main(["tests/fixtures/acroform_form.pdf", "-o", str(out), "--profile", str(prof)])
    ff = PdfReader(str(out)).get_fields() or {}
    assert ff["full_name"]["/V"] == "Marie Tremblay"
    assert ff["email"]["/V"] == "m@x.com"
