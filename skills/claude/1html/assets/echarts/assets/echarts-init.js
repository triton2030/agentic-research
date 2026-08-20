(() => {
  "use strict";

  const API_VERSION = "1.1.0";
  const existingApi = window.HTMLECharts;
  if (existingApi?.version === API_VERSION) {
    existingApi.mountAll();
    return;
  }

  const library = window.echarts;
  if (!library) {
    throw new Error("Apache ECharts must load before echarts-init.js");
  }

  const mounted = new WeakMap();
  const mountedHosts = new Set();
  const pending = new WeakMap();

  function fail(message) {
    throw new Error(message);
  }

  function cssToken(style, names, fallback) {
    for (const name of names) {
      const value = style.getPropertyValue(name).trim();
      if (value) return value;
    }
    return fallback;
  }

  function legacyRgb(host, value) {
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
  }

  function themeFrom(host) {
    const style = getComputedStyle(host);
    const inkValue = cssToken(
      style,
      ["--color-base-content"],
      style.color,
    );
    const paperValue = cssToken(
      style,
      ["--color-base-100"],
      "Canvas",
    );
    const ink = legacyRgb(host, inkValue);
    const line = legacyRgb(
      host,
      `color-mix(in srgb, ${inkValue} 25%, ${paperValue})`,
    );
    const fontFamily = style.fontFamily;
    const palette = [
      cssToken(style, ["--color-primary-content"], ""),
      cssToken(style, ["--color-secondary-content"], ""),
      cssToken(style, ["--color-accent-content"], ""),
    ].filter(Boolean).map((value) => legacyRgb(host, value));
    const textStyle = { color: ink, fontFamily };
    const axisTheme = () => ({
      axisLabel: { ...textStyle },
      axisLine: { lineStyle: { color: line } },
      nameTextStyle: { ...textStyle },
      splitLine: { lineStyle: { color: line } },
    });

    return {
      backgroundColor: "transparent",
      ...(palette.length ? { color: palette } : {}),
      textStyle,
      title: { subtextStyle: textStyle, textStyle },
      legend: { textStyle },
      categoryAxis: axisTheme(),
      valueAxis: axisTheme(),
      timeAxis: axisTheme(),
      logAxis: axisTheme(),
    };
  }

  function configFor(host) {
    const configId = host.dataset.echart;
    if (!configId) fail("ECharts host needs a non-empty data-echart config id");
    const config = document.getElementById(configId);
    if (!(config instanceof HTMLScriptElement) || config.type !== "application/json") {
      fail(`ECharts config must be a script[type=application/json]: ${configId}`);
    }

    let option;
    try {
      option = JSON.parse(config.textContent || "");
    } catch (error) {
      fail(`ECharts config is invalid JSON: ${configId} (${error.message})`);
    }
    if (!option || typeof option !== "object" || Array.isArray(option)) {
      fail(`ECharts option must be a JSON object: ${configId}`);
    }
    if (!Array.isArray(option.series) || !option.series.length) {
      fail(`ECharts option needs a non-empty series array: ${configId}`);
    }
    return option;
  }

  function resolvedOptionColors(host, option) {
    if (option.color === undefined) return option;
    if (!Array.isArray(option.color) || !option.color.length) {
      fail("ECharts option.color must be a non-empty array when provided");
    }
    return {
      ...option,
      color: option.color.map((value) => {
        if (typeof value !== "string" || !value.trim()) {
          fail("ECharts option.color values must be non-empty CSS color strings");
        }
        return legacyRgb(host, value);
      }),
    };
  }

  function labelledText(host) {
    const direct = host.getAttribute("aria-label")?.trim();
    if (direct) return direct;

    const labelledBy = host.getAttribute("aria-labelledby")?.trim();
    if (!labelledBy) return "";
    return labelledBy
      .split(/\s+/)
      .map((id) => document.getElementById(id)?.textContent?.trim() || "")
      .filter(Boolean)
      .join(". ");
  }

  function accessibleOption(host, option) {
    const authoredAria = option.aria && typeof option.aria === "object"
      ? option.aria
      : {};
    const authoredLabel = authoredAria.label && typeof authoredAria.label === "object"
      ? authoredAria.label
      : {};
    const description = authoredLabel.description
      || authoredAria.description
      || labelledText(host);
    if (!description) {
      fail("ECharts host needs aria-label/aria-labelledby or aria.label.description");
    }

    return {
      ...authoredAria,
      enabled: true,
      label: {
        ...authoredLabel,
        description,
        enabled: true,
      },
    };
  }

  function mount(host) {
    const existing = mounted.get(host);
    if (existing) return existing.chart;
    if (pending.has(host)) return null;

    try {
      const option = resolvedOptionColors(host, configFor(host));
      const bounds = host.getBoundingClientRect();
      if (bounds.width <= 0 || bounds.height <= 0) {
        host.style.minBlockSize ||= "var(--echart-fallback-block-size, 20rem)";
        host.dataset.echartPending = "size";
        if (typeof ResizeObserver === "undefined") {
          fail("ECharts deferred sizing needs ResizeObserver");
        }
        const observer = new ResizeObserver(() => {
          const nextBounds = host.getBoundingClientRect();
          if (nextBounds.width <= 0 || nextBounds.height <= 0) return;
          observer.disconnect();
          pending.delete(host);
          delete host.dataset.echartPending;
          mount(host);
        });
        pending.set(host, observer);
        observer.observe(host);
        return null;
      }

      const renderer = host.dataset.echartRenderer || "svg";
      if (renderer !== "svg" && renderer !== "canvas") {
        fail(`Unsupported ECharts renderer: ${renderer}`);
      }
      const motion = window.matchMedia?.("(prefers-reduced-motion: reduce)");
      const reducedMotion = Boolean(motion?.matches);
      const finalOption = {
        ...option,
        aria: accessibleOption(host, option),
        ...(reducedMotion ? { animation: false } : {}),
      };
      const chart = library.init(host, themeFrom(host), { renderer });
      chart.setOption(finalOption);

      const resizeObserver = typeof ResizeObserver === "undefined"
        ? null
        : new ResizeObserver(() => {
            if (host.clientWidth > 0 && host.clientHeight > 0) chart.resize();
          });
      resizeObserver?.observe(host);

      const onMotionChange = (event) => {
        chart.setOption({ animation: event.matches ? false : option.animation ?? true });
      };
      motion?.addEventListener?.("change", onMotionChange);

      const record = { chart, motion, onMotionChange, resizeObserver };
      mounted.set(host, record);
      mountedHosts.add(host);
      host.dataset.echartReady = "true";
      delete host.dataset.echartError;
      return chart;
    } catch (error) {
      host.dataset.echartError = error.message;
      console.error(error);
      return null;
    }
  }

  function mountAll(root = document) {
    return [...root.querySelectorAll("[data-echart]")].map(mount).filter(Boolean);
  }

  function resizeAll() {
    for (const host of mountedHosts) mounted.get(host)?.chart.resize();
  }

  function destroy(host) {
    pending.get(host)?.disconnect();
    pending.delete(host);
    delete host.dataset.echartPending;
    const record = mounted.get(host);
    if (!record) return;
    record.resizeObserver?.disconnect();
    record.motion?.removeEventListener?.("change", record.onMotionChange);
    record.chart.dispose();
    mounted.delete(host);
    mountedHosts.delete(host);
    delete host.dataset.echartReady;
  }

  window.HTMLECharts = {
    destroy,
    mount,
    mountAll,
    resizeAll,
    version: API_VERSION,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => mountAll(), { once: true });
  } else {
    mountAll();
  }
  window.addEventListener("pageshow", resizeAll);
})();
