---
name: claymation-ad
description: Use when the user wants a claymation / stop-motion style VIDEO AD with story, consistent characters, voiceover, sound effects, and music — produced end-to-end with uni-1 (stills), ray-3.2 (animation), and ElevenLabs (VO/SFX/score). Triggers on "claymation ad", "clay ad", "stop-motion ad/video", "animated story ad", "make a video like The Lab". Builds multi-beat narrative films (15s–60s+), not single clips — for one-off video beats use ray3-video-ad instead.
---

# claymation-ad

End-to-end claymation story ads on a beat grid: every beat is a 5s ray-3.2 clip anchored on a uni-1 still, characters stay consistent via reference sheets, and audio (ElevenLabs VO + per-scene SFX + score) is mixed on a VO-driven "punchy" timeline. Validated by producing "The Lab" (45.7s, 12 beats) for The AI Ad Alchemists — see `references/example-project/`.

Depends on sibling skills' scripts (same repo): `skills/uni1-image-ad/scripts/generate_image.py` and `skills/ray3-video-ad/scripts/generate_video.py`. Their hard rules (uni-1 / ray-3.2 lock, cost gates, PAUSED ads) all apply.

## The architecture (why this produces consistent characters)

```
brand research ──► beat map + VO script (≤ ~2.4 words/sec of beat time)
       │
reference sheets (uni-1):  clay character sheets + environment master
       │                   ← ground a real person via --image-ref photo
scene anchor stills (uni-1, one per beat):
       │                   ← --image-ref = character sheets + environment
animated beats (ray-3.2):  --start-frame = approved still, 720p draft
       │
audio (ElevenLabs):        VO per beat → SFX per beat → score
       │
claymation_pipeline.py:    timeline plan → punchy cut → full mix
```

Consistency chain: **character sheet → image_ref in every still → start_frame in every clip.** The model never improvises a character from text alone.

## Workflow

### Phase 1 — Brief
1. Research the brand/offer (their site, Skool page, winning ads via `top_spending_ads.py`). Pull positioning, audience, proof points, brand world. If a winning visual asset exists (e.g. a thumbnail), use it as the style seed.
2. Elicit four decisions (AskUserQuestion): aspect ratio (9:16 default), cast (clay-ify the real founder? get explicit OK for likeness), audio plan (ElevenLabs needs `ELEVENLABS_API_KEY` in `.env`), budget tier (default: 720p draft → 1080p finish).

### Phase 2 — Story
Write a three-act beat map: N beats × ~5s (12 beats ≈ 45–60s final). Per beat: scene description + VO line. **Word budget: ≤ ~12 words per 5s beat** (2.4 words/sec); lines may bleed ~1s into the next beat (J-cut) but never two beats. Text-on-screen only where it's load-bearing (sign, machine label, end card) — short and large. Get user approval on the beat map BEFORE generating anything.

### Phase 3 — Reference sheets (uni-1, ~$0.05 each)
Generate full-body character sheets (2:3) and an environment master (target AR). Recipes in `references/prompt-recipes.md`. Real-person characters: `--image-ref <their photo/thumbnail>`. Show the user the cast; iterate here — it's the cheapest place to fix design.

### Phase 4 — Scene anchor stills (uni-1, one per beat)
Each still: `--image-ref` every character sheet appearing in the scene + the environment master (≤9 refs), target AR, style tokens from the recipes file. **Run generations into per-beat output dirs or re-download via generation_id — same-prefix prompts collide on output slugs.** QC every still (Read them): character on-model, text exact, composition leaves motion headroom. Retake failures (~$0.05) before animating. Show the user the storyboard; gate here.

### Phase 5 — Animate (ray-3.2, $0.30/beat at 720p)
Per beat: `generate_video.py --start-frame <still> --aspect-ratio <AR> --resolution 720p --out <project>/clips/bNN`. Motion prompts: stepped 12fps cadence language, ONE primary action per beat, camera locked or slow push, and name every on-screen text string with "stays perfectly static and legible". **Batch ≤4 concurrent** (account video concurrency limit; the script auto-retries 429s but don't lean on it). Cost-gate first with the per-beat total.

### Phase 6 — Audio + assembly (`scripts/claymation_pipeline.py`)
1. Write `<project>/project.json`: voice, per-beat `vo` + `sfx` prompts, `music_prompt` (see recipes; **never name studios/artists/brands in the music prompt — moderation rejects them**).
2. `python3 …/claymation_pipeline.py <project> vo` — per-beat VO lines, durations printed; rewrite any line that runs >1s over its beat.
3. `plan` — VO-driven punchy timeline: 0.4s gaps, beats clamped 3–5s, J-cuts, end-card hold. This is what makes it feel edited, not generated.
4. `sfx` + `music` — per-scene foley (durations auto-matched) and a score arced to the story, exact runtime.
5. `mix` — trims clips to the timeline, lays VO/SFX/music (defaults: SFX 0.32, music 0.17, loudnorm −15 LUFS — SFX above 0.4 drowns VO), writes `<project>/master.mp4`.

### Phase 7 — QC + finish
1. Vision QC the master: `video_analyze` (scene_changes confirm cuts; loudness ≈ target), then frame-per-beat visual pass — character drift, text integrity, motion landed.
2. Retake list → re-roll only failed beats (stills are cached; $0.30 each), `mix` again.
3. On approval: re-render all beats at 1080p (same stills + prompts, ~$1.20 each), `mix` → final. Note: 9:16 1080p generation is supported (only *reframe* restricts vertical 1080p).
4. Meta upload of video ads is NOT wired into the CLI — hand off the file, or stop and propose building the upload helper.

## Hard-won rules (violations cost money or quality)

1. **Still-first always.** Never iterate look/text/casting at video prices. Fix it at $0.05, animate at $0.30, finish at $1.20.
2. **Text lives in stills, not motion prompts.** ray-3.2 holds baked-in static text nearly perfectly; it cannot *add* clean text. Keep strings short, large, and repeated verbatim in the motion prompt as "stays static and legible".
3. **Matte clay tokens everywhere** (see recipes) — without "zero glossy/translucent materials" the model reverts to realistic materials; glass flasks are the allowed exception.
4. **Dense/small UI text never survives animation.** Don't build beats around it.
5. **Concurrency 4, slug collisions, 1h URL expiry** — batch ≤4 videos, per-beat output dirs, download immediately (re-poll generation_id for a fresh URL if missed).
6. **ElevenLabs moderation** rejects music prompts naming studios/artists; describe the sound instead.
7. **.env appends need a leading newline check** — a missing trailing newline once glued two secrets into one line.
8. **Cost gates at every paid phase**, totals stated up front. "The Lab" reference costs: refs+stills ≈ $1.20, 12×720p beats $3.60, retakes ~$0.65, total ≈ $5.50 + ~3k ElevenLabs credits.
