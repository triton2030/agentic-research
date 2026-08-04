---
description: "Seeded, bounded discovery of absent semantic edges without turning retrieval into a completeness claim."
---

# Missing Edge Discovery

## Boundary

Существующие edges образуют перечислимый closed set только в названном scope.
Отсутствующие edges — open-world: свободный поиск «чего не хватает» не имеет
denominator и не может закончиться честным verdict о полноте.

Открывай этот route, когда уже есть конкретный seed и отсутствие связи может
изменить owner attribution, propagation, evidence или reader behavior.

## Valid Seeds

- изменяемый owner claim или section predicate;
- стабильный Rule/FR/decision/domain ID;
- local owner key, registry entry или contract marker;
- конкретный consumer behavior, который использует upstream meaning;
- прочитанный holder с неатрибутированным или противоречивым утверждением.

Topic, имя файла и общий вопрос «что ещё связано» seed не создают.

Seed выбирает retrieval, но не доказывает missing relation. Наличие marker-а,
locator-а или direct-read consumer-а само по себе не создаёт prose link или hard
dependency.

## Bounded Route

1. **Назови искомый relation.** Что должен делать missing edge:
   `authority`, `application`, `support`, `provenance`, `navigation` или
   `hard invalidation`.
2. **Зафиксируй scope.** Corpus root, path filters, exclusions, consumer types и
   seeds. Если scope нельзя перечислить, назови его open remainder до поиска.
3. **Используй дешёвые каналы по порядку достаточности:**
   - exact IDs, terms и refs через `1cli-tools`;
   - known-folder map и selected bodies через `1md-read`;
   - declared reverse graph;
   - paraphrase candidates через `1md-search`, только когда exact vocabulary не
     покрывает вероятных consumers.
4. **Прочитай selected bodies.** Search row, snippet, score или совпадение
   термина — candidate. `missing` возникает только после X/Y attribution test из
   [`semantic-edge-audit.md`](semantic-edge-audit.md).
5. **Отдели отсутствие edge от отсутствия необходимости.** Не каждый mention
   требует link. Edge нужен, только если без него теряется addressable owner,
   проверяемая support/provenance job, reader path или propagation obligation.
6. **Проверь local graph contract.** Для hard invalidation нужны пройденный X/Y
   test, разрешённая relation class и допустимый serialized endpoint. Если
   dialect не прочитан, mutation остаётся `unread`.
7. **Запиши disposition candidate:** `missing`, если edge нужен и отсутствует;
   `not-required`, `already-covered`, `conflict` или `unread` в остальных
   случаях.

Не добавляй edge автоматически: `missing` — semantic verdict; edit требует
current write scope и local metadata/link contract. Не создавай locator только
ради graph edge.

## Retrieval Limits

- Empty exact search означает отсутствие exact match в фактическом scope.
- Empty semantic search означает `no candidate in this probe`.
- Similarity не определяет owner, relation job или direction.
- Query rewrite допустим один раз, если первый результат оказался source echo.
- Несколько каналов уменьшают неизвестность, но не превращают open-world в
  closed set.

Если completeness material, сначала создай конечную cohort: список owner keys,
consumer types или files. Без неё остановись с named remainder.

## Output And Stop

Верни:

```text
seeds:
relation sought:
corpus and exclusions:
channels executed:
candidates selected/read:
missing verdicts with X/Y:
conflicts/unread:
unsearched remainder:
```

Стоп после bounded probes и прочитанных candidate verdicts. Допустимый вывод:
`no missing edge found in these probes`; недопустимый — `no missing edges`.
