import json
from unittest.mock import patch
from pypdf import PdfReader
from pdf_fill_studio.cli import main


def test_cli_acroform_autofill(tmp_path):
    prof = tmp_path / "p.json"
    prof.write_text(json.dumps({"full_name": "Marie Tremblay", "email": "m@x.com"}))
    out = tmp_path / "o.pdf"
    main(["tests/fixtures/acroform_form.pdf", "-o", str(out), "--profile", str(prof)])
    ff = PdfReader(str(out)).get_fields() or {}
    assert ff["full_name"]["/V"] == "Marie Tremblay"
    assert ff["email"]["/V"] == "m@x.com"


def test_cli_flat_profile_prefill(tmp_path):
    prof = tmp_path / "p.json"
    prof.write_text(json.dumps({"full_name": "Marie Tremblay", "address": "123 Main St"}))
    out = tmp_path / "o.pdf"
    captured = {}

    def fake_serve(job, out_path, **kwargs):
        captured["fields"] = {f["id"]: f["value"] for f in job["fields"]}

    with patch("pdf_fill_studio.cli.serve", fake_serve):
        main(["tests/fixtures/flat_form.pdf", "-o", str(out), "--profile", str(prof)])

    assert captured["fields"].get("f1") == "Marie Tremblay"
    assert captured["fields"].get("f2") == "123 Main St"
