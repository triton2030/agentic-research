import React from "react";

export function ToastStack({ toasts, onDismiss }) {
  if (!toasts.length) return null;
  return (
    <div className="toast-stack" role="status" aria-live="polite">
      {toasts.map((t) => (
        <button
          key={t.id}
          type="button"
          className={`toast toast--${t.kind}`}
          onClick={() => onDismiss(t.id)}
        >
          {t.text}
        </button>
      ))}
    </div>
  );
}
