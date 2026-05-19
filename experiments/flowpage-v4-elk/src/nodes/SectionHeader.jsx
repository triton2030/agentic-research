// Крупный заголовок-якорь над группой узлов. По умолчанию используется как
// чисто визуальный маркер, но имеет handles на случай если хочется
// соединить с группой стрелкой-якорем (например dimmed edge).

import React from "react";
import { Handle, Position } from "@xyflow/react";

export const nodeType = "sectionHeader";

const HANDLE_SIDES = [
  { id: "t", position: Position.Top },
  { id: "r", position: Position.Right },
  { id: "b", position: Position.Bottom },
  { id: "l", position: Position.Left }
];

export default function SectionHeader({ data }) {
  return (
    <div className="flow-section-header">
      {HANDLE_SIDES.map((s) => (
        <React.Fragment key={s.id}>
          <Handle type="source" id={`s-${s.id}`} position={s.position} className="flow-handle flow-handle--auto" />
          <Handle type="target" id={`t-${s.id}`} position={s.position} className="flow-handle flow-handle--auto" />
        </React.Fragment>
      ))}
      <h2>{data.title}</h2>
      {data.subtitle ? <p className="flow-section-header__sub">{data.subtitle}</p> : null}
    </div>
  );
}

export function nodeSize(data) {
  const titleLen = (data.title ?? "").length;
  const subLen = (data.subtitle ?? "").length;
  const width = Math.max(280, Math.min(520, titleLen * 12 + 40));
  const height = subLen > 0 ? 84 : 56;
  return { width, height };
}
