# Буквальная проверка minimal-pass v1

## Verdict

`pass` — **Находок нет**. Exact candidate буквально сохраняет принятый
owner-смысл, не возвращает снятые ритуальные стадии и остаётся в пределах
одновременно активного бюджета.

## Exact версия и scope

- `candidate/SKILL.md`: SHA-256
  `6aa4ec3785d3c57d2cec142c92e4541dc52e114225661f9c5ffee7382e9496c7`;
  фактический SHA совпал с ожидаемым до суждения.
- `candidate/agents/openai.yaml`: SHA-256
  `64f664e75d2254dace69065ffb86e887b36a0258f42f25cbebcaead75ea83f0d`.
- Полностью прочитан текущий `/Users/triton/.codex/skills/1skill-creation/`:
  `SKILL.md`, оба файла checker-ролей, `agents/openai.yaml` и все восемь
  `references/*.md`.
- Полностью прочитаны project-wide
  `_ops/product-frames/agentic-research.md` и
  `_ops/product-frames/agentic-research.principles.md`.
- Полностью прочитаны три заданных owner-source:
  `_ops/chat-recall/2026-08-29-153512-codex-01a04d13.md`,
  `_ops/chat-recall/2026-08-29-163434-codex-01a04d4a.md` и
  `_ops/chat-recall/2026-08-30-130004-codex-01a051ac.md`.
- Полностью прочитан весь состав `skills/1readable-code/`, существовавший до
  записи этого receipt: `origin.md`, `evidence.md`, `cut.md`; все файлы
  `draft-2026-08-29/`; `recheck-2026-08-30/{intent,authoring-map,
  preservation-map,clean-room-semantic-draft,simple-zero-based}.md`; оба файла
  `reconstructed/`; оба файла exact `candidate/`; два receipt прежнего SHA и
  два исторических review прежнего SHA. Выводы других checker-ов текущего
  minimal-pass не читались.

## Буквальное соответствие принятым решениям

| Требование | Выполняющий фрагмент или наблюдаемый след |
| --- | --- |
| Automatic use при любом writing/changing code | `candidate/SKILL.md:3-5`: `Use before writing or changing code`; trigger не зависит от предварительного признания задачи архитектурной. |
| CTO/architect view будущей системы | `candidate/SKILL.md:12-14,25-28`: назван потерянный future-system view и конечная форма системы. |
| Named practices вместо tutorial | `candidate/SKILL.md:16-18`: три коротких method handle прямо названы уже известными знаниями, а не учебником или обязательной процедурой. |
| Reactive task-focus gap | `candidate/SKILL.md:12-14`: локальный task focus причинно связан с потерей формы системы, цены следующих изменений и CTO/architect view. |
| Полное профессиональное суждение не подменяется одной future-cost метрикой | `candidate/SKILL.md:20-21`: strategic evolvability не вытесняет safety, correctness, performance, compatibility и explicit requirements. |
| Ясная работа без ритуала; material uncertainty не скрыта | `candidate/SKILL.md:29-31`: обе ветви удержаны как outcomes commander’s intent, без отдельной runtime-стадии. |
| Один fresh subagent только после unresolved material strategic uncertainty либо direct owner-request | `candidate/SKILL.md:37-39`: условие стоит после собственного суждения, дизъюнкция едина, число `одного`, свежесть и задача challenge заданы одной boundary. В сочетании с `:29-31` ясная работа не получает вызова. |
| Contract decision остаётся у точного runtime-owner до решения | `candidate/SKILL.md:35-36`: `codebase-design` в Claude либо `1codebase-design` в Codex до решения. Оба installed handle существуют. |
| Русский instructional body, короткий English trigger-only description | Body русский; устойчивые имена методов и runtime handles оставлены как имена. Собранный `description` — 78 символов; `agents/openai.yaml:3` — 35 символов. |
| Commander's intent ведёт умного агента | Уникальный контекст — 438 символов; три законченные зонтичные цели; постоянного workflow нет. |
| Самостоятельные references получают локальные цели только при самостоятельной функции | Candidate references не содержит и не создаёт декоративных стадий. `agents/openai.yaml` — UI metadata, не role/reference-stage. |
| Candidate-only до exact approval | Official shared owner, tracked Claude/Codex и обе live projection имеют прежний SHA `1bcb9e27fd2e355a2b74501063fec476c105bd2423cbefae5ad66438eda5a42a`; новый SHA существует только в candidate history. |
| Не переусложнять process; не обходить active-set дроблением | Нет references, checklist, strongest-objection disposition, same-cost closure, отдельного отчёта или искусственных стадий. |

Снятые `strongest-objection` и `same-cost` строки не считаются потерей:
commander's intent, обычное профессиональное суждение и engineering verification
надёжно выводят их полезное поведение, а прямое owner-решение требует не
переносить authoring/check process в runtime-skill.

## Самостоятельные units exact candidate

### `candidate/SKILL.md` — 19 units в runtime-union

1. Использовать перед написанием кода.
2. Использовать перед изменением кода.
3. Функция вызова — стратегический взгляд на будущую систему.
4. Task focus скрывает форму будущей системы, цену следующих изменений и
   CTO/architect view как один причинный contextual gap.
5. Три named practices — handles уже известного знания, не tutorial и не
   обязательная процедура.
6. Strategic evolvability не вытесняет safety, correctness, performance,
   compatibility и explicit requirements.
7. До программирования подход оценивается одновременно из текущей задачи и
   будущей системы.
8. Ответственность размещена так, чтобы система оставалась цельной.
9. Сложность размещена так, чтобы система оставалась цельной.
10. Вероятная будущая правка остаётся локальной.
11. Вероятная будущая правка остаётся читаемой.
12. Ясная работа не получает дополнительной церемонии.
13. Материальная стратегическая неопределённость не остаётся скрытой.
14. Contract choice/change в Claude до решения передаётся `codebase-design`.
15. Contract choice/change в Codex до решения передаётся `1codebase-design`.
16. Оставшаяся после собственного суждения material strategic uncertainty
    активирует внешний взгляд.
17. Прямой owner-request активирует тот же внешний взгляд.
18. Вызывается ровно один свежий subagent.
19. Subagent оспаривает подход с позиции будущей системы.

Составные формулировки целей не образуют скрытого протокола: это независимо
проверяемые стороны одного конечного состояния, а не последовательные действия.
Альтернативы `writing/changing`, `choice/change`, Claude/Codex и два условия
fresh view задают scope одной границы; они не создают дроблёные стадии.

### `candidate/agents/openai.yaml` — 3 UI units

1. `display_name`.
2. `short_description`.
3. `default_prompt`.

Это не самостоятельный agent-role и не runtime-stage. `default_prompt`
повторяет уже существующий code-trigger, не добавляя нового решения.

### Одновременно активный набор

- Claude: 18 units `SKILL.md`; Codex-specific handle неактивен.
- Codex: 18 units `SKILL.md`; Claude-specific handle неактивен.
- При явном Codex-запуске UI `default_prompt` добавляет одну повторную launch
  instruction; консервативная текстовая верхняя граница — 19, semantic active
  set остаётся 18. В обоих чтениях предел 20 не превышен.

## Hard lines и counterfactual harm

| Hard line | Ближайший разумный default без неё | Конкретный вред |
| --- | --- | --- |
| Automatic trigger до writing/changing code | Обычная правка не выглядит архитектурной и начинает исполняться локально | Сам task focus, который должен исправить skill, не даёт агенту поднять future-system lens. |
| Strategic evolvability не подменяет safety/correctness/performance/compatibility/requirements | Future-change lens читается как единственная метрика решения | Обязательная безопасность, корректность или совместимость может быть ослаблена только потому, что не удешевляет следующую правку. |
| Runtime-owner contract choice/change до решения | Общий readability prior сам выбирает seam/interface | `1readable-code` присваивает чужую функцию, а два semantic owner-а порождают расходящиеся контракты. |
| Один fresh subagent после unresolved material uncertainty либо direct request | Собственный подход кажется достаточным; без точного порога reviewer либо не вызывается, либо вызывается на каждой ясной правке | В первой ветке скрытая будущая связность остаётся в self-confirming frame; во второй растут latency, контекст и размывание ответственности. |

Других hard lines, procedures, references или stages candidate не добавляет.

## Ближайшие правдоподобные неверные разборы

- `before writing or changing code` не означает read-only explanation/review:
  наблюдаемый trigger — предстоящая запись или правка кода.
- Runtime names не требуют оба design-skill одновременно: `в Claude` и
  `в Codex` — взаимоисключающие runtime qualifiers.
- Два условия fresh view не создают два вызова: они соединены одним `или` и
  управляют одним объектом `одного свежего субагента`.
- `попроси ... оспорить` не требует обязательного принятия любого возражения и
  не возвращает снятую disposition-stage; обычное профессиональное суждение
  различает обоснованное возражение и опровергнутую гипотезу.
- Goals про пропорциональность не требуют письменного анализа или отчёта:
  candidate не задаёт такого trace, а ясную работу прямо освобождает от
  дополнительной церемонии.

## Links, language и structural checks

- Внутренних Markdown-ссылок и ссылок на references нет.
- Оба runtime handle существуют:
  `/Users/triton/.claude/skills/codebase-design/SKILL.md` и
  `/Users/triton/.codex/skills/1codebase-design/SKILL.md`.
- Frontmatter и `candidate/agents/openai.yaml` разбираются как YAML.
- Самостоятельных role/reference-файлов нет; UI YAML самодостаточен как
  интерфейсная metadata и не требует чтения другого файла для выполнения
  отдельного режима.

## Findings

**Находок нет.**

## Внешние gaps, не дефекты текста

- Routing use/skip/near-miss ещё не выполнен на exact SHA
  `6aa4ec3785d3c57d2cec142c92e4541dc52e114225661f9c5ffee7382e9496c7`.
- Реалистичный clean-run exact SHA ещё не проверил обе главные ветви:
  ясную работу без ritual/subagent и material uncertainty либо direct request
  с ровно одним fresh subagent.
- Поэтому этот receipt не является approval или installation evidence;
  candidate-only gate остаётся закрытым.
