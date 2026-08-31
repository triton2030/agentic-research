# Mantine: version delta

## Вход

При version uncertainty получай неизменный self-contained `{packet, cohort}`
только после exact cohort; при `cohort: unknown` немедленно верни `unknown` и не
выбирай version-sensitive API. Проверяй official release index и migration guides
за последние 12 месяцев против installed public types этой cohort; без
доказуемых types верни `unknown`.

## Выход

Верни неизменный self-contained `{packet, cohort, result}`:

- `result = {delta, official_address, summary}` при применимой подтверждённой
  дельте;
- `result = none` при подтверждённом отсутствии применимой дельты;
- `result = unknown` при недоказуемости.

В joint route передай этот result вместе с теми же packet и cohort в audit; не
выбирай version-sensitive API из `unknown`.
