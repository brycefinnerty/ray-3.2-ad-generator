#!/usr/bin/env bash
# install.sh — set up the uni1-image-ad workbench. Idempotent.
#
# 1. Checks prerequisites (Python 3.12+, uv)
# 2. Installs the Meta Ads CLI via uv if not present
# 3. Symlinks ./skills/uni1-image-ad into ~/.claude/skills/
# 4. Creates .env from .env.example if missing
#
# Does NOT touch credentials. Run ./verify.sh after editing .env to confirm
# everything is wired up.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS=(uni1-image-ad image-ad-clone)

green()  { printf "\033[32m%s\033[0m\n" "$*"; }
yellow() { printf "\033[33m%s\033[0m\n" "$*"; }
red()    { printf "\033[31m%s\033[0m\n" "$*" >&2; }

# 1. Python 3.12+
if ! command -v python3 >/dev/null 2>&1; then
  red "error: python3 not found."
  red "  macOS:  brew install python@3.13"
  red "  Linux:  see https://docs.python.org/3/using/index.html"
  exit 1
fi
PY_OK=$(python3 -c 'import sys; print(int(sys.version_info >= (3,12)))')
if [[ "$PY_OK" != "1" ]]; then
  red "error: Python 3.12+ required (got $(python3 --version))."
  exit 1
fi
green "ok   python3 $(python3 -c 'import sys;print("%d.%d.%d"%sys.version_info[:3])') detected"

# 2. uv
if ! command -v uv >/dev/null 2>&1; then
  red "error: uv not found."
  red "  macOS:  brew install uv"
  red "  any:    curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi
green "ok   uv $(uv --version 2>/dev/null | awk '{print $2}') detected"

# 3. meta-ads CLI
if ! command -v meta >/dev/null 2>&1; then
  yellow "→ installing meta-ads CLI via uv (one-time)…"
  uv tool install meta-ads --python 3.13
fi
META_VER=$(meta --version 2>/dev/null | awk '{print $3}')
green "ok   meta $META_VER detected"

# 4. Symlink the skills (both uni1-image-ad and image-ad-clone)
DEST_DIR="$HOME/.claude/skills"
mkdir -p "$DEST_DIR"

for skill in "${SKILLS[@]}"; do
  src="$REPO_ROOT/skills/$skill"
  dest="$DEST_DIR/$skill"
  if [[ ! -d "$src" ]]; then
    red "error: skill source not found at $src"
    exit 1
  fi
  if [[ -L "$dest" ]]; then
    current="$(readlink "$dest")"
    if [[ "$current" == "$src" ]]; then
      green "ok   $dest already linked to $src"
    else
      yellow "→ replacing stale symlink ($current → $src)"
      rm "$dest"
      ln -s "$src" "$dest"
      green "ok   linked $dest → $src"
    fi
  elif [[ -e "$dest" ]]; then
    red "error: $dest exists and is not a symlink."
    red "  Move or remove it manually if you want to install this skill there."
    exit 1
  else
    ln -s "$src" "$dest"
    green "ok   linked $dest → $src"
  fi
done

# 5. .env scaffolding
if [[ ! -f "$REPO_ROOT/.env" ]]; then
  cp "$REPO_ROOT/.env.example" "$REPO_ROOT/.env"
  yellow "→ created .env from .env.example (you need to fill it in)"
else
  green "ok   .env already exists"
fi

# Final summary
echo ""
green "=== install complete ==="
echo ""
echo "Next steps:"
echo "  1. Edit .env and fill in:"
echo "     LUMA_API_KEY     get from https://platform.lumalabs.ai → API keys"
echo "     ACCESS_TOKEN     Meta system user token; see README.md → 'Meta token setup'"
echo "     AD_ACCOUNT_ID    after auth: meta ads adaccount list (format: act_<numeric>)"
echo ""
echo "  2. Run ./verify.sh to confirm everything is wired correctly."
echo ""
echo "  3. IMPORTANT: open a fresh Claude Code session in this repo so the"
echo "     skill loads. Then ask: 'make a uni-1 image ad'."
