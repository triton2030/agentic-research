# Аудит глобальных Claude skills на отставание от текущих skills

## Цель
Глобальная Claude skills-папка найдена, а отстающие или лишние skills перечислены по фактическому сравнению с текущими repo/Codex источниками.

## Подшаги
- [ ] Найти фактическую глобальную Claude skills-папку на компьютере.
- [ ] Составить текущие эталонные источники: repo `projects/meta/*--skill-claude-code`, installed Codex skills и релевантные live inventories.
- [ ] Сравнить Claude skills с текущими источниками по именам, структуре и содержанию.
- [ ] Выдать короткий список: актуальны, отстают, отсутствуют, лишние/устаревшие, неопределённые.

## Критерии приёмки

### Must
- [ ] Аудит опирается на фактический путь Claude skills, найденный через filesystem evidence, а не на память. — **Evidence**: команда показывает найденные Claude skill directories.
  **Anchored in**: `_ops/INTERVIEW.md#Рабочий-Режим`
- [ ] Сравнение отделяет Claude Code global skills от repo-local Claude variants и Codex installed skills. — **Evidence**: результат явно называет baseline и target для сравнения.
  **Anchored in**: `_ops/PROJECT-ROADMAP.md#Stage 1`
- [ ] Отстающие skills названы с конкретной причиной отставания: missing, stale content, metadata/package mismatch, superseded duplicate или no current counterpart. — **Evidence**: итоговая таблица/список с причиной по каждому skill.
  **Anchored in**: `_ops/PROJECT-ROADMAP.md#Stage 1`
- [ ] Никакие Claude или Codex skill files не изменяются в рамках аудита без отдельного запроса на синхронизацию. — **Evidence**: `git status --short` не получает новых skill edits от этого аудита.
  **Anchored in**: `_ops/INTERVIEW.md#Минимальный-След`

### Must not
- [ ] Не считать skill актуальным только потому, что имя совпадает. — **Why this would be bypassed**: совпадающий handle может скрывать старый контракт.
- [ ] Не смешивать уже существующие незавершённые repo edits с результатами этого аудита. — **Why this would be bypassed**: текущий worktree уже грязный после предыдущей meta-skill работы.

### Verification protocol
1. Найти Claude skill paths через `find` / `ls` в пользовательских конфиг-папках.
   Expected: найден фактический путь или явно доказано отсутствие.
2. Сравнить найденные Claude skills с repo/Codex baseline через `find`, `diff -qr` или checksum/content probes.
   Expected: по каждому релевантному skill есть статус и причина.
3. Проверить `git status --short` после аудита.
   Expected: без новых правок в skill files от аудита.
