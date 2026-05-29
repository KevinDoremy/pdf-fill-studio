# Changelog

## 0.3.1
- Add this changelog. First release published via the automated GitHub Actions + PyPI trusted-publishing pipeline.

## 0.3.0
- pip-installable (`pip install pdf-fill-studio`), editor bundled in the package.
- Installable as a Claude Code plugin/marketplace.
- Optional MCP server (`pip install "pdf-fill-studio[mcp]"`, `pdf-fill-studio-mcp`).
- CI on push; tag-driven release pipeline.

## 0.2.0
- Native AcroForm field fill (text + checkbox).
- Profile autofill from a private JSON; SIN/bank/card never stored or filled.

## 0.1.1
- Values snap to the underline (start of line, just above it).
- Per-character (comb) fields: one character centered per cell.
- Colon-only and full multi-word label detection. English editor UI.

## 0.1.0
- Fill flat PDFs by text overlay; local browser editor (drag + arrow-key nudge); signature left blank.
- 100% local, no network at runtime. MIT.
