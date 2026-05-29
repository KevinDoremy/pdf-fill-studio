from pdf_fill_studio.acroform import extract_acroform_fields
def test_extract():
    fields = extract_acroform_fields("tests/fixtures/acroform_form.pdf")
    by_id = {f["id"]: f for f in fields}
    assert by_id["full_name"]["type"] == "text"
    assert by_id["consent"]["type"] == "checkbox"
    assert all(f["page"] == 1 for f in fields)
