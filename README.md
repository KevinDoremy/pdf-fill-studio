# pdf-fill-studio

> Fill any PDF on your machine, then drag every value into place.

pdf-fill-studio fills PDF forms locally and hands you a visual editor to fix the
placement. It detects how a PDF is built and fills it the right way. The filled
values show up over a browser preview of the real page. You drag them into the
boxes, nudge with the arrow keys, and export. Nothing leaves your machine. The
signature line stays empty so you sign it yourself.

### Why

Most forms you actually have to fill have no form fields. The text is right, it
just has to sit on the correct line, and getting there by typing coordinates is
slow. The hosted tools that do this upload your document to a server, which you
don't want for tax or insurance paperwork. This keeps everything local and gives
you a real editor instead.

### What it does

- Handles the three kinds of PDF forms: plain (text overlay), AcroForm (native
  fields), and XFA, with an Adobe Reader fallback for the dynamic XFA forms that
  defeat every headless library.
- Browser editor: drag values over the rendered page, 1px nudges with the arrow
  keys, signature left blank.
- Pulls known fields from a private profile you keep yourself, and asks you for
  whatever is missing. Never stores a SIN or a bank number.
- Ships as a Claude Code skill. MIT licensed, and it never touches the network.

## Status

MVP: flat PDFs. AcroForm, XFA, and profile autofill are on the roadmap.

## Install

```bash
git clone https://github.com/KevinDoremy/pdf-fill-studio
cd pdf-fill-studio
pip3 install -r requirements.txt
python3 -m pdf_fill_studio.cli path/to/form.pdf
```
