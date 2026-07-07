---
description: "Domain-neutral artifact anchor schema for prose-audit evidence."
depends-on: []
---

# Artifact Anchor

Every evidence row needs a locator that fits the artifact modality.

Markdown line refs are only one locator type. They are not the universal model.

## Fields

| Field | Meaning |
| --- | --- |
| `artifact_ref` | Path, URL, file id, Figma node source, video file, screenshot, deck, or interview reference. |
| `modality` | Kind of artifact being cited. |
| `locator_type` | How to interpret `locator`. |
| `locator` | Concrete address inside the artifact. |
| `capture_ref` | Optional rendered capture: screenshot, exported frame, transcript, recording, PDF page image. |
| `text_excerpt` | Short excerpt or description of the observed evidence. |
| `anchor_quote` | Optional verbatim fragment of the source at `locator`. On load-bearing anchors (money, core invariants), deterministic checks confirm it still appears there; skip it on low-stakes rows to keep capture cheap. |

## Modalities

| Modality | Example Locator Types |
| --- | --- |
| `markdown` | `line_range`, `heading`, `block_id` |
| `plain_text` | `line_range`, `paragraph`, `char_range` |
| `url` | `url`, `dom_selector`, `viewport_state` |
| `screenshot` | `region`, `ocr_text`, `visual_element` |
| `deck` | `slide`, `slide_region`, `speaker_note` |
| `video` | `timecode`, `shot`, `transcript_range` |
| `audio` | `timecode`, `transcript_range` |
| `figma` | `node_id`, `frame`, `component` |
| `dataset` | `row_id`, `column`, `query` |
| `interview` | `participant_id`, `quote_id`, `timecode` |
| `measurement` | `metric`, `event`, `query` |

## Rule

If a locator cannot be checked or re-opened by a future auditor, it is not a
traceable anchor. Put it in `notes` as context, not as evidence.
