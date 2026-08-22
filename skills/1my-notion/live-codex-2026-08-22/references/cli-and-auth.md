---
description: "Live ntn discovery, authentication, raw API invocation, and operational limits."
---

# CLI And Authentication

## Live Discovery

The CLI is beta and its surface can move. Discover it instead of remembering
syntax:

```bash
command -v ntn
ntn --version
ntn --help
ntn pages --help
ntn api ls
ntn api '/v1/pages/{page_id}/markdown' -X GET --docs
ntn api '/v1/pages/{page_id}/markdown' -X PATCH --spec
```

`ntn api PATH --docs` returns the official endpoint documentation available to
the CLI. `--spec` returns the reduced OpenAPI fragment. When a path supports
multiple methods, select one with `-X`. Use the actual path from `ntn api ls`;
do not infer it from an old example.

## Authentication

Use non-secret probes:

```bash
ntn whoami
ntn doctor
```

`NOTION_API_TOKEN` overrides stored authentication. The CLI may otherwise use
the OS keychain; interactive authentication starts with `ntn login`. Never run
`ntn auth token` in agent-visible output. Never embed a token in a command,
Markdown file, patch, transcript, Worker source, or version control.

An authenticated connection sees only content shared with that connection and
only operations allowed by its capabilities. A `404` can mean “not shared with
this connection,” not necessarily “does not exist.” Treat permissions as part
of the result.

## Raw API Calls

General shape:

```bash
ntn api /v1/search --data @request.json
ntn api /v1/pages/PAGE_ID/markdown
ntn api /v1/pages/PAGE_ID/markdown -X PATCH --data @request.json
```

For request bodies, use exactly one source: stdin JSON, `--data`, or inline
inputs. Prefer `--data @file.json` for inspectable non-trivial payloads. Use
`-X` only when method inference is wrong or the endpoint supports several
methods.

Before a mutating call:

1. Inspect `--docs` or `--spec` for the exact endpoint.
2. Retrieve the current owner object.
3. Keep the payload to the narrow intended delta.
4. Apply once; do not blindly retry non-idempotent creates.
5. Retrieve again and compare the intended fields.

## Limits And Retries

Notion documents an average integration limit of about three requests per
second, with endpoint-specific size limits. On `429`, honor `Retry-After` and
use bounded retries with jitter. Paginate while `has_more` is true and preserve
`next_cursor`; a first page is not corpus coverage.

For large page creates or Markdown updates, inspect the current endpoint docs
for asynchronous operation. If a response returns a task rather than the final
object, poll that task to `succeeded` or `failed` before reporting completion.

## Official Sources

- [CLI overview](https://developers.notion.com/cli/get-started/overview)
- [CLI commands](https://developers.notion.com/cli/reference/commands)
- [CLI authentication](https://developers.notion.com/cli/get-started/authentication)
- [Request limits](https://developers.notion.com/reference/request-limits)
- [API introduction](https://developers.notion.com/reference/intro)
