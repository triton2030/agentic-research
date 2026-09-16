# Структурная проверка

2026-09-16, кандидат после текстовой правки.

- TOML разобран Python tomllib; sandbox_mode read-only сохранён.
- YAML разобран PyYAML 6.0.3; disable-model-invocation true в обеих версиях,
  Codex allow_implicit_invocation false, description 157 символов.
- SKILL.md двух runtime совпадают; тело Claude-роли совпадает с Codex
  developer_instructions. Платформенные оболочки сохранены отдельно.
- rumdl: no issues для двух SKILL.md и Claude role.
- git diff --check: без ошибок.
- Все 28 дословных записей в review.md сверены с текущими строками источников.
- qv-skill отклонил поле disable-model-invocation: его список допустимых ключей
  устарел относительно платформенной документации. Поле было в исходной
  версии и необходимо для решения владельца. Это не pass qv-skill;
  платформа поддерживает поле, что проверено по официальным docs.

Проверки доставки выполняются после независимой проверки.

До установки live SKILL и зарегистрированные роли совпадают со снимками owner.
Исключение: bundled Claude role заменяла `1product-shaping` на `1docs-write,
1goal`. Новая роль снимает весь routing-перечень, сохраняя семантическую границу
планирования реализации. Отличавшаяся копия сохранена в
[live-claude-role-before.md](live-claude-role-before.md).

## Доставка

`sync_simple_projections.py 1business-growth-analysis --write --install`:
обе установленные проекции совпадают с owners. Зарегистрированные агенты
доставлены отдельным копированием и побайтно сверены:

- codex registered agent: `d51fc692e1f027268ead82eab1775c064685c8cf29870e506caa47d7c79d5a80`
- claude registered agent: `2b0899fa0474a6d7f74418a4a9dbdc3a516ef0604b7b82c23da58379f15fff44`

Внутренние ссылки новых материалов разрешаются; финальные тела ролей и скилов
между средами совпадают. Снимки доставленных runtime-пакетов сохранены в
`versions/installed-2026-09-16-{codex,claude}/`. Действующие сессии могут держать
старый загруженный каталог; end-to-end нового named launch не заявляется.
