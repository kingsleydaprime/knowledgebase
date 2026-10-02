#!/bin/sh
# The fixed service is race-free; the buggy one must be caught by the race detector.
set -eu
export LC_ALL=C
out=$(mktemp)
trap 'rm -f "$out"' EXIT
go test -race -run TestServiceTakesTheUserAsAnArgument -count=1 . >/dev/null
echo "ok: the fixed service passes under -race"
if go test -race -run TestBuggyServiceRaces -count=1 . >"$out" 2>&1; then
  echo "FAIL: the race detector missed the shared CurrentUser field"; exit 1
fi
grep -q "WARNING: DATA RACE" "$out" || { echo "failed, but not with a data race:"; cat "$out"; exit 1; }
echo "ok: the race detector caught the per-request field on a shared service"
