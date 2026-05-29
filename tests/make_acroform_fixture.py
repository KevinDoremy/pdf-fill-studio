"""Deterministic fillable AcroForm PDF for tests."""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

OUT = "tests/fixtures/acroform_form.pdf"

def build(path=OUT):
    c = canvas.Canvas(path, pagesize=letter)
    W, H = letter
    c.setFont("Helvetica", 11)
    c.drawString(72, H - 100, "Full name:")
    c.acroForm.textfield(name="full_name", x=150, y=H - 105, width=240, height=18, borderWidth=1)
    c.drawString(72, H - 140, "Email:")
    c.acroForm.textfield(name="email", x=150, y=H - 145, width=240, height=18, borderWidth=1)
    c.drawString(72, H - 180, "Consent:")
    c.acroForm.checkbox(name="consent", x=150, y=H - 183, size=14, borderWidth=1)
    c.showPage(); c.save()

if __name__ == "__main__":
    build()
