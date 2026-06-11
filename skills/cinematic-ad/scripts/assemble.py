#!/usr/bin/env python3
"""Assemble a fast-cut cinematic ad master from project.json:
trim each shot's clip to its window, concat on the grid, lay VO + SFX +
music at mapped times, master with loudnorm.

project.json schema (assembly sections):
{
  "total": 15.0,
  "loudnorm": "I=-14:TP=-1.5:LRA=9",
  "shots": [
    {"clip": "generated/<ad>/clips/s1/<file>.mp4", "offset": 0.8, "duration": 2.0},
    …                                  // offset = trim-in point within the 5s clip
  ],
  "audio_dir": "generated/<ad>/audio",
  "vo_events":  [{"file": "vo1.mp3", "start": 0.30, "volume": 1.0, "atempo": null}, …],
  "sfx_events": [{"file": "sfx/braam.mp3", "start": 0.0, "volume": 0.5}, …],
  "music_mix": {"file": "music.mp3", "volume": 0.32}
}

SFX longer than the remaining runtime are trimmed+faded automatically.

Usage:
  python3 assemble.py --project project.json --out master.mp4
Stdlib only (drives ffmpeg).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    proj = json.loads(args.project.read_text())
    total = float(proj["total"])
    shots = proj["shots"]
    audio_dir = Path(proj["audio_dir"])
    loudnorm = proj.get("loudnorm", "I=-14:TP=-1.5:LRA=9")

    grid = sum(s["duration"] for s in shots)
    if abs(grid - total) > 0.05:
        log(f"warn: shot durations sum to {grid:.2f}s but total is {total:.2f}s")

    inputs: list[str] = []
    flt: list[str] = []
    idx = 0

    for i, s in enumerate(shots):
        clip = Path(s["clip"])
        if not clip.exists():
            raise SystemExit(f"error: clip not found: {clip}")
        inputs += ["-i", str(clip)]
        flt.append(f"[{idx}:v]trim=start={s['offset']}:duration={s['duration']},"
                   f"setpts=PTS-STARTPTS[v{i}]")
        idx += 1
    flt.append("".join(f"[v{i}]" for i in range(len(shots))) +
               f"concat=n={len(shots)}:v=1:a=0[vout]")

    amix: list[str] = []
    for j, e in enumerate(proj.get("vo_events", [])):
        inputs += ["-i", str(audio_dir / e["file"])]
        ms = int(float(e["start"]) * 1000)
        chain = f"[{idx}:a]"
        if e.get("atempo"):
            chain += f"atempo={e['atempo']},"
        flt.append(chain + f"volume={e.get('volume', 1.0)},adelay={ms}|{ms}[vo{j}]")
        amix.append(f"[vo{j}]")
        idx += 1

    for j, e in enumerate(proj.get("sfx_events", [])):
        inputs += ["-i", str(audio_dir / e["file"])]
        start = float(e["start"])
        ms = int(start * 1000)
        room = max(total - start, 0.3)
        flt.append(f"[{idx}:a]atrim=duration={room},"
                   f"afade=t=out:st={max(room - 0.4, 0)}:d=0.4,"
                   f"volume={e.get('volume', 0.5)},adelay={ms}|{ms}[fx{j}]")
        amix.append(f"[fx{j}]")
        idx += 1

    music = proj.get("music_mix")
    if music:
        inputs += ["-i", str(audio_dir / music["file"])]
        flt.append(f"[{idx}:a]atrim=duration={total},"
                   f"afade=t=out:st={total - 0.4}:d=0.4,"
                   f"volume={music.get('volume', 0.3)}[mus]")
        amix.append("[mus]")
        idx += 1

    if not amix:
        raise SystemExit("error: no audio events in project.json")

    flt.append("".join(amix) + f"amix=inputs={len(amix)}:normalize=0,"
               f"loudnorm={loudnorm},apad=whole_dur={total}[aout]")

    cmd = ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(flt),
           "-map", "[vout]", "-map", "[aout]",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
           "-t", str(total), str(args.out)]
    subprocess.run(cmd, check=True, capture_output=True)
    log(f"wrote {args.out} ({total}s, {len(shots)} shots, {len(amix)} audio layers)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
