# Behavioral probe — round 1

## Input

«Используй фоновые треды, чтобы провести крупный рефактор сервиса: API,
миграции и документация лежат в раздельных файлах, но два исполнителя могут
затронуть один schema-файл; есть одна материальная архитектурная развилка. Я
хочу экономить токены».

## Фактическая траектория чистого исполнителя

1. Root выбрал роль технического директора и оставил себе бизнес-приоритет,
   архитектурное решение, integration и acceptance.
2. Архитектурный анализ ушёл в новый bounded Sol/xhigh read-only thread; API,
   migrations и docs — в Luna/max threads.
3. Потенциальный schema-overlap снят single-writer: migration-thread пишет
   schema, API-thread возвращает proposal и не пишет этот файл; все работают
   Local.
4. После принятого архитектурного анализа API и migrations запускаются
   параллельно; docs — после integration поведения.
5. Каждый mutable writer получил отдельный Luna/max read-only verifier.
6. Controller выбрал event wait, разрешил каждый `THREAD_DONE` против карточки,
   artifacts и checks, затем потребовал archive всех bounded threads.

## Наблюдаемые расхождения

- Draft позволял прочитать verification как обязательный для любого outcome
  либо только для durable writer; исполнитель выбрал второй вариант.
- Draft жёстко назначил Sol/xhigh любой материальной архитектурной развилке,
  хотя владелец разрешил medium либо xhigh по реальной сложности.
- Draft не говорил, может ли один verifier последовательно покрыть несколько
  mutable outcomes; исполнитель создал отдельный slot на каждый outcome.

## Решение round 1

- Verification теперь явно привязан к mutable author и каждому его
  `done_when`; один verifier может выполнять несколько независимых slots
  последовательно, если он не автор и контекст остаётся посильным по
  `1orchestration`.
- Sol medium/xhigh выбирается по сложности, неопределённости и риску, а не по
  названию архитектурной категории.
