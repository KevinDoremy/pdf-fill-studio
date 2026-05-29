"""Coordinate conversions. job.json uses PDF points, TOP-LEFT origin (y grows downward)."""

def topleft_box_to_baseline(x, y, w, h, page_height, font_size):
    """Convert a top-left-origin box to a reportlab text anchor (bottom-left origin).

    Returns (x, baseline_y) where baseline_y is where reportlab should draw the text
    so it sits near the bottom of the box with a small descent allowance.
    """
    baseline_y = page_height - y - h + 0.2 * font_size
    return x, baseline_y

def px_to_points(value_px, scale):
    """Editor pixels -> PDF points. `scale` is pixels per point (the pdf.js viewport scale)."""
    return value_px / scale
