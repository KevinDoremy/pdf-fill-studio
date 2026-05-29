import json
import pytest
from unittest.mock import patch
from pdf_fill_studio.build_job import build_job


@pytest.mark.parametrize("xfa_type", ["xfa-static", "xfa-dynamic"])
def test_build_job_raises_for_xfa(tmp_path, xfa_type):
    out = tmp_path / "job.json"
    fake_info = {"type": xfa_type, "page_count": 1, "field_count": 0, "has_xfa": True, "xfa_dynamic": xfa_type == "xfa-dynamic"}
    with patch("pdf_fill_studio.build_job.detect_type", return_value=fake_info):
        with pytest.raises(NotImplementedError):
            build_job("tests/fixtures/flat_form.pdf", str(out))


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
