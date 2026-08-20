---
description: "Датированный evidence snapshot о неоднозначности, числе правил, порядке и проверке формулировок для skills и instruction files."
---

# Instruction Wording And Adherence — Research 2026-08

Срез источников на 20 августа 2026. Использовать при создании и аудите skills,
system prompts, `AGENTS.md` и заданий субагентам. Это evidence snapshot, не новый
portable-канон и не обещание, что хорошая проза сама обеспечит соблюдение.

Полной инженерией соблюдения — delivery, runtime, affordances, observable gates
и проверкой действий — владеет
[`science/how-to-make-llm-obey.md`](../../../science/how-to-make-llm-obey.md).
Этот файл отвечает на более узкий вопрос: **как сформулировать правило, когда
текст уже выбран правильным носителем**.

## Ответ В Одной Фразе

Пиши не «как для дебила», а **для умного нового сотрудника без твоего
контекста**: минимально достаточно, без лишних активных обязательств, с одним
операционным прочтением и наблюдаемым результатом.

Рабочая формула:

> минимально достаточная подробность + нулевая устранимая неоднозначность +
> проверяемый результат

Краткость не равна примитивности. Подробность не равна надёжности. Полезна та
строка, которая меняет selection, action, boundary, priority, evidence или
completion и не требует от свежей сессии додумывать локальную конвенцию.

## Требование Владельца

Свежая сессия, впервые увидевшая skill или instruction file, должна восстановить
то же действие, scope и условие, которые имел в виду автор. Неоднозначную строку
следует переформулировать, а не страховать ещё одной строкой рядом.

Sources:

- owner criterion и решение об audit:
  [`2026-08-20-222653-claude-93d2bd06.md`](../../../_ops/chat-recall/2026-08-20-222653-claude-93d2bd06.md);
- owner criterion о силе малого числа инструкций:
  [`2026-08-15-134233-codex-01a00494.md`](../../../_ops/chat-recall/2026-08-15-134233-codex-01a00494.md);
- решение сохранить этот срез как knowledge-файл:
  [`2026-08-20-224519-codex-01a02038.md`](../../../_ops/chat-recall/2026-08-20-224519-codex-01a02038.md).

## Что Достаточно Хорошо Подтверждено

### Число Одновременно Активных Правил Имеет Цену

- ManyIFEval и StyleMBPP на десяти моделях показали последовательное ухудшение
  по мере роста числа одновременных инструкций: до десяти для текста и до шести
  для кода. Это рецензированное evidence 2025 года, но не замер текущего рабочего
  model set.
- FollowBench добавляет ограничения по одному и проверяет каждое ограничение
  отдельно, а не только общее качество ответа; авторы показывают слабые места
  instruction following. Это рецензированное evidence на 13 моделях поколения
  2024.
- Свежий Instruction Stacking Collapse измерил 24 verifier-checked правила на
  трёх моделях: follow rate упал примерно с 96% при одном правиле до 20–60% при
  двадцати; значимую часть деградации объясняют воспроизводимые попарные
  конфликты. Это сильный по эффекту, но пока нерецензированный препринт на одной
  синтетической постановке.
- VeyraBench получил нулевой perfect-response rate к 80 правилам у всех пяти
  моделей независимо от четырёх форматов и placement. Это соло-препринт на
  синтетическом корпусе: полезен как falsifier идеи «правильный Markdown всё
  спасёт», но не как точный production threshold.

**Authoring consequence:** считать не символы, а активные обязательства и их
конфликты. Новую строку принимать только если она закрывает отдельный failure
mode; при конфликте удалять или сливать старое правило, а не добавлять третье.

### Неоднозначность Реальна, Но У Неё Нет Магического Антонима

- Prompt underspecification в zero/few-shot classification даёт более высокую
  variance, чем prompts с конкретными task-инструкциями. Это препринт и узкий
  task class, но он поддерживает устранение недосказанного scope и output space.
- В few-shot экспериментах ICLR 2024 смыслосохраняющие изменения форматирования
  меняли accuracy до 76 п.п. на LLaMA-2-13B; порядок форматов слабо переносился
  между моделями. Это доказывает чувствительность, но не превосходство Markdown,
  XML, таблиц или plain text вообще.
- Anthropic рекомендует мыслить о Claude как об очень способном новичке без
  знания локальных норм: явно задавать желаемый результат, формат и constraints,
  а шаги нумеровать только когда важны порядок или полнота.
- OpenAI для GPT-5.6 рекомендует outcome-focused prompt: goal, relevant context,
  constraints, required evidence, success criteria и output format; routing
  instructions должны быть task-specific, а не общими лозунгами.

**Authoring consequence:** недвусмысленность — не многословие, а один допустимый
операционный разбор. Свежий читатель должен одинаково назвать:

- кто и когда действует;
- какое действие выполняет над каким объектом;
- где scope заканчивается;
- что важнее при конфликте;
- какой след доказывает completion.

Если один из ответов приходится угадывать, строка недоопределена. Если ответы
однозначны и без пояснения, добавлять пояснение не надо.

### Порядок Влияет, Но Универсального Порядка Не Найдено

- Рецензированная работа Order Matters обнаружила преимущество порядка
  hard-to-easy в своей multi-constraint постановке.
- Lost in the Middle показал ухудшение доступа к релевантной информации в
  середине длинного контекста.
- Прямой факторный препринт по coding-agent configuration files не нашёл
  различимого эффекта size, position, flat/nested architecture или adjacent
  conflict в 1 650 Claude Code sessions. Самый крупный эффект был внутри
  траектории: odds соблюдения снижались примерно на 5,6% с каждой следующей
  сгенерированной функцией в исследованном диапазоне; эффект был нелинейным.
- VeyraBench не подтвердил заранее заданный универсальный рейтинг форматов;
  направление placement-эффекта зависело от модели.

**Authoring consequence:** не превращать «важное в начало», «hard-to-easy» или
«повтори в конце» в универсальный закон. Критическое правило ставить рядом с
условием и точкой действия, а placement проверять на target model и реальной
траектории.

### Хорошая Формулировка Не Равна Соблюдению

- The Compliance Gap получил 0% process compliance при словесном согласии
  моделей, 0–4% для непроверяемых требований и 97% производства audit trail;
  удаление affordance делегирования подняло compliance примерно до 75% без
  изменения формулировки. Это крупный, но соло-препринт без независимой
  репликации; он показывает границу prompt-only управления, а не универсальные
  production rates.
- DeCRIM на real-world multi-constraint queries показал, что даже GPT-4 нарушал
  хотя бы одно ограничение более чем в 21% запросов; явное разложение constraints,
  critique и refine улучшило открытые модели. Это рецензированное evidence 2024
  года, не прямое доказательство для текущих reasoning-моделей.
- Evaluating AGENTS.md не нашёл общего роста task success от context files и
  получил более 20% дополнительной inference cost; нестандартные инструкции
  соблюдались, а repository overviews не помогали. Это препринт: полезен против
  memory-dump, но не против узких локальных конвенций.
- Anthropic сообщает, что удалил более 80% Claude Code system prompt для Opus 5
  и Fable 5 без измеримой потери на собственных coding evals; причиной пересмотра
  были overconstraint и конфликты между system prompt, skills и `CLAUDE.md`.
  Это актуальный vendor report, не опубликованный факторный эксперимент.

**Authoring consequence:** текстом удерживать предпочтения и локальные
конвенции. Инварианты закрывать permission, schema, validator, hook, test или
другим наблюдаемым gate. «Я прочитал», «я учёл» и красивый финальный отчёт не
доказывают действие.

## Практический Контракт Формулировки

Ни один пункт ниже не изолирован отдельной абляцией. Это локальный инженерный
вывод из набора evidence и owner criteria, который следует проверять как
intervention, а не принимать за универсальный закон.

### Оставить

- Один конкретный глагол и один объект действия на clause.
- Condition непосредственно перед command: `если X — сделай Y`.
- Точный scope, особенно для `always`, `never`, `all`, `only` и исключений.
- Явный priority только там, где два хороших правила реально сталкиваются.
- Позитивное целевое действие для constructive behavior.
- Запрет для настоящей safety/scope boundary; при возможности рядом назвать
  безопасную замену.
- Rationale только если без него свежая сессия выберет неверную ветку или не
  сможет перенести правило на новый случай.
- Observable artifact или test для обязательного поведения.

### Удалить Или Вынести

- Повтор одной нормы другими словами.
- Лозунги вроде «будь качественным», «думай глубоко», «действуй разумно» без
  decision standard или операции.
- Сведения, которые не меняют действие в момент trigger.
- Длинный обзор системы вместо точного owner pointer.
- Примеры «на всякий случай»; оставлять edge case, неочевидный формат или
  измеренный failure mode.
- Rare detail из active core; загружать его через progressive disclosure.
- Пошаговый ritual, если корректность не зависит от порядка.

## Минимальная Форма

Это не обязательные headings, а диагностическая раскладка смысла:

```text
Outcome: что должно стать истинным.
Action: что именно сделать.
Condition/scope: когда действует правило и где заканчивается.
Priority/boundary: что побеждает при настоящем конфликте.
Evidence: какой наблюдаемый след доказывает результат.
Stop: когда не продолжать и не расширять работу.
```

Пустой или общеизвестный элемент не добавляется. Несколько элементов можно
сжать в одну строку, если после сжатия остаётся один операционный разбор.

## Fresh-Window Audit

Предлагаемый локальный acceptance method: проверять candidate строку без
исходного разговора автора.

1. Независимый читатель выписывает `condition → action → object → boundary →
   evidence` только из текста.
2. Он называет ближайший правдоподобный неверный разбор.
3. Если неверный разбор допускается грамматикой, строку переписывают; соседнее
   пояснение не добавляют по умолчанию.
4. Каждую clause удаляют мысленно: если selection, action, boundary, evidence
   или completion не меняются, clause — кандидат на удаление.
5. Считают одновременно активные обязательства и попарные конфликты, а не
   символы файла.
6. Для материального claim запускают matched holdout: одинаковые task, model,
   settings и context; сравнивают minimal wording с candidate wording.
7. Мерят joint pass rate и каждый constraint отдельно. Один удачный output
   доказывает возможность, но не повышение надёжности.

## Чего Исследования Не Доказали

- Нет универсального character cap или безопасного числа правил для любого
  agent/runtime.
- Нет универсального победителя между Markdown, XML, таблицей, bullets и prose.
- Нет доказательства, что вежливость, капслок, `IMPORTANT` или persona сами по
  себе повышают adherence.
- Нет доказательства, что любой запрет хуже позитивной команды: hard boundary
  остаётся нормальным применением отрицания.
- Нет доказательства, что подробная инструкция всегда лучше короткой или
  короткая всегда лучше подробной.
- Нет прямого переноса старых benchmark numbers на GPT-5.6, Claude Opus 5 и
  Claude Fable 5 без matched eval.
- Vendor guidance описывает рабочий baseline провайдера, но не заменяет
  причинный эксперимент.

## Source Ledger

### Прямые Исследования

- [Instruction Stacking Collapse](https://arxiv.org/abs/2608.02639) — число
  правил и попарные конфликты; препринт, 2026.
- [When Instructions Multiply / ManyIFEval](https://aclanthology.org/2025.findings-emnlp.896/)
  — рост числа инструкций; EMNLP Findings 2025.
- [FollowBench](https://aclanthology.org/2024.acl-long.257/) — инкрементальные
  fine-grained constraints; ACL 2024.
- [Order Matters](https://aclanthology.org/2025.findings-acl.646/) — position
  bias и hard-to-easy; ACL Findings 2025.
- [DeCRIM / RealInstruct](https://aclanthology.org/2024.findings-emnlp.458/) —
  реальный multi-constraint adherence и correction; EMNLP Findings 2024.
- [Prompt formatting sensitivity](https://proceedings.iclr.cc/paper_files/paper/2024/hash/6c0e99d736da621403018ca7b32b1a4d-Abstract-Conference.html)
  — смыслосохраняющие форматы и variance; ICLR 2024.
- [Lost in the Middle](https://aclanthology.org/2024.tacl-1.9/) — позиция
  релевантной информации в длинном контексте; TACL 2024.
- [Instruction Adherence in Coding Agent Configuration Files](https://arxiv.org/abs/2605.10039)
  — size, position, architecture, conflicts и trajectory drift; препринт, 2026.
- [Evaluating AGENTS.md](https://arxiv.org/abs/2602.11988) — task success и
  cost repository context files; препринт v2, 2026.
- [Prompt Design at Scale / VeyraBench](https://arxiv.org/abs/2607.19257) —
  formats, rule count, placement и context length; соло-препринт, 2026.
- [Prompt underspecification](https://arxiv.org/abs/2602.04297) — конкретность
  task-инструкции и sensitivity в classification; препринт, 2026.
- [The Compliance Gap](https://arxiv.org/abs/2605.01771) — process compliance,
  affordances и audit trail; соло-препринт, 2026.

### Актуальная Практика Провайдеров

- [OpenAI GPT-5.6 model guidance](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-5.6#prompting-best-practices)
  — outcome-focused prompt и task-specific routing.
- [Anthropic prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
  — clear/direct wording, context, constraints, examples и order-sensitive steps.
- [Anthropic: context engineering for Claude 5](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models)
  — pruning, overconstraint и progressive disclosure для Claude 5.

## Downstream Owners

Этот файл владеет только датированным evidence snapshot о wording.

- Полная инженерия соблюдения:
  [`science/how-to-make-llm-obey.md`](../../../science/how-to-make-llm-obey.md).
- Portable skill authoring truth: [`authoring-canon.md`](authoring-canon.md).
- System prompt guide:
  [`perfect-system-prompts.md`](../../guides/perfect-system-prompts.md).
- Runtime shaping и approval:
  [`1skill-shaping`](../../../skills/shared/1skill-shaping/portable/SKILL.md) и
  [`1instruction-shaping`](../../../skills/shared/1instruction-shaping/portable/SKILL.md).
- Promotion в канон или runtime skill: отдельное решение, cognitive audit и
  behavioral proof на рабочем model set.
