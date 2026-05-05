#!/usr/bin/env python3
"""Fire N uni-1 generations in parallel. Used for batch prompt-library iteration.

Each job is a dict: {name, prompt_path, ref_path, aspect, out_dir}
Reads jobs from a JSON file passed as argv[1]; writes per-job logs and PNGs
into out_dir; prints a summary table to stderr."""
import json, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Prefer the in-repo skill (works on a fresh clone before the user installs).
# Fall back to the user-installed skill at ~/.claude/skills/.
_REPO_SCRIPT = Path(__file__).resolve().parent.parent / "skills/uni1-image-ad/scripts/generate_image.py"
_HOME_SCRIPT = Path.home() / ".claude/skills/uni1-image-ad/scripts/generate_image.py"
SCRIPT = _REPO_SCRIPT if _REPO_SCRIPT.exists() else _HOME_SCRIPT


def run_job(job: dict) -> dict:
    name = job["name"]
    out_dir = Path(job["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    prompt = Path(job["prompt_path"]).read_text()
    cmd = [
        str(SCRIPT),
        "--prompt", prompt,
        "--aspect-ratio", job["aspect"],
        "--n", "1",
        "--out", str(out_dir),
        "--env-file", str(Path(__file__).parent.parent / ".env"),
    ]
    if job.get("ref_path"):
        cmd += ["--image-ref", job["ref_path"]]
    t0 = time.monotonic()
    p = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.monotonic() - t0
    result = {"name": name, "elapsed": round(elapsed, 1), "rc": p.returncode}
    if p.returncode == 0 and p.stdout.strip():
        try:
            out = json.loads(p.stdout.strip().splitlines()[0])
            result.update({"path": out["path"], "generation_id": out["generation_id"],
                           "width": out.get("width"), "height": out.get("height")})
        except Exception as e:
            result["parse_error"] = str(e)
            result["stdout"] = p.stdout
    else:
        result["stderr_tail"] = p.stderr.strip().splitlines()[-3:] if p.stderr else []
    return result


def main():
    jobs = json.loads(Path(sys.argv[1]).read_text())
    print(f"firing {len(jobs)} jobs in parallel…", file=sys.stderr)
    results = []
    with ThreadPoolExecutor(max_workers=len(jobs)) as ex:
        futures = {ex.submit(run_job, j): j["name"] for j in jobs}
        for fut in as_completed(futures):
            r = fut.result()
            status = "OK" if r["rc"] == 0 and "path" in r else "FAIL"
            print(f"  [{status}] {r['name']:<28} {r['elapsed']:>5}s "
                  f"{r.get('path','')}", file=sys.stderr)
            results.append(r)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
