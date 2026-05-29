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

### What it does today

- Fills flat PDFs (no form fields) by overlaying text where it belongs.
- Browser editor: drag values over the rendered page, 1px nudges with the arrow
  keys, signature left blank.
- Runs as a Claude Code skill. MIT licensed, and it never touches the network at runtime.

### Roadmap

- AcroForm native-field fill and XFA, with an Adobe Reader fallback for the dynamic
  XFA forms that defeat every headless library.
- Profile autofill from a private file you keep yourself, asking only for what's
  missing. A SIN or bank number is never stored.

## Install

```bash
git clone https://github.com/KevinDoremy/pdf-fill-studio
cd pdf-fill-studio
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pdf_fill_studio.cli path/to/form.pdf
```
