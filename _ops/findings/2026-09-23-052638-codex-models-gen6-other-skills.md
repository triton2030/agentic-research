После перевода ярусов Codex на `gpt-6-luna` / `gpt-6-sol` / `gpt-6-astra` (владелец 2026-09-23, `_ops/chat-recall/2026-09-23-051553-claude-483a304e.md#recall-9805fef9e16041928ddf6a675d7d952d`) обновлены только мост `experiments/codex-bridge` и скил `1codex`. Модели 5.6 по-прежнему прописаны как рабочий выбор в других живых местах (наблюдение `git grep`, 2026-09-23):

- `skills/shared/1-max-review/portable/scripts/max_review.py:26` (`MODEL = "gpt-5.6-luna"`) и `portable/SKILL.md:40`;
- `skills/shared/1folder-tree/portable/scripts/check_tree.py:16` (`MODEL = "gpt-5.6-sol"`) и `portable/SKILL.md:176`;
- `skills/codex/1orchestration/SKILL.md:43,45` (luna max / sol);
- `experiments/1design-review/scripts/design-review:28,50` и `run-clean-design-agent.sh:17,32` (дефолт `gpt-5.6-sol`);
- `experiments/graphiti-codex/src/graphiti_codex/codex_llm.py:22` и README (`gpt-5.6-luna`).
- `md-scout` из `1codex/references/delegate.md` работает на `gpt-5.6-terra`, а `/Users/triton/Documents/My_projects/md-tools/scripts/run_md_scout.py:78` отвергает любую модель не из семейства `gpt-5.6` — переход на 6 там потребует правки кода (нашёл проверяющий тройки 1skill-creation).

Не проверено, распространяется ли слово владельца на эти скилы и нет ли у них своих причин держать 5.6. Модели 5.6 в каталоге движка ещё есть, так что сейчас ничего не ломается.
