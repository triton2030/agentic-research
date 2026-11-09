# JavaScript И TypeScript

Ловушки запуска и проверки JS/TS на этом Mac.

- **Глобальный `tsc` 7** вне проекта: `strict`, `target es2025`,
  `esModuleInterop` включены по умолчанию.
- **TypeScript в LSP Claude Code.** Официальный плагин `typescript-lsp`
  выключен: его `typescript-language-server` работает через
  `lib/tsserver.js`, а в TypeScript 7 его нет. Вместо него стоит сторонний
  `typescript-native-lsp@typescript-native-lsp`. Проект на TS 7, без
  `node_modules` или без TS он обслуживает родным `tsc --lsp` (подходит
  глобальный TS 7), проект с TS ≤6 — через `typescript-language-server`
  с TS проекта. Тот лежит в `~/.local/share/typescript-language-server`,
  в `~/.local/bin` — ссылка. Что плагин запустит в проекте — `node
  <installPath>/scripts/launch.mjs --resolve` из его папки, `installPath`
  даёт `claude plugin list --json`. Оба плагина сразу не включай: на одни
  расширения стартует только один. Автообновление стороннего каталога
  выключено: `claude plugin update typescript-native-lsp@typescript-native-lsp`
  и `npm update --prefix ~/.local/share/typescript-language-server`. Когда
  официальный научится TS 7
  ([#4492](https://github.com/anthropics/claude-plugins-official/issues/4492)),
  сторонний можно снять.
- **dependency-cruiser 18** выкидывает из графа импорты, которые TypeScript
  удалит при компиляции: неиспользуемые и только для типов. Граница, которую
  держит проверка, без `options.tsPreCompilationDeps: true` пропускает такой
  импорт, и «посаженное» нарушение не роняет проверку. После включения циклы,
  замкнутые импортом типа, снимает правило `to: { circular: true, viaOnly:
  { dependencyTypesNot: ["type-only"] } }`.
- **npm 12** печатает `npm notice run …` перед каждым `npm run` и `npx`:
  `npm run -s` их убирает, после `npx` — `rg -v '^npm notice'`.
