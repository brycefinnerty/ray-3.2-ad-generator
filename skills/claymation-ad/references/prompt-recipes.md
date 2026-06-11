# Claymation prompt recipes

Validated patterns from "The Lab" production (2026-06-11). Copy the skeletons, fill the {SLOTS}.

## The style token block (append to EVERY uni-1 still prompt)

> Handcrafted claymation stop-motion style, matte modeling clay with visible fingerprint texture, zero glossy or translucent materials except glass flasks, miniature diorama set, soft warm studio lighting, vertical cinematic composition.

- "matte … zero glossy or translucent" is load-bearing — without it the model mixes realistic materials (round 1: ice cubes stayed glassy at `reimagine_2`).
- Adjust the exception clause ("except glass flasks") per project, or drop it.

## Character sheet (uni-1, 2:3, ~$0.05)

> Claymation character sheet: {a friendly clay sculpture of the man from the reference image — {REAL FEATURES: cap, glasses, beard, shirt} | an {ARCHETYPE} sculpted in clay — {INVENTED FEATURES}}, reimagined as {ROLE/COSTUME}. Full body, 3/4 standing pose, {EXPRESSION}, standing in an empty neutral clay workshop. + style tokens

- Real person: pass their photo/winning thumbnail via `--image-ref`. Likeness → clay works remarkably well; get the person's OK first.
- Make co-stars visually disjoint (explicit "NO hat, NO beard" carved Dave away from Caleb).
- The sheet's job is downstream grounding — neutral background, full body, no props that would leak into every scene.

## Environment master (uni-1, target AR)

> Claymation environment master shot, vertical composition: {WORLD rebuilt entirely in matte modeling clay — palette, materials, signature props, lighting}. NO characters, NO text anywhere. + style tokens

Ground on a brand visual via `--image-ref` when one exists. "NO characters, NO text" keeps it reusable for every scene.

## Scene anchor still (uni-1, one per beat)

> {Same clay character as the reference (RESTATE 3-4 IDENTIFYING FEATURES)} {ACTION/POSE} in {SETTING SLICE}, {KEY PROPS}, {LIGHTING/MOOD}. {TEXT ELEMENTS: a sign reading "EXACT TEXT"}. + style tokens

- `--image-ref`: every character sheet in the scene + environment master (≤9).
- RESTATE features in words even though the ref image is attached — belt and suspenders is what held identity across 12 scenes.
- Recurring sets (e.g. the office in beats 1/2/3/9): repeat the same scene-slice wording verbatim in each prompt; cuts tolerate minor set drift, characters don't.
- Text: short, large, in quotes. Multi-word brand text is fine ("THE AI AD ALCHEMISTS", "SKOOL.COM/MRPAIDSOCIAL" both rendered perfectly). Gauge-face/instrument text needs an explicit "ONLY the single word X, no other text or numbers" (first ROAS gauge garbled without it).
- Leave motion headroom: mid-action poses (lever half-pulled, liquid mid-pour) animate better than completed actions.

## Motion prompt (ray-3.2, i2v from the still)

> Stop-motion claymation: {ONE primary action, described as a sequence}, {2-3 secondary ambient motions: steam, flicker, bob}. Camera {locked off | very slow gentle push-in}. {The sign text "EXACT TEXT" stays perfectly static and legible the entire clip.} Stepped 12fps stop-motion cadence, {handcrafted jitter | handcrafted charm}.

- ONE primary action per 5s beat. Two actions = neither lands.
- Re-quote every visible text string with "stays perfectly static and legible" — this held 6/6 text elements in The Lab.
- "Stepped 12fps stop-motion cadence" sells the medium; "subtle handcrafted jitter" adds charm without wobble.
- Camera: locked off by default; one slow push-in per act maximum. Claymation reads fake with sweeping camera moves.

## VO lines (ElevenLabs)

- Budget ≤ ~12 words per 5s beat (2.4 w/s). Lines may bleed ~1s into the next beat (the pipeline J-cuts around it); >1s over means rewrite.
- Wry nature-doc third person ("This is Dave…") suits claymation; George (storyteller) validated, Roger/Bill are alternates.
- Numbers: write out what must be spoken precisely ("a hundred and fifty million dollars").

## SFX prompts (ElevenLabs /v1/sound-generation)

> {stop-motion foley | ambience}: {2-4 concrete sound events matching the beat's visible actions}, {texture words: papery, clunky, weighty, whimsical}

- Derive from what's VISIBLE in the beat — the audience pairs sound with picture instantly.
- Lead with "stop-motion foley" for action beats, "ambience" for mood beats; end-card gets a "soft triumphant shimmer".
- Duration is auto-matched to the beat by the pipeline; mix at ≤0.32 volume or it masks VO (0.45 was too loud).

## Music prompt (ElevenLabs /v1/music)

> {GENRE/MOOD} score, fully instrumental, no vocals: opens {ACT-1 MOOD + instruments}; {ACT-2 SHIFT + instruments}; builds to {ACT-3 RESOLUTION + instruments}, ending on {FINAL GESTURE}. {HANDMADE-FEEL descriptor}.

- Arc the three clauses to the three acts — the model genuinely follows the progression.
- **NEVER name studios, artists, or brands** ("Aardman energy" → hard moderation reject). Describe the sound instead ("charming handmade animation feel").
- Request `music_length_ms` = timeline total; it returns the exact length.

## Mix defaults (validated)

| Layer | Level | Note |
|---|---|---|
| VO | full | the spine; everything else serves it |
| SFX | 0.32 | 0.45 drowned VO |
| Music | 0.17 | bed, not feature |
| Master | loudnorm −15 LUFS, TP −1.5 | lands ≈ −15.8 mean, social-ready |
