// Owns one page's layout snapshot lifecycle:
// - load: read { positions, routes, viewport, options, direction }; never run ELK on load.
// - drag: save new positions and null routes for touched edges.
// - move: debounce-save viewport as part of the same snapshot.
// - preset: save ELK options/direction into the same snapshot, without layout.
// - applyLayout: explicit button path from current settings to a new snapshot.

import { useCallback, useEffect, useRef } from "react";
import { loadLayout, saveLayout } from "../storage";
import { EDGE_ROUTING } from "../elk-layout";

function collectPositions(nodes) {
  const positions = {};
  for (const n of nodes) {
    positions[n.id] = { x: n.position.x, y: n.position.y };
  }
  return positions;
}

function collectRoutes(edges, invalidate = null) {
  const routes = {};
  const invalidSet = invalidate ? new Set(invalidate) : null;
  for (const e of edges) {
    const touched = invalidSet && (invalidSet.has(e.source) || invalidSet.has(e.target));
    routes[e.id] = {
      sections: touched ? null : (e.data?.elkSections ?? null),
      routing: e.data?.routing ?? EDGE_ROUTING
    };
  }
  return routes;
}

function applyRoutesToEdges(edges, routes) {
  if (!routes) return edges;
  return edges.map((e) => {
    const route = routes[e.id];
    if (!route) return e;
    return {
      ...e,
      type: "elk",
      data: {
        ...(e.data ?? {}),
        elkSections: route.sections ?? null,
        routing: route.routing ?? EDGE_ROUTING
      }
    };
  });
}

export function usePageLayout({
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
}) {
  const pageIdRef = useRef(page.id);
  pageIdRef.current = page.id;
  const saveQueueRef = useRef(Promise.resolve());
  const viewportTimerRef = useRef(null);
  const suppressViewportSaveUntilRef = useRef(0);

  const suppressViewportSave = useCallback((ms = 600) => {
    suppressViewportSaveUntilRef.current = Math.max(
      suppressViewportSaveUntilRef.current,
      Date.now() + ms
    );
  }, []);

  const collectLayout = useCallback(
    (override = {}) => ({
      positions: override.positions ?? collectPositions(nodesRef.current),
      routes: override.routes ?? collectRoutes(edgesRef.current),
      viewport: override.viewport ?? flow.getViewport(),
      options: override.options ?? optsRef.current,
      direction: override.direction ?? directionRef.current
    }),
    [nodesRef, edgesRef, optsRef, directionRef, flow]
  );

  const enqueueSave = useCallback(
    (layout, statusText = null) => {
      const pageId = pageIdRef.current;
      saveQueueRef.current = saveQueueRef.current
        .catch(() => null)
        .then(async () => {
          try {
            await saveLayout(pageId, layout);
            if (statusText) setStatus?.(statusText);
          } catch (e) {
            setStatus?.(`ошибка сохранения: ${e.message}`);
          }
        });
      return saveQueueRef.current;
    },
    [setStatus]
  );

  useEffect(() => {
    let cancelled = false;
    const freshNodes = buildInitialNodes(page.nodes);
    const freshEdges = buildInitialEdges(page.edges);
    setNodes(freshNodes);
    setEdges(freshEdges);

    (async () => {
      let res;
      try {
        res = await loadLayout(page.id);
      } catch (e) {
        if (!cancelled) setStatus?.(`ошибка загрузки раскладки: ${e.message}`);
        return;
      }
      if (cancelled) return;
      const { layout } = res;

      if (!layout?.positions) {
        setStatus?.("нет сохранённой раскладки — нажми «Применить ELK»");
        return;
      }

      onPresetLoaded?.({ options: layout.options, direction: layout.direction });

      const restoredNodes = freshNodes.map((n) =>
        layout.positions[n.id] ? { ...n, position: { ...layout.positions[n.id] } } : n
      );
      setNodes(restoredNodes);
      setEdges(applyRoutesToEdges(freshEdges, layout.routes));
      setStatus?.("раскладка загружена");

      suppressViewportSave();
      window.requestAnimationFrame(() => {
        if (layout.viewport) {
          flow.setViewport(layout.viewport, { duration: 0 });
        } else {
          flow.fitView({ padding: 0.16, duration: 0 });
        }
      });
    })();

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page.id]);

  const invalidateEdgesFor = useCallback(
    (nodeIds) => {
      const ids = new Set(nodeIds);
      setEdges((prev) =>
        prev.map((e) =>
          ids.has(e.source) || ids.has(e.target)
            ? { ...e, data: { ...(e.data ?? {}), elkSections: null } }
            : e
        )
      );
    },
    [setEdges]
  );

  const onNodeDrag = useCallback(
    (_, draggedNode) => {
      invalidateEdgesFor([draggedNode.id]);
    },
    [invalidateEdgesFor]
  );

  const onNodeDragStop = useCallback(
    (_, draggedNode) => {
      invalidateEdgesFor([draggedNode.id]);
      const positions = collectPositions(nodesRef.current);
      const routes = collectRoutes(edgesRef.current, [draggedNode.id]);
      enqueueSave(
        collectLayout({ positions, routes }),
        "ручная правка сохранена"
      );
    },
    [invalidateEdgesFor, nodesRef, edgesRef, collectLayout, enqueueSave]
  );

  const onMoveEnd = useCallback(() => {
    if (Date.now() < suppressViewportSaveUntilRef.current) return;
    if (viewportTimerRef.current) clearTimeout(viewportTimerRef.current);
    viewportTimerRef.current = setTimeout(() => {
      viewportTimerRef.current = null;
      enqueueSave(collectLayout());
    }, 250);
  }, [collectLayout, enqueueSave]);

  const savePreset = useCallback(
    (options, direction) => {
      enqueueSave(collectLayout({ options, direction }));
    },
    [collectLayout, enqueueSave]
  );

  const applyLayout = useCallback(async () => {
    const options = optsRef.current;
    const direction = directionRef.current;
    const res = await runLayout({
      nodes: nodesRef.current,
      edges: edgesRef.current,
      opts: options,
      direction
    });
    if (!res) return;

    await new Promise((resolve) => window.requestAnimationFrame(resolve));
    suppressViewportSave();
    await flow.fitView({ padding: 0.16, duration: 0 });

    const positions = collectPositions(res.nodes);
    const routes = collectRoutes(res.edges);
    await enqueueSave(
      collectLayout({ positions, routes, viewport: flow.getViewport(), options, direction }),
      "раскладка применена"
    );
  }, [
    runLayout,
    nodesRef,
    edgesRef,
    optsRef,
    directionRef,
    flow,
    collectLayout,
    enqueueSave,
    suppressViewportSave
  ]);

  return { onNodeDrag, onNodeDragStop, onMoveEnd, applyLayout, savePreset };
}
