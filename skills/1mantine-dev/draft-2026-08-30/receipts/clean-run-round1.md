# Clean run — round 1

## Пробный случай

React 19.2 и `@mantine/core`, `@mantine/form`, `@mantine/modals`,
`@mantine/notifications` 9.5.1. Settings page использовала raw CSS grid, по
одному `useState` на поле, homemade success toast и wrapper `PrimaryButton` 1:1.

## Фактическая траектория

1. Исполнитель подтвердил resolved-когорту и заметил, что current docs уже
   показывают 9.5.2, поэтому exact API сверял с published `.d.ts` 9.5.1.
2. Raw grid заменён в решении на `Stack` + responsive `SimpleGrid`; actions —
   на responsive `Flex`.
3. Field state и validation сведены в uncontrolled `useForm`, `form.key`,
   `getInputProps`, `isEmail`, `hasLength`; отдельный schema package не добавлен.
4. Async submit использует `form.submitting`, `Button.loading` и disabled
   `Fieldset`; success — `notifications.show`; discard —
   `modals.openConfirmModal` + `form.isDirty/reset`.
5. Wrapper `PrimaryButton` удалён; theme default не добавлен без повторения.
6. Custom residue оставлен для native `<form>`, application types/data,
   `saveAccount`, product copy и минимального workflow glue.
7. Исполнитель выдал audit-таблицу по 13 механизмам и назвал проверки:
   cohort listing, typecheck, production build, responsive browser states,
   validation, pending/success/error, keyboard modal и SSR hard reload.

## Наблюдаемый результат

Черновик изменил дефолт в требуемую сторону: все четыре названных обхода
Mantine были сняты, а допустимый native/custom остаток сохранился с конкретной
причиной.

## Gap

Workspace прогона не содержал приложение и его `node_modules`, поэтому команды
валидации были спроектированы, но не выполнены. Exact declarations 9.5.1
исполнитель прочитал из опубликованных npm tarballs без записи файлов.
