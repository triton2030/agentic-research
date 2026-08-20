(function (global) {
  "use strict";

  const viewers = new WeakMap();

  function toolbarMarkup() {
    return `
      <div class="join diagram-viewer__toolbar" role="toolbar" aria-label="Управление диаграммой">
        <button class="btn btn-xs join-item tooltip tooltip-bottom" type="button"
          data-tip="Уменьшить" data-diagram-action="zoom-out" aria-label="Уменьшить диаграмму">
          <i data-lucide="minus" class="size-4" aria-hidden="true"></i>
        </button>
        <span class="btn btn-xs join-item diagram-viewer__scale" data-diagram-zoom>100%</span>
        <button class="btn btn-xs join-item tooltip tooltip-bottom" type="button"
          data-tip="Увеличить" data-diagram-action="zoom-in" aria-label="Увеличить диаграмму">
          <i data-lucide="plus" class="size-4" aria-hidden="true"></i>
        </button>
        <button class="btn btn-xs join-item tooltip tooltip-bottom" type="button"
          data-tip="Вписать целиком" data-diagram-action="fit" aria-label="Вписать диаграмму целиком">
          <i data-lucide="scan" class="size-4" aria-hidden="true"></i>
        </button>
        <button class="btn btn-xs join-item tooltip tooltip-bottom" type="button"
          data-tip="Полный экран" data-diagram-action="fullscreen" aria-label="Открыть на весь экран">
          <i data-lucide="maximize-2" class="size-4" aria-hidden="true"></i>
        </button>
      </div>
    `;
  }

  function init(host) {
    if (!host || viewers.has(host)) return viewers.get(host);
    if (typeof global.Panzoom !== "function") return null;

    const canvas = host.querySelector("[data-diagram-canvas]") || host;
    const svg = canvas.querySelector("svg");
    if (!svg) return null;

    if (!host.querySelector("[data-diagram-action]")) {
      host.insertAdjacentHTML("afterbegin", toolbarMarkup());
      if (global.lucide) global.lucide.createIcons();
    }

    svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
    const panzoom = global.Panzoom(svg, {
      canvas: true,
      minScale: 1,
      maxScale: 6,
      step: 0.2,
      panOnlyWhenZoomed: true
    });

    const scaleLabel = host.querySelector("[data-diagram-zoom]");
    const updateScale = () => {
      if (scaleLabel) scaleLabel.textContent = `${Math.round(panzoom.getScale() * 100)}%`;
    };

    canvas.addEventListener("wheel", panzoom.zoomWithWheel, { passive: false });
    svg.addEventListener("panzoomchange", updateScale);

    host.addEventListener("click", (event) => {
      const control = event.target.closest("[data-diagram-action]");
      if (!control) return;

      const action = control.dataset.diagramAction;
      if (action === "zoom-in") panzoom.zoomIn();
      if (action === "zoom-out") panzoom.zoomOut();
      if (action === "fit") panzoom.reset();
      if (action === "fullscreen" && host.requestFullscreen) host.requestFullscreen();
    });

    document.addEventListener("fullscreenchange", () => {
      if (document.fullscreenElement === host || !document.fullscreenElement) {
        requestAnimationFrame(() => panzoom.reset({ animate: false }));
      }
    });

    host.dataset.diagramViewerReady = "true";
    updateScale();
    viewers.set(host, panzoom);
    return panzoom;
  }

  function initAll(root) {
    return Array.from((root || document).querySelectorAll("[data-diagram-viewer]"), init);
  }

  global.HTMLDiagramViewer = { init, initAll };
})(window);
