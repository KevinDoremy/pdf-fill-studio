"""MCP server exposing pdf-fill-studio over the Model Context Protocol.

Optional feature: install with `pip install pdf-fill-studio[mcp]`, run with `pdf-fill-studio-mcp`.
Everything runs locally; no document leaves the machine.
"""
import os
from mcp.server.fastmcp import FastMCP

from pdf_fill_studio.detect_type import detect_type
from pdf_fill_studio.acroform import extract_acroform_fields, fill_acroform
from pdf_fill_studio.xfa import extract_xfa_fields, fill_xfa
from pdf_fill_studio.build_job import build_job
from pdf_fill_studio.bake_overlay import bake_overlay

mcp = FastMCP("pdf-fill-studio")


@mcp.tool()
def detect_pdf_type(pdf_path: str) -> dict:
    """Detect a PDF's form type: flat, acroform, xfa-static, or xfa-dynamic (plus field counts)."""
    return detect_type(pdf_path)


@mcp.tool()
def list_fields(pdf_path: str) -> list:
    """List fillable fields. AcroForm: native field names and types. XFA: datasets leaf names. Flat: guessed labels."""
    info = detect_type(pdf_path)
    if info["type"] == "acroform":
        return extract_acroform_fields(pdf_path)
    if info["type"].startswith("xfa"):
        return extract_xfa_fields(pdf_path)
    if info["type"] == "flat":
        job = build_job(pdf_path, os.path.join(os.path.dirname(os.path.abspath(pdf_path)), "_job.json"))
        return [{"id": f["id"], "label": f["label"], "type": f["type"]} for f in job["fields"]]
    return []


@mcp.tool()
def fill_xfa_fields(pdf_path: str, values: dict, out_path: str) -> str:
    """Fill XFA form fields by injecting values into the datasets packet and setting AcroForm /V.
    Open the result in free Adobe Reader if your viewer shows blanks (it re-renders XFA)."""
    info = detect_type(pdf_path)
    return fill_xfa(pdf_path, values, out_path, xfa_type=info["type"])


@mcp.tool()
def fill_acroform_fields(pdf_path: str, values: dict, out_path: str) -> str:
    """Fill native AcroForm fields from {field_name: value} and write out_path."""
    return fill_acroform(pdf_path, values, out_path)


@mcp.tool()
def fill_flat_text(pdf_path: str, items: list, out_path: str) -> str:
    """Fill a flat PDF by overlaying text. items = [{"label": "...", "value": "..."}]; each value is
    placed on the line of the matching label. Signature fields are always left blank."""
    job = build_job(pdf_path, os.path.join(os.path.dirname(os.path.abspath(out_path)), "_job.json"))
    want = {it["label"]: it["value"] for it in items}
    for f in job["fields"]:
        if f.get("label") in want:
            f["value"] = want[f["label"]]
    bake_overlay(job, out_path)
    return out_path


def main():
    mcp.run()


if __name__ == "__main__":
    main()
