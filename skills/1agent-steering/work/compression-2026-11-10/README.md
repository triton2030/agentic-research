# Сжатие трёх скилов и снятие конфликтов — 2026-11-10

Полная переработка `1agent-steering`, `1skill-creation` и `1instruction-authoring`
как одной системы. Снимки: [`1agent-steering` installed-2026-11-10-v2](../../versions/installed-2026-11-10-v2/SKILL.md),
[`1skill-creation` v23](../../../1skill-creation/versions/v23/portable/SKILL.md),
[`1instruction-authoring` v22](../../../1instruction-authoring/versions/v22/portable/SKILL.md).
Сессия Claude Code `4ab2091c-fb00-4f6d-beaf-4c58eff3642c`.

## Заказ и решения владельца

- Заказ: «можно создать зонтичные… инструкции… сейчас по количеству символов
  токенов и объяснений как будто у нас перебор. И важно, чтобы инструкции ещё
  логически не тянули в разные стороны».
- Рецензия Fable 5.2 `medium` — по просьбе владельца.
- «Да, переписывай» — на набросок v2 с двумя рекомендациями: мысленная проба
  «что сделал бы исполнитель без строки» остаётся, P-009 снимает только
  прогоны (К8); проверка субагентами в `1instruction-authoring` — только
  предложением в конце (П4).

## Что сделано

- Наука: 17 разделов → пять частей (Намерение · Дельта · Момент · Вес ·
  Поручение), пять проб — в `SKILL.md`, лестница починки, разговор
  с исполнителем после поручения.
- Носители: снят пересказ науки; внесены пункты разбора `1skill-creation`
  H1–H7 с поправками Fable к H2 и H4.
- `1orchestration` (Claude): указатель переведён с «Декомпозиции»
  и «Автономного продолжения» на «Поручение».
- Объём и всё снятое — [loss-map.md](loss-map.md).

## Материалы

- [conflict-map.md](conflict-map.md) — 9 конфликтов и незаданная мера, цитаты
  сверены `check_quotes.py`; адреса строк — до переписывания.
- [review-fable.md](review-fable.md) — рецензия; принято почти всё, кроме
  переноса знаний о steer/queue в `1orchestration` — это осталось в `1t3`.
- [compression-sketch-v2.md](compression-sketch-v2.md), [skill-creation-audit.md](skill-creation-audit.md),
  [sources-agent-conversation.md](sources-agent-conversation.md).

## Проверка

Сноски науки сверены: у каждой ссылки есть определение. Установка в Claude
и Codex сверена `--check`. Проб и проверяющих после переписывания не было:
поведение не проверено.
