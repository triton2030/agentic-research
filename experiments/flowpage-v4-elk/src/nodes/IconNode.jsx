// Маленький узел только с символом, emoji или Material Symbol. Маркер,
// breakpoint, переключатель, иконка-связка. С handles — может быть в стрелках.

import React from "react";
import { Handle, Position } from "@xyflow/react";

export const nodeType = "iconNode";

const HANDLE_SIDES = [
  { id: "t", position: Position.Top },
  { id: "r", position: Position.Right },
  { id: "b", position: Position.Bottom },
  { id: "l", position: Position.Left }
];

export default function IconNode({ data }) {
  const iconSet = data.iconSet ?? "text";
  const glyphClass = iconSet === "material"
    ? "flow-icon-node__glyph flow-icon-node__glyph--material"
    : "flow-icon-node__glyph";

  return (
    <div className="flow-icon-node" title={data.tooltip ?? ""}>
      {HANDLE_SIDES.map((s) => (
        <React.Fragment key={s.id}>
          <Handle type="source" id={`s-${s.id}`} position={s.position} className="flow-handle flow-handle--auto" />
          <Handle type="target" id={`t-${s.id}`} position={s.position} className="flow-handle flow-handle--auto" />
        </React.Fragment>
      ))}
      <span className={glyphClass} aria-hidden={iconSet === "material" ? "true" : undefined}>
        {data.icon}
      </span>
      {data.label ? <span className="flow-icon-node__label">{data.label}</span> : null}
    </div>
  );
}

export function nodeSize(data) {
  const hasLabel = !!data.label;
  return { width: hasLabel ? 120 : 72, height: 72 };
}
