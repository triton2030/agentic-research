# Panel trial — round 1 — 2026-08-29

Clean Codex executor проверил реальную material fork: передавать ли упрощённый
candidate final checker-ам или снова пересобирать. Writes были запрещены.

## Direct trace

- Packets `PM-1/L-1/S-1/P-1` заморожены до первого report; primary zones разведены.
- Один `$1claude-mcp` call завершился `resolved_model=claude-opus-5`, warnings
  `[]`, первая строка `signal_watchable`; native reports ему не передавались.
- Native launch receipts: `ladder`, `solvent`, `prospector`, каждый
  `fork_turns: "none"` и только со своим packet.
- Capacity реально упёрлась в `agent thread limit reached`; Ladder/Solvent
  сохранены, Prospector завершён второй bounded wave без подмены.
- Ladder missing-falsifier исправлен в retained stream только evidence delta;
  verdict остался `ladder_holds`, новый голос не создан.
- Reports различались: direction · assumptions · external precedents ·
  failure story. Общего evidence path не было.
- Synthesis вернул next/alternative/unchanged без голосования и без final acceptance.

## Decision

Next: final checker; full rebuild не обоснован. Observed functional defect у
упрощённого controller-а не найден.

## Findings

1. `premortem.md` мог вернуть blocker, а controller не имел terminal edge.
   Final checker усилил fix: blocker останавливает pass как `panel_incomplete`;
   synthesis запускается только с четырьмя фактическими reports.
2. Primary zone Premortem была выводима, но не буквальна. Принято локальное
   уточнение «каждой из четырёх линз».
3. Host фактически применил `$1claude-mcp`, поэтому local count 22 не описывал
   actual active set. Принято: runtime-owner назван явно; nested count помечен
   unknown. Повторное micro-stage дробление отклонено: trial не показал
   functional omission.
