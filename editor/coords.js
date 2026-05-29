// Editor pixels -> PDF points (top-left origin). `scale` is pixels per point.
export function pxToPoints(px, scale) {
  return px / scale;
}

// Convert an absolutely-positioned box (CSS px, top-left) to PDF points.
export function boxPxToPoints(boxPx, scale) {
  return {
    x: pxToPoints(boxPx.left, scale),
    y: pxToPoints(boxPx.top, scale),
    w: pxToPoints(boxPx.width, scale),
    h: pxToPoints(boxPx.height, scale),
  };
}
