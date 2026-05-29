"""MCP wrapper smoke test. Skips when the optional `mcp` dependency is absent."""
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
