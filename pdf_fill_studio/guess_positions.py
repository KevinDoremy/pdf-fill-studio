"""Heuristic field discovery for flat PDFs using pdfplumber.

Coordinates are PDF points, TOP-LEFT origin (pdfplumber's native `top`).
For each text label we propose an entry box on the same row, to the right of the label,
ending at the next label's x0 (or a default width).
"""
import re
import pdfplumber

SIGNATURE_RE = re.compile(r"signature|sign[ée]?|signed", re.IGNORECASE)
DEFAULT_FONT_SIZE = 10
ROW_TOLERANCE = 6          # words within this vertical distance are on the same row
DEFAULT_ENTRY_WIDTH = 200  # points, when no following label/edge is found
GAP_AFTER_LABEL = 6        # points between label end and entry start


def _looks_like_label(text):
    # Labels usually end with ":" or are short words; keep it permissive.
    return text.strip().endswith(":") or len(text.strip()) <= 24


def guess_positions(path):
    pages_out = []
    fields = []
    fid = 0
    with pdfplumber.open(path) as pdf:
        for pidx, page in enumerate(pdf.pages, start=1):
            pages_out.append({"page": pidx, "width": page.width, "height": page.height})
            words = page.extract_words(use_text_flow=False)
            words = sorted(words, key=lambda w: (round(w["top"]), w["x0"]))
            for w in words:
                text = w["text"]
                if not _looks_like_label(text):
                    continue
                # Find the next word on the same row to bound the entry box.
                row_top = w["top"]
                next_x = None
                for other in words:
                    if other is w:
                        continue
                    if abs(other["top"] - row_top) <= ROW_TOLERANCE and other["x0"] > w["x1"]:
                        next_x = other["x0"] if next_x is None else min(next_x, other["x0"])
                entry_x = w["x1"] + GAP_AFTER_LABEL
                entry_w = (next_x - entry_x) if next_x else DEFAULT_ENTRY_WIDTH
                if entry_w < 30:
                    entry_w = DEFAULT_ENTRY_WIDTH
                fid += 1
                ftype = "signature" if SIGNATURE_RE.search(text) else "text"
                fields.append({
                    "id": f"f{fid}",
                    "page": pidx,
                    "label": text,
                    "x": round(entry_x, 1),
                    "y": round(w["top"], 1),
                    "w": round(entry_w, 1),
                    # Height = the label's own text height so the baked baseline lines up
                    # with the label baseline (value sits on the line, not below it).
                    "h": round(w["bottom"] - w["top"], 1),
                    "value": "",
                    "type": ftype,
                    "font_size": DEFAULT_FONT_SIZE,
                })
    return {"pages": pages_out, "fields": fields}
