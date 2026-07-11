export function buildReadingModel(map, selectedNodeId, selectedEdgeId) {
  const nodesById = new Map(map.nodes.map((node) => [node.id, node]));
  const selectedEdge = map.edges.find((edge) => edge.id === selectedEdgeId) ?? null;
  const selectedNode = selectedEdge && !selectedNodeId
    ? null
    : nodesById.get(selectedNodeId) ?? map.nodes[0] ?? null;

  if (selectedEdge && !selectedNode) {
    return {
      selectedNode: null,
      selectedEdge,
      incoming: [],
      outgoing: [],
      neighborhoodIds: new Set([selectedEdge.source, selectedEdge.target]),
      selectedEdgeIds: new Set([selectedEdge.id])
    };
  }

  if (!selectedNode) {
    return {
      selectedNode: null,
      selectedEdge,
      incoming: [],
      outgoing: [],
      neighborhoodIds: new Set(),
      selectedEdgeIds: new Set()
    };
  }

  const incoming = map.edges.filter((edge) => edge.target === selectedNode.id);
  const outgoing = map.edges.filter((edge) => edge.source === selectedNode.id);
  const selectedEdgeIds = new Set([...incoming, ...outgoing].map((edge) => edge.id));
  const neighborhoodIds = new Set([selectedNode.id]);

  for (const edge of [...incoming, ...outgoing]) {
    neighborhoodIds.add(edge.source);
    neighborhoodIds.add(edge.target);
  }

  return {
    selectedNode,
    selectedEdge,
    incoming,
    outgoing,
    neighborhoodIds,
    selectedEdgeIds
  };
}

export function nodeTitle(nodes, id) {
  return nodes.find((node) => node.id === id)?.title ?? id;
}
