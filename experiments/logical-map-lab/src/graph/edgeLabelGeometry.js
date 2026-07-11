export function estimateEdgeLabelSize(label) {
  const textLength = String(label ?? "").length;
  const width = Math.min(156, Math.max(92, textLength * 6.2 + 28));
  const lines = Math.max(1, Math.ceil(textLength / 18));

  return {
    width,
    height: 18 + lines * 14
  };
}

export function getCenteredBox(point, size) {
  return {
    left: point.x - size.width / 2,
    right: point.x + size.width / 2,
    top: point.y - size.height / 2,
    bottom: point.y + size.height / 2
  };
}

export function getBoxOverlapArea(box, frame, padding = 10) {
  const expandedFrame = {
    left: frame.x - padding,
    right: frame.x + frame.width + padding,
    top: frame.y - padding,
    bottom: frame.y + frame.height + padding
  };
  const x = Math.max(0, Math.min(box.right, expandedFrame.right) - Math.max(box.left, expandedFrame.left));
  const y = Math.max(0, Math.min(box.bottom, expandedFrame.bottom) - Math.max(box.top, expandedFrame.top));

  return x * y;
}
