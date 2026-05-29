"""Assemble job.json from detection + position guessing (flat path)."""
import json
import os
from pdf_fill_studio.detect_type import detect_type
from pdf_fill_studio.guess_positions import guess_positions
from pdf_fill_studio.acroform import extract_acroform_fields
from pdf_fill_studio.xfa import extract_xfa_fields


def build_job(pdf_path, out_path):
    info = detect_type(pdf_path)
    if info["type"] in ("xfa-static", "xfa-dynamic"):
        job = {
            "pdf": os.path.abspath(pdf_path),
            "type": info["type"],
            "fields": extract_xfa_fields(pdf_path),
        }
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(job, fh, ensure_ascii=False, indent=2)
        return job
    if info["type"] == "acroform":
        job = {
            "pdf": os.path.abspath(pdf_path),
            "type": "acroform",
            "fields": extract_acroform_fields(pdf_path),
        }
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(job, fh, ensure_ascii=False, indent=2)
        return job
    positions = guess_positions(pdf_path)
    job = {
        "pdf": os.path.abspath(pdf_path),
        "type": info["type"],
        "pages": positions["pages"],
        "fields": positions["fields"],
    }
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(job, fh, ensure_ascii=False, indent=2)
    return job
