// Демо: все доступные node-типы и edge-варианты на одной странице.
// Полезно как визуальная палитра при сборке новых графов.

import { card, note, header, icon, materialIcon, decision, quote, file, edge } from "./_helpers";

export default {
  id: "gallery",
  title: "Галерея — все типы",
  description: "Визуальный справочник: node-types + edge-варианты",
  nodes: [
    header({
      id: "h-nodes",
      title: "Типы узлов",
      subtitle: "Каждый тип решает свою выразительную задачу"
    }),
    card({
      id: "c-card",
      kind: "skill",
      weight: 2,
      title: "SkillCard",
      kicker: "default",
      body: "Универсальная карточка: kicker + title + body + bullets. Стилизуется через kind и weight.",
      bullets: ["kicker", "title", "body", "bullets"]
    }),
    note({ id: "n-s", text: "TextNote — заметка размер s", size: "s" }),
    note({ id: "n-m", text: "TextNote — заметка размер m, помещается одна-две строки", size: "m" }),
    note({
      id: "n-l",
      text: "TextNote — заметка размер l, для более длинных аннотаций которые комментируют узел или ребро.",
      size: "l"
    }),
    icon({ id: "i-1", icon: "⚡", tooltip: "молния" }),
    icon({ id: "i-2", icon: "🔒", label: "замок" }),
    materialIcon({ id: "mi-flow", icon: "account_tree", label: "связи", tooltip: "Material Symbols: account_tree" }),
    materialIcon({ id: "mi-rule", icon: "rule", label: "правило", tooltip: "Material Symbols: rule" }),
    decision({ id: "d-1", title: "если успех?" }),
    quote({
      id: "q-1",
      text: "context drift — это когда модель забывает контракт, выработанный в начале сессии.",
      cite: "анти-паттерны"
    }),
    file({ id: "f-md", title: "README.md", note: "входная точка" }),
    file({ id: "f-json", title: "settings.json", note: "конфигурация runtime" }),

    header({ id: "h-edges", title: "Варианты рёбер" }),
    card({ id: "e-from", kind: "origin", weight: 1, title: "От", kicker: "источник" }),
    card({ id: "e-solid", kind: "skill", weight: 1, title: "solid", kicker: "по умолчанию" }),
    card({ id: "e-dashed", kind: "branch", weight: 1, title: "dashed", kicker: "опционально" }),
    card({ id: "e-dotted", kind: "memory", weight: 1, title: "dotted", kicker: "аннотация" }),
    card({ id: "e-bold", kind: "output", weight: 1, title: "bold", kicker: "главный путь" }),
    card({ id: "e-dimmed", kind: "doc", weight: 1, title: "dimmed", kicker: "слабая связь" }),
    card({ id: "e-accent", kind: "review", weight: 1, title: "accent", kicker: "акцент" })
  ],
  edges: [
    edge("h-nodes", "c-card", { kind: "dimmed" }),
    edge("c-card", "n-m", { label: "может комментироваться", kind: "dashed" }),
    edge("c-card", "d-1", { label: "ветвление", kind: "solid" }),
    edge("d-1", "i-1", { label: "если ok", kind: "solid" }),
    edge("d-1", "mi-rule", { label: "проверить", kind: "dashed" }),
    edge("mi-rule", "mi-flow", { label: "связать", kind: "dotted" }),
    edge("d-1", "q-1", { label: "иначе — правило", kind: "dotted" }),
    edge("c-card", "f-md", { kind: "dimmed" }),
    edge("f-md", "f-json", { label: "ссылается", kind: "dashed" }),
    edge("e-from", "e-solid", { kind: "solid" }),
    edge("e-from", "e-dashed", { kind: "dashed" }),
    edge("e-from", "e-dotted", { kind: "dotted" }),
    edge("e-from", "e-bold", { kind: "bold" }),
    edge("e-from", "e-dimmed", { kind: "dimmed" }),
    edge("e-from", "e-accent", { kind: "accent" })
  ]
};
