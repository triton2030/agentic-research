// App owns only shell state and the currently visible ELK preset. Page/usePageLayout
// owns the graph snapshot file; the only preset -> geometry bridge is "Apply ELK".
import React, { useEffect, useRef, useState } from "react";
import { ReactFlowProvider } from "@xyflow/react";
import { toPng } from "html-to-image";
import { Page } from "./Page";
import { BUILTIN_PAGES } from "./pages";
import { DEFAULT_OPTIONS, supportsDirection } from "./elk-layout";
import { CollapsibleSection } from "./ui/CollapsibleSection";
import { ToastStack } from "./ui/Toast";
import { useToast } from "./ui/useToast";
import { PagesSection } from "./sidebar/PagesSection";
import { CurrentPageSection } from "./sidebar/CurrentPageSection";
import { ElkSettingsSection } from "./sidebar/ElkSettingsSection";
export function App() {
  const [activeId, setActiveId] = useState(BUILTIN_PAGES[0].id);
  const [opts, setOpts] = useState(DEFAULT_OPTIONS);
  const [direction, setDirection] = useState("DOWN");
  const pageRef = useRef(null);
  const { toasts, show, dismiss } = useToast(1600);
  const activePage = BUILTIN_PAGES.find((p) => p.id === activeId) ?? BUILTIN_PAGES[0];
  const directionEnabled = supportsDirection(opts.algorithm ?? DEFAULT_OPTIONS.algorithm);

  useEffect(() => {
    setOpts(DEFAULT_OPTIONS);
    setDirection("DOWN");
  }, [activeId]);

  function handlePresetLoaded({ options, direction: loadedDirection }) {
    setOpts(options ? { ...DEFAULT_OPTIONS, ...options } : DEFAULT_OPTIONS);
    setDirection(loadedDirection || "DOWN");
  }

  function updateOpt(key, value) {
    const next = { ...opts, [key]: value };
    setOpts(next);
    pageRef.current?.savePreset(next, direction);
  }

  function resetOpts() {
    setOpts(DEFAULT_OPTIONS);
    pageRef.current?.savePreset(DEFAULT_OPTIONS, direction);
  }

  function changeDirection(nextDirection) {
    setDirection(nextDirection);
    pageRef.current?.savePreset(opts, nextDirection);
  }

  async function exportPng() {
    const target = document.querySelector(".react-flow__viewport");
    if (!target) return;
    try {
      const dataUrl = await toPng(target, { backgroundColor: "#f6f0e4", pixelRatio: 2, cacheBust: true });
      const a = document.createElement("a");
      a.href = dataUrl;
      a.download = `${activePage.id}.png`;
      a.click();
    } catch (e) {
      console.error(e);
      show("экспорт не удался", "error");
    }
  }
  function handleStatus(text) {
    if (!text) return;
    const ok = /сохранен|загружена|применена|раскладка/i.test(text);
    show(text, /ошибка/i.test(text) ? "error" : ok ? "ok" : "info");
  }
  return (
    <div className="app">
      <aside className="sidebar">
        <header className="sidebar__head">
          <h1 className="sidebar__title">FlowPage v4</h1>
          <p className="sidebar__subtitle">ELK · snapshot · apply вручную</p>
        </header>
        <PagesSection pages={BUILTIN_PAGES} activeId={activeId} onSelect={setActiveId} />
        <CurrentPageSection title={activePage.title} direction={direction} directionEnabled={directionEnabled} onDirectionChange={changeDirection} onApplyLayout={() => pageRef.current?.applyLayout()} onExportPng={exportPng} />
        <CollapsibleSection title="ELK Preset" defaultOpen={false}>
          <ElkSettingsSection opts={opts} onChange={updateOpt} onReset={resetOpts} />
        </CollapsibleSection>
        <footer className="sidebar__footer">
          <div className="sidebar__footer-line">раскладка → <code>data/layouts/{activePage.id}.json</code></div>
          <div className="sidebar__footer-hint">геометрия и ELK-пресет живут в одном snapshot-файле.</div>
        </footer>
      </aside>
      <main className="canvas">
        <ReactFlowProvider key={activePage.id}>
          <Page
            ref={pageRef}
            page={activePage}
            opts={opts}
            direction={direction}
            onStatusChange={handleStatus}
            onPresetLoaded={handlePresetLoaded}
          />
        </ReactFlowProvider>
        <ToastStack toasts={toasts} onDismiss={dismiss} />
      </main>
    </div>
  );
}
