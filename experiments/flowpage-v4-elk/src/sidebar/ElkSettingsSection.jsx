import React from "react";
import { SLIDER_DEFS, SELECT_DEFS, settingAppliesTo } from "../elk-layout";

export function ElkSettingsSection({ opts, onChange, onReset }) {
  const algorithm = opts.algorithm ?? "layered";
  const visibleSliders = SLIDER_DEFS.filter((s) => settingAppliesTo(s, algorithm));
  const visibleSelects = SELECT_DEFS.filter((s) => settingAppliesTo(s, algorithm));

  return (
    <div className="sidebar__settings">
      <div className="sidebar__settings-head">
        <p className="sidebar__hint">
          Пресет инструмента. Показаны только опции, которые выбранный алгоритм поддерживает.
        </p>
        <button
          type="button"
          className="sidebar__reset"
          onClick={onReset}
          title="сбросить к default"
        >
          Сбросить пресет
        </button>
      </div>

      {visibleSliders.map((s) => (
        <label key={s.key} title={s.hint}>
          <span className="sidebar__slider-label">{s.label}</span>
          <span className="sidebar__slider-value">
            {typeof opts[s.key] === "number" && s.step < 1
              ? Number(opts[s.key]).toFixed(2)
              : opts[s.key]}
          </span>
          <input
            type="range"
            min={s.min}
            max={s.max}
            step={s.step}
            value={opts[s.key]}
            onChange={(e) => onChange(s.key, Number(e.target.value))}
          />
        </label>
      ))}

      {visibleSelects.map((s) => (
        <label key={s.key} className="sidebar__select-label" title={s.hint}>
          <span className="sidebar__slider-label">{s.label}</span>
          <select
            value={opts[s.key]}
            onChange={(e) => onChange(s.key, e.target.value)}
          >
            {s.options.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </label>
      ))}
    </div>
  );
}
