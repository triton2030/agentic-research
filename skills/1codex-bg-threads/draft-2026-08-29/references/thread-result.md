# Результат треда

## Цель

Дать root проверяемый semantic result, который можно разрешить против live
state и artifacts; self-report не назначает себе success.

Открывай при terminal, failed или needs-input состоянии:

```text
THREAD_DONE
status: candidate|blocked|failed
outcome: <result or bounded partial result>
artifacts: <addressable durable paths/refs|none>
evidence: <support for outcome|none + reason>
checks: <check + observed result|not-run + reason>
gaps: <unresolved facts and risks|none>
needs: <exact root/main or user action|none>
retained: <source_basis; same|delta-ingested|reingested|unknown; coverage;
  blocked claims|omit for bounded thread>
```

- `candidate` просит внешнюю acceptance.
- Mutable artifact автора требует verification slot в `1orchestration`.
- Проверяющий не может быть автором mutable artifact.
- Проверяющий доказывает каждый `done_when` до acceptance.
- Root сверяет packet с карточкой, live state, artifact и checks.
- Убедительный текст без этих опор остаётся unresolved.
