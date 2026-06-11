#!/usr/bin/env python3
"""Generate the full audio layer for a cinematic ad from project.json:
VO lines (ElevenLabs TTS), SFX stingers (sound-generation), and a music
cue at the exact runtime (music API).

project.json schema (audio sections):
{
  "audio_dir": "generated/<ad>/audio",
  "voice": "David Trailer",            // matched by name prefix in /v1/voices
  "voice_settings": {"stability": 0.4, "similarity_boost": 0.85, "style": 0.5},
  "vo":    [{"id": "vo1", "text": "Performance isn't loud."}, …],
  "sfx":   [{"id": "braam", "prompt": "deep cinematic trailer braam…", "seconds": 2.0}, …],
  "music_gen": {"prompt": "Cinematic product-launch trailer cue…", "seconds": 15.0}
}

Existing files are skipped (delete to regenerate). Measured VO durations are
printed as JSON on stdout — use them to build the timing map in project.json.

Usage:
  python3 make_audio.py --project project.json [--plan] [--env-file .env]

--plan prints what would be generated (with credit-cost hints) and exits
without calling any API. Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.elevenlabs.io"
TTS_MODEL = "eleven_multilingual_v2"
DEFAULT_VOICE_SETTINGS = {"stability": 0.40, "similarity_boost": 0.85, "style": 0.5}


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def load_key(env_path: Path) -> str:
    if not env_path.exists():
        raise SystemExit(f"error: .env not found at {env_path}")
    for raw in env_path.read_text().splitlines():
        if raw.strip().startswith("ELEVENLABS_API_KEY="):
            v = raw.split("=", 1)[1].strip().strip('"').strip("'")
            if v:
                return v
    raise SystemExit("error: ELEVENLABS_API_KEY not found in .env")


def post(path: str, body: dict, key: str, timeout: int = 600) -> bytes:
    req = urllib.request.Request(
        f"{API}{path}", data=json.dumps(body).encode(),
        headers={"xi-api-key": key, "Content-Type": "application/json"})
    try:
        return urllib.request.urlopen(req, timeout=timeout).read()
    except urllib.error.HTTPError as e:
        raise SystemExit(f"error: {path} -> HTTP {e.code}: "
                         f"{e.read().decode()[:300]}") from e


def ffprobe_dur(p: Path) -> float:
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
        capture_output=True, text=True, check=True).stdout.strip())


def resolve_voice(name: str, key: str) -> str:
    req = urllib.request.Request(f"{API}/v1/voices", headers={"xi-api-key": key})
    voices = json.loads(urllib.request.urlopen(req, timeout=60).read())["voices"]
    for v in voices:
        if v["name"].lower().startswith(name.lower()):
            log(f"voice: {v['name']} ({v['voice_id']})")
            return v["voice_id"]
    available = ", ".join(v["name"].split(" -")[0] for v in voices)
    raise SystemExit(f"error: no voice starting with '{name}'. Available: {available}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--env-file", type=Path, default=Path(".env"))
    ap.add_argument("--plan", action="store_true",
                    help="Print the generation plan and exit (no API calls).")
    args = ap.parse_args()

    proj = json.loads(args.project.read_text())
    out = Path(proj["audio_dir"])
    vo_lines = proj.get("vo", [])
    sfx_items = proj.get("sfx", [])
    music = proj.get("music_gen")

    if args.plan:
        chars = sum(len(l["text"]) for l in vo_lines)
        log(f"plan: {len(vo_lines)} VO lines (~{chars} chars), "
            f"{len(sfx_items)} SFX, music {music['seconds'] if music else 0}s "
            f"-> {out}/  (voice: {proj.get('voice', 'David Trailer')})")
        return 0

    key = load_key(args.env_file)
    (out / "sfx").mkdir(parents=True, exist_ok=True)
    durations: dict[str, float] = {}

    if vo_lines:
        vid = resolve_voice(proj.get("voice", "David Trailer"), key)
        settings = {**DEFAULT_VOICE_SETTINGS, **proj.get("voice_settings", {})}
        for line in vo_lines:
            dest = out / f"{line['id']}.mp3"
            if dest.exists():
                log(f"{line['id']}: cached")
            else:
                audio = post(f"/v1/text-to-speech/{vid}?output_format=mp3_44100_128",
                             {"text": line["text"], "model_id": TTS_MODEL,
                              "voice_settings": settings}, key, timeout=120)
                dest.write_bytes(audio)
            durations[line["id"]] = round(ffprobe_dur(dest), 2)
            log(f"{line['id']}: {durations[line['id']]:.2f}s — “{line['text']}”")

    for item in sfx_items:
        dest = out / "sfx" / f"{item['id']}.mp3"
        if dest.exists():
            log(f"sfx {item['id']}: cached")
            continue
        audio = post("/v1/sound-generation",
                     {"text": item["prompt"],
                      "duration_seconds": round(float(item["seconds"]), 1),
                      "prompt_influence": item.get("prompt_influence", 0.4)},
                     key, timeout=300)
        dest.write_bytes(audio)
        log(f"sfx {item['id']}: {item['seconds']}s, {len(audio) // 1024}KB")

    if music:
        dest = out / "music.mp3"
        if dest.exists():
            log("music: cached")
        else:
            # NB: brand/studio names in music prompts trip moderation — keep
            # prompts descriptive ("handmade animation feel", not "Aardman").
            audio = post("/v1/music",
                         {"prompt": music["prompt"],
                          "music_length_ms": int(float(music["seconds"]) * 1000)},
                         key, timeout=600)
            dest.write_bytes(audio)
        log(f"music: {ffprobe_dur(dest):.2f}s")

    print(json.dumps({"vo_durations": durations}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
