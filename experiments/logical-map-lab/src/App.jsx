import { useCallback, useEffect, useMemo, useState } from "react";
import {
  applyNodeChanges,
  Background,
  Controls,
  MarkerType,
  Panel,
  ReactFlow
} from "@xyflow/react";
import { GitCommitHorizontal, MousePointer2 } from "lucide-react";
import { CausalEdge } from "./components/CausalEdge.jsx";
import { Inspector } from "./components/Inspector.jsx";
import { LogicNode } from "./components/LogicNode.jsx";
import { Sidebar } from "./components/Sidebar.jsx";
import { getNearestEdgeHandles } from "./graph/handles.js";
import { DEFAULT_EDGE_ROUTING, DEFAULT_OPTIONS, getNodeFrame, layoutGraph } from "./graph/layout.js";
import { defaultMapId, getMapById, maps } from "./maps/index.js";
import { buildReadingModel } from "./reading/model.js";

const flowNodeTypes = { logic: LogicNode };
const flowEdgeTypes = { causal: CausalEdge };
const THEME_STORAGE_KEY = "logical-map-lab-theme";
const SIDEBAR_STORAGE_KEY = "logical-map-lab-sidebar-collapsed";

function readStoredTheme() {
  if (typeof window === "undefined") return "light";

  return window.localStorage.getItem(THEME_STORAGE_KEY) === "dark" ? "dark" : "light";
}

function readStoredSidebarState() {
  if (typeof window === "undefined") return false;

  return window.localStorage.getItem(SIDEBAR_STORAGE_KEY) === "true";
}

function buildBaseNode(node) {
  return {
    id: node.id,
    type: "logic",
    position: node.position,
    data: node,
    draggable: true,
    style: { width: node.layoutWidth, height: node.layoutHeight }
  };
}

function buildNodeFrame(node) {
  const fallbackFrame = getNodeFrame();
  const width = node.layoutWidth ?? node.style?.width ?? fallbackFrame.width;
  const height = node.layoutHeight ?? node.style?.height ?? fallbackFrame.height;

  return {
    x: node.position.x,
    y: node.position.y,
    width,
    height,
    centerX: node.position.x + width / 2,
    centerY: node.position.y + height / 2
  };
}

export function App() {
  const [activeMapId, setActiveMapId] = useState(defaultMapId);
  const [theme, setTheme] = useState(readStoredTheme);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(readStoredSidebarState);
  const [baseNodes, setBaseNodes] = useState([]);
  const [edgeLayouts, setEdgeLayouts] = useState(() => new Map());
  const [selectedNodeId, setSelectedNodeId] = useState(null);
  const [selectedEdgeId, setSelectedEdgeId] = useState(null);
  const [focusPath, setFocusPath] = useState(false);
  const [layoutOptions, setLayoutOptions] = useState(DEFAULT_OPTIONS);
  const [layoutStatus, setLayoutStatus] = useState("Готово");

  const activeMap = useMemo(() => getMapById(activeMapId), [activeMapId]);
  const nodeById = useMemo(() => new Map(activeMap.nodes.map((node) => [node.id, node])), [activeMap]);
  const pathNodeIds = useMemo(() => new Set(activeMap.corePath ?? []), [activeMap]);
  const pathEdgeKeys = useMemo(
    () => new Set((activeMap.corePath ?? []).slice(0, -1).map((id, index) => `${id}->${activeMap.corePath[index + 1]}`)),
    [activeMap]
  );
  const readingModel = useMemo(
    () => buildReadingModel(activeMap, selectedNodeId, selectedEdgeId),
    [activeMap, selectedEdgeId, selectedNodeId]
  );
  const isDarkTheme = theme === "dark";

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    window.localStorage.setItem(THEME_STORAGE_KEY, theme);
  }, [theme]);

  useEffect(() => {
    window.localStorage.setItem(SIDEBAR_STORAGE_KEY, String(sidebarCollapsed));
  }, [sidebarCollapsed]);

  const selectNodeNeighborhood = useCallback(
    (id) => {
      setSelectedNodeId(id);
      setSelectedEdgeId(null);
    },
    []
  );

  const selectEdgeForReading = useCallback(
    (id) => {
      setSelectedEdgeId(id);
      setSelectedNodeId(null);
    },
    []
  );

  const clearReaderFocus = useCallback(() => {
    setSelectedEdgeId(null);
  }, []);

  const runLayout = useCallback(async () => {
    setLayoutStatus("Раскладываю...");
    try {
      const { nodes: positioned, edgeLayouts: layoutMap, routing } = await layoutGraph(activeMap.nodes, activeMap.edges, layoutOptions);
      setBaseNodes(positioned.map(buildBaseNode));
      setEdgeLayouts(
        new Map(
          Array.from(layoutMap.entries()).map(([id, edgeLayout]) => [
            id,
            { ...edgeLayout, routing }
          ])
        )
      );
      setLayoutStatus("ELK применён");
    } catch (error) {
      console.error(error);
      setLayoutStatus("Ошибка layout");
    }
  }, [activeMap, layoutOptions]);

  useEffect(() => {
    runLayout();
  }, [runLayout]);

  useEffect(() => {
    setSelectedNodeId(activeMap.nodes[0]?.id ?? null);
    setSelectedEdgeId(null);
    setFocusPath(false);
    setEdgeLayouts(new Map());
  }, [activeMap]);

  function updateLayoutOption(key, value) {
    setLayoutOptions((current) => ({ ...current, [key]: value }));
    setLayoutStatus("Настройки изменены; примените ELK");
  }

  function resetLayoutOptions() {
    setLayoutOptions(DEFAULT_OPTIONS);
    setLayoutStatus("Настройки сброшены; примените ELK");
  }

  const flowNodes = useMemo(
    () =>
      baseNodes.map((node) => {
        const raw = nodeById.get(node.id) ?? node.data;
        const typeInfo = activeMap.nodeTypes[raw.type] ?? activeMap.nodeTypes.risk;
        const outsidePath = focusPath && !pathNodeIds.has(node.id);
        const outsideReaderFocus = readingModel.neighborhoodIds.size > 0 && !readingModel.neighborhoodIds.has(node.id);
        const dimmed = outsidePath || outsideReaderFocus;
        return {
          ...node,
          selected: node.id === selectedNodeId,
          data: {
            ...raw,
            neighbor: readingModel.neighborhoodIds.has(node.id) && node.id !== selectedNodeId,
            dimmed,
            typeInfo,
          }
        };
      }),
    [activeMap, baseNodes, focusPath, nodeById, pathNodeIds, readingModel.neighborhoodIds, selectedNodeId]
  );

  const nodeFramesById = useMemo(
    () => new Map(baseNodes.map((node) => [node.id, buildNodeFrame(node)])),
    [baseNodes]
  );
  const nodeFrames = useMemo(() => Array.from(nodeFramesById.values()), [nodeFramesById]);

  const flowEdges = useMemo(
    () =>
      activeMap.edges.map((edge) => {
        const meta = activeMap.edgeTypes[edge.type] ?? activeMap.edgeTypes.defines;
        const inPath = pathEdgeKeys.has(`${edge.source}->${edge.target}`);
        const outsidePath = focusPath && !inPath;
        const outsideReaderFocus = readingModel.selectedEdgeIds.size > 0 && !readingModel.selectedEdgeIds.has(edge.id);
        const dimmed = outsidePath || outsideReaderFocus;
        const selected = readingModel.selectedEdgeIds.has(edge.id);
        const edgeLayout = edgeLayouts.get(edge.id);
        const routing = edgeLayout?.routing ?? layoutOptions.edgeRouting ?? DEFAULT_EDGE_ROUTING;
        const routeForHandles = routing === "SPLINES" ? null : edgeLayout;
        return {
          id: edge.id,
          source: edge.source,
          target: edge.target,
          ...getNearestEdgeHandles(edge, nodeFramesById, routeForHandles),
          type: "causal",
          data: {
            label: edge.label ?? meta.label,
            kindLabel: meta.label,
            why: edge.why,
            color: meta.color,
            elkSections: routing === "SPLINES" ? null : edgeLayout?.sections ?? null,
            elkLabelCenter: edgeLayout?.labelCenter ?? null,
            nodeFrames,
            routing,
            dimmed,
            onSelect: selectEdgeForReading
          },
          ariaLabel: `Связь: ${edge.label ?? meta.label}`,
          markerEnd: { type: MarkerType.ArrowClosed, color: meta.color },
          style: {
            stroke: meta.color,
            strokeWidth: selected || inPath ? 3 : 2,
            opacity: dimmed ? 0.16 : 0.92,
            strokeDasharray: "10 8",
            animation: dimmed ? "none" : "flow-dash 1.2s linear infinite"
          }
        };
      }),
    [
      activeMap,
      edgeLayouts,
      focusPath,
      layoutOptions.edgeRouting,
      nodeFramesById,
      nodeFrames,
      pathEdgeKeys,
      readingModel.selectedEdgeIds,
      selectEdgeForReading
    ]
  );

  const handleNodesChange = useCallback((changes) => {
    const positionChanged = changes.some((change) => change.type === "position");
      setBaseNodes((current) => applyNodeChanges(changes, current));

    if (positionChanged) {
      setEdgeLayouts(new Map());
      setLayoutStatus("Позиции изменены; примените ELK");
    }
  }, []);

  return (
    <div className={`app-shell theme-${theme} ${sidebarCollapsed ? "app-shell--sidebar-collapsed" : ""}`}>
      <Sidebar
        activeMap={activeMap}
        activeMapId={activeMap.id}
        maps={maps}
        theme={theme}
        collapsed={sidebarCollapsed}
        focusPath={focusPath}
        layoutOptions={layoutOptions}
        onMapChange={setActiveMapId}
        onLayoutOptionChange={updateLayoutOption}
        onResetLayoutOptions={resetLayoutOptions}
        onToggleTheme={() => setTheme((value) => (value === "dark" ? "light" : "dark"))}
        onToggleSidebar={() => setSidebarCollapsed((value) => !value)}
        onToggleFocusPath={() => setFocusPath((value) => !value)}
        onCollapseAll={clearReaderFocus}
        onRelayout={runLayout}
      />
      <main className="map-shell">
        <header className="topbar">
          <div>
            <p>{activeMap.title}</p>
            <h2>{activeMap.subtitle}</h2>
          </div>
          <div className="topbar__meta">
            <span>
              <GitCommitHorizontal aria-hidden="true" size={15} />
              {activeMap.nodes.length} нод / {activeMap.edges.length} связей
            </span>
            <span>
              <MousePointer2 aria-hidden="true" size={15} />
              Клик по ноде или ребру открывает reader
            </span>
          </div>
        </header>
        <section className="canvas-frame" aria-label="Logic map canvas">
          <ReactFlow
            key={activeMap.id}
            nodes={flowNodes}
            edges={flowEdges}
            nodeTypes={flowNodeTypes}
            edgeTypes={flowEdgeTypes}
            onNodesChange={handleNodesChange}
            onNodeClick={(_, node) => selectNodeNeighborhood(node.id)}
            onEdgeClick={(_, edge) => selectEdgeForReading(edge.id)}
            minZoom={0.06}
            maxZoom={1.2}
            defaultViewport={{ x: 0, y: 0, zoom: 1 }}
            proOptions={{ hideAttribution: true }}
          >
            <Background color={isDarkTheme ? "#263449" : "#dbe3ee"} gap={24} size={1.2} />
            <Controls position="bottom-right" showInteractive={false} />
            <Panel position="top-right" className="canvas-panel">
              <span>{layoutStatus}</span>
              <strong>{focusPath ? "Главная цепочка" : "Вся карта"}</strong>
            </Panel>
          </ReactFlow>
        </section>
      </main>
      <Inspector
        edgeTypes={activeMap.edgeTypes}
        node={readingModel.selectedNode}
        nodeTypes={activeMap.nodeTypes}
        nodes={activeMap.nodes}
        edge={readingModel.selectedEdge}
        incoming={readingModel.incoming}
        outgoing={readingModel.outgoing}
        onSelectEdge={selectEdgeForReading}
      />
    </div>
  );
}
