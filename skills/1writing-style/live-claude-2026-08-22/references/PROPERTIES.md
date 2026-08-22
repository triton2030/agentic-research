# Справочник Properties (Frontmatter)

Properties используют YAML frontmatter в начале note:

```yaml
---
title: My Note Title
date: 2024-01-15
tags:
  - project
  - important
aliases:
  - My Note
  - Alternative Name
cssclasses:
  - custom-class
status: in-progress
rating: 4.5
completed: false
due: 2024-02-01T14:30:00
---
```

## Property Types

| Type | Example |
|------|---------|
| Text | `title: My Title` |
| Number | `rating: 4.5` |
| Checkbox | `completed: true` |
| Date | `date: 2024-01-15` |
| Date & Time | `due: 2024-01-15T14:30:00` |
| List | `tags: [one, two]` or YAML list |
| Links | `related: "[[Other Note]]"` |

## Default Properties

- `tags` - tags note (searchable, shown in graph view)
- `aliases` - альтернативные имена note (используются в link suggestions)
- `cssclasses` - CSS classes, применяемые к note в reading/editing view

## Tags

```markdown
#tag
#nested/tag
#tag-with-dashes
#tag_with_underscores
```

Tags могут содержать: letters (any language), numbers (not first character),
underscores `_`, hyphens `-`, forward slashes `/` (for nesting).

Во frontmatter:

```yaml
---
tags:
  - tag1
  - nested/tag2
---
```
