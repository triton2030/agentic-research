# Происхождение — 1cli-tools

Переработка 2026-08-19 меняет работу скила с общего local-tool router-а на
пакет знания в момент.

## Дефицит И Форма

Класс: **знание в момент**.

Дефицит словами владельца: «скилл по терминальным инструментам существует для
того, чтобы оповестить агента о той информации, о которой у него нет в памяти»
— `_ops/chat-recall/2026-08-19-160259-codex-01a019a8.md`.

Форма владельца: «тело скилла маленькое, компактное, короткое описание
вызывающее и должно звучать как важное, а референс файлы разделены по разделам»
— тот же holder.

Владелец отдельно разрешил автономно закончить весь цикл без следующих
согласований — тот же holder.

## Триада

- Цель: дать агенту новую локальную возможность CLI, которой нет в памяти и
  которая меняет ход текущей задачи.
- Готово: агент открывает один тематический reference, сверяет active
  version/help и применяет capability вместо старого маршрута или helper-а.
- Не цель: каталог binaries, полный release archive, blanket inventory или
  разрешение на mutation.

## Источники Фактов

Факты снимка 2026-08-19 взяты из active binaries и их help:

- `agent-browser --help`, `agent-browser skills list --json`;
- `ast-grep --help`, `ast-grep outline --help`, `sg --version`;
- `npm help approve-scripts`, `npm help deny-scripts`, `npm ci --help`;
- `uv tool --help`, `uv tool audit --help`, `uv tool upgrade --help`;
- `tsc --help --all`;
- `md --help`, `md tools --help`, tool-specific help;
- `gh --help`, `gh skill --help`, `gh agent-task --help`;
- `vercel --help`, `vercel skills --help`;
- `ffmpeg -encoders`, `ffmpeg -filters`, `ffmpeg -buildconf`;
- fresh no-tool model comparator для knowledge-gap claim — точный receipt в
  `evidence.md`, task `/root/cli_memory_baseline`.

References — датированный knowledge snapshot. Live help остаётся каноническим
владельцем быстро меняющегося точного синтаксиса. Пакет knowledge-dominant:
единственное поведенческое исключение — прямо названное владельцем совместное
обновление конфликтующих active versions.
