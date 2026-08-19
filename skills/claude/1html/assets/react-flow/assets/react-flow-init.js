(() => {
  "use strict";

  const API_VERSION = "1.0.0";
  const existingApi = window.HTMLReactFlow;
  if (existingApi?.version === API_VERSION) {
    existingApi.mountAll();
    return;
  }

  const vendor = window.HTMLReactFlowVendor;
  if (!vendor) {
    throw new Error("React Flow vendor bundle must load before react-flow-init.js");
  }

  const { React, createRoot, XYFlow } = vendor;
  const {
    Background,
    BaseEdge,
    Controls,
    EdgeLabelRenderer,
    Handle,
    Panel,
    Position,
    ReactFlow,
    getSmoothStepPath,
    useUpdateNodeInternals,
  } = XYFlow;
  const mounted = new WeakMap();
  const h = React.createElement;

  function fail(message) {
    throw new Error(message);
  }

  function positionFor(value, fallback) {
    if (typeof value !== "string") return fallback;
    return Position[value] || Object.values(Position).find((item) => item === value) || fallback;
  }

  function finiteNumber(value, fallback) {
    return Number.isFinite(value) ? value : fallback;
  }

  function nodeTemplate(templateId) {
    const template = document.getElementById(templateId);
    if (!(template instanceof HTMLTemplateElement)) {
      fail(`React Flow node template not found: ${templateId}`);
    }
    return template;
  }

  function normalizeNode(node) {
    const { data, handles, kind, label, template, ...nodeOptions } = node;
    if (data !== undefined && (!data || typeof data !== "object" || Array.isArray(data))) {
      fail(`React Flow node data must be an object: ${node.id}`);
    }
    return {
      ...nodeOptions,
      data: {
        ...(data || {}),
        ...(template === undefined ? {} : { template }),
        ...(label === undefined ? {} : { label }),
        ...(handles === undefined ? {} : { handles }),
        ...(kind === undefined ? {} : { kind }),
      },
    };
  }

  function validateConfig(config) {
    if (!config || typeof config !== "object" || Array.isArray(config)) {
      fail("React Flow config must be a JSON object");
    }
    if (!Array.isArray(config.nodes) || !config.nodes.length) {
      fail("React Flow config needs a non-empty nodes array");
    }
    if (config.edges !== undefined && !Array.isArray(config.edges)) {
      fail("React Flow config edges must be an array");
    }

    const nodeIds = new Set();
    const nodes = [];
    for (const rawNode of config.nodes) {
      const node = rawNode && typeof rawNode === "object" && !Array.isArray(rawNode)
        ? normalizeNode(rawNode)
        : rawNode;
      if (!node || typeof node !== "object" || typeof node.id !== "string" || !node.id) {
        fail("Every React Flow node needs a non-empty string id");
      }
      if (nodeIds.has(node.id)) fail(`Duplicate React Flow node id: ${node.id}`);
      nodeIds.add(node.id);
      if (!node.position || !Number.isFinite(node.position.x) || !Number.isFinite(node.position.y)) {
        fail(`React Flow node needs a numeric position: ${node.id}`);
      }
      if (node.data?.template !== undefined) {
        if (typeof node.data.template !== "string" || !node.data.template) {
          fail(`React Flow node template id must be a non-empty string: ${node.id}`);
        }
        nodeTemplate(node.data.template);
      }
      nodes.push(node);
    }

    const edgeIds = new Set();
    for (const edge of config.edges || []) {
      if (!edge || typeof edge !== "object" || typeof edge.id !== "string" || !edge.id) {
        fail("Every React Flow edge needs a non-empty string id");
      }
      if (edgeIds.has(edge.id)) fail(`Duplicate React Flow edge id: ${edge.id}`);
      edgeIds.add(edge.id);
      if (!nodeIds.has(edge.source) || !nodeIds.has(edge.target)) {
        fail(`React Flow edge points to an unknown node: ${edge.id}`);
      }
    }
    return { ...config, nodes };
  }

  function HtmlNode({ id, data = {} }) {
    const contentRef = React.useRef(null);
    const updateNodeInternals = useUpdateNodeInternals();
    const handles = Array.isArray(data.handles) && data.handles.length
      ? data.handles
      : [
          { id: "in", type: "target", position: "Left" },
          { id: "out", type: "source", position: "Right" },
        ];

    React.useLayoutEffect(() => {
      const content = contentRef.current;
      if (!content || !data.template) return;
      content.replaceChildren(nodeTemplate(data.template).content.cloneNode(true));
    }, [data.template]);

    React.useEffect(() => {
      const content = contentRef.current;
      if (!content) return undefined;

      let frame = 0;
      const refresh = () => {
        cancelAnimationFrame(frame);
        frame = requestAnimationFrame(() => updateNodeInternals(id));
      };
      const resizeObserver = typeof ResizeObserver === "undefined"
        ? null
        : new ResizeObserver(refresh);
      resizeObserver?.observe(content);
      content.addEventListener("toggle", refresh, true);
      content.addEventListener("transitionend", refresh, true);

      return () => {
        cancelAnimationFrame(frame);
        resizeObserver?.disconnect();
        content.removeEventListener("toggle", refresh, true);
        content.removeEventListener("transitionend", refresh, true);
      };
    }, [id, updateNodeInternals]);

    const body = h(
      "div",
      { className: "rf-node-content nodrag nopan nowheel", ref: contentRef },
      data.template ? null : data.label || id,
    );
    const kind = typeof data.kind === "string"
      ? data.kind.replace(/[^a-zA-Z0-9_-]/g, "")
      : "";

    return h(
      "div",
      { className: `rf-html-node${kind ? ` rf-html-node--${kind}` : ""}` },
      ...handles.map((handle) => h(Handle, {
        id: handle.id,
        key: `${handle.type}:${handle.id || handle.position}`,
        position: positionFor(
          handle.position,
          handle.type === "target" ? Position.Left : Position.Right,
        ),
        type: handle.type === "target" ? "target" : "source",
      })),
      body,
    );
  }

  function DataFlowEdge({
    id,
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition,
    targetPosition,
    markerEnd,
    style,
    data = {},
    label,
  }) {
    const [edgePath, labelX, labelY] = getSmoothStepPath({
      sourceX,
      sourceY,
      targetX,
      targetY,
      sourcePosition,
      targetPosition,
      borderRadius: finiteNumber(data.borderRadius, 18),
      offset: finiteNumber(data.offset, 24),
    });
    const reducedMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    const particle = reducedMotion || data.animate === false
      ? null
      : h(
          "circle",
          {
            "aria-hidden": "true",
            className: "rf-flow-particle",
            r: finiteNumber(data.particleRadius, 4),
          },
          h("animateMotion", {
            dur: `${finiteNumber(data.duration, 2.4)}s`,
            path: edgePath,
            repeatCount: "indefinite",
          }),
        );
    const edgeLabel = label
      ? h(
          EdgeLabelRenderer,
          null,
          h(
            "span",
            {
              className: "rf-edge-label nodrag nopan",
              style: {
                transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,
              },
            },
            label,
          ),
        )
      : null;

    return h(
      React.Fragment,
      null,
      h(BaseEdge, {
        className: "rf-data-edge-path",
        id,
        markerEnd,
        path: edgePath,
        style,
      }),
      particle,
      edgeLabel,
    );
  }

  const nodeTypes = Object.freeze({ html: HtmlNode });
  const edgeTypes = Object.freeze({ dataFlow: DataFlowEdge });

  function readConfig(host) {
    const configId = host.getAttribute("data-react-flow");
    if (!configId) fail("data-react-flow must name an application/json script id");
    const source = document.getElementById(configId);
    if (!(source instanceof HTMLScriptElement) || source.type !== "application/json") {
      fail(`React Flow JSON config not found: ${configId}`);
    }
    return validateConfig(JSON.parse(source.textContent || "{}"));
  }

  function FlowCanvas({ config, host }) {
    const options = config.options || {};
    const reducedMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches === true;
    const narrowViewport = window.matchMedia?.("(max-width: 42rem)").matches === true;
    const [motionPaused, setMotionPaused] = React.useState(false);
    const nodes = React.useMemo(() => config.nodes.map((node) => ({
      ...node,
      type: node.type || "html",
    })), [config]);
    const edges = React.useMemo(() => (config.edges || []).map((edge) => ({
      ...edge,
      type: edge.type || "dataFlow",
    })), [config]);
    const hasMotion = edges.some((edge) => edge.type === "dataFlow" && edge.data?.animate !== false);

    React.useEffect(() => {
      const edgeLayer = host.querySelector(".react-flow__edges");
      const svg = edgeLayer?.tagName.toLowerCase() === "svg"
        ? edgeLayer
        : edgeLayer?.ownerSVGElement || edgeLayer?.querySelector("svg");
      const method = motionPaused ? "pauseAnimations" : "unpauseAnimations";
      svg?.[method]?.();
    }, [host, motionPaused]);

    return h(
      ReactFlow,
      {
        defaultEdges: edges,
        defaultNodes: nodes,
        defaultViewport: options.defaultViewport || (
          narrowViewport ? { x: 16, y: 72, zoom: 0.88 } : undefined
        ),
        edgeTypes,
        fitView: options.fitView !== false && (
          !narrowViewport || options.fitViewOnMobile === true
        ),
        fitViewOptions: options.fitViewOptions || { padding: 0.16 },
        maxZoom: finiteNumber(options.maxZoom, 1.6),
        minZoom: finiteNumber(options.minZoom, 0.15),
        nodeTypes,
        nodesConnectable: options.nodesConnectable === true,
        nodesDraggable: options.nodesDraggable === true,
        onInit: () => {
          host.dataset.reactFlowReady = "true";
          host.removeAttribute("data-react-flow-loading");
          host.dispatchEvent(new CustomEvent("html-react-flow:ready"));
        },
        panOnScroll: options.panOnScroll === true,
        proOptions: { hideAttribution: true },
      },
      options.background === false
        ? null
        : h(Background, {
            gap: finiteNumber(options.gridGap, 24),
            size: finiteNumber(options.gridDot, 1),
          }),
      options.controls === false ? null : h(Controls),
      hasMotion && !reducedMotion
        ? h(
            Panel,
            { className: "rf-motion-panel nodrag nopan", position: "top-right" },
            h(
              "button",
              {
                "aria-pressed": motionPaused ? "true" : "false",
                className: "rf-motion-toggle nodrag nopan",
                onClick: () => setMotionPaused((paused) => !paused),
                type: "button",
              },
              motionPaused ? "Play data flow" : "Pause data flow",
            ),
          )
        : null,
    );
  }

  function renderError(host, error) {
    host.dataset.reactFlowError = "true";
    host.removeAttribute("data-react-flow-loading");
    host.replaceChildren();
    const message = document.createElement("p");
    message.className = "rf-load-error";
    message.textContent = `React Flow: ${error.message}`;
    host.append(message);
    console.error(error);
  }

  function mount(host) {
    if (!(host instanceof HTMLElement)) fail("React Flow host must be an HTML element");
    if (mounted.has(host)) return mounted.get(host);

    try {
      const config = readConfig(host);
      const bounds = host.getBoundingClientRect();
      if (bounds.width <= 0 || bounds.height <= 0) {
        host.style.minBlockSize ||= "var(--react-flow-fallback-block-size, 28rem)";
      }
      host.dataset.reactFlowLoading = "true";
      const root = createRoot(host, { onUncaughtError: (error) => renderError(host, error) });
      mounted.set(host, root);
      root.render(h(FlowCanvas, { config, host }));
      return root;
    } catch (error) {
      renderError(host, error);
      return null;
    }
  }

  function hostsIn(root) {
    const hosts = root instanceof HTMLElement && root.matches("[data-react-flow]")
      ? [root]
      : [];
    return hosts.concat([...root.querySelectorAll("[data-react-flow]")]);
  }

  function mountAll(root = document) {
    return hostsIn(root).map(mount).filter(Boolean);
  }

  window.HTMLReactFlow = Object.freeze({ mount, mountAll, version: API_VERSION });
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => mountAll(), { once: true });
  } else {
    mountAll();
  }
})();
