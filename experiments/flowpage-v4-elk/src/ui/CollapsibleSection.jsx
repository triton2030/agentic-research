import React, { useState } from "react";

export function CollapsibleSection({ title, defaultOpen = true, children }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <section className={`collapsible ${open ? "is-open" : "is-closed"}`}>
      <div className="collapsible__head">
        <button
          type="button"
          className="collapsible__toggle"
          onClick={() => setOpen((o) => !o)}
          aria-expanded={open}
        >
          <span className="collapsible__chevron" aria-hidden="true">{open ? "▾" : "▸"}</span>
          <span className="collapsible__title">{title}</span>
        </button>
      </div>
      {open ? <div className="collapsible__body">{children}</div> : null}
    </section>
  );
}
