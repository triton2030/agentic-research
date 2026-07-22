---
description: "Bounded secret, vulnerability, SAST and final-native-binary evidence routes."
---

# Security Scans

Открывай для explicit secrets/vulnerability/SAST/supply-chain вопроса. Сначала
зафиксируй repo/image/binary scope, network policy и допустимость verifier calls.

## Minimal Route

1. Проверь project config и live `<scanner> --help` / `--version`.
2. Выбери один primary scanner по claim; второй нужен только для независимого
   coverage, а не ради списка.
3. Предпочти offline/local rules. Registry rules, verifier calls и image pulls
   — network routes.
4. Выводи redacted location/type, никогда secret value.
5. Finding = candidate до owner/scope confirmation и воспроизводимого check.

Типовые формы, если соответствующий tool уже выбран:

```bash
gitleaks dir --redact --report-format json --report-path - .
trufflehog filesystem . --no-verification --json
osv-scanner scan source -L LOCKFILE -f json
trivy fs --scanners vuln,secret,misconfig --format json .
semgrep scan --config LOCAL_RULE --metrics=off --json
```

`--no-verification` отключает liveness check, а не превращает detector в
regex-only. Registry Semgrep config может требовать network. Любая точная
команда и output schema проверяются по live help.

## Native Supply Chain

Package registry integrity относится к package artifact, но lifecycle script
может заменить executable. Если claim про финальный native binary, зафиксируй
resolved path, receipt, checksum и platform signature именно финального файла.
Signature без trusted identity оставляй residual risk.

## Credentials

Ищи metadata и exact-token counts в разрешённом scope; не печатай значения.
После подтверждённой утечки нужны отдельные действия: local redaction, restart
процессов с унаследованной env и server-side rotate/revoke. Ни одно из них не
следует автоматически из scan.

## Стоп

Стоп, когда coverage и exclusions названы, findings redacted и
candidate/verified различены, а network calls, cache writes и remediation
оставлены в пределах авторизации.
