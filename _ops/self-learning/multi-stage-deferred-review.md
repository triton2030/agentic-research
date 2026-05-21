# Multi-stage deferred review

## Observation

Multi-stage план (A → B → C) формирует cognitive frame «один план — один closeout в конце», и модель откладывает `1work-review` до финального step. Каждая stage производит substantive writes на sensitive surfaces, cumulative file count растёт незаметно. Stop hook ловит в момент когда уже два-три ход подряд без review случились.

Корень: момент когда писать review не triggered размером diff'а или количеством файлов одного хода, а **surface'ом** (cross-project blast → review). При forward-momentum frame этот trigger выпадает из внимания.

## Counter

- 2026-05-21 [Claude Opus 4.7]: реанимация после archive того же дня. Сессия про MCP-сервер md-mcp. Multi-stage план (D1–D7), Plan mode approved → 6 stages подряд с writes на `~/.claude/skills/`, `~/.codex/skills/`, `~/.codex/config.toml`, `~/.claude.json`, новая subfolder `experiments/md-embedding-server/mcp/`. Review не запускался между stages. Stop hook fired на втором ходу подряд без review после D7 burn-in summary. Pattern идентичен archived версии того же дня — learning не stuck despite recent application.

## Possible upgrade

Plan mode approval мог бы expose review-gate per stage в plan workflow, не только финальный closeout. Альтернатива — внутри `1planning` (или skill-architect для plan files) рекомендация добавлять explicit «review checkpoint» строку между D-blocks для multi-day плана. Hook сейчас ловит по cumulative count, но это reactive; proactive trigger в самом план-шаблоне сильнее.
