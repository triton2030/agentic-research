# Чем проверено — 1design-review

## v2 (2026-08-13)

- Полный runtime V3 дважды независимо прошёл cognitive audit до утверждения
  владельцем; lifecycle delta `routed` отдельно проверена двумя аудиторами.
- Fresh Eyes перед реализацией: Ladder подтвердил цепочку к цели проекта;
  Solvent снял aggregate/scheduler; Prospector независимо рекомендовал
  Playwright, DOMRect/Range, browser-rendered collage и раздельные modes.
  Claude Premortem не прошёл из-за `api_error`; чужая линза не имитировалась.
- `node --test experiments/1design-review/tests/*.test.mjs`: 7/7. Проверены
  10% crop + clamp, transition boundary, union area, общий family scale, запрет
  >4 members, URL-only diagnostics; fixture реально создал все шесть kinds,
  красно-белую density map, многоцветную spacing map, 2×2 collage и один task
  на один question. Второй fixture-run доказал supplied-image viewport, block
  с explicit rect и family с explicit member rects. Regression probes
  отклоняют path-colliding task ids и делают missing reviewer output
  terminal failure даже при process exit 0.
- Live capture:
  `/Users/triton/Documents/My_projects/kumysbekov/_workspace/design-review/20260813T114017Z-v3-proof/`.
  Manifest: 8/8 artifacts, 0 failures; root открыл каждый final PNG.
- Visual gate live run поймал и исправил два дефекта scripts: offscreen family
  crop обрезал icons; all-pairs spacing выдавал ложные gap/overlap. После
  исправлений fixture снова 7/7, Kumysbekov снова 8/8.
- Clean fanout live run: 6 plan tasks → ровно 6 reviewer tasks, все
  `done/exitCode=0`; старый runtime создал бы 48 focused tasks плюс aggregate.
- Root adjudication:
  `adjudication.json` подтверждает один major mobile finding и сохраняет
  остальные evidence-backed preserve conditions. Blind aggregate отсутствует.
- Структурные проверки: `npm run check`,
  system `quick_validate.py`, Markdown lint и projection parity выполняются
  перед commit.
