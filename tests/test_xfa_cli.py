import json
import pikepdf
from pdf_fill_studio.cli import main


def test_cli_xfa_autofill(tmp_path):
    prof = tmp_path / "p.json"
    prof.write_text(json.dumps({"full_name": "Marie Tremblay"}))
    out = tmp_path / "o.pdf"
    main(["tests/fixtures/xfa_form.pdf", "-o", str(out), "--profile", str(prof)])
    pdf = pikepdf.open(str(out))
    xfa = pdf.Root.AcroForm.XFA
    ds = next(
        bytes(xfa[i + 1].read_bytes())
        for i in range(0, len(xfa) - 1, 2)
        if str(xfa[i]) == "datasets"
    )
    assert b"Marie Tremblay" in ds
