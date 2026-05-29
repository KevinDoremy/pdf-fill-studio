---
name: pdf-fill-studio
description: Fill any PDF locally and place each value precisely in a visual editor. Use when the user wants to fill out a PDF form, enter data into a PDF, complete a tax/insurance/bank form, or position text on a flat/scanned PDF. Currently handles flat (field-less) PDFs; leaves the signature blank for the user to sign.
---

# pdf-fill-studio

Fill a PDF and let the user place the values in a browser editor, then export a flattened PDF.

## When to use
The user gives you a PDF to fill. For flat PDFs (no form fields), follow the flow below.

## Flow
1. Detect the type: `python3 -m pdf_fill_studio.cli <input.pdf> -o out/<name>_rempli.pdf`
   - If detection reports `acroform` or `xfa`, tell the user that path is not in this version yet.
2. The CLI opens a local browser editor. Tell the user to type values, drag boxes into the
   boxes/lines, nudge with arrow keys, and click "Exporter le PDF". The signature is left blank.
3. The filled PDF is written to `out/`. The user signs it themselves.

## Rules
- Never fill a signature field.
- Never store or hard-code a SIN or a bank account number.
- Everything runs locally; no document is uploaded.
