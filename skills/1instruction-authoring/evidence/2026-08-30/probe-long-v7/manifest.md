# Manifest слепого long-trajectory probe

## Неизменяемые настройки

- Fixture: `fixture/**`, 23 файла, fingerprint
  `aaf7231d40ed8a6f500248b82b9f903d54ab0e533ed8c7498e6045caa5a2cc5f`.
- Task: `fixture/REQUEST.md`, SHA-256
  `6ec313e6488de7b62d444c200596dc4ce30bea3039e04a69da82c56c46548abf`.
- Resolved model: `gpt-5.6-terra`.
- Reasoning effort: `medium`.
- Context: `fork_turns=none`.
- Isolation: общий read-only fixture; отдельный opaque package symlink и
  отдельная owned output directory у каждого arm; запуск других агентов
  запрещён.
- Оба dispatch prompt идентичны по задаче и ограничениям; различаются только
  opaque package path и owned output path.
- Исполнителям не переданы значение arm, comparator, соседний output или
  ожидаемый ответ; чтение symlink target и sibling packages запрещено.

## Скрытое до terminal outputs соответствие

| Opaque arm | Assigned package | Fingerprint |
| --- | --- | --- |
| `ember` | current installed | `07c6fffae9681ab3e2bf61872955b7b0d2c9e8903be4a9ee6770d8c626e923fa` |
| `slate` | `candidate-v7` | `b6dd5b397cc78d49b6edd7212a48bb021a7c6b41b6feec359b81aaeaf378b1ee` |

Package был единственной контролируемой переменной. Один run на arm доказывает
возможность различающего поведения, а не вероятностный сдвиг.
