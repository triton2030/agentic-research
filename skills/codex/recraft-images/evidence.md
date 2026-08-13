# Evidence

Проверено 2026-08-13 без платной генерации.

- `quick_validate.py /Users/triton/.codex/skills/recraft-images` →
  `Skill is valid!`.
- `python3 -m py_compile scripts/save_generation.py` → exit 0.
- `ruff check scripts/save_generation.py` → `All checks passed!`.
- `rumdl check --disable MD041` → `Success: No issues found`; `MD041` is
  intentionally disabled because the shaping contract requires `## Контекст`
  to be the first body heading.
- Temp-project `/private/tmp/recraft-images-test.QH9LdU`, дата `2026-08-03`:
  `Workspace/Recraft/3-августа`; PNG/MD pair; exact two-line prompt bytes;
  collision `-2`; multi-output `-01/-02`; native SVG retained; JPEG converted
  to a valid PNG signature. Assertions → `PASS`.
- Final fresh Codex `019fface-cdeb-7f93-b1ad-f24610246be0`: direct «Рекрафт» loaded
  `recraft-images`, built a structured prompt and made no MCP/file call.
- Final fresh Codex `019fface-cdea-70b2-8db6-211b36f76648`: same generic task
  without Recraft did not load `recraft-images`.
- Fresh Codex `019ffac3-87fc-7612-bfb3-7789be31a153`: explicit Recraft
  background removal routed to `remove_background`, then upload/save/get_user;
  no operation executed.
- Final fresh Codex `019fface-cdeb-7d92-96ad-3b3d230ab450`: live `get_user` succeeded,
  account `triton2030`, balance 1000; no paid image tool called.
- Two independent read-only audits: bloat and provenance/loss. Accepted fixes:
  absolute project root, exact Design Agent message provenance, durable owner
  addresses, selected SVG/one-output evidence, executed-test receipts.

## Итерация: компиляция количественного намерения

Owner correction: `_ops/chat-recall/2026-08-13-154355-Codex-019ffa9f.md:21-22`.

- `quick_validate.py` → `Skill is valid!`; `rumdl check --disable MD041` →
  `Success: No issues found`.
- Независимый bloat audit предложил снять повтор из верхних разделов; отклонено,
  потому что владелец прямо потребовал правило и в description, и наверху skill.
- Независимый loss/provenance audit → `PASS`: raw `80%` однозначно переводится
  в framing cues, исключения для visible text и semantic count не пропускают
  процент кадрирования.
- Fresh Codex `019ffadc-e2bc-7a20-82e9-bf776dc2bbf7`, raw request
  `майка ... на 80%`, dry run: skill activated; model-facing prompt содержал
  `dominates`, `tight framing`, `narrow margins`, `edges close`; цифры и `%` —
  `NO`; Recraft и файловые операции не вызывались.
- Paid acceptance run `019ffadd-f659-7f40-af5e-d4a069b02867`: ровно один
  `generate_image(prompt, model=recraftv4_1, image_size=4:5, n=1)` и один
  последующий `get_user`; баланс после вызова — 998 кредитов.
- Output сохранён как
  `Workspace/Recraft/13-августа/blank-tshirt-tight-frame.png` и парный `.md`.
  `sips` подтвердил PNG 896 × 1152; `.md` содержит только точный отправленный
  prompt без цифр и `%`.
- Визуальная приёмка original PNG: майка доминирует, фон сведён к узким полям,
  ворот и оба рукава видны; нижний край находится у границы кадра. Повторная
  платная генерация не выполнялась.
