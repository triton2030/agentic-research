# Exact candidate review — planning-family

## Основание

- Baseline `1skill-creation` fingerprint:
  `c892d9e3747984ff7154959f819f22700a90784de8f90d70c8c6f404e83c35e4`.
- Owner criteria: `_ops/chat-recall/2026-08-26-220614-claude-4ee6bbef.md:20-22`,
  `_ops/chat-recall/2026-08-29-152644-codex-01a04d0d.md:23-29` и
  `_ops/chat-recall/2026-08-29-163434-codex-01a04d4a.md:17,20-22,33`.
- Текущий acceptance input — проверочный результат оркестратора, не owner
  speech; он не добавлялся в chat-recall.

## Exact candidates

Canonical hash: в candidate directory отсортировать пути с ведущим `./`, затем
для каждого записать `relative-path NUL exact-bytes NUL` и SHA-256 всего потока.

| Package | Candidate | SHA-256 | Active route peak |
| --- | --- | --- | ---: |
| `1planning` | `skills/1planning/versions/candidate-2026-08-30/` | `91b4cc7db09fb5909a69cf4ff6c02830f361b30ffebaef3122f86a13ab031ee4` | 28–31 |
| `1plan-map` | `skills/1plan-map/versions/candidate-2026-08-30/` | `57f9fadb7eafbaf60a4a1fff105c9c3ec3e818dffe1b99c1fc391e0bde0e47b1` | 30–32 |
| `1plan-task` | `skills/1plan-task/versions/candidate-2026-08-30/` | `0b90fe7ab5af763258d42fe69a9c17f159d9e87f3b8a6eb8a3efb26bc2216e05` | 39–40 |

Runtime references: `0 / 0 / 0`. Peaks — честный atomic recount всего
context+goals+applicable route, не счёт строк. Они выше ориентира 20, потому
что включают independently violable hard gates; удалять их ради счёта означало
бы вернуть доказанные смысловые потери.

## Restored invariants

- `1planning`: applicable root/subtree instructions; named book+method trace;
  approval только полного `result + boundary + proof + surprise` handoff.
- `1plan-map`: composition acceptance требует non-overlap results, order,
  dependencies и proof до принятия карты.
- `1plan-task`: один current writer, явная последовательная authority transfer,
  reasoned defer и stop/replan при изменении полного handoff before resume.

Не возвращены schemas, status catalogs, references, snapshots и writer-recovery
ceremony: этот acceptance-цикл не показал вреда без них.

## Addressable acceptance outputs

- [Literal exact-byte checker](final-literal-check.md) — PASS; count above
  heuristic documented.
- [Independent acceptance checker](final-acceptance-check.md) — PASS.
- [Clean probe](final-mixed-probe.md) — PASS.

## Verdict

**FUNCTIONALLY READY CANDIDATE.** Ориентир `~20` не достигнут без удаления
несущих атомов; это явный tradeoff, не скрытая игра со счётом. Official,
tracked и live packages не изменялись, установка не выполнялась. Для
продолжения нужен отдельный exact approval трёх hashes.
