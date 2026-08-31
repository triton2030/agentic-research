# Terminal trajectory exact-byte checker

## Exact-byte verdict

**PASS.** По той же канонической схеме `./relative-path NUL bytes NUL`:

- `1planning`: `3888a840155d57c594739aa147aad6ddc9f6f8e7beb3a4a47bc3a00b09337de2`
- `1plan-map`: `ffad57275a129c79cfe540c384906a47618d5e7684411f4a97ac96645d7b0aaa`
- `1plan-task`: `f1ee6f586d8efd8d8ed3d11c45bac819a0f61a75555f2c937ffae69a3fa054df`

Эталонная траектория: `1planning` читает применимые инструкции, показывает
named book-method decomposition и получает approval полного handoff →
`1plan-map` принимает только непересекающуюся проверяемую композицию →
`1plan-task` сохраняет одного writer-а через handoff, reasoned defer и
full-handoff revalidation before resume.

`trajectory_ok`: material findings отсутствуют.
