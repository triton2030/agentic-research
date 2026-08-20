(() => {
  "use strict";

  const isRecord = (value) =>
    Boolean(value) && typeof value === "object" && !Array.isArray(value);

  const firstCustomProperty = (elements, names) => {
    for (const element of elements) {
      if (!element) continue;
      const style = getComputedStyle(element);
      for (const name of names) {
        const value = style.getPropertyValue(name).trim();
        if (value) return value;
      }
    }
    return "";
  };

  const computedValue = (elements, property) => {
    for (const element of elements) {
      if (!element) continue;
      const value = getComputedStyle(element)[property]?.trim();
      if (value && value !== "transparent" && value !== "rgba(0, 0, 0, 0)") {
        return value;
      }
    }
    return "";
  };

  const systemColor = (keyword, property) => {
    const probe = document.createElement("span");
    probe.style[property] = keyword;
    probe.style.position = "fixed";
    probe.style.visibility = "hidden";
    document.body.append(probe);
    const value = getComputedStyle(probe)[property];
    probe.remove();
    return value;
  };

  const legacyRgb = (value, host) => {
    const probe = document.createElement("span");
    probe.style.color = value;
    probe.style.position = "fixed";
    probe.style.visibility = "hidden";
    host.append(probe);
    const resolved = getComputedStyle(probe).color;
    probe.remove();

    const canvas = document.createElement("canvas");
    canvas.width = 1;
    canvas.height = 1;
    const context = canvas.getContext("2d", { willReadFrequently: true });
    context.clearRect(0, 0, 1, 1);
    context.fillStyle = resolved;
    context.fillRect(0, 0, 1, 1);
    const [red, green, blue, alpha] = context.getImageData(0, 0, 1, 1).data;
    return alpha === 255
      ? `rgb(${red}, ${green}, ${blue})`
      : `rgba(${red}, ${green}, ${blue}, ${alpha / 255})`;
  };

  const inheritedTheme = (host) => {
    const sources = [
      host,
      host?.closest("[data-theme]"),
      document.body,
      document.documentElement,
    ];
    const fontFamily = computedValue([
      host?.closest("[data-diagram-viewer]"),
      host?.parentElement,
      document.body,
      document.documentElement,
    ], "fontFamily");
    const inkValue =
      firstCustomProperty(sources, ["--color-base-content"]) ||
      computedValue(sources, "color") ||
      systemColor("CanvasText", "color");
    const paperValue =
      firstCustomProperty(sources, ["--color-base-100"]) ||
      computedValue(sources, "backgroundColor") ||
      systemColor("Canvas", "backgroundColor");
    const surfaceValue =
      firstCustomProperty(sources, ["--color-base-200"]) || paperValue;
    const lineValue = `color-mix(in srgb, ${inkValue} 25%, ${paperValue})`;
    const accentValue =
      firstCustomProperty(sources, ["--color-primary-content"]) || lineValue;
    const ink = legacyRgb(inkValue, host);
    const paper = legacyRgb(paperValue, host);
    const surface = legacyRgb(surfaceValue, host);
    const line = legacyRgb(lineValue, host);
    const accent = legacyRgb(accentValue, host);

    return {
      fontFamily,
      themeVariables: {
        background: paper,
        primaryColor: surface,
        primaryTextColor: ink,
        primaryBorderColor: line,
        lineColor: accent,
        secondaryColor: paper,
        secondaryTextColor: ink,
        secondaryBorderColor: line,
        tertiaryColor: surface,
        tertiaryTextColor: ink,
        tertiaryBorderColor: line,
        textColor: ink,
        titleColor: ink,
        edgeLabelBackground: paper,
        clusterBkg: paper,
        clusterBorder: line,
        noteBkgColor: surface,
        noteTextColor: ink,
        noteBorderColor: line,
        actorBkg: surface,
        actorBorder: line,
        actorTextColor: ink,
        signalColor: accent,
        signalTextColor: ink,
        labelBoxBkgColor: paper,
        labelBoxBorderColor: line,
        labelTextColor: ink,
        loopTextColor: ink,
        activationBkgColor: surface,
        activationBorderColor: line,
        sequenceNumberColor: paper,
        fontFamily,
        git0: surface,
        git1: paper,
        git2: surface,
        git3: paper,
        gitBranchLabel0: ink,
        gitBranchLabel1: ink,
        gitBranchLabel2: ink,
        gitBranchLabel3: ink,
        pieTitleTextColor: ink,
        pieSectionTextColor: ink,
        pieLegendTextColor: ink,
        pieStrokeColor: line,
      },
    };
  };

  const configuration = (host) => {
    const inherited = inheritedTheme(host);
    const authored = isRecord(window.HTMLMermaidConfig) ? window.HTMLMermaidConfig : {};
    const behavior = Object.fromEntries(
      Object.entries(authored).filter(
        ([key]) => !["fontFamily", "theme", "themeCSS", "themeVariables"].includes(key),
      ),
    );

    return {
      ...behavior,
      secure: [
        "secure",
        "securityLevel",
        "startOnLoad",
        "maxTextSize",
        "suppressErrorRendering",
        "maxEdges",
        "theme",
        "themeCSS",
        "themeVariables",
        "fontFamily",
      ],
      startOnLoad: false,
      securityLevel: "strict",
      theme: "base",
      fontFamily: inherited.fontFamily,
      themeVariables: inherited.themeVariables,
    };
  };

  const markError = (element, source, phase) => {
    element.replaceChildren(document.createTextNode(source));
    element.removeAttribute("data-processed");
    element.dataset.mermaidError = phase;
  };

  const renderOne = async (element) => {
    const source = element.textContent;
    element.removeAttribute("data-mermaid-error");

    try {
      await window.mermaid.parse(source);
    } catch (_error) {
      markError(element, source, "parse");
      return false;
    }

    try {
      await window.mermaid.run({ nodes: [element], suppressErrors: true });
      if (element.querySelector("svg")) return true;
      markError(element, source, "render");
      return false;
    } catch (_error) {
      await new Promise((resolve) => requestAnimationFrame(resolve));
      if (element.querySelector("svg")) {
        element.removeAttribute("data-mermaid-error");
        return true;
      }
      markError(element, source, "render");
      return false;
    }
  };

  const prepare = (host) => {
    try {
      const elkLayouts = window.MermaidElkLayouts?.default;
      if (elkLayouts && typeof window.mermaid.registerLayoutLoaders === "function") {
        window.mermaid.registerLayoutLoaders(elkLayouts);
      }
      window.mermaid.initialize(configuration(host));
      return true;
    } catch (_error) {
      return false;
    }
  };

  const render = async (diagrams) => {
    for (const diagram of diagrams) {
      await renderOne(diagram);
    }
    try {
      window.HTMLDiagramViewer?.initAll(document);
    } catch (_error) {
      // The diagram remains readable when optional pan/zoom setup fails.
    }
  };

  if (!window.mermaid) return;
  const diagrams = Array.from(document.querySelectorAll(".mermaid"));
  if (!diagrams.length) return;

  if (!prepare(diagrams[0])) {
    for (const diagram of diagrams) markError(diagram, diagram.textContent, "render");
    return;
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => void render(diagrams), { once: true });
  } else {
    void render(diagrams);
  }
})();
