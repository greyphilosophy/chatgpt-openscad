#!/usr/bin/env bash
set -euo pipefail

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-3000}"
WORKSPACE="${OPENSCAD_WORKSPACE:-$PWD}"

export OPENSCAD_WORKSPACE="$WORKSPACE"

exec mcp-proxy \
  --host "$HOST" \
  --port "$PORT" \
  -- \
  openscad-mcp-server
