# Terminal literal exact-byte checker

## Exact-byte verdict

**PASS.** Канонический поток для каждого candidate: отсортированные имена
`./SKILL.md`, `./agents/openai.yaml`; для каждого — `relative-path NUL bytes
NUL`.

| Package | SHA-256 | Semantic route count |
| --- | --- | ---: |
| `1planning` | `3888a840155d57c594739aa147aad6ddc9f6f8e7beb3a4a47bc3a00b09337de2` | 7 |
| `1plan-map` | `ffad57275a129c79cfe540c384906a47618d5e7684411f4a97ac96645d7b0aaa` | 5 |
| `1plan-task` | `f1ee6f586d8efd8d8ed3d11c45bac819a0f61a75555f2c937ffae69a3fa054df` | 4 create/rebuild + 5 lifecycle = 9 |

Проверено: русское body, English trigger-only description, отсутствие runtime
references; root/subtree instructions; named book+method trace; approval полного
handoff; map acceptance; single writer, sequential handoff, defer reason и
revalidated full-handoff resume. Schema, status catalog и writer-recovery
ceremony не требуются.
