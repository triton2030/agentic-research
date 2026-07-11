# Map Authoring Contract

Each map page is a JSON graph document in `src/maps/pages/*.json`.

Agent-friendly rule: edit JSON data, not React components.

Minimum page shape:

```json
{
  "id": "stable-page-id",
  "title": "Readable page title",
  "subtitle": "What this page explains",
  "nodes": [
    {
      "id": "stable-node-id",
      "type": "principle",
      "title": "Full node title",
      "summary": "One sentence shown in the reader rail.",
      "explanation": "Why this node matters.",
      "evidence": ["file.md: section or source note"],
      "quotes": [
        {
          "source": "file.md:12-13",
          "text": "Short verbatim quote that anchors the claim."
        }
      ],
      "agentOpinion": "Model judgement, separated from evidence.",
      "confidence": 0.8,
      "metrics": ["optional", "chips"],
      "openQuestions": ["optional unresolved question"]
    }
  ],
  "edges": [
    {
      "id": "stable-edge-id",
      "source": "source-node-id",
      "target": "target-node-id",
      "type": "defines",
      "label": "short line reason",
      "why": "Full causal rationale: why source implies target.",
      "quotes": [
        {
          "source": "file.md:42",
          "text": "Short verbatim quote that anchors this relationship."
        }
      ]
    }
  ],
  "corePath": ["node-a", "node-b"]
}
```

Reading model:

- Canvas nodes show full `title` values. Clicks select and highlight, but never resize nodes.
- The reader rail derives selected node, incoming edges, outgoing edges, selected edge rationale, and quotes from this data.
- Canvas edges show short `label` cards. The line, the label, and the reader card are clickable; full `why` and `quotes` live on the edge data.
- `corePath` powers the main-chain focus mode; it is not a separate source of truth.

Writing rules:

- `title` should be readable on the canvas without opening the reader rail.
- `shortTitle` is optional compatibility/search metadata; the canvas does not use it.
- `label` is the short reason drawn on the edge.
- `why` is the full causal explanation shown in the reader rail.
- `quotes` are verbatim source fragments with `file:line` anchors. Use them for any important node or edge.
- `agentOpinion` is allowed, but it must stay separate from `quotes` and `evidence`.
- Prefer one map page per question. Do not put the whole project in one canvas.
- If an edge needs a paragraph to make sense, add an intermediate node.
