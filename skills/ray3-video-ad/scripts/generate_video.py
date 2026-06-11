#!/usr/bin/env python3
"""
Generate, edit, or reframe video via Luma's ray-3.2 API.

Brand contract: this script REFUSES to use any model other than `ray-3.2`
for video, mirroring the uni-1 lock on the image side. Do not relax this
check.

Modes:
  --mode video          (default) text-to-video, optionally anchored with
                        --start-frame / --end-frame (image-to-video,
                        interpolation, or extend via gen:<id>).
  --mode video_edit     re-render a --source video under a new prompt,
                        preserving motion/performance per --strength /
                        --auto-controls / --controls-json. Supports up to
                        64 guide keyframes (--keyframe + --keyframe-indexes).
  --mode video_reframe  outpaint a --source video to a new --aspect-ratio.

Frame/source value syntax (for --start-frame, --end-frame, --source, --keyframe):
  gen:<uuid>            a prior Luma generation (extend / edit chaining)
  http(s)://…           a hosted URL
  anything else         a local file path, base64-inlined

Cost safety: every run logs an estimated cost to stderr BEFORE submitting.
Use --dry-run to print the exact request JSON (base64 elided) + cost and
exit without submitting or spending anything.

Output contract:
  stdout: one JSON object per successful variant, one per line
          {"variant": int, "path": str, "extra_paths": [str], "generation_id": str,
           "mode": str, "resolution": str, "duration": str|null,
           "aspect_ratio": str|null, "est_cost_usd": float|null, "prompt": str}
  stderr: human-readable progress + errors
  exit:   0 if at least one variant succeeded; 1 if all failed; 2 on bad args.

Stdlib only. No `requests`, no `python-dotenv`.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

API_BASE = "https://agents.lumalabs.ai/v1/generations"
LOCKED_MODEL = "ray-3.2"
ALLOWED_MODES = {"video", "video_edit", "video_reframe"}
ALLOWED_RATIOS = {"9:16", "3:4", "1:1", "4:3", "16:9", "21:9"}
ALLOWED_RESOLUTIONS = {"540p", "720p", "1080p"}
ALLOWED_DURATIONS = {"5s", "10s"}
ALLOWED_STRENGTHS = {
    f"{band}_{n}" for band in ("adhere", "flex", "reimagine") for n in (1, 2, 3)
}
MAX_EDIT_KEYFRAMES = 64
MAX_SOURCE_MB = 200
POLL_INTERVAL_S = 5
POLL_TIMEOUT_S = 900  # 1080p/HDR jobs can run several minutes

# Per-clip SDR pricing; HDR/EXR 5s-only (per docs/luma-agents-api/video-generation.md)
SDR_PRICE = {
    "540p": {"5s": 0.15, "10s": 0.45},
    "720p": {"5s": 0.30, "10s": 0.90},
    "1080p": {"5s": 1.20, "10s": 3.60},
}
HDR_PRICE = {"720p": 0.60, "1080p": 2.40}
HDR_EXR_PRICE = {"720p": 0.90, "1080p": 3.60}
# Reframe bills per output second ($0.06–$0.36/s by resolution; midpoint mapping)
REFRAME_PER_SECOND = {"540p": 0.06, "720p": 0.12, "1080p": 0.36}

IMAGE_MEDIA_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
}
VIDEO_MEDIA_TYPES = {
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".webm": "video/webm",
}

# Auto-appended to every prompt unless --allow-chrome is set. Same contract
# as the image side: the output is the standalone ad creative the advertiser
# uploads, not a screen recording of how it displays in-app.
NO_CHROME_SUFFIX = (
    "\n\n[NO PLATFORM CHROME] Render only the standalone ad video (the file uploaded to Meta), "
    "not a screen recording of it playing in-feed. Exclude: phone status bars and home indicators; "
    "platform UI overlays (TikTok/Reels/Stories buttons, like/comment/share stacks, music tickers, "
    "progress bars); usernames, handles, avatars, or Sponsored labels; engagement counters; "
    "captions-app subtitle chrome; any watermark or app logo. Just the standalone video."
)

# Always on for ad work: keep supers/text inside the safe area so platform
# UI overlays don't cover them when the ad runs.
SAFE_ZONE_SUFFIX = (
    "\n\n[EDGE-SAFE] Any on-screen text, supers, product wordmarks, and key focal subjects stay "
    "within the central 80% of the frame for the full clip duration — nothing important within "
    "the top/bottom 10% where platform UI overlays sit."
)


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def load_api_key(env_path: Path) -> str:
    """Parse LUMA_API_KEY from a .env file. No external deps."""
    if not env_path.exists():
        raise SystemExit(f"error: .env not found at {env_path}")
    for raw in env_path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        if k.strip() == "LUMA_API_KEY":
            v = v.strip().strip('"').strip("'")
            if not v:
                raise SystemExit("error: LUMA_API_KEY is empty in .env")
            return v
    raise SystemExit("error: LUMA_API_KEY not found in .env")


def slugify(text: str, max_len: int = 40) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:max_len] or "video"


def parse_frame_ref(value: str) -> dict:
    """Parse a frame reference: gen:<id> | URL | local image path."""
    if value.startswith("gen:"):
        gen_id = value[4:].strip()
        if not gen_id:
            raise SystemExit(f"error: empty generation id in '{value}'")
        return {"generation_id": gen_id}
    if value.startswith(("http://", "https://")):
        return {"url": value}
    path = Path(value)
    if not path.exists():
        raise SystemExit(f"error: frame image not found: {path}")
    mt = IMAGE_MEDIA_TYPES.get(path.suffix.lower())
    if not mt:
        raise SystemExit(
            f"error: unsupported image extension '{path.suffix}' for {path}. "
            f"Supported: {sorted(IMAGE_MEDIA_TYPES)}"
        )
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return {"data": data, "media_type": mt}


def parse_source_ref(value: str) -> dict:
    """Parse a source video reference: gen:<id> | URL | local video path."""
    if value.startswith("gen:"):
        gen_id = value[4:].strip()
        if not gen_id:
            raise SystemExit(f"error: empty generation id in '{value}'")
        return {"generation_id": gen_id}
    if value.startswith(("http://", "https://")):
        # Hosted URLs require an explicit media_type; mp4 is the safe default.
        return {"url": value, "media_type": "video/mp4"}
    path = Path(value)
    if not path.exists():
        raise SystemExit(f"error: source video not found: {path}")
    mt = VIDEO_MEDIA_TYPES.get(path.suffix.lower())
    if not mt:
        raise SystemExit(
            f"error: unsupported video extension '{path.suffix}' for {path}. "
            f"Supported: {sorted(VIDEO_MEDIA_TYPES)}"
        )
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > MAX_SOURCE_MB:
        raise SystemExit(
            f"error: {path.name} is {size_mb:.0f} MB — Luma caps inline/URL "
            f"sources at {MAX_SOURCE_MB} MB. Trim or compress first."
        )
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return {"data": data, "media_type": mt}


def estimate_cost(args) -> float | None:
    """Best-effort USD estimate per variant. None when the tier is unknown."""
    res = args.resolution
    if args.mode == "video":
        if args.hdr:
            table = HDR_EXR_PRICE if args.exr else HDR_PRICE
            return table.get(res)
        return SDR_PRICE.get(res, {}).get(args.duration)
    if args.mode == "video_reframe":
        per_s = REFRAME_PER_SECOND.get(res)
        secs = probe_source_seconds(args.source)
        if per_s is None or secs is None:
            return None
        return round(per_s * secs, 4)
    return None  # video_edit: dedicated tier, not published in our offline docs


def probe_source_seconds(source_value: str | None) -> float | None:
    """Duration of a local source video via ffprobe, if available."""
    if not source_value or source_value.startswith(("gen:", "http://", "https://")):
        return None
    if not shutil.which("ffprobe"):
        return None
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", source_value],
            capture_output=True, text=True, timeout=15, check=True,
        ).stdout.strip()
        return float(out)
    except Exception:  # noqa: BLE001
        return None


def probe_video(path: Path) -> dict:
    """Best-effort width/height/duration via ffprobe. Empty dict if unavailable."""
    if not shutil.which("ffprobe"):
        return {}
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height", "-show_entries",
             "format=duration", "-of", "json", str(path)],
            capture_output=True, text=True, timeout=15, check=True,
        ).stdout
        info = json.loads(out)
        stream = (info.get("streams") or [{}])[0]
        return {
            "width": stream.get("width"),
            "height": stream.get("height"),
            "seconds": round(float(info.get("format", {}).get("duration", 0)), 2),
        }
    except Exception:  # noqa: BLE001
        return {}


def http_post_json(url: str, headers: dict, body: dict, timeout: int = 120,
                   max_429_retries: int = 12) -> dict:
    """POST with retry on 429 (RPM or concurrent-job limit). Honors Retry-After."""
    attempt = 0
    while True:
        req = urllib.request.Request(
            url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")[:2000]
            if e.code == 429 and attempt < max_429_retries:
                attempt += 1
                wait = int(e.headers.get("Retry-After") or 60)
                log(f"  429 ({detail[:80]}…) — retry {attempt}/{max_429_retries} in {wait}s")
                time.sleep(wait)
                continue
            raise RuntimeError(f"HTTP {e.code} from Luma: {detail}") from e


def http_get_json(url: str, headers: dict, timeout: int = 30) -> dict:
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def http_download(url: str, dest: Path, timeout: int = 600) -> None:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp, dest.open("wb") as out:
        while chunk := resp.read(256 * 1024):
            out.write(chunk)


def redact(obj):
    """Deep-copy a request body with base64 payloads elided for logging."""
    if isinstance(obj, dict):
        return {
            k: ("<base64 elided>" if k == "data" else redact(v))
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [redact(v) for v in obj]
    return obj


def build_body(args, start_obj, end_obj, source_obj, keyframe_objs) -> dict:
    final_prompt = args.prompt
    if not args.allow_chrome:
        final_prompt += NO_CHROME_SUFFIX
    final_prompt += SAFE_ZONE_SUFFIX

    body: dict = {"prompt": final_prompt, "model": LOCKED_MODEL, "type": args.mode}
    video: dict = {"resolution": args.resolution}

    if args.mode == "video":
        if args.aspect_ratio:
            body["aspect_ratio"] = args.aspect_ratio
        video["duration"] = args.duration
        if args.loop:
            video["loop"] = True
        if args.hdr:
            video["hdr"] = True
        if args.exr:
            video["exr_export"] = True
        if start_obj:
            video["start_frame"] = start_obj
        if end_obj:
            video["end_frame"] = end_obj

    elif args.mode == "video_edit":
        body["source"] = source_obj
        if args.hdr:
            video["hdr"] = True
        if args.exr:
            video["exr_export"] = True
        if start_obj:
            video["start_frame"] = start_obj
        edit: dict = {}
        if args.controls_json:
            edit["controls"] = json.loads(args.controls_json)
        elif args.strength:
            edit["strength"] = args.strength
        else:
            edit["auto_controls"] = True
        if keyframe_objs:
            edit["keyframes"] = keyframe_objs
            edit["keyframe_indexes"] = args.keyframe_indexes_parsed
        video["edit"] = edit

    elif args.mode == "video_reframe":
        body["source"] = source_obj
        body["aspect_ratio"] = args.aspect_ratio
        if args.source_position_parsed:
            video["source_position"] = args.source_position_parsed

    body["video"] = video
    return body


def poll(gen_id: str, api_key: str) -> list[dict]:
    """Poll until completed. Returns the output entries."""
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    deadline = time.monotonic() + POLL_TIMEOUT_S
    last_state = None
    while time.monotonic() < deadline:
        resp = http_get_json(f"{API_BASE}/{gen_id}", headers)
        state = resp.get("state")
        if state != last_state:
            log(f"  [{gen_id[:8]}] state={state}")
            last_state = state
        if state == "completed":
            outputs = resp.get("output") or []
            if not outputs or not outputs[0].get("url"):
                raise RuntimeError(f"completed but no output url: {resp}")
            return outputs
        if state == "failed":
            raise RuntimeError(
                f"generation failed: {resp.get('failure_reason')} "
                f"(code={resp.get('failure_code')})"
            )
        time.sleep(POLL_INTERVAL_S)
    raise TimeoutError(f"generation {gen_id} did not complete in {POLL_TIMEOUT_S}s")


def output_ext(entry: dict) -> str:
    url = entry.get("url", "")
    path_part = url.split("?", 1)[0].lower()
    for ext in (".mp4", ".mov", ".webm", ".exr", ".png", ".jpg"):
        if path_part.endswith(ext):
            return ext
    mt = (entry.get("media_type") or "").lower()
    if "exr" in mt:
        return ".exr"
    return ".mp4"


def generate_one(variant, body, out_dir, slug, ts, api_key, est_cost, args) -> dict:
    log(f"variant {variant}: submitting (mode={args.mode})…")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    resp = http_post_json(API_BASE, headers, body)
    gen_id = resp.get("id")
    if not gen_id:
        raise RuntimeError(f"submit returned no id: {resp}")
    log(f"variant {variant}: id={gen_id}")
    outputs = poll(gen_id, api_key)

    primary: Path | None = None
    extras: list[str] = []
    for i, entry in enumerate(outputs):
        ext = output_ext(entry)
        suffix = "" if i == 0 else f"-{i}"
        dest = out_dir / f"{ts}-{slug}-v{variant}{suffix}{ext}"
        log(f"variant {variant}: downloading output {i} -> {dest.name}")
        http_download(entry["url"], dest)
        if i == 0:
            primary = dest
        else:
            extras.append(str(dest))

    probed = probe_video(primary) if primary else {}
    if probed:
        log(
            f"variant {variant}: {probed.get('width')}x{probed.get('height')} "
            f"{probed.get('seconds')}s"
        )
    return {
        "variant": variant,
        "path": str(primary),
        "extra_paths": extras,
        "generation_id": gen_id,
        "mode": args.mode,
        "resolution": args.resolution,
        "duration": args.duration if args.mode == "video" else None,
        "aspect_ratio": args.aspect_ratio,
        "est_cost_usd": est_cost,
        "prompt": args.prompt,
        **probed,
    }


def validate(args) -> None:
    """Enforce ray-3.2 constraint matrix before spending money."""
    err = lambda m: (_ for _ in ()).throw(SystemExit(f"error: {m}"))  # noqa: E731

    if args.mode == "video":
        if args.source:
            err("--source is only for video_edit / video_reframe. "
                "For image-to-video use --start-frame.")
        if args.keyframe or args.keyframe_indexes:
            err("--keyframe is only for --mode video_edit.")
        if args.strength or args.auto_controls or args.controls_json:
            err("edit controls are only for --mode video_edit.")
        if args.duration == "10s" and (args.hdr or args.start_frame or args.end_frame):
            err("10s clips reject hdr/start-frame/end-frame (5s only for those). "
                "Chain extends (--start-frame gen:<id>) to go longer.")
        if args.loop and (args.duration == "10s" or args.hdr or args.end_frame):
            err("--loop is incompatible with 10s, --hdr, and --end-frame.")
        if args.hdr and args.resolution == "540p":
            err("--hdr requires 720p or 1080p.")
        if args.exr and not args.hdr:
            err("--exr requires --hdr.")

    elif args.mode == "video_edit":
        if not args.source:
            err("--source is required for video_edit.")
        if args.end_frame:
            err("--end-frame is not supported in video_edit (use --keyframe).")
        if args.loop:
            err("--loop is not supported in video_edit.")
        if args.aspect_ratio:
            log("warn: --aspect-ratio is ignored for video_edit "
                "(output matches the source).")
        picked = [bool(args.strength), args.auto_controls, bool(args.controls_json)]
        if sum(picked) > 1:
            err("pick ONE of --strength / --auto-controls / --controls-json.")
        if args.hdr and args.resolution == "540p":
            err("--hdr requires 720p or 1080p.")
        if args.exr and not args.hdr:
            err("--exr requires --hdr.")
        if bool(args.keyframe) != bool(args.keyframe_indexes):
            err("--keyframe and --keyframe-indexes must be provided together.")
        if args.keyframe:
            if args.start_frame:
                err("--keyframe is mutually exclusive with --start-frame.")
            if len(args.keyframe) > MAX_EDIT_KEYFRAMES:
                err(f"too many keyframes ({len(args.keyframe)}); max {MAX_EDIT_KEYFRAMES}.")
            if len(args.keyframe) != len(args.keyframe_indexes_parsed):
                err(f"{len(args.keyframe)} keyframes but "
                    f"{len(args.keyframe_indexes_parsed)} indexes — counts must match.")

    elif args.mode == "video_reframe":
        if not args.source:
            err("--source is required for video_reframe.")
        if not args.aspect_ratio:
            err("--aspect-ratio (target) is required for video_reframe.")
        for flag, name in ((args.hdr, "--hdr"), (args.exr, "--exr"),
                           (args.loop, "--loop"), (args.start_frame, "--start-frame"),
                           (args.end_frame, "--end-frame"), (args.keyframe, "--keyframe")):
            if flag:
                err(f"{name} is not supported in video_reframe.")
        if args.resolution == "1080p" and args.aspect_ratio in {"9:16", "3:4"}:
            err("vertical targets at 1080p are not supported yet — use 720p.")


def main() -> int:
    p = argparse.ArgumentParser(
        description="Generate/edit/reframe ray-3.2 video. Brand contract: ray-3.2 only.",
    )
    p.add_argument("--prompt", required=True, help="Video prompt (post-rewrite).")
    p.add_argument("--mode", default="video", choices=sorted(ALLOWED_MODES))
    p.add_argument("--aspect-ratio", choices=sorted(ALLOWED_RATIOS),
                   help="Optional for video (model picks); required target for "
                        "video_reframe; ignored for video_edit.")
    p.add_argument("--resolution", default="720p", choices=sorted(ALLOWED_RESOLUTIONS))
    p.add_argument("--duration", default="5s", choices=sorted(ALLOWED_DURATIONS),
                   help="video mode only. 10s is text-to-video SDR only.")
    p.add_argument("--loop", action="store_true", help="Seamless loop (video mode).")
    p.add_argument("--hdr", action="store_true", help="HDR MP4 (720p/1080p, 5s).")
    p.add_argument("--exr", action="store_true", help="16-bit EXR sidecar (needs --hdr).")
    p.add_argument("--start-frame", metavar="REF",
                   help="First-frame anchor: gen:<id> | URL | local image. "
                        "In video_edit this is the single guide frame.")
    p.add_argument("--end-frame", metavar="REF",
                   help="Last-frame anchor: gen:<id> | URL | local image (video mode).")
    p.add_argument("--source", metavar="REF",
                   help="Source video for video_edit/video_reframe: "
                        "gen:<id> | URL | local file (≤200 MB, ≤30s).")
    p.add_argument("--strength", choices=sorted(ALLOWED_STRENGTHS),
                   help="video_edit preset: adhere_1..3 | flex_1..3 | reimagine_1..3.")
    p.add_argument("--auto-controls", action="store_true",
                   help="video_edit: let the model derive conditioning (default "
                        "when no --strength/--controls-json given).")
    p.add_argument("--controls-json", metavar="JSON",
                   help="video_edit per-signal controls as raw JSON "
                        '(e.g. \'{"pose":{"enabled":true,"strength":"precise"}}\').')
    p.add_argument("--keyframe", action="append", default=[], metavar="REF",
                   help=f"video_edit guide keyframe (repeatable, max {MAX_EDIT_KEYFRAMES}); "
                        "pair with --keyframe-indexes.")
    p.add_argument("--keyframe-indexes", metavar="N,N,…",
                   help="Comma-separated source frame indexes, one per --keyframe.")
    p.add_argument("--source-position", metavar="X,Y,W,H",
                   help="video_reframe: normalized source placement "
                        "(x_norm,y_norm,w_norm,h_norm). Omit for centered fit.")
    p.add_argument("--n", type=int, default=1, help="Variant count, 1-3 (video is $$).")
    p.add_argument("--out", type=Path, default=Path("./generated"))
    p.add_argument("--model", default=LOCKED_MODEL,
                   help=f"Locked to {LOCKED_MODEL} by brand contract.")
    p.add_argument("--env-file", type=Path, default=Path(".env"))
    p.add_argument("--allow-chrome", action="store_true",
                   help="Allow platform/screen-recording UI in the output. Default "
                        "strips it so the output is the standalone ad creative.")
    p.add_argument("--dry-run", action="store_true",
                   help="Print the request JSON (base64 elided) + cost estimate "
                        "and exit WITHOUT submitting.")
    args = p.parse_args()

    if args.model != LOCKED_MODEL:
        log(
            f"error: brand contract violation — video model must be '{LOCKED_MODEL}', "
            f"got '{args.model}'. This script refuses, same as the uni-1 lock on images."
        )
        return 2

    if not (1 <= args.n <= 3):
        log(f"error: --n must be 1..3 for video (got {args.n}) — clips cost real money.")
        return 2

    # Parse compound args before validation.
    args.keyframe_indexes_parsed = []
    if args.keyframe_indexes:
        try:
            args.keyframe_indexes_parsed = [
                int(x) for x in args.keyframe_indexes.split(",") if x.strip() != ""
            ]
        except ValueError:
            log(f"error: --keyframe-indexes must be comma-separated integers, "
                f"got '{args.keyframe_indexes}'")
            return 2

    args.source_position_parsed = None
    if args.source_position:
        parts = args.source_position.split(",")
        if len(parts) != 4:
            log("error: --source-position needs exactly 4 comma-separated floats "
                "(x_norm,y_norm,w_norm,h_norm).")
            return 2
        try:
            x, y, w, h = (float(v) for v in parts)
        except ValueError:
            log(f"error: non-numeric --source-position '{args.source_position}'")
            return 2
        args.source_position_parsed = {
            "x_norm": x, "y_norm": y, "w_norm": w, "h_norm": h,
        }

    if args.controls_json:
        try:
            json.loads(args.controls_json)
        except json.JSONDecodeError as e:
            log(f"error: --controls-json is not valid JSON: {e}")
            return 2

    try:
        validate(args)
    except SystemExit as e:
        log(str(e))
        return 2

    # Encode refs ONCE; reused across variants.
    start_obj = parse_frame_ref(args.start_frame) if args.start_frame else None
    end_obj = parse_frame_ref(args.end_frame) if args.end_frame else None
    source_obj = parse_source_ref(args.source) if args.source else None
    keyframe_objs = [parse_frame_ref(k) for k in args.keyframe]

    body = build_body(args, start_obj, end_obj, source_obj, keyframe_objs)
    est = estimate_cost(args)
    est_str = f"~${est:.2f}" if est is not None else "unknown (dedicated tier)"
    total_str = f" (x{args.n} = ~${est * args.n:.2f})" if est is not None and args.n > 1 else ""
    log(f"estimated cost per variant: {est_str}{total_str}")

    if args.dry_run:
        log("dry run — request body (base64 elided), NOT submitted:")
        print(json.dumps(redact(body), indent=2))
        return 0

    api_key = load_api_key(args.env_file)
    args.out.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    slug = slugify(args.prompt)

    log(
        f"generating {args.n} variant(s) mode={args.mode} res={args.resolution}"
        f"{' dur=' + args.duration if args.mode == 'video' else ''}"
        f"{' ar=' + args.aspect_ratio if args.aspect_ratio else ''} -> {args.out}/"
    )

    results: list[dict] = []
    errors: list[str] = []
    with ThreadPoolExecutor(max_workers=args.n) as ex:
        futures = {
            ex.submit(generate_one, i, body, args.out, slug, ts, api_key, est, args): i
            for i in range(1, args.n + 1)
        }
        for fut in as_completed(futures):
            i = futures[fut]
            try:
                results.append(fut.result())
            except Exception as e:  # noqa: BLE001
                errors.append(f"variant {i}: {e}")
                log(f"variant {i}: FAILED — {e}")

    results.sort(key=lambda r: r["variant"])
    for r in results:
        print(json.dumps(r), flush=True)

    if not results:
        log(f"all {args.n} variant(s) failed")
        return 1
    if errors:
        log(f"{len(results)}/{args.n} succeeded, {len(errors)} failed")
    else:
        log(f"all {args.n} variant(s) succeeded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
