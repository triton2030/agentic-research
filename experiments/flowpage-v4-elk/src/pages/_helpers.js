// Декларативные helper'ы для page-данных. Каждая функция возвращает
// node-object с правильным `type` и плоским data, чтобы page-файлы
// читались как outline:
//
//   import { card, note, header, icon, materialIcon, decision, quote, file, edge } from "./_helpers";
//
//   export default {
//     id: "...", title: "...", description: "...",
//     nodes: [
//       header({ id: "h1", title: "Phase 1" }),
//       card({ id: "n1", title: "Запрос", body: "..." }),
//       note({ id: "n2", text: "это аннотация", size: "s" }),
//       icon({ id: "i1", icon: "⚡" }),
//       materialIcon({ id: "i2", icon: "account_tree", label: "связи" }),
//       decision({ id: "d1", title: "если ok?" }),
//       quote({ id: "q1", text: "context drift — это когда..." }),
//       file({ id: "f1", title: "README.md" })
//     ],
//     edges: [
//       edge("n1", "n2", { label: "путь", kind: "dashed" }),
//       ["n1", "d1", "tuple-form тоже работает"]
//     ]
//   };
//
// Файлы pages с префиксом `_` не подхватываются auto-discovery.

export const card = (data) => ({ type: "skillCard", ...data });
export const note = (data) => ({ type: "textNote", ...data });
export const header = (data) => ({ type: "sectionHeader", ...data });
export const icon = (data) => ({ type: "iconNode", ...data });
export const materialIcon = (data) => ({ type: "iconNode", iconSet: "material", ...data });
export const decision = (data) => ({ type: "decision", ...data });
export const quote = (data) => ({ type: "quote", ...data });
export const file = (data) => ({ type: "fileCard", ...data });

// Edge constructor. Использовать вместо tuple когда нужен kind или другие
// поля. Tuple `[source, target, label]` тоже работает для простых случаев.
export const edge = (source, target, opts = {}) => ({
  source,
  target,
  label: opts.label,
  kind: opts.kind ?? "solid"
});
