import ELK from "elkjs/lib/elk.bundled.js";
import { estimateEdgeLabelSize } from "./edgeLabelGeometry.js";

const elk = new ELK();

export const DEFAULT_EDGE_ROUTING = "SPLINES";
export const GRAPH_NODE_FRAME = {
  width: 242,
  height: 96
};

export const DEFAULT_OPTIONS = {
  direction: "RIGHT",
  edgeRouting: DEFAULT_EDGE_ROUTING,
  nodeNode: 110,
  betweenLayers: 70,
  edgeNode: 24,
  edgeEdge: 18,
  thoroughness: 12,
  nodePlacement: "BRANDES_KOEPF",
  layering: "NETWORK_SIMPLEX"
};

export const DIRECTION_OPTIONS = [
  { value: "DOWN", label: "Вниз" },
  { value: "RIGHT", label: "Вправо" },
  { value: "LEFT", label: "Влево" },
  { value: "UP", label: "Вверх" }
];

export const EDGE_ROUTING_OPTIONS = [
  { value: "SPLINES", label: "Гибкие кривые" },
  { value: "ORTHOGONAL", label: "Умные изгибы" },
  { value: "POLYLINE", label: "Ломаная" }
];

export const SLIDER_DEFS = [
  {
    key: "betweenLayers",
    label: "Между слоями",
    hint: "Расстояние между причинными слоями",
    min: 40,
    max: 340,
    step: 5
  },
  {
    key: "nodeNode",
    label: "Между нодами",
    hint: "Расстояние между соседними нодами",
    min: 30,
    max: 260,
    step: 5
  },
  {
    key: "edgeNode",
    label: "Ребро к ноде",
    hint: "Зазор между рёбрами и близкими нодами",
    min: 5,
    max: 90,
    step: 1
  },
  {
    key: "edgeEdge",
    label: "Между рёбрами",
    hint: "Зазор между параллельными рёбрами",
    min: 5,
    max: 90,
    step: 1
  },
  {
    key: "thoroughness",
    label: "Тщательность",
    hint: "Больше попыток может уменьшить пересечения; медленнее на больших графах",
    min: 1,
    max: 80,
    step: 1
  }
];

export const SELECT_DEFS = [
  {
    key: "direction",
    label: "Направление",
    hint: "Основное направление чтения",
    options: DIRECTION_OPTIONS
  },
  {
    key: "edgeRouting",
    label: "Маршрут рёбер",
    hint: "SPLINES дают живые кривые; orthogonal оставлен как ручной режим",
    options: EDGE_ROUTING_OPTIONS
  },
  {
    key: "nodePlacement",
    label: "Размещение нод",
    hint: "Стратегия размещения нод в ELK layered",
    options: [
      { value: "BRANDES_KOEPF", label: "Brandes-Koepf" },
      { value: "LINEAR_SEGMENTS", label: "Линейные сегменты" },
      { value: "NETWORK_SIMPLEX", label: "Network simplex" },
      { value: "SIMPLE", label: "Простое" }
    ]
  },
  {
    key: "layering",
    label: "Слои",
    hint: "Стратегия назначения слоёв в ELK layered",
    options: [
      { value: "NETWORK_SIMPLEX", label: "Network simplex" },
      { value: "LONGEST_PATH", label: "Длиннейший путь" },
      { value: "COFFMAN_GRAHAM", label: "Coffman-Graham" }
    ]
  }
];

function buildLayoutOptions(options) {
  return {
    "elk.algorithm": "layered",
    "elk.direction": options.direction,
    "elk.edgeRouting": options.edgeRouting,
    "elk.json.edgeCoords": "ROOT",
    "elk.json.shapeCoords": "ROOT",
    "elk.spacing.nodeNode": String(options.nodeNode),
    "elk.layered.spacing.nodeNodeBetweenLayers": String(options.betweenLayers),
    "elk.spacing.edgeNode": String(options.edgeNode),
    "elk.layered.spacing.edgeNodeBetweenLayers": String(options.edgeNode),
    "elk.spacing.edgeEdge": String(options.edgeEdge),
    "elk.layered.spacing.edgeEdgeBetweenLayers": String(options.edgeEdge),
    "elk.layered.thoroughness": String(options.thoroughness),
    "elk.layered.nodePlacement.strategy": options.nodePlacement,
    "elk.layered.layering.strategy": options.layering,
    "elk.layered.crossingMinimization.strategy": "LAYER_SWEEP",
    "elk.layered.nodePlacement.favorStraightEdges": "true",
    "elk.layered.nodePlacement.bk.edgeStraightening": "IMPROVE_STRAIGHTNESS",
    "elk.layered.unnecessaryBendpoints": "false",
    "elk.edgeLabels.placement": "CENTER",
    "elk.edgeLabels.inline": "true",
    "elk.spacing.edgeLabel": "8"
  };
}

export function getNodeFrame() {
  return GRAPH_NODE_FRAME;
}

function offsetPoint(point, offsetX, offsetY) {
  return { x: point.x + offsetX, y: point.y + offsetY };
}

function isFiniteNumber(value) {
  return typeof value === "number" && Number.isFinite(value);
}

function extractLabelCenter(edge, offsetX, offsetY) {
  const label = edge.labels?.[0];
  if (!label || !isFiniteNumber(label.x) || !isFiniteNumber(label.y) || !isFiniteNumber(label.width) || !isFiniteNumber(label.height)) {
    return null;
  }

  return {
    x: label.x + label.width / 2 + offsetX,
    y: label.y + label.height / 2 + offsetY
  };
}

function extractEdgeLayouts(edges = [], offsetX, offsetY) {
  const edgeLayouts = new Map();

  for (const edge of edges) {
    const sections =
      edge.sections?.map((section) => ({
        startPoint: offsetPoint(section.startPoint, offsetX, offsetY),
        bendPoints: (section.bendPoints ?? []).map((point) => offsetPoint(point, offsetX, offsetY)),
        endPoint: offsetPoint(section.endPoint, offsetX, offsetY)
      })) ?? [];
    const labelCenter = extractLabelCenter(edge, offsetX, offsetY);

    if (sections.length > 0 || labelCenter) {
      edgeLayouts.set(edge.id, { sections, labelCenter });
    }
  }

  return edgeLayouts;
}

export async function layoutGraph(nodes, edges, options = DEFAULT_OPTIONS) {
  const resolvedOptions = { ...DEFAULT_OPTIONS, ...options };
  const frame = getNodeFrame();
  const graph = {
    id: "root",
    layoutOptions: buildLayoutOptions(resolvedOptions),
    children: nodes.map((node) => ({
      id: node.id,
      width: frame.width,
      height: frame.height
    })),
    edges: edges.map((edge) => {
      const labelSize = estimateEdgeLabelSize(edge.label);

      return {
        id: edge.id,
        sources: [edge.source],
        targets: [edge.target],
        labels: [
          {
            id: `${edge.id}:label`,
            text: edge.label ?? "",
            ...labelSize
          }
        ]
      };
    })
  };

  const result = await elk.layout(graph);
  const children = result.children ?? [];
  const minX = children.length > 0 ? Math.min(...children.map((node) => node.x ?? 0)) : 0;
  const minY = children.length > 0 ? Math.min(...children.map((node) => node.y ?? 0)) : 0;
  const offsetX = -minX + 72;
  const offsetY = -minY + 56;
  const positions = new Map(
    children.map((node) => [node.id, { x: (node.x ?? 0) + offsetX, y: (node.y ?? 0) + offsetY }])
  );
  const edgeLayouts = extractEdgeLayouts(result.edges, offsetX, offsetY);

  return {
    nodes: nodes.map((node) => ({
      ...node,
      position: positions.get(node.id) ?? { x: 0, y: 0 },
      layoutWidth: frame.width,
      layoutHeight: frame.height
    })),
    edgeLayouts,
    routesMap: edgeLayouts,
    routing: resolvedOptions.edgeRouting
  };
}
