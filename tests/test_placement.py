"""Regression test: the baked value baseline should line up with its label baseline,
so values sit on the line by default and need little or no manual nudging."""
import pdfplumber
from pdf_fill_studio.build_job import build_job
from pdf_fill_studio.serve_editor import handle_export


def test_value_baseline_aligns_with_label(tmp_path):
    job = build_job("tests/fixtures/flat_form.pdf", str(tmp_path / "job.json"))
    posted = {"fields": [
        {**f, "value": "ZZVALUE"} if f["label"] == "Nom:" else f
        for f in job["fields"]
    ]}
    out = tmp_path / "filled.pdf"
    handle_export(job, posted, str(out))

    with pdfplumber.open(str(out)) as pdf:
        words = pdf.pages[0].extract_words()
        label = next(w for w in words if w["text"].startswith("Nom"))
        value = next(w for w in words if "ZZVALUE" in w["text"])
        # Baselines (word bottom) within 3 points => visually on the same line.
        assert abs(label["bottom"] - value["bottom"]) <= 3
