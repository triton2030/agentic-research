# Logic Map Lab

Prototype for readable causal maps built from prose business context. The
current seeded map explains:

```text
/Users/triton/Documents/My_projects/mavo-render-factory/
```

The experiment uses React Flow as the interactive canvas and keeps the map as
JSON graph data, not JSX. The intended future pipeline is:

```text
business prose -> extracted claims -> typed nodes/edges -> readable map
```

## What This Tests

- Causal map UX, not generic mind mapping.
- Stable canvas nodes that show full `title` values.
- Click-to-read behavior: selected node and its causal neighborhood are
  highlighted without moving layout.
- A right-hand reader for explanation, incoming/outgoing edge rationale,
  document quotes, evidence, confidence, agent opinion, and open questions.
- Canvas edge labels show short relationship descriptions; clicking a label,
  the edge path, or a reader edge card opens detailed edge data.
- A demo system path from owner vision to rendered product catalog.
- Animated causal arrows.
- Manual pan/zoom, with no automatic fit-to-view zoom.
- ELK spacing controls borrowed from the FlowPage v4 pattern.
- Multi-page map data under `src/maps/pages`.
- A schema shape that an agent can write without touching React components.

## Run

```bash
cd experiments/logical-map-lab
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5182/
```

Smoke test, with the dev server already running:

```bash
npm run test:smoke
```

## Files

- `src/maps/pages/*.json` - map pages with nodes, edges, labels, causal `why`, and quotes.
- `src/maps/index.js` - auto-registry for map pages.
- `src/maps/README.md` - agent authoring contract for new maps.
- `src/graph/layout.js` - ELK layout bridge and graph spacing settings.
- `src/reading/model.js` - derived node/edge reading projection.
- `src/components/LogicNode.jsx` - custom React Flow node.
- `src/components/Inspector.jsx` - selected node and edge reader.
- `src/App.jsx` - app state and canvas wiring.
- `assets/concept-logic-map-lab.png` - generated visual reference only.

## Boundary

This is not an automatic prose extraction engine yet. The important boundary is
that the UI consumes plain structured graph data, so a later agent pipeline can
replace the seed map without rewriting the renderer.
