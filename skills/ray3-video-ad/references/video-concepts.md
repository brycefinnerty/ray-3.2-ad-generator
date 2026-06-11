# ray-3.2 video ad concept library

Parameterizable video-ad concepts for Meta, organized by use case. Each entry lists the API pipeline (which ray-3.2 features it rides on), recommended specs, estimated cost per take, and a prompt/recipe skeleton. `{PRODUCT}`, `{BRAND}`, `{BENEFIT}`, `{SETTING}` are fill-ins.

Two structural facts shape every concept here:
- **Clips are 5s (10s for pure text-to-video).** Longer cuts = chain extends (`--start-frame gen:<id>`) in 5s beats, or stitch in post.
- **Output is silent.** Every concept must work sound-off: motion is the hook, supers are described in the prompt, VO/music happens in post.

Cost shorthand: 720p/5s SDR = $0.30 ("1 take"). Iterate at 720p, finish at 1080p ($1.20) or HDR ($2.40).

---

## A. Product b-roll

**A1 — Hero orbit.** uni-1 still of {PRODUCT} (image_ref-grounded) → i2v: "slow 90° orbit around the product, shallow depth of field, studio softbox lighting, background bokeh drifting." Loop-friendly. `video` + start_frame, 1:1 or 4:5→3:4, 5s. ~$0.34/take incl. still.

**A2 — Texture macro.** The sensory close-up: pour, smear, fizz, steam, crumble. "Extreme macro, {PRODUCT TEXTURE} slowly {ACTION}, specular highlights, 120fps slow-motion feel." Pure t2v works (no exact label visible) — or start_frame when packaging is in frame. `video`, 9:16, 5s. $0.30.

**A3 — Seamless ambient loop.** Shelf/kitchen/vanity scene with {PRODUCT}, micro-motion only (steam, dust motes, light shifting, plant swaying). `--loop` makes it cycle invisibly in-feed — autoplay never visibly restarts. `video` + start_frame + loop, 1:1, 5s. $0.30.

**A4 — Before/after interpolation.** Two uni-1 stills — messy desk → organized with {PRODUCT}; dull skin → glowing; tangled cables → clean setup — and ray-3.2 invents the transformation between them. THE transformation-promise format. `video` + start_frame + end_frame, 9:16 or 1:1, 5s. ~$0.38 incl. two stills.

**A5 — Ingredient cascade.** "Ingredients of {PRODUCT} fall in slow motion against {COLOR} seamless background — {INGREDIENT LIST} tumbling, then the bottle lands center frame" with end_frame = product still so it resolves on faithful packaging. `video` + end_frame, 9:16, 5s. $0.34.

**A6 — Unboxing hands.** "Overhead shot, hands lift the lid off {PRODUCT} box, tissue paper parts, product revealed, soft window light" — start_frame from a uni-1 packaging still. `video` + start_frame, 9:16, 5s. $0.34.

**A7 — 15s b-roll reel via extend chain.** A1 orbit → extend "camera pulls back revealing the full {SETTING}" → extend "hand enters and lifts the product". Three 5s beats, one continuous shot, cut points free. `video` + 2 extends, ~$0.90 total at 720p.

## B. UGC-style

(Silent-video reality: fake "talking" UGC reads as broken without audio. Lean on demo/POV/reaction formats where mouths don't carry the message; captions belong in post or in supers.)

**B1 — POV phone demo.** "Handheld vertical phone footage, slightly shaky, someone demonstrates {PRODUCT} {ACTION} on a {SETTING}, harsh indoor lighting, authentic amateur framing." The deliberately-unpolished look that out-performs studio polish. `video`, 9:16, 720p (crispness reads as ad), 5–10s. $0.30–$0.90.

**B2 — Mirror routine.** "Vertical mirror selfie framing, person mid-routine applies {PRODUCT}, bathroom counter cluttered with real products, morning light." `video`, 9:16, 5s. $0.30.

**B3 — Reaction + product reveal.** Beat 1: face lights up looking at {PRODUCT} off-frame; beat 2 (extend): cut-in of what they saw. Pair with post-added caption "when the {BENEFIT} kicks in". `video` + extend, 9:16, 10s total. $0.60.

**B4 — Real-UGC restyle (rights required).** Take YOUR existing UGC footage → `video_edit` `adhere_2`/`flex_1`: swap in the new colorway/flavor/packaging, keep the creator's motion, face, and energy. One filmed asset becomes a seasonal/SKU family. ⚠️ only on footage you own rights to.

**B5 — Street-interview look.** "Vertical street-interview framing, person gesturing enthusiastically mid-conversation, urban sidewalk, golden hour, mic in frame" + post captions carrying the testimonial text. `video`, 9:16, 5s. $0.30.

## C. Animation

**C1 — Mascot spot.** "{STYLE: Pixar-style 3D / 2D rubber-hose / felt-puppet} character {MASCOT DESCRIPTION} discovers {PRODUCT}, delighted bounce, {SETTING}, expressive squash-and-stretch." Brand the mascot via uni-1 character sheet → start_frame. `video` + start_frame, 1:1/9:16, 5s. $0.34.

**C2 — Kinetic-type stat card.** Animated typography for the one number that sells: "Bold kinetic typography, the text '{STAT}' assembles from particles, {BRAND COLOR} background, punchy easing, subtle camera push-in." Keep copy SHORT (one stat + 3-4 words) — text fidelity degrades with length; regenerate until clean. `video`, 1:1, 5s. $0.30.

**C3 — Live-action → animation flip.** `video_edit` `reimagine_2` on existing footage: "same scene as anime / claymation / watercolor". Motion and blocking survive, world restyles. The mid-clip style-flip (real → animated at 50%) is its own scroll-stopper via keyframes: real-style frame at index 0, animated frame at the flip point. `video_edit` + keyframes.

**C4 — Logo-morph end-card.** "Abstract {BRAND COLORS} fluid ribbons swirl and resolve into the {BRAND} logo, centered, dark background" — end_frame = exact logo still from uni-1. Loop the master 3s cut in post. `video` + end_frame, 1:1, 5s. $0.34.

**C5 — Whiteboard explainer beat.** "Hand-drawn line-art animates itself onto white paper: {PROBLEM DIAGRAM} sketches in, then {PRODUCT} sketch resolves and fills with color." `video`, 1:1/16:9, 5–10s. $0.30–$0.90.

## D. Stop-motion

(ray-3.2 renders the stepped-motion *aesthetic* from the prompt; for true frame-by-frame authorship, drive it with keyframes via video_edit.)

**D1 — Claymation product world.** "Stop-motion claymation, 12fps stepped motion, fingerprint texture on clay, {PRODUCT} hops across a miniature clay {SETTING}, handcrafted charm, slight flicker." `video` + start_frame (clay-styled uni-1 still), 1:1, 5s. $0.34.

**D2 — Flatlay choreography.** "Overhead stop-motion: {ITEMS} slide, snap, and rearrange themselves into a perfect grid around {PRODUCT}, paper-craft shadows, stepped 12fps motion." Classic for food/cosmetics/EDC. `video` + start_frame, 1:1, 5s. $0.34.

**D3 — Keyframe-authored stop-motion (the power move).** Generate N uni-1 stills of {PRODUCT} in successive poses (consistent via image_ref chaining) → `video_edit` with `--keyframe` × N pinned to `--keyframe-indexes` — up to 64 frames of explicit pose-by-pose control. This is the closest thing to hand-animating with a generative model. Cost: N × $0.04 stills + one edit run.

**D4 — Paper-craft assembly.** "Layered paper-craft pieces fold and assemble into {PRODUCT/SCENE}, stop-motion cadence, visible paper grain, drop shadows." `video`, 9:16, 5s. $0.30.

## E. Cinematic

**E1 — Premium hero spot (HDR).** "Anamorphic 2.39:1 feel, {PRODUCT} on {DRAMATIC SURFACE}, volumetric light shaft sweeps across, dust particles, slow 10° orbit, high-contrast rim lighting." 21:9 AR, 1080p + `--hdr` for the final ($2.40); EXR if it's going through a grade ($3.60). `video` + start_frame.

**E2 — Three-beat mini-film via extend.** Beat 1: tension/problem in cinematic light → extend beat 2: product enters → extend beat 3: resolution + logo end-card (end-frame chaining is per-clip; land the logo via prompt or cut to C4 in post). 15s, ~$0.90 at 720p iterate / ~$3.60 at 1080p finish.

**E3 — Impossible camera move.** The signature AI-video flex: "camera flies through the {PRODUCT} bottle interior, through amber liquid, bubbles parting, emerges out the other side into {SETTING}" — physically unshootable, reads premium. `video`, 9:16/16:9, 5s. $0.30–$1.20.

**E4 — Atmosphere-first brand film.** No product until the last beat: "slow dolly through {EVOCATIVE SETTING}, {WEATHER/LIGHT}, cinematic color grade" → extend with product reveal. Works for fragrance/wellness/finance feel campaigns. 10s+. $0.60+.

**E5 — Macro-to-wide reveal.** "Starts as extreme macro of {TEXTURE}, camera pulls back and cranes up, revealing it was {SURPRISE WIDER SCENE}" — built-in curiosity hook for the first 2 seconds. `video`, 9:16, 5s. $0.30.

## F. Repurposing existing assets (highest ROI in the account)

**F1 — Animate the winning image ad.** Pull top spenders via `top_spending_ads.py`, take the proven static, run i2v: "subtle parallax, light sweep across the headline, product breathes, steam rises" — the static you already know converts, now with motion to fight feed blindness. `video` + start_frame(winning PNG), 5s. $0.30/ad. **Do this to the whole top-10 first; it's the cheapest test with the strongest prior.**
⚠️ The no-chrome guard suffix conflicts with statics that ARE platform-style mockups (T1 Notes listicle etc.) — pass `--allow-chrome` when animating those, since the chrome is the creative.

**F2 — Placement multiplication.** Every video master → `video_reframe` to 9:16 (Reels/Stories), 1:1 (feed), 4:3. Source preserved frame-for-frame, ray-3.2 outpaints the new canvas with matching lighting; `--source-position` controls where the original sits. ~$0.30–$0.60 per 5s placement at 720p. One shoot → full placement coverage.

**F3 — Seasonal/SKU refresh.** `video_edit` `adhere_2` on a proven video ad: "same everything, but winter — frost on the window, warm tungsten light" or swap the hero SKU colorway. Performance structure intact, creative reads fresh. Beats re-shooting.

**F4 — Extend the winner.** A 5s hook that's working → `--start-frame gen:<id>` to add a payoff/CTA beat without touching the proven opening.

**F5 — Live-action → animated variant.** `video_edit` `reimagine_1-2` on your best performer: anime/clay/illustration version of the exact same ad. Same motion, new audience segment, A/B against the original.

**F6 — Talking-ad facelift.** Old talking-head ad with dated set/wardrobe → `video_edit` with `face` + `pose` controls enabled: keep the speaker's performance and lip movement (your post-production audio still syncs), restyle everything around them.

## G. Cloning ad structures

(Clone the *structure*, never the assets. Feeding a competitor's footage into video_edit is both a rights problem and lazy — the durable move is reverse-engineering the format into a parameterized template, exactly like `image-ad-clone` does for statics.)

**G1 — Beat-map clone.** Watch a winning ad (yours or a swipe-file reference), write its beat map — 0-2s hook type, 2-4s demo type, framing, pacing, camera grammar — then re-shoot it via t2v/i2v with {YOUR PRODUCT} in every slot. The concept entries above are all pre-chewed beat maps.

**G2 — Frame-anchor clone.** For a static-ad-style you admire: rebuild the layout as a uni-1 still with YOUR brand (image-ad-clone skill), then animate per F1. Two skills chained = video clone of any image-ad format in the swipe file.

**G3 — video-ad-clone (future skill).** The systematic version of G1: given a reference video, extract a parameterizable video-prompt template (beat map + camera grammar + style tokens) and append it to this library. Build once validated, mirroring image-ad-clone's template-format.

---

## Picking specs quickly

| Destination | AR | Res | Notes |
|---|---|---|---|
| Reels / Stories | 9:16 | 720p (1080p reframe unsupported for vertical) | safe-zone supers, hook in first 2s |
| FB/IG feed | 1:1 or 4:3 | 720p iterate → 1080p final | loop where possible |
| In-stream / YT | 16:9 | 1080p | E-series concepts |
| Premium brand | 21:9 / 16:9 | 1080p HDR (+EXR if grading) | E1 |

Iterate everything at 720p/5s SDR ($0.30). Finish winners at 1080p. Never start at HDR.

---

## Validation log — round 1 (2026-06-11, Mr. Paid Social account)

Six concepts tested live; frame-by-frame vision review. Ratings are Meta-readiness.

| Concept | Result | Rating |
|---|---|---|
| F1 animate designed static (Ad Alchemists thumbnail) | ✅ Ship-ready. All sign text pixel-stable for full 5s, identity stable, natural smile + hand motion, gentle push-in. **Best ROI validated.** | 9/10 |
| F1 animate dense-UI screenshot (Airtable demo) | ❌ Layout/colors held but small text re-rendered as pseudo-glyphs, number chips wobble, and prompted cursor/click motion never executed. **Don't animate dense UI** — use real screen capture, or animate a zoomed crop with large text only. | 4/10 |
| A4 before/after interpolation | ⚠️ Hits both anchor stills exactly; screen content morphs nicely early, but the scene switch is a ghosty cross-dissolve, not object-level animation — because the uni-1 "after" still changed geometry (monitor→laptop, new angle). **Fix: build the after-frame with uni-1 `image_edit` on the before-frame** so geometry locks and ray morphs objects instead of dissolving scenes. On-screen body text → gibberish; keep it out or large. | 6.5/10 |
| A3 seamless ambient loop | ✅ Loop returns home cleanly (0s ≈ end framing, steam/bubbles continuous); minor background-prop drift mid-clip, invisible at feed size. Bonus: loop mode rendered 8.75s for a 5s estimate — verify billing. | 8.5/10 |
| D1/C3 claymation restyle via video_edit (reimagine_2) | ⚠️ Pipeline solid — source pour motion fully preserved, liquid restyled to sculpted clay — but glass/ice kept translucency and motion stayed smooth, not stepped. **Push reimagine_3 + "matte clay, zero translucency, stepped 12fps"** or drive with keyframes (D3). | 7/10 |
| F2 reframe 9:16 → 1:1 | ✅ Outpaint seam invisible in every frame, added regions match lighting AND motion. Note: it ignored an off-scene fill prompt ("café bokeh") in favor of scene continuity — write fill prompts that extend what's actually at the edges. | 8/10 |

Meta API caveat (F-series): `source` on existing ad videos comes back empty — Meta restricts video downloads, so repurposing real video ads requires the master files locally.

## Validation log — round 2: UGC product B-roll recipe (2026-06-11, sneakers test)

**B6 — UGC lifestyle B-roll batch (VALIDATED).** 5 scenes, 5 different people/environments, all product-faithful. Pipeline: uni-1 still per scene (`--image-ref` product photo, 9:16) → ray-3.2 i2v 720p/5s → ffmpeg trim to 4.0s. ~$0.35/finished clip.

Recipe rules learned the hard way:
0. **START-FRAME APPROVAL GATE (hard rule from Caleb):** generate stills, show ALL of them to the user, get explicit approval, and only then animate. Never skip to video.
1. **Style block** (append to every still prompt — v2, after "way too cinematic" feedback): "Extremely raw amateur iPhone photo as posted to an Instagram story: harsh unflattering mixed lighting, visible skin shine and real skin texture, candid mid-action expression (mouth open mid-sentence is good), slightly tilted awkward framing, cluttered lived-in real background, mildly blown highlights, everything in focus. Absolutely NOT cinematic: no golden hour, no shallow depth of field, no bokeh, no color grade, no rim light, no editorial composition." Anti-cinematic levers matter more than pro-UGC words: explicitly BAN golden hour/bokeh/grade or the model drifts editorial.
1b. **People in frame**: real-looking, never posed, and **NEVER camera-aware** (hard rule from Caleb): no talking/laughing at the lens, no selfie-style address — silent video makes camera-aware faces read as broken. People do things: walk, lace up, carry laundry, check their phone, step out the door; the camera observes. Avoid large foreground hands (anatomy failure zone). One scene = two shoes max, both worn; never leave the hero shoe floating empty. No real-world trademarks in backgrounds. Always specify a top ("plain t-shirt") or gym/summer contexts go shirtless. Never write "as posted to an Instagram story" (renders literal story-editor UI) — use "sent in a group chat".
2. **Wordmark fidelity needs side-on framing.** Logos/text survive ONLY when the printed surface faces the camera squarely (±30°). Extreme foreshortening, mirror shots, and top-down angles scramble text every time (3 failed rolls proved it). Recompose the scene rather than fighting the angle.
3. **Spell it out**: include `reading exactly "BRAND NAME"` in quotes in the still prompt.
4. **Don't rotate the product in motion prompts.** i2v keeps frame-1 text crisp only on surfaces that stay put; "turns it in his hands" drifted the print mid-clip. Move the camera/person, not the printed surface.
5. **Motion block** (append to every video prompt): "Authentic handheld smartphone video, subtle natural hand-shake throughout, one continuous take, no cuts. The product print and details stay exactly as in the first frame."
6. 4s deliverables = generate 5s, `ffmpeg -t 4.0` — ray-3.2 has no 4s native duration.
