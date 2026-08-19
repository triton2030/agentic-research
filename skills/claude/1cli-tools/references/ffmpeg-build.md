---
description: "Hardware and quality capabilities compiled into active FFmpeg 9.0.1."
---

# FFmpeg 9: Active Build

Момент: выбирается codec/quality route на этом Mac. Сверено 2026-08-19 с active
Homebrew FFmpeg 9.0.1; build options меняются при reinstall/upgrade.

## Локальная Дельта

Эта сборка уже содержит:

- VideoToolbox encoders `h264_videotoolbox`, `hevc_videotoolbox`,
  `prores_videotoolbox`;
- software AV1 encoder `libsvtav1`;
- quality filters `libvmaf` и `vmafmotion`.

Канонический владелец именно локальной сборки:

```bash
ffmpeg -hide_banner -encoders | rg 'videotoolbox|svtav1|prores'
ffmpeg -hide_banner -filters | rg 'vmaf'
ffmpeg -buildconf
```
