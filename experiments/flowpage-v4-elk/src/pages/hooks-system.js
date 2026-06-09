// Что такое хуки в Claude Code и какую проблему они решают.
// Граф начинается с проблемы, потом показывает механизм и типы хуков,
// заканчивается эффектом — почему это работает.

export default {
  id: "hooks-system",
  title: "Хуки — зачем",
  description: "Проблема дисциплины LLM → runtime reminders/gates → надёжность",
  nodes: [
    {
      id: "problem",
      kind: "origin",
      weight: 3,
      title: "Проблема",
      kicker: "что мы решаем",
      body: "LLM каждый ход начинает с нуля. Контракт сессии (правила, маркеры, чтения anchor-документов) живёт в инструкциях, но модель про них «забывает» под нагрузкой контекста.",
      bullets: ["context drift", "instruction decay", "selective compliance"]
    },
    {
      id: "mechanism",
      kind: "memory",
      weight: 3,
      title: "Хуки как механизм",
      kicker: "structural enforcement",
      body: "Хук — shell-команда, привязанная к событию runtime (start, prompt submit, before-tool, stop). Срабатывает всегда, не зависит от внимания модели. Может блокировать, инжектировать контекст или валидировать вывод.",
      bullets: ["событие → команда", "независимо от LLM", "всегда срабатывает"]
    },
    {
      id: "sessionStart",
      kind: "gate",
      weight: 2,
      title: "No live SessionStart",
      kicker: "не текущий runtime",
      body: "Стартовая дисциплина сейчас живёт в инструкциях и локальном context/owner pass. Не ссылаться на не wired SessionStart как на гарантию.",
      bullets: ["instructions", "context pass"]
    },
    {
      id: "userPromptSubmit",
      kind: "gate",
      weight: 2,
      title: "UserPromptSubmit",
      kicker: "intent guard",
      body: "В Codex live config это короткий context reminder. Это не auto-capture и не criteria writer; Claude settings сейчас не wired на UserPromptSubmit.",
      bullets: ["context reminder", "no auto-capture"]
    },
    {
      id: "preToolUse",
      kind: "gate",
      weight: 2,
      title: "PreToolUse",
      kicker: "ground-check",
      body: "Текущие live examples: Markdown graph reminder перед write и search reminder перед grep. Это reminder/guardrail, не старый criteria write-gate.",
      bullets: ["md graph", "search reminder"]
    },
    {
      id: "stop",
      kind: "gate",
      weight: 2,
      title: "Stop hook",
      kicker: "финальная проверка",
      body: "В Codex live config Stop делает Markdown graph rollup. Старые review/user-truth маркеры не являются текущим контрактом.",
      bullets: ["graph rollup", "no review markers"]
    },
    {
      id: "markers",
      kind: "review",
      weight: 2,
      title: "Evidence вместо маркеров",
      kicker: "verifiable closeout",
      body: "Финал доказывается changed/checked/risk и конкретными verifier outputs. Строковый маркер без проверки не считается evidence.",
      bullets: ["changed", "checked", "risk"]
    },
    {
      id: "effect",
      kind: "output",
      weight: 3,
      title: "Эффект",
      kicker: "результат",
      body: "Дисциплина перестаёт зависеть от вдохновения модели. Even «ленивая» сессия проходит через те же гейты, что и внимательная. Проект остаётся когерентным через 50+ сессий без накопления drift.",
      bullets: ["consistent across sessions", "drift-resistant", "verifiable"]
    }
  ],
  edges: [
    ["problem", "mechanism", "как чиним"],
    ["mechanism", "sessionStart", "тип: на старте"],
    ["mechanism", "userPromptSubmit", "тип: на запросе"],
    ["mechanism", "preToolUse", "тип: до правки"],
    ["mechanism", "stop", "тип: на финале"],
    ["stop", "markers", "что требует"],
    ["sessionStart", "effect", "не выдумывать hook"],
    ["userPromptSubmit", "effect", "context напомнен"],
    ["preToolUse", "effect", "правка обоснована"],
    ["markers", "effect", "compliance доказана"]
  ]
};
