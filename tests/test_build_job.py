import json
from pdf_fill_studio.build_job import build_job


def test_build_job_xfa(tmp_path):
    out = tmp_path / "job.json"
    job = build_job("tests/fixtures/xfa_form.pdf", str(out))
    assert job["type"] in ("xfa-static", "xfa-dynamic")
    assert job["pdf"].endswith("xfa_form.pdf")
    assert any(f["id"] == "full_name" for f in job["fields"])
    reloaded = json.loads(out.read_text())
    assert reloaded["type"] == job["type"]


def test_build_job_shape(tmp_path):
    out = tmp_path / "job.json"
    job = build_job("tests/fixtures/flat_form.pdf", str(out))
    assert job["type"] == "flat"
    assert job["pdf"].endswith("flat_form.pdf")
    assert isinstance(job["pages"], list) and job["pages"][0]["page"] == 1
    assert any(f["label"] == "Nom:" for f in job["fields"])
    # File written and reloadable.
    reloaded = json.loads(out.read_text())
    assert reloaded["type"] == "flat"
