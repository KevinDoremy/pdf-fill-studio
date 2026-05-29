"""Render a PDF's pages to PNG images, for a visual self-check of placement.

Used by the skill flow: bake a draft, render it, look at the result, apply minimal
coordinate corrections if a value sits off its line/cell, then re-bake.
"""
import os
import shutil
import subprocess


def render(pdf_path, out_dir, dpi=130):
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.join(out_dir, "page")
    if shutil.which("pdftoppm"):
        subprocess.run(["pdftoppm", "-png", "-r", str(dpi), pdf_path, stem], check=True)
    else:
        from pdf2image import convert_from_path
        for i, img in enumerate(convert_from_path(pdf_path, dpi=dpi), start=1):
            img.save(f"{stem}-{i}.png")
    return sorted(
        os.path.join(out_dir, f)
        for f in os.listdir(out_dir)
        if f.startswith("page") and f.endswith(".png")
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("usage: python -m pdf_fill_studio.render_page <pdf> [out_dir]")
        raise SystemExit(2)
    pdf = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "out/preview"
    for path in render(pdf, out):
        print(path)
