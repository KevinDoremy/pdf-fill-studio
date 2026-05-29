"""Heuristic field discovery for flat PDFs using pdfplumber.

Coordinates are PDF points, TOP-LEFT origin (pdfplumber's native `top`).

Two field kinds are produced:
- "text": a label with an entry area on the same row, to its right.
- "comb": a run of equal, evenly spaced cells (one box per character), e.g. a
  postal code or SIN; the value is later distributed one character per cell.
"signature" is a text field whose label matches a signature cue.
"""
import re
import pdfplumber

SIGNATURE_RE = re.compile(r"signature|sign[ée]?|signed", re.IGNORECASE)
DEFAULT_FONT_SIZE = 10
ROW_TOLERANCE = 6          # words within this vertical distance are on the same row
DEFAULT_ENTRY_WIDTH = 200  # points, when no following label/edge is found
GAP_AFTER_LABEL = 6        # points between label end and entry start
LINE_LEFT_PAD = 4          # small gap between the underline start and the value
MIN_LINE_LEN = 40          # a horizontal line must be at least this long to be an entry line

# Comb (per-character cell) detection.
COMB_MIN_CELLS = 3
CELL_MIN_W, CELL_MAX_W = 8, 45
CELL_MIN_H, CELL_MAX_H = 12, 45
COMB_TOP_TOL = 3           # cells in the same comb share a top within this
SIZE_TOL = 3               # cells in a comb share width/height within this
LABEL_ROW_TOL = 10         # a comb's label sits within this of the cell row


def _looks_like_label(text):
    # A label ends with a colon ("Nom:", "postal:"). Requiring the colon avoids
    # treating every short word (titles, prose) as a field. Non-colon labels are
    # a known limitation handled later via line/cell adjacency.
    return text.strip().endswith(":")


def _full_label(colon_word, words):
    """Join the contiguous words on the same row that form the label phrase ending at
    `colon_word` (e.g. "Nom complet:" rather than just "complet:")."""
    row_top = colon_word["top"]
    left = sorted(
        (w for w in words
         if w is not colon_word
         and abs(w["top"] - row_top) <= ROW_TOLERANCE
         and w["x1"] <= colon_word["x0"] + 1),
        key=lambda w: w["x0"],
    )
    phrase = [colon_word]
    prev_x0 = colon_word["x0"]
    for w in reversed(left):
        if 0 <= prev_x0 - w["x1"] <= 16:   # small gap => part of the same label
            phrase.insert(0, w)
            prev_x0 = w["x0"]
        else:
            break
    return " ".join(w["text"] for w in phrase)


def _cell_like(r):
    return (CELL_MIN_W <= r["width"] <= CELL_MAX_W and
            CELL_MIN_H <= r["height"] <= CELL_MAX_H)


def _detect_combs(rects):
    """Return runs of >= COMB_MIN_CELLS equal, evenly spaced cells (each run a list of rects)."""
    cells = sorted((r for r in rects if _cell_like(r)), key=lambda r: (round(r["top"]), r["x0"]))
    rows = []
    for r in cells:
        for row in rows:
            if abs(row[0]["top"] - r["top"]) <= COMB_TOP_TOL:
                row.append(r)
                break
        else:
            rows.append([r])

    combs = []
    for row in rows:
        row = sorted(row, key=lambda r: r["x0"])
        run = [row[0]]
        for prev, cur in zip(row, row[1:]):
            gap = cur["x0"] - prev["x1"]
            same_size = (abs(cur["width"] - run[0]["width"]) <= SIZE_TOL and
                         abs(cur["height"] - run[0]["height"]) <= SIZE_TOL)
            if same_size and -2 <= gap <= run[0]["width"] + 4:
                run.append(cur)
            else:
                if len(run) >= COMB_MIN_CELLS:
                    combs.append(run)
                run = [cur]
        if len(run) >= COMB_MIN_CELLS:
            combs.append(run)
    return combs


def _comb_field(run, words, used_word_ids, fid, pidx):
    cells = [{"x": round(c["x0"], 1), "y": round(c["top"], 1),
              "w": round(c["width"], 1), "h": round(c["height"], 1)} for c in run]
    row_top = run[0]["top"]
    run_x0 = run[0]["x0"]
    label_words = sorted(
        (w for w in words if abs(w["top"] - row_top) <= LABEL_ROW_TOL and w["x1"] <= run_x0 + 2),
        key=lambda w: w["x0"],
    )
    for w in label_words:
        used_word_ids.add(id(w))
    label = " ".join(w["text"] for w in label_words) or "Champ"
    left = cells[0]["x"]
    right = cells[-1]["x"] + cells[-1]["w"]
    top = min(c["y"] for c in cells)
    height = max(c["h"] for c in cells)
    return {
        "id": f"f{fid}",
        "page": pidx,
        "label": label,
        "type": "comb",
        "cells": cells,
        "x": left,
        "y": round(top, 1),
        "w": round(right - left, 1),
        "h": round(height, 1),
        "value": "",
        "font_size": DEFAULT_FONT_SIZE,
    }


def _horizontal_lines(page):
    """Long horizontal lines (entry underlines), as {x0, x1, top} in top-left points."""
    out = []
    for obj in list(page.lines) + list(page.edges):
        if abs(obj["top"] - obj["bottom"]) <= 1.5 and (obj["x1"] - obj["x0"]) >= MIN_LINE_LEN:
            out.append({"x0": obj["x0"], "x1": obj["x1"], "top": obj["top"]})
    return out


def _line_for_label(word, hlines):
    """The underline that belongs to a label: just below its baseline, extending right."""
    base = word["bottom"]
    cands = [L for L in hlines
             if -2 <= (L["top"] - base) <= 14 and L["x1"] > word["x1"]]
    if not cands:
        return None
    cands.sort(key=lambda L: abs(L["x0"] - word["x1"]))
    return cands[0]


def guess_positions(path):
    pages_out = []
    fields = []
    fid = 0
    with pdfplumber.open(path) as pdf:
        for pidx, page in enumerate(pdf.pages, start=1):
            pages_out.append({"page": pidx, "width": page.width, "height": page.height})
            words = page.extract_words(use_text_flow=False)
            words = sorted(words, key=lambda w: (round(w["top"]), w["x0"]))
            used_word_ids = set()
            hlines = _horizontal_lines(page)

            for run in _detect_combs(page.rects):
                fid += 1
                fields.append(_comb_field(run, words, used_word_ids, fid, pidx))

            for w in words:
                if id(w) in used_word_ids:
                    continue
                text = w["text"]
                if not _looks_like_label(text):
                    continue
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
                label = _full_label(w, words)
                ftype = "signature" if SIGNATURE_RE.search(label) else "text"
                fs = DEFAULT_FONT_SIZE
                line = _line_for_label(w, hlines)
                if line is not None:
                    # Snap to the underline: start at the line + a small gap, sit just above it.
                    box_x = round(max(line["x0"] + LINE_LEFT_PAD, w["x1"] + GAP_AFTER_LABEL), 1)
                    box_h = fs
                    box_y = round(line["top"] - 1 - box_h, 1)
                    box_w = round(line["x1"] - box_x, 1)
                else:
                    box_x = round(entry_x, 1)
                    box_y = round(w["top"], 1)
                    box_w = round(entry_w, 1)
                    box_h = round(w["bottom"] - w["top"], 1)
                fields.append({
                    "id": f"f{fid}",
                    "page": pidx,
                    "label": label,
                    "x": box_x,
                    "y": box_y,
                    "w": box_w,
                    "h": box_h,
                    "value": "",
                    "type": ftype,
                    "font_size": fs,
                })
    return {"pages": pages_out, "fields": fields}
