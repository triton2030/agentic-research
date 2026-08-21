---
kind: module-return
wave: 6
stage: F1-source-lock
state: accepted
date: 2026-08-22
---

# Wave 6 F1 — frozen source lock

## Результат

Visible Luna Max task `01a025ca-3714-7082-be9f-27ece6673e54`
зафиксировал корпус из explicit source commit
`6f98fcccdbf4b4de45ef787239ad101f70d106e2`. Root интегрировал writer commits
`4b96d30` и `421d6b3` в `main` как `acb3def` и `31c8a4f`.

Exact ownership:

- `experiments/openviking-chat-recall/scripts/freeze_corpus.py`;
- `experiments/openviking-chat-recall/tests/test_freeze_corpus.py`;
- `experiments/openviking-chat-recall/artifacts/full-build/frozen/source-manifest.json`;
- `experiments/openviking-chat-recall/artifacts/full-build/frozen/source-lock.json`.

Lock фиксирует 184 holder files. Manifest содержит только path, Git blob OID,
SHA-256 и bytes; quotes и parsed records в него не копируются.

| Поле | Значение |
| --- | --- |
| manifest SHA-256 | `9cf1f74a0ee48347a9f2db4bf01eeb795577913fd9d04c235540564e9c753450` |
| parser SHA-256 | `cd2f558947255f8648a08a0c86989a2c8af60e2439be617b5e2a02db94cc1d23` |
| config SHA-256 | `d8122ad1c5b4bb889459f3959bb3a5e5fcd406431904109a1d3dbcc79b86e153` |
| code SHA-256 | `b580f5d79601dcb4bb15cbbed4e06bdd3ec561cfb94809e5700bb0636974de85` |
| source-lock file SHA-256 | `8d370407047e7d600e5656e153842120fc6bd7fdca1ee0b4d5ad957a261e52fc` |

## Проверка root

На интегрированном `main` выполнено:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s
  experiments/openviking-chat-recall/tests -p 'test_*.py' -v` — 24/24 PASS;
- fresh build под `/tmp` без `TMPDIR` — PASS;
- оба сгенерированных файла совпали с committed artifacts через `cmp`.

Negative tests отклоняют `HEAD`, сокращённый SHA, dirty/path/count drift,
source-root drift, escaping symlink и symlinked parent. Пересборка сохраняет
несвязанные файлы output directory.

Первый writer ошибочно доверял environment-sensitive `tempfile.gettempdir()`:
тот же output под `/tmp` падал без `TMPDIR` и проходил с `TMPDIR=/tmp`.
Repair `421d6b3` заменил это на стабильные system aliases `/tmp` и `/var` и
добавил regression test; manifest остался byte-identical.

## Независимая приемка

Read-only auditor `/root/f1_acceptance` проверил 16 acceptance conditions и
вернул PASS без blocking findings. Nested checker writer-а остался UNKNOWN и
не использован как evidence.

## Frontier

F1 принят. F2 обязан читать только этот source lock и Git objects exact corpus
commit, а не live holders. Следующий результат — deterministic evidence layer
для всех 1101 parsed records с явным disposition 34 source diagnostics.
