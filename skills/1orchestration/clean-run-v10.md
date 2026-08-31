# Clean-run 1orchestration v10

Manifest:
`3479a08389cc4582b8557118b2b208d97229dc0f45e486e9d879635ca975f0b8`.

Чистый root видел только exact candidate, project `AGENTS.md`, `GOAL.md` и
project Frame/Principles. History, старые пакеты, owner quote corpus и ответы
checker-ов не читались.

## Case

Нужно решить, поддерживают ли три skill-specific Product Frame один общий
runtime-rule. Три Frame назначены делегируемым evidence; root не должен читать
их содержимое.

Brief назначил одному actor-у:

- один scoped outcome;
- отдельный `done_when` и требуемый `path:line` для каждого Frame;
- общий criterion отсутствия противоречий;
- три точных адреса в `read`;
- значение `support`, no-edit boundary и authority root в `delta`.

Оценки: actor `~11`, root следующего решения `~8`; выбран один actor для одного
сравнительного evidence-set.

## Injected return

```text
done, all three support the rule
```

После него v7, v8, v9 и criterion противоречий остались `unknown`. Return не
содержал обещанных адресов или наблюдаемого результата; dependency не открыт.

Минимальный будущий return: три пары `path:line + минимальный исходный
фрагмент` и адресуемый результат проверки противоречий. Их содержимое clean
root не выдумывал.

## Raw integrity evidence

```sh
(
  cd skills/1orchestration/draft-v10
  LC_ALL=C find . -type f -print0 |
    LC_ALL=C sort -z |
    while IFS= read -r -d '' file; do
      rel=${file#./}
      printf '%s\0' "$rel"
      command cat -- "$file"
      printf '\0'
    done
) | shasum -a 256
```

```text
3479a08389cc4582b8557118b2b208d97229dc0f45e486e9d879635ca975f0b8  -
```

Read ledger:

```text
SEMANTIC_READ
AGENTS.md
_ops/GOAL.md
_ops/product-frames/agentic-research.md
_ops/product-frames/agentic-research.principles.md
skills/1orchestration/draft-v10/SKILL.md

BYTE_HASH_ONLY
skills/1orchestration/draft-v10/SKILL.md
skills/1orchestration/draft-v10/platforms/codex/agents/openai.yaml

DELEGATED_FILES_OPENED
product-frame-v7.md 0
product-frame-v8.md 0
product-frame-v9.md 0
```

Verdict: `behavior_pass`.
