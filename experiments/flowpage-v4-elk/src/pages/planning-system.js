// Как README, PROJECT-ROADMAP и task-файлы связаны. Кто что владеет,
// куда течёт информация, где замыкается петля.

export default {
  id: "planning-system",
  title: "Система планирования",
  description: "README → roadmap → tasks → criteria → review (петля)",
  nodes: [
    {
      id: "userVision",
      kind: "origin",
      weight: 3,
      title: "Пользовательское видение",
      kicker: "direction",
      body: "Куда хочется двигаться. Не процесс, не задача, не план — а намерение. Всё планирование стартует отсюда.",
      bullets: ["raw direction", "long-term", "vision"]
    },
    {
      id: "strategySkill",
      kind: "branch",
      weight: 2,
      title: "1strategy",
      kicker: "vision keeper",
      body: "Owner-скил для README. Переводит видение в approach: что делаем, чего не делаем, какие развилки выбраны.",
      bullets: ["vision", "approach", "anti-goals"]
    },
    {
      id: "readme",
      kind: "doc",
      weight: 2,
      title: "README.md",
      kicker: "L1 public",
      body: "Публичная рамка проекта: зачем, как сейчас работать, что не делать. Onboarding-документ для нового человека и новой сессии.",
      bullets: ["vision", "motivation", "on-ramp"]
    },
    {
      id: "roadmapSkill",
      kind: "skill",
      weight: 2,
      title: "1roadmap",
      kicker: "stage keeper",
      body: "Owner-скил для PROJECT-ROADMAP. Превращает выбранный approach в цепочку стадий + текущую позицию.",
      bullets: ["Goal", "Stages", "position"]
    },
    {
      id: "roadmap",
      kind: "doc",
      weight: 3,
      title: "_ops/PROJECT-ROADMAP.md",
      kicker: "L1 trajectory",
      body: "Live-картина пути от нуля до готово. Goal + Stage chain + где мы сейчас. Динамическая — стадии меняются при сдвиге целей.",
      bullets: ["Goal", "current stage", "trajectory"]
    },
    {
      id: "tasksSkill",
      kind: "skill",
      weight: 2,
      title: "1tasks",
      kicker: "scope keeper",
      body: "Owner-скил для task-файлов внутри текущей стадии. Формирует scope, цитирует applicable criteria и agent instructions.",
      bullets: ["scope", "applicable criteria", "done state"]
    },
    {
      id: "taskFile",
      kind: "output",
      weight: 3,
      title: "task-MM-*.md",
      kicker: "L2 scope",
      body: "Конкретная задача внутри стадии: цель, подшаги, критерии приёмки, evidence. Цитирует прямые criteria и инструкции.",
      bullets: ["цель", "подшаги", "критерии"]
    },
    {
      id: "substeps",
      kind: "gate",
      weight: 1,
      title: "Подшаги",
      kicker: "L3",
      body: "Конкретные шаги внутри task-файла. Не самостоятельный артефакт — живут внутри своей задачи.",
      bullets: ["concrete", "verifiable"]
    },
    {
      id: "criteria",
      kind: "memory",
      weight: 2,
      title: "_ops/criteria",
      kicker: "rule layer",
      body: "Durable правила приёмки по сфере работы. Пишет 1user-truth по сигналу пользователя; читают tasks, гейты и review.",
      bullets: ["durable", "user-backed", "cross-task"]
    },
    {
      id: "review",
      kind: "review",
      weight: 2,
      title: "1work-review",
      kicker: "closeout",
      body: "Сверяет artifact с goal, criteria и agent-instructions. Поднимает stale-anchor сигналы обратно в roadmap и criteria.",
      bullets: ["evidence", "residual risk", "stale anchor"]
    }
  ],
  edges: [
    ["userVision", "strategySkill", "raw direction"],
    ["strategySkill", "readme", "пишет vision"],
    ["strategySkill", "roadmapSkill", "approach → stages"],
    ["roadmapSkill", "roadmap", "Goal + Stages"],
    ["roadmap", "tasksSkill", "стадия → задачи"],
    ["tasksSkill", "taskFile", "создаёт"],
    ["taskFile", "substeps", "L3 внутри"],
    ["criteria", "taskFile", "applicable rules"],
    ["taskFile", "review", "closeout"],
    ["review", "criteria", "durable learnings"],
    ["review", "roadmap", "status reconcile"]
  ]
};
