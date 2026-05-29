"""Read and fill XFA forms by editing the datasets XML packet. Uses lxml to preserve prefixes."""
import pikepdf
from lxml import etree
from pikepdf import String

XFA_DATA_NS = "http://www.xfa.org/schema/xfa-data/1.0/"


def _datasets_index(xfa):
    """Index of the datasets stream in the XFA name/stream array, or None."""
    for i in range(0, len(xfa) - 1, 2):
        if str(xfa[i]) == "datasets":
            return i + 1
    return None


def _read_datasets(pdf):
    acro = pdf.Root.get("/AcroForm")
    if acro is None or "/XFA" not in acro:
        return None
    xfa = acro.XFA
    if isinstance(xfa, pikepdf.Stream):     # single-stream form
        return xfa, None, bytes(xfa.read_bytes())
    idx = _datasets_index(xfa)
    if idx is None:
        return None
    return xfa, idx, bytes(xfa[idx].read_bytes())


def extract_xfa_fields(pdf_path):
    pdf = pikepdf.open(pdf_path)
    try:
        found = _read_datasets(pdf)
        if not found:
            return []
        _, _, raw = found
        root = etree.fromstring(raw)
        # data lives under xfa:data; every leaf element is a field
        data = root.find("{%s}data" % XFA_DATA_NS)
        scope = data if data is not None else root
        fields = []
        for el in scope.iter():
            if len(el) == 0 and el is not scope:        # leaf element
                tag = etree.QName(el).localname
                fields.append({"id": tag, "type": "text"})
        return fields
    finally:
        pdf.close()


def fill_xfa(pdf_path, values, out_path):
    """Inject {field_id: value} into the XFA datasets (matched by leaf element name) and set the
    matching AcroForm /V. Marks dynamic forms as needing re-render. Best-effort."""
    pdf = pikepdf.open(pdf_path)
    try:
        found = _read_datasets(pdf)
        if not found:
            raise ValueError("No XFA datasets packet found.")
        xfa, idx, raw = found
        root = etree.fromstring(raw)
        data = root.find("{%s}data" % XFA_DATA_NS)
        scope = data if data is not None else root
        for el in scope.iter():
            tag = etree.QName(el).localname
            if tag in values and len(el) == 0:
                el.text = str(values[tag])
        new = etree.tostring(root)
        if idx is None:               # single-stream XFA
            xfa.write(new)
        else:
            xfa[idx].write(new)
        # mirror into AcroForm /V so static viewers and Adobe show the values
        acro = pdf.Root.AcroForm
        for f in acro.get("/Fields", []):
            name = str(f.get("/T", ""))
            if name in values:
                f.V = String(str(values[name]))
        # dynamic XFA: tell the viewer to re-render from template+datasets
        pdf.Root.NeedsRendering = True
        out = str(out_path)
        pdf.save(out)
    finally:
        pdf.close()
    return out
