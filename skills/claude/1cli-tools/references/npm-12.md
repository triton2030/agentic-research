---
description: "Deny-by-default dependency lifecycle scripts in active npm 12.0.2."
---

# npm 12: allowScripts

Момент: install завершился, но package с native asset/generator не работает или
npm перечислил skipped lifecycle scripts. Сверено 2026-08-19 с npm 12.0.2;
быстрее всего меняется `allowScripts` policy.

## Дельта

Dependency `preinstall` / `install` / `postinstall` теперь заблокированы по
умолчанию без matching `allowScripts`. Install может завершиться успешно после
пропуска script-а, поэтому его exit code больше не доказывает готовность
runtime asset.

```bash
npm approve-scripts --allow-scripts-pending
npm approve-scripts PACKAGE
npm deny-scripts PACKAGE
npm help approve-scripts
```

`--allow-scripts-pending` только показывает непокрытые packages.
`approve-scripts PACKAGE` пишет version-pinned entry в `package.json`;
`deny-scripts` пишет name-wide `false`. Для global install и `npx` отдельного
`package.json` нет: точечный allow передаётся install-команде как
`--allow-scripts=PACKAGE`.
