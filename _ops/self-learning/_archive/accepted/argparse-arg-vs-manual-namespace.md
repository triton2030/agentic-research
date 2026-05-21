# Argparse Arg Vs Manual Namespace

## Observation

При добавлении нового CLI-аргумента в argparse модель синхронизирует
parser, но забывает что **tests конструируют `args` как
`argparse.Namespace(...)` вручную**, без default'ов из parser. Новый
attribute существует в production runtime, отсутствует в test fixtures
→ `AttributeError` валит tests без явной связи с моей правкой.

Pattern: **runtime-vs-test argument asymmetry**. argparse defaults
живут в `add_argument(default=...)`, но Namespace в test'е этого
канала не знает. Production code, читающий `args.new_attr` напрямую,
работает в реальном CLI и падает в test.

## Counter

- 2026-05-20 [Claude Opus 4.7]: heading-side signals для `1md-navigator
  audit`. Добавил `--threshold-heading-diversity` и
  `--min-files-in-family` в argparse + новые orchestrators
  обращались к `args.threshold_heading_diversity` напрямую. `tests/
  test_audit.py` (5 тестов) валились с `AttributeError: 'Namespace'
  object has no attribute 'min_files_in_family'` — fixtures строили
  Namespace из явного списка kwargs. Fix: `getattr(args, "x", default)`
  на caller side. Один лишний repair cycle.

## Possible upgrade

При добавлении нового argparse arg, перед running tests:
- `grep -n "Namespace(" tests/` — есть ли manual construction?
- Если да: либо защититься `getattr(args, "x", default)` на caller
  side, либо обновить test fixtures.

Defensive `getattr` cheaper и сохраняет backwards compat для любого
внешнего caller, который конструирует args программно (не только
test). Стоит дефолтом для public-ish orchestrators.

Применимо: любой CLI tool с pytest test suite где tests конструируют
`args` через `Namespace(...)` или `SimpleNamespace(...)`, а не через
`parser.parse_args([...])`.
