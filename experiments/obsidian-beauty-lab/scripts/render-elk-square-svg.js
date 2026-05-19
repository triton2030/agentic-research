#!/usr/bin/env node
"use strict";

const fs = require("node:fs/promises");
const path = require("node:path");
const ELK = require("elkjs");

const ROOT = path.resolve(__dirname, "..");
const DEFAULT_INPUT = path.join(ROOT, "data", "elk-square-demo.json");
const DEFAULT_OUTPUT = path.join(ROOT, "generated", "elk-square-demo.svg");
const CANVAS = 1080;
const TOP_BAND = 118;
const PAD = 70;

const TYPE_STYLES = {
  start: { fill: "#e9f6ef", stroke: "#3f7b67", text: "#1e4437", badge: "#2f6a58" },
  data: { fill: "#edf2ff", stroke: "#6177bd", text: "#27376d", badge: "#4e65ad" },
  guard: { fill: "#fff1d7", stroke: "#c38a2e", text: "#5a3a10", badge: "#a76e20" },
  compute: { fill: "#eaf7fb", stroke: "#408098", text: "#214e5d", badge: "#337186" },
  process: { fill: "#fff8ec", stroke: "#c28a34", text: "#3b2d19", badge: "#a77224" },
  decision: { fill: "#f9edf3", stroke: "#a45b7b", text: "#573146", badge: "#8e4666" },
  output: { fill: "#f1eefb", stroke: "#7565ad", text: "#40346b", badge: "#6553a0" },
  success: { fill: "#e9f8e5", stroke: "#5d9654", text: "#294d25", badge: "#4d8147" },
  note: { fill: "#f6f0e8", stroke: "#9a8063", text: "#453827", badge: "#83694d" },
  future: { fill: "#eef1f4", stroke: "#63717d", text: "#2f3b45", badge: "#52616d" }
};

const TRIALS = [
  { algorithm: "stress", cleanup: true, desiredEdgeLength: 120, nodeSpacing: 20, penalty: 0 },
  { algorithm: "stress", cleanup: true, desiredEdgeLength: 145, nodeSpacing: 28, penalty: 4 },
  { algorithm: "force", model: "EADES", nodeSpacing: 25, temperature: 0.12, penalty: 12 },
  { algorithm: "force", model: "EADES", nodeSpacing: 25, temperature: 0.25, penalty: 14 },
  { algorithm: "mrtree", nodeSpacing: 30, penalty: 28 },
  { algorithm: "radial", nodeSpacing: 5, penalty: 45 },
  { algorithm: "layered", direction: "DOWN", layerSpacing: 56, nodeSpacing: 42, penalty: 60 },
  { algorithm: "layered", direction: "RIGHT", layerSpacing: 54, nodeSpacing: 42, penalty: 92 }
];

function escapeXml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function wrapText(value, maxChars) {
  const words = String(value).split(/\s+/).filter(Boolean);
  const lines = [];
  let current = "";

  for (const word of words) {
    const chunks = word.length > maxChars ? word.match(new RegExp(`.{1,${maxChars}}`, "g")) : [word];
    for (const chunk of chunks) {
      const next = current ? `${current} ${chunk}` : chunk;
      if (next.length > maxChars && current) {
        lines.push(current);
        current = chunk;
      } else {
        current = next;
      }
    }
  }

  if (current) lines.push(current);
  return lines.slice(0, 3);
}

function measureNode(node) {
  const lines = wrapText(node.label, 22);
  const width = node.type === "decision" ? 194 : 218;
  const height = Math.max(82, 42 + lines.length * 18);
  return { ...node, width, height, lines };
}

function toElkGraph(spec, trial) {
  const nodes = spec.nodes.map(measureNode);
  const knownIds = new Set(nodes.map((node) => node.id));
  const edges = spec.edges.filter((edge) => knownIds.has(edge.from) && knownIds.has(edge.to));
  const layoutOptions = {
    "elk.algorithm": trial.algorithm,
    "elk.aspectRatio": "1.0",
    "elk.spacing.nodeNode": String(trial.nodeSpacing),
    "elk.padding": "[top=24,left=24,bottom=24,right=24]"
  };

  if (trial.algorithm === "layered") {
    Object.assign(layoutOptions, {
      "elk.direction": trial.direction,
      "elk.edgeRouting": "ORTHOGONAL",
      "elk.layered.spacing.nodeNodeBetweenLayers": String(trial.layerSpacing),
      "elk.layered.crossingMinimization.strategy": "LAYER_SWEEP",
      "elk.layered.nodePlacement.strategy": "BRANDES_KOEPF",
      "elk.layered.considerModelOrder.strategy": "NODES_AND_EDGES",
      "elk.layered.mergeEdges": "true"
    });
  }

  if (trial.algorithm === "stress") {
    Object.assign(layoutOptions, {
      "elk.stress.desiredEdgeLength": String(trial.desiredEdgeLength),
      "elk.stress.iterationLimit": "600"
    });
  }

  if (trial.algorithm === "force") {
    Object.assign(layoutOptions, {
      "elk.force.model": trial.model,
      "elk.force.iterations": "700",
      "elk.force.repulsion": "2",
      "elk.force.temperature": String(trial.temperature)
    });
  }

  return {
    id: "root",
    layoutOptions,
    children: nodes.map((node) => ({
      id: node.id,
      width: node.width,
      height: node.height
    })),
    edges: edges.map((edge, index) => ({
      id: edge.id || `e${index + 1}`,
      sources: [edge.from],
      targets: [edge.to]
    }))
  };
}

function nodeMetaById(spec) {
  return new Map(spec.nodes.map((node) => {
    const measured = measureNode(node);
    return [node.id, measured];
  }));
}

function edgeMetaById(spec) {
  return new Map(spec.edges.map((edge, index) => [edge.id || `e${index + 1}`, edge]));
}

function contentBounds(layout) {
  const points = [];
  for (const node of layout.children || []) {
    points.push([node.x, node.y], [node.x + node.width, node.y + node.height]);
  }
  for (const edge of layout.edges || []) {
    for (const section of edge.sections || []) {
      points.push([section.startPoint.x, section.startPoint.y], [section.endPoint.x, section.endPoint.y]);
      for (const bend of section.bendPoints || []) points.push([bend.x, bend.y]);
    }
  }

  const xs = points.map(([x]) => x);
  const ys = points.map(([, y]) => y);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);

  return {
    minX,
    minY,
    maxX,
    maxY,
    width: maxX - minX,
    height: maxY - minY
  };
}

function overlapArea(layout) {
  let area = 0;
  const nodes = layout.children || [];

  for (let i = 0; i < nodes.length; i += 1) {
    for (let j = i + 1; j < nodes.length; j += 1) {
      const left = nodes[i];
      const right = nodes[j];
      const overlapX = Math.max(0, Math.min(left.x + left.width, right.x + right.width) - Math.max(left.x, right.x));
      const overlapY = Math.max(0, Math.min(left.y + left.height, right.y + right.height) - Math.max(left.y, right.y));
      area += overlapX * overlapY;
    }
  }

  return area;
}

function layoutScore(layout, trial) {
  const bounds = contentBounds(layout);
  const aspect = bounds.width / bounds.height;
  const squarePenalty = Math.abs(Math.log(aspect)) * 1000;
  const areaPenalty = (bounds.width * bounds.height) / 45000;
  const overlapPenalty = overlapArea(layout) * 2;
  return squarePenalty + areaPenalty + overlapPenalty + trial.penalty;
}

async function removeOverlaps(elk, layout, spec, trial) {
  if (!trial.cleanup) return layout;

  const graph = {
    id: "root",
    layoutOptions: {
      "elk.algorithm": "sporeOverlap",
      "elk.spacing.nodeNode": String(trial.nodeSpacing)
    },
    children: (layout.children || []).map((node) => ({
      id: node.id,
      width: node.width,
      height: node.height,
      x: node.x,
      y: node.y
    })),
    edges: spec.edges.map((edge, index) => ({
      id: edge.id || `e${index + 1}`,
      sources: [edge.from],
      targets: [edge.to]
    }))
  };

  const cleaned = await elk.layout(graph);
  cleaned.layoutPass = `${trial.algorithm}+overlap`;
  return cleaned;
}

async function chooseLayout(spec) {
  const elk = new ELK();
  const layouts = [];
  for (const trial of TRIALS) {
    const initialLayout = await elk.layout(toElkGraph(spec, trial));
    const layout = await removeOverlaps(elk, initialLayout, spec, trial);
    layouts.push({ trial, layout, score: layoutScore(layout, trial) });
  }
  layouts.sort((left, right) => left.score - right.score);
  return layouts[0];
}

function edgePoints(edge) {
  const section = (edge.sections || [])[0];
  if (!section) return [];
  return [
    section.startPoint,
    ...(section.bendPoints || []),
    section.endPoint
  ];
}

function renderEdge(edge, edgeMeta, showLabels) {
  const points = edgePoints(edge);
  if (points.length < 2) return "";

  const pathData = points
    .map((point, index) => `${index === 0 ? "M" : "L"} ${point.x.toFixed(1)} ${point.y.toFixed(1)}`)
    .join(" ");
  const label = showLabels ? edgeMeta.get(edge.id)?.label : "";
  const middle = points[Math.floor(points.length / 2)];
  const labelMarkup = label
    ? `<g class="edge-label"><rect x="${(middle.x - 38).toFixed(1)}" y="${(middle.y - 13).toFixed(1)}" width="76" height="24" rx="12"/><text x="${middle.x.toFixed(1)}" y="${(middle.y + 4).toFixed(1)}" text-anchor="middle">${escapeXml(label)}</text></g>`
    : "";

  return `<path class="edge" d="${pathData}" marker-end="url(#arrow)"/>${labelMarkup}`;
}

function renderNode(node, nodeMeta) {
  const meta = nodeMeta.get(node.id) || { type: "process", label: node.id, lines: [node.id] };
  const type = meta.type || "process";
  const lines = meta.lines || wrapText(meta.label || node.id, 22);
  const style = TYPE_STYLES[type] || TYPE_STYLES.process;
  const cx = node.x + node.width / 2;
  const labelY = node.y + node.height / 2 - (lines.length - 1) * 8 + 13;
  const badge = `<text class="badge" x="${cx.toFixed(1)}" y="${(node.y + 22).toFixed(1)}" text-anchor="middle">${escapeXml(type)}</text>`;
  const body = lines
    .map((line, index) => `<text class="node-label" x="${cx.toFixed(1)}" y="${(labelY + index * 18).toFixed(1)}" text-anchor="middle">${escapeXml(line)}</text>`)
    .join("");
  const vars = `--fill:${style.fill};--stroke:${style.stroke};--text:${style.text};--badge:${style.badge}`;

  if (type === "decision") {
    const points = [
      [cx, node.y],
      [node.x + node.width, node.y + node.height / 2],
      [cx, node.y + node.height],
      [node.x, node.y + node.height / 2]
    ]
      .map((point) => `${point[0].toFixed(1)},${point[1].toFixed(1)}`)
      .join(" ");
    return `<g class="node" style="${vars}"><polygon points="${points}"/>${badge}${body}</g>`;
  }

  const radius = type === "start" || type === "success" ? 34 : 18;
  return `<g class="node" style="${vars}"><rect x="${node.x.toFixed(1)}" y="${node.y.toFixed(1)}" width="${node.width.toFixed(1)}" height="${node.height.toFixed(1)}" rx="${radius}"/>${badge}${body}</g>`;
}

function renderSvg(spec, picked) {
  const { layout, trial, score } = picked;
  const bounds = contentBounds(layout);
  const nodesById = nodeMetaById(spec);
  const edgesById = edgeMetaById(spec);
  const availableWidth = CANVAS - PAD * 2;
  const availableHeight = CANVAS - TOP_BAND - PAD * 2;
  const scale = Math.min(availableWidth / bounds.width, availableHeight / bounds.height);
  const offsetX = (CANVAS - bounds.width * scale) / 2 - bounds.minX * scale;
  const offsetY = TOP_BAND + (availableHeight - bounds.height * scale) / 2 - bounds.minY * scale;
  const aspect = bounds.width / bounds.height;
  const mode = layout.layoutPass || (trial.direction ? `${trial.algorithm}/${trial.direction}` : trial.algorithm);
  const stats = `AtlasGrid - ${mode} - aspect ${aspect.toFixed(2)}`;

  const edges = (layout.edges || []).map((edge) => renderEdge(edge, edgesById, spec.edgeLabels !== false)).join("\n      ");
  const nodes = (layout.children || []).map((node) => renderNode(node, nodesById)).join("\n      ");

  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc" viewBox="0 0 ${CANVAS} ${CANVAS}" width="${CANVAS}" height="${CANVAS}">
  <title id="title">${escapeXml(spec.title)}</title>
  <desc id="desc">${escapeXml(spec.subtitle || "Generated square SVG diagram using ELK.js.")}</desc>
  <defs>
    <filter id="soft-shadow" x="-20%" y="-20%" width="140%" height="150%">
      <feDropShadow dx="0" dy="16" stdDeviation="16" flood-color="#263238" flood-opacity=".13"/>
    </filter>
    <marker id="arrow" viewBox="0 0 10 10" refX="8.4" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#52616d"/>
    </marker>
    <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0" stop-color="#fff8ec"/>
      <stop offset=".58" stop-color="#edf7f2"/>
      <stop offset="1" stop-color="#eef1fb"/>
    </linearGradient>
  </defs>
  <style>
    svg { font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    .panel { fill: url(#bg); }
    .grid { stroke: rgba(49, 55, 68, .08); stroke-width: 1; }
    .title { fill: #242a2f; font-size: 34px; font-weight: 850; letter-spacing: 0; }
    .subtitle { fill: #5f665f; font-size: 16px; font-weight: 560; letter-spacing: 0; }
    .metric { fill: rgba(255, 255, 255, .72); stroke: rgba(58, 67, 74, .14); }
    .metric-text { fill: #4f5b52; font-size: 13px; font-weight: 720; letter-spacing: 0; }
    .edge { fill: none; stroke: #52616d; stroke-width: 3.2; stroke-linecap: round; stroke-linejoin: round; opacity: .86; }
    .edge-label rect { fill: rgba(255, 255, 255, .88); stroke: rgba(82, 97, 109, .16); }
    .edge-label text { fill: #52616d; font-size: 12px; font-weight: 760; letter-spacing: 0; }
    .node rect, .node polygon { fill: var(--fill); stroke: var(--stroke); stroke-width: 2.3; filter: url(#soft-shadow); }
    .badge { fill: var(--badge); font-size: 11px; font-weight: 850; letter-spacing: .06em; text-transform: uppercase; }
    .node-label { fill: var(--text); font-size: 15.5px; font-weight: 760; letter-spacing: 0; }
  </style>
  <rect class="panel" x="18" y="18" width="1044" height="1044" rx="42"/>
  <path class="grid" d="M 70 170 H 1010 M 70 330 H 1010 M 70 490 H 1010 M 70 650 H 1010 M 70 810 H 1010 M 230 150 V 1010 M 390 150 V 1010 M 550 150 V 1010 M 710 150 V 1010 M 870 150 V 1010"/>
  <text class="title" x="70" y="70">${escapeXml(spec.title)}</text>
  <text class="subtitle" x="70" y="99">${escapeXml(spec.subtitle || "")}</text>
  <g transform="translate(718 52)">
    <rect class="metric" x="0" y="0" width="292" height="38" rx="19"/>
    <text class="metric-text" x="146" y="25" text-anchor="middle">${escapeXml(stats)}</text>
  </g>
  <g transform="translate(${offsetX.toFixed(2)} ${offsetY.toFixed(2)}) scale(${scale.toFixed(4)})">
      ${edges}
      ${nodes}
  </g>
</svg>
`;
}

async function main() {
  const inputPath = path.resolve(process.argv[2] || DEFAULT_INPUT);
  const outputPath = path.resolve(process.argv[3] || DEFAULT_OUTPUT);
  const spec = JSON.parse(await fs.readFile(inputPath, "utf8"));
  const picked = await chooseLayout(spec);
  const svg = renderSvg(spec, picked);

  await fs.mkdir(path.dirname(outputPath), { recursive: true });
  await fs.writeFile(outputPath, svg);

  const bounds = contentBounds(picked.layout);
  console.log(`generated ${path.relative(ROOT, outputPath)}`);
  const mode = picked.layout.layoutPass || `${picked.trial.algorithm}${picked.trial.direction ? `/${picked.trial.direction}` : ""}`;
  console.log(`ELK ${require("elkjs/package.json").version}; mode ${mode}; raw ${bounds.width.toFixed(0)}x${bounds.height.toFixed(0)}; aspect ${(bounds.width / bounds.height).toFixed(2)}; overlap ${overlapArea(picked.layout).toFixed(0)}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
