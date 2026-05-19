(function () {
  "use strict";

  const TYPE_STYLES = {
    start: { fill: "#e7f2ed", stroke: "#3f7168", text: "#203f39" },
    end: { fill: "#242a2f", stroke: "#242a2f", text: "#fff8ec" },
    process: { fill: "#fff8ec", stroke: "#c28a34", text: "#29251d" },
    decision: { fill: "#f8eef2", stroke: "#9c6374", text: "#4e2935" },
    data: { fill: "#eff1fb", stroke: "#6876b8", text: "#303a67" },
    note: { fill: "#fff2d8", stroke: "#d8a64e", text: "#3b3124" },
    risk: { fill: "#fde8dc", stroke: "#b8653f", text: "#5d2f20" },
    success: { fill: "#e7f6e7", stroke: "#4f8a54", text: "#27492a" },
  };

  const NODE_W = 190;
  const NODE_H = 72;
  const GAP_X = 255;
  const GAP_Y = 122;
  const PAD = 52;

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function parse(input) {
    const nodes = new Map();
    const nodeOrder = [];
    const edges = [];
    const meta = {
      title: "TinyFlow",
      direction: "LR",
      skin: "warm",
    };

    const ensureNode = (id) => {
      if (!nodes.has(id)) {
        nodes.set(id, { id, type: "process", label: id });
        nodeOrder.push(id);
      }
      return nodes.get(id);
    };

    const lines = String(input)
      .split(/\r?\n/)
      .map((raw, index) => ({ raw, line: raw.trim(), index: index + 1 }))
      .filter(({ line }) => line && !line.startsWith("#"));

    for (const { line, index } of lines) {
      let match = line.match(/^title\s*:\s*(.+)$/i);
      if (match) {
        meta.title = match[1].trim();
        continue;
      }

      match = line.match(/^direction\s*:\s*(LR|TB)$/i);
      if (match) {
        meta.direction = match[1].toUpperCase();
        continue;
      }

      match = line.match(/^skin\s*:\s*([a-z0-9_-]+)$/i);
      if (match) {
        meta.skin = match[1].toLowerCase();
        continue;
      }

      match = line.match(/^([A-Za-z][\w-]*)\s*->\s*([A-Za-z][\w-]*)(?:\s*:\s*(.+))?$/);
      if (match) {
        const [, from, to, label = ""] = match;
        ensureNode(from);
        ensureNode(to);
        edges.push({ from, to, label: label.trim() });
        continue;
      }

      match = line.match(/^([A-Za-z][\w-]*)\s*\[\s*(?:(start|end|process|data|note|risk|success|decision)\s*:\s*)?(.+?)\s*\]$/i);
      if (match) {
        const [, id, rawType = "process", label] = match;
        if (!nodes.has(id)) nodeOrder.push(id);
        nodes.set(id, {
          id,
          type: rawType.toLowerCase(),
          label: label.trim(),
        });
        continue;
      }

      match = line.match(/^([A-Za-z][\w-]*)\s*\{\s*(.+?)\s*\}$/);
      if (match) {
        const [, id, label] = match;
        if (!nodes.has(id)) nodeOrder.push(id);
        nodes.set(id, { id, type: "decision", label: label.trim() });
        continue;
      }

      match = line.match(/^([A-Za-z][\w-]*)\s*\(\(\s*(.+?)\s*\)\)$/);
      if (match) {
        const [, id, label] = match;
        if (!nodes.has(id)) nodeOrder.push(id);
        nodes.set(id, { id, type: "end", label: label.trim() });
        continue;
      }

      throw new Error(`Line ${index}: cannot parse "${line}"`);
    }

    return {
      meta,
      nodes: nodeOrder.map((id) => nodes.get(id)).filter(Boolean),
      edges,
    };
  }

  function computeLayout(model) {
    const byId = new Map(model.nodes.map((node) => [node.id, { ...node }]));
    const indegree = new Map(model.nodes.map((node) => [node.id, 0]));
    const outgoing = new Map(model.nodes.map((node) => [node.id, []]));

    for (const edge of model.edges) {
      if (!byId.has(edge.from) || !byId.has(edge.to)) continue;
      indegree.set(edge.to, (indegree.get(edge.to) || 0) + 1);
      outgoing.get(edge.from).push(edge.to);
    }

    const queue = model.nodes
      .filter((node) => (indegree.get(node.id) || 0) === 0)
      .map((node) => node.id);
    const layer = new Map(model.nodes.map((node) => [node.id, 0]));

    while (queue.length) {
      const id = queue.shift();
      for (const to of outgoing.get(id) || []) {
        layer.set(to, Math.max(layer.get(to) || 0, (layer.get(id) || 0) + 1));
        indegree.set(to, (indegree.get(to) || 0) - 1);
        if ((indegree.get(to) || 0) === 0) queue.push(to);
      }
    }

    const buckets = new Map();
    for (const node of model.nodes) {
      const key = layer.get(node.id) || 0;
      if (!buckets.has(key)) buckets.set(key, []);
      buckets.get(key).push(node.id);
    }

    const horizontal = model.meta.direction !== "TB";
    const maxLayer = Math.max(0, ...Array.from(buckets.keys()));
    const maxItems = Math.max(1, ...Array.from(buckets.values()).map((items) => items.length));

    for (const [key, ids] of buckets) {
      ids.forEach((id, slot) => {
        const node = byId.get(id);
        if (horizontal) {
          node.x = PAD + key * GAP_X;
          node.y = PAD + slot * GAP_Y;
        } else {
          node.x = PAD + slot * GAP_X;
          node.y = PAD + key * GAP_Y;
        }
      });
    }

    const width = horizontal
      ? PAD * 2 + NODE_W + maxLayer * GAP_X
      : PAD * 2 + NODE_W + (maxItems - 1) * GAP_X;
    const height = horizontal
      ? PAD * 2 + NODE_H + (maxItems - 1) * GAP_Y
      : PAD * 2 + NODE_H + maxLayer * GAP_Y;

    return {
      nodes: Array.from(byId.values()),
      edges: model.edges,
      width,
      height,
      horizontal,
    };
  }

  function wrapText(text, maxChars = 22) {
    const words = String(text).split(/\s+/);
    const lines = [];
    let current = "";
    for (const word of words) {
      const next = current ? `${current} ${word}` : word;
      if (next.length > maxChars && current) {
        lines.push(current);
        current = word;
      } else {
        current = next;
      }
    }
    if (current) lines.push(current);
    return lines.slice(0, 3);
  }

  function nodeAnchor(node, horizontal, side) {
    if (horizontal) {
      return {
        x: side === "out" ? node.x + NODE_W : node.x,
        y: node.y + NODE_H / 2,
      };
    }
    return {
      x: node.x + NODE_W / 2,
      y: side === "out" ? node.y + NODE_H : node.y,
    };
  }

  function renderNode(node) {
    const style = TYPE_STYLES[node.type] || TYPE_STYLES.process;
    const labelLines = wrapText(node.label);
    const title = `<text x="${node.x + NODE_W / 2}" y="${node.y + 26}" text-anchor="middle" class="tf-node-type">${escapeHtml(node.type)}</text>`;
    const body = labelLines
      .map((line, index) => `<text x="${node.x + NODE_W / 2}" y="${node.y + 48 + index * 17}" text-anchor="middle" class="tf-node-label">${escapeHtml(line)}</text>`)
      .join("");

    if (node.type === "decision") {
      const points = [
        [node.x + NODE_W / 2, node.y],
        [node.x + NODE_W, node.y + NODE_H / 2],
        [node.x + NODE_W / 2, node.y + NODE_H],
        [node.x, node.y + NODE_H / 2],
      ]
        .map((point) => point.join(","))
        .join(" ");
      return `<g style="--tf-fill:${style.fill};--tf-stroke:${style.stroke};--tf-text:${style.text}"><polygon class="tf-node" points="${points}"></polygon>${title}${body}</g>`;
    }

    const radius = node.type === "start" || node.type === "end" ? 34 : 18;
    return `<g style="--tf-fill:${style.fill};--tf-stroke:${style.stroke};--tf-text:${style.text}"><rect class="tf-node" x="${node.x}" y="${node.y}" width="${NODE_W}" height="${NODE_H}" rx="${radius}"></rect>${title}${body}</g>`;
  }

  function renderEdge(edge, nodesById, horizontal) {
    const from = nodesById.get(edge.from);
    const to = nodesById.get(edge.to);
    if (!from || !to) return "";

    const start = nodeAnchor(from, horizontal, "out");
    const end = nodeAnchor(to, horizontal, "in");
    const midX = (start.x + end.x) / 2;
    const midY = (start.y + end.y) / 2;
    const path = horizontal
      ? `M ${start.x} ${start.y} C ${midX} ${start.y}, ${midX} ${end.y}, ${end.x} ${end.y}`
      : `M ${start.x} ${start.y} C ${start.x} ${midY}, ${end.x} ${midY}, ${end.x} ${end.y}`;
    const label = edge.label
      ? `<g><rect class="tf-edge-label-bg" x="${midX - 44}" y="${midY - 14}" width="88" height="24" rx="12"></rect><text class="tf-edge-label" x="${midX}" y="${midY + 4}" text-anchor="middle">${escapeHtml(edge.label)}</text></g>`
      : "";
    return `<path class="tf-edge" d="${path}" marker-end="url(#tf-arrow)"></path>${label}`;
  }

  function render(input, options = {}) {
    const model = parse(input);
    const layout = computeLayout(model);
    const nodesById = new Map(layout.nodes.map((node) => [node.id, node]));
    const title = options.title || model.meta.title;
    const edges = layout.edges.map((edge) => renderEdge(edge, nodesById, layout.horizontal)).join("");
    const nodes = layout.nodes.map(renderNode).join("");

    return `
      <figure class="tinyflow tinyflow-${escapeHtml(model.meta.skin)}">
        <figcaption>${escapeHtml(title)}</figcaption>
        <svg viewBox="0 0 ${layout.width} ${layout.height}" role="img" aria-label="${escapeHtml(title)}">
          <defs>
            <marker id="tf-arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
              <path d="M0,0 L0,6 L9,3 z" fill="#54756f"></path>
            </marker>
          </defs>
          <g>${edges}</g>
          <g>${nodes}</g>
        </svg>
      </figure>
    `;
  }

  window.TinyFlow = {
    parse,
    render,
  };
})();
