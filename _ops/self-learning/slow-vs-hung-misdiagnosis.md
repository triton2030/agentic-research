# Slow ≠ hung — background process status misdiagnosis

## Observation

Когда long-running background process shows минимальный CPU usage (e.g. 2.14s CPU over 17 minutes), я диагностирую как «hung» и киляю. Реальность: process может быть **waiting on rate-limited network** — это **legitimate slow**, not hung. CPU не растёт потому что process спит между network calls / в rate-limit backoff.

В сессии 2026-05-21: F1 (`profile-sections --mode llm` background, 300 sections × OpenRouter haiku-4.5 call). После 17 min: 2.14s CPU, 0 records в DB. Я classify'нул как hung, kill'нул, retry. Но: F1 actually проrабатывал records параллельно — pkill попал на already-completed process по race condition. Через минуту notification: «exit code 0», DB показала 300 LLM-profiled.

То есть F1 **успешно работал** через rate-limit waits. CPU low = not hung, просто waiting.

## Counter

- 2026-05-21 [Claude Opus 4.7]: P8 backend hardening session. F1 started 8:18PM. После 5 min run и 17 min monitoring decided hung based on `ps aux` showing 0.x% CPU. Misdiagnosed — actually 280 sections wrote successfully перед kill. Lesson: low CPU без output не = hung. Distinguishing signals: (a) DB state changing (writes happening?); (b) process strace shows actual syscalls; (c) network activity (`lsof -p PID -i` shows TCP connections).

## Possible upgrade

Перед classifying long-running process как hung, проверить:
1. **DB / output state changing** — `sqlite3 ... 'SELECT COUNT'` повторно, не просто `ps aux`
2. **Process internals** — `lsof -p PID` shows active sockets to API endpoint = waiting on response (legitimate slow), no sockets = actually stuck
3. **Expected duration** — для known rate-limited APIs (OpenRouter 200/min), 300 sections × rate-limit budget = legit многоминутный run. Patience criterion before kill.

Detection rule: «process X running long без видимого progress» — STOP кiяlить, проверить DB writes + network sockets first. Hung process = no syscalls + no DB activity. Slow process = network waits + intermittent DB writes.

Related: archived `background-poll-loop-antipattern.md` — same family pattern (impatience с long background tasks).
