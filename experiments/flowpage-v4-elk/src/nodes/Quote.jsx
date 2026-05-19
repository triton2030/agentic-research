// Выделенная цитата с акцентной полосой слева. Для важных формулировок,
// которые нужно запомнить или подчеркнуть как «правило».

import React from "react";
import { Handle, Position } from "@xyflow/react";

export const nodeType = "quote";

const HANDLE_SIDES = [
  { id: "t", position: Position.Top },
  { id: "r", position: Position.Right },
  { id: "b", position: Position.Bottom },
  { id: "l", position: Position.Left }
];

export default function Quote({ data }) {
  return (
    <blockquote className="flow-quote">
      {HANDLE_SIDES.map((s) => (
        <React.Fragment key={s.id}>
          <Handle type="source" id={`s-${s.id}`} position={s.position} className="flow-handle flow-handle--auto" />
          <Handle type="target" id={`t-${s.id}`} position={s.position} className="flow-handle flow-handle--auto" />
        </React.Fragment>
      ))}
      <p>{data.text}</p>
      {data.cite ? <footer className="flow-quote__cite">— {data.cite}</footer> : null}
    </blockquote>
  );
}

export function nodeSize(data) {
  const text = data.text ?? "";
  const lines = Math.max(2, Math.ceil(text.length / 36));
  const width = 340;
  const height = 36 + lines * 22 + (data.cite ? 24 : 0);
  return { width, height };
}
