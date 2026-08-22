---
description: "Admission, deployment, verification, and secret handling for persistent Notion Workers."
---

# Workers

## When A Worker Is Justified

Use a Worker only when the outcome needs persistent behavior inside Notion:

- a schedule or database sync;
- event-driven handling through webhooks;
- a reusable tool or integration capability;
- code that must keep running after the local agent turn ends.

Ordinary page reads, edits, one-off queries, and local reports should stay on
`ntn pages`, `ntn datasources`, or `ntn api`. A Worker adds hosted state,
permissions, deployment, observability, secret, and possible cost obligations.

## Discover The Live Surface

Workers are beta. Start with:

```bash
ntn workers --help
ntn workers capabilities --help
ntn workers new --help
ntn workers deploy --help
ntn workers sync --help
ntn workers webhooks --help
ntn workers env --help
ntn workers runs --help
ntn workers usage --help
```

Do not copy an old manifest or assume command flags. Scaffold with the live CLI,
inspect the generated project contract, and keep Worker-specific configuration
within that project.

## Delivery Flow

1. Define the trigger, target database or page scope, permissions, idempotency
   key, retry ceiling, and failure owner.
2. Confirm that the workspace and current plan support the needed capability;
   read live pricing and limits instead of encoding them in the skill.
3. Scaffold the smallest Worker and keep business logic deterministic where
   possible.
4. Configure secrets with `ntn workers env`; never commit them or echo their
   values.
5. Test a bounded capability or run before enabling a schedule or webhook.
6. Deploy, retrieve the Worker, inspect runs, and confirm the intended Notion
   object changed exactly once.
7. Report how to inspect, disable, redeploy, and delete the persistent behavior.

## Sync And Webhook Safety

A sync or webhook is not “automatic Markdown folder sync” by default. Name the
source of truth, mapping direction, conflict policy, deletion semantics,
deduplication key, pagination strategy, and recovery procedure. If any of these
is unresolved, prototype read-only or stop before enabling persistence.

Prefer webhooks for incremental change detection when polling would repeatedly
scan large views. Verify signatures and make handlers idempotent. Bound retries
and surface poison events rather than looping indefinitely.

## Secrets And Data Boundaries

Keep secrets in Worker environment storage and local `.env` files out of
version control. Declare every external destination that receives Notion data.
Do not send private page bodies to third-party APIs merely because a Worker can
reach them.

## Official Sources

- [Workers overview](https://developers.notion.com/workers/get-started/overview)
- [Worker secrets](https://developers.notion.com/workers/guides/secrets)
- [Working with views](https://developers.notion.com/guides/data-apis/working-with-views)
