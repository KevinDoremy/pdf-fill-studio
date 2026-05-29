---
name: pdf-fill-studio
description: Fill any PDF locally and place each value precisely in a visual editor. Use when the user wants to fill out a PDF form, enter data into a PDF, complete a tax/insurance/bank form, or position text on a flat/scanned PDF. Currently handles flat (field-less) PDFs; leaves the signature blank for the user to sign.
---

# pdf-fill-studio

Fill a PDF and let the user place the values in a browser editor, then export a flattened PDF.

## When to use
The user gives you a PDF to fill. For flat PDFs (no form fields), follow the flow below.

## Setup (once)
Dependencies live in a project venv (the system Python is usually externally managed):
`python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`

## Flow
1. Detect the type and start: `.venv/bin/python -m pdf_fill_studio.cli <input.pdf> -o out/<name>_filled.pdf`
2. **If detection reports `acroform`:**
   Run `.venv/bin/python -m pdf_fill_studio.cli <input.pdf> -o out/<name>_filled.pdf --profile <profile.json>`.
   The CLI fills matched fields automatically and prints "Needs manual input: [...]" for any field it
   could not match. Ask the user for each listed field, then re-run with a profile that includes
   those values. Render the result to verify.
3. **If detection reports `flat`:**
   The CLI opens a local browser editor. Tell the user to type values, drag boxes into the
   boxes/lines, nudge with arrow keys, and click "Export PDF". The signature is left blank.
   Comb fields (one box per character, e.g. postal code) are detected automatically and filled
   one character per cell; they are not draggable because the cells are already precise.
4. **If detection reports `xfa`:** tell the user that path is not in this version yet.
5. The filled PDF is written to `out/`. The user signs it themselves.

## Self-check (do this before declaring done)
Render the result and look at it, then fix small offsets:
`.venv/bin/python -m pdf_fill_studio.render_page out/<name>_filled.pdf out/preview`
Open the PNG(s). For each value, check it sits on its line / inside its cell, not too low and
not spilling outside. If something is off, apply minimal coordinate corrections to the job
(shift y up a few points, recenter) and re-bake. Repeat until it reads cleanly.

## Rules
- Never fill a signature field.
- Never store or hard-code a SIN or a bank account number.
- Everything runs locally; no document is uploaded.
