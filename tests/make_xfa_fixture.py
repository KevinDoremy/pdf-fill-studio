"""Deterministic static-XFA PDF for tests: an AcroForm text field 'full_name' plus an XFA packet."""
import pikepdf
from pikepdf import String, Array
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

OUT = "tests/fixtures/xfa_form.pdf"
TEMPLATE = (b'<xdp:xdp xmlns:xdp="http://ns.adobe.com/xdp/"><template '
            b'xmlns="http://www.xfa.org/schema/xfa-template/3.0/"><subform name="form1">'
            b'<field name="full_name"><ui><textEdit/></ui></field></subform></template></xdp:xdp>')
DATASETS = (b'<xfa:datasets xmlns:xfa="http://www.xfa.org/schema/xfa-data/1.0/"><xfa:data>'
            b'<form1><full_name></full_name></form1></xfa:data></xfa:datasets>')

def build(path=OUT):
    base = path + ".base.tmp"
    c = canvas.Canvas(base, pagesize=letter)
    W, H = letter
    c.setFont("Helvetica", 11); c.drawString(72, H - 100, "Full name (XFA):")
    c.acroForm.textfield(name="full_name", x=180, y=H - 105, width=240, height=18, borderWidth=1)
    c.showPage(); c.save()
    pdf = pikepdf.open(base)
    pdf.Root.AcroForm.XFA = Array([
        String("template"), pikepdf.Stream(pdf, TEMPLATE),
        String("datasets"), pikepdf.Stream(pdf, DATASETS),
    ])
    pdf.save(path); pdf.close()
    import os; os.remove(base)

if __name__ == "__main__":
    build()
