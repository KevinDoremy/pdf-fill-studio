"""Tests for the single-stream XFA code path in _read_datasets / fill_xfa."""
import pikepdf
from pikepdf import String
from pdf_fill_studio.xfa import _read_datasets, fill_xfa

DATASETS = (
    b'<xfa:datasets xmlns:xfa="http://www.xfa.org/schema/xfa-data/1.0/"><xfa:data>'
    b'<form1><full_name></full_name></form1></xfa:data></xfa:datasets>'
)


def _make_single_stream_pdf(path):
    """Build a minimal PDF whose AcroForm.XFA is a single stream (not an array)."""
    pdf = pikepdf.Pdf.new()
    page = pikepdf.Page(
        pikepdf.Dictionary(
            Type=pikepdf.Name("/Page"),
            MediaBox=[0, 0, 612, 792],
        )
    )
    pdf.pages.append(page)
    field = pikepdf.Dictionary(
        T=String("full_name"),
        FT=pikepdf.Name("/Tx"),
        Ff=0,
    )
    pdf.Root.AcroForm = pikepdf.Dictionary(
        Fields=pikepdf.Array([pdf.make_indirect(field)]),
    )
    pdf.Root.AcroForm.XFA = pikepdf.Stream(pdf, DATASETS)
    pdf.save(str(path))


def test_read_datasets_single_stream(tmp_path):
    pdf_path = tmp_path / "single.pdf"
    _make_single_stream_pdf(pdf_path)
    pdf = pikepdf.open(str(pdf_path))
    try:
        result = _read_datasets(pdf)
        assert result is not None
        assert result.xfa_array is None      # single-stream: no array
        assert result.array_idx is None      # single-stream: no index
        assert b"xfa:datasets" in result.raw
        assert b"full_name" in result.raw
    finally:
        pdf.close()


def test_fill_xfa_single_stream(tmp_path):
    pdf_path = tmp_path / "single.pdf"
    out_path = tmp_path / "filled.pdf"
    _make_single_stream_pdf(pdf_path)
    fill_xfa(str(pdf_path), {"full_name": "Marie Tremblay"}, str(out_path))
    pdf = pikepdf.open(str(out_path))
    try:
        xfa = pdf.Root.AcroForm.XFA
        assert isinstance(xfa, pikepdf.Stream)
        raw = bytes(xfa.read_bytes())
        assert b"Marie Tremblay" in raw
        assert b"xfa:datasets" in raw  # lxml preserved the prefix
        vs = [
            str(f.V)
            for f in pdf.Root.AcroForm.Fields
            if str(f.get("/T", "")) == "full_name"
        ]
        assert vs == ["Marie Tremblay"]
    finally:
        pdf.close()
