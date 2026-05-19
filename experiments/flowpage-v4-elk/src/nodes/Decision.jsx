// Точка ветвления — diamond. Для условий «если X → A, иначе B».
// Handles на 4-х углах ромба (через CSS rotation).

import React from "react";
import { Handle, Position } from "@xyflow/react";

export const nodeType = "decision";

const HANDLE_SIDES = [
  { id: "t", position: Position.Top },
  { id: "r", position: Position.Right },
  { id: "b", position: Position.Bottom },
  { id: "l", position: Position.Left }
];

export default function Decision({ data }) {
  return (
    <div className="flow-decision">
      {HANDLE_SIDES.map((s) => (
        <React.Fragment key={s.id}>
          <Handle type="source" id={`s-${s.id}`} position={s.position} className="flow-handle flow-handle--auto" />
          <Handle type="target" id={`t-${s.id}`} position={s.position} className="flow-handle flow-handle--auto" />
        </React.Fragment>
      ))}
      <div className="flow-decision__shape" />
      <div className="flow-decision__text">{data.title}</div>
    </div>
  );
}

export function nodeSize(data) {
  const titleLen = (data.title ?? "").length;
  return { width: Math.max(180, titleLen * 9 + 60), height: 120 };
}
