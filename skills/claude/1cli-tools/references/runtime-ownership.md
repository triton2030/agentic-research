---
description: "PATH, receipt, version, update and explicit machine-wide ownership evidence."
---

# Runtime Ownership

Открывай для PATH/versions, «что обновить», broken CLI environment или explicit
machine-wide audit. Repo-level tool choice принадлежит
[`tool-map.md`](tool-map.md).

## Active Owner

```bash
bash ~/.claude/skills/1cli-tools/scripts/probe-tools.sh TOOL
which -a TOOL
realpath "$(command -v TOOL)"
TOOL --version
```

Затем сверь owning receipt/registry. Registry version не доказывает active
binary. Для package CLI добавь production dependency tree или runtime import:
зелёный manager receipt не доказывает целостность environment.

Project work предпочитает project-local binary. Global owner нужен только для
global update/machine audit или когда local owner отсутствует.

## Update Gate

До update отдели drift от проблемы и проверь manager, который реально владеет
active binary. Common registry probes:

```bash
HOMEBREW_NO_AUTO_UPDATE=1 brew outdated --json=v2 --greedy
npm outdated -g --json
uv tool list --show-paths --outdated
python3 -m pip list --user --outdated --format=json
```

Это network/metadata probes; запускай при соответствующем scope. После
авторизованного update повтори `which -a`, version smoke и targeted health той
команды, ради которой обновлял. Package update и runtime assets/cache могут
иметь разных owners; проверяй оба только если задача их затрагивает.

## Side-effect Ledger

| Класс | Возможный side effect | Default |
|---|---|---|
| `brew outdated/info` | update API/tap metadata | `HOMEBREW_NO_AUTO_UPDATE=1` |
| `npm doctor/cache verify` | cache repair/GC | не запускать как version probe |
| plain `npx`, `uvx` | download + cache writes | installed/local или explicit gated version |
| manager `dry-run/list/root` | cache repair или directories | сверить live help и filesystem |
| browser/runtime install | asset download/cache writes | version/list до explicit refresh |

После probe назови реально наблюдавшиеся изменения.

## Explicit Machine-wide Gate

Не включай эту ветку в обычный repo audit. Для всей машины нужны отдельные
слои, и ни один не заменяет другой:

- active command: PATH, symlink, receipt, dependency/import health;
- persistence/runtime: launch/login items, processes, listening sockets;
- live app: version из bundle metadata, code signature финального binary;
- credentials: только metadata/counts, без значений; local deletion не revoke;
- isolated environments: каждый `uv tool`/venv проверяется отдельно.

Перед process/service mutation нужен точный owner. Ad-hoc signature и stale
manager receipt остаются residual risk, а не «healthy».

## Стоп

Стоп, когда active path, owner, version/runtime smoke и manager state не
противоречат друг другу; side effects и blockers названы. Не превращай один
tool update в blanket machine cleanup.
