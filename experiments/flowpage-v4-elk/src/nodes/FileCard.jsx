// Карточка-документ с явным значком расширения. Для файлов проекта
// (README.md, settings.json, и т.п.). Расширение выводится из имени.

import React from "react";
import { Handle, Position } from "@xyflow/react";

export const nodeType = "fileCard";

const HANDLE_SIDES = [
  { id: "t", position: Position.Top },
  { id: "r", position: Position.Right },
  { id: "b", position: Position.Bottom },
  { id: "l", position: Position.Left }
];

function extOf(title) {
  const m = (title ?? "").match(/\.([a-z0-9]+)$/i);
  return m ? m[1].toLowerCase() : "doc";
}

export default function FileCard({ data }) {
  const ext = data.ext ?? extOf(data.title);
  return (
    <div className={`flow-file-card flow-file-card--${ext}`}>
      {HANDLE_SIDES.map((s) => (
        <React.Fragment key={s.id}>
          <Handle type="source" id={`s-${s.id}`} position={s.position} className="flow-handle flow-handle--auto" />
          <Handle type="target" id={`t-${s.id}`} position={s.position} className="flow-handle flow-handle--auto" />
        </React.Fragment>
      ))}
      <div className="flow-file-card__ext">{ext}</div>
      <div className="flow-file-card__name">{data.title}</div>
      {data.note ? <div className="flow-file-card__note">{data.note}</div> : null}
    </div>
  );
}

export function nodeSize(data) {
  const hasNote = !!data.note;
  return { width: 260, height: hasNote ? 110 : 72 };
}
