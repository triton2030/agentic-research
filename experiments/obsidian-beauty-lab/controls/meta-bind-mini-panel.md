---
aliases:
  - Meta Bind Mini Panel
tags:
  - experiment/obsidian/control
demo_mode: system
---

> [!info]+ Embedded control block
> **Готово:** `INPUT[toggle:demo_done]`
>
> **Режим:** `INPUT[inlineSelect(option(research, research), option(design, design), option(system, system), option(playground, playground)):demo_mode]`
>
> **Прогресс:** `INPUT[slider(minValue(0), maxValue(100)):demo_progress]`
>
> `VIEW[{demo_title}]` · `VIEW[{demo_progress}]`%
