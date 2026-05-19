import ELK from "elkjs/lib/elk.bundled.js";

const elk = new ELK();

// Default ELK preset. Не каждый алгоритм читает каждую настройку: ниже UI defs
// и buildLayoutOptions держат одну матрицу "algorithm -> supported options".
// Это защищает от ложных ползунков и от передачи layered-only параметров в
// force/stress/radial.
export const DEFAULT_OPTIONS = {
  algorithm: "layered",
  nodeNode: 110,
  betweenLayers: 150,
  edgeNode: 20,
  edgeEdge: 15,
  thoroughness: 10,
  forceIterations: 300,
  stressEdgeLength: 100,
  radialRadius: 0,
  nodePlacement: "BRANDES_KOEPF",
  layering: "NETWORK_SIMPLEX"
};

export const EDGE_ROUTING = "SPLINES";
const POLYLINE_ROUTING = "POLYLINE";

const DIRECTION_ALGORITHMS = new Set(["layered", "mrtree"]);

export function settingAppliesTo(def, algorithm = DEFAULT_OPTIONS.algorithm) {
  return !def.appliesTo || def.appliesTo.includes(algorithm);
}

export function supportsDirection(algorithm = DEFAULT_OPTIONS.algorithm) {
  return DIRECTION_ALGORITHMS.has(algorithm);
}

export function routingForAlgorithm(algorithm = DEFAULT_OPTIONS.algorithm) {
  return algorithm === "layered" ? EDGE_ROUTING : POLYLINE_ROUTING;
}

export const ALGORITHMS = [
  { value: "layered", label: "Layered (иерархия / поток)" },
  { value: "mrtree", label: "MrTree (строгое дерево)" },
  { value: "force", label: "Force (сеть без направления)" },
  { value: "stress", label: "Stress (равные расстояния)" },
  { value: "radial", label: "Radial (звезда / круг)" }
];

// appliesTo: null = опция работает независимо от алгоритма;
//           ["layered", ...] = только для перечисленных. Опции, которые ELK
//           игнорирует для текущего алгоритма, прячутся из UI, чтобы не
//           создавать впечатление «крутил — ничего не происходит».
export const SLIDER_DEFS = [
  {
    key: "betweenLayers",
    label: "Между слоями",
    hint: "elk.layered.spacing.nodeNodeBetweenLayers — расстояние между уровнями DAG",
    min: 40,
    max: 500,
    step: 5,
    appliesTo: ["layered"]
  },
  {
    key: "nodeNode",
    label: "Расстояние узлов",
    hint: "elk.spacing.nodeNode — между siblings в слое",
    min: 30,
    max: 400,
    step: 5,
    appliesTo: ["layered", "mrtree", "force", "radial"]
  },
  {
    key: "edgeNode",
    label: "Ребро ↔ узел",
    hint: "elk.spacing.edgeNode — зазор между рёбрами и чужими узлами",
    min: 5,
    max: 120,
    step: 1,
    appliesTo: ["layered", "mrtree"]
  },
  {
    key: "edgeEdge",
    label: "Ребро ↔ ребро",
    hint: "elk.spacing.edgeEdge — зазор между параллельными рёбрами",
    min: 5,
    max: 120,
    step: 1,
    appliesTo: ["layered"]
  },
  {
    key: "thoroughness",
    label: "Тщательность",
    hint: "elk.layered.thoroughness — глубина поиска. Больше = меньше пересечений, медленнее.",
    min: 1,
    max: 100,
    step: 1,
    appliesTo: ["layered"]
  },
  {
    key: "forceIterations",
    label: "Итерации force",
    hint: "elk.force.iterations — больше итераций = стабильнее сеть, но медленнее",
    min: 50,
    max: 1000,
    step: 25,
    appliesTo: ["force"]
  },
  {
    key: "stressEdgeLength",
    label: "Длина связи",
    hint: "elk.stress.desiredEdgeLength — желаемая длина ребра в stress layout",
    min: 40,
    max: 500,
    step: 5,
    appliesTo: ["stress"]
  },
  {
    key: "radialRadius",
    label: "Радиус уровня",
    hint: "elk.radial.radius — 0 значит auto; работает только на деревьях",
    min: 0,
    max: 800,
    step: 10,
    appliesTo: ["radial"]
  }
];

export const SELECT_DEFS = [
  {
    key: "algorithm",
    label: "Алгоритм",
    hint: "elk.algorithm — выбор алгоритма ELK под тип графа",
    options: ALGORITHMS,
    appliesTo: null
  },
  {
    key: "nodePlacement",
    label: "Размещение узлов",
    hint: "elk.layered.nodePlacement.strategy",
    options: [
      { value: "BRANDES_KOEPF", label: "Brandes-Köpf (по умолчанию)" },
      { value: "LINEAR_SEGMENTS", label: "Линейные сегменты" },
      { value: "NETWORK_SIMPLEX", label: "Network simplex" },
      { value: "SIMPLE", label: "Простое" }
    ],
    appliesTo: ["layered"]
  },
  {
    key: "layering",
    label: "Стратегия слоёв",
    hint: "elk.layered.layering.strategy — как узлы распределяются по слоям",
    options: [
      { value: "NETWORK_SIMPLEX", label: "Network simplex" },
      { value: "LONGEST_PATH", label: "Длиннейший путь" },
      { value: "COFFMAN_GRAHAM", label: "Coffman-Graham" }
    ],
    appliesTo: ["layered"]
  }
];

function isUndirectedTree(nodes, edges) {
  if (nodes.length === 0) return true;
  if (edges.length !== nodes.length - 1) return false;

  const nodeIds = new Set(nodes.map((n) => n.id));
  const adjacency = new Map(nodes.map((n) => [n.id, []]));
  for (const e of edges) {
    if (!nodeIds.has(e.source) || !nodeIds.has(e.target)) return false;
    adjacency.get(e.source).push(e.target);
    adjacency.get(e.target).push(e.source);
  }

  const seen = new Set();
  const stack = [nodes[0].id];
  while (stack.length > 0) {
    const id = stack.pop();
    if (seen.has(id)) continue;
    seen.add(id);
    for (const next of adjacency.get(id) ?? []) {
      if (!seen.has(next)) stack.push(next);
    }
  }
  return seen.size === nodes.length;
}

function assertAlgorithmCanLayout(algorithm, nodes, edges) {
  if (algorithm === "radial" && !isUndirectedTree(nodes, edges)) {
    throw new Error("ELK Radial работает только для дерева: нужна связная структура без циклов и multi-parent связей.");
  }
}

function buildLayoutOptions(o, direction) {
  const algorithm = o.algorithm ?? DEFAULT_OPTIONS.algorithm;
  const layoutOptions = {
    "elk.algorithm": algorithm,
    // ROOT-relative coords — упрощают перенос sections в React Flow без
    // компенсации parent-смещений.
    "elk.json.edgeCoords": "ROOT"
  };

  if (supportsDirection(algorithm)) {
    layoutOptions["elk.direction"] = direction;
  }

  if (algorithm === "layered") {
    return {
      ...layoutOptions,
      "elk.edgeRouting": EDGE_ROUTING,
      "elk.spacing.nodeNode": String(o.nodeNode),
      "elk.layered.spacing.nodeNode": String(o.nodeNode),
      "elk.layered.spacing.nodeNodeBetweenLayers": String(o.betweenLayers),
      "elk.spacing.edgeNode": String(o.edgeNode),
      "elk.layered.spacing.edgeNode": String(o.edgeNode),
      "elk.spacing.edgeEdge": String(o.edgeEdge),
      "elk.layered.spacing.edgeEdge": String(o.edgeEdge),
      "elk.layered.thoroughness": String(o.thoroughness),
      "elk.layered.nodePlacement.strategy": o.nodePlacement,
      "elk.layered.layering.strategy": o.layering,
      "elk.layered.nodePlacement.favorStraightEdges": "true",
      "elk.layered.nodePlacement.bk.edgeStraightening": "IMPROVE_STRAIGHTNESS",
      "elk.layered.unnecessaryBendpoints": "false"
    };
  }

  if (algorithm === "mrtree") {
    return {
      ...layoutOptions,
      "elk.spacing.nodeNode": String(o.nodeNode),
      "elk.spacing.edgeNode": String(o.edgeNode),
      "elk.mrtree.edgeRoutingMode": "AVOID_OVERLAP"
    };
  }

  if (algorithm === "force") {
    return {
      ...layoutOptions,
      "elk.spacing.nodeNode": String(o.nodeNode),
      "elk.force.iterations": String(o.forceIterations)
    };
  }

  if (algorithm === "stress") {
    return {
      ...layoutOptions,
      "elk.stress.desiredEdgeLength": String(o.stressEdgeLength)
    };
  }

  if (algorithm === "radial") {
    return {
      ...layoutOptions,
      "elk.spacing.nodeNode": String(o.nodeNode),
      "elk.radial.radius": String(o.radialRadius)
    };
  }

  return layoutOptions;
}

// ELK становится автором геометрии: считает позиции узлов И маршруты рёбер
// через edge.sections. React Flow рендерит из этих данных.
//
// Принципы:
// - Никаких pre-decided port sides. ELK с FREE ports сам выбирает где
//   рёбра входят/выходят.
// - Все рёбра передаются в ELK. Для layered back-edges допустимы: алгоритм
//   имеет cycle-breaking phase и сам разберётся.
// - Координаты приводим к ROOT через elk.json.edgeCoords чтобы у нас
//   была единая система отсчёта без относительных смещений.
export async function layoutWithELK(nodes, edges, options, direction = "DOWN") {
  const o = { ...DEFAULT_OPTIONS, ...(options ?? {}) };
  assertAlgorithmCanLayout(o.algorithm, nodes, edges);
  const layoutOptions = buildLayoutOptions(o, direction);

  const graph = {
    id: "root",
    layoutOptions,
    children: nodes.map((n) => ({
      id: n.id,
      width: n.data.layoutWidth ?? 360,
      height: n.data.layoutHeight ?? 200
      // Никаких ports / portConstraints — ELK имеет полную свободу.
    })),
    edges: edges.map((e) => ({
      id: e.id,
      sources: [e.source],
      targets: [e.target]
    }))
  };

  const layouted = await elk.layout(graph);
  const byId = new Map((layouted.children ?? []).map((c) => [c.id, c]));

  const positioned = nodes.map((n) => {
    const ln = byId.get(n.id);
    return {
      ...n,
      position: { x: ln?.x ?? 0, y: ln?.y ?? 0 }
    };
  });

  // Главный результат: маршруты рёбер из ELK. Каждое ребро — массив
  // sections с startPoint, bendPoints, endPoint.
  const routesMap = new Map();
  for (const e of layouted.edges ?? []) {
    if (e.sections && e.sections.length > 0) {
      routesMap.set(e.id, {
        sections: e.sections.map((s) => ({
          startPoint: { x: s.startPoint.x, y: s.startPoint.y },
          bendPoints: (s.bendPoints ?? []).map((p) => ({ x: p.x, y: p.y })),
          endPoint: { x: s.endPoint.x, y: s.endPoint.y }
        }))
      });
    }
  }

  return { nodes: positioned, routesMap };
}
