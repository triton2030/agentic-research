// Что такое хуки в Claude Code и какую проблему они решают.
// Граф начинается с проблемы, потом показывает механизм и типы хуков,
// заканчивается эффектом — почему это работает.

export default {
  id: "hooks-system",
  title: "Хуки — зачем",
  description: "Проблема дисциплины LLM → runtime gates в settings.json → надёжность",
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
      title: "SessionStart",
      kicker: "загрузка контракта",
      body: "В начале сессии хук инжектит подсказку: «открой 1start-here, прочти карту скилов, mandatory cases». Модель не может пропустить — текст уже в первом сообщении системы.",
      bullets: ["context injection", "first-turn contract"]
    },
    {
      id: "userPromptSubmit",
      kind: "gate",
      weight: 2,
      title: "UserPromptSubmit",
      kicker: "intent guard",
      body: "Перед обработкой каждого user-запроса хук добавляет напоминание: «сначала фразой назови что услышал». Это перехватывает paraphrase theater до того как ответ начнёт формироваться.",
      bullets: ["per-turn reminder", "intent capture"]
    },
    {
      id: "preToolUse",
      kind: "gate",
      weight: 2,
      title: "PreToolUse",
      kicker: "ground-check",
      body: "Перед substantive Edit/Write хук может проверить что applicable criteria прочитан, заблокировать запись если нет, или инжектить путь к нужному файлу.",
      bullets: ["write-gate validation", "criteria gate"]
    },
    {
      id: "stop",
      kind: "gate",
      weight: 2,
      title: "Stop hook",
      kicker: "финальная проверка",
      body: "На завершении turn'а хук проверяет вывод модели: есть ли маркер «1work-review: да» после file-changes, есть ли verbatim-цитата из anchor-docs, есть ли «1user-truth: да» при правке criteria.",
      bullets: ["output validation", "marker enforcement"]
    },
    {
      id: "markers",
      kind: "review",
      weight: 2,
      title: "Маркеры в выводе",
      kicker: "verifiable compliance",
      body: "Хуки требуют конкретных строк в финале ответа. Маркер — это контракт между моделью и runtime: «я сделал X, вот доказательство». Без маркера turn не закрывается.",
      bullets: ["1work-review: да", "verbatim quote", "1user-truth: да"]
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
    ["sessionStart", "effect", "контракт загружен"],
    ["userPromptSubmit", "effect", "intent зафиксирован"],
    ["preToolUse", "effect", "правка обоснована"],
    ["markers", "effect", "compliance доказана"]
  ]
};
