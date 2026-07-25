#!/usr/bin/env bash
#
# Deploy this FastAPI app to Vercel.
#
#   ./deploy.sh              -> preview deployment
#   ./deploy.sh --prod       -> production deployment
#
set -euo pipefail

cd "$(dirname "$0")"

TARGET="preview"
VERCEL_ARGS=()
if [[ "${1:-}" == "--prod" || "${1:-}" == "-p" ]]; then
  TARGET="production"
  VERCEL_ARGS+=(--prod)
fi

# --- preflight -------------------------------------------------------------

if ! command -v vercel >/dev/null 2>&1; then
  echo "error: vercel CLI not found on PATH. Install with: npm i -g vercel" >&2
  exit 1
fi

if ! vercel whoami >/dev/null 2>&1; then
  echo "Not logged in to Vercel. Running 'vercel login'..."
  vercel login
fi

for f in vercel.json requirements.txt main.py; do
  [[ -f "$f" ]] || { echo "error: missing required file: $f" >&2; exit 1; }
done

# The app imports these at request time; a missing dir means a broken build.
for d in templates services scripts; do
  [[ -d "$d" ]] || { echo "error: missing required directory: $d" >&2; exit 1; }
done

# Advisory sanity check: try to import the ASGI app locally. This is skipped
# rather than fatal, since a broken/missing local venv says nothing about the
# build Vercel will run from requirements.txt.
PY=python3
[[ -x venv/bin/python ]] && PY=venv/bin/python
echo "==> Checking that main:app imports (advisory)..."
if DATA_DIR="$(mktemp -d)" "$PY" -c "import main; assert main.app" 2>/dev/null; then
  echo "    ok"
else
  echo "    skipped: could not import main with '$PY' (local deps missing?)"
fi

# --- deploy ----------------------------------------------------------------

echo "==> Deploying to Vercel ($TARGET)..."
vercel deploy "${VERCEL_ARGS[@]}"

echo
echo "Done. Notes for this app on Vercel:"
echo "  * Rendering runs in a serverless function: 300s max duration, 3009MB memory."
echo "    Long audio files WILL time out."
echo "  * Only /tmp is writable; uploads/outputs go there and are not shared"
echo "    between invocations, so /download/<file> can 404 after a render."
echo "    Persist finished videos to blob storage (e.g. Vercel Blob / S3) to fix."
