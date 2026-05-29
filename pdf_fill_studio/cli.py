"""CLI entry point: pdf-fill-studio <input.pdf> [-o out.pdf] [--no-editor layout.json]"""
import argparse
import json
import os
from pdf_fill_studio.build_job import build_job
from pdf_fill_studio.serve_editor import serve, handle_export
from pdf_fill_studio.acroform import fill_acroform
from pdf_fill_studio.xfa import fill_xfa
from pdf_fill_studio.profile import load_profile, match_fields


def main(argv=None):
    parser = argparse.ArgumentParser(prog="pdf-fill-studio")
    parser.add_argument("pdf")
    parser.add_argument("-o", "--out", default=None)
    parser.add_argument("--no-editor", metavar="LAYOUT_JSON", default=None,
                        help="Skip the browser; bake from a saved layout JSON.")
    parser.add_argument("--profile", metavar="PATH", default=None,
                        help="JSON profile for autofill.")
    args = parser.parse_args(argv)

    out = args.out or os.path.join("out", os.path.basename(args.pdf).replace(".pdf", "_filled.pdf"))
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

    job_path = os.path.join("out", "job.json")
    os.makedirs("out", exist_ok=True)
    job = build_job(args.pdf, job_path)

    if job["type"] == "acroform":
        profile = load_profile(args.profile) if args.profile else {}
        values, unmatched = match_fields(job["fields"], profile)
        fill_acroform(args.pdf, values, out)
        print("Wrote:", out)
        print("Needs manual input:", unmatched)
        return

    if job["type"].startswith("xfa"):
        profile = load_profile(args.profile) if args.profile else {}
        values, unmatched = match_fields(job["fields"], profile)
        fill_xfa(args.pdf, values, out)
        print("Wrote:", out)
        print("Needs manual input:", unmatched)
        print(
            "XFA form: values were injected. If your viewer shows blanks, open the output "
            "in free Adobe Reader (it re-renders XFA). Dynamic XFA that still fails should "
            "be filled directly in Adobe Reader."
        )
        return

    if args.profile:
        profile = load_profile(args.profile)
        values, _ = match_fields(job["fields"], profile)
        for field in job["fields"]:
            if field["id"] in values:
                field["value"] = values[field["id"]]

    if args.no_editor:
        posted = json.loads(open(args.no_editor, encoding="utf-8").read())
        handle_export(job, posted, out)
        print(f"Wrote: {out}")
        return

    serve(job, out)
    print(f"Wrote: {out}")


if __name__ == "__main__":
    main()
