import React from "react";

export function CurrentPageSection({
  title,
  direction,
  directionEnabled = true,
  onDirectionChange,
  onApplyLayout,
  onExportPng
}) {
  return (
    <section className="sidebar__current" aria-label="Текущая страница">
      <div className="sidebar__group-title">Текущая страница</div>
      <h2 className="sidebar__page-title">{title}</h2>

      <div className="sidebar__row">
        <span className="sidebar__row-label">Направление</span>
        {directionEnabled ? (
          <div className="sidebar__row-buttons">
            <button
              type="button"
              className={direction === "DOWN" ? "is-active" : ""}
              onClick={() => onDirectionChange("DOWN")}
              aria-label="Сверху вниз"
            >
              ↓
            </button>
            <button
              type="button"
              className={direction === "RIGHT" ? "is-active" : ""}
              onClick={() => onDirectionChange("RIGHT")}
              aria-label="Слева направо"
            >
              →
            </button>
            <button
              type="button"
              className={direction === "UP" ? "is-active" : ""}
              onClick={() => onDirectionChange("UP")}
              aria-label="Снизу вверх"
            >
              ↑
            </button>
            <button
              type="button"
              className={direction === "LEFT" ? "is-active" : ""}
              onClick={() => onDirectionChange("LEFT")}
              aria-label="Справа налево"
            >
              ←
            </button>
          </div>
        ) : (
          <span className="sidebar__row-note">не используется</span>
        )}
      </div>

      <button type="button" className="sidebar__primary" onClick={onApplyLayout}>
        Применить ELK
      </button>

      <button type="button" className="sidebar__secondary" onClick={onExportPng}>
        Скачать PNG
      </button>
    </section>
  );
}
