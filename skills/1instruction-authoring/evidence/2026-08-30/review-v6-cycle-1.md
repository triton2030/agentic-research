# Независимая проверка `candidate-v6` — цикл 1

Проверенная версия: 4 файла, fingerprint
`20d7062bd2aee013d34e79624317e48951de9f0d6bcc30c506edb5c374341860`.

## Общий вердикт

`fail` с локальными исправлениями без возврата удалённых runtime-стадий.

## Принятые findings

1. Trigger `project instructions` захватывал человеческие README-инструкции.
2. Hard-line allowlist не называл невыводимые межзонные связи.
3. Scout требовался слишком широко и не был явно независимым чистым агентом.
4. `no-change` не исключал текст, ссылку и самоотчёт как достаточное evidence.
5. Verification не имел самостоятельного входа и полного выхода.
6. Verification description не покрывал authorized install-only continuation.
7. Запрет «не дроби процесс» был шире owner-критерия о механической маскировке.
8. Verification имел 21 active unit; локальная цель дублировала gates.
9. Preservation map содержал смещённые адреса; `cut.md` не отражал v6.

Root и scout подтвердили допустимые active counts: 15 и 15.
