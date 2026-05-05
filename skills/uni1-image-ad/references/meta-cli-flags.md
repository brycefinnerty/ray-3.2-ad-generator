# Meta Ads CLI flag reference (uni1-image-ad skill)

Lazy-loaded by `SKILL.md` only when constructing upload commands. Keep this short
and exact — Claude reads this verbatim before composing each `meta` command.

CLI binary: `meta` (v1.0.1, package `meta-ads`). Authenticates via `ACCESS_TOKEN`
and uses `AD_ACCOUNT_ID` from the project `.env` automatically.

## Discovery (read-only)

```bash
meta auth status                        # confirms token is live
meta ads adaccount current              # echoes the active ad account
meta ads campaign list                  # list campaigns
meta ads adset list                     # list ad sets across all campaigns
meta ads adset list <CAMPAIGN_ID>       # ad sets under a specific campaign
meta ads ad list                        # list ads (use to find an ad to clone)
```

> Note: `meta ads page list` requires a `BUSINESS_ID` env var. The skill avoids
> this by deriving the page ID from the cloned ad's creative instead.

## Clone-from-ad lookup

The skill clones page/adset/link/CTA from an existing ad. Use these two reads:

```bash
# 1. Get the cloned ad's adset_id and creative.id
meta -o json ads ad get <AD_ID>

# 2. Get the cloned creative's page_id, link, and CTA
meta -o json ads creative get <CREATIVE_ID>
```

Fields to extract from the creative:

| Field path | Use as |
|---|---|
| `object_story_spec.page_id` | `--page-id` for new creative |
| `object_story_spec.link_data.link` | `--link-url` for new creative |
| `object_story_spec.link_data.call_to_action.type` | `--call-to-action` for new creative |
| `object_story_spec.link_data.message` | reference only — do not reuse verbatim |
| `object_story_spec.link_data.name` | reference only — do not reuse verbatim |

## Creative create (image)

```bash
meta ads creative create \
  --name "<creative-name>" \
  --image <PATH_TO_PNG> \
  --page-id <PAGE_ID> \
  [--body "<primary-text>"] \
  [--title "<headline>"] \
  [--link-url "<destination-url>"] \
  [--call-to-action <CTA>]
```

| Flag | Required | Notes |
|---|---|---|
| `--name` | yes | Internal label for the creative. Use `<base> v<i>` for variants. |
| `--image` | yes | Local file path. Accepts `.png`, `.jpg`, `.gif`, `.bmp`, `.webp`. |
| `--page-id` | yes | Facebook Page ID. From `meta ads page list`. |
| `--body` | no | Primary text shown above the image. |
| `--title` | no | Headline below the image. |
| `--link-url` | no | Destination URL when the user clicks the ad. |
| `--call-to-action` | no | Enum: `SHOP_NOW`, `LEARN_MORE`, `SIGN_UP`, `BUY_NOW`, `WATCH_MORE`, `DOWNLOAD`. |

Returns the new creative ID on stdout. To force JSON output for parsing:

```bash
meta -o json ads creative create … | jq -r '.id'
```

## Ad create

```bash
meta ads ad create <ADSET_ID> \
  --name "<ad-name>" \
  --creative-id <CREATIVE_ID>
```

| Flag / arg | Required | Notes |
|---|---|---|
| `<ADSET_ID>` | yes | Positional. Existing ad set; v1 of the skill never creates new ones. |
| `--name` | yes | Display name for the ad. |
| `--creative-id` | yes | ID returned from `meta ads creative create`. |
| `--status` | NEVER PASS | Default is `PAUSED`. The skill MUST NOT override this. |

Returns the new ad ID on stdout (or `.id` in JSON mode).

## Verifying a created ad

```bash
meta ads ad get <AD_ID>                  # confirms status=PAUSED, creative_id, etc.
```

## Ads Manager deep link

```
https://business.facebook.com/adsmanager/manage/ads?act=<ACCOUNT_NUMERIC>&selected_ad_ids=<AD_ID>
```

`<ACCOUNT_NUMERIC>` is the `act_…` ID with the `act_` prefix stripped.

## Common errors

| Error | Likely cause | Fix |
|---|---|---|
| `Not authenticated.` (exit 3) | Missing/expired `ACCESS_TOKEN` | Generate a fresh system-user token in Meta Business Suite → System Users → Generate New Token. Update `.env`. |
| `code 17` / `code 32` / `code 613` | Marketing API rate limit | Back off 60s and retry; surface to user if it persists. |
| `Invalid parameter: image` | Image below Meta's dimension floor or unsupported format | Regenerate at higher resolution; the helper script enforces a 1080×1080 minimum. |
| `permission denied` on the page | System user lacks page access | In Meta Business Suite → System Users → Assign Assets, grant the page to the system user. |

## Token refresh quick steps

1. Meta Business Suite → Settings → Users → System Users → select your system user.
2. Click **Generate New Token**, pick the app, grant scopes:
   `business_management`, `ads_management`, `pages_show_list`,
   `pages_read_engagement`, `pages_manage_ads`, `catalog_management`,
   `read_insights`.
3. Copy the token, replace `ACCESS_TOKEN=…` in `<project>/.env`.
4. `meta auth status` should print `Authenticated`.
