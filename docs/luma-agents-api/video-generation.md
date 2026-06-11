---
title: Video generation (ray-3.2) | Luma Agents
description: Text-to-video and image-to-video with Ray 3.2 — every parameter, frame anchors, extend, loop, HDR/EXR.
---

Ray 3.2 video generation goes through the same endpoint as image generation: `POST /v1/generations` with `type: "video"` and `model: "ray-3.2"`. Submit, poll `GET /v1/generations/{id}`, download the MP4 when `state: "completed"`.

> Sourced from https://docs.agents.lumalabs.ai/guides/videos/generation/ (fetched 2026-06-11). The agents platform is the canonical home of the Ray 3.2 API — the legacy Dream Machine API (`api.lumalabs.ai/dream-machine/v1`) only documents ray-2 era models.

## Request shape

```json
{
  "prompt": "Slow dolly-in on a glass jar of moisturizer on wet slate, steam curling, morning backlight",
  "model": "ray-3.2",
  "type": "video",
  "aspect_ratio": "16:9",
  "video": {
    "resolution": "720p",
    "duration": "5s",
    "loop": false,
    "hdr": false,
    "exr_export": false,
    "start_frame": { "url": "https://example.com/first.jpg" },
    "end_frame": { "url": "https://example.com/last.jpg" }
  }
}
```

## Parameters

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `prompt` | string | **required** | 1–6,000 characters |
| `model` | string | **required** | `"ray-3.2"` |
| `type` | string | **required** | `"video"` |
| `aspect_ratio` | string \| null | model picks | `9:16`, `3:4`, `1:1`, `4:3`, `16:9`, `21:9` |
| `video.resolution` | string | `"720p"` | `"540p"`, `"720p"`, `"1080p"` |
| `video.duration` | string | `"5s"` | `"5s"` or `"10s"` |
| `video.loop` | boolean | `false` | Seamless loop |
| `video.hdr` | boolean | `false` | HDR-encoded MP4 |
| `video.exr_export` | boolean | `false` | 16-bit EXR sidecar alongside the MP4 |
| `video.start_frame` | object \| null | — | Anchor first frame (image-to-video) |
| `video.end_frame` | object \| null | — | Anchor last frame |

### Frame object shapes

`start_frame` / `end_frame` each accept exactly one of three shapes:

```json
{ "url": "https://example.com/frame.jpg" }
{ "data": "<base64>", "media_type": "image/png" }
{ "generation_id": "<uuid-of-prior-generation>" }
```

`generation_id` references a prior completed generation by the same client — this is how **extend** works:

- `start_frame: {generation_id}` → forward-extend a prior video (new clip continues from its last frame)
- `end_frame: {generation_id}` → reverse-extend (new clip leads into its first frame)
- `start_frame` image + `end_frame` image → interpolation between two stills (before/after transitions)
- Interpolation from a prior generation **plus** another keyframe is not available yet — use a single `generation_id` keyframe for extend.

### Constraint matrix (rejected combinations)

| If you set… | You cannot set… |
| --- | --- |
| `duration: "10s"` | `hdr`, `start_frame`, `end_frame` |
| `loop: true` | `duration: "10s"`, `hdr`, `end_frame` |
| `hdr: true` | `resolution: "540p"`, `duration: "10s"`, `loop` |
| `exr_export: true` | anything without `hdr: true` |

Practical reading: **10s clips are text-to-video SDR only.** Anything anchored on a frame (i2v, extend, interpolate) is 5s — chain extends to go longer. HDR is 5s @ 720p/1080p.

> Multi-keyframe ("up to 16 keyframes" in Ray 3.2 marketing) is **not** part of `type: "video"`. Keyframe arrays live in `type: "video_edit"` (`video.edit.keyframes`, up to 64) — see [video-editing.md](./video-editing.md).

## No audio

Ray 3.2 on the agents API generates **silent video**. There is no audio/voiceover/music parameter. Plan ads accordingly: design for sound-off (supers, captions baked into the prompt) or add music/VO in post.

## Response & polling

`201` returns `{id, state: "queued", ...}`. Poll `GET /v1/generations/{id}` until `completed`/`failed`. Typical 5s/720p completes in under 2 minutes; 10s, 1080p, and HDR take proportionally longer. Output MP4 (and EXR when requested) are presigned URLs that **expire after 1 hour** — download immediately, re-poll to mint fresh URLs.

## Pricing (pay-as-you-go, per clip)

| Resolution | 5s SDR | 10s SDR | 5s HDR | 5s HDR+EXR |
| --- | --- | --- | --- | --- |
| 540p | $0.15 | $0.45 | — | — |
| 720p | $0.30 | $0.90 | $0.60 | $0.90 |
| 1080p | $1.20 | $3.60 | $2.40 | $3.60 |

Single-keyframe extend bills like a standard generation ($0.15–$1.20 per extend, SDR only). Failed/moderated generations are refunded.

## Rate limits

Video shares the same RPM + concurrent-job bucket as image generations (see [rate-limits.md](./rate-limits.md)). A video job occupies a concurrency slot from submit until terminal state — budget for multi-minute holds when batching.
