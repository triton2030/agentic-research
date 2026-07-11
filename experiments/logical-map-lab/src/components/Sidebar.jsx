import { GitBranch, Layers3, Moon, PanelLeftClose, PanelLeftOpen, Route, ShieldQuestion, Sun } from "lucide-react";
import { ElkSettings } from "./ElkSettings.jsx";

export function Sidebar({
  activeMap,
  activeMapId,
  maps,
  theme,
  collapsed,
  focusPath,
  layoutOptions,
  onMapChange,
  onLayoutOptionChange,
  onResetLayoutOptions,
  onToggleTheme,
  onToggleSidebar,
  onToggleFocusPath,
  onCollapseAll,
  onRelayout
}) {
  const isDarkTheme = theme === "dark";
  const themeLabel = isDarkTheme ? "Включить дневную тему" : "Включить ночную тему";

  if (collapsed) {
    return (
      <aside className="sidebar sidebar--collapsed" aria-label="Левое меню">
        <div className="sidebar-rail">
          <button type="button" className="icon-button" onClick={onToggleSidebar} aria-label="Показать левое меню" title="Показать левое меню">
            <PanelLeftOpen aria-hidden="true" size={18} />
          </button>
          <button type="button" className="icon-button" onClick={onToggleTheme} aria-label={themeLabel} title={themeLabel}>
            {isDarkTheme ? <Sun aria-hidden="true" size={18} /> : <Moon aria-hidden="true" size={18} />}
          </button>
        </div>
      </aside>
    );
  }

  return (
    <aside className="sidebar" aria-label="Левое меню">
      <div className="sidebar__brand">
        <GitBranch aria-hidden="true" size={22} />
        <div>
          <h1>Logic Map Lab</h1>
          <p>Многостраничные карты причинных связей</p>
        </div>
        <div className="sidebar__controls">
          <button type="button" className="icon-button" onClick={onToggleTheme} aria-label={themeLabel} title={themeLabel}>
            {isDarkTheme ? <Sun aria-hidden="true" size={17} /> : <Moon aria-hidden="true" size={17} />}
          </button>
          <button type="button" className="icon-button" onClick={onToggleSidebar} aria-label="Скрыть левое меню" title="Скрыть левое меню">
            <PanelLeftClose aria-hidden="true" size={17} />
          </button>
        </div>
      </div>

      <section className="sidebar__section">
        <h2>Страница</h2>
        <label className="setting-row setting-row--select page-select">
          <span>Карта</span>
          <select value={activeMapId} onChange={(event) => onMapChange(event.target.value)}>
            {maps.map((map) => (
              <option key={map.id} value={map.id}>
                {map.title}
              </option>
            ))}
          </select>
        </label>
      </section>

      <section className="sidebar__section">
        <h2>Действия</h2>
        <div className="action-stack">
          <button type="button" className={focusPath ? "is-active" : ""} onClick={onToggleFocusPath}>
            <Route aria-hidden="true" size={16} />
            <span>{focusPath ? "Показать всё" : "Показать главную цепочку"}</span>
          </button>
          <button type="button" onClick={onRelayout}>
            <Layers3 aria-hidden="true" size={16} />
            <span>Применить ELK</span>
          </button>
          <button type="button" onClick={onCollapseAll}>
            <ShieldQuestion aria-hidden="true" size={16} />
            <span>Сбросить связь</span>
          </button>
        </div>
      </section>

      <ElkSettings options={layoutOptions} onChange={onLayoutOptionChange} onReset={onResetLayoutOptions} />

      <section className="sidebar__section">
        <h2>Типы нод</h2>
        <div className="legend">
          {Object.entries(activeMap.nodeTypes).map(([key, type]) => (
            <div className="legend__item" key={key}>
              <span style={{ background: type.color }} />
              <strong>{type.label}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="sidebar__section">
        <h2>Типы связей</h2>
        <div className="edge-legend">
          {Object.entries(activeMap.edgeTypes).map(([key, edge]) => (
            <div className="edge-legend__item" key={key}>
              <span style={{ borderColor: edge.color }} />
              <strong>{edge.label}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="sidebar__note">
        <h2>Формат</h2>
        <p>Карты лежат в src/maps/pages/*.json. Агент пишет title, связи, короткий label, полное why и quotes; React Flow только рендерит.</p>
      </section>
    </aside>
  );
}
