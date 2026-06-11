---
name: cinematic-ad
description: Use when the user wants a CINEMATIC, fast-cut, trailer-style VIDEO AD for a product — multiple quick shots cut to a beat grid, movie-trailer voiceover, sound design (whooshes/impacts/risers), original score, and motion-graphic text supers synced to the VO. Triggers on "cinematic ad", "trailer-style ad", "fast-cut ad", "epic product ad", "product trailer", "hype video for my product". Produces a finished 15–30s master end-to-end (uni-1 stills → ray-3.2 shots → ElevenLabs audio → HyperFrames supers). For story-driven claymation use claymation-ad; for single clips use ray3-video-ad.
---

# cinematic-ad

Produce a fast-cut cinematic product ad end-to-end. Validated by "Stitched" (15s, 7 shots, ~$4.15 all-in, June 2026). The whole pipeline keys off one **project.json** manifest — see `references/project-template.json`.

## Hard rules — never relax

1. **Models locked:** uni-1 (stills) / ray-3.2 (video) on `agents.lumalabs.ai`. ElevenLabs for VO/SFX/music. The helper scripts enforce the Luma locks.
2. **Cost gate:** present the beat map with estimated cost (stills ≈ $0.05 ea, clips $0.30 ea at 720p) and get approval before the still pass AND before the animation pass. Draft at 720p; 1080p only on the approved final.
3. **Product fidelity is the contract.** Every shot that shows the product anchors on a real product photo via `--image-ref` (ask the user for the file if not in `Reference Images/`). QC every still AND the final frames against the photo — **including colorway** (see playbook §colorway).
4. **Max 4 concurrent Luma jobs** (account cap). Batch 4-wide; the generate script retries 429s automatically.
5. **Frame-accurate audio.** Never place an event SFX on a planned mark — find the visible contact/event frame with dense extracts (±0.1s) and pin the SFX to it.
6. **QC before every delivery:** frame-by-frame pass at 2fps minimum over the full runtime + dense extracts at sync points and the end card. The end card is the most-remembered frame — check it hardest.
7. No platform chrome; PAUSED-only if a Meta upload phase ever runs (inherited from ray3-video-ad).

## Pipeline (9 phases)

### 1. Brief → beat map
Fixed total runtime (15s standard). 6–8 shots, each 1.5–2.5s on the master grid, cut from 5s ray clips. Draft the table: shot | window | visual | VO line | SFX events | super copy. Sparse trailer VO (≤30 words for 15s). Standard arc: texture macro hook → product reveal (drop/land) → detail macro → lifestyle beat → hero worship (god rays) → motion flex → end card with baked supers.

### 2. Audio first
Write `project.json`, then `scripts/make_audio.py --project project.json` — generates VO lines, SFX stingers, and the music cue (exact runtime) and prints measured durations. **VO durations drive the timing map** — voices pace differently (David Trailer reads ~40% slower than premade voices; re-map slots to measured durations, don't assume).
- Default trailer voice: **"David Trailer"** (in the user's ElevenLabs voice list, added from the shared library). Wry narration: George. Confirm with the user.
- Music prompt: describe arc (dark pulse → build → finale), instrumental, no brand/studio names (moderation rejects them).

### 3. Stills (uni-1, ~$0.05/shot)
One 9:16 still per shot via `uni1-image-ad/scripts/generate_image.py`, every product shot grounded with `--image-ref <product photo>`. Output to per-shot dirs (`stills/sN/`) — identical prompt prefixes collide on slug+timestamp otherwise. Copy to canonical `shotN.png`. **QC each still** against playbook §stills before animating. Retake at $0.05, never animate a flawed still.

### 4. Animate (ray-3.2, $0.30/shot draft)
`ray3-video-ad/scripts/generate_video.py --start-frame stills/shotN.png --aspect-ratio 9:16 --resolution 720p`, 4-wide batches. Motion prompts per playbook §motion (camera moves not object moves for rigid products; explicit continuous motion for ambient shots; "text stays static sharp legible" on every text-bearing shot).

### 5. Assemble
`scripts/assemble.py --project project.json` — trims each clip to its window (offset + duration), concats on the grid, lays VO/SFX/music at the mapped times, masters to −14 LUFS. Choose each shot's `offset` by extracting frames: the best ~2s of a 5s clip is rarely the first 2s.

### 6. Sync verification
For every physical event SFX (impact, landing, tap): dense frame extracts at ±0.1s around the planned mark → move the SFX to the observed contact frame → re-assemble. This ALWAYS finds drift; budget for it.

### 7. Motion-graphic supers (HyperFrames)
`npx hyperframes init overlay` next to the master. Composition: master video as muted layer + extracted `mix.wav` audio track + GSAP supers timed to the VO map. Rules that bite (playbook §hyperframes): media elements need `id` or they render frozen/silent; use auto-resolving fonts (Bebas Neue — the right trailer face anyway); `npm run check` after every edit; verify super placement against each shot's composition frame-by-frame — center-placed text WILL collide with the product eventually. Render ≈ 11s, so iterate freely.

### 8. Full QC pass
2fps frame review of the entire render + dense passes at: every SFX event, every super in/out, the end card. Checklist: product colorway in every shot · no warp/deformation · supers legible and collision-free · text carryover across cuts is intentional · baked end-card text not doubled by overlay supers.

### 9. Finish
On approval: re-run animation at 1080p for approved shots (same stills/prompts, ~$1.20 ea), re-assemble, re-render supers (resolution-independent). Then reframe for placements via `video_reframe` if needed.

## Cost reference (15s / 7 shots)
Draft: ~10 stills $0.50 + ~11 clips (incl. retakes) $3.30 + ElevenLabs ~$0.40 ≈ **$4.25**. 1080p finish: +$8.40. Budget 30–50% clip overage for re-rolls — motion and physics flaws only show after animation.

## References
- `references/cinematic-playbook.md` — every validated lesson: still QC rubric, motion-prompt patterns, warp avoidance, colorway pinning, VO pacing, HyperFrames gotchas, sync method.
- `references/project-template.json` — manifest schema, populated with the "Stitched" worked example.
