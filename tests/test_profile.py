from pdf_fill_studio.profile import match_fields, normalize

def test_normalize():
    assert normalize("Full name:") == "full_name"
    assert normalize("Code postal :") == "code_postal"

def test_match_and_sensitive():
    profile = {"full_name": "Marie Tremblay", "email": "m@x.com",
               "address": "123 Main St", "sin": "999-999-999"}
    fields = [
        {"id": "f1", "label": "Full name:"},
        {"id": "f2", "label": "Email:"},
        {"id": "f3", "label": "Address:"},
        {"id": "f4", "label": "SIN:"},            # sensitive -> never filled
        {"id": "f5", "label": "Amount claimed:"},  # not in profile -> unmatched
    ]
    values, unmatched = match_fields(fields, profile)
    assert values == {"f1": "Marie Tremblay", "f2": "m@x.com", "f3": "123 Main St"}
    assert "f4" in unmatched and "f5" in unmatched
