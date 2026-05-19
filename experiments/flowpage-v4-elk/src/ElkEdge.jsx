import React from "react";
import { BaseEdge, EdgeLabelRenderer, getBezierPath } from "@xyflow/react";

// Builders для разных режимов ELK edgeRouting:
// - ORTHOGONAL / POLYLINE: bendPoints — это углы ломаной, рисуем через L
// - SPLINES: bendPoints — control points cubic Bezier. Каждая тройка
//   (c1, c2, anchor) = один cubic-сегмент. Последний остаток (0/1/2 точки)
//   обрабатываем как L / Q / C соответственно.

function fmt(p) {
  return `${p.x.toFixed(2)} ${p.y.toFixed(2)}`;
}

function buildPolylinePath(sections) {
  const pieces = [];
  for (const s of sections) {
    pieces.push(`M ${fmt(s.startPoint)}`);
    for (const b of s.bendPoints ?? []) pieces.push(`L ${fmt(b)}`);
    pieces.push(`L ${fmt(s.endPoint)}`);
  }
  return pieces.join(" ");
}

function buildSplinesPath(sections) {
  const pieces = [];
  for (const s of sections) {
    pieces.push(`M ${fmt(s.startPoint)}`);
    const bends = s.bendPoints ?? [];
    let i = 0;
    // Полные cubic-сегменты: тройки (c1, c2, anchor).
    while (i + 2 < bends.length) {
      pieces.push(`C ${fmt(bends[i])} ${fmt(bends[i + 1])} ${fmt(bends[i + 2])}`);
      i += 3;
    }
    const remaining = bends.length - i;
    // Финальный сегмент до endPoint, используя оставшиеся bend points как
    // control points если они есть.
    if (remaining === 0) {
      pieces.push(`L ${fmt(s.endPoint)}`);
    } else if (remaining === 1) {
      pieces.push(`Q ${fmt(bends[i])} ${fmt(s.endPoint)}`);
    } else if (remaining === 2) {
      pieces.push(`C ${fmt(bends[i])} ${fmt(bends[i + 1])} ${fmt(s.endPoint)}`);
    }
  }
  return pieces.join(" ");
}

function collectAllPoints(sections) {
  const all = [];
  for (const s of sections) {
    all.push(s.startPoint);
    for (const b of s.bendPoints ?? []) all.push(b);
    all.push(s.endPoint);
  }
  return all;
}

// ELK становится автором геометрии: считает позиции узлов И маршруты рёбер.
// Custom edge рисует SVG path из ELK sections, выбирая интерпретацию по
// data.routing (ORTHOGONAL/POLYLINE/SPLINES). Fallback на bezier когда
// sections отсутствуют (drag, до первого «Применить ELK»).
export function ElkEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  label,
  labelStyle,
  labelBgPadding,
  labelBgBorderRadius,
  markerEnd,
  style
}) {
  const sections = data?.elkSections;
  const routing = data?.routing ?? "ORTHOGONAL";
  const kind = data?.kind ?? "solid";
  let path;
  let midX;
  let midY;

  if (sections && sections.length > 0) {
    path = routing === "SPLINES" ? buildSplinesPath(sections) : buildPolylinePath(sections);
    // Approximate midpoint для label: середина списка всех точек.
    // Для splines это будет около кривой, точно на пути не гарантируется,
    // но визуально приемлемо.
    const allPoints = collectAllPoints(sections);
    const midIdx = Math.floor(allPoints.length / 2);
    if (allPoints.length % 2 === 0) {
      midX = (allPoints[midIdx - 1].x + allPoints[midIdx].x) / 2;
      midY = (allPoints[midIdx - 1].y + allPoints[midIdx].y) / 2;
    } else {
      midX = allPoints[midIdx].x;
      midY = allPoints[midIdx].y;
    }
  } else {
    const [bezierPath, bx, by] = getBezierPath({
      sourceX,
      sourceY,
      sourcePosition,
      targetX,
      targetY,
      targetPosition
    });
    path = bezierPath;
    midX = bx;
    midY = by;
  }

  const padX = Array.isArray(labelBgPadding) ? labelBgPadding[0] : 10;
  const padY = Array.isArray(labelBgPadding) ? labelBgPadding[1] : 6;

  // Варианты edge по data.kind. Через CSS-классы на BaseEdge path и
  // label-контейнер, чтобы можно было править стиль из styles.css.
  const edgeClass = `elk-edge elk-edge--${kind}`;
  const labelClass = `elk-edge-label elk-edge-label--${kind}`;

  return (
    <>
      <BaseEdge
        id={id}
        path={path}
        markerEnd={markerEnd}
        style={style}
        className={edgeClass}
      />
      {label ? (
        <EdgeLabelRenderer>
          <div
            className={labelClass}
            style={{
              position: "absolute",
              transform: `translate(-50%, -50%) translate(${midX}px, ${midY}px)`,
              padding: `${padY}px ${padX}px`,
              borderRadius: labelBgBorderRadius ?? 6,
              ...labelStyle
            }}
          >
            {label}
          </div>
        </EdgeLabelRenderer>
      ) : null}
    </>
  );
}

export const elkEdgeTypes = { elk: ElkEdge };
