# Закрытие lifecycle

## Цель

Закрыть принятые background threads наблюдаемым persisted state, не потеряв
mutable результат и не оставив флот закреплённым.

Открывай после acceptance bounded результата или завершения зонтичной
retained-service.

- Все background threads остаются unpinned.
- Принятый bounded thread архивируется.
- Bounded thread с mutable artifact архивируется только после integration.
- Setter return не доказывает persisted state; bounded archive проверяется в
  archived listing.
- Retained specialist остаётся с точным title, unpinned и current-source
  resolver.
- После acceptance зонтичной service-работы retained thread архивируется.
- Retained archive проверяется в archived listing.
- Launch-only controller останавливается на подтверждённом handle.
- Managed controller останавливается после требуемого persisted state.
