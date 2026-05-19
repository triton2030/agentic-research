import { useCallback } from "react";
import { layoutWithELK, routingForAlgorithm } from "../elk-layout";

// Чистый layout-калькулятор. ELK считает позиции + маршруты, мы кладём в state.
// Persistence + status — снаружи (usePageLayout).
export function useElkRunner({ setNodes, setEdges, onError }) {
  return useCallback(
    async ({ nodes, edges, opts, direction }) => {
      try {
        const { nodes: positioned, routesMap } = await layoutWithELK(
          nodes,
          edges,
          opts,
          direction
        );
        const routing = routingForAlgorithm(opts?.algorithm);
        const withRoutes = edges.map((e) => {
          const route = routesMap.get(e.id);
          return {
            ...e,
            type: "elk",
            data: {
              ...(e.data ?? {}),
              elkSections: route?.sections ?? null,
              routing
            }
          };
        });
        setNodes(positioned);
        setEdges(withRoutes);
        return { nodes: positioned, edges: withRoutes };
      } catch (e) {
        console.error(e);
        onError?.(e.message);
        return null;
      }
    },
    [setNodes, setEdges, onError]
  );
}
