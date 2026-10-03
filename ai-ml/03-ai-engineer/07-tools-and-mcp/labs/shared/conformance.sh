#!/bin/sh
# Checks a language's MCP server with the official TypeScript client: sh ../shared/conformance.sh <command> [args...]
# Run from a language's lab folder. Installs the client into ../typescript on first use.
set -eu
here=$(cd "$(dirname "$0")/../typescript" && pwd)
[ -d "$here/node_modules" ] || (cd "$here" && npm ci --silent)
exec node "$here/conformance.ts" "$@"
