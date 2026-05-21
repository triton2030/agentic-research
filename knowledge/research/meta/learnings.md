# Meta — Learnings

Снимок после cleanup 18 мая 2026.

Здесь только staging/source-backed выводы про управление агентной системой:
память, eval, аудит, ролевой дизайн и продвижение знаний. Уже повышенные
принципы живут в `knowledge/agents/` и не дублируются здесь.

## Проверено

- Memory skill нельзя проектировать как прямую автозапись из чата. Более
  безопасная форма: `candidate -> policy/merge -> committed`.
- Для memory activation нужен гибрид: явная команда пользователя,
  детерминированные правила/hooks и вероятностная классификация с threshold и
  ambiguity margin.
- Memory-систему полезно делить по scope и типу: `turn`, `session`, `user`,
  `project`, `org`; `semantic`, `episodic`, `procedural`.
- Конфликты памяти требуют явного precedence: deny и запрет пользователя выше
  всего; новые явные указания сильнее старых inferred facts.
- Append-only журнал с `supersedes`, audit и trace correlation надёжнее
  перезаписи одного состояния.
- Качество памяти нужно мерить раздельно: activation quality, extraction
  quality и commit quality.
- PII, secrets и regulated data не должны auto-commit'иться; нужен confirm или
  deny path.
- Retention policy должна защищать long-tail knowledge: частотное вытеснение
  опасно для редких, но критичных фактов.
- Curator-паттерн: отдельный этап извлечения learnings после задачи и
  injection в следующий запуск.

## Promotion Rule

- Пока вывод не начал повторно влиять на решения в нескольких сессиях или
  линиях, ему место здесь.
- Когда вывод стал правилом по умолчанию, owner становится `wisdom-*`,
  `guides/`, `AGENTS.md` или criteria layer.
- При продвижении удалить или заменить staging-пункт, чтобы research не стал
  вторым каноном.

## Promoted

- Agent roles, role separation -> `knowledge/agents/multi-agent.md`.
- Trajectory audit, observable acceptance criteria, multi-channel audit
  -> `knowledge/agents/evaluation.md`.
- Полная retention vs structured forgetting -> `knowledge/agents/memory.md`.
- User corrections как сильный memory signal -> `knowledge/agents/memory.md`.
- Learnings quality gate -> `knowledge/agents/memory.md`.
- Dedup / contradiction discipline -> `knowledge/agents/memory.md`.

## Рабочие Гипотезы

- Для meta-линии полезнее мыслить цепочкой `цель -> границы -> исполнение ->
  evidence -> audit`, а не “усилить prompt”.
- `meta-thinking` должен оставаться лёгким reframe-слоем, а не обязательным
  тяжёлым ритуалом.
- Для memory-линии перспективна композиция узких маршрутов: явная запись,
  удаление, preference extraction, strategic signals, summary-only и confirm
  path.
