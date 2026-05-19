import React, { memo, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Background,
  Controls,
  Handle,
  MarkerType,
  MiniMap,
  Panel,
  Position,
  ReactFlow,
  ReactFlowProvider,
  useReactFlow,
  useStoreApi
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import {
  forceCenter,
  forceLink,
  forceManyBody,
  forceSimulation,
  forceX,
  forceY
} from "d3-force";
import ELK from "elkjs/lib/elk.bundled.js";
import { Layout as ColaLayout } from "webcola";
import "./styles.css";

const elk = new ELK();

const NODE_WIDTH = 360;
const READABLE_ZOOM = 0.92;
const DEFAULT_FORCE_SETTINGS = {
  repulsion: 1120,
  linkDistance: 300,
  nodeGap: 46
};
const HANDLE_SIDES = [
  { id: "top", position: Position.Top },
  { id: "right", position: Position.Right },
  { id: "bottom", position: Position.Bottom },
  { id: "left", position: Position.Left }
];

function estimateNodeHeight(node) {
  const bodyLines = Math.ceil(node.body.length / 42);
  const chipUnits = node.bullets.reduce((sum, item) => sum + item.length + 3, 0);
  const chipRows = Math.max(1, Math.ceil(chipUnits / 32));
  return Math.max(168, Math.min(286, 92 + bodyLines * 24 + chipRows * 38));
}

const rawNodes = [
  {
    id: "request",
    kind: "origin",
    title: "Запрос",
    kicker: "intent",
    body: "Пользователь формулирует желание обычным языком. Агент сначала восстанавливает смысл, а не бежит по первому техническому маршруту.",
    bullets: ["цель", "риски", "один следующий шаг"]
  },
  {
    id: "agents",
    kind: "instruction",
    title: "AGENTS.md",
    kicker: "верхняя рамка",
    body: "Роль, язык, запреты, placement rules и маршруты. Это не рабочий алгоритм, а контракт поведения для всей сессии.",
    bullets: ["сооснователь", "русский язык", "не плодить surfaces"]
  },
  {
    id: "criteria",
    kind: "memory",
    title: "_ops/criteria",
    kicker: "память качества",
    body: "Критерии выбираются по типу работы. Они отвечают не за красивый текст, а за повторяемые правила приёмки.",
    bullets: ["user-backed", "будущие проверки", "без backlog"]
  },
  {
    id: "router",
    kind: "skill",
    title: "1start-here",
    kicker: "маршрутизатор",
    body: "Классифицирует форму запроса и выбирает один активный маршрут: разговор, стратегия, правка, ревью или системная работа.",
    bullets: ["один active skill", "без preload", "ясная граница"]
  },
  {
    id: "active",
    kind: "skill",
    title: "Активный скилл",
    kicker: "рабочий слой",
    body: "Ведёт конкретный тип работы: Obsidian UX, instruction layer, task scope, user truth, roadmap или review.",
    bullets: ["owner", "stop rule", "verification"]
  },
  {
    id: "writeGate",
    kind: "gate",
    title: "Instruction/criteria gate",
    kicker: "перед записью",
    body: "Перед содержательной правкой связывает owner, target files, применимые criteria и риск рассинхрона.",
    bullets: ["owner", "criteria", "drift risk"]
  },
  {
    id: "artifact",
    kind: "output",
    title: "Артефакт",
    kicker: "результат",
    body: "Заметка, граф, скрипт, страница или инструкция. Главное: не становиться вторым источником правды без причины.",
    bullets: ["readable", "owned", "verifiable"]
  },
  {
    id: "obsidian",
    kind: "surface",
    title: "Obsidian surface",
    kicker: "видимый слой",
    body: "Markdown остаётся входом и навигацией. Сложная интерактивность уходит на отдельную страницу с zoom/pan.",
    bullets: ["wikilink", "callout", "external page"]
  },
  {
    id: "review",
    kind: "review",
    title: "1work-review",
    kicker: "закрытие",
    body: "Сравнивает цель, инструкции, критерии и evidence. Если проверка не держится, работа продолжается, а не закрывается словами.",
    bullets: ["diff", "evidence", "residual risk"]
  }
];

const rawEdges = [
  ["request", "agents", "читает рамку"],
  ["request", "router", "выбирает маршрут"],
  ["agents", "criteria", "подключает критерии"],
  ["agents", "router", "задаёт границы"],
  ["criteria", "beforeWork", "правила приёмки"],
  ["router", "active", "один ведущий скилл"],
  ["active", "beforeWork", "проверка подхода"],
  ["beforeWork", "artifact", "создать / изменить"],
  ["artifact", "obsidian", "показать человеку"],
  ["artifact", "review", "проверить"],
  ["review", "router", "новый цикл"]
];

function makeNodes() {
  return rawNodes.map((node) => {
    const layoutHeight = estimateNodeHeight(node);

    return {
      id: node.id,
      type: "skillCard",
      position: { x: 0, y: 0 },
      data: { ...node, layoutHeight },
      width: NODE_WIDTH,
      style: {
        width: NODE_WIDTH
      }
    };
  });
}

function makeEdges() {
  return rawEdges.map(([source, target, label]) => ({
    id: `${source}-${target}`,
    source,
    target,
    label,
    markerEnd: {
      type: MarkerType.ArrowClosed,
      width: 18,
      height: 18
    },
    style: { strokeWidth: 2.5 },
    labelStyle: {
      fontSize: 15,
      fontWeight: 760
    },
    labelBgPadding: [10, 6],
    labelBgBorderRadius: 6
  }));
}

function getNodeSize(node) {
  return {
    width: node.measured?.width ?? node.width ?? NODE_WIDTH,
    height: node.measured?.height ?? node.height ?? node.data.layoutHeight
  };
}

function getNodeCenter(node) {
  const size = getNodeSize(node);
  return {
    x: node.position.x + size.width / 2,
    y: node.position.y + size.height / 2
  };
}

function withCurrentPositions(freshNodes, currentNodes) {
  const currentById = new Map(currentNodes.map((node) => [node.id, node]));

  return freshNodes.map((node) => {
    const currentNode = currentById.get(node.id);
    if (!currentNode) return node;

    return {
      ...node,
      measured: currentNode.measured,
      position: currentNode.position,
      selected: currentNode.selected
    };
  });
}

function waitForAnimationFrame() {
  return new Promise((resolve) => {
    if (typeof window !== "undefined" && window.requestAnimationFrame) {
      window.requestAnimationFrame(() => {
        window.setTimeout(resolve, 0);
      });
      return;
    }

    setTimeout(resolve, 16);
  });
}

function easeInOutCubic(t) {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

async function animateNodeTransition(fromNodes, toNodes, onFrame, duration = 520) {
  const fromById = new Map(fromNodes.map((node) => [node.id, node]));
  const startedAt = performance.now();
  let latestNodes = toNodes;

  while (true) {
    const progress = Math.min(1, (performance.now() - startedAt) / duration);
    const eased = easeInOutCubic(progress);
    latestNodes = toNodes.map((toNode) => {
      const fromNode = fromById.get(toNode.id) ?? toNode;

      return {
        ...toNode,
        position: {
          x: Math.round(fromNode.position.x + (toNode.position.x - fromNode.position.x) * eased),
          y: Math.round(fromNode.position.y + (toNode.position.y - fromNode.position.y) * eased)
        }
      };
    });

    if (!onFrame(latestNodes) || progress >= 1) return latestNodes;

    await waitForAnimationFrame();
  }
}

function pickNearestSides(sourceNode, targetNode) {
  const sourceCenter = getNodeCenter(sourceNode);
  const targetCenter = getNodeCenter(targetNode);
  const dx = targetCenter.x - sourceCenter.x;
  const dy = targetCenter.y - sourceCenter.y;

  if (Math.abs(dx) > Math.abs(dy)) {
    return dx > 0
      ? { sourceSide: "right", targetSide: "left" }
      : { sourceSide: "left", targetSide: "right" };
  }

  return dy > 0
    ? { sourceSide: "bottom", targetSide: "top" }
    : { sourceSide: "top", targetSide: "bottom" };
}

function attachSmartHandles(edges, nodes) {
  const nodesById = new Map(nodes.map((node) => [node.id, node]));

  return edges.map((edge) => {
    const sourceNode = nodesById.get(edge.source);
    const targetNode = nodesById.get(edge.target);

    if (!sourceNode || !targetNode) return edge;

    const { sourceSide, targetSide } = pickNearestSides(sourceNode, targetNode);
    return {
      ...edge,
      sourceHandle: `source-${sourceSide}`,
      targetHandle: `target-${targetSide}`
    };
  });
}

function rectangularCollision(padding = 42) {
  let nodes = [];

  function force() {
    for (let index = 0; index < nodes.length; index += 1) {
      const node = nodes[index];

      for (let nextIndex = index + 1; nextIndex < nodes.length; nextIndex += 1) {
        const nextNode = nodes[nextIndex];
        const dx = nextNode.x - node.x || 1;
        const dy = nextNode.y - node.y || 1;
        const overlapX = (node.width + nextNode.width) / 2 + padding - Math.abs(dx);
        const overlapY = (node.height + nextNode.height) / 2 + padding - Math.abs(dy);

        if (overlapX <= 0 || overlapY <= 0) continue;

        if (overlapX < overlapY) {
          const push = (overlapX / 2) * Math.sign(dx);
          node.x -= push;
          nextNode.x += push;
        } else {
          const push = (overlapY / 2) * Math.sign(dy);
          node.y -= push;
          nextNode.y += push;
        }
      }
    }
  }

  force.initialize = (nextNodes) => {
    nodes = nextNodes;
  };

  return force;
}

async function layoutElkGraph(nodes, edges) {
  const graph = {
    id: "root",
    layoutOptions: {
      "elk.algorithm": "layered",
      "elk.direction": "DOWN",
      "elk.spacing.nodeNode": "116",
      "elk.layered.spacing.nodeNodeBetweenLayers": "168",
      "elk.edgeRouting": "ORTHOGONAL",
      "elk.layered.nodePlacement.strategy": "BRANDES_KOEPF"
    },
    children: nodes.map((node) => ({
      id: node.id,
      width: node.width ?? NODE_WIDTH,
      height: node.data.layoutHeight
    })),
    edges: edges.map((edge) => ({
      id: edge.id,
      sources: [edge.source],
      targets: [edge.target]
    }))
  };

  const layouted = await elk.layout(graph);
  const byId = new Map(layouted.children.map((node) => [node.id, node]));

  return nodes.map((node) => {
    const layoutNode = byId.get(node.id);
    return {
      ...node,
      position: {
        x: layoutNode?.x ?? 0,
        y: layoutNode?.y ?? 0
      }
    };
  });
}

function positionNodeByCenter(node, center) {
  const size = getNodeSize(node);

  return {
    ...node,
    position: {
      x: Math.round(center.x - size.width / 2),
      y: Math.round(center.y - size.height / 2)
    }
  };
}

function orientation(a, b, c) {
  return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
}

function segmentsIntersect(a, b, c, d) {
  const abC = orientation(a, b, c);
  const abD = orientation(a, b, d);
  const cdA = orientation(c, d, a);
  const cdB = orientation(c, d, b);

  return abC * abD < 0 && cdA * cdB < 0;
}

function countEdgeCrossings(nodes, edges) {
  const nodesById = new Map(nodes.map((node) => [node.id, node]));
  let crossings = 0;

  for (let index = 0; index < edges.length; index += 1) {
    const edge = edges[index];
    const sourceNode = nodesById.get(edge.source);
    const targetNode = nodesById.get(edge.target);
    if (!sourceNode || !targetNode) continue;

    for (let nextIndex = index + 1; nextIndex < edges.length; nextIndex += 1) {
      const nextEdge = edges[nextIndex];
      const sharesEndpoint =
        edge.source === nextEdge.source ||
        edge.source === nextEdge.target ||
        edge.target === nextEdge.source ||
        edge.target === nextEdge.target;

      if (sharesEndpoint) continue;

      const nextSourceNode = nodesById.get(nextEdge.source);
      const nextTargetNode = nodesById.get(nextEdge.target);
      if (!nextSourceNode || !nextTargetNode) continue;

      if (
        segmentsIntersect(
          getNodeCenter(sourceNode),
          getNodeCenter(targetNode),
          getNodeCenter(nextSourceNode),
          getNodeCenter(nextTargetNode)
        )
      ) {
        crossings += 1;
      }
    }
  }

  return crossings;
}

function edgeLengthScore(nodes, edges) {
  const nodesById = new Map(nodes.map((node) => [node.id, node]));

  return edges.reduce((score, edge) => {
    const sourceNode = nodesById.get(edge.source);
    const targetNode = nodesById.get(edge.target);
    if (!sourceNode || !targetNode) return score;

    const sourceCenter = getNodeCenter(sourceNode);
    const targetCenter = getNodeCenter(targetNode);
    return score + Math.hypot(targetCenter.x - sourceCenter.x, targetCenter.y - sourceCenter.y);
  }, 0);
}

function countNodeOverlaps(nodes, padding = 24) {
  let overlaps = 0;

  for (let index = 0; index < nodes.length; index += 1) {
    const node = nodes[index];
    const nodeSize = getNodeSize(node);
    const nodeCenter = getNodeCenter(node);

    for (let nextIndex = index + 1; nextIndex < nodes.length; nextIndex += 1) {
      const nextNode = nodes[nextIndex];
      const nextSize = getNodeSize(nextNode);
      const nextCenter = getNodeCenter(nextNode);
      const overlapX = (nodeSize.width + nextSize.width) / 2 + padding - Math.abs(nextCenter.x - nodeCenter.x);
      const overlapY = (nodeSize.height + nextSize.height) / 2 + padding - Math.abs(nextCenter.y - nodeCenter.y);

      if (overlapX > 0 && overlapY > 0) {
        overlaps += 1;
      }
    }
  }

  return overlaps;
}

function resolveNodeOverlaps(nodes, padding = 46, maxPasses = 120) {
  let resolvedNodes = nodes;

  for (let pass = 0; pass < maxPasses; pass += 1) {
    let moved = false;
    const centers = new Map(resolvedNodes.map((node) => [node.id, getNodeCenter(node)]));

    for (let index = 0; index < resolvedNodes.length; index += 1) {
      const node = resolvedNodes[index];
      const nodeSize = getNodeSize(node);
      const nodeCenter = centers.get(node.id);

      for (let nextIndex = index + 1; nextIndex < resolvedNodes.length; nextIndex += 1) {
        const nextNode = resolvedNodes[nextIndex];
        const nextSize = getNodeSize(nextNode);
        const nextCenter = centers.get(nextNode.id);
        const dx = nextCenter.x - nodeCenter.x || 1;
        const dy = nextCenter.y - nodeCenter.y || 1;
        const overlapX = (nodeSize.width + nextSize.width) / 2 + padding - Math.abs(dx);
        const overlapY = (nodeSize.height + nextSize.height) / 2 + padding - Math.abs(dy);

        if (overlapX <= 0 || overlapY <= 0) continue;

        moved = true;

        if (overlapX < overlapY) {
          const push = (overlapX / 2) * Math.sign(dx);
          nodeCenter.x -= push;
          nextCenter.x += push;
        } else {
          const push = (overlapY / 2) * Math.sign(dy);
          nodeCenter.y -= push;
          nextCenter.y += push;
        }
      }
    }

    resolvedNodes = resolvedNodes.map((node) => positionNodeByCenter(node, centers.get(node.id)));

    if (!moved) break;
  }

  return resolvedNodes;
}

function layoutScore(nodes, edges, settings = DEFAULT_FORCE_SETTINGS) {
  return (
    countNodeOverlaps(nodes, settings.nodeGap) * 1000000 +
    countEdgeCrossings(nodes, edges) * 100000 +
    edgeLengthScore(nodes, edges)
  );
}

function swapNodeCenters(nodes, firstId, secondId) {
  const firstNode = nodes.find((node) => node.id === firstId);
  const secondNode = nodes.find((node) => node.id === secondId);
  if (!firstNode || !secondNode) return nodes;

  const firstCenter = getNodeCenter(firstNode);
  const secondCenter = getNodeCenter(secondNode);

  return nodes.map((node) => {
    if (node.id === firstId) return positionNodeByCenter(node, secondCenter);
    if (node.id === secondId) return positionNodeByCenter(node, firstCenter);
    return node;
  });
}

function moveNodeCenter(nodes, nodeId, offset) {
  return nodes.map((node) => {
    if (node.id !== nodeId) return node;

    const center = getNodeCenter(node);
    return positionNodeByCenter(node, {
      x: center.x + offset.x,
      y: center.y + offset.y
    });
  });
}

function nudgeNodesToReduceCrossings(nodes, edges, settings = DEFAULT_FORCE_SETTINGS) {
  let bestNodes = resolveNodeOverlaps(nodes, settings.nodeGap);
  let bestScore = layoutScore(bestNodes, edges, settings);
  const directions = [
    { x: 1, y: 0 },
    { x: -1, y: 0 },
    { x: 0, y: 1 },
    { x: 0, y: -1 },
    { x: 1, y: 1 },
    { x: 1, y: -1 },
    { x: -1, y: 1 },
    { x: -1, y: -1 }
  ];

  for (const step of [280, 200, 140, 90, 54, 32]) {
    let improved = true;
    let pass = 0;

    while (improved && pass < 5) {
      improved = false;
      pass += 1;

      for (const node of bestNodes) {
        for (const direction of directions) {
          const candidateNodes = resolveNodeOverlaps(
            moveNodeCenter(bestNodes, node.id, {
              x: direction.x * step,
              y: direction.y * step
            }),
            settings.nodeGap,
            48
          );
          const candidateScore = layoutScore(candidateNodes, edges, settings);

          if (candidateScore < bestScore) {
            bestNodes = candidateNodes;
            bestScore = candidateScore;
            improved = true;
          }
        }
      }
    }
  }

  return bestNodes;
}

function minimizeEdgeCrossings(nodes, edges, settings = DEFAULT_FORCE_SETTINGS) {
  let bestNodes = resolveNodeOverlaps(nodes, settings.nodeGap);
  let bestScore = layoutScore(bestNodes, edges, settings);
  let improved = true;
  let pass = 0;

  while (improved && pass < 8) {
    improved = false;
    pass += 1;

    for (let index = 0; index < bestNodes.length; index += 1) {
      for (let nextIndex = index + 1; nextIndex < bestNodes.length; nextIndex += 1) {
        const candidateNodes = swapNodeCenters(bestNodes, bestNodes[index].id, bestNodes[nextIndex].id);
        const resolvedCandidateNodes = resolveNodeOverlaps(candidateNodes, settings.nodeGap, 32);
        const candidateScore = layoutScore(resolvedCandidateNodes, edges, settings);

        if (candidateScore < bestScore) {
          bestNodes = resolvedCandidateNodes;
          bestScore = candidateScore;
          improved = true;
        }
      }
    }
  }

  return nudgeNodesToReduceCrossings(bestNodes, edges, settings);
}

function layoutForceGraph(nodes, edges, settings = DEFAULT_FORCE_SETTINGS) {
  const simulationNodes = nodes.map((node, index) => {
    const center = getNodeCenter(node);
    const angle = (index / nodes.length) * Math.PI * 2 - Math.PI / 2;
    const radius = index % 2 === 0 ? 360 : 520;
    const size = getNodeSize(node);

    return {
      id: node.id,
      width: size.width,
      height: size.height,
      x: Number.isFinite(center.x) && center.x !== NODE_WIDTH / 2 ? center.x : Math.cos(angle) * radius,
      y: Number.isFinite(center.y) && center.y !== size.height / 2 ? center.y : Math.sin(angle) * radius
    };
  });
  const simulationEdges = edges.map((edge) => ({
    source: edge.source,
    target: edge.target
  }));

  const simulation = forceSimulation(simulationNodes)
    .force(
      "link",
      forceLink(simulationEdges)
        .id((node) => node.id)
        .distance(settings.linkDistance)
        .strength(0.28)
    )
    .force("charge", forceManyBody().strength(-settings.repulsion))
    .force("rect-collision", rectangularCollision(Math.max(24, settings.nodeGap - 6)))
    .force("center", forceCenter(0, 0))
    .force("x", forceX(0).strength(0.035))
    .force("y", forceY(0).strength(0.035))
    .stop();

  for (let index = 0; index < 360; index += 1) {
    simulation.tick();
  }

  const byId = new Map(simulationNodes.map((node) => [node.id, node]));

  const forceNodes = nodes.map((node) => {
    const layoutNode = byId.get(node.id);
    const size = getNodeSize(node);

    return {
      ...node,
      position: {
        x: Math.round((layoutNode?.x ?? 0) - size.width / 2),
        y: Math.round((layoutNode?.y ?? 0) - size.height / 2)
      }
    };
  });

  return minimizeEdgeCrossings(forceNodes, edges, settings);
}

function createD3ForceSimulation(nodes, edges, settings = DEFAULT_FORCE_SETTINGS) {
  const simulationNodes = nodes.map((node, index) => {
    const center = getNodeCenter(node);
    const angle = (index / nodes.length) * Math.PI * 2 - Math.PI / 2;
    const radius = index % 2 === 0 ? 360 : 520;
    const size = getNodeSize(node);

    return {
      id: node.id,
      width: size.width,
      height: size.height,
      x: Number.isFinite(center.x) && center.x !== NODE_WIDTH / 2 ? center.x : Math.cos(angle) * radius,
      y: Number.isFinite(center.y) && center.y !== size.height / 2 ? center.y : Math.sin(angle) * radius
    };
  });
  const simulationEdges = edges.map((edge) => ({
    source: edge.source,
    target: edge.target
  }));
  const simulation = forceSimulation(simulationNodes)
    .force(
      "link",
      forceLink(simulationEdges)
        .id((node) => node.id)
        .distance(settings.linkDistance)
        .strength(0.28)
    )
    .force("charge", forceManyBody().strength(-settings.repulsion))
    .force("rect-collision", rectangularCollision(Math.max(24, settings.nodeGap - 6)))
    .force("center", forceCenter(0, 0))
    .force("x", forceX(0).strength(0.035))
    .force("y", forceY(0).strength(0.035))
    .stop();

  return { simulation, simulationNodes };
}

function simulationNodesToReactNodes(nodes, simulationNodes) {
  const byId = new Map(simulationNodes.map((node) => [node.id, node]));

  return nodes.map((node) => {
    const simulationNode = byId.get(node.id);
    return positionNodeByCenter(node, {
      x: simulationNode?.x ?? getNodeCenter(node).x,
      y: simulationNode?.y ?? getNodeCenter(node).y
    });
  });
}

async function animateD3ForceGraph(nodes, edges, settings = DEFAULT_FORCE_SETTINGS, onFrame) {
  const { simulation, simulationNodes } = createD3ForceSimulation(nodes, edges, settings);
  let frameNodes = nodes;

  for (let frame = 0; frame < 72; frame += 1) {
    for (let tick = 0; tick < 5; tick += 1) {
      simulation.tick();
    }

    frameNodes = simulationNodesToReactNodes(nodes, simulationNodes);
    if (!onFrame(frameNodes)) return frameNodes;

    await waitForAnimationFrame();
  }

  const finalNodes = minimizeEdgeCrossings(frameNodes, edges, settings);
  return animateNodeTransition(frameNodes, finalNodes, onFrame, 420);
}

function createColaLayout(nodes, edges, settings = DEFAULT_FORCE_SETTINGS, attempt = 0) {
  const repulsionScale = Math.max(0.72, Math.min(1.8, Math.sqrt(settings.repulsion / DEFAULT_FORCE_SETTINGS.repulsion)));
  const nodeIndexById = new Map(nodes.map((node, index) => [node.id, index]));
  const angleOffset = attempt * 0.63;
  const radiusJitter = 1 + (attempt % 3) * 0.12;
  const colaNodes = nodes.map((node, index) => {
    const currentCenter = getNodeCenter(node);
    const angle = (index / nodes.length) * Math.PI * 2 - Math.PI / 2 + angleOffset;
    const radius = (index % 2 === 0 ? 420 : 620) * repulsionScale * radiusJitter;
    const size = getNodeSize(node);
    const hasCurrentPosition = currentCenter.x !== NODE_WIDTH / 2 || currentCenter.y !== size.height / 2;

    return {
      id: node.id,
      width: size.width + settings.nodeGap,
      height: size.height + settings.nodeGap,
      x: hasCurrentPosition ? currentCenter.x : Math.cos(angle) * radius,
      y: hasCurrentPosition ? currentCenter.y : Math.sin(angle) * radius
    };
  });
  const colaLinks = edges.map((edge) => ({
    source: nodeIndexById.get(edge.source),
    target: nodeIndexById.get(edge.target),
    weight: 1.1
  }));
  const directedGap = Math.max(settings.nodeGap + 84, settings.linkDistance * 0.58);
  const idealLinkDistance = settings.linkDistance * (0.82 + repulsionScale * 0.18);
  const layout = new ColaLayout()
    .size([2200 * repulsionScale, 1800 * repulsionScale])
    .nodes(colaNodes)
    .links(colaLinks)
    .linkDistance(idealLinkDistance)
    .flowLayout("y", directedGap)
    .avoidOverlaps(true)
    .convergenceThreshold(0.0005);

  return { colaNodes, layout };
}

function runColaLayoutAttempt(nodes, edges, settings = DEFAULT_FORCE_SETTINGS, attempt = 0) {
  const { colaNodes, layout } = createColaLayout(nodes, edges, settings, attempt);

  layout.start(90, 90, 150, 0, false, false);

  const colaLayoutedNodes = nodes.map((node, index) =>
    positionNodeByCenter(node, {
      x: colaNodes[index].x,
      y: colaNodes[index].y
    })
  );

  return minimizeEdgeCrossings(colaLayoutedNodes, edges, settings);
}

function layoutColaGraph(nodes, edges, settings = DEFAULT_FORCE_SETTINGS) {
  let bestNodes = null;
  let bestScore = Number.POSITIVE_INFINITY;

  for (let attempt = 0; attempt < 9; attempt += 1) {
    const candidateNodes = runColaLayoutAttempt(nodes, edges, settings, attempt);
    const candidateScore = layoutScore(candidateNodes, edges, settings);

    if (candidateScore < bestScore) {
      bestNodes = candidateNodes;
      bestScore = candidateScore;
    }

    if (countNodeOverlaps(candidateNodes, settings.nodeGap) === 0 && countEdgeCrossings(candidateNodes, edges) === 0) {
      break;
    }
  }

  return bestNodes ?? nodes;
}

async function animateColaGraph(nodes, edges, settings = DEFAULT_FORCE_SETTINGS, onFrame) {
  let bestAttempt = 0;
  let bestScore = Number.POSITIVE_INFINITY;

  for (let attempt = 0; attempt < 9; attempt += 1) {
    const candidateNodes = runColaLayoutAttempt(nodes, edges, settings, attempt);
    const candidateScore = layoutScore(candidateNodes, edges, settings);

    if (candidateScore < bestScore) {
      bestAttempt = attempt;
      bestScore = candidateScore;
    }

    if (countNodeOverlaps(candidateNodes, settings.nodeGap) === 0 && countEdgeCrossings(candidateNodes, edges) === 0) {
      break;
    }
  }

  const { colaNodes, layout } = createColaLayout(nodes, edges, settings, bestAttempt);
  layout.start(0, 0, 0, 0, false, false);
  layout._alpha = 0.1;

  let frameNodes = nodes;

  for (let frame = 0; frame < 120; frame += 1) {
    let done = false;
    for (let tick = 0; tick < 4; tick += 1) {
      done = layout.tick();
      if (done) break;
    }

    frameNodes = nodes.map((node, index) =>
      positionNodeByCenter(node, {
        x: colaNodes[index].x,
        y: colaNodes[index].y
      })
    );

    if (!onFrame(frameNodes)) return frameNodes;
    if (done) break;

    await waitForAnimationFrame();
  }

  const finalNodes = minimizeEdgeCrossings(frameNodes, edges, settings);
  return animateNodeTransition(frameNodes, finalNodes, onFrame, 420);
}

function centerOnStart(flow, nodes, duration = 360) {
  const startNode = nodes.find((node) => node.id === "request") ?? nodes[0];
  if (!startNode) return;

  const size = getNodeSize(startNode);
  flow.setCenter(startNode.position.x + size.width / 2, startNode.position.y + size.height / 2, {
    zoom: READABLE_ZOOM,
    duration
  });
}

const SkillCard = memo(function SkillCard({ data }) {
  return (
    <article className={`flow-card flow-card--${data.kind}`}>
      {HANDLE_SIDES.map((side) => (
        <React.Fragment key={side.id}>
          <Handle
            id={`target-${side.id}`}
            type="target"
            position={side.position}
            className="flow-handle"
            isConnectable={false}
          />
          <Handle
            id={`source-${side.id}`}
            type="source"
            position={side.position}
            className="flow-handle"
            isConnectable={false}
          />
        </React.Fragment>
      ))}
      <div className="flow-card__topline">
        <span>{data.kicker}</span>
      </div>
      <h2>{data.title}</h2>
      <p>{data.body}</p>
      <div className="flow-card__chips">
        {data.bullets.map((item) => (
          <span key={item}>{item}</span>
        ))}
      </div>
    </article>
  );
});

const nodeTypes = { skillCard: SkillCard };

function ForceSlider({ label, value, min, max, step, onChange }) {
  return (
    <label className="flow-force-setting">
      <span className="flow-force-setting__meta">
        <span>{label}</span>
        <b>{value}</b>
      </span>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
      />
    </label>
  );
}

function FlowPage() {
  const flow = useReactFlow();
  const store = useStoreApi();
  const animationIdRef = useRef(0);
  const initialLayoutDoneRef = useRef(false);
  const initialCenterDoneRef = useRef(false);
  const baseEdges = useMemo(makeEdges, []);
  const [layoutMode, setLayoutMode] = useState("elk");
  const [forceSettings, setForceSettings] = useState(DEFAULT_FORCE_SETTINGS);
  const [status, setStatus] = useState("ELK готов");

  const updateForceSetting = useCallback((key, value) => {
    setForceSettings((current) => ({ ...current, [key]: value }));
    setStatus("настройки гравитации изменены");
  }, []);

  const relayout = useCallback(
    async (nextMode = layoutMode) => {
      const animationId = animationIdRef.current + 1;
      animationIdRef.current = animationId;
      setLayoutMode(nextMode);
      setStatus(
        nextMode === "force"
          ? "анимация d3-force..."
          : nextMode === "cola"
            ? "анимация Cola..."
            : "анимация ELK..."
      );
      const sourceNodes = withCurrentPositions(makeNodes(), flow.getNodes());
      const publishFrame = (frameNodes) => {
        if (animationIdRef.current !== animationId) return false;
        const state = store.getState();
        state.setNodes(frameNodes);
        state.setEdges(attachSmartHandles(baseEdges, frameNodes));
        return true;
      };
      const layoutedNodes =
        nextMode === "force"
          ? await animateD3ForceGraph(sourceNodes, baseEdges, forceSettings, publishFrame)
          : nextMode === "cola"
            ? await animateColaGraph(sourceNodes, baseEdges, forceSettings, publishFrame)
            : await animateNodeTransition(sourceNodes, await layoutElkGraph(makeNodes(), baseEdges), publishFrame);

      if (animationIdRef.current !== animationId) return;

      store.getState().setEdges(attachSmartHandles(baseEdges, layoutedNodes));
      setStatus(
        nextMode === "force" || nextMode === "cola"
          ? `${nextMode === "cola" ? "Cola" : "d3-force"}: связи ${countEdgeCrossings(layoutedNodes, baseEdges)}, ноды ${countNodeOverlaps(layoutedNodes, forceSettings.nodeGap)}`
          : "ELK карта"
      );

      if (!initialCenterDoneRef.current) {
        initialCenterDoneRef.current = true;
        window.requestAnimationFrame(() => {
          centerOnStart(flow, layoutedNodes, 360);
        });
      }
    },
    [baseEdges, flow, forceSettings, layoutMode, store]
  );

  useEffect(() => {
    if (!flow.viewportInitialized || initialLayoutDoneRef.current) return;

    initialLayoutDoneRef.current = true;
    const params = new URLSearchParams(window.location.search);
    const requestedLayout = params.get("layout");
    store.getState().setEdges(baseEdges);
    relayout(requestedLayout === "force" || requestedLayout === "cola" ? requestedLayout : "elk");
  }, [baseEdges, flow.viewportInitialized, relayout, store]);

  useEffect(() => {
    return () => {
      animationIdRef.current += 1;
    };
  }, []);

  const minimapColor = useCallback((node) => {
    const kind = node.data.kind;
    if (kind === "skill") return "#7db9aa";
    if (kind === "gate") return "#e5b65b";
    if (kind === "instruction") return "#c9977d";
    if (kind === "memory") return "#a6d8c9";
    if (kind === "review") return "#a4a9c9";
    return "#f5e5c7";
  }, []);

  const title = useMemo(() => {
    if (layoutMode === "cola") return "FlowPage / Cola";
    if (layoutMode === "force") return "FlowPage / d3-force";
    return "FlowPage / ELK";
  }, [layoutMode]);

  return (
    <main className="flow-page">
      <ReactFlow
        defaultNodes={[]}
        defaultEdges={baseEdges}
        nodeTypes={nodeTypes}
        onNodeDragStart={() => {
          animationIdRef.current += 1;
          setStatus("manual drag");
        }}
        onNodeDrag={() => {
          flow.setEdges(attachSmartHandles(baseEdges, flow.getNodes()));
        }}
        onNodeDragStop={() => {
          flow.setEdges(attachSmartHandles(baseEdges, flow.getNodes()));
          setStatus("manual positions");
        }}
        minZoom={0.18}
        maxZoom={2.2}
        nodesDraggable
        nodesConnectable={false}
        elementsSelectable
        panOnScroll
        selectionOnDrag
        zoomOnDoubleClick={false}
      >
        <Background color="#d5c7ad" gap={28} size={1.2} />
        <Controls showInteractive={false} />
        <MiniMap
          nodeColor={minimapColor}
          maskColor="rgba(28, 35, 38, 0.18)"
          pannable
          zoomable
        />
        <Panel position="top-left">
          <section className="flow-toolbar" aria-label="FlowPage controls">
            <div className="flow-toolbar__header">
              <div>
                <h1>{title}</h1>
                <p>{status}</p>
              </div>
              <div className="flow-toolbar__actions">
                <button type="button" onClick={() => flow.fitView({ padding: 0.16, duration: 320 })}>
                  Обзор
                </button>
                <button
                  type="button"
                  onClick={() => {
                    const currentNodes = flow.getNodes();
                    const startNode = currentNodes.find((node) => node.id === "request") ?? currentNodes[0];
                    if (!startNode) return;
                    const size = getNodeSize(startNode);
                    flow.setCenter(startNode.position.x + size.width / 2, startNode.position.y + size.height / 2, {
                      zoom: READABLE_ZOOM,
                      duration: 320
                    });
                  }}
                >
                  Старт
                </button>
                <button type="button" onClick={() => flow.zoomTo(1, { duration: 320 })}>
                  100%
                </button>
                <button type="button" aria-pressed={layoutMode === "elk"} onClick={() => relayout("elk")}>
                  ELK
                </button>
                <button type="button" aria-pressed={layoutMode === "force"} onClick={() => relayout("force")}>
                  d3-force
                </button>
                <button type="button" aria-pressed={layoutMode === "cola"} onClick={() => relayout("cola")}>
                  Cola
                </button>
              </div>
            </div>
            <div className="flow-force-settings" aria-label="Настройки гравитации">
              <ForceSlider
                label="Отталкивание"
                min={420}
                max={2200}
                step={20}
                value={forceSettings.repulsion}
                onChange={(value) => updateForceSetting("repulsion", value)}
              />
              <ForceSlider
                label="Длина связей"
                min={180}
                max={520}
                step={10}
                value={forceSettings.linkDistance}
                onChange={(value) => updateForceSetting("linkDistance", value)}
              />
              <ForceSlider
                label="Зазор нод"
                min={18}
                max={110}
                step={2}
                value={forceSettings.nodeGap}
                onChange={(value) => updateForceSetting("nodeGap", value)}
              />
              <button type="button" onClick={() => relayout(layoutMode === "elk" ? "cola" : layoutMode)}>
                Пересчитать
              </button>
            </div>
          </section>
        </Panel>
        <Panel position="top-right">
          <div className="flow-note">
            Старт открывается крупно. Узлы можно таскать; Cola добавляет направленные
            ограничения и непересечение карточек.
          </div>
        </Panel>
      </ReactFlow>
    </main>
  );
}

function App() {
  return (
    <ReactFlowProvider>
      <FlowPage />
    </ReactFlowProvider>
  );
}

createRoot(document.getElementById("root")).render(<App />);
