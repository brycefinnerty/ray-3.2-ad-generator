# uni-1 ad-template prompt library

Validated, parameterizable prompt templates for generating standalone Meta ad creatives with `uni-1`. Pair each with a brand product reference image via `--image-ref` for brand fidelity.

**Hard rule:** every prompt in this library produces a *standalone* image upload — no iOS chrome, no platform UI, no brand-row, no link card, no engagement counts. Those are added by Meta when displaying the ad.

**The script auto-appends three always-on safety suffixes** to every prompt (you don't need to repeat these constraints in your library entry):
1. **`NO_CHROME_SUFFIX`** — strips iOS chrome, platform brand-rows, post text, link-card footers, engagement rows, action buttons, comment input, tab bars, Story chrome.
2. **`SAFE_ZONE_SUFFIX`** — forces all text/headlines/CTAs/focal subjects to fit within the central 84% of the canvas (8% padding from every edge). Backgrounds may bleed; text and focal elements may not. Eliminates clipped headlines.
3. **`GLYPH_SAFETY_SUFFIX`** — forbids emoji and unicode glyphs inside body-text blocks (chat bubbles, comments, ChatGPT responses, Slack messages); enforces the exact count of conversation elements the prompt specifies.

Together: ~1,575 chars of always-on guard, leaving ~4,400 chars of headroom under Luma's ~6,000 char prompt cap for your actual prompt body.

**Reference image:** unless noted otherwise, pass a clean product hero shot (white-background product photo of the brand's packaging, including pouch / bottle / canister / sachets). The reference is the brand-fidelity anchor; the prompt is the format.

---

## How to use this file

When the user asks for a uni-1 ad with a known format, find the matching template below, replace the `{placeholder}` variables, then invoke `generate_image.py` with the filled prompt + the brand's reference image.

**Variable conventions:**
- `{brand.name}` — wordmark text on the product label (e.g. `AG1`)
- `{brand.color_primary}` — primary brand color hex (e.g. `#1A4731` deep forest green)
- `{brand.product_description}` — one-line how-the-product-looks (e.g. `forest-green pouch with white AG1 wordmark, clear shaker bottle with green liquid, coral travel sachets`)
- `{brand.competitor_category}` — what the brand is replacing/winning against (e.g. `Generic Multivitamin`)
- `{brand.tagline}` — the brand's short value prop (e.g. `Greens, simplified.`)
- Template-specific variables defined per section.

---

## T1 — Apple Notes listicle aesthetic

**When to use:** emotional / sentimental product positioning, "things I love about X" voice, brands targeting older or wellness-conscious audiences. Reads like a real customer's private list.

**Aspect ratio:** `2:3` (Meta feed-portrait friendly without iOS device frame)

**Reference image:** clean product hero (helps brand-color drift in the rare emoji that gets a brand cue)

**Variables:**
- `{notes_title}` — bold black title (≤40 chars, may end with brand-relevant emoji)
- `{date_string}` — small grey timestamp under the header (e.g. "March 14, 2026 at 6:42 AM")
- `{checklist_items[]}` — 8-12 items, each conversational + 1-2 emoji decorations, optional date suffix

**Template prompt:**
```
2:3 portrait static ad creative — a clean Apple Notes app aesthetic mock-up rendered as a standalone image, edge-to-edge, on a pure white #FFFFFF background. The aesthetic mimics the look of a personal note in Apple Notes, but this is the upload-ready ad creative itself, not a phone screenshot.

Top of the image (taking ~10% height): an Apple Notes navigation header. Left: orange "< Notes" back-chevron + label in SF Pro semibold. Center: two orange icons — a forward-arrow circle (redo) and a circular refresh arrow. Right: a share-square icon and an ellipsis-in-circle icon, both grey. Hairline grey divider beneath.

Centered just below the header, in small grey SF Pro: "{date_string}"

Then bold black SF Pro title (large, ~32pt feel): "{notes_title}"

Then a vertical list of {N} unchecked checklist items. Each row: a hollow grey circle bullet on the left, then the item text in regular black SF Pro with emoji decorations interleaved. Items (verbatim):
{checklist_items_numbered}

Generous vertical spacing, items left-aligned with consistent left padding from the bullet.

Bottom of the image (~6% height): an Apple Notes toolbar with four icons evenly spaced — orange checklist/list icon (active), camera icon, "A" inside a circle (text style), and a pencil-edit-square icon.

The composition reads as a calm, honest personal note — like a real customer's private journal entry — but rendered as a standalone ad creative ready to upload. No keyboard, no selection state, no device chrome.
```

**AG1 example fill:**
- `{notes_title}` = `Why I Switched To AG1 🌿`
- `{date_string}` = `March 14, 2026 at 6:42 AM`
- `{checklist_items}` = 10 items: `Less time meal-prepping ⏱️🥗`, `No more 12-pill morning stack 💊→🌱`, `Travel-friendly sachets ✈️🍃`, `Easier to actually drink 💚`, `Backed by clinical research 🔬`, `Endorsed by people I trust 👥`, `One scoop, one minute ⏲️`, `Berry flavor I don't gag on 🫐`, `Fewer "did I take my vitamins?" thoughts 🧠`, `More energy by 10am ⚡`

Validated example: `iterations/ag1-v2/T1-ios-notes/`

---

## T2 — Editorial article hero

**When to use:** credibility-led ads — "[respected publication] covers brand X." High-trust audiences, science-backed products. The publication logo functions as a third-party endorsement.

**Aspect ratio:** `1:1` (Meta feed standard)

**Reference image:** clean product hero (for the inset product shot in the photo block)

**Variables:**
- `{publication}` — publication wordmark (`FORBES`, `WIRED`, `Vogue`, `The Wall Street Journal`)
- `{headline}` — bold editorial headline, 8-15 words, declarative
- `{subcopy}` — 1-2 sentence editorial sub-copy expanding the headline
- `{photo_subject_description}` — what's shown in the bottom 55% (e.g. `fit person in athletic wear holding clear AG1 shaker, AG1 pouch + canister + sachets in foreground`)
- `{tagline}` — short brand promise on the bottom green band (≤4 words, e.g. `Greens, simplified.`)
- `{band_color}` — brand-color hex for the bottom band (e.g. `#1A4731`)

**Template prompt:**
```
1:1 static ad creative, 1080x1080, edge-to-edge — an editorial / publication-style ad image. Standalone, ready to upload as a Meta ad creative. White inner background.

Top-left: "{publication}" wordmark in chunky bold black serif on a small white box (the publication's logo, treated as a credibility stamp).

Headline below the logo, large bold black sans-serif tight tracking: "{headline}"

Sub-copy below the headline, regular weight black sans-serif: "{subcopy}"

Hero photograph occupies the bottom ~55% of the image: {photo_subject_description}. Premium-wellness product photography, soft natural light.

Across the very bottom of the image, an inset {band_color} band about 12% tall, containing white sans-serif headline "{tagline}" left-aligned, with a small white "Learn more >" pill on the right edge.

The composition is the standalone ad creative — editorial layout that reads as a publication-co-signed brand piece. No social platform UI of any kind.
```

**AG1 example fill:**
- `{publication}` = `FORBES`
- `{headline}` = `How AG1 Became the Greens Powder Doctors Actually Recommend`
- `{subcopy}` = `Most multivitamins fail bioavailability tests. The brand fronted by Dr. Andrew Huberman built theirs around what your body can actually absorb.`
- `{tagline}` = `Greens, simplified.`
- `{band_color}` = `~#1A4731`

Validated example: `iterations/ag1-v2/T2-ig-feed/`

---

## T3 — Story tweet+UGC composite

**When to use:** influencer / authority endorsements paired with UGC-style customer footage. Story-format placements (Reels/Stories), high social-proof angle.

**Aspect ratio:** `9:16` (Stories / Reels)

**Reference image:** product hero (for the shaker/product visible in the UGC photo)

**Variables:**
- `{authority_name}` — full name of the quoted authority (a doctor, scientist, athlete, founder — someone with category credibility)
- `{authority_handle}` — Twitter/X handle of the authority
- `{authority_face_description}` — 1-line face description for the small profile photo
- `{tweet_body}` — multi-line tweet text including the value-prop bullets with emojis
- `{ugc_subject}` — what the UGC photo shows (e.g. `fit woman in workout clothes mid-laugh holding an AG1 shaker bottle`)
- `{ugc_overlay_text}` — the black-rectangle text label across the UGC photo (e.g. `Watch this BEFORE / you skip your greens 🌿`)
- `{cursive_line}` — italic teaser line above the LEARN MORE (e.g. `75+ ingredients in one daily scoop...`)

**Template prompt:**
```
9:16 portrait static ad creative, 1080x1920, edge-to-edge. Standalone — this image gets uploaded directly as the Story ad asset.

Background: soft cream / warm grey gradient ~#F2EEE6, full bleed.

Upper-mid composition: a screenshot-style Twitter/X post card, white rounded-corner card with thin shadow, occupying roughly 55-60% of the width on the left side, vertically positioned in the upper third:
- Top of card: small round profile photo of {authority_face_description}, "{authority_name}" in bold black + a small blue-check verified mark, "{authority_handle}" in grey beneath.
- Tweet text in black sans-serif:
"{tweet_body}"

To the right of the tweet card, slightly overlapping its right edge: a vertical 9:16-cropped photo of {ugc_subject}, soft window-light morning kitchen background. Across the lower-mid of the photo, a black rounded-rectangle overlay text label: "{ugc_overlay_text}" in white sans-serif.

Below the tweet+photo composite, in the lower third of the image:
- A faint cursive italic line in black: "{cursive_line}" then "more" in grey-blue underline.
- Below that, centered, in cursive blue script: "🔗 LEARN MORE" — a link-chain icon then "LEARN MORE" in caps.

The composition is the static Story ad creative ONLY. No iOS device chrome, no Story progress bars, no story header, no swipe-up arrows.
```

Validated example: `iterations/ag1-v2/T3-ig-story/`

---

## T4 — "Fake Google search" mosaic

**When to use:** "as the internet says..." angle. Implicit social proof from search results aesthetic + media logos. Wellness, nutrition, beauty, supplement categories where consumers actively Google solutions.

**Aspect ratio:** `9:16`

**Reference image:** clean product hero with multiple SKUs visible (the 2×2 grid uses 4 product variations)

**Variables:**
- `{search_query}` — the query in the search bar (e.g. `The BEST greens powder for energy and gut health`)
- `{grid_tile_descriptions[]}` — 4 product-photo descriptions, one per tile, all sharing a soft tonal background (e.g. cream/sage)
- `{publication_logos[]}` — 4 publication wordmarks for the bottom row (e.g. `FORBES`, `Vogue`, `Men's Health`, `The Wall Street Journal`)
- `{accent_color_family}` — the soft tonal background for the grid (e.g. `cream-to-sage`, `pink-to-lavender`, `cream-to-amber`)

**Template prompt:**
```
9:16 portrait static ad creative, 1080x1920, edge-to-edge. A "fake Google search results" aesthetic rendered as a standalone upload-ready image. White inner background fading to soft {accent_color_family} at the bottom 30%.

Top of the image (~6% height): a thin top app row — a small grey hamburger-menu icon on the left; centered, the multicolor "Google" wordmark (capital G blue, o red, o yellow, g blue, l green, e red) in the standard Google Sans typeface; on the right, a small color microphone icon.

Below that: a rounded-pill grey search bar with a magnifier icon on the left and the text "{search_query}" in standard sans-serif. On the right inside the pill, a small Google Lens icon (multicolor camera/diamond shape).

Below the search bar: a horizontal tab row "All  Videos  Images  News  Maps  Books" with "All" underlined in faint blue, others in muted grey. Hairline divider beneath.

Main area: a 2x2 grid of square image search results with subtle rounded corners and small gaps between them. All four tiles share a soft {accent_color_family} background:
- Top-left: {grid_tile_descriptions[0]}
- Top-right: {grid_tile_descriptions[1]}
- Bottom-left: {grid_tile_descriptions[2]}
- Bottom-right: {grid_tile_descriptions[3]}

Below the grid, soft {accent_color_family} area at the bottom: in small spaced caps "AS SEEN ON" in muted grey, then below a horizontal row of four publication wordmarks in classic typefaces: {publication_logos joined with comma}.

The composition reads as a believable "Google search results page" rendered as a standalone static ad creative. No iOS device chrome.
```

Validated example: `iterations/ag1-v2/T4-google-search/`

---

## T5 — Comparison table (light)

**When to use:** clinical/feature-led brand differentiation against a generic category competitor. Best for products with clear feature-superiority claims (clinical research, certifications, ingredient counts, sugar content, etc.).

**Aspect ratio:** `2:3` (Meta tall feed)

**Reference image:** product hero showing the brand's primary SKU(s)

**Variables:**
- `{brand.name}` — the wordmark text in the header
- `{brand.product_image_description}` — what the brand's product looks like (1-line)
- `{competitor_category}` — what the brand is being compared against (e.g. `Your Daily Multivitamin`, `Generic Pre-Workout`)
- `{competitor_image_description}` — generic stand-in product (1-line, deliberately dull/unbranded)
- `{brand.color_primary}` — header text color hex (deep brand color)
- `{row_accent_color}` — soft tint of the alternating row color (e.g. `~#E8F0E5` sage for green brands, `~#E5F0F8` for blue)
- `{rows[]}` — 6 rows of `{label, sublabel?, brand_value, competitor_value}` where values are `green ✓`, `red ✗`, or text (numbers, ranges)

**Template prompt:**
```
2:3 portrait static ad creative, 1080x1620 — a clean, edge-to-edge comparison-table ad image. Standalone, ready to upload as a Meta ad creative. White background.

Header section (top ~22% of the image):
- Left side: bold {brand.color_primary} sans-serif headline in two stacked lines: "{brand.name} vs. {competitor_category}"
- Right side, on the same vertical band as the headline: two product photos in a row — {brand.product_image_description} on the left, {competitor_image_description} on the right.
- Hairline thin grey divider beneath the header.

Comparison table (bottom ~78% of the image): six rows, each spanning the full width, with alternating row backgrounds — {row_accent_color} for odd rows and white for even rows. Each row has three columns: label (left, ~50% width), {brand.name} column (~25%), and competitor column (~25%).

{rows_rendered_with_label_brand_competitor}

Typography is clean modern sans-serif throughout. Iconography is consistent — same green-circle ✓ and red-circle ✗ across all check rows.

This is the standalone ad creative — only the comparison table and product header. No surrounding social platform UI.
```

**AG1 example fill** — see `iterations/ag1-v2/T5-saved-fb-comparison/prompt.txt` for a fully-rendered version. Rows used:
1. `Clinical Research` | ✓ | ✗
2. `Probiotics + Prebiotics` / `For gut health` | ✓ | ✗
3. `Adaptogens` / `Ashwagandha, Rhodiola` | ✓ | ✗
4. `Essential Vitamins` | ✓ | ✓
5. `Number of Ingredients` | `75+` | `23`
6. `NSF Certified for Sport` | ✓ | ✗

Validated example: `iterations/ag1-v2/T5-saved-fb-comparison/`

---

## T6 — Comparison table (dark, hooky)

**When to use:** stop-the-scroll dark-mode creative. More provocative tone than T5 — leads with "this RUINS X" hook. Strong for SaaS/info-product/supplement brands willing to be confrontational with the category.

**Aspect ratio:** `2:3`

**Reference image:** product hero (used for the right-side icon in the VS row)

**Variables:**
- `{hook_line_1}` — top line, white, large (e.g. `This RUINS`)
- `{hook_line_2}` — bottom line, white with one word in bright accent green (e.g. `Your {{Greens}} Powder` where the word in `{{}}` is colored)
- `{competitor_label}` — short caption under the left "VS" tile (e.g. `Generic Greens`, `Your Old Pre-Workout`)
- `{brand.name}` — the wordmark on the right tile
- `{brand.color_primary}` — the green/accent color used for highlights and the AG1-column outline
- `{table_columns}` — three: `Ingredient` / `{competitor_label}` / `{brand.name}` (or analogous metric column names)
- `{table_rows[]}` — 5 rows of `{metric_label, competitor_value, brand_value}` — brand value rendered in accent green

**Template prompt:**
```
2:3 portrait static ad creative, 1080x1620, edge-to-edge — a dark-mode comparison ad image. Standalone, upload-ready as a Meta ad creative. Near-black background ~#0A1A12 with a subtle radial deep-{brand.color_primary} glow at the center.

Tiny green "+" cross marks in the four corners of the image (decorative tick marks).

Top text in chunky white sans-serif (large, ~80pt feel), stacked across two lines centered horizontally: "{hook_line_1}" on line 1, "{hook_line_2}" on line 2 — the word(s) marked with double-braces in {hook_line_2} are colored bright vivid green ~#3FCB7E, the rest white.

Centered below the headline, a row of three small rounded-square icons:
- Left tile: black background with a stylized white {competitor_visual} graphic on it, captioned with small white text "{competitor_label}" beneath.
- Middle: a small angled bright-green "VS" badge in a parallelogram shape.
- Right tile: {brand.color_primary} background with white "{brand.name}" wordmark stamped boldly.

Below the icons, a dark comparison table with thin light-grey grid lines:
- Header row in regular grey caps: {table_columns[0]} | {table_columns[1]} | {table_columns[2]}
- The "{brand.name}" column is outlined / highlighted with a thin bright-green border framing it.
{table_rows_rendered}

Numbers in monospace IBM Plex Mono / Roboto Mono feel; labels in regular sans-serif.

The composition is the standalone dark-mode ad creative ONLY — no surrounding platform UI.
```

Validated example: `iterations/ag1-v2/T6-fb-sponsored/`

---

## T7 — Sticky-note + product flatlay

**When to use:** tactile / UGC-aesthetic ads. Best for consumable products that can be physically scattered (gummies, sachets, capsules, sample packets). Works for "I tried this for N days" reviewer-voice angles.

**Aspect ratio:** `1:1`

**Reference image:** product photo showing the small / scatter-able product unit (sachet, gummy, packet)

**Variables:**
- `{handwritten_text_lines}` — 3-5 lines of bold all-caps text, marker-style. Should fit on a square sticky note. Personal/conversational voice.
- `{sticky_note_color}` — vivid post-it color (default `bright magenta-pink ~#E84F88`); could be neon yellow `#FCE96A`, lime `#B7E36B`, or orange `#F7931E`
- `{product_unit_description}` — what gets scattered around the note (e.g. `coral / orange-red AG1 travel sachets with white "AG1" wordmark`, `green sour gummy worms with sugar crystals`, `single-serve protein scoops`)
- `{powder_or_residue_hint}` — optional small detail to ground the product as real (e.g. `a few scattered green powder flecks near one of the open sachet ends`)

**Template prompt:**
```
Top-down 1:1 flatlay product photograph, 1080x1080, soft off-white seamless background. Center: a {sticky_note_color} square sticky note (3M Post-it style), slightly rotated counter-clockwise about 5 degrees, with hand-lettered black marker text in bold all-caps stacked over multiple lines: "{handwritten_text_lines}". Letters are hand-drawn with a chunky black permanent marker — slightly uneven baseline, irregular kerning, marker bleed at stroke edges, organic and imperfect.

Around all four sides of the sticky note, partially overlapping its edges in places: 8-12 individual {product_unit_description}. Scattered organically — some flat, some slightly tilted, some overlapping each other or the sticky-note edge.

Even diffuse soft overhead lighting, no harsh shadows. {powder_or_residue_hint}

Casual, organic, social-content aesthetic — feels homemade UGC, not over-styled.
```

**AG1 example fill:**
- `{handwritten_text_lines}` = `I DRANK ONE / OF THESE EVERY / MORNING FOR / 30 DAYS`
- `{sticky_note_color}` = `bright magenta-pink ~#E84F88`
- `{product_unit_description}` = `AG1 travel sachets — small rectangular foil packets in warm coral / orange-red color, with white "AG1" wordmark visible on each, stamped boldly`
- `{powder_or_residue_hint}` = `A few scattered green powder flecks (a hint of spilled greens) on the background near one of the open sachet ends`

Validated example: `iterations/ag1-v2/T7-sticky-note/`

---

## T8 — Handwritten whiteboard / posterboard comparison

**When to use:** UGC-aesthetic "real person made this" social proof. Strong for DTC, supplements, coaching/info-products. Especially effective in IG Reels-derived ads.

**Aspect ratio:** `2:3` (a tall held-up board needs vertical room — 1:1 clips the headline at the top)

**Reference image:** product hero (informs the brand color used for the "wins" column marker)

**Variables:**
- `{N}` — number of reasons (default 5)
- `{brand.name}` — wordmark for the LEFT (winning) column (e.g. `AG1`)
- `{competitor_label}` — what's being compared against (e.g. `Generic Multivitamins`, `Traditional Hiring`)
- `{brand.color_marker}` — color of the marker used on the brand side (e.g. `deep forest green`, `bright red`)
- `{brand_wins[]}` — N short bullet items, brand-side advantages
- `{competitor_cons[]}` — N short bullet items, competitor-side cons
- `{environment}` — outdoor patio / sunlit kitchen / bright office (the IRL setting in the soft background)

**Template prompt summary:** A hand from the bottom of the frame holds a real white whiteboard or foam-board sign at a slight tilt, photographed in a soft-focus IRL environment with bright natural light. The board is hand-lettered in two-color marker — brand's color for the LEFT column wins, dim grey for the RIGHT column cons — with a hand-drawn `>` symbol between the brand and competitor names at the top. Headline reads `{N} Reasons Why / {brand.name} > {competitor_label}`. Bullets on the left are filled circles or stars; on the right are X marks. UGC aesthetic, looks like a real Reels still.

Validated example: `iterations/ag1-v2/T8-whiteboard-comparison-v2/` (v2 switched to 2:3 + dropped airplane emoji that caused glyph garbling — full headline now visible)

---

## T9 — Annotated product features (arrow callouts)

**When to use:** feature-rich product breakdowns. Best for products where each feature is a discrete selling point (watches, supplements, gadgets). Reads like a Goop / Apothékary product card.

**Aspect ratio:** `1:1`

**Reference image:** clean product hero (the central product is rendered faithfully from the ref)

**Variables:**
- `{testimonial_quote}` — short pull-quote at the top in italic serif (≤80 chars, in quotation marks)
- `{star_count}` — usually 5 (★★★★★)
- `{callouts[]}` — 4-6 feature labels, each with a positional hint (top-left, top-right, bottom-left, bottom-right, center-bottom). 1-3 word labels are best
- `{brand.name}` — wordmark to display at the bottom

**Template prompt summary:** Soft cream background. Top: 5 small black stars + italic dark-navy serif testimonial pull-quote. Center: clean product hero. 4-6 thin black hand-drawn arrow lines (slightly irregular, fine-marker feel) sweep from specific points on the product outward to feature labels in the negative space. Each arrow has a small arrowhead at the callout end. Brand wordmark centered at the bottom. Editorial wellness product photography.

Validated example: `iterations/ag1-v2/T9-annotated-callouts/`

---

## T10 — Letter board sign + product

**When to use:** UGC / influencer-flatlay aesthetic. Tactile, social-content feel. Best for consumer brands that fit a "morning routine" or "daily ritual" lifestyle frame.

**Aspect ratio:** `1:1`

**Reference image:** product hero (used for the product placed beside the letter board)

**Variables:**
- `{letter_board_text}` — 2-3 short stacked lines, all caps, fits a small letter board (e.g. `ONE SCOOP / REPLACED MY / 12-PILL STACK`)
- `{environment}` — sunlit kitchen / bedside / desk corner (the IRL setting)
- `{board_frame_color}` — wood color for the letter board frame (default `warm honey oak`)
- `{product_arrangement}` — what's arranged beside the board (e.g. `AG1 pouch upright + clear shaker bottle in front + small wooden scoop + 2 travel sachets casually placed`)

**Template prompt summary:** Real-world flatlay-adjacent shot of a vintage-style felt letter board (wooden frame, classic black felt) with hand-arranged white plastic letters spelling the message in 2-3 stacked lines, slight letter imperfections. Beside the board, slightly overlapping its edge: the brand's product arrangement. Bright morning natural light, shallow background DOF, premium-wellness aesthetic. Looks like an influencer Reel still.

Validated example: `iterations/ag1-v2/T10-letter-board/`

---

## T11 — Fake comment thread (user → brand)

**When to use:** social proof with response — show a real customer asking, brand giving a clean call-to-action answer. Strong for higher-consideration purchases where buyers want to see other buyers ask.

**Aspect ratio:** `1:1`

**Reference image:** product hero (for the product photo in the lower half)

**Variables:**
- `{user_name}` — first name + last initial (e.g. `Sarah K.`)
- `{user_avatar_description}` — 1-line for the small profile photo (e.g. `smiling brunette woman`)
- `{user_question}` — the prospect's question (≤80 chars)
- `{brand.name}` — brand wordmark
- `{brand.avatar_description}` — what the brand's circular avatar looks like
- `{brand_response}` — multi-line answer with a 3-step numbered list (avoid emoji — see "known issue")

**Template prompt summary:** Light grey FB-comment background. Upper half: vertical chain of two grey rounded comment bubbles — first the user's question (with avatar + name + bubble + tiny `Like · Reply · N likes` row), connected by a thin grey vertical line to the brand's reply (slightly indented, with brand avatar + verified-blue check + bubble + reply metadata). Lower half: clean product photograph edge-to-edge.

**Note:** the script's `GLYPH_SAFETY_SUFFIX` (always on) handles both the "exactly N comments" constraint and the "no emoji in body text" rule globally — your prompt only needs to describe the desired content. The v3 of this template is locked-in clean.

Validated example: `iterations/ag1-v2/T11-comment-thread-v3/` (v3: exactly 2 comments, plain text, full product photo visible)

---

## T12 — Fake ChatGPT conversation

**When to use:** "AI agrees" social proof. Trending pattern in 2026. Effective when the brand naturally emerges as the answer to a category question — works best for category leaders, less for unknown brands.

**Aspect ratio:** `1:1`

**Reference image:** brand product (helps the green CTA bar pull from brand color)

**Variables:**
- `{user_question}` — the question typed to ChatGPT (1 sentence, no longer than 80 chars)
- `{user_avatar_description}` — small profile photo description
- `{chatgpt_response_short}` — KEEP THIS UNDER 4 short lines. uni-1 garbles dense small text — see known issue. Use 3-4 numbered points max, each 1 line.
- `{cta_text}` — green-bar CTA (e.g. `Try AG1 risk-free for 30 days`)
- `{cta_color}` — brand-color hex for the bottom CTA bar

**Template prompt summary:** Dark grey ChatGPT chat background. Top: small user avatar + question. Middle: green ChatGPT logo tile + numbered response with thumbs-up/down icons in the corner. Bottom: full-width green CTA bar with white text + right-arrow.

**Note:** keep the ChatGPT response sparse — 3 short numbered lines + 1 closer line, rendered at LARGE text size. Dense / small body text will garble even with the global `GLYPH_SAFETY_SUFFIX`. Less is more.

Validated example: `iterations/ag1-v2/T12-fake-chatgpt-v2/` (v2: shorter response, large text, clean rendering)

---

## T13 — Before/After two-panel split

**When to use:** transformation narratives. Universal pattern — works for fitness, supplements, productivity tools, hair/skin, anywhere a "messy before, clean after" makes the pitch instantly.

**Aspect ratio:** `1:1`

**Reference image:** product hero (for the "after" panel)

**Variables:**
- `{before_label}` — usually `HOW IT STARTED` (other variants: `BEFORE`, `WITHOUT {brand.name}`)
- `{after_label}` — usually `HOW IT'S GOING` (other variants: `AFTER`, `WITH {brand.name}`)
- `{before_scene_description}` — chaotic / messy / mid-pain-point flatlay
- `{after_scene_description}` — clean / styled / product-led flatlay using the brand's product
- `{before_tone}` — desaturated / muted background hex (e.g. grey-beige)
- `{after_tone}` — warm / bright background hex (e.g. cream)

**Template prompt summary:** Image is divided exactly down the center by a hairline 2px white vertical divider into two equal-width halves. Same camera angle (top-down flatlay), same headline placement on both sides. LEFT: muted background, BEFORE label, chaotic scene. RIGHT: warm bright background, AFTER label, clean product-led scene. The visual contrast IS the joke.

Validated example: `iterations/ag1-v2/T13-before-after/`

---

## T14 — Fake Slack team conversation

**When to use:** B2B / SaaS / agency products where the buyer's "moment of consideration" happens in a work context. Also works for wellness brands with a "team / colleague recommendation" angle.

**Aspect ratio:** `1:1`

**Reference image:** product hero (used for color cues in the green CTA pill)

**Variables:**
- `{channel_name}` — Slack channel (e.g. `#wellness-team`, `#growth`, `#founders`)
- `{messages[]}` — 3 messages, each `{author_name, role, time, message_text}`. Avoid emoji in message text (see known issue)
- `{cta_text}` — pill button text (e.g. `TRY AG1 →`)
- `{cta_color}` — brand-color hex for the CTA pill

**Template prompt summary:** Slack window header (deep aubergine ~#3F0E40 with traffic-light dots, search bar, profile avatar). Below: white chat area with bold channel header + member-count pill. Three message rows, each with cartoon-style avatar + bold name + timestamp + message text. Big green pill CTA centered below the messages. Looks like a real Slack thread snapshot.

**Note:** the script's global `GLYPH_SAFETY_SUFFIX` strips emoji from message bodies and enforces the "exactly N messages" count — you don't need to repeat those constraints in the prompt.

Validated example: `iterations/ag1-v2/T14-fake-slack-v2/` (v2: plain-text messages, exactly 3, clean)

---

## T15 — Ingredient list + collage (left/right split)

**When to use:** ingredient-forward consumables — supplements, food, drinks, beauty. Visual proof that the labeled ingredients are real / present / sourced.

**Aspect ratio:** `1:1`

**Reference image:** brand product hero (the actual product image is reproduced on the right)

**Variables:**
- `{ingredients[]}` — 4-6 ingredient names, plain text, premium typography (no emoji needed)
- `{ingredient_visuals[]}` — for each ingredient, a 1-line visual description for the right-side collage tile (e.g. `extreme close-up of vibrant green spirulina powder texture`)
- `{brand.product_description}` — how the product looks (pulled from the reference image)

**Template prompt summary:** Soft cream background. LEFT half: vertical list of 4-6 ingredient names in clean black sans-serif, each followed by a thin hairline grey divider running to the right edge of the left half. RIGHT half: vertical photo collage stack of the ingredients (one tile per ingredient) flowing into the actual product, which sits at the bottom-right overlapping the collage. Premium-wellness editorial aesthetic.

Validated example: `iterations/ag1-v2/T15-ingredient-list/`

---

## T17 — Stacked-bar with vs without comparison

**When to use:** data-viz framing of the brand's value prop. Reads as objective even though it's editorial. Strong for productivity, wellness, finance, time-saving brands where the "without" side has many discrete failure modes.

**Aspect ratio:** `2:3`

**Reference image:** product hero (informs brand color for the winning bar)

**Variables:**
- `{header_label}` — top label both columns share (e.g. `Time spent`, `Money spent`, `Brain space`)
- `{winning_bar_color}` — soft tone for the brand's solid bar (e.g. mint-sage `#D4E8D4`)
- `{winning_bar_text}` — short phrase centered in the brand bar (e.g. `feeling great`, `actually working`)
- `{losing_segments[]}` — EXACTLY 5 short pain-point labels (top to bottom), each on a different soft pastel. Be explicit: "five segments only, no more."
- `{brand.name}` and `{competitor_label}` — column footers

**Template summary:** Two equal-width columns, hairline divider between. Left: solid colored bar with one centered phrase, brand-color footer. Right: same-height bar divided into exactly 5 horizontal pastel segments, each with a short pain-point label. Headers and footers in plain black sans-serif.

Validated example: `iterations/ag1-v2/T17-stacked-bar-v2/`

---

## T18 — Flowchart "old way" vs "new way"

**When to use:** workflow / habit transformation. Best when the brand replaces a complicated process with a simple one. Strong for SaaS, supplements, productivity, info-products.

**Aspect ratio:** `1:1`

**Reference image:** product hero (drives the brand color in the new-way pill + box borders)

**Variables:**
- `{old_way_steps[]}` — 5 short pain-point steps for the old-way column (each ≤4 words). Last step is a "give up" / failure state.
- `{new_way_steps[]}` — 3 short steps for the new-way column (≤6 words each). Ends with the brand's outcome.
- `{closing_outcome}` — short bold tagline beneath the new-way chain (e.g. `Calm Consistency`, `Just one step`)
- `{brand.color_primary}` — for the new-way header pill + box borders

**Template summary:** Two halves, vertical hairline divider. LEFT: black rounded-rect "Old Way" header pill, then 5 outlined boxes connected by wonky hand-drawn arrows, ending with skull/crossed-out icon at "Give Up". RIGHT: brand-colored "New Way" header pill, 3 sage-toned rounded boxes with clean confident arrows, ending in a flourish star + bold dark-green outcome text.

Validated example: `iterations/ag1-v2/T18-flowchart-old-vs-new/`

---

## T19 — Fake AirDrop dialog (with before/after)

**When to use:** stop-the-scroll iOS modal pattern. The AirDrop dialog is so familiar that users instinctively look at it. Pair with a before/after to deliver the value prop in one glance. Strong for transformation-led brands (apparel, fitness, supplements, beauty, finance).

**Aspect ratio:** `1:1`

**Reference image:** product hero (only used for color cues in the after photo)

**Variables:**
- `{prompt_question}` — the dialog's two-line subhead, ending with the brand cue (e.g. `Looking to feel like yourself again? Try AG1.`)
- `{before_subject_description}` — what the left photo shows (the "before" pain state)
- `{after_subject_description}` — what the right photo shows (the "after" branded state)

**Template summary:** Soft blurred neutral grey-beige background. Centered: a white rounded-rectangle iOS AirDrop dialog with bold "AirDrop" title, two-line subhead, side-by-side before/after photo split (thin white vertical divider), then bottom row with "Decline" (light blue) / "Accept" (dark blue) buttons split by hairline.

Validated example: `iterations/ag1-v2/T19-airdrop-dialog/`

---

## T20 — IG Story Q&A sticker over lifestyle photo

**When to use:** UGC / influencer authority — feels like a real creator answering a real question. Pair with an aspirational lifestyle background to bake the brand into the lifestyle the user wants.

**Aspect ratio:** `9:16`

**Reference image:** product hero (helps the answer text reference the actual product accurately)

**Variables:**
- `{lifestyle_photo_description}` — the full-bleed background (sunset coastline, mountain trail, kitchen at golden hour, etc.)
- `{question}` — the white-card question text (1-2 lines, conversational, ≤80 chars)
- `{answer}` — typewriter-style multi-line answer in 4 short lines, mentioning the brand naturally
- `{cta_text}` — bottom pill CTA (e.g. `🔗 SHOP NOW`)

**Template summary:** Full-canvas lifestyle photo. Upper third: composite "Ask me anything!" black bar + white question card stacked, then a translucent typewriter-style answer panel below. Bottom: small white rounded pill CTA.

Validated example: `iterations/ag1-v2/T20-ig-qa-sticker/`

---

## T21 — Handwritten testimonial on napkin / paper

**When to use:** UGC raw-and-real aesthetic. Reads as authentic creator content, not branded. Best for brands with a "friend recommendation" angle.

**Aspect ratio:** `2:3`

**Reference image:** product hero (used for the small product element placed near the napkin)

**Variables:**
- `{handwritten_message}` — multi-line cursive ink text, friend-to-friend voice, ending with the brand mention
- `{table_setting}` — what's around the napkin (cafe table, kitchen counter, marble countertop)
- `{product_element_description}` — the single product cue placed near the napkin (a sachet, a bottle, packaging glimpse)
- `{cta_color}` — color for the bottom shop-now pill

**Template summary:** Top-down/angled real-world photograph of a paper napkin on a table, with hand-written ink message in casual cursive. Surrounded by a glass with the brand's product, an open sachet, food crumbs / fruit dish edges. Soft warm natural daylight. Small bottom pill CTA.

Validated example: `iterations/ag1-v2/T21-napkin-testimonial/`

---

## T23 — POV calendar timeline of pain points

**When to use:** relatability humor for time-pressed audiences (founders, parents, students). The brand emerges in the last calendar block as the relief. Strong scroll-stopper.

**Aspect ratio:** `1:1`

**Reference image:** product hero (only color cues)

**Variables:**
- `{pov_headline}` — two-line "POV: A [target customer]'s [domain] schedule" (e.g. `POV: A burned-out founder's daily energy schedule`)
- `{calendar_blocks[]}` — EXACTLY 8 events, top-to-bottom: 6 pain-points + 1 sliver "lunch / break / promise" + 1 final brand-arrival event. Each has color, title, and time range.
- `{time_axis_labels[]}` — 8 labels, each appearing exactly once (do NOT duplicate any label like "3 PM" twice)

**Template summary:** Headline at top, then a dark-mode Apple Calendar panel with vertical time-axis labels and 8 color-coded rounded-rectangle event blocks. Each event title and time-range plainly readable. Last event is the brand showing up — the joke pays off there.

Validated example: `iterations/ag1-v2/T23-pov-calendar-v2/`

---

## T24 — Phone-in-phone Reel composite

**When to use:** "watch this Reel" pattern — the canvas itself looks like a Reel still, with a phone-frame inset showing UGC. Strong when paired with intrigue overlay text ("Watch this BEFORE…", "What I tried after…"). Works for personality-led / influencer brands.

**Aspect ratio:** `9:16`

**Reference image:** product hero (used for the brand-pattern background and the product visible in the UGC photo)

**Variables:**
- `{background_pattern}` — repeating wordmark / branded backdrop (e.g. low-opacity AG1 wordmark on forest green)
- `{ugc_subject}` — what the inset photo shows (creator with product, mid-action, golden hour, etc.)
- `{overlay_text}` — black rounded-rectangle text label across the UGC photo (e.g. `Watch this BEFORE / your morning coffee`)
- `{cta_color}` — color for the bottom CTA bar
- `{cta_text}` — bottom CTA text (e.g. `Learn more`)

**Template summary:** Full-canvas branded backdrop (saturated brand color with low-opacity wordmark pattern). Centered: a slightly tilted phone-frame mockup containing a vertical UGC-style photo with a black rounded-rect overlay label across the lower-mid. Bottom: full-width CTA bar in accent color with right-arrow.

Validated example: `iterations/ag1-v2/T24-phone-in-phone/`

---

## T25 — Newspaper crossword puzzle

**When to use:** clever editorial brand-puzzle moment. Plays well in lifestyle / wellness categories where a "Sunday morning, coffee and crossword" association is on-brand.

**Aspect ratio:** `1:1`

**Reference image:** product hero (props the small product accent)

**Variables:** `{newspaper_masthead}` (e.g. "The AG1 Daily"), `{date_string}`, `{across_clues[]}`, `{down_clues[]}`, `{filled_words[]}` (3-4 short crossing words, ≤5 letters each so each grid cell stays large enough to render legibly)

**Template prompt summary:** Top-down photo of a tilted aged-newsprint page on a wood coffee-shop table, with a SMALL 5x5 crossword grid (large cells, big legible letters), masthead + date sub-header, ACROSS/DOWN clue list to the right, faint brand watermark bottom-right. Coffee cup steam + scattered brand sachets + brand pouch as props around the page.

**Note:** Keep the grid SMALL (5x5 max) and use only 3-4 short crossing words. uni-1 garbles letters in tiny crossword cells; a small grid with big letters renders clean. T25 v1 used a 12x12 grid and the in-grid letters came out as glyph soup.

Validated example: `iterations/ag1-v2/T25-newspaper-crossword-v2/`

---

## T26 — Cash register receipt

**When to use:** product-as-receipt joke. List the brand's "benefits received" as itemized line items + total. Strong for "you get [list]" value-prop positioning.

**Aspect ratio:** `1:1`

**Reference image:** product hero (sits beside the receipt as a real-world prop)

**Variables:** `{store_header}` (e.g. "AG1 WELLNESS CO.\ndrinkag1.com\n123 Foundation Way"), `{date_line}`, `{benefits[]}` (each `{label, value}` like `ENERGY  FREE`), `{total_line}` (e.g. "ONE GREAT DAY"), `{footer_text}`

**Template prompt summary:** Top-down photo of a long thermal-printer receipt on a soft cream surface, slightly curled at the bottom, with the brand product placed beside it. Receipt content in monospaced caps: store header, "BENEFITS RECEIVED" section with itemized lines, faux barcode at the bottom, footer text. Soft warm natural light.

Validated example: `iterations/ag1-v2/T26-cash-register-receipt/`

---

## T27 — Handwritten founder letter

**When to use:** intimate brand storytelling. Founder voice, mission, gratitude, or insider-first-batch moment. Premium DTC brands use this to humanize at scale.

**Aspect ratio:** `2:3`

**Reference image:** product hero (placed beside the letter as a desk prop)

**Variables:** `{letter_body}` (handwritten cursive, 6-10 short lines max — keep it sparse), `{founder_name}`, `{footer}` (URL + role)

**Template prompt summary:** Top-down photo of cream stationery on a warm walnut desk, slightly tilted, with brand wordmark printed top-left. Letter body in flowing dark-blue cursive ink, organic imperfections (varying line weights, occasional ink flow). Black fountain pen across the bottom. Optional coffee-ring stain, edge of leather notebook, brand product visible in the upper-right corner.

**Note:** uni-1 partially garbles handwritten cursive — keep letter content under 10 lines and accept that 2-3 words may shift. The aesthetic and intent come through; word-perfect handwriting is hard.

Validated example: `iterations/ag1-v2/T27-handwritten-founder-letter/`

---

## T28 — Dating app swipe card (Hinge-style)

**When to use:** brand personality / "what we're about" angle. Treats the brand as a dateable persona. Strong for personality brands and lifestyle products.

**Aspect ratio:** `2:3`

**Reference image:** product hero (the photo on the profile card)

**Variables:** `{brand_age_label}` (e.g. "AG1, 75" — using ingredient count as age), `{location_line}` (e.g. "Foundational Nutrition · Here for the long haul"), `{prompts[]}` (2 prompt+answer pairs in Hinge style)

**Template prompt summary:** Hinge-style profile card centered on cream background. Card has: header (brand name as "age" + location), hero product photo, 2 stacked answer prompts (each: small grey label + bold black answer + small grey heart icon), and the X / ♥ buttons centered at the bottom.

Validated example: `iterations/ag1-v2/T28-dating-app-swipe/`

---

## T29 — TikTok creator video screenshot

**When to use:** UGC creator energy. "Influencer holding the product mid-explanation" with chunky white-on-black caption text + comments overlay sliding up from the bottom. Native to TikTok/Reels.

**Aspect ratio:** `9:16`

**Reference image:** product hero

**Variables:** `{creator_description}` (1-line — age, energy, setting), `{caption_text}` (3-4 short lines, white on black rounded-rectangles), `{comments[]}` (2 fake comments with @handle + body + heart count)

**Template prompt summary:** Vertical canvas filled with a cinematic shallow-DOF kitchen photo of a casual creator holding the product up to camera mid-grin. White-text-on-black-rounded-rectangle TikTok-style captions in lower-mid area. Semi-transparent comments-overlay panel in the lower third with 2 visible comments. Plain text only — no emoji in body text.

Validated example: `iterations/ag1-v2/T29-tiktok-creator/`

---

## T30 — Billboard / OOH placement mockup

**When to use:** "we're a real brand" credibility through scale. Subway, transit, or street billboard imagery. Gives the brand the gravitas of an OOH campaign.

**Aspect ratio:** `1:1`

**Reference image:** product hero (small product photo at the bottom of the billboard)

**Variables:** `{environment}` (e.g. "modern subway platform"), `{billboard_headline}` (2 stacked lines, bold sans), `{billboard_subcopy}`, `{brand.color_primary}` (billboard background), `{brand.url}`

**Template prompt summary:** Cinematic photograph of a vertical digital billboard set in a real-world transit environment with motion-blurred pedestrians and atmospheric lighting. Inside the billboard: brand-color background, small brand wordmark top-left, large headline + sub-copy, small product photo near the bottom, URL at the very bottom. Premium DTC OOH aesthetic.

Validated example: `iterations/ag1-v2/T30-billboard-ooh/`

---

## T31 — Scratch-off lottery ticket

**When to use:** novelty / interactive feel. Treats the brand's benefits as "scratch to win" panels. Tactile, fun, distinctive.

**Aspect ratio:** `2:3`

**Reference image:** product hero (one of the 6 panels shows the actual product photo)

**Variables:** `{ticket_title}` (e.g. "Match to Foundational Nutrition"), `{benefit_panels[]}` (5 panels, each `{icon, label}`), `{footer_line}` (e.g. "$0 LOSING TICKETS. EVERY SCOOP WINS."), `{ticket_serial}`

**Template prompt summary:** Top-down photo of a cardstock scratch-off ticket on a textured surface, brand-color border framing a 3x2 grid of 5 silver scratch-off panels (with realistic foil partially scratched, revealing icons + labels) plus 1 panel containing the brand product photo. Title at top, "WIN ALL FIVE = …" line at bottom. Coin prop in lower-right corner. Silver flake dust scattered around.

Validated example: `iterations/ag1-v2/T31-scratch-off-ticket/`

---

## T32 — Pain-point checklist + product

**When to use:** problem-aware audiences. Lead with their pain via an unchecked-checkbox list, deliver the product as the answer below.

**Aspect ratio:** `1:1`

**Reference image:** product hero

**Variables:** `{headline}` (2-line bold all-caps question or statement), `{checklist_items[]}` (exactly 5 unchecked items, each conversational), `{tagline}` (1 closing line in bold serif), `{footer_url_line}`

**Template prompt summary:** Pure white background. Top: bold black headline (~60pt). Middle: 5 unchecked checkbox rows, generous spacing. Lower-middle: clean product hero photo. Bottom: bold serif tagline + small caption with brand name and URL. Modern editorial layout.

Validated example: `iterations/ag1-v2/T32-headline-checklist/`

---

## T33 — Bold typography hero quote

**When to use:** stop-the-scroll brutalist statement. Strong for declarative or contrarian brand voice. Type IS the visual.

**Aspect ratio:** `1:1`

**Reference image:** product hero (small product accent in the lower-right)

**Variables:** `{statement}` (3-line punchy declaration in chunky condensed sans, ~140pt feel, period at the end), `{supporting_text}` (3-4 short lines in the lower-left), `{brand.color_primary}` (canvas background), `{type_color}` (cream off-white that contrasts the brand color)

**Template prompt summary:** Brand-color canvas with subtle radial vignette. Top 60%: HUGE bold condensed sans-serif statement, left-aligned, in cream off-white, three lines, tight letter/line-spacing. A small hand-drawn arrow curves from the period to the lower-right. Lower-right corner: small product photo color-matched to the background. Lower-left: small cream supporting text. Brutalist-meets-premium typography.

Validated example: `iterations/ag1-v2/T33-bold-typography-quote/`

---

## T34 — iMessage conversation (with rich link card)

**When to use:** "friend recommended it" social proof. Pixel-faithful iOS Messages screenshot, including a rich link preview card embedded in the conversation.

**Aspect ratio:** `9:16`

**Reference image:** product hero (used in the rich link preview card)

**Variables:** `{contact_name}`, `{messages[]}` (4 bubbles total: 2 incoming grey, 2 outgoing blue including 1 with a rich link card preview), `{rich_card.url}`, `{rich_card.title}`, `{rich_card.description}`

**Template prompt summary:** White background with iOS Messages header (contact avatar + name + timestamp + FaceTime icon). 4 bubbles in alternating grey (incoming) and blue (outgoing) with one outgoing message rendered as a rich link preview card containing the product photo + URL + title + 1-line description. iMessage input pill at the bottom. No iOS status bar, no home indicator, no Messages tab bar.

Validated example: `iterations/ag1-v2/T34-imessage-conversation/`

---

## T35 — Magazine cover

**When to use:** premium brand spotlight. Editorial magazine masthead with the product as the cover hero. Pairs well with wellness, fashion, lifestyle categories.

**Aspect ratio:** `2:3`

**Reference image:** product hero (the cover photograph)

**Variables:** `{magazine_title}` (e.g. "VITALITY"), `{issue_subbar}` (e.g. "THE WELLNESS ISSUE · SUMMER 2026 · ISSUE 16"), `{cover_lines[]}` (3-4 cover-line headlines stacked down the left edge, each with a topic + 1-line description), `{spotlight_badge_text}`, `{bottom_band_text}` (italic serif, 2 lines)

**Template prompt summary:** Top: bold serif magazine masthead + issue sub-bar. Left edge: vertical stack of cover-line headlines (each headline + one-line desc). Center-right: hero product photograph. Upper-right: small circular brand-spotlight badge. Bottom inset band with italic serif tagline + small caps subtitle. Glossy magazine cover aesthetic.

Validated example: `iterations/ag1-v2/T35-magazine-cover/`

---

## T36 — Lifestyle "operator's daily kit" flatlay

**When to use:** "what's in my bag/desk" lifestyle association. Curated flatlay of the brand product alongside aspirational everyday-carry items, each labeled with a small annotation. Strong for premium DTC trying to attach to a target audience's identity.

**Aspect ratio:** `1:1`

**Reference image:** product hero (centerpiece of the flatlay)

**Variables:** `{surface_color}` (typically charcoal-black or warm walnut), `{items[]}` (6-8 EDC items each with `{description, position, label}`), `{center_caption}` (small product label under the centerpiece)

**Template prompt summary:** Top-down flatlay on dark moody surface. Brand product as the centerpiece. 6-8 surrounding items (laptop, water bottle, phone, notebook, earbuds, glasses, wallet, etc.) arranged with negative space. Each item has a thin white hairline annotation line connecting it to a small white sans-serif caption. Cinematic top-down lighting.

Validated example: `iterations/ag1-v2/T36-lifestyle-flatlay/`

---

## T37 — Weather-app forecast UI

**When to use:** "your day on the brand" wellness narrative styled as a weather forecast. Each "hour" is a brand-driven outcome (Clear Strategy, Stress-Free Sunset, etc.). Distinctive and on-trend.

**Aspect ratio:** `1:1`

**Reference image:** product hero

**Variables:** `{headline}` (2-line "0% Stress." style), `{forecast_columns[]}` (5 columns, each `{time, icon_shape, condition_label, subtitle}`)

**Template prompt summary:** Soft cream background. Small "FORECAST SOURCE" caps header, then bold black 2-line headline. Hairline divider. 5-column hourly forecast strip with stylized minimal vector icons (sun, lightning, sparkle, sunset, moon — render as shapes, not literal emoji). Each column: time + icon + condition + subtitle. Below: small product hero. Brand line at the bottom.

Validated example: `iterations/ag1-v2/T37-weather-forecast/`

---

## T38 — Big stat hero with chart

**When to use:** data-led credibility. Lead with a giant percentage/number, support with a minimal line chart, anchor with the product. Strong for outcome-driven brands (supplements, productivity, finance).

**Aspect ratio:** `1:1`

**Reference image:** product hero (right side of the canvas)

**Variables:** `{stat_value}` (e.g. "-37%" — the giant headline number in chunky condensed sans), `{stat_subhead}` (2-line bold black, e.g. "LESS STRESS. / MORE FOCUS."), `{stat_caption}` (1-line explanation), `{chart_axis_labels}` (e.g. weekly markers), `{benefit_icon_rows}` (3 small icon+label rows)

**Template prompt summary:** White canvas. Top-left ~50%: huge brand-color condensed sans percentage statistic. Below the number: bold 2-line subhead, regular caption. Mini line chart with weekly markers and an emphasized data-point label. Three small icon-rows beneath. Right side: product hero with subtle drop shadow. Brand line at bottom. Modern data-led editorial.

Validated example: `iterations/ag1-v2/T38-stat-hero-chart/`

---

## T39 — Museum exhibit display

**When to use:** "the brand as cultural artifact" prestige play. Treats the product as an art piece on a plinth with a museum placard. Aspirational, premium, tongue-in-cheek.

**Aspect ratio:** `1:1`

**Reference image:** product hero (placed on the plinth)

**Variables:** `{placard_title}` (e.g. "AG1 NEXT GEN"), `{placard_subtitle}` (e.g. "Foundational Nutrition, 2026"), `{placard_body}` (2-4 sentence "museum label" describing the artifact in dry institutional voice)

**Template prompt summary:** Pale beige gallery wall, polished floor. Center-left: walnut-top dark-side plinth photographed at slight 3/4 angle, spot-lit from above. Brand product on the plinth, casting a soft elongated shadow. Right of center: wall-mounted white placard with thin grey border, formal museum-label typography (small caps brand line, serif title, subtitle, body, faint italic credit at bottom). Cinematic gallery lighting, hushed museum feel.

**Note:** uni-1 partially garbles the small placard body text. Keep it under 4 sentences and the title/subtitle will stay crisp.

Validated example: `iterations/ag1-v2/T39-museum-exhibit/`

---

## Adding new templates

When a new ad reference is worth turning into a template:
1. Generate a faithful reproduction with `--image-ref` set to the original reference (round 1).
2. Strip the chrome from the prompt and re-run (round 2) — verify the standalone creative still reads correctly.
3. Identify what's brand-specific vs. structural; replace brand-specific bits with `{placeholder}` variables.
4. Write a brand example fill against a different brand to verify the template generalizes.
5. Add the section to this file with: when-to-use, aspect ratio, reference image guidance, variable schema, template prompt, example fill, and path to the validated example.

## Known uni-1 rendering limits (most now mitigated by always-on suffixes)

- **Dense small text still garbles** even with the glyph-safety suffix. Keep body-text blocks SPARSE — 3-4 short lines max for chat/response bubbles, large readable size. The fix is fewer words, not more rules.
- **Reference image bleeds.** When the reference is a product hero, uni-1 sometimes draws extra product shots into negative space even when not requested. Usually harmless; constrain with "NO additional product shots beyond the one described" if it's a problem.
- **Tall content + 1:1 canvas = clipping.** Even with `SAFE_ZONE_SUFFIX`, a held-up board / letter sign / portrait product really benefits from a tall aspect ratio (`2:3` or `9:16`). Pick the canvas to match the focal subject's proportions.

**Solved by the always-on suffixes (no longer need to call out per template):**
- ~~iOS chrome / Sponsored badges / engagement rows leak in~~ — handled by `NO_CHROME_SUFFIX`
- ~~Headlines clipping at edges~~ — handled by `SAFE_ZONE_SUFFIX`
- ~~Emoji in chat bubbles becomes glyph soup~~ — handled by `GLYPH_SAFETY_SUFFIX`
- ~~Phantom 3rd comment / extra Slack message appears~~ — handled by `GLYPH_SAFETY_SUFFIX` count constraint
