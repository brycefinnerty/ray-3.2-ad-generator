---
title: Video reframing (ray-3.2) | Luma Agents
description: type "video_reframe" — outpaint an existing video to a new aspect ratio, preserving the source frame-for-frame.
---

`type: "video_reframe"` outpaints an existing video to a new target aspect ratio. The source content is preserved **frame-for-frame**; Ray 3.2 fills the newly exposed canvas around it, matching lighting and scene. This is the placement-coverage workhorse: one 16:9 master → 9:16 Reels, 1:1 feed, 4:3, etc.

> Sourced from https://docs.agents.lumalabs.ai/guides/videos/reframing/ (fetched 2026-06-11).

## Request shape

```json
{
  "prompt": "Extend the kitchen scene naturally — warm wood counters, soft window light continuing beyond the original frame",
  "model": "ray-3.2",
  "type": "video_reframe",
  "aspect_ratio": "9:16",
  "source": { "generation_id": "<uuid>" },
  "video": {
    "resolution": "720p",
    "source_position": { "x_norm": 0.0, "y_norm": 0.25, "w_norm": 1.0, "h_norm": 0.56 }
  }
}
```

## Parameters

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `prompt` | string | **required** | 1–6,000 chars — describes how to fill the new canvas |
| `model` | string | **required** | `"ray-3.2"` |
| `type` | string | **required** | `"video_reframe"` |
| `aspect_ratio` | string | **required** | Target: `9:16`, `3:4`, `1:1`, `4:3`, `16:9`, `21:9` |
| `source` | object | **required** | Same three shapes as video_edit (`generation_id` \| `url`+`media_type` \| `data`+`media_type`); ≤30s, ≤200 MB |
| `video.resolution` | string | `"720p"` | `540p` / `720p` / `1080p` |
| `video.source_position` | object \| null | auto centered-fit | Where the source sits in the new canvas |

### `source_position` (all four fields or none)

Normalized coordinates relative to the output canvas:

| Field | Range | Meaning |
| --- | --- | --- |
| `x_norm`, `y_norm` | −2.0 to 2.0 | Top-left position of the source |
| `w_norm`, `h_norm` | >0 to 2.0 | Source dimensions in canvas units |

Omit entirely for automatic centered fit.

## Constraints

- **Vertical targets at 1080p are unsupported** ("coming soon") — use 720p for 9:16 / 3:4.
- HDR, EXR export, looping, and frame trimming are all rejected on reframe.
- Output duration matches the source.

## Pricing

Reframe bills **per second of output**, standard tier only: $0.06–$0.36/s depending on resolution. A 10-second 720p reframe lands around $1.20; budget before batch-reframing long sources. Failed/moderated jobs are refunded.
