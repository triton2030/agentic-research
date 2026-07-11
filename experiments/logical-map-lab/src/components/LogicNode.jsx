import { Fragment } from "react";
import { Handle, Position } from "@xyflow/react";
import { HANDLE_SIDES, sourceHandleId, targetHandleId } from "../graph/handles.js";

const HANDLE_POSITIONS = {
  top: Position.Top,
  right: Position.Right,
  bottom: Position.Bottom,
  left: Position.Left
};

export function LogicNode({ data, selected }) {
  const type = data.typeInfo;
  const className = [
    "logic-node",
    "logic-node--collapsed",
    selected ? "logic-node--selected" : "",
    data.neighbor ? "logic-node--neighbor" : "",
    data.dimmed ? "logic-node--dimmed" : ""
  ].join(" ");

  return (
    <article
      className={className}
      style={{ "--node-color": type.color, "--node-tint": type.tint }}
    >
      {HANDLE_SIDES.map((side) => (
        <Fragment key={side}>
          <Handle
            type="source"
            id={sourceHandleId(side)}
            position={HANDLE_POSITIONS[side]}
            className="logic-node__handle"
          />
          <Handle
            type="target"
            id={targetHandleId(side)}
            position={HANDLE_POSITIONS[side]}
            className="logic-node__handle"
          />
        </Fragment>
      ))}
      <div className="logic-node__bar" />
      <h3>{data.title}</h3>
    </article>
  );
}
