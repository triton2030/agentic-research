// Универсальная карточка узла: kicker (надстрочник) + title + body + bullets.
// Стилизация через kind-классы (origin/skill/gate/memory/review/...) + weight.
// Подключается к ELK через 4 handles (top/right/bottom/left) на каждом узле —
// ELK сам решает с какой стороны рисовать ребро.

import React from "react";
import { Handle, Position } from "@xyflow/react";

export const nodeType = "skillCard";

const HANDLE_SIDES = [
  { id: "t", position: Position.Top },
  { id: "r", position: Position.Right },
  { id: "b", position: Position.Bottom },
  { id: "l", position: Position.Left }
];

export default function SkillCard({ data }) {
  const weight = data.weight ?? 2;
  const className = [
    "flow-card",
    `flow-card--${data.kind ?? "skill"}`,
    `flow-card--w${weight}`
  ].join(" ");
  return (
    <article className={className}>
      {HANDLE_SIDES.map((s) => (
        <React.Fragment key={s.id}>
          <Handle
            type="source"
            id={`s-${s.id}`}
            position={s.position}
            className="flow-handle flow-handle--auto"
          />
          <Handle
            type="target"
            id={`t-${s.id}`}
            position={s.position}
            className="flow-handle flow-handle--auto"
          />
        </React.Fragment>
      ))}
      <div className="flow-card__topline">
        <span>{data.kicker}</span>
      </div>
      <h2>{data.title}</h2>
      {data.body ? <p>{data.body}</p> : null}
      {data.bullets && data.bullets.length > 0 ? (
        <div className="flow-card__chips">
          {data.bullets.map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      ) : null}
    </article>
  );
}

// Геометрия для ELK: ширина зависит от weight, высота — приблизительная
// оценка по контенту. ELK использует их как layout-input.
export function cardWidth(weight) {
  if (weight >= 3) return 380;
  if (weight === 1) return 260;
  return 340;
}

export function estimateHeight(node) {
  const w = cardWidth(node.weight ?? 2);
  const bodyChars = (node.body ?? "").length;
  const charsPerLine = Math.max(28, Math.floor((w - 40) / 8));
  const bodyLines = Math.ceil(bodyChars / charsPerLine);
  const chipsUnits = (node.bullets ?? []).reduce(
    (sum, b) => sum + b.length + 3,
    0
  );
  const chipRows = Math.max(0, Math.ceil(chipsUnits / 28));
  const base = 88;
  return Math.max(140, Math.min(320, base + bodyLines * 22 + chipRows * 36));
}

// Размер для ELK layout-input. Контракт `nodeSize(data) → {width, height}`
// общий для всех node-типов — реализуется в каждом файле, используется
// в buildInitial.
export function nodeSize(data) {
  return { width: cardWidth(data.weight ?? 2), height: estimateHeight(data) };
}
