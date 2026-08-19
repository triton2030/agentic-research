---
description: "Built-in evidence and diagnostics active agent-browser 0.34.0."
---

# agent-browser: Diagnostics

Момент: для browser claim выбирается вид evidence. Сверено 2026-08-19 с active
`agent-browser 0.34.0`; точные options быстрее всего меняются в top-level help.

## Дельта

| Claim | Встроенный route вместо helper-а |
|---|---|
| accessibility/WCAG | `a11y [url] --json` |
| Core Web Vitals и hydration | `vitals [url] --json` |
| React tree, state, rerenders, Suspense | `react tree|inspect|renders|suspense` после `open --enable react-devtools` |
| structural/visual regression | `diff snapshot`, `diff screenshot --baseline`, `diff url` |
| network trace | `network har start|stop` |
| browser performance/debug | `trace`, `profiler`, `record` |

Канонический владелец exact syntax:

```bash
agent-browser --help
agent-browser skills get core --full
```
