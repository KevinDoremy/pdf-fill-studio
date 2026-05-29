"""Read and fill XFA forms by editing the datasets XML packet. Uses lxml to preserve prefixes."""
import pikepdf
from lxml import etree
from pikepdf import String
from typing import NamedTuple, Optional

XFA_DATA_NS = "http://www.xfa.org/schema/xfa-data/1.0/"


def _datasets_index(xfa):
    """Index of the datasets stream in the XFA name/stream array, or None."""
    for i in range(0, len(xfa) - 1, 2):
        if str(xfa[i]) == "datasets":
            return i + 1
    return None


class _DatasetsResult(NamedTuple):
    """Parsed location of the XFA datasets packet inside a PDF.

    xfa_array:  the pikepdf Array that holds alternating name/stream pairs, or
                None when the XFA value is a single-stream object.
    array_idx:  index of the datasets stream inside xfa_array, or None when
                the XFA value is a single stream (stream is then datasets_stream).
    datasets_stream: the pikepdf.Stream for the datasets packet.
    raw:        raw bytes of the datasets XML.
    """
    xfa_array: Optional[pikepdf.Array]
    array_idx: Optional[int]
    datasets_stream: pikepdf.Stream
    raw: bytes


def _read_datasets(pdf) -> Optional[_DatasetsResult]:
    """Return a _DatasetsResult for the XFA datasets packet, or None if absent."""
    acro = pdf.Root.get("/AcroForm")
    if acro is None or "/XFA" not in acro:
        return None
    xfa = acro.XFA
    if isinstance(xfa, pikepdf.Stream):
        # single-stream XFA: the entire XFA lives in one stream
        return _DatasetsResult(
            xfa_array=None,
            array_idx=None,
            datasets_stream=xfa,
            raw=bytes(xfa.read_bytes()),
        )
    # array-style XFA: alternating (name, stream) pairs
    idx = _datasets_index(xfa)
    if idx is None:
        return None
    stream = xfa[idx]
    return _DatasetsResult(
        xfa_array=xfa,
        array_idx=idx,
        datasets_stream=stream,
        raw=bytes(stream.read_bytes()),
    )


def extract_xfa_fields(pdf_path):
    pdf = pikepdf.open(pdf_path)
    try:
        found = _read_datasets(pdf)
        if not found:
            return []
        root = etree.fromstring(found.raw)
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


def fill_xfa(pdf_path, values, out_path, xfa_type=None):
    """Inject {field_id: value} into the XFA datasets (matched by leaf element name) and set the
    matching AcroForm /V.

    NeedsRendering is only set when xfa_type is 'xfa-dynamic' (or when the PDF already has
    the flag set). Setting it on static XFA causes Adobe Reader to re-render from the
    template+datasets pipeline, which blanks out the injected values.

    Best-effort; call with xfa_type from detect_type for correct behaviour.
    """
    pdf = pikepdf.open(pdf_path)
    try:
        found = _read_datasets(pdf)
        if not found:
            raise ValueError("No XFA datasets packet found.")
        root = etree.fromstring(found.raw)
        data = root.find("{%s}data" % XFA_DATA_NS)
        scope = data if data is not None else root
        for el in scope.iter():
            tag = etree.QName(el).localname
            if tag in values and len(el) == 0:
                el.text = str(values[tag])
        new_xml = etree.tostring(root)
        found.datasets_stream.write(new_xml)
        # mirror into AcroForm /V so static viewers and Adobe show the values
        acro = pdf.Root.AcroForm
        for f in acro.get("/Fields", []):
            name = str(f.get("/T", ""))
            if name in values:
                f.V = String(str(values[name]))
        # NeedsRendering tells the viewer to re-render from template+datasets —
        # correct for dynamic XFA, but causes blanks on static XFA.
        if xfa_type == "xfa-dynamic":
            pdf.Root.NeedsRendering = True
        out = str(out_path)
        pdf.save(out)
    finally:
        pdf.close()
    return out
