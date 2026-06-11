---
name: ray3-video-ad
description: Use when the user wants to generate, edit, or reframe a VIDEO ad creative with Luma's ray-3.2 model — product b-roll, UGC-style clips, animation/stop-motion, cinematic spots, animating an existing image ad, restyling or reframing an existing video ad. Triggers on "ray 3.2", "Luma video", "video ad with Luma", "animate this image/product", "make b-roll", "reframe this video", "extend this clip", "restyle this video". Video only — for static image ads use uni1-image-ad instead.
---

# ray3-video-ad

Generate, edit, or reframe video ad creatives with Luma's **ray-3.2** model via the agents API. Companion to `uni1-image-ad` (images stay on uni-1; video is ray-3.2 — same API endpoint, same key).

## Hard rules — never relax

1. **Model is `ray-3.2`** for all video work. Never substitute `ray-2`, `ray-flash-2`, or any Dream Machine-era model, and never hit the legacy `api.lumalabs.ai` endpoint. The helper script enforces this.
2. **Cost gate before every paid generation.** Video costs real money ($0.15–$3.60 per clip). Always run the helper with `--dry-run` first, show the user the request + estimated cost, and get explicit approval before the real run. Default to 720p/5s for iteration; only go 1080p/HDR on an approved final.
3. **No audio exists.** ray-3.2 outputs silent video. Design every concept sound-off-first: motion hooks, supers described in the prompt, captions baked into the scene. Music/VO is post-production, outside this skill.
4. **No platform chrome** in generated video (same contract as images) — the script auto-appends the guard; `--allow-chrome` only with explicit justification.
5. **Meta upload of video ads is NOT yet wired.** The `meta` CLI flags for video creatives are unverified. Generate and review locally; if the user wants the ad uploaded, stop and say the Meta-video-upload phase still needs to be built (direct Marketing API `advideos` + `video_data` creative, like `create_text_variant_creative.py` does for text variants). Never improvise a mutation.
6. **Ads created in any future upload phase are `PAUSED`,** with the confirmation-gate and audit-log rules from `uni1-image-ad` carried over unchanged.

## The three modes

| Mode | What it does | Cost (per clip) |
|---|---|---|
| `video` | Text-to-video, image-to-video (`--start-frame`), interpolation (`--start-frame` + `--end-frame`), extend (`gen:<id>`), loop, HDR/EXR | 540p $0.15 · 720p $0.30 · 1080p $1.20 (5s SDR); 10s ×3; HDR ×2 |
| `video_edit` | Re-render an existing video under a new prompt; preserve motion/faces via `--strength adhere_*..reimagine_*`, `--auto-controls`, or per-signal `--controls-json`; up to 64 guide `--keyframe`s | dedicated tier — treat as ≥generation price |
| `video_reframe` | Outpaint to a new aspect ratio, source preserved frame-for-frame | $0.06–$0.36 per output second |

Constraint cheat-sheet: 10s = text-to-video SDR only · anything frame-anchored = 5s (chain extends for length) · HDR = 720p/1080p 5s · loop ≠ 10s/HDR/end-frame · reframe 9:16/3:4 maxes at 720p. Full reference: `docs/luma-agents-api/video-generation.md`, `video-editing.md`, `video-reframing.md` in the repo.

## The still-first workflow (default for product work)

Iterating in video at $0.30–$1.20 a take is wasteful. Nail the look in images first:

1. **uni-1 still** (~$0.04): generate the first frame with `uni1-image-ad`'s `generate_image.py`, grounding the product via `--image-ref` so packaging/wordmarks are faithful. Iterate here until the frame is right.
2. **Animate it**: `generate_video.py --start-frame <approved.png> --prompt "<motion direction>"`. The start frame carries brand fidelity; the prompt only has to direct motion.
3. **Before/after**: generate TWO uni-1 stills and interpolate (`--start-frame` + `--end-frame`).
4. **Length**: approved 5s clip → `--start-frame gen:<id>` to extend in 5s beats.
5. **Placements**: final master → `video_reframe` to 9:16 / 1:1 / 4:3.

## Workflow

### Phase 1: Preflight
1. `.env` has `LUMA_API_KEY` (video uses the same key/endpoint as uni-1).
2. Pick concept — load `references/video-concepts.md` (the concept library: b-roll, UGC, animation, stop-motion, cinematic, repurpose, clone) and match the user's ask to a template, or write fresh.

### Phase 2: Prompt + plan
Write the video prompt: subject, setting, **camera move** (dolly-in, orbit, handheld, locked-off), **motion content** (what changes over the 5s), lighting, style. State the beat structure for 5 seconds explicitly ("first 2s …, then …"). Decide mode, resolution, duration, aspect ratio, frames.

### Phase 3: Cost gate
Run with `--dry-run`, show the user the redacted request + estimated cost, get approval.

### Phase 4: Generate
```bash
python3 skills/ray3-video-ad/scripts/generate_video.py \
  --prompt "<rewritten prompt>" --aspect-ratio 9:16 --resolution 720p [--start-frame …]
```
Outputs land in `./generated/` as MP4 (presigned URLs die after 1h — the script downloads immediately). One JSON line per variant on stdout; `generation_id` is what extend/edit/reframe chain from.

### Phase 5: Review + iterate
Watch the clip (video-vision tooling if available, otherwise have the user review). Iterate at 720p; upscale the winner by re-running the same prompt/frames at 1080p (or HDR for premium placements). Then reframe for remaining placements.

### Phase 6: Delivery
Hand the user file paths + generation IDs. Meta upload: see hard rule 5.
