"""Generates a deterministic flat PDF form (no AcroForm fields) for tests."""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

OUT = "tests/fixtures/flat_form.pdf"  # 612 x 792 points

def build(path=OUT):
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter  # 612, 792
    c.setFont("Helvetica", 11)
    # Labels with an entry line to their right (top-left visual layout).
    c.drawString(72, height - 100, "Nom:")
    c.line(120, height - 103, 400, height - 103)
    c.drawString(72, height - 130, "Adresse:")
    c.line(140, height - 133, 500, height - 133)
    c.drawString(72, height - 160, "Date:")
    c.line(120, height - 163, 250, height - 163)
    # A checkbox (small square) + label.
    c.rect(72, height - 200, 12, 12, stroke=1, fill=0)
    c.drawString(92, height - 198, "J'accepte")
    # A signature line.
    c.drawString(72, height - 260, "Signature:")
    c.line(150, height - 263, 400, height - 263)
    c.showPage()
    c.save()

if __name__ == "__main__":
    build()
