#!/usr/bin/env python3
"""Claymation-ad production pipeline: VO -> timeline -> SFX -> music -> mix.

Operates on a PROJECT DIRECTORY containing project.json:

{
  "voice": "George",                  // ElevenLabs voice name prefix (or exact id)
  "music_prompt": "…instrumental…",   // NO brand/studio names — moderation rejects them
  "beats": [
    {"vo": "This is Dave. …", "sfx": "soft tense office ambience: …"},
    …one entry per beat, in order…
  ],
  "vo_gap": 0.40,        // optional overrides ↓
  "min_beat": 3.0, "max_beat": 5.0, "end_hold": 1.8,
  "vol_sfx": 0.32, "vol_music": 0.17, "lufs": -15
}

Expected layout produced by the workflow (see SKILL.md):
  <project>/clips/bNN/result.json   — generate_video.py output per beat (NN = 01..)
  <project>/audio/beatNN.mp3        — VO lines (created by `vo` step)
  <project>/audio/sfx/beatNN.mp3    — sound effects (created by `sfx` step)
  <project>/audio/music.mp3         — score (created by `music` step)
  <project>/timeline.json           — created by `plan` step
  <project>/master.mp4              — created by `mix` step

Steps are cached: delete an artifact to regenerate it.

Usage:
  python3 claymation_pipeline.py <project-dir> [vo|plan|sfx|music|mix|all] [--env-file .env]
"""
import json, subprocess, sys, time, urllib.request, urllib.error
from pathlib import Path

CUT_LEAD = 0.15   # J-cut: scene cut lands this far after the next VO line starts
VO_START = 0.30


def die(msg):
    sys.exit(f"error: {msg}")


def load_key(env_file):
    for line in open(env_file):
        if line.startswith("ELEVENLABS_API_KEY="):
            return line.split("=", 1)[1].strip()
    die(f"no ELEVENLABS_API_KEY in {env_file}")


def ffprobe_dur(p):
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
        capture_output=True, text=True, check=True).stdout.strip())


def el_post(key, path, body, timeout=600):
    req = urllib.request.Request(
        f"https://api.elevenlabs.io{path}", data=json.dumps(body).encode(),
        headers={"xi-api-key": key, "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            return urllib.request.urlopen(req, timeout=timeout).read()
        except urllib.error.HTTPError as e:
            detail = e.read().decode()[:300]
            if e.code == 429 and attempt < 2:
                time.sleep(30); continue
            raise RuntimeError(f"{path} -> HTTP {e.code}: {detail}") from e


class Project:
    def __init__(self, root, env_file):
        self.root = Path(root)
        cfg_path = self.root / "project.json"
        if not cfg_path.exists():
            die(f"{cfg_path} not found")
        self.cfg = json.load(open(cfg_path))
        self.beats = self.cfg["beats"]
        self.n = len(self.beats)
        self.env_file = env_file
        self.opt = lambda k, d: self.cfg.get(k, d)

    # -- step: vo ------------------------------------------------------------
    def vo(self):
        key = load_key(self.env_file)
        req = urllib.request.Request("https://api.elevenlabs.io/v1/voices",
                                     headers={"xi-api-key": key})
        voices = json.loads(urllib.request.urlopen(req).read())["voices"]
        want = self.opt("voice", "George")
        vid = next((v["voice_id"] for v in voices
                    if v["name"].startswith(want) or v["voice_id"] == want), None)
        if not vid:
            die(f"voice '{want}' not found")
        out = self.root / "audio"; out.mkdir(parents=True, exist_ok=True)
        for i, b in enumerate(self.beats, 1):
            dest = out / f"beat{i:02d}.mp3"
            if dest.exists():
                print(f"vo beat{i:02d}: cached"); continue
            audio = el_post(key, f"/v1/text-to-speech/{vid}?output_format=mp3_44100_128",
                            {"text": b["vo"], "model_id": "eleven_multilingual_v2",
                             "voice_settings": {"stability": 0.45,
                                                "similarity_boost": 0.75, "style": 0.35}})
            dest.write_bytes(audio)
            print(f"vo beat{i:02d}: {ffprobe_dur(dest):.2f}s")

    # -- step: plan ----------------------------------------------------------
    def plan(self):
        gap = self.opt("vo_gap", 0.40)
        min_b, max_b = self.opt("min_beat", 3.0), self.opt("max_beat", 5.0)
        end_hold = self.opt("end_hold", 1.8)
        vo_dur = [ffprobe_dur(self.root / f"audio/beat{i:02d}.mp3")
                  for i in range(1, self.n + 1)]
        vo_start, t = [], VO_START
        for d in vo_dur:
            vo_start.append(round(t, 3)); t += d + gap
        starts, s = [], 0.0
        for i in range(self.n):
            starts.append(round(s, 3))
            if i < self.n - 1:
                s = min(max(vo_start[i + 1] - CUT_LEAD, s + min_b), s + max_b)
        total = round(max(starts[-1] + min_b, vo_start[-1] + vo_dur[-1] + end_hold), 3)
        durs = [round((starts + [total])[i + 1] - starts[i], 3) for i in range(self.n)]
        tl = {"vo_start": vo_start, "vo_dur": [round(d, 3) for d in vo_dur],
              "beat_start": starts, "beat_dur": durs, "total": total}
        json.dump(tl, open(self.root / "timeline.json", "w"), indent=1)
        for i in range(self.n):
            print(f"beat{i+1:02d}: video {starts[i]:6.2f}s +{durs[i]:.2f}s | "
                  f"VO {vo_start[i]:6.2f}s–{vo_start[i]+vo_dur[i]:6.2f}s")
        print(f"TOTAL: {total:.2f}s")

    # -- step: sfx -----------------------------------------------------------
    def sfx(self):
        key = load_key(self.env_file)
        tl = json.load(open(self.root / "timeline.json"))
        out = self.root / "audio/sfx"; out.mkdir(parents=True, exist_ok=True)
        for i, b in enumerate(self.beats):
            dest = out / f"beat{i+1:02d}.mp3"
            if dest.exists() or not b.get("sfx"):
                print(f"sfx beat{i+1:02d}: {'cached' if dest.exists() else 'none'}")
                continue
            dur = min(tl["beat_dur"][i], 22.0)
            audio = el_post(key, "/v1/sound-generation",
                            {"text": b["sfx"], "duration_seconds": round(dur, 1),
                             "prompt_influence": 0.35})
            dest.write_bytes(audio)
            print(f"sfx beat{i+1:02d}: {dur:.1f}s")

    # -- step: music ---------------------------------------------------------
    def music(self):
        dest = self.root / "audio/music.mp3"
        if dest.exists():
            print("music: cached"); return
        prompt = self.opt("music_prompt", None)
        if not prompt:
            print("music: no music_prompt in project.json — skipping"); return
        key = load_key(self.env_file)
        tl = json.load(open(self.root / "timeline.json"))
        audio = el_post(key, "/v1/music",
                        {"prompt": prompt, "music_length_ms": int(tl["total"] * 1000)})
        dest.write_bytes(audio)
        print(f"music: {tl['total']:.1f}s")

    # -- step: mix -----------------------------------------------------------
    def mix(self):
        tl = json.load(open(self.root / "timeline.json"))
        vol_sfx, vol_mus = self.opt("vol_sfx", 0.32), self.opt("vol_music", 0.17)
        lufs = self.opt("lufs", -15)
        clips = []
        for i in range(1, self.n + 1):
            rj = self.root / f"clips/b{i:02d}/result.json"
            if not rj.exists():
                die(f"{rj} missing — animate beats first (generate_video.py)")
            clips.append(json.load(open(rj))["path"])
        inputs, flt, idx, amix_in = [], [], 0, []
        for i, c in enumerate(clips):
            inputs += ["-i", c]
            flt.append(f"[{idx}:v]trim=duration={tl['beat_dur'][i]},"
                       f"setpts=PTS-STARTPTS[v{i}]"); idx += 1
        flt.append("".join(f"[v{i}]" for i in range(self.n)) +
                   f"concat=n={self.n}:v=1:a=0[vout]")
        for i in range(self.n):
            inputs += ["-i", str(self.root / f"audio/beat{i+1:02d}.mp3")]
            ms = int(tl["vo_start"][i] * 1000)
            flt.append(f"[{idx}:a]adelay={ms}|{ms}[vo{i}]")
            amix_in.append(f"[vo{i}]"); idx += 1
        for i in range(self.n):
            p = self.root / f"audio/sfx/beat{i+1:02d}.mp3"
            if not p.exists():
                continue
            inputs += ["-i", str(p)]
            ms, d = int(tl["beat_start"][i] * 1000), tl["beat_dur"][i]
            flt.append(f"[{idx}:a]atrim=duration={d},"
                       f"afade=t=out:st={max(d-0.5,0)}:d=0.5,volume={vol_sfx},"
                       f"adelay={ms}|{ms}[fx{i}]")
            amix_in.append(f"[fx{i}]"); idx += 1
        mp = self.root / "audio/music.mp3"
        if mp.exists():
            inputs += ["-i", str(mp)]
            flt.append(f"[{idx}:a]atrim=duration={tl['total']},"
                       f"afade=t=out:st={tl['total']-1.5}:d=1.5,volume={vol_mus}[mus]")
            amix_in.append("[mus]"); idx += 1
        flt.append("".join(amix_in) + f"amix=inputs={len(amix_in)}:normalize=0,"
                   f"loudnorm=I={lufs}:TP=-1.5:LRA=11,apad=whole_dur={tl['total']}[aout]")
        out = str(self.root / "master.mp4")
        subprocess.run(
            ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(flt),
             "-map", "[vout]", "-map", "[aout]",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18",
             "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
             "-t", str(tl["total"]), out],
            check=True, capture_output=True)
        print(f"wrote {out} ({tl['total']:.2f}s)")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    env_file = ".env"
    if "--env-file" in sys.argv:
        env_file = sys.argv[sys.argv.index("--env-file") + 1]
    if not args:
        die("usage: claymation_pipeline.py <project-dir> [vo|plan|sfx|music|mix|all]")
    proj = Project(args[0], env_file)
    step = args[1] if len(args) > 1 else "all"
    for s in (["vo", "plan", "sfx", "music", "mix"] if step == "all" else [step]):
        getattr(proj, s)()


if __name__ == "__main__":
    main()
