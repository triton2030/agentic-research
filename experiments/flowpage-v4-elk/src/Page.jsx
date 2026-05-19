// Оркестратор одной диаграммы. Что где:
//   - state (nodes / edges) — useNodesState/useEdgesState из @xyflow/react.
//   - refs (nodesRef, edgesRef, optsRef, directionRef) — для async closures
//     usePageLayout / useElkRunner. Обновляются при каждом render.
//   - useElkRunner       — чистый layout-калькулятор (без persistence).
//   - usePageLayout      — load layout snapshot, autosave drag/settings/viewport,
//                          command applyLayout.
//   - PageCanvas         — рендер <ReactFlow>.
//
// useImperativeHandle exposes explicit shell commands: applyLayout/savePreset.
// Сохранение происходит автоматически: drag → save, applyLayout → save,
// viewport/settings change → save. Settings are props only; they never trigger layout.
//
// Контракт async closures: после смены page.id ReactFlowProvider в App имеет
// key={page.id}, поэтому весь Page разворачивается. Старые refs остаются
// валидными для уже запущенного async save — он завершится для правильного
// pageId.

import React, {
  forwardRef,
  useCallback,
  useImperativeHandle,
  useRef
} from "react";
import {
  useEdgesState,
  useNodesState,
  useReactFlow
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useElkRunner } from "./page/useElkRunner";
import { usePageLayout } from "./page/usePageLayout";
import { PageCanvas } from "./page/PageCanvas";
import { buildInitialNodes, buildInitialEdges } from "./page/buildInitial";

export const Page = forwardRef(function Page(
  { page, opts, direction, onStatusChange, onPresetLoaded },
  ref
) {
  const flow = useReactFlow();
  const [nodes, setNodes, onNodesChange] = useNodesState(buildInitialNodes(page.nodes));
  const [edges, setEdges, onEdgesChange] = useEdgesState(buildInitialEdges(page.edges));

  const nodesRef = useRef(nodes);
  nodesRef.current = nodes;
  const edgesRef = useRef(edges);
  edgesRef.current = edges;
  const optsRef = useRef(opts);
  optsRef.current = opts;
  const directionRef = useRef(direction);
  directionRef.current = direction;

  const setStatus = useCallback(
    (s) => {
      if (typeof onStatusChange === "function") onStatusChange(s);
    },
    [onStatusChange]
  );

  const runLayout = useElkRunner({
    setNodes,
    setEdges,
    onError: (msg) => setStatus(`ошибка: ${msg}`)
  });

  const { onNodeDrag, onNodeDragStop, onMoveEnd, applyLayout, savePreset } = usePageLayout({
    page,
    buildInitialNodes,
    buildInitialEdges,
    setNodes,
    setEdges,
    nodesRef,
    edgesRef,
    optsRef,
    directionRef,
    runLayout,
    setStatus,
    flow,
    onPresetLoaded
  });

  useImperativeHandle(ref, () => ({ applyLayout, savePreset }), [applyLayout, savePreset]);

  return (
    <PageCanvas
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onNodeDrag={onNodeDrag}
      onNodeDragStop={onNodeDragStop}
      onMoveEnd={onMoveEnd}
      description={page.description}
    />
  );
});
