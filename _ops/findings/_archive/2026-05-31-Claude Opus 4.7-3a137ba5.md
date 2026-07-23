# Findings — 2026-05-31 — Claude Opus 4.7 — sess:3a137ba5

- 15:57 — self-learning: tool/output miss — 'md ls PATH --json' дефолтом вернул 78.9KB (items_returned:50, large_reply:true): bounded top-50 файлов с ПОЛНЫМИ headings + свёрнутый folders-summary. Для 'понять структуру без дампа' это шумно — нужный folders-агрегат утоплен под top-50 разворотами. Helpful был бы дефолт ещё компактнее (только folders-summary), а top-N файлов — под флаг. md status напротив образцовый: ~1.1KB, state+recommended_action, действуй сразу.
