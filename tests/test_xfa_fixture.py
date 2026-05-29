from pdf_fill_studio.detect_type import detect_type


def test_fixture_is_xfa():
    info = detect_type("tests/fixtures/xfa_form.pdf")
    assert info["has_xfa"] is True
    assert info["type"] in ("xfa-static", "xfa-dynamic")
