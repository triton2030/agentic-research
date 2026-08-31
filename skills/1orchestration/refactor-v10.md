# Минимальный post-install repair 1orchestration — v10

Status: `candidate; official/tracked/live frozen`.

## Baseline и функция

- Действующий `1skill-creation`: `SKILL.md` SHA-256
  `6e6b93e97eef2a31c8922ba8462a28a086c82ec80c6566c39ed63fc6bdc9f6a3`.
- Старый пакет и v9 использованы как evidence потерь, а не как форма нового
  commander's intent.
- FAST-функция: распределить когнитивную нагрузку перед поручением так, чтобы
  участники сохранили качество, а root не потерял владение общей работой.

## Commander's intent

Поручение перераспределяет нагрузку. Root действует как технический директор:
удерживает пользу и траекторию общей цели, принимает решения, интегрирует
результаты и владеет приёмкой, пока остальные участники удерживают только
выполнимые наборы. Root лично читает только load-bearing owner/authority truth;
делегируемое evidence читает исполнитель. Зависимый ход открывается только по
доказанному `pass` каждого обязательного критерия.

## Clean-room и zero-based verdict

Чистый исполнитель, не видевший старого пакета, восстановил все три смысла, но
предложил пять runtime-разделов и шестнадцать новых строк. Форма отклонена:
она повторяла выводимое стандартное поведение и увеличивала active set. Из неё
принят только semantic confirmation; candidate сохраняет двухфайловую форму v9
и меняет три шва.

## Три изменения

1. В Уникальный контекст возвращена одна CTO-формулировка root-владения
   пользой, траекторией, решениями, интеграцией и приёмкой.
2. Pre-brief чтение сужено: root читает load-bearing owner/authority sources,
   а делегируемое evidence читает назначенный исполнитель.
3. Приёмка снова явно отвергает assertion/progress/`done` как evidence и даёт
   `pass` только по обещанному адресу либо наблюдаемому результату.

State machine, reference-файлы, новые стадии и поля brief не добавлены.

## Preservation map

| Смысл | Адрес v10 | Решение |
| --- | --- | --- |
| CTO, польза и траектория | Уникальный контекст | восстановлен зонтиком |
| решения, интеграция, acceptance | Уникальный контекст | восстановлены зонтиком |
| root читает owner/authority truth | шаг 1 | сохранён и сужен |
| делегируемое evidence читает actor | шаг 1 | восстановлено |
| source-bound brief | шаг 2 | сохранён без изменений |
| actor/root active-set и soft `20` | шаги 3–8 | сохранены без изменений |
| self-report не evidence | шаг 9 | восстановлен hard line |
| upstream invalidation | шаг 10 | сохранён без изменений |

## Agent-default audit

| Добавка | Дефолт → механизм → вред без строки → цена строгости |
| --- | --- |
| CTO-зонтик | root оптимизирует передачу → ментальная модель владельца общей работы → теряются польза, интеграция и acceptance → root сохраняет верхнеуровневое ownership |
| граница чтения | «всё влияющее» выглядит безопасно → root читает delegated evidence повторно → нагрузка дублируется → root обязан отличать owner/authority truth от evidence actor-а |
| evidence hard line | self-report выглядит достаточным progress signal → dependency открывается без проверки → ложный pass → root требует адрес или наблюдаемый результат |

Остальные строки чистого пересоздания сняты: их поведение выводится из этих
трёх смыслов и существующего brief/active-set протокола.

## Предварительный active set

Счёт до независимой проверки: `prepare 10 · root-work 11 · direct 11 · split
11 · accept 8 · upstream-change 5`. Это mode-specific body units; task/source
units каждого участника добавляются отдельно. `20` остаётся мягким ориентиром.

## Falsifiers

- Root в clean case всё ещё читает делегируемые Product Frames до brief.
- Root открывает dependency после сообщения «done, all three support the rule»
  без обещанных адресов или наблюдаемого результата.
- Любой реальный режим exact candidate превышает 20 body units.
- Для прохождения проверки требуется новая стадия, reference или state machine.

## Exact candidate

- Путь: `skills/1orchestration/draft-v10/`.
- Package manifest: `3479a08389cc4582b8557118b2b208d97229dc0f45e486e9d879635ca975f0b8`.
- `SKILL.md`: `0dab19d7bf285693f84f4eebac9ca2733698a9d0abb40fd604c61215a6edbf7e`.
- `platforms/codex/agents/openai.yaml`:
  `bfa2ce85d16ee139393137b2d2d566062e47a059fa335bf0b212db4729011a5d`.

Manifest hash: для package-relative файлов в лексикографическом порядке
хешируется `relative_path + NUL + raw_bytes + NUL`.

## Check round 1

- Trajectory: findings `[]`; counts `10 · 11 · 11 · 11 · 8 · 5`.
- Clean probe: behavior pass; delegated files opened `0`; bare `done` оставил
  все пять критериев без `pass`.
- Literal: одна finding — trigger начинался с `Use before`, тогда как current
  `skill-short-description.md` требует шаблон `Use when`.
- Исправлены только `description` и `short_description`; body и counts не
  менялись. Manifest `0477d979…1aeaa` снят новой exact версией выше.

## Terminal gate

- Literal round 2: findings `[]`; оба файла, YAML, language, links и trigger
  use/skip/near-miss проверены.
- Trajectory round 2: после исправления неполного path-scope проверены оба
  файла; findings `[]`; verdict `PASS`.
- Clean round 2: `behavior_pass`; exact manifest совпал; delegated reads `0`;
  bare `done` не открыл dependency.
- Counts двух checker-ов совпали: `10 · 11 · 11 · 11 · 8 · 5`.
- Candidate готов к exact approval; установка этим циклом запрещена.
