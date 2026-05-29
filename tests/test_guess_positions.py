from pdf_fill_studio.guess_positions import guess_positions

def test_finds_labels_with_entry_boxes():
    result = guess_positions("tests/fixtures/flat_form.pdf")
    assert len(result["pages"]) == 1
    page = result["pages"][0]
    assert page["page"] == 1
    assert round(page["width"]) == 612
    assert round(page["height"]) == 792

    labels = {f["label"] for f in result["fields"]}
    assert "Nom:" in labels
    assert "Adresse:" in labels
    assert "Signature:" in labels

    nom = next(f for f in result["fields"] if f["label"] == "Nom:")
    # Entry box starts to the RIGHT of the label and stays on its row.
    assert nom["x"] > 72
    assert nom["w"] > 0
    assert 90 < nom["y"] < 110   # ~100 pts from top (top-left origin)

def test_signature_label_is_tagged():
    result = guess_positions("tests/fixtures/flat_form.pdf")
    sig = next(f for f in result["fields"] if f["label"] == "Signature:")
    assert sig["type"] == "signature"
