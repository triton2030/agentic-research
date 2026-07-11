import { BaseEdge, EdgeLabelRenderer, getBezierPath } from "@xyflow/react";
import { estimateEdgeLabelSize, getBoxOverlapArea, getCenteredBox } from "../graph/edgeLabelGeometry.js";

function formatPoint(point) {
  return `${point.x.toFixed(2)} ${point.y.toFixed(2)}`;
}

function buildPolylinePath(sections) {
  const pieces = [];

  for (const section of sections) {
    pieces.push(`M ${formatPoint(section.startPoint)}`);
    for (const bendPoint of section.bendPoints ?? []) {
      pieces.push(`L ${formatPoint(bendPoint)}`);
    }
    pieces.push(`L ${formatPoint(section.endPoint)}`);
  }

  return pieces.join(" ");
}

function buildSplinePath(sections) {
  const pieces = [];

  for (const section of sections) {
    pieces.push(`M ${formatPoint(section.startPoint)}`);
    const bends = section.bendPoints ?? [];
    let index = 0;

    while (index + 2 < bends.length) {
      pieces.push(`C ${formatPoint(bends[index])} ${formatPoint(bends[index + 1])} ${formatPoint(bends[index + 2])}`);
      index += 3;
    }

    const remaining = bends.length - index;
    if (remaining === 0) {
      pieces.push(`L ${formatPoint(section.endPoint)}`);
    } else if (remaining === 1) {
      pieces.push(`Q ${formatPoint(bends[index])} ${formatPoint(section.endPoint)}`);
    } else if (remaining === 2) {
      pieces.push(`C ${formatPoint(bends[index])} ${formatPoint(bends[index + 1])} ${formatPoint(section.endPoint)}`);
    }
  }

  return pieces.join(" ");
}

function collectSectionPoints(sections) {
  const points = [];

  for (const section of sections) {
    points.push(section.startPoint);
    for (const bendPoint of section.bendPoints ?? []) {
      points.push(bendPoint);
    }
    points.push(section.endPoint);
  }

  return points;
}

function interpolatePoint(a, b, ratio) {
  return {
    x: a.x + (b.x - a.x) * ratio,
    y: a.y + (b.y - a.y) * ratio
  };
}

function pointOnPolyline(points, ratio) {
  if (points.length === 0) return { x: 0, y: 0 };
  if (points.length === 1) return points[0];

  const segments = [];
  let total = 0;

  for (let index = 0; index < points.length - 1; index += 1) {
    const start = points[index];
    const end = points[index + 1];
    const length = Math.hypot(end.x - start.x, end.y - start.y);
    segments.push({ start, end, length });
    total += length;
  }

  if (total === 0) return points[0];

  let distance = total * ratio;
  for (const segment of segments) {
    if (distance <= segment.length) {
      return interpolatePoint(segment.start, segment.end, distance / segment.length);
    }
    distance -= segment.length;
  }

  return points.at(-1);
}

function getLabelOffsets(size) {
  const horizontal = size.width * 0.65 + 26;
  const vertical = size.height * 0.85 + 26;

  return [
    { x: 0, y: 0, penalty: 0 },
    { x: 0, y: -vertical, penalty: vertical },
    { x: 0, y: vertical, penalty: vertical },
    { x: -horizontal, y: 0, penalty: horizontal },
    { x: horizontal, y: 0, penalty: horizontal },
    { x: -horizontal * 0.75, y: -vertical * 0.75, penalty: Math.hypot(horizontal, vertical) },
    { x: horizontal * 0.75, y: -vertical * 0.75, penalty: Math.hypot(horizontal, vertical) },
    { x: -horizontal * 0.75, y: vertical * 0.75, penalty: Math.hypot(horizontal, vertical) },
    { x: horizontal * 0.75, y: vertical * 0.75, penalty: Math.hypot(horizontal, vertical) }
  ];
}

function chooseLabelPoint({ fallbackPoint, label, nodeFrames, points }) {
  const size = estimateEdgeLabelSize(label);
  const ratios = [0.5, 0.36, 0.64, 0.24, 0.76, 0.14, 0.86];
  const offsets = getLabelOffsets(size);
  const candidates = ratios.flatMap((ratio) => {
    const basePoint = ratio === 0.5 && fallbackPoint ? fallbackPoint : pointOnPolyline(points, ratio);

    return offsets.map((offset) => ({
      ratio,
      offsetPenalty: offset.penalty,
      point: {
        x: basePoint.x + offset.x,
        y: basePoint.y + offset.y
      }
    }));
  });

  return candidates
    .map((candidate) => {
      const box = getCenteredBox(candidate.point, size);
      const overlap = nodeFrames.reduce((sum, frame) => sum + getBoxOverlapArea(box, frame), 0);
      return {
        ...candidate,
        overlap,
        centerPenalty: Math.abs(candidate.ratio - 0.5)
      };
    })
    .sort((a, b) => a.overlap - b.overlap || a.offsetPenalty - b.offsetPenalty || a.centerPenalty - b.centerPenalty)[0].point;
}

export function CausalEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  markerEnd,
  style,
  data
}) {
  const sections = data.elkSections;
  const hasElkRoute = sections && sections.length > 0;
  const fallback = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
    curvature: 0.32
  });
  const edgePath = hasElkRoute
    ? data.routing === "SPLINES"
      ? buildSplinePath(sections)
      : buildPolylinePath(sections)
    : fallback[0];
  const fallbackPoint = { x: fallback[1], y: fallback[2] };
  const points = hasElkRoute
    ? collectSectionPoints(sections)
    : [
        { x: sourceX, y: sourceY },
        { x: targetX, y: targetY }
      ];
  const labelPoint =
    data.elkLabelCenter ??
    chooseLabelPoint({
      fallbackPoint,
      label: data.label,
      nodeFrames: data.nodeFrames ?? [],
      points
    });

  return (
    <>
      <BaseEdge id={id} path={edgePath} markerEnd={markerEnd} style={style} interactionWidth={32} />
      <EdgeLabelRenderer>
        <button
          type="button"
          className={`causal-edge-label nodrag nopan ${data.dimmed ? "causal-edge-label--dimmed" : ""}`}
          style={{
            transform: `translate(-50%, -50%) translate(${labelPoint.x}px, ${labelPoint.y}px)`,
            "--edge-color": data.color
          }}
          onClick={(event) => {
            event.stopPropagation();
            data.onSelect(id);
          }}
        >
          {data.label}
        </button>
      </EdgeLabelRenderer>
    </>
  );
}
