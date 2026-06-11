# Cinematic-ad playbook — validated lessons

Everything below was learned the expensive way on "Stitched" (June 2026). Follow it and a 15s ad lands in ~$4–5 and one revision round.

## Stills (uni-1)

- **Ground every product shot** with `--image-ref <product photo>`. No exceptions — ungrounded shots drift to generic lookalikes.
- **Pin the colorway in words, with negatives.** Grounding alone does NOT hold color under dramatic lighting — the end-card hat came back terracotta. Name every panel ("tan-khaki crown, golden-brown sides, DARK CHOCOLATE-BROWN front panel and flat brim") and add negative colors ("never red, never pink, never terracotta"). Warm scene light pulls browns red; specify "neutral color grade" on hero/end-card shots.
- **Never isolate product text in an extreme macro.** A patch/label filling the frame alone gets re-imagined (rotated gibberish glyphs). Frame text **in context on the product** at an angle similar to the reference photo — grounding then copies it faithfully.
- **Small product = weak grounding.** A hat-sized object in a wide lifestyle shot morphed into a different hat entirely. Either crop tighter or spell out shape + colorway in the prompt as backup.
- **Per-shot output dirs** (`stills/s1/`, `stills/s2/`…) then copy to canonical `shotN.png`. Same-prefix prompts in the same minute collide on slug+timestamp and silently overwrite.
- **End card: bake the supers into the still.** uni-1 renders display text better than any overlay tool; the end card is also the frame where overlay supers must be OFF (no double text).
- QC each still before animating: product match · colorway · text legibility · composition leaves a clear zone for the planned super.

## Motion prompts (ray-3.2)

- **Rigid products never rotate — the camera does.** Object rotation re-draws geometry every frame; flat planes (brims, lids, labels) inflate. Two failed spins; the fix: "the {PRODUCT} hangs perfectly still and rigid — its shape, size, and proportions never change. The CAMERA performs a smooth arc around it." Static object + camera move = zero deformation, same energy.
- **Demand continuous motion explicitly** on ambient/macro shots: "continuous, clearly visible motion for the entire clip — the light never stops moving." Otherwise you get a живая-photo opener that reads frozen.
- Text-bearing shots: append "the text stays perfectly static, sharp, and legible the entire time."
- Physical events (drop/land/tap) resolve in the clip's first ~1.5s. You'll cut ~2s windows from 5s clips, so plan the trim-in (`offset`) to put contact ~0.5–0.7s into the window.
- Constraint reminders: frame-anchored clips are 5s; 720p drafts; 4 concurrent jobs max on this account (the generate script auto-retries 429s).

## The grid edit

- 6–8 shots × 1.5–2.5s = fast-cut feel; the editor energy comes from cutting the **best ~2s window** out of each 5s clip, never the first 2s by default. Extract frames to choose offsets.
- J-cuts read professional: next VO line starts ~0.15s before its picture cut.
- Brief super/VO carryover across a cut (fading text crossing the boundary) reads as intentional trailer style — keep it under ~0.4s.

## Audio

- **VO durations drive the map, not vice versa.** Generate VO first (`make_audio.py` prints measured durations), then place lines. Voices pace wildly differently — David Trailer reads ~40% slower than premade voices and broke a map built for them.
- Voice defaults: **David Trailer** (epic, in the user's account from the shared library) · George (wry story). User rejected Adam ("not deep enough") and Brian ("not epic enough") for trailer work.
- Line gaps 0.3–0.4s. `atempo` up to ~1.15 is inaudible and buys back a long tail line.
- **Event SFX get pinned to observed frames, not planned marks.** After first assembly: extract ±0.1s frames around each physical event, find the contact frame, move the SFX, re-assemble. This found drift twice in one production (planned 2.45 → "verified" 2.68 → actually 2.50). One confirming frame is not verification; bracket it.
- Whooshes sit at cut points by construction; braam at 0; risers start with their shot; resolve on the end-card cut.
- Levels that landed (trailer format): SFX hits 0.50–0.55, ambience 0.30–0.35, music 0.30–0.32 under VO, master loudnorm `I=-14:TP=-1.5:LRA=9`. (Calmer story formats: SFX 0.32 / music 0.17 / I=-15.)
- Music prompts: describe the arc (dark pulse → build → triumphant finale), "instrumental, no vocals", **no brand or studio names** — moderation rejects them ("Aardman" bounced; "charming handmade animation feel" passed).
- ElevenLabs SFX cap: 22s per generation.

## HyperFrames supers

(HeyGen's open-source HTML→video renderer — `npx hyperframes init overlay`. The user may call it "Hayflow".)

- Composition: master mp4 as **muted** video layer + audio extracted to wav as a separate `<audio>` track + GSAP supers. 720×1280 viewport = composition size.
- **Every media element needs an `id`** — without it video renders frozen and audio silent. The linter flags this; `npm run check` after every edit and fix all errors.
- **Fonts must auto-resolve** in the headless renderer: Bebas Neue ✓ (and it's the canonical trailer face); system fonts like Avenir Next Condensed ✗ (silently falls back unless you @font-face a local woff2).
- GSAP: paused timeline registered on `window.__timelines["main"]`; position tweens at absolute seconds = the VO map transfers 1:1. Supported props only: opacity/x/y/scale/rotation (no letter-spacing tweens — set tracking in CSS).
- Animate exits to land just before the clip's `data-duration` end, or visibility hard-cuts mid-fade.
- **Placement is per-shot work**: render, then check every super against its shot's composition frame-by-frame. Center text collides with center product; lower-third is safest; keep inside the central 80% for platform UI. Overlay supers hard-out before the baked end card.
- Deterministic only (no Date.now / Math.random / fetch). Renders take ~11s — iterate freely.

## QC gates (in order)

1. Stills pass (before any clip money).
2. Per-clip frame check after animation (warp, motion present, text held).
3. Post-assembly sync pass (event SFX vs contact frames).
4. Post-overlay placement pass (supers vs composition).
5. **Final 2fps full-runtime pass + dense end-card check.** The end card is the most-remembered frame and where the colorway bug hid. Small-size spot checks miss color casts — review at ≥280px.

## Cost reference (15s, 7 shots, 720p draft)

| | |
|---|---|
| Stills incl. retakes | ~$0.50 |
| Clips incl. ~40% re-roll overage | ~$3.30 |
| ElevenLabs (VO + SFX + music) | ~$0.40 |
| HyperFrames | $0 |
| **Draft total** | **≈ $4.25** |
| 1080p finish | +$1.20/shot |
