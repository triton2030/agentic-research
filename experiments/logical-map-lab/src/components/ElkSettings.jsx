import { RotateCcw } from "lucide-react";
import { SLIDER_DEFS, SELECT_DEFS } from "../graph/layout.js";

export function ElkSettings({ options, onChange, onReset }) {
  return (
    <section className="sidebar__section graph-settings">
      <div className="settings-head">
        <h2>Настройки графа</h2>
        <button type="button" onClick={onReset} title="Сбросить настройки графа">
          <RotateCcw aria-hidden="true" size={14} />
          <span>Сброс</span>
        </button>
      </div>
      <p className="settings-hint">Двигайте настройки, затем применяйте ELK. Масштаб viewport остаётся ручным.</p>

      <div className="settings-list">
        {SELECT_DEFS.map((setting) => (
          <label key={setting.key} title={setting.hint} className="setting-row setting-row--select">
            <span>{setting.label}</span>
            <select value={options[setting.key]} onChange={(event) => onChange(setting.key, event.target.value)}>
              {setting.options.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        ))}

        {SLIDER_DEFS.map((setting) => (
          <label key={setting.key} title={setting.hint} className="setting-row">
            <span>{setting.label}</span>
            <strong>{options[setting.key]}</strong>
            <input
              type="range"
              min={setting.min}
              max={setting.max}
              step={setting.step}
              value={options[setting.key]}
              onChange={(event) => onChange(setting.key, Number(event.target.value))}
            />
          </label>
        ))}
      </div>
    </section>
  );
}
