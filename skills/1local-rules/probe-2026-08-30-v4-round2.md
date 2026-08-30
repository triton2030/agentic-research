# Реалистичная проба v4 · раунд 2

Чистый исполнитель подтвердил SHA-256 переданных bytes:
`9f95956c832c3066fe1e5b72304362ddcfc9863a9e26e8cb7fa53d9e4d1f21ac`.
Он не читал history и выводы checker-ов и не выполнял реальные записи.

## Trigger checks

- Use: «Сделай обычный skill локальным `2*` для этого проекта сразу в Claude и
  Codex» → `1local-rules`.
- Skip: «Создай обычный глобальный skill для всех проектов» → только
  `$1skill-creation`.
- Near-miss: «Обнови приватный Claude-only skill этого проекта» → skip;
  намерение одновременно для Claude и Codex отсутствует.

## Update trace

Исполнитель разрешил owner, обе проекции и общую поверхность Atlas, передал
четыре локальных ограничения `$1skill-creation` и остановил все writes до
точного утверждения. После условного утверждения он связал его с точными bytes,
проверил candidate против Claude/Codex/root security instructions, выбрал одну
owner→projections установку и сформировал conditional-квитанцию с topology,
approval, conflict и recursive hashes. Codex `agents/openai.yaml` сохранил как
явно runtime-owned metadata вне общей поверхности.

## Retire trace

Исполнитель не перенёс authority update-а на снятие. Он потребовал отдельное
точное утверждение состояния отсутствия до удаления, не применял content-
conflict gate и сформировал ветку квитанции с тремя адресами и отрицательными
existence checks.

## Непроверенное

Проба не читала реальные Atlas-файлы, не получила реальный approval и не
запускала sync или delete. Поэтому она доказывает routing и фактическую
траекторию exact candidate, но не будущие conflict/parity/absence outcomes.
