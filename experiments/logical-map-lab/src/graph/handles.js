export const HANDLE_SIDES = ["top", "right", "bottom", "left"];

export function sourceHandleId(side) {
  return `source-${side}`;
}

export function targetHandleId(side) {
  return `target-${side}`;
}

function closestSide(fromFrame, toFrame) {
  const dx = toFrame.centerX - fromFrame.centerX;
  const dy = toFrame.centerY - fromFrame.centerY;

  if (Math.abs(dx) >= Math.abs(dy)) {
    return dx >= 0 ? "right" : "left";
  }

  return dy >= 0 ? "bottom" : "top";
}

function closestFrameSide(point, frame) {
  const distances = [
    ["left", Math.abs(point.x - frame.x)],
    ["right", Math.abs(point.x - (frame.x + frame.width))],
    ["top", Math.abs(point.y - frame.y)],
    ["bottom", Math.abs(point.y - (frame.y + frame.height))]
  ];
  distances.sort((a, b) => a[1] - b[1]);
  return distances[0][0];
}

function getRouteHandleSides(edge, framesById, route) {
  const source = framesById.get(edge.source);
  const target = framesById.get(edge.target);
  const sections = route?.sections ?? [];
  const firstSection = sections[0];
  const lastSection = sections[sections.length - 1];

  if (!source || !target || !firstSection || !lastSection) return null;

  return {
    sourceSide: closestFrameSide(firstSection.startPoint, source),
    targetSide: closestFrameSide(lastSection.endPoint, target)
  };
}

export function getNearestEdgeHandles(edge, framesById, route = null) {
  const source = framesById.get(edge.source);
  const target = framesById.get(edge.target);
  const routeSides = getRouteHandleSides(edge, framesById, route);

  if (routeSides) {
    return {
      sourceHandle: sourceHandleId(routeSides.sourceSide),
      targetHandle: targetHandleId(routeSides.targetSide)
    };
  }

  if (!source || !target) {
    return {
      sourceHandle: sourceHandleId("right"),
      targetHandle: targetHandleId("left")
    };
  }

  return {
    sourceHandle: sourceHandleId(closestSide(source, target)),
    targetHandle: targetHandleId(closestSide(target, source))
  };
}
