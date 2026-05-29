"""MCP wrapper smoke test. Skips when the optional `mcp` dependency is absent."""
import pikepdf
import pytest

pytest.importorskip("mcp")


def test_mcp_tools(tmp_path):
    from pdf_fill_studio import mcp_server as m
    from pypdf import PdfReader

    assert m.detect_pdf_type("tests/fixtures/acroform_form.pdf")["type"] == "acroform"

    fields = m.list_fields("tests/fixtures/acroform_form.pdf")
    assert any(f["id"] == "full_name" for f in fields)

    out = tmp_path / "filled.pdf"
    m.fill_acroform_fields("tests/fixtures/acroform_form.pdf", {"full_name": "Marie Tremblay"}, str(out))
    assert (PdfReader(str(out)).get_fields() or {})["full_name"]["/V"] == "Marie Tremblay"


def test_fill_xfa_fields_mcp_datasets_and_acroform(tmp_path):
    """MCP fill_xfa_fields must inject into the datasets packet and set AcroForm /V."""
    from pdf_fill_studio import mcp_server as m

    out = tmp_path / "xfa_filled.pdf"
    m.fill_xfa_fields("tests/fixtures/xfa_form.pdf", {"full_name": "Marie Tremblay"}, str(out))
    pdf = pikepdf.open(str(out))
    try:
        xfa = pdf.Root.AcroForm.XFA
        ds = next(
            bytes(xfa[i + 1].read_bytes())
            for i in range(0, len(xfa) - 1, 2)
            if str(xfa[i]) == "datasets"
        )
        assert b"Marie Tremblay" in ds
        assert b"xfa:datasets" in ds          # lxml preserved the prefix
        vs = [
            str(f.V)
            for f in pdf.Root.AcroForm.Fields
            if str(f.get("/T", "")) == "full_name"
        ]
        assert vs == ["Marie Tremblay"]
    finally:
        pdf.close()


def test_fill_xfa_fields_mcp_dynamic_sets_needs_rendering(tmp_path, monkeypatch):
    """MCP path must pass xfa_type so NeedsRendering is set for dynamic XFA."""
    from pdf_fill_studio import mcp_server as m
    import pdf_fill_studio.mcp_server as ms
    import pdf_fill_studio.detect_type as dt

    # Patch detect_type to report xfa-dynamic so we can verify the flag without a real dynamic PDF
    original = dt.detect_type
    def fake_detect(path):
        result = original(path)
        result = dict(result)
        result["type"] = "xfa-dynamic"
        return result

    monkeypatch.setattr(ms, "detect_type", fake_detect)

    out = tmp_path / "dynamic_xfa.pdf"
    ms.fill_xfa_fields("tests/fixtures/xfa_form.pdf", {"full_name": "Test"}, str(out))
    pdf = pikepdf.open(str(out))
    try:
        assert bool(pdf.Root.get("/NeedsRendering", False)) is True
    finally:
        pdf.close()
