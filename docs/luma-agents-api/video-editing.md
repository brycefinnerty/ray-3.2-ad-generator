---
title: Video editing (ray-3.2) | Luma Agents
description: type "video_edit" — restyle, modify, and re-render existing video while preserving motion and performance.
---

`type: "video_edit"` re-renders an existing video under a new prompt while preserving (or deliberately loosening) the source's motion, composition, and performances. This is the "Modify" capability: live-action → animation, wardrobe/product swaps, background/era changes, style transfer — with lip sync, choreography, and facial performance carried over.

> Sourced from https://docs.agents.lumalabs.ai/guides/videos/editing/ (fetched 2026-06-11).

## Request shape

```json
{
  "prompt": "Same scene and motion, but the kitchen is now a sunlit Tuscan villa and the bottle is the summer colorway",
  "model": "ray-3.2",
  "type": "video_edit",
  "source": { "url": "https://example.com/ad.mp4", "media_type": "video/mp4" },
  "video": {
    "resolution": "720p",
    "edit": { "strength": "flex_2" }
  }
}
```

## Source video (exactly one shape)

```json
{ "generation_id": "<uuid>" }
{ "url": "https://example.com/video.mp4", "media_type": "video/mp4" }
{ "data": "<base64>", "media_type": "video/mp4" }
```

Constraints: source ≤ **30 seconds**, ≤ **200 MB** (URL/inline; `generation_id` is exempt from the size cap). `generation_id` must be a completed video generation from the same client.

## Edit conditioning — three mutually exclusive ways

### 1. Auto controls (recommended default)

```json
{ "video": { "edit": { "auto_controls": true } } }
```

The model derives the full conditioning schedule from the source automatically.

### 2. Strength presets — nine levels, three bands

```json
{ "video": { "edit": { "strength": "flex_2" } } }
```

| Band | Levels | Behavior |
| --- | --- | --- |
| `adhere_1..3` | subtle | Output closely preserves source motion, composition, structure — enhancements, set-dressing, colorway swaps |
| `flex_1..3` | balanced | Recognizable source, real changes — the common default for ad restyles |
| `reimagine_1..3` | loose | Prompt drives the output; source is grounding only — full restyles, live-action → animation |

### 3. Per-signal controls (fine-grained; cannot combine with `auto_controls`)

```json
{
  "video": {
    "edit": {
      "controls": {
        "pose":       { "enabled": true, "strength": "precise" },
        "depth":      { "enabled": true, "blur": 0.3 },
        "normals":    { "enabled": false, "augmentation": 0.5 },
        "trajectory": { "enabled": true, "sparsity": 0.2 },
        "face":       { "enabled": true }
      }
    }
  }
}
```

| Signal | Knobs | What it holds |
| --- | --- | --- |
| `pose` | `strength`: `precise` \| `coarse` | Skeleton / body movement |
| `depth` | `blur`: 0–1 (higher = more freedom) | Scene geometry |
| `normals` | `augmentation`: 0–1 | Surface orientation / relighting freedom |
| `trajectory` | `sparsity`: 0–1 (higher = fewer anchors) | Motion paths |
| `face` | `enabled` | Identity / expression preservation |

## Guide frames

**Single guide frame** (what the first output frame should look like — pairs perfectly with a uni-1 edited still of the source's first frame):

```json
{ "video": { "start_frame": { "url": "https://example.com/styled-frame.jpg" } } }
```

**Multi-keyframe** (this is where Ray 3.2's "multi-keyframe" control lives — up to **64** keyframes pinned to source frame indexes; mutually exclusive with `start_frame`):

```json
{
  "video": {
    "edit": {
      "keyframes":        [ { "url": "look0.jpg" }, { "url": "look90.jpg" } ],
      "keyframe_indexes": [ 0, 90 ]
    }
  }
}
```

Arrays must match in length. Each keyframe accepts the standard image shapes (`url` or `data`+`media_type`).

## Output settings

| Parameter | Notes |
| --- | --- |
| `video.resolution` | `540p` / `720p` (default) / `1080p` |
| `video.hdr` | 720p/1080p only |
| `video.exr_export` | requires `hdr: true` |
| `aspect_ratio` | **ignored** — output always matches the source |
| duration | not settable — output tracks the source clip |

## Pricing

Video edits bill on a dedicated tier with separate 5s/10s rates (distinct from generation pricing) — check the live pricing page before large batches. Failed/moderated jobs are refunded.
