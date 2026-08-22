---
description: "Safe page Markdown snapshots, creates, edits, targeted updates, and round-trip verification."
---

# Pages And Round-Trip

## Read A Page

Use the page ID from the URL; dashed or undashed UUIDs are accepted by the API.

```bash
ntn pages get PAGE_ID
ntn pages get PAGE_ID --json
```

Plain output includes page properties as leading frontmatter. JSON output is the
verification surface: inspect `.markdown.truncated` and
`.markdown.unknown_block_ids` before any edit. Unsupported blocks can appear as
`<unknown ...>` in Notion-flavored Markdown; do not silently replace a page
containing them.

## Local Snapshot Contract

A downloaded `.md` file is a point-in-time working copy. It is not watched or
automatically synchronized by `ntn pages`. Record at least the Notion page ID or
URL and the retrieval time outside the content that will be pushed.

The runtime observed on 2026-08-02 lists `ntn notion-as-code` as alpha and “not
publicly available.” Re-check `ntn --help` when this changes; until then it is
not an active local-folder sync contract.

Safe explicit flow:

1. Pull the current page and JSON status.
2. Preserve an unedited baseline or its hash locally.
3. Edit the working Markdown.
4. Pull again immediately before push and compare it with the baseline.
5. Stop on a remote change; reconcile rather than overwrite.
6. Push once, retrieve again, and compare semantically.

Do not promise byte-identical round trips. Notion can normalize whitespace,
empty blocks, rich text, and supported Markdown constructs.

## Create A Page

```bash
ntn pages create --parent page:PARENT_ID < page.md
ntn pages create --parent data-source:DATA_SOURCE_ID < page.md
```

On create, leading frontmatter `title` sets the title; other frontmatter
properties are ignored by the convenience command. Use the Pages API for
database properties, templates, icons, covers, or other full-surface fields.
Capture the returned page ID and retrieve it after creation.

## Edit Existing Content

The current convenience command is discovered with `ntn pages edit --help`:

```bash
ntn pages edit PAGE_ID < page.md
ntn pages edit PAGE_ID --json < page.md
```

This replaces the page content represented by the Markdown input. The command
strips leading frontmatter. It protects child pages and child databases unless
`--allow-deleting-content` is explicitly supplied. Do not supply that flag
without inspecting the children and obtaining clear deletion intent.

For a small change to a large or structured page, prefer the raw Markdown API's
current targeted operations such as `update_content` or `replace_content` over
whole-page replacement. Inspect the live endpoint first:

```bash
ntn api '/v1/pages/{page_id}/markdown' -X PATCH --docs
ntn api '/v1/pages/{page_id}/markdown' -X PATCH --spec
```

## Special Content

- Meeting-note transcripts are read-only through the documented Markdown
  surface; do not attempt to edit or text-match transcript content.
- File references may require separate upload or download handling; inspect
  `ntn files --help` and the current endpoint docs.
- Page properties are not ordinary body Markdown. Read and update them through
  the Pages/Data Sources API and verify each intended property separately.

## Write Evidence

Report the page ID/URL, whether the operation created or replaced content, the
pre-write truncation/unknown-block status, the post-write retrieval result, and
any preserved remote changes or unsupported constructs.

## Official Sources

- [Working with Markdown content](https://developers.notion.com/guides/data-apis/working-with-markdown-content)
- [Working with page content](https://developers.notion.com/guides/data-apis/working-with-page-content)
- [CLI commands](https://developers.notion.com/cli/reference/commands)
