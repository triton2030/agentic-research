// Persistence model:
//
//   layout snapshot — the only truth about one graph.
//     Shape: { positions, routes, viewport, options, direction }.
//     Storage: data/layouts/<id>.json through the Vite dev API.
//
// Loading a page is a pure read of the snapshot. Settings are saved into the
// same file, but they change geometry only after the explicit "Apply ELK" run.

const API_BASE = "/api/layout";

function finiteNumber(value) {
  return typeof value === "number" && Number.isFinite(value);
}

function extractViewport(raw) {
  if (!raw || typeof raw !== "object") return null;
  const { x, y, zoom } = raw;
  if (!finiteNumber(x) || !finiteNumber(y) || !finiteNumber(zoom)) return null;
  return { x, y, zoom };
}

function extractPositions(raw) {
  if (!raw || typeof raw !== "object") return null;
  const values = Object.values(raw);
  if (values.length === 0) return null;
  const looksFlat = values.every(
    (v) => v && typeof v === "object" && finiteNumber(v.x) && finiteNumber(v.y)
  );
  return looksFlat ? raw : null;
}

function extractLayout(raw) {
  if (!raw || typeof raw !== "object") return null;
  const positions = extractPositions(raw.positions);
  if (!positions) return null;
  if (!raw.options || typeof raw.options !== "object") return null;
  if (typeof raw.direction !== "string") return null;
  return {
    positions,
    routes: raw.routes && typeof raw.routes === "object" ? raw.routes : {},
    viewport: extractViewport(raw.viewport),
    options: raw.options,
    direction: raw.direction
  };
}

export async function loadLayout(pageId) {
  const r = await fetch(`${API_BASE}/${encodeURIComponent(pageId)}`);
  if (r.status === 404) return { source: "none", layout: null };
  if (!r.ok) throw new Error(`layout load failed: ${r.status}`);
  const layout = extractLayout(await r.json());
  if (!layout) throw new Error(`layout file is invalid: ${pageId}`);
  return { source: "file", layout };
}

export async function saveLayout(pageId, layout) {
  if (!layout.options || typeof layout.direction !== "string") {
    throw new Error("layout snapshot missing options/direction");
  }
  const payload = {
    positions: layout.positions,
    routes: layout.routes ?? {},
    viewport: layout.viewport ?? null,
    options: layout.options,
    direction: layout.direction
  };

  const r = await fetch(`${API_BASE}/${encodeURIComponent(pageId)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!r.ok) throw new Error(`layout save failed: ${r.status}`);
  const data = await r.json();
  return { source: "file", filePath: data.path };
}
