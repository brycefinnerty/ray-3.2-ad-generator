#!/usr/bin/env python3
"""
Pull the top-N spending ads in the configured Meta ad account, with each ad's
body + title copy attached. Used in Phase 5.5 of uni1-image-ad to ground new
copy in what's actually winning spend.

Output contract:
  stdout: one JSON object per top ad, sorted by spend desc:
    {ad_id, ad_name, spend, impressions, ctr, creative_id, body, title}
  stderr: progress + warnings
  exit:   0 on success; 1 on hard failure

Reads ACCESS_TOKEN and AD_ACCOUNT_ID from the meta CLI's environment (it
parses the project .env automatically). Runs `meta -o json ads …` under the
hood so the auth path is identical to interactive use.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def run_meta(args: list[str], timeout: int = 60):
    """Run `meta -o json …` and return the parsed JSON, or None on empty."""
    p = subprocess.run(
        ["meta", "-o", "json"] + args,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if p.returncode != 0:
        raise RuntimeError(f"meta {' '.join(args)}: {p.stderr.strip()}")
    out = p.stdout.strip()
    return json.loads(out) if out else None


def parse_pseudo_json(s: str) -> dict | None:
    """The meta CLI sometimes prints fields like:
        "<AdCreative> {\n    \"id\": \"821...\"\n}"
    Extract and parse the brace-delimited JSON body."""
    if not isinstance(s, str):
        return None
    m = re.search(r"\{.*\}", s, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def extract_creative_id(ad: dict) -> str | None:
    raw = ad.get("creative")
    if isinstance(raw, dict):
        return raw.get("id")
    if isinstance(raw, str):
        parsed = parse_pseudo_json(raw)
        if parsed:
            return parsed.get("id")
    return None


def extract_copy(creative: dict) -> tuple[str, str]:
    """Return (body, title) from a creative response."""
    body = creative.get("body") or ""
    title = creative.get("title") or ""
    oss = creative.get("object_story_spec")
    if isinstance(oss, str):
        oss = parse_pseudo_json(oss)
    if isinstance(oss, dict):
        ld = oss.get("link_data") or {}
        if not body:
            body = ld.get("message") or ""
        if not title:
            title = ld.get("name") or ""
    return body.strip(), title.strip()


def get_ad_spend(ad_id: str, days: int) -> tuple[float, int, float]:
    res = run_meta(
        [
            "ads", "insights", "get",
            "--ad-id", ad_id,
            "--date-preset", f"last_{days}d",
            "--fields", "spend,impressions,ctr",
        ]
    )
    rows = res.get("data") if isinstance(res, dict) else res
    if not rows:
        return 0.0, 0, 0.0
    r = rows[0]
    try:
        return float(r.get("spend", 0)), int(r.get("impressions", 0)), float(r.get("ctr", 0))
    except (TypeError, ValueError):
        return 0.0, 0, 0.0


def get_creative(creative_id: str) -> dict:
    res = run_meta(["ads", "creative", "get", creative_id])
    if isinstance(res, list):
        return res[0] if res else {}
    return res or {}


def main() -> int:
    p = argparse.ArgumentParser(
        description="List top-N spending ads with their body/title copy."
    )
    p.add_argument("--limit", type=int, default=10, help="Number of top ads to return.")
    p.add_argument(
        "--days",
        type=int,
        default=30,
        choices=[3, 7, 14, 30, 90],
        help="Lookback window in days.",
    )
    p.add_argument(
        "--max-scan",
        type=int,
        default=200,
        help="Max ads to query insights for. Increase if your account has many ads.",
    )
    p.add_argument(
        "--workers",
        type=int,
        default=8,
        help="Parallel insights queries.",
    )
    args = p.parse_args()

    log(f"listing ads (limit={args.max_scan})…")
    ads_res = run_meta(["ads", "ad", "list", "--limit", str(args.max_scan)])
    ads = ads_res if isinstance(ads_res, list) else (ads_res or {}).get("data", [])
    log(f"  {len(ads)} ads to scan")
    if not ads:
        log("no ads in account")
        return 0

    log(f"fetching {args.days}-day spend for each (parallel, {args.workers} workers)…")

    def score(ad: dict) -> dict:
        try:
            spend, imps, ctr = get_ad_spend(ad["id"], args.days)
        except Exception as e:  # noqa: BLE001
            log(f"  ad {ad['id']}: insights failed — {e}")
            spend, imps, ctr = 0.0, 0, 0.0
        return {**ad, "_spend": spend, "_impressions": imps, "_ctr": ctr}

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        scored = list(ex.map(score, ads))

    spending = [a for a in scored if a["_spend"] > 0]
    spending.sort(key=lambda a: a["_spend"], reverse=True)
    top = spending[: args.limit]
    log(f"  {len(spending)} ads with spend > 0; taking top {len(top)}")

    log(f"fetching copy for top {len(top)}…")

    def enrich(ad: dict) -> dict:
        cid = extract_creative_id(ad)
        body = title = ""
        if cid:
            try:
                creative = get_creative(cid)
                body, title = extract_copy(creative)
            except Exception as e:  # noqa: BLE001
                log(f"  creative {cid}: failed — {e}")
        return {
            "ad_id": ad["id"],
            "ad_name": ad.get("name", ""),
            "spend": round(ad["_spend"], 2),
            "impressions": ad["_impressions"],
            "ctr": round(ad["_ctr"], 4),
            "creative_id": cid,
            "body": body,
            "title": title,
        }

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        enriched = list(ex.map(enrich, top))

    for row in enriched:
        print(json.dumps(row), flush=True)

    total = sum(a["spend"] for a in enriched)
    log(f"\nDone. {len(enriched)} ads, ${total:,.2f} combined spend.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
