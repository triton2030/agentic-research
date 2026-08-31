# Installed receipt — goal correction 2026-08-31

## Статус

`INSTALLED_APPROVED`: владелец безусловно одобрил exact candidate
`9ffc82e60afe2a3974bff1912ed2b2e51038b827976ad7a22a87937f03df2c06`, и
неизменная версия установлена в Codex и Claude live packages. Tracked owner в
registry отсутствует, поэтому второй source tree не создавался.

Предыдущие receipts для `5cac26…`, `c909675…` и `da51a30…` superseded; этот
receipt описывает только текущий пакет `9ffc82e…`.

## Runtime candidate

Пакет состоит из трёх runtime-файлов:

| Файл | SHA-256 |
| --- | --- |
| `SKILL.md` | `0841d5195ec7c10d78e82a71a7c6a8a8d08d2f03d5971d890d6e5830fc1c1e9f` |
| `references/audit.md` | `1181f809aae5891017e1adae3e24e3c63700a1a7d3ac557e5a967fc815870a06` |
| `references/last-year.md` | `63fdd044a835b731a3137423dcae4ed1845d7cf2ff43216e62065bd5a5f962ba` |

Aggregate (sorted relative path + NUL + bytes + NUL):

`9ffc82e60afe2a3974bff1912ed2b2e51038b827976ad7a22a87937f03df2c06`

Синхронизированная карта: `map.md` —
`23440eac905aa81ea8066671db5c3f21cf1d03deef77465a6de04fd50d9e26aa`.

## Literal counts

| Surface | Units |
| --- | ---: |
| `SKILL.md` / core | 23 |
| `references/audit.md` | 33 |
| `references/last-year.md` | 28 |
| core active set | 23 |
| version gate (`core + last-year`) | 51 |
| audit gate (`core + audit`) | 56 |

Оба gate условны: обычный `Button + useForm` их не открывает без собственной
uncertainty. Active set выше ориентира 20 остаётся явным когнитивным риском:
candidate discovery, official addresses, coverage evidence, exact cohort и
delta handoff предотвращают разные доказанные вреды. Это не новые стадии и не
автоматический blocker текущего authoring-контракта.

## Пройденные стадии и проверки

- `$1chat-recall`: owner evidence подтверждён перед финальным артефактом;
  orchestrator delegation не записывалась как owner speech; безусловное
  install approval сохранено по адресу
  `_ops/chat-recall/2026-08-30-170320-codex-01a0528c.md:23`.
- `1skill-creation`: полный refactor route, clean-room/zero-based semantic
  pass и loss checks применены; authoring/check bureaucracy не попала в runtime.
- Две допустимые checker-волны уже израсходованы предыдущим exact cycle;
  semantic evidence для незатронутых routing-свойств сохранено причинно.
- Поздняя цель проверена основным агентом против буквальных owner-цитат
  `_ops/chat-recall/2026-08-30-170320-codex-01a0528c.md:17-21`: official
  Mantine, full relevant public use, less/readable code и редкое readable custom
  exception сохранены буквально как зонтичный outcome.
- Самостоятельная loss-проверка: удаление `## Порядок` оставляет правильное
  направление, а удаление `## Цель` снова теряет критерий результата; цель не
  подменяет gates и не превращает Mantine в самоцель.
- Realistic clean probe: routing contract PASS; отсутствие pinned Mantine
  fixture сохраняет installed compatibility и runtime result как `unknown`,
  а routing не считается runtime proof.
- `qv-skill skills/1mantine-dev/draft-2026-08-30`: pass.
- `md check --paths skills/1mantine-dev`: 21 targets, 0 issues.
- `git diff --check -- skills/1mantine-dev`: pass.
- `python3 skills/shared/sync_simple_projections.py 1skill-creation --check`:
  pass; tracked owner и установленные projections соответствуют текущему
  effective baseline.
- Exact install parity: Codex и Claude
  `/Users/triton/.codex/skills/1mantine-dev/SKILL.md` и
  `/Users/triton/.claude/skills/1mantine-dev/SKILL.md` обе имеют hash
  `0841d5195ec7c10d78e82a71a7c6a8a8d08d2f03d5971d890d6e5830fc1c1e9f`;
  оба трёхфайловых package aggregate равны approved `9ffc82e…`.
- `qv-skill` для обоих live packages: pass; `md check`: по 3 targets, 0 issues;
  каждый установленный файл побайтово совпадает с candidate.

## Semantic repair

- `SKILL.md` требует exact resolved cohort одной версии для всех затронутых
  `@mantine/*`, сохраняет immutable packet/result handoff и задаёт
  `version → audit` при совместной uncertainty.
- `SKILL.md` теперь отдельно хранит Уникальный контекст и две зонтичные цели:
  official/full-use/less-readable code outcome и редкое custom-исключение.
- `audit.md` сначала строит полный relevant public candidate set из official
  Mantine surface, затем доказывает coverage с official address; hints не
  считаются полным списком, runtime без evidence остаётся `unknown`.
- `last-year.md` возвращает self-contained `{packet, cohort, result}` с
  подтверждённой `delta + official_address`, `none` или `unknown` и передаёт
  тот же packet/cohort в audit.
- Body переведён на русский; description остался коротким English
  trigger-only; component SHA receipt исправлен на текущие байты.

## Gaps / needs

- В репозитории нет pinned Mantine lockfile/package metadata/public-types
  fixture; installed compatibility и фактическое runtime behavior clean probe
  должны оставаться `unknown`, а routing не считается runtime proof.
- Остался только cognitive-risk active set `23/51/56`; current
  `1skill-creation` не делает его blocker автоматически.

## Сдача по `install-approved.md`

### Функция словами владельца

Вызов `1mantine-dev` означает сделать работу ровно по текущей официальной
документации Mantine, чтобы агент не ошибся из-за generic frontend-привычек,
использовал все релевантные public-компоненты и возможности и получил меньше
понятного, легко изменяемого кода. Mantine не становится самоцелью: редкий
читаемый локальный custom остаётся допустим, когда public-механизм повышает
совокупную сложность.

Owner evidence: `_ops/chat-recall/2026-08-30-170320-codex-01a0528c.md:18-20`.

### Findings двух независимых проверяющих

- Буквальный checker потребовал не принимать заранее названные candidates за
  полный Mantine surface: audit должен сначала вывести весь релевантный public
  candidate set, затем доказать coverage каждого required behavior с official
  address. Он также потребовал одну exact resolved version для всех затронутых
  `@mantine/*`, буквальную передачу task packet/cohort/delta и честный
  `unknown`, если installed public types недоказуемы.
- Trajectory checker подтвердил условные ordinary/version/audit маршруты и
  потребовал однозначный `version → audit` при совместной неопределённости,
  current official Mantine authority на core-пути и сохранение подтверждённой
  version delta до audit. Realistic probe подтвердил routing, но не runtime
  compatibility без pinned app fixture.

Позднее восстановление `## Цель` не меняло проверенные routing-свойства: оно
вернуло уже доказанный owner outcome в тело. После исчерпания двух checker-волн
основной агент проверил причинно затронутые точные байты, owner evidence и
loss-map самостоятельно, как требует `check-approve.md`.

### Решения основного агента

- Приняты и внесены full-candidate-set-first audit, exact cohort, immutable
  packet/cohort/result handoff, `cohort: unknown`, version-before-audit и
  official-address evidence.
- Принята owner-коррекция о явной цели; она не заменяет gates и не делает
  Mantine самоцелью.
- Отклонён возврат `help-center-map.md` и `placement.md`: более позднее
  owner-решение 2026-08-22 заменило эту пару условными `audit.md` и
  `last-year.md`.
- Отклонено механическое дробление active set ради числа: текущий протокол
  считает превышение 20 сигналом риска, а оставшиеся cohort, audit coverage и
  version handoff предотвращают разные уже наблюдавшиеся ошибки.

### Снятое с причиной

- Статические каталоги компонентов, props и миграционных ловушек сняты как
  быстро стареющая копия official docs и installed public types.
- Always-on changelog, обязательный audit обычного `Button + useForm`, шесть
  микростадий и authoring/check ceremony сняты как runtime-переусложнение; их
  заменяют core и два условных gate.
- Codex-only `agents/openai.yaml` удалён при установке: его не было в exact
  approved composition из трёх файлов, а `install-approved.md` требует
  совпадения состава и запрещает самовольное добавление `agents/`.

### Остаточные риски

- Без pinned Mantine fixture installed compatibility и runtime behavior
  остаются `unknown`; routing-проверка не является доказательством компиляции.
- Active sets `23/51/56` выше ориентира 20 и остаются видимым когнитивным
  риском, хотя version и audit gate не активируются в обычной задаче без
  соответствующей uncertainty.
- Удалённый live-only `agents/openai.yaml` не был частью owner/source package и
  отдельно не архивировался; при необходимости UI-метаданных их придётся
  восстановить как новую явно утверждённую часть пакета.
