# Проверки 1orchestration v10

Exact candidate: `skills/1orchestration/draft-v10/`.

## Exact bytes

```text
package  3479a08389cc4582b8557118b2b208d97229dc0f45e486e9d879635ca975f0b8
SKILL    0dab19d7bf285693f84f4eebac9ca2733698a9d0abb40fd604c61215a6edbf7e
openai   bfa2ce85d16ee139393137b2d2d566062e47a059fa335bf0b212db4729011a5d
baseline 1skill-creation SKILL
         6e6b93e97eef2a31c8922ba8462a28a086c82ec80c6566c39ed63fc6bdc9f6a3
```

Package manifest: для двух путей в лексикографическом порядке хешируется
`relative_path + NUL + raw_bytes + NUL`.

```text
SKILL.md
platforms/codex/agents/openai.yaml
```

## Check round 1

- Literal: единственная finding — `Use before` не соответствует текущему
  буквальному шаблону `Use when`.
- Trajectory: findings `[]`.
- Clean probe: behavior pass; delegated reads `0`; bare `done` не дал pass.

После round 1 изменены только `description` и `short_description`. Старый
manifest `0477d9790f41760bd0e3ca0e42fea548590eb89fab9720802a67bc36dcc1aeaa`
перестал быть candidate.

## Terminal independent checks

### Literal

Findings: `[]`.

- Оба YAML parsed.
- `description == short_description`, 69 символов, начинается с `Use when`.
- Body и `default_prompt` русские; trigger-поверхности английские.
- Ровно два regular files, symlinks `0`, Markdown links `0`.
- Use: assignment/subagent и cognitive split.
- Skip: одно известное чтение без поручения.
- Near-miss: code-module decomposition → `1codebase-design`.

### Trajectory

Эталон:

```text
root owner/authority truth → source-bound brief → actor/root estimates →
simplest releasing form → delegated evidence → addressed/observed all-pass →
dependent hop; upstream change → first stale result
```

Findings: `[]`.

Первый return ошибочно заявил, что package содержит только `SKILL.md`; raw
manifest включал оба файла. Root не принял assertion как evidence. Checker
подтвердил ошибку недостаточным `find -maxdepth`, затем прочитал второй файл и
вернул terminal scope из двух путей, findings `[]`, verdict `PASS`.

## Active set

Оба checker-а независимо совпали:

```text
prepare 10 · root-work 11 · direct 11 · split 11 · accept 8 · upstream-change 5
```

`SKILL.md`: 28 самостоятельных единиц всего; одновременно применимый body
остаётся ниже мягкого ориентира `20`. Task/source units считаются отдельно для
каждого участника.

## Structural evidence

```text
manifest 3479a08389cc4582b8557118b2b208d97229dc0f45e486e9d879635ca975f0b8
frontmatter ok
openai.yaml ok
files 2
symlinks 0
markdown links 0
references 0
state-machine files 0
```

## Terminal verdict

`ready_exact_candidate`.

Official, tracked и live не изменены этим candidate-cycle.
