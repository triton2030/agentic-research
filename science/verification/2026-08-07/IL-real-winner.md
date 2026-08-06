# Аудит корневого `AGENTS.md` методом IL-cand-2

Прогон: `science/verification/2026-08-07/IL-cand-2/` (SKILL.md + все references,
кроме `route-table.md` и `probes.md`).
Цель: аудит `/Users/triton/Documents/GitHub/agentic-research/AGENTS.md` без правок.

---

## Ход работы

### Загрузка метода

Прочитал `SKILL.md`, затем до Gate 0 — `product-jobs.md` (три job: Load / Steer /
Prove) и `controller.md` (не смешивать три failure-а иерархии, clean re-anchor).
Дальше открывал по файлу на gate в момент gate-а, плюс условную глубину:
`triggered-rules`, `audit-placement-structure` + `placement-protocol`,
`steering-cell`, `audit-meaning-criteria` + `meaning-protocol` +
`meaning-design-mode`, `language-quality-audit` + `-findings`, `llm-divergences`
+ `-stop`, `claude-discovery` + `-placement`, `cli-recipes`, `output-stop`.

### Gate 0 — допуск

- **Mode:** `audit`. Ни один файл репо не тронут; единственная запись — этот файл.
- **Durability:** цель аудита — durable текст целиком, не разовое условие задачи.
- **Основание:** stable local fact (можно проверить существование каждого
  referent-а) + hard invariant (root объявлен центральной инструкцией в
  `README.md`).
- **Material premises, которые я НЕ взял на веру:**
  - «`_ops/GOAL.md` существует и держит scope/done/stop» → проверено, верно.
  - «`knowledge/wisdom-*` и `knowledge/practical-guides/how-to-write-skills/`
    существуют» → проверено, верно.
  - «Перечисленные `experiments/` существуют» → **опровергнуто**, см. F1.
  - «У subtree `AGENTS.md` в шапках есть `depends-on`» → **опровергнуто**, см. F2.
  - «`skills/**` однозначно указывает на owner-а» → **опровергнуто**, см. F3.
  - «Root маршрутизирует все живые owner-зоны» → **опровергнуто**, см. F4, F5.
- **Failed jobs:** `Load` (провален — F1–F5), `Steer` (частично — F3, F6),
  `Prove` (провален — F6, F7). Здоровые части не переписываю, см. «Что работает».
- Surface decision (текст vs skill/hook) не пересматриваю: это `1skill-architect`.

### Gate 1 — effective chain

- **Runtime:** Claude Code (и Codex как второй потребитель).
- **Цепь:** `~/.claude/CLAUDE.md` (global, каждую сессию) → repo `CLAUDE.md`
  (ровно одна строка `@AGENTS.md`, проверено `cat`) → `AGENTS.md`. Subtree
  `AGENTS.md` грузятся on demand при чтении субтри. Codex читает `AGENTS.md`
  напрямую. Схема соответствует `claude-discovery.md` («AGENTS.md — optional
  shared owner через `@`»).
- **Отделил «файл есть» от «текст доходит»:** `_ops/rules/**` (3 rule-doc-а),
  `skills/shared/README.md` и `science/**` существуют, но в цепь из root не
  входят — root на них не ссылается ни разу (`grep -n "rules\|science"
  AGENTS.md` → пусто).
- **Precedence и конфликты:** root vs `_ops/AGENTS.md` расходятся по механизму
  графа зон (F2). Root vs global CLAUDE.md расходятся по формату финала (F7).
  Root vs `_ops/rules/instruction-and-runtime.md` дублируют три правила (F6).
- **Effective winner** по смыслу инструкций для skill/instruction работы —
  фактически `_ops/rules/instruction-and-runtime.md`, но только для того, кто до
  него дошёл; загрузка не гарантирована ничем.
- Дополнительно: `.md-tools.toml` ограничивает semantic index `knowledge/**`.
  Значит `_ops/rules/**`, `skills/**` и сам `AGENTS.md` не ищутся через
  `1md-search` — единственный способ найти orphan-правило — grep вслепую.

### Gate 2 — owner и класс delta

Root по определению из `_ops/rules/instruction-and-runtime.md` обязан быть
«routing, local owner map, красные линии и короткие triggers». Сверил фактическое
содержимое с этим контрактом: **owner map отсутствует** (нет `_ops`, `science`,
`skills/shared`, `knowledge`), **красных линий нет вовсе** (они есть у
`_ops/AGENTS.md`, но не у root). Вместо этого root держит три процедурных
правила, копии которых лежат в cold rule-doc-е (F6).

Класс delta по находкам: F1, F2 — `local fact` (устаревший факт);
F3, F4, F5 — `owner pointer`; F6 — `behavioral rule` + duplicate repair;
F7 — `behavioral rule`.

Контейнеры не двигаю: `1ia-audit` мне здесь не нужен, все правки помещаются в
существующие файлы.

### Gate 3 — steering cell

Взял три representative fork-а и прогнал их через реально загружаемую цепь,
не подставляя предлагаемое правило задним числом.

**Cell A (самый острый).**
Fork: агенту сказали «сократи описание скила `1md-read`».
Natural act: открыть `skills/claude/1md-read/SKILL.md` — он в `skills/**`, он
tracked, он совпадает с runtime, root прямо говорит «правь его».
Plausibility: правило root буквально разрешает этот файл.
Harm: это **projection**, а не owner. Правку молча затрёт
`sync_simple_projections.py --write`, либо `--check` встанет красным.
Target act: сначала открыть `skills/shared/README.md`, разрешить owner
(`skills/shared/1md-read/portable/`), править его, потом синхронизировать.

**Cell B.** Fork: агент правит корневой `AGENTS.md`. Natural act: править сразу.
Harm: пропущен `_ops/rules/instruction-and-runtime.md`, у которого trigger
буквально «правишь `AGENTS.md`», плюс `placement.md`. Target act: открыть
rule-doc по совпадению trigger-а до правки.

**Cell C.** Fork: агент отвечает на вопрос «как устроены связи зон в репо».
Natural act: пересказать root («`depends-on` в шапках subtree `AGENTS.md`») как
факт. Harm: ложная карта репо уходит дальше по цепочке решений.

### Gate 4 — control и repair

Спросил по каждому обязательству, допустимо ли, чтобы соблюдение зависело от
качества reasoning. Проверил, что доступно как внешний gate:
`~/.claude/settings.json` → `hooks: {}`, в репо только
`.claude/settings.local.json` с одними permissions, hook-ов нет. Владелец
хуки отвергает как класс. Значит **`handoff to enforcement` для этого репо
недоступен** — честный потолок здесь prose + артефакт, который владелец видит
глазами. Поэтому нигде не рекомендую хук и не усиливаю `MUST`.

Repairs по находкам: F1 `narrow scope`, F2 `rewrite exact wording`,
F3/F4/F5 `replace with pointer` (root — маршрут, глубина у owner-а),
F6 `move to owner` + `replace with pointer`, F7 `narrow scope` + `delete`.

**Primary repair — один:** вернуть root его собственную работу маршрутизатора
(F3 + F4 + F5 одной секцией `trigger → owner`). Меньший repair (починить только
устаревшие факты F1/F2) не закрывает harm: агент по-прежнему не узнает про
`skills/shared`, `_ops/rules/**` и `science/`, а именно там лежит правда,
меняющая следующий ход.

### Gate 5 — exact delta

Формулировки в findings ниже даны как `trigger → положительное правило →
owner/source`, а не как «будь внимателен». Прогнал delete-first pass: всё, что
не меняет следующий акт (перечисление experiments, повтор языка, исследовательская
вставка про «единицы процентов»), помечено на удаление, а не на переписывание.

### Gate 6 — bypass и доказательство

**Предсказанный bypass primary repair-а:** агент «выполнит» его, добавив в root
секцию со списком путей (`_ops/rules/` — правила, `science/` — наука). Форма
выполнена, решение не изменилось: список зон не говорит **когда** открывать,
поэтому следующий агент всё равно не откроет rule-doc. Защита: каждая строка
маршрута обязана начинаться с наблюдаемого момента («правишь `SKILL.md` →
…»), а не с имени папки. Это не лечится ещё одним `MUST`.

**Прогнанные probe (2 холодных субагента, read-only, голый промпт):**

| Probe | Промпт | Наблюдаемый результат |
|---|---|---|
| A | «Надо сократить формулировку в описании скила `1md-read`. Какой файл править?» | Назвал **правильный** owner `skills/shared/1md-read/portable/SKILL.md` и явно сказал, что `skills/claude/` и `skills/codex/` — projections. Но дошёл до этого через самостоятельный широкий поиск и чтение `skills/shared/README.md`, **не** через root. |
| B | «Собираюсь править корневой `AGENTS.md`. Какие правила этого репо тут действуют?» | Нашёл `_ops/rules/instruction-and-runtime.md` и `placement.md` — снова широким поиском, root на них не указывал. И **воспроизвёл ложный факт**: «Граф зон живёт в `depends-on` в шапках subtree `AGENTS.md`. Субтри-файлы и `_ops/rules/*.md` имеют [frontmatter]». Проверка: 6 из 8 subtree `AGENTS.md` не имеют frontmatter вообще. |

**Сила claim — честно:**

- Probe B — **прямое поведенческое подтверждение F2**: агент взял строку root за
  факт и передал её дальше как карту репо, не проверив. Cell C реализовалась.
- Probe A и «нашёл rule-doc» в B — **evidence слабое и загрязнённое**: оба
  агента были поисковыми (`Explore`), их работа — широкий fan-out. Рабочий агент
  с задачей «правь» так не ищет. Поэтому probe A **не** доказывает, что F3
  безвреден, и **не** доказывает, что он вреден: natural act рабочего агента
  здесь не измерен.
- Matched with/without прогонов (старая цепь vs исправленная, тот же кейс, та же
  модель) **не делал** — правки запрещены mode-ом. Всё, кроме F2, стоит на
  design-time proxy + проверке referent-ов. Design-time proxy до доказательства
  эффективности не повышаю.

---

## Findings

### Что работает как правило

Не трогать. Каждое из них имеет наблюдаемый trigger, положительный дефолт и
меняет первый акт.

**W1. GitHub — коммить и пушить прямо в `main` без спроса.**
Лучшее правило в файле. Оно рвёт явный конкурирующий дефолт среды («commit or
push only when the user asks; if on the default branch, branch first»), называет
момент (любой коммит), даёт положительный дефолт (пуш в `main`) и убирает
вопрос («без подтверждений»). Без него агент каждый раз спрашивал бы или
заводил ветку.

**W2. «Skill contract сильнее старых repo notes».**
Наблюдаемая развилка (обнаружено расхождение) → однозначное правило (следуй
`SKILL.md`). Работает. Оговорка — дубль, см. F6.

**W3. «Продукт всегда снаружи репо; правка скила — глобальный артефакт, пиши
project-independent».**
Меняет реальный ход: удерживает от вшивания путей и допущений этого репо в
глобальный скил. Слабое место — нет наблюдаемой операции проверки. Усиление на
одну строку: *«перед готовностью назови в тексте скила каждое место, которое
верно только для этого репо; либо убери, либо обобщи»*.

**W4. Рамка моделей и запрет model-neutral канона.**
Сверено с `_ops/GOAL.md` — совпадает, не расходится. Но это повтор
`GOAL.md → NOT in scope`, а не маршрут к нему; см. F5.

### Что не работает

---

**F1 — Список `experiments/` устарел и вводит в заблуждение.**

*Failure mode:* accidental mandate + устаревший referent.
*Evidence:* `AGENTS.md:52-54` перечисляет `claude-bridge`, `gemini-mcp`,
`md-tools`, `flowpage-v4-elk`, `strategy-gallery`, `global-agent-surface-viewer`.
Факт: `gemini-mcp` и `md-tools` в `experiments/` **отсутствуют** (единственное
совпадение по всему репо — файл конфига `.md-tools.toml`). При этом список
пропускает 9 реально существующих под-проектов (`1design-review`,
`clickup-tool`, `codex-bridge`, `logical-map-lab`, `mavo-task-containers`,
`obsidian-base-board-mavo-snapshot`, `obsidian-beauty-lab`, `profit-forecast`,
`prose-audit-lab`, `zbs-dossier`, `обзор-хуков`).
*Почему это не косметика:* описательный список в инструкции читается как карта.
Агент, ищущий `md-tools` в `experiments/`, не найдёт его и решит, что его нет.
*Repair (delete):* убрать перечисление целиком. Правило («каждый под-проект
держит свою правду в локальном `README.md`/`AGENTS.md`; правь от неё, не от
корневой») работает без имён и не устаревает.

---

**F2 — «Граф зон — `depends-on` в шапках subtree `AGENTS.md`» неверно.**

*Failure mode:* literal scope / устаревший факт, подтверждён поведением.
*Evidence:* `AGENTS.md:30-31`. Проверка всех 8 subtree `AGENTS.md`:
frontmatter есть у **двух** (`_workspace/HTML_artifacts`,
`experiments/clickup-tool`), `depends-on` — у **одного**
(`experiments/clickup-tool`). `_workspace/HTML_artifacts/AGENTS.md` использует
**другой** механизм: `read-before-edit` / `edit-after-edit`. И `_ops/AGENTS.md`
прямо объявляет для своей зоны третий набор: «`read-before-edit`,
`edit-after-edit`, related-docs sections и dependency-radius».
Root и `_ops` противоречат друг другу по механизму.
*Поведенческое подтверждение:* холодный probe B пересказал строку root как факт
о репо, добавив от себя, что frontmatter есть у субтри-файлов. Это неверно для
6 из 8. Правило не просто мёртвое — оно активно производит ложную карту.
*Repair (rewrite exact wording):* заменить на честное —
*«У зоны своя правда: перед правкой в субтри прочитай его `AGENTS.md`/`README.md`.
Объявленные связи между документами (`depends-on`, `read-before-edit`,
`edit-after-edit`) есть не везде; когда они есть, влияние правки считает
`1md-graph`.»*
Альтернатива, если владелец хочет именно граф: сделать `depends-on` реальным
требованием и заполнить 7 файлов — но тогда это change-задача, а не строчка.

---

**F3 — `skills/**` не разрешает owner-а; настоящая карта владения не в цепи.**

*Failure mode:* under-specified scope у самого дорогого правила файла.
*Evidence:* `AGENTS.md:12-15`: «Если package имеет tracked owner в `skills/**`
или `experiments/**`, сначала правь его, а global install считай projection».
Факт из `skills/shared/README.md`: внутри `skills/**` **три** уровня —
owner (`skills/shared/<pkg>/portable/`), tracked projection
(`skills/claude/<pkg>/`, `skills/codex/<pkg>/`) и installed projection
(`~/.claude/skills/`). Для `1md-read`, `1md-search`, `1skill-architect`,
`1deep-agents` owner — в `shared`, а `skills/claude/...` — projection, «их не
редактируют напрямую».
*Почему это steering-провал:* правило противопоставляет `skills/**` только
global install. Внутри `skills/**` оно молчит, а именно там развилка. Буквальное
прочтение разрешает править `skills/claude/1md-read/SKILL.md` — projection.
Harm: правку затирает `sync_simple_projections.py --write`.
*Оговорка по evidence:* probe A owner-а нашёл правильно, но самостоятельным
поиском, не по root. То есть избыточность репо пока спасает; правило свою работу
не делает.
*Repair (replace with pointer):* дописать одну строку —
*«Внутри `skills/**` owner-а разрешает `skills/shared/README.md`:
`skills/claude/**` и `skills/codex/**` бывают tracked projections. Правишь
package — сначала открой его.»*

---

**F4 — `_ops/rules/**` — три orphan-правила, root на них не ссылается.**

*Failure mode:* orphan RULE (по `triggered-rules.md`: «RULE без root route —
orphan»).
*Evidence:* `_ops/rules/` содержит `instruction-and-runtime.md`,
`local-tools.md`, `placement.md`. У каждого явный `Trigger:`, `Owner:`, `Check:`
и `depends-on` на `AGENTS.md` — то есть они спроектированы как cold surface,
подключаемая из root. `grep -n "rules" AGENTS.md` → **ноль совпадений**.
Обратная сторона: `_ops/AGENTS.md` требует «Если route/owner rule-doc меняется,
синхронизировать root `AGENTS.md`» — обязанность объявлена у ребёнка, маршрута
у родителя нет.
*Утяжеляющее обстоятельство:* `.md-tools.toml` держит semantic index только на
`knowledge/**`. `_ops/rules/**` не ищется через `1md-search`. Единственный путь —
угадать grep-ом.
*Repair (primary, replace with pointer):* секция маршрутов в root, где каждая
строка — **наблюдаемый момент**, а не папка:
- правишь `AGENTS.md` / `CLAUDE.md` / `SKILL.md` / prompt / hook →
  `_ops/rules/instruction-and-runtime.md`
- двигаешь раздел или заводишь новый файл → `_ops/rules/placement.md`
- собираешь CLI-evidence, ищешь stale refs / links / dead code →
  `_ops/rules/local-tools.md`

---

**F5 — `science/` не существует для корневой инструкции.**

*Failure mode:* gap в owner map.
*Evidence:* `science/` — живая зона: `_ops/GOAL.md` держит её в **In scope**
(«Вести научную программу `science/`», решение владельца 2026-08-04),
`README.md` даёт ей пункт 6 с входом `science/README.md`. В `AGENTS.md` — ни
одного упоминания (`grep -n "science"` → пусто). Секция «Что Это За Репо»
перечисляет зоны репо и пропускает активную.
*Harm:* агент, пришедший в `science/` из root, не знает ни owner-а, ни того, что
это не `knowledge/` и не `experiments/`.
*Repair (replace with pointer):* одна строка в «Локальная Правда»:
*«`science/` — программа изучения мышления ЛЛМ (тезисы, статусы evidence,
верификация); вход и правила — `science/README.md`. Физику держит
`knowledge/how-llms-think.md`, дубли не заводить.»*

---

**F6 — Три из четырёх «Приоритетов» — дубли cold rule-doc-а; направление
владения перепутано.**

*Failure mode:* text-level duplicate + competing owner.
*Evidence:* совпадения root ↔ `_ops/rules/instruction-and-runtime.md`:

| Правило | Root | Rule-doc |
|---|---|---|
| «Живой `SKILL.md` выигрывает конфликт» | `AGENTS.md:35-36` | «Живой `SKILL.md` выигрывает конфликт с root-инструкцией» |
| «Начинай с ближайшего `wisdom-*` и одного guide» | `AGENTS.md:37-39` | «Для instruction/skill/prompt work читать ближайший `wisdom-*` и один релевантный guide» |
| «Правка skill только через `1skill-architect`» | `AGENTS.md:40-41` | «Claude skills можно редактировать только по явной просьбе и через `1skill-architect`» |

*Диагноз по `triggered-rules.md`:* «Always-on invariant остаётся в effective
`AGENTS.md`; копия procedure в root — competing owner». Направление перепутано в
обе стороны:
- «`SKILL.md` бьёт root» — **always-on precedence-инвариант**, его место в root.
  Копию убрать из rule-doc-а.
- «читать `wisdom-*` + guide» и «через `1skill-architect`» — **triggered**
  правила (срабатывают только на instruction/skill работе), их место в rule-doc-е.
  Из root убрать процедуру, оставить trigger→маршрут (см. F4).

*Отдельно — «ближайший `wisdom-*`» не является операцией.* Все 8 файлов
`wisdom-*` лежат плоско в `knowledge/`; «ближайший» ничего не выбирает.
Repair: *«правишь Claude-скил → `wisdom-claude-code.md` + `wisdom-skills-plugins.md`;
Codex-поверхность → `wisdom-codex.md`; поведение модели → `wisdom-llm.md` или
`how-llms-think.md`»*.

---

**F7 — Абзац про `1skill-architect`: мандат без следа + жанровый сбой.**

*Failure mode:* risk-word overclaim + нарушение репозиторием собственного правила
о жанре instruction file.
*Evidence:* `AGENTS.md:40-48` — 9 строк, в которых смешаны: мандат
(«**обязательно** вызови»), исследовательское утверждение («соблюдается в
единицах процентов независимо от формулировки»), определение хорошего оператора,
контрастивный пример («процитируй строку» vs «рассмотри несколько подходов») и
указатель на владельца. При этом `_ops/rules/instruction-and-runtime.md` прямо
запрещает: «В instruction file не класть историю, обоснование, examples или
редкую глубину. Оставляй trigger и ссылку на owner».
*Главное — правило не выполняет собственный тезис.* Абзац утверждает:
«правило без предъявляемого следа соблюдается в единицах процентов». У самого
мандата предъявляемого следа нет. «Вызови `1skill-architect` и проведи его audit
когнитивных пустот» закрывается фразой «провёл» в финале — и bypass бесплатен.
*Control (Gate 4):* хуков в системе нет (`hooks: {}`), владелец их отвергает как
класс. Значит усиливать нечем и не надо; единственный доступный control —
**артефакт, который видно глазами**.
*Repair (narrow scope + move to owner):* оставить в root трёхстрочный мандат с
наблюдаемым следом, остальное вернуть владельцу:
> Новый или переписанный skill принимается только после `1skill-architect`. В
> финале приведи: (1) строку контракта выхода, из которой шаг не выводится,
> (2) операцию, которая её закрывает, (3) наблюдаемый след, по которому видно
> исполнение. Нет всех трёх — skill не принят. Метод и evidence — живой
> `1skill-architect`.

Исследовательскую вставку и пример перенести в `1skill-architect` /
`knowledge/`.

---

**F8 — Секция «Проверка» конфликтует с глобальным контрактом финала.**

*Failure mode:* конфликт precedence + повтор глобального правила.
*Evidence:* `AGENTS.md:68-69`: «покажи только существенное evidence… Пиши
по-русски, коротко, без справочного шума». Глобальный `~/.claude/CLAUDE.md`
требует обратного акцента: «Понятность важнее краткости: строка-ярлык, из которой
не видно, что произошло, хуже лишнего предложения» + обязательный отдельный блок
с пересказом простым языком и собственным мнением.
*Harm:* два durable текста в одной цепи тянут финал в разные стороны; агент
может срезать обязательный пересказ, сославшись на «коротко».
*Второе:* «Пиши по-русски» — чистый повтор глобального раздела «# Язык». Первая
же строка `AGENTS.md` гласит: «усиливай глобальную инструкцию локальной правдой
проекта, **не повторяй её**». Файл нарушает собственное открывающее правило.
*Repair (delete + narrow scope):* снять «Пиши по-русски» и переформулировать как
дельту, а не как конкурента:
*«Локально к глобальному формату финала: покажи, что изменено, чем проверено и
какой риск остался. Это дополняет обязательный простой пересказ, а не заменяет
его.»*

---

## Сводка

```text
Mode + durability: audit; durable
Effective chain + owner: ~/.claude/CLAUDE.md -> CLAUDE.md(@AGENTS.md) -> AGENTS.md
  -> subtree on demand. Вне цепи: _ops/rules/**, skills/shared/README.md,
  science/**. Semantic index (.md-tools.toml) = только knowledge/**.
Steering fork: «правь package в skills/**» -> natural act: правка projection
  skills/claude/1md-read -> harm: затирается sync-скриптом. Target act: разрешить
  owner через skills/shared/README.md.
Control + repair: enforcement недоступен (hooks {}, отвергнуты владельцем) ->
  prose + наблюдаемый артефакт. Primary repair: вернуть root работу
  маршрутизатора (F3+F4+F5) секцией «наблюдаемый момент -> owner».
Behavioral proof + risk: F2 подтверждён холодным probe (агент пересказал ложный
  факт как карту репо). Остальное — design-time proxy + проверка referent-ов.
  Matched with/without прогонов НЕ делал (audit mode). Probe A/B загрязнены:
  поисковые агенты ищут шире рабочих, поэтому natural act рабочего агента для
  F3 не измерен.
```

### Порядок правок, если владелец даст change mode

1. **F4 + F3 + F5** — маршруты (primary). Без них остальное косметика.
2. **F2** — ложная карта, единственная находка с поведенческим подтверждением.
3. **F6 + F7** — развести дубли по направлению владения, вернуть глубину скилу.
4. **F1 + F8** — удаления.

### Что осталось непроверенным

- Natural act **рабочего** (не поискового) агента на fork-е F3.
- Действительно ли `experiments/1design-review`, `logical-map-lab` и прочие
  9 папок сознательно не названы, или список просто не обновляли.
- Нужен ли `depends-on` как реальный механизм (F2, альтернатива) — это решение
  владельца о работе, а не правка строки.
