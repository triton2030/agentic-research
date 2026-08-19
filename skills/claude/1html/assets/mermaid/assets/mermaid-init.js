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

  const inheritedTheme = (host) => {
    const sources = [
      host,
      host?.closest("[data-theme]"),
      document.body,
      document.documentElement,
    ];
    const fontFamily = computedValue(sources, "fontFamily");
    const ink =
      firstCustomProperty(sources, ["--artifact-ink", "--color-base-content"]) ||
      computedValue(sources, "color") ||
      systemColor("CanvasText", "color");
    const paper =
      firstCustomProperty(sources, ["--artifact-paper", "--color-base-100"]) ||
      computedValue(sources, "backgroundColor") ||
      systemColor("Canvas", "backgroundColor");
    const surface =
      firstCustomProperty(sources, ["--artifact-surface", "--color-base-200"]) ||
      paper;
    const line =
      firstCustomProperty(sources, ["--artifact-line", "--color-base-300"]) ||
      ink;
    const accent =
      firstCustomProperty(sources, ["--artifact-accent", "--color-primary"]) ||
      line;
    const muted =
      firstCustomProperty(sources, ["--artifact-muted", "--color-neutral-content"]) ||
      ink;

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
        pieLegendTextColor: muted,
        pieStrokeColor: line,
      },
    };
  };

  const configuration = (host) => {
    const inherited = inheritedTheme(host);
    const authored = isRecord(window.HTMLMermaidConfig) ? window.HTMLMermaidConfig : {};
    const authoredTheme = isRecord(authored.themeVariables) ? authored.themeVariables : {};

    return {
      ...authored,
      startOnLoad: false,
      securityLevel: "strict",
      theme: authored.theme || "base",
      fontFamily: authored.fontFamily || inherited.fontFamily,
      themeVariables: {
        ...inherited.themeVariables,
        ...authoredTheme,
      },
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
      markError(element, source, "render");
      return false;
    }
  };

  const render = async () => {
    if (!window.mermaid) return;

    const diagrams = Array.from(document.querySelectorAll(".mermaid"));
    if (!diagrams.length) return;

    try {
      const elkLayouts = window.MermaidElkLayouts?.default;
      if (elkLayouts && typeof window.mermaid.registerLayoutLoaders === "function") {
        window.mermaid.registerLayoutLoaders(elkLayouts);
      }
      window.mermaid.initialize(configuration(diagrams[0]));
    } catch (_error) {
      for (const diagram of diagrams) {
        markError(diagram, diagram.textContent, "render");
      }
      return;
    }
    for (const diagram of diagrams) {
      await renderOne(diagram);
    }
    try {
      window.HTMLDiagramViewer?.initAll(document);
    } catch (_error) {
      // The diagram remains readable when optional pan/zoom setup fails.
    }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => void render(), { once: true });
  } else {
    void render();
  }
})();
