# Evidence — 1context-refactor

2026-08-26, рождение при раскройке пары. Проверено:

- два независимых Opus-окна: линза «лишнее» (счёт обязанностей, дубли,
  пересечения триггеров) и линза «потерянное/выдуманное» (построчный diff
  против пары, проверка absorbed-вердиктов цитатами, лимиты, ссылки);
- приёмка оркестратора: собственный пересчёт обязанностей (метод: Контекст и
  Завершение считаются), descriptions ≤200, строки-аннотации ≤200, разрешение
  всех cross-ссылок в installed-раскладке скриптом;
- полный отчёт обеих линз и применённые вердикты — снимок
  `_workspace/skill-split-5/map.md` на дату рождения.

Candidate (не проверено поведенчески): срабатывание триггера в живой задаче и
различие решения против прогона без скила. Проверяется первым реальным
использованием; до того пакет — принятая структура, не доказанное поведение.

2026-08-26, поздний вечер, переделка по словам владельца (#L21–#L23): своё
независимое Opus-окно (потери против прежнего тела, верность словам построчно,
швы семьи и внешних соседей, механика); блокирующие находки применены до
установки, каскад переименования — одной операцией со снятием прежнего пакета.

## 2026-08-29 — postfactum refactor и установка

Owner evidence:
`_ops/chat-recall/2026-08-29-205016-codex-01a04e33.md:22,23`.

| Что | Evidence | Статус |
| --- | --- | --- |
| Exact candidate до owner/live | `candidate-2026-08-29/`; tracked owner оставался без diff до gate | pass |
| Независимый instruction acceptance | active sets: causal 19, preservation 20, refactor 17, coherence 16, simplify 19, audit 20, check 18 | pass |
| Независимый trajectory review | causal trace требует exact anchors; outputs условны; автоматический trigger не расширяет write-authority | pass |
| Trigger surfaces | frontmatter 116 символов; Codex short_description 105; обе English trigger-only `Use after…` | pass |
| Causal fixture | `_workspace/1context-refactor-probe-2026-08-29/RESULT.md`; две causal cards, INDEX-route, одна сырая finding-строка и owner-speech advice | causal pass |
| Falsifying fixture | old/new INDEX comparator меняет следующий ход с полного поиска на точный owner-раздел | structural pass; probabilistic effect candidate |
| Установка | tracked owner → Codex/Claude tracked projections → `~/.codex/skills/1context-refactor` и `~/.claude/skills/1context-refactor` | pass |
| Validator и parity | `quick_validate.py` для owner и четырёх projections; `sync_simple_projections.py --check`; tracked/live directory diff | pass |
| Markdown edges | семь связей body→reference прочитаны с обеих сторон; labels совпали с локальными Целями | semantic edge review pass for package scope |

Residual risk: automatic routing и повторяемый behavioral effect ещё не
измерены серией cold-session прогонов; один fixture доказывает causal форму и
возможность различающего structural route, но не частоту улучшения.
