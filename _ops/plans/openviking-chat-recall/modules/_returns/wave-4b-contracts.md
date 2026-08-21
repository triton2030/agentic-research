---
kind: module-return
волна: 4b
состояние: accepted-contract
записано: 2026-08-21
---

# Return — OpenViking Context Layers и execution seam

## Pinned upstream tuple

Текущая технология фиксируется на commit
`2af48624e03b2df6922ab82c6720eb71439c805a`:

| Owner | Path | SHA-256 |
| --- | --- | --- |
| Wiki L2 | `examples/compile/ov-compile-skills/llm-wiki/SKILL.md` | `c5e379843a0af6c4574f29ae8fd6637b2b89a0481da63a76472188633f4792de` |
| Directory L1 | `openviking/prompts/templates/semantic/overview_generation.yaml` | `6a3e077fdb785ba8268ee750a4a5709f82bb72675aecbad0d5fe9432f80a57ad` |
| Context Layers | `docs/en/concepts/03-context-layers.md` | `5c5543e52036fccc87c63f62eb9c9008c71f3e511b97a4b0106661ed56c2d318` |
| License | `LICENSE` | `1bd87fa6d9a5c79daf0c2af042b6725c9773bf095cc3d1bdf3656e66d1c3e5b1` |

Pinned v0.4.16 commit `499995f3ed2e7f551a715179c4053772c51ff819`
имеет тот же Wiki Skill, но другой L1 prompt SHA-256 `5a67431d…` без current
coverage-aware contract. Поэтому единицей provenance является tuple артефактов,
а не package version.

## L0/L1 generation path

- Directory L1 генерирует `SemanticProcessor._generate_overview()` через
  `semantic.overview_generation`.
- Prompt получает `dir_name`, `file_summaries`, `children_abstracts`,
  `output_language` и `directory_coverage`; output содержит `Brief
  Description`, coverage, navigation и detail.
- Directory L0 `.abstract.md` не имеет отдельного LLM prompt: он
  детерминированно извлекается из `Brief Description` сгенерированного L1.
- `parsing/context_generation.yaml` создаёт node-level JSON context и не
  является прямым writer-ом directory sidecars.
- Сборка идёт bottom-up: file summaries → leaf L1 → leaf L0 → parents с child
  L0. Сгенерированные sidecars не входят обратно в собственный input.

## Local seam

- L2 writer реализует официальный Wiki Skill и не пишет `.abstract.md` или
  `.overview.md`.
- Layer writer принимает только accepted L2 pages и child L0, затем создаёт L1
  и извлекает L0.
- Stage receipt фиксирует input/output digests, prompt digest и config digest;
  drift любого входа инвалидирует directory и его ancestors.
- Для текущей production-сборки разрешены видимые Luna Max worktree writers;
  root владеет frozen snapshot, manifests, hot integration files и publish.
- Future reusable tool начинает с fixture/fake semantic adapter. `codex exec`
  не становится default, пока отдельно не закрыты auth, data-egress, logging и
  cost semantics.

## Неизвестно

Retrieval benefit coverage-aware L1, точная page-to-directory grouping и
semantic quality полного русского corpus ещё не доказаны. Их закрывают sample
и blind acceptance, а не источник upstream.
