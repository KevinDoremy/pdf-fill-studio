"""The render helper turns a PDF page into a PNG for visual self-check."""
import os
from pdf_fill_studio.render_page import render


def test_render_produces_png(tmp_path):
    pngs = render("tests/fixtures/flat_form.pdf", str(tmp_path), dpi=80)
    assert len(pngs) == 1
    assert pngs[0].endswith(".png")
    assert os.path.getsize(pngs[0]) > 0
