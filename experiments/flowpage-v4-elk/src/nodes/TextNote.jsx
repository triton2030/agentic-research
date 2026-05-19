// Свободный текст без карточки. Для аннотаций, заметок, мини-пояснений.
// Размеры: s (узкая короткая), m (средняя), l (широкая многострочная).
// Имеет handles чтобы могла быть участником стрелки-комментария.

import React from "react";
import { Handle, Position } from "@xyflow/react";

export const nodeType = "textNote";

const SIZE_DIMENSIONS = {
  s: { width: 200, charsPerLine: 22 },
  m: { width: 280, charsPerLine: 32 },
  l: { width: 380, charsPerLine: 44 }
};

const HANDLE_SIDES = [
  { id: "t", position: Position.Top },
  { id: "r", position: Position.Right },
  { id: "b", position: Position.Bottom },
  { id: "l", position: Position.Left }
];

export default function TextNote({ data }) {
  const size = data.size ?? "m";
  return (
    <div className={`flow-note-node flow-note-node--${size}`}>
      {HANDLE_SIDES.map((s) => (
        <React.Fragment key={s.id}>
          <Handle type="source" id={`s-${s.id}`} position={s.position} className="flow-handle flow-handle--auto" />
          <Handle type="target" id={`t-${s.id}`} position={s.position} className="flow-handle flow-handle--auto" />
        </React.Fragment>
      ))}
      <p>{data.text}</p>
    </div>
  );
}

export function nodeSize(data) {
  const size = data.size ?? "m";
  const { width, charsPerLine } = SIZE_DIMENSIONS[size] ?? SIZE_DIMENSIONS.m;
  const text = data.text ?? "";
  const lines = Math.max(1, Math.ceil(text.length / charsPerLine));
  const height = 24 + lines * 20;
  return { width, height };
}
