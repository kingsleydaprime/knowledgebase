#!/bin/sh
# Runs a command against a throwaway PostgreSQL cluster: created in a temporary folder, reachable through a Unix
# socket there and on a random port of 127.0.0.1 only, and deleted afterwards. Needs initdb and pg_ctl on PATH
# (PostgreSQL 16 or later). Usage: sh with-postgres.sh <command> [args...]
# The command sees PGHOST (the socket folder), PGPORT, PGUSER and PGDATABASE; clients that can't use a Unix
# socket (JDBC, a container) connect to 127.0.0.1:$PGPORT instead.
set -eu
dir=$(mktemp -d)
stop() {
    pg_ctl -D "$dir/data" -m immediate stop >/dev/null 2>&1 || true
    rm -rf "$dir"
}
trap stop EXIT
port=$((20000 + $(od -An -N2 -tu2 /dev/urandom) % 40000))
initdb -D "$dir/data" -U postgres -A trust -E UTF8 --no-sync >/dev/null
# Settings for repeatable plans, not for production: no autovacuum (statistics change only when the lab says so),
# no parallel query (no Gather nodes that vary with the machine), and no durability (fsync off: it's thrown away).
pg_ctl -D "$dir/data" -w -l "$dir/log" -o "-k $dir -p $port -c listen_addresses=127.0.0.1 -c autovacuum=off \
  -c max_parallel_workers_per_gather=0 -c fsync=off -c synchronous_commit=off -c full_page_writes=off" start >/dev/null
PGHOST=$dir PGPORT=$port PGUSER=postgres PGDATABASE=postgres "$@"
