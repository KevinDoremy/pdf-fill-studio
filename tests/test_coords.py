from pdf_fill_studio.coords import topleft_box_to_baseline, px_to_points

def test_baseline_for_topleft_box():
    # page 792 tall; box top y=100 from top, height 16, font 11
    x, baseline = topleft_box_to_baseline(x=120, y=100, w=200, h=16, page_height=792, font_size=11)
    assert x == 120
    # baseline = 792 - 100 - 16 + 0.2*11 = 678.2
    assert round(baseline, 1) == 678.2

def test_px_to_points_uses_scale():
    # editor renders at 2 px per point; 240 px == 120 points
    assert px_to_points(240, scale=2.0) == 120.0
