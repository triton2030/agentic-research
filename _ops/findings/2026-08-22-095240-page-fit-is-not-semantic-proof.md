---
kind: finding
status: open
scope: cross-project derived knowledge
---

# Page-fit self-report не доказывает смысл

Writer может назначить близкую по теме запись странице, повторить её H1 в
`page_fit` и пройти structural validation, хотя запись не отвечает на этот
вопрос. Поэтому page-fit остаётся объектом независимого semantic audit, а не
машинным verdict.

Дешёвый mechanical gate всё же полезен: каждая запись со статусом `used` должна
поддерживать хотя бы один material claim. Он отсекает формальное coverage без
claim-ответственности, но не заменяет чтение источника независимым агентом.
