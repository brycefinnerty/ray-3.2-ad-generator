#!/usr/bin/env python3
"""
Create a Meta ad creative with ONE image and multiple body/title variations.

This is "Pattern 2" — single image, single CTA, single link, but Meta cycles
through 1-5 bodies and 1-5 titles within a single ad. The Meta CLI's DCO mode
can't produce this exact shape; it always treats images as part of the asset
feed and fails with "asset feed can have exactly one ad format."

We hit the Marketing API directly:
  1. POST /act_<id>/adimages   → upload PNG, get image_hash
  2. POST /act_<id>/adcreatives → create creative with object_story_spec.link_data
                                  + asset_feed_spec.bodies/titles

Output: prints the new creative ID on stdout. Errors to stderr.

Reads ACCESS_TOKEN and AD_ACCOUNT_ID from a .env file. Stdlib only.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

GRAPH = "https://graph.facebook.com/v21.0"

ALLOWED_CTAS = {
    "APPLY_NOW", "BOOK_TRAVEL", "BUY_NOW", "CONTACT_US", "DOWNLOAD",
    "GET_OFFER", "GET_QUOTE", "LEARN_MORE", "NO_BUTTON", "OPEN_LINK",
    "SHOP_NOW", "SIGN_UP", "SUBSCRIBE", "WATCH_MORE",
}


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def load_env(env_path: Path) -> dict[str, str]:
    if not env_path.exists():
        raise SystemExit(f"error: .env not found at {env_path}")
    out: dict[str, str] = {}
    for raw in env_path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def http_post(url: str, fields: dict, timeout: int = 120) -> dict:
    """POST application/x-www-form-urlencoded. Returns parsed JSON."""
    data = urllib.parse.urlencode(fields).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {e.code} from {url}:\n{body}") from None


def upload_image(account_id: str, image_path: Path, token: str) -> str:
    """Upload an image to /adimages, return its hash."""
    log(f"uploading {image_path.name}…")
    payload = base64.b64encode(image_path.read_bytes()).decode("ascii")
    resp = http_post(
        f"{GRAPH}/{account_id}/adimages",
        {
            "access_token": token,
            "bytes": payload,
        },
    )
    images = resp.get("images") or {}
    if not images:
        raise SystemExit(f"upload returned no image hash: {resp}")
    # The key in `images` is the filename Meta inferred — we only have one.
    info = next(iter(images.values()))
    h = info.get("hash")
    if not h:
        raise SystemExit(f"upload response missing hash: {resp}")
    log(f"  image_hash={h}")
    return h


def create_creative(
    account_id: str,
    name: str,
    page_id: str,
    image_hash: str,
    link_url: str,
    cta: str,
    bodies: list[str],
    titles: list[str],
    descriptions: list[str],
    token: str,
) -> str:
    """Create the creative with object_story_spec + asset_feed_spec."""
    object_story_spec = {
        "page_id": page_id,
        "link_data": {
            "image_hash": image_hash,
            "link": link_url,
            "call_to_action": {
                "type": cta,
                "value": {"link": link_url},
            },
        },
    }
    asset_feed_spec: dict = {
        "bodies": [{"text": b} for b in bodies],
        "titles": [{"text": t} for t in titles],
        "optimization_type": "DEGREES_OF_FREEDOM",
    }
    if descriptions:
        asset_feed_spec["descriptions"] = [{"text": d} for d in descriptions]

    log(
        f"creating creative '{name}' "
        f"({len(bodies)} bodies × {len(titles)} titles)…"
    )
    resp = http_post(
        f"{GRAPH}/{account_id}/adcreatives",
        {
            "access_token": token,
            "name": name,
            "object_story_spec": json.dumps(object_story_spec),
            "asset_feed_spec": json.dumps(asset_feed_spec),
        },
    )
    cid = resp.get("id")
    if not cid:
        raise SystemExit(f"creative create returned no id: {resp}")
    return cid


def main() -> int:
    p = argparse.ArgumentParser(
        description=(
            "Create a Meta ad creative with one image + multiple body/title "
            "variations (Pattern 2: single-image, multi-text)."
        )
    )
    p.add_argument("--name", required=True, help="Creative display name.")
    p.add_argument("--image", required=True, type=Path, help="Path to image PNG/JPG.")
    p.add_argument("--page-id", required=True, help="Facebook Page ID.")
    p.add_argument("--link-url", required=True, help="Destination URL.")
    p.add_argument(
        "--call-to-action",
        required=True,
        choices=sorted(ALLOWED_CTAS),
        help="CTA button type.",
    )
    p.add_argument(
        "--body",
        action="append",
        default=[],
        help="Body text. Repeat for multiple variants (1-5).",
    )
    p.add_argument(
        "--title",
        action="append",
        default=[],
        help="Title/headline. Repeat for multiple variants (1-5).",
    )
    p.add_argument(
        "--description",
        action="append",
        default=[],
        help="Optional description. Repeat for multiple variants (max 5).",
    )
    p.add_argument(
        "--env-file",
        type=Path,
        default=Path(".env"),
        help="Path to .env (default: ./.env).",
    )
    args = p.parse_args()

    if not args.image.exists():
        log(f"error: image not found: {args.image}")
        return 2
    if not args.body or not args.title:
        log("error: provide at least one --body and one --title")
        return 2
    if len(args.body) > 5 or len(args.title) > 5 or len(args.description) > 5:
        log("error: max 5 each of --body, --title, --description")
        return 2

    env = load_env(args.env_file)
    token = env.get("ACCESS_TOKEN")
    account_id = env.get("AD_ACCOUNT_ID")
    if not token:
        raise SystemExit("error: ACCESS_TOKEN missing in .env")
    if not account_id:
        raise SystemExit("error: AD_ACCOUNT_ID missing in .env")

    image_hash = upload_image(account_id, args.image, token)
    creative_id = create_creative(
        account_id=account_id,
        name=args.name,
        page_id=args.page_id,
        image_hash=image_hash,
        link_url=args.link_url,
        cta=args.call_to_action,
        bodies=args.body,
        titles=args.title,
        descriptions=args.description,
        token=token,
    )
    log(f"  creative_id={creative_id}")
    print(creative_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
