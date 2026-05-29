"""Generates a deterministic flat PDF with comb fields (one box per character)
for tests: a postal-code row of 6 cells and a normal labelled line."""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

OUT = "tests/fixtures/comb_form.pdf"
CELL_W = 22
CELL_H = 26
GAP = 4


def build(path=OUT):
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter  # 612 x 792
    c.setFont("Helvetica", 11)

    # Normal labelled line (free text).
    c.drawString(72, height - 100, "Nom:")
    c.line(120, height - 103, 400, height - 103)

    # Comb field: "Code postal:" label, then 6 adjacent cells in a row.
    c.drawString(72, height - 150, "Code postal:")
    x0 = 160
    top = height - 165  # top of the cells in reportlab coords (bottom-left origin -> this is the BOTTOM of each rect)
    for i in range(6):
        x = x0 + i * (CELL_W + GAP)
        c.rect(x, top, CELL_W, CELL_H, stroke=1, fill=0)

    # Signature line.
    c.drawString(72, height - 230, "Signature:")
    c.line(150, height - 233, 400, height - 233)

    c.showPage()
    c.save()


if __name__ == "__main__":
    build()
