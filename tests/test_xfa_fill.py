import pikepdf
from pdf_fill_studio.xfa import fill_xfa


def test_fill_xfa(tmp_path):
    out = tmp_path / "filled.pdf"
    fill_xfa("tests/fixtures/xfa_form.pdf", {"full_name": "Marie Tremblay"}, str(out))
    pdf = pikepdf.open(str(out))
    try:
        xfa = pdf.Root.AcroForm.XFA
        ds = next(
            bytes(xfa[i + 1].read_bytes())
            for i in range(0, len(xfa) - 1, 2)
            if str(xfa[i]) == "datasets"
        )
        assert b"Marie Tremblay" in ds
        assert b"xfa:datasets" in ds                  # lxml preserved the prefix
        vs = [
            str(f.V)
            for f in pdf.Root.AcroForm.Fields
            if str(f.get("/T", "")) == "full_name"
        ]
        assert vs == ["Marie Tremblay"]
    finally:
        pdf.close()
