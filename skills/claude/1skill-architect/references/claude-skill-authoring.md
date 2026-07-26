# Claude Skill Authoring

Читай этот reference при создании или существенной правке Claude skill,
`description`, limits, runtime transfer или source-backed claims.

## Оглавление

- Core Rules — frontmatter, micro-router, limits.
- Evaluation — should-trigger / should-not-trigger gates, output check.
- Checks — команды для длины `description`, line count, reference depth.
- Collision test against live skills — semantic-proxy против соседей.
- Source Discipline — что можно цитировать как Anthropic.
- Current Source Anchors — официальные URL и runnable `skill-creator`.

## Core Rules

- `description` — discovery contract. Front-load главный use case, trigger
  words и adjacent boundaries. Limit зависит от target: portable Agent Skills
  max 1024; Claude Code skill listing сейчас сокращает combined
  `description + when_to_use` после 1536. Cross-surface skill держи ≤1024 и
  перепроверяй live docs/runtime.
- `SKILL.md` — микро-роутер: outcome, границы, минимальный default path,
  conditional routes, validation и stop. Scope, authority, required output и
  side-effect boundary называй явно, только если они меняют поведение. Не
  отправляй Claude читать все references подряд.
- Reference files держи one level deep от `SKILL.md`; если reference >100 lines,
  добавь table of contents at the top — **plain-text списком, не `[](#…)`-якорями**
  (reference читается моделью линейно; slug-якоря renderer-specific и непереносимы).
- Body держи <500 lines. При приближении к лимиту выноси depth в references.
- `name`: max 64 characters, lowercase letters/numbers/hyphens, без XML tags и
  reserved words `anthropic` / `claude`.
- Для текущих Claude-моделей не добавляй общие объяснения «на всякий случай»:
  добавляй только context, который меняет действие.

## Метод триггерного описания: архитектура → сжатие

`description` грузится в контекст КАЖДЫЙ ход у всех model-invoked скилов — постоянный
налог, растущий с числом скилов. Поэтому описание пишется в ДВЕ фазы: сперва построй
полную архитектуру (несёт все функции), потом отдельным глубоким ходом сожми её объём,
не теряя ни одной функции. Не сворачивай фазы в одну: «строй сразу минимально» прячет
и недостающие функции, и неочевидные сжатия, которые видны только на готовой архитектуре.

### Фаза 1 — Архитектура (опиши все функции, длина пока не важна)

Ядро — **Условие × Дельта**: триггер срабатывает, только если оба ≠ 0.

- **Условие — наблюдаемый якорь.** Вяжи на действие, в котором модель уверена ПРЯМО
  СЕЙЧАС (какой файл/папку пишет, что генерит новый код), не на категорию, в которую
  ей надо себя сначала опознать («дизайн», «безопасность») — это опознание модель
  пропускает (решение растворяется в одном проходе генерации). Классификацию делаешь
  ты при написании и зашиваешь как якорь; рантайм — ноль суждений. Спектр жёсткости:
  путь/папка → глагол действия → категория (избегай). Частое срабатывание одного скила
  не вредит (модель не перевызывает уже вызванный) — не сужай условие из страха «слишком
  часто», сужай только против ЧУЖОГО момента (collision).
- **Дельта — неочевидная ставка в самом триггере.** Модель решает, открывать ли скил,
  ПО ОПИСАНИЮ, не открывая тело. Банальный триггер → не откроет, даже если внутри
  важное. Сигналь, что неочевидного / что сломётся. Дельта = 0 → no-op обнаружения.

Остальные функции архитектуры (детально — Core Rules выше и канон `writing-great-skills`):

- **Hot zone** — главный момент + trigger words + leading word в первые ~120-200 симв.
- **Trigger surface, не capability list** — «когда нужно X», не «умеет A, B, C».
- **Один триггер на ветку** — синонимы одной ветки схлопни.
- **Near-miss границы и skip-routes** — против overtrigger и collision у соседей.
- **Intent / понятный use case**, потолок выбранного runtime; portable = 1024.

Конец фазы 1: описание делает каждую работу — но, скорее всего, длинное.

### Фаза 2 — Сжатие (та же функция, минимальный объём)

Отдельный глубокий ход ПОСЛЕ готовой архитектуры. Принцип: **описание — указатель к
телу, не выжимка тела.** Единственная работа загруженного слоя — маршрутизация
(открыть / не открыть); всё, что объясняет, — в тело (читается при открытии = бесплатно).
Рычаги, по убыванию выгоды:

1. **Перенеси в тело.** Identity, полное «почему», примеры, обоснование → тело. В
   описании остаётся триггер + сигнал ставки.
2. **Leading word** — главный движок сжатия: несёт и якорь, и дельту/роль в одном
   претрейн-токене. Объяснение ставки → тело, в триггере только слово-сигнал.
3. **Срежь неподтверждённые skip-routes.** Оставь маршрут только на ЭМПИРИЧЕСКИ
   подтверждённую collision (collision-test: top-1 dominance не держится). Не ростер
   «на всякий случай». skip-хвосты — главный налог набора, растущий с N; уникальный
   **Наблюдаемый якорь** снимает их у источника.
4. **Нулевой налог.** Скил, который зовут только руками и который не нужен другим
   скилам, → user-invoked (`disable-model-invocation: true`): описание уходит из
   контекста модели целиком; индекс держит router-скил.

**Cut-test (по каждому пункту):** удали — изменилось, КАКОЙ скил выстрелит? Нет →
no-op или материал тела, режь/переноси.

**Ярусный бюджет (цель фазы 2, не потолок):** уникальный якорь (path/folder/file-type;
большинство локальных `2*`) — ~120-250 симв; общий скил с реальной коллизией —
~300-500; runtime ceiling не является целью.

### Candidate canvas и аудит полотна

Полный live-набор model-invoked descriptions — authoring-time candidate canvas,
но runtime co-presence не гарантирована. Сначала склей candidate canvas и прочти
его как один документ, затем для broad/adjacent trigger проверь фактически
видимый prompt surface.

Правда о скиле живёт в ЕГО описании; соседи указывают на него bare pointer,
не пересказывают. Это уменьшает налог и остаётся корректным, даже если runtime
не показал весь candidate canvas.

Аудит полотна РЕЖЕТ:

- повторную **характеристику** соседа → bare pointer;
- **no-op skip-route** — маршрут к цели, чей момент этот скил и так не перехватил бы
  (цель громко claim'ит его сама). Cut-test: убери маршрут — скил начнёт over-fire на
  этот момент? Нет → no-op, режь. Маршрут оставляй только на реальный **near-miss**
  (триггеры скила правда граничат с моментом соседа). Это безопасная замена полному
  collision-тесту для дропа маршрутов.
- повтор мета-прозы / скаффолдинга.

Аудит полотна НЕ режет: **триггер-фразы**. Одна фраза-триггер в двух описаниях — не
дубль, а **collision**: решай владением (момент одному owner), не удалением, иначе дыра
в discovery. Literal grep/n-gram недосчитывает — дубль обычно семантический (та же мысль
другими словами), виден глазом на полотне, не регуляркой.

## Evaluation

- До body набросай should-trigger и should-not-trigger prompts.
- Minimum gate: ≥3 should-trigger и ≥3 should-not-trigger.
- Strict gate: 8-10/8-10 near-misses для global, frequent, risky, broad,
  security/network/credentials или already-regressed skills.
- Проверяй both discovery and output: скилл должен не только активироваться, но
  и вести к наблюдаемому результату.
- Для нового skill сравни with-skill vs no-skill; для улучшения existing skill
  сравни with-skill vs previous-skill snapshot. Хотя бы один realistic output
  check нужен для значимых правок; matcher-only проверка не ловит слабое тело.
- Этот output check — лёгкая ручная проверка. Measured benchmark с variance,
  baseline-сравнение и iteration loop делегируй официальному `skill-creator`
  (его эмпирический конвейер), а не строй параллельный здесь.

## Checks

Description length for block frontmatter:

```bash
awk '/^description: >/{flag=1; next} /^---$/{flag=0} flag' SKILL.md | wc -m
```

Description length for inline/mixed frontmatter:

```bash
python3 -c "import yaml; print(len(yaml.safe_load(open('SKILL.md').read().split('---',2)[1])['description']))"
```

Line count:

```bash
wc -l SKILL.md references/*.md
```

Reference depth:

```bash
find . -path './references/*/*' -type f
```

## Collision test against live skills

`skill-creator` меряет триггеринг в изоляции — коллизию против живых соседей он
не ловит. Дешёвый semantic-proxy: не индексируй live `~/.claude/skills`
напрямую, сделай копию (`/tmp/skills-test`), индексируй `md index
/tmp/skills-test` по протоколу `1md-navigator` (dry-run→confirm), после каждой
правки `description` переиндексируй (иначе vectors stale).

- should-trigger (≥3): `md search /tmp/skills-test --query "<phrase>" --scope
  descriptions --limit 5 --json` → top-1 = candidate; unrelated skill в top-3 =
  collision, переписывай пока dominance не держится.
- should-not-trigger (≥3): candidate отсутствует в top-3.
- `md overlaps` для этого не бери: он сравнивает retrieval-enriched section
  vectors (в них подмешаны description, title и heading-chain), а не
  model-invoked trigger surface. Кто делит момент — решай по should-trigger
  прогонам выше: сведи к одному owner или задокументируй dual-fire.

Semantic-proxy, не замена `run_loop.py` (`skill-creator`: train/test split,
held-out выбор) — измеренная оптимизация триггеринга там.

## Source Discipline

- Anthropic-endorsed: official docs or close paraphrase from
  `platform.claude.com/docs`, `anthropic.com/engineering`,
  `github.com/anthropics/skills`, `code.claude.com/docs`.
- Anthropic-compatible engineering: our composition against documented failure
  patterns. Mark as our engineering, not “Anthropic recommends”.
- Pure extrapolation: mark explicitly and treat skeptically.
- Do not invent metrics. If a concrete number is not in the source, do not cite
  it as fact.
- If unsure, re-fetch the Anthropic source; do not quote from memory.

## Current Source Anchors

- `https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices`
- `https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview`
- `https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md`
  — официальный `skill-creator`: это и канонический текст best-practices, и
  **установленный runnable tool** (`~/.claude/plugins/.../skill-creator`):
  benchmark с variance (`aggregate_benchmark.py`), eval-viewer
  (`generate_review.py`), авто-оптимизатор `description` (`run_loop.py`),
  упаковка (`package_skill.py`). Для measured evaluation, оптимизации
  триггеринга и packaging делегируй ему; не воспроизводи его конвейер и не
  редактируй его (чужой owner).
