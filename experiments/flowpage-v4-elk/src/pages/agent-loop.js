// Каноническая цепочка из 1start-here. Узлы — обязательные точки маршрута,
// рёбра — реальные передачи смысла, не контекстная рамка.

export default {
  id: "agent-loop",
  title: "Agent loop",
  description: "Запрос → правда → почва → правка → проверка",
  nodes: [
    {
      id: "request",
      kind: "origin",
      weight: 3,
      title: "Запрос",
      kicker: "intent",
      body: "Пользователь формулирует желание обычным языком. Агент сначала восстанавливает смысл, а не бежит по первому техническому маршруту.",
      bullets: ["цель", "риски", "один следующий шаг"]
    },
    {
      id: "userTruth",
      kind: "truth",
      weight: 2,
      title: "1user-truth",
      kicker: "durable signal",
      body: "Ловит «хочу / не люблю / всегда / никогда / make this default» и переводит сигнал в durable правило в criteria.",
      bullets: ["red line", "taste", "criteria writer"]
    },
    {
      id: "strategy",
      kind: "branch",
      weight: 2,
      title: "1strategy",
      kicker: "hidden branch",
      body: "Срабатывает на raw desire, сомнение, развилку, «что выбрать». Раскрывает 2-3 варианта через экспертную линзу до того, как scope замёрзнет.",
      bullets: ["raw desire", "approach options", "fresh-session"]
    },
    {
      id: "criteria",
      kind: "memory",
      weight: 3,
      title: "_ops/criteria",
      kicker: "durable rules",
      body: "Критерии приёмки по сфере работы. Их пишет 1user-truth, читают гейты и review.",
      bullets: ["user-backed", "read at gates", "verified at review"]
    },
    {
      id: "router",
      kind: "skill",
      weight: 2,
      title: "1start-here",
      kicker: "orientation",
      body: "Карта скилов, mandatory cases, runtime delegate. Помогает выбрать один маршрут под форму запроса.",
      bullets: ["orient", "choose one", "no preload"]
    },
    {
      id: "beforeWork",
      kind: "gate",
      weight: 2,
      title: "1before-work",
      kicker: "почва и запись",
      body: "Anchor-check перед нетривиальным execution и Write Gate перед substantive Edit/Write.",
      bullets: ["blocker", "criteria", "owner check"]
    },
    {
      id: "active",
      kind: "skill",
      weight: 3,
      title: "Активный скилл",
      kicker: "рабочий слой",
      body: "Ведёт конкретный тип работы: instruction layer, task scope, roadmap, skill-architect, cli-tools — что уместно. Один за раз.",
      bullets: ["owner", "stop rule", "verification"]
    },
    {
      id: "artifact",
      kind: "output",
      weight: 3,
      title: "Артефакт",
      kicker: "результат",
      body: "Заметка, граф, скрипт, страница, criterion, instruction. Любая поверхность куда уходит работа.",
      bullets: ["readable", "owned", "verifiable"]
    },
    {
      id: "review",
      kind: "review",
      weight: 2,
      title: "1work-review",
      kicker: "закрытие",
      body: "Сравнивает diff/артефакт с goal, applicable criteria, agent instructions и evidence.",
      bullets: ["diff", "evidence", "residual risk"]
    }
  ],
  edges: [
    ["request", "userTruth", "durable signal?"],
    ["request", "strategy", "hidden branch?"],
    ["request", "router", "выбрать маршрут"],
    ["strategy", "userTruth", "durable → правда"],
    ["userTruth", "criteria", "write rule"],
    ["router", "beforeWork", "anchor check"],
    ["criteria", "beforeWork", "ground-check"],
    ["beforeWork", "active", "если почва ок"],
    ["active", "beforeWork", "перед правкой"],
    ["criteria", "beforeWork", "applicable rules"],
    ["beforeWork", "artifact", "создать / изменить"],
    ["artifact", "review", "проверить"],
    ["criteria", "review", "verify against rules"],
    ["review", "request", "новый цикл"]
  ]
};
