"""CLI entry point: pdf-fill-studio <input.pdf> [-o out.pdf] [--no-editor layout.json]"""
import argparse
import json
import os
from pdf_fill_studio.build_job import build_job
from pdf_fill_studio.serve_editor import serve, handle_export


def main(argv=None):
    parser = argparse.ArgumentParser(prog="pdf-fill-studio")
    parser.add_argument("pdf")
    parser.add_argument("-o", "--out", default=None)
    parser.add_argument("--no-editor", metavar="LAYOUT_JSON", default=None,
                        help="Skip the browser; bake from a saved layout JSON.")
    args = parser.parse_args(argv)

    out = args.out or os.path.join("out", os.path.basename(args.pdf).replace(".pdf", "_rempli.pdf"))
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

    job_path = os.path.join("out", "job.json")
    os.makedirs("out", exist_ok=True)
    job = build_job(args.pdf, job_path)

    if args.no_editor:
        posted = json.loads(open(args.no_editor, encoding="utf-8").read())
        handle_export(job, posted, out)
        print(f"Écrit : {out}")
        return

    serve(job, out)
    print(f"Écrit : {out}")


if __name__ == "__main__":
    main()
