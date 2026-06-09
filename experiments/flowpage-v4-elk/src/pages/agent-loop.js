// Каноническая цепочка из локального context/owner pass. Узлы — обязательные точки маршрута,
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
      title: "Owner truth",
      kicker: "durable signal",
      body: "Ловит «хочу / не люблю / всегда / никогда / make this default» и передаёт сигнал правильному owner-у или memory layer по явной просьбе.",
      bullets: ["red line", "taste", "owner route"]
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
      title: "Owner rules",
      kicker: "durable checks",
      body: "Правила приёмки живут у владельца: AGENTS, GOAL, rule-doc, skill contract или memory layer. Их читают перед правкой и сверяют на closeout.",
      bullets: ["user-backed", "owned", "verified"]
    },
    {
      id: "router",
      kind: "gate",
      weight: 2,
      title: "Context pass",
      kicker: "orientation",
      body: "Локальные инструкции, owner-файлы и live skill contracts помогают выбрать один маршрут под форму запроса.",
      bullets: ["orient", "choose one", "live surface"]
    },
    {
      id: "beforeWork",
      kind: "gate",
      weight: 2,
      title: "Owner/write check",
      kicker: "почва и запись",
      body: "Проверка owner-а, применимых инструкций и graph/radius перед substantive Edit/Write.",
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
      body: "Заметка, граф, скрипт, страница или инструкция. Любая поверхность куда уходит работа.",
      bullets: ["readable", "owned", "verifiable"]
    },
    {
      id: "review",
      kind: "review",
      weight: 2,
      title: "Evidence-closeout",
      kicker: "закрытие",
      body: "Текущий execution owner сравнивает artifact с просьбой, owner-инструкциями и evidence.",
      bullets: ["diff", "evidence", "residual risk"]
    }
  ],
  edges: [
    ["request", "userTruth", "durable signal?"],
    ["request", "strategy", "hidden branch?"],
    ["request", "router", "выбрать маршрут"],
    ["strategy", "userTruth", "durable → owner"],
    ["userTruth", "criteria", "route rule"],
    ["router", "beforeWork", "anchor check"],
    ["criteria", "beforeWork", "ground-check"],
    ["beforeWork", "active", "если почва ок"],
    ["active", "beforeWork", "перед правкой"],
    ["criteria", "beforeWork", "applicable rules"],
    ["beforeWork", "artifact", "создать / изменить"],
    ["artifact", "review", "проверить"],
    ["criteria", "review", "verify against owner rules"],
    ["review", "request", "новый цикл"]
  ]
};
