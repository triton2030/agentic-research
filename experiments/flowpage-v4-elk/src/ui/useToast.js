import { useCallback, useRef, useState } from "react";

// Один toast на экране. Каждый show() вытесняет предыдущий, чтобы окно не
// захламлялось. autoHideMs короткий — это статус-вспышка, не диалог.
// kind: "info" | "ok" | "error"
export function useToast(autoHideMs = 1600) {
  const [toasts, setToasts] = useState([]);
  const idRef = useRef(0);
  const timerRef = useRef(null);

  const dismiss = useCallback((id) => {
    setToasts((prev) => (id ? prev.filter((t) => t.id !== id) : []));
  }, []);

  const show = useCallback(
    (text, kind = "info") => {
      if (!text) return;
      const id = ++idRef.current;
      setToasts([{ id, text, kind }]);
      if (timerRef.current) clearTimeout(timerRef.current);
      const ms = kind === "error" ? Math.max(autoHideMs, 3500) : autoHideMs;
      if (ms > 0) {
        timerRef.current = setTimeout(() => {
          setToasts((prev) => prev.filter((t) => t.id !== id));
        }, ms);
      }
    },
    [autoHideMs]
  );

  return { toasts, show, dismiss };
}
