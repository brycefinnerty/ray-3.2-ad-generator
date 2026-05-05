#!/usr/bin/env bash
# verify.sh — confirm the uni1-image-ad workbench is fully wired up.
# Run after install.sh and after editing .env.
#
# Checks:
#   1. .env exists with all three required vars
#   2. AD_ACCOUNT_ID has the right format
#   3. Skill is symlinked into ~/.claude/skills/
#   4. meta CLI auth works
#   5. Luma uni-1 API key authenticates
#
# Exit code 0 if all pass, 1 otherwise.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
green() { printf "\033[32m%s\033[0m\n" "$*"; }
red()   { printf "\033[31m%s\033[0m\n" "$*"; }

cd "$REPO_ROOT"
fail=0

# 1. .env
if [[ ! -f .env ]]; then
  red "FAIL .env not found. Run ./install.sh, then edit .env."
  exit 1
fi
set -a; source .env; set +a

for var in LUMA_API_KEY ACCESS_TOKEN AD_ACCOUNT_ID; do
  if [[ -z "${!var:-}" ]]; then
    red "FAIL $var is empty in .env"
    fail=1
  else
    green "ok   $var present"
  fi
done

# 2. AD_ACCOUNT_ID format
if [[ -n "${AD_ACCOUNT_ID:-}" ]]; then
  if [[ ! "$AD_ACCOUNT_ID" =~ ^act_[0-9]+$ ]]; then
    red "FAIL AD_ACCOUNT_ID must look like 'act_<numeric>' (got '$AD_ACCOUNT_ID')"
    fail=1
  else
    green "ok   AD_ACCOUNT_ID format valid"
  fi
fi

# 3. Skill symlinks (both skills)
for skill in uni1-image-ad image-ad-clone; do
  dest="$HOME/.claude/skills/$skill"
  expected="$REPO_ROOT/skills/$skill"
  if [[ -L "$dest" && "$(readlink "$dest")" == "$expected" ]]; then
    green "ok   $skill symlinked at $dest"
  else
    red "FAIL $skill not correctly symlinked at $dest. Run ./install.sh."
    fail=1
  fi
done

# 4. Meta CLI
if ! command -v meta >/dev/null 2>&1; then
  red "FAIL meta CLI not on PATH. Run ./install.sh."
  fail=1
elif meta auth status 2>&1 | grep -q "Authenticated"; then
  green "ok   meta auth status: Authenticated"
else
  red "FAIL meta auth status not Authenticated"
  red "     ACCESS_TOKEN may be wrong, expired, or missing scopes."
  red "     See README.md → 'Meta token setup'."
  fail=1
fi

# 5. Luma API smoke test
if [[ -n "${LUMA_API_KEY:-}" ]]; then
  # Submitting a generation (HTTP 200/201) confirms auth works.
  # NOTE: this counts as one Luma generation (~$0.02). The submission
  # is left in "queued" state and not polled — cheapest verification
  # path the API supports.
  resp=$(curl -s -o /tmp/uni1-verify.json -w "%{http_code}" \
    -X POST https://agents.lumalabs.ai/v1/generations \
    -H "Authorization: Bearer $LUMA_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"prompt":"verify-test","model":"uni-1","type":"image","aspect_ratio":"1:1"}' 2>/dev/null)
  if [[ "$resp" == "200" || "$resp" == "201" ]]; then
    green "ok   Luma uni-1 API authenticates (HTTP $resp)"
  else
    red "FAIL Luma API returned HTTP $resp (expected 200 or 201)"
    if [[ -s /tmp/uni1-verify.json ]]; then
      red "     response: $(cat /tmp/uni1-verify.json | head -c 300)"
    fi
    red "     LUMA_API_KEY may be wrong or you're hitting the legacy endpoint."
    fail=1
  fi
  rm -f /tmp/uni1-verify.json
fi

echo ""
if [[ $fail -eq 0 ]]; then
  green "✓ all checks passed"
  echo ""
  echo "IMPORTANT: open a fresh Claude Code session in this repo to load the skill."
  echo "Then ask: 'make a uni-1 image ad cloning ad <existing-ad-id>'."
  exit 0
else
  red "✗ verification failed; fix the errors above and re-run ./verify.sh"
  exit 1
fi
