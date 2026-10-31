---
description: "Built-in evidence and diagnostics active agent-browser 0.38.1."
---

# agent-browser: Diagnostics

Момент: для browser claim выбирается вид evidence. Сверено 2026-09-24 с active
`agent-browser 0.38.1`; точные options быстрее всего меняются в top-level help.

## Дельта

| Claim | Встроенный route вместо helper-а |
|---|---|
| accessibility/WCAG | `a11y [url] --json` |
| Core Web Vitals и hydration | `vitals [url] --json` |
| React tree, state, rerenders, Suspense | `react tree|inspect|renders|suspense` после `open --enable react-devtools` |
| structural/visual regression | `diff snapshot`, `diff screenshot --baseline`, `diff url` |
| повторное чтение меняющейся страницы | `snapshot --delta`; `--full` обновляет полный baseline |
| повторный screenshot | `screenshot --if-changed`; `--threshold <0-1>` допускает малые отличия |
| network trace | `network har start|stop` |
| browser performance/debug | `trace`, `profiler`, `record` |

Канонический владелец exact syntax:

```bash
agent-browser --help
agent-browser skills get core --full
```

`--delta` сначала возвращает полный снимок, затем изменения или признак
неизменности. При `--if-changed` неизменный снимок не содержит пути к картинке.
Refs сохраняются для выживших DOM-элементов; навигация или замена элемента
делает старый ref недействительным.

Источник новшеств: [agent-browser 0.38.0](https://github.com/vercel-labs/agent-browser/releases/tag/v0.38.0),
сверено с локальной справкой 0.38.1.
