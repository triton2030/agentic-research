import { MarkerType } from "@xyflow/react";
import { nodeSizes } from "../nodes";

// Initial grid-раскладка по контенту страницы. Используется как состояние до
// первого Apply ELK (если snapshot отсутствует). Тип ноды берётся из
// raw.type, default — "skillCard". Размер вычисляется через nodeSizes[type].

const DEFAULT_NODE_TYPE = "skillCard";

export function buildInitialNodes(rawNodes) {
  return rawNodes.map((raw, i) => {
    const type = raw.type ?? DEFAULT_NODE_TYPE;
    const sizeFn = nodeSizes[type];
    if (!sizeFn) {
      throw new Error(`buildInitialNodes: неизвестный nodeType "${type}" для узла "${raw.id}"`);
    }
    const { width, height } = sizeFn(raw);
    return {
      id: raw.id,
      type,
      position: { x: (i % 4) * (width + 80) + 80, y: Math.floor(i / 4) * (height + 80) + 80 },
      data: { ...raw, layoutWidth: width, layoutHeight: height },
      style: { width }
    };
  });
}

// Edge ID uniqueness: для параллельных рёбер от A к B префикс ${A}-${B}
// конфликтует. Добавляем индекс при повторе.
// Edge может быть либо tuple [source, target, label?] либо объект
// { source, target, label?, kind? } — kind пробрасывается в data для
// ElkEdge (solid/dashed/dotted/bold/dimmed/accent).
export function buildInitialEdges(rawEdges) {
  const seen = new Map();
  return rawEdges.map((raw) => {
    const obj = Array.isArray(raw)
      ? { source: raw[0], target: raw[1], label: raw[2] }
      : raw;
    const { source, target, label, kind } = obj;
    const baseId = `${source}-${target}`;
    const count = seen.get(baseId) ?? 0;
    seen.set(baseId, count + 1);
    const id = count === 0 ? baseId : `${baseId}#${count}`;
    return {
      id,
      type: "elk",
      source,
      target,
      sourceHandle: "s-b",
      targetHandle: "t-t",
      label,
      markerEnd: { type: MarkerType.ArrowClosed, width: 18, height: 18 },
      style: { strokeWidth: 2.2, stroke: "#43534d" },
      labelStyle: { fontSize: 14, fontWeight: 760 },
      labelBgPadding: [10, 6],
      labelBgBorderRadius: 6,
      data: { elkSections: null, kind: kind ?? "solid" }
    };
  });
}
