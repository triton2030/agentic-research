# Claude Failure Recovery

Вход: exact typed non-session failure. Выход: одна recovery action либо stop с
failed layer, packet evidence и одним следующим действием.

- Recovery сохраняет authorization, model, destination, data scope и external
  identity исходного вызова; иначе это новый запрос.
- Не повторяй автоматически externally attempted call.
- Missing/stale tool или schema — сохрани diagnosis, остановись и предложи
  владельцу fresh Codex task; сам task не создавай.
- Approval, auth, billing, unsupported model/profile или non-Opus evidence —
  назови точную границу и stop.
- Invalid path или permission исправляй только в прежнем approved scope.
