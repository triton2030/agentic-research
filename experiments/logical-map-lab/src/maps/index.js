import { edgeTypes, nodeTypes } from "./types.js";

const pageModules = import.meta.glob("./pages/*.json", { eager: true, import: "default" });

function hydrateMap(map) {
  return {
    ...map,
    nodeTypes,
    edgeTypes,
    nodes: map.nodes ?? [],
    edges: map.edges ?? [],
    corePath: map.corePath ?? []
  };
}

export const maps = Object.values(pageModules)
  .map(hydrateMap)
  .filter(Boolean)
  .sort((a, b) => (a.order ?? 999) - (b.order ?? 999) || a.title.localeCompare(b.title));

export const defaultMapId = "mavo-render-factory";

export function getMapById(id) {
  return maps.find((map) => map.id === id) ?? maps[0];
}
