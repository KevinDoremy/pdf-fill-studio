"""Comb fields: detection of per-character cell runs and one-char-per-cell baking."""
import pdfplumber
from pdf_fill_studio.build_job import build_job
from pdf_fill_studio.guess_positions import guess_positions
from pdf_fill_studio.serve_editor import handle_export


def test_detect_comb_run():
    result = guess_positions("tests/fixtures/comb_form.pdf")
    combs = [f for f in result["fields"] if f["type"] == "comb"]
    assert len(combs) == 1
    assert len(combs[0]["cells"]) == 6
    assert "Code postal" in combs[0]["label"]


def test_comb_places_one_char_per_cell(tmp_path):
    job = build_job("tests/fixtures/comb_form.pdf", str(tmp_path / "job.json"))
    comb = next(f for f in job["fields"] if f["type"] == "comb")
    posted = {"fields": [
        {**f, "value": "H2T3G9"} if f["id"] == comb["id"] else f
        for f in job["fields"]
    ]}
    out = tmp_path / "filled.pdf"
    handle_export(job, posted, str(out))

    cells = comb["cells"]
    row_center = cells[0]["y"] + cells[0]["h"] / 2
    left, right = cells[0]["x"], cells[-1]["x"] + cells[-1]["w"]
    with pdfplumber.open(str(out)) as pdf:
        page = pdf.pages[0]
        row_chars = [
            c for c in page.chars
            if abs((c["top"] + c["bottom"]) / 2 - row_center) <= cells[0]["h"] / 2
            and left <= (c["x0"] + c["x1"]) / 2 <= right
        ]
        row_chars.sort(key=lambda c: c["x0"])
        assert "".join(c["text"] for c in row_chars) == "H2T3G9"
        # Each character's center falls inside its own cell.
        for cell, ch in zip(cells, row_chars):
            cx = (ch["x0"] + ch["x1"]) / 2
            assert cell["x"] <= cx <= cell["x"] + cell["w"]
