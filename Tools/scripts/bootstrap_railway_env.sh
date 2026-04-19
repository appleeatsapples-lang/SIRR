#!/usr/bin/env bash
# SIRR — Railway environment bootstrap
# Generates SIRR_TOKEN_SECRET, SIRR_ENCRYPTION_KEY, SIRR_INTERNAL_SECRET
# and pushes them to the currently-linked Railway service.
#
# Prerequisite: run `railway login` once (opens browser), then `railway link`
# into the magnificent-friendship / web service.
#
# Usage:
#   ./Tools/scripts/bootstrap_railway_env.sh
#   ./Tools/scripts/bootstrap_railway_env.sh --dry-run
set -euo pipefail

DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
fi

if ! command -v railway >/dev/null 2>&1; then
  echo "railway CLI not found. Install: npm install -g @railway/cli" >&2
  exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found — needed to generate secrets" >&2
  exit 1
fi
if ! railway whoami >/dev/null 2>&1; then
  echo "not logged in. Run: railway login" >&2
  exit 1
fi

gen() { python3 -c "import secrets; print(secrets.token_hex(32))"; }

echo "generating three 32-byte hex secrets"
T="$(gen)"
E="$(gen)"
I="$(gen)"

echo "linked Railway context:"
railway status 2>&1 | sed 's/^/    /' || { echo "no linked service. Run: railway link"; exit 1; }

set_var() {
  local name="$1" value="$2"
  local preview="${value:0:6}...${value: -4}"
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "    [dry-run] $name = $preview"
  else
    echo "    setting $name ($preview)"
    railway variables --set "$name=$value" >/dev/null
  fi
}

echo ""
echo "setting variables:"
set_var "SIRR_TOKEN_SECRET"    "$T"
set_var "SIRR_ENCRYPTION_KEY"  "$E"
set_var "SIRR_INTERNAL_SECRET" "$I"

if [[ $DRY_RUN -eq 1 ]]; then
  echo ""
  echo "dry-run complete. No changes made."
  exit 0
fi

echo ""
echo "all three env vars set. Railway will redeploy automatically."
echo ""
echo "Save these offline (1Password, whatever):"
echo "  SIRR_TOKEN_SECRET    = $T"
echo "  SIRR_ENCRYPTION_KEY  = $E"
echo "  SIRR_INTERNAL_SECRET = $I"
echo ""
echo "After redeploy (~2 min), verify:"
echo "  curl -so /dev/null -w '%{http_code}\\n' -X POST https://web-production-ec2871.up.railway.app/api/internal/purge"
echo "  expect 401 (was 503 before SIRR_INTERNAL_SECRET was set)"
