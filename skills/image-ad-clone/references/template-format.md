# Library entry format

The exact markdown skeleton for a `prompt-library.md` entry. Lazy-loaded by `image-ad-clone` Phase 8 before composing the entry. The seed library at `~/.claude/skills/uni1-image-ad/references/prompt-library.md` already contains T1–T7 in this format — match its style when appending new entries so the file stays consistent.

## Skeleton

```markdown
## {tag} — {one-line title}

**When to use:** {1-2 sentence positioning fit. What kind of ad is this? Who/what is it good for?}

**Aspect ratio:** `{ratio}` ({1-line why — e.g. "Meta feed-portrait friendly", "Stories / Reels"})

**Reference image:** {what kind of `--image-ref` to pass. Examples: "clean product hero (white background, all SKUs visible)", "lifestyle portrait of subject mid-action", "logo + product flatlay"}

**Variables:**
- `{variable_name}` — {description; what kind of value goes in it; format hint if any}
- `{variable_name}` — …

**Template prompt:**
\`\`\`
{The full prompt text, with {placeholders} embedded. Should produce a standalone ad creative when filled and paired with the reference image. No screenshot/platform chrome.}
\`\`\`

**Example fill** ({brand_name}):
- `{variable_name}` = `{example value}`
- `{variable_name}` = `{example value}`
- …

Validated example: `{path/to/iteration/dir/}`

---
```

(End every entry with a horizontal rule on its own line so the next entry has visual separation.)

## Field-by-field guidance

### `{tag}`
Format `T<n> — <short noun phrase>`. Continue numbering from the existing library — if T1–T7 exist, the next is T8. The noun phrase is searchable; pick something that describes the format, not the content (e.g. "T8 — Lifestyle hero with overlay text", not "T8 — AG1 morning shaker ad").

### `{one-line title}` (after the em-dash)
A short noun phrase distilling the format. 4-8 words. Examples: "Apple Notes listicle aesthetic", "Editorial article hero", "Comparison table (dark, hooky)".

### **When to use**
Two ideas: who/what brand fit (product category, target audience temperament), and which positioning angle (credibility, social proof, comparison, sentimental, etc.). Don't list rules; describe the gut fit.

### **Aspect ratio**
One of `1:1`, `2:3`, `9:16`, `1:2`, `1:3`, `3:2`, `16:9`, `2:1`, `3:1`. (Luma doesn't support `4:5` or `1.91:1` — use `2:3` for tall feed and `16:9` for wide instead.) Add a 1-line note on why this ratio (e.g. "Meta feed standard", "Stories / Reels", "Tall scroller for comparison-heavy content").

### **Reference image** (what `--image-ref` to pass)
Tell the future user/agent what kind of image to ground the generation on. The more specific the better:
- "Clean product hero shot, white background, all SKUs visible"
- "Lifestyle portrait, subject mid-action, soft daylight"
- "Logo wordmark on neutral background"
- "Existing ad in the same format" (rare — usually sub-optimal)

Reference images are how the brand identity stays faithful. Bad guidance here causes wrong-looking outputs no matter how good the prompt is.

### **Variables**
List every `{placeholder}` in the template prompt. For each, describe in one line:
- What the value represents
- The expected type / format (string? hex code? list? short headline?)
- Any constraints (max chars, must be one of an enum)

Use the standard variable names where they fit:

| Variable | Use for |
|---|---|
| `{brand.name}` | Wordmark text (e.g., the literal word/letters that appear on the packaging) |
| `{brand.color_primary}` | Primary brand color hex (`#RRGGBB`) |
| `{brand.color_accent}` | Secondary accent color hex |
| `{brand.product_image_description}` | One-line description of the product visible in the ad |
| `{brand.tagline}` | Short brand promise (≤6 words) |
| `{brand.competitor_category}` | What the brand is being compared against |
| `{ad.headline}` | Top-line headline |
| `{ad.subcopy}` | Sub-headline / supporting copy |
| `{ad.body}` | Primary text block |
| `{ad.cta_phrase}` | CTA button text |

For template-specific variables, name them clearly. Examples that already exist in the library:
- `{notes_title}`, `{checklist_items[]}` (T1)
- `{publication}`, `{photo_subject_description}`, `{tagline}`, `{band_color}` (T2)
- `{authority_name}`, `{tweet_body}`, `{ugc_subject}`, `{ugc_overlay_text}`, `{cursive_line}` (T3)
- `{search_query}`, `{grid_tile_descriptions[]}`, `{publication_logos[]}`, `{accent_color_family}` (T4)
- `{competitor_image_description}`, `{rows[]}`, `{row_accent_color}` (T5)
- `{hook_line_1}`, `{hook_line_2}`, `{competitor_label}`, `{table_columns}`, `{table_rows[]}` (T6)
- `{handwritten_text_lines}`, `{sticky_note_color}`, `{product_unit_description}`, `{powder_or_residue_hint}` (T7)

### **Template prompt**
The actual prompt body, in a fenced code block. Plug-and-play after substitution. Things to remember:
1. **Always specify aspect ratio at the top** as part of the prompt (e.g. "1:1 static ad creative, 1080x1080, edge-to-edge").
2. **Always describe the canvas as standalone** — phrases like "edge-to-edge", "static ad creative", "the standalone image that would be uploaded as a Meta creative". This pairs with the script's auto-appended no-chrome suffix to make sure the output is the actual upload, not a screenshot.
3. **Explicitly exclude chrome** in a closing paragraph: "No surrounding social platform UI: no brand row, no body copy, no engagement counts, no app navigation, no iOS device chrome." The auto-suffix is a safety net; the prompt itself should also be explicit.
4. **Describe regions in vertical order** — top X%, middle, bottom. Helps the model lay out predictably.
5. **Name reference roles when multiple refs are expected.** "The product visible in image_ref[0] should appear at center" — Luma's docs say this improves multi-ref fidelity.

### **Example fill**
Pick a real brand (AG1 is the seeded test case) and show every variable substituted. Should be the version that was actually validated in Phase 7 of the cloning skill.

### **Validated example path**
Pointer to `iterations/clone-<date>/<tag>/` — the directory containing the locked-in `prompt.txt`, the round-1 generation against the original reference, and the round-N generation against the test-fill brand. So a future agent (or human) can audit the template's provenance.

## Style notes for matching the existing library

- Use `*italic*` for terse asides, `**bold**` only for the section labels (`**When to use:**`, etc.) and key callouts.
- Hex codes go in backticks: `` `#1A4731` ``.
- Use em-dashes `—` (not `--`) for parenthetical asides.
- Wrap variables in single backticks: `` `{brand.name}` ``.
- Code-block fences use triple-backtick — no language tag for prompts (they're not code).
- The horizontal rule between entries is `---` on its own line, separated by blank lines from neighboring content.

## Hard rules

- **Never silently overwrite an existing entry.** If the new tag collides, ask the user before replacing.
- **Append, don't reorder.** New templates go at the bottom of the library, before any "Adding new templates" or footer sections. Don't reshuffle existing entries' order.
- **Keep entries self-contained.** Don't reference other library entries by tag inside a template prompt. Each entry should be readable and usable on its own.
