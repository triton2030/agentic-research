import React from "react";

export function PagesSection({ pages, activeId, onSelect }) {
  return (
    <nav className="sidebar__nav" aria-label="Страницы">
      <div className="sidebar__group-title">Страницы</div>
      {pages.map((p) => (
        <button
          key={p.id}
          type="button"
          className={`sidebar__page ${p.id === activeId ? "is-active" : ""}`}
          onClick={() => onSelect(p.id)}
        >
          {p.title}
        </button>
      ))}
    </nav>
  );
}
