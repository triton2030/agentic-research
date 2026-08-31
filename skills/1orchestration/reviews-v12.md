# Проверки 1orchestration v12

## Authority и owner override

- Current `1skill-creation/SKILL.md`:
  `c2ca7634a518779fd0c52da0f7bc83bcd55845f6708e86359c46fce9db17ea08`.
- Owner-evidence
  `_ops/chat-recall/2026-08-29-152721-codex-01a04d0e.md:24` снимает
  промежуточную approval-паузу: repair и validation выполняются автономно;
  вопрос задаётся только перед установкой.
- Поэтому v12 получает один новый bounded current-authority check после
  material protocol change; это прямое owner-разрешение продолжить, а не
  скрытый reset старого claim-а.

## Exact input

- package: `7ae572d1c9cab1f6fa35c8dff817e1a52e47563f29e7f9c97c35590b590af0c4`;
- `SKILL.md`: `e21fd6e8e512f9afd3f75a6877212068cb78aadee429d0500250a8e53dd24ad8`;
- `openai.yaml`: `0b30c4c292aaa3b9af97f172f9c3cb4a50465916912bf54f9fa6360fa3d476ab`;
- structural precheck: YAML/frontmatter pass, description parity, 86 chars,
  2 regular files, 0 symlinks, 0 Markdown links.

## Opus findings carried into v12

- rollback loss — accepted and repaired in step 8;
- ambiguous file scope of `delta` — repaired against literal owner boundary;
- trigger function — clarified;
- full current `agent-defaults` ledger — added to `refactor-v12.md`;
- zero-margin active set — accepted as explicit `body 21` risk; no reference
  can lower a universal obligation.

## Current-authority terminal results

- Literal checker, clean window, exact package
  `7ae572d1c9cab1f6fa35c8dff817e1a52e47563f29e7f9c97c35590b590af0c4`:
  `[]`.
- Trajectory checker, independent clean window, same exact package: реалистичный
  case прошёл `before-trigger → read → source-bound brief → 23-unit actor/model
  fit → releasing boundary → all-pass evidence gate → upstream rollback`;
  `Находки: []`.
- Обязательный long-work Fresh Eyes после этих проверок:
  `trajectory_ok: no trajectory findings`. Его вывод: новый архитектурный
  цикл не нужен; следующий ход — exact-byte gate и запрос установки.

## Root exact-byte gate

- Manifest повторно получен по сохранённой формуле
  `relative_path + NUL + raw_bytes + NUL`:
  `7ae572d1c9cab1f6fa35c8dff817e1a52e47563f29e7f9c97c35590b590af0c4`.
- File hashes повторно совпали:
  `SKILL.md e21fd6e8e512f9afd3f75a6877212068cb78aadee429d0500250a8e53dd24ad8`;
  `openai.yaml 0b30c4c292aaa3b9af97f172f9c3cb4a50465916912bf54f9fa6360fa3d476ab`.
- YAML и frontmatter разбираются; `description` совпадает с
  `short_description`, имеет 86 символов и остаётся коротким English
  trigger-only текстом. Instructional body и runtime prompt — русские.
- Пакет содержит 2 regular files, 0 symlinks, 0 Markdown links; запрещённой
  кальки «государственный автомат» нет.
- Tracked owner, Claude/Codex projections и live packages не менялись после
  заморозки v12 и сохраняют взаимный v10 parity:
  `SKILL.md 0dab19d7bf285693f84f4eebac9ca2733698a9d0abb40fd604c61215a6edbf7e`,
  Codex `openai.yaml bfa2ce85d16ee139393137b2d2d566062e47a059fa335bf0b212db4729011a5d`.

Terminal verdict: `ready_exact_candidate; needs installation approval`.
