import React, { useCallback } from "react";
import {
  Background,
  Controls,
  MiniMap,
  Panel,
  ReactFlow
} from "@xyflow/react";
import { nodeTypes } from "../nodes";
import { elkEdgeTypes } from "../ElkEdge";

const MINIMAP_COLORS = {
  skill: "#7db9aa",
  gate: "#e5b65b",
  memory: "#a6d8c9",
  review: "#a4a9c9",
  truth: "#b8c4e8",
  branch: "#dbb9e0",
  doc: "#dce4cf",
  output: "#f8d8a8"
};

export function PageCanvas({
  nodes,
  edges,
  onNodesChange,
  onEdgesChange,
  onNodeDrag,
  onNodeDragStop,
  onMoveEnd,
  description
}) {
  const minimapColor = useCallback((node) => {
    return MINIMAP_COLORS[node.data?.kind] ?? "#f5e5c7";
  }, []);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      nodeTypes={nodeTypes}
      edgeTypes={elkEdgeTypes}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onNodeDrag={onNodeDrag}
      onNodeDragStop={onNodeDragStop}
      onMoveEnd={onMoveEnd}
      minZoom={0.18}
      maxZoom={2.4}
      nodesDraggable
      nodesConnectable={false}
      elementsSelectable
      panOnScroll
      selectionOnDrag
      zoomOnDoubleClick={false}
      snapToGrid
      snapGrid={[20, 20]}
    >
      <Background color="#d5c7ad" gap={28} size={1.2} />
      <Controls showInteractive={false} />
      <MiniMap nodeColor={minimapColor} maskColor="rgba(28, 35, 38, 0.18)" pannable zoomable />
      {description ? (
        <Panel position="top-right">
          <div className="flow-note">{description}</div>
        </Panel>
      ) : null}
    </ReactFlow>
  );
}
