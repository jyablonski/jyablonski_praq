#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

compose=(docker compose -f docker-compose.yml)
log_dir="$(mktemp -d "${TMPDIR:-/tmp}/sql-proxy-poc.XXXXXX")"
keep_containers="${KEEP_CONTAINERS:-0}"

cleanup() {
  if [[ "$keep_containers" != "1" ]]; then
    "${compose[@]}" down --volumes --remove-orphans >/dev/null
  fi
  rm -rf "$log_dir"
}

trap cleanup EXIT INT TERM

run_client() {
  local service_name="$1"
  local log_name="$2"

  printf '\n=== %s logs ===\n' "$service_name"
  "${compose[@]}" run --build --rm --no-deps "$service_name" 2>&1 | tee "$log_dir/$log_name"
}

assert_log_contains() {
  local log_name="$1"
  local expected="$2"

  if ! grep -Fq "$expected" "$log_dir/$log_name"; then
    printf 'verification failed: %s is missing from %s\n' "$expected" "$log_name" >&2
    exit 1
  fi
}

printf 'Starting PostgreSQL and PgBouncer...\n'
"${compose[@]}" up -d --build postgres pgbouncer

run_client direct-client direct.log
run_client proxied-client proxied.log

printf '\n=== verification ===\n'
assert_log_contains direct.log '"connection_mode": "direct"'
assert_log_contains direct.log '"configured_target": "postgres:5432"'
assert_log_contains direct.log '"backend_port": 5432'
assert_log_contains proxied.log '"connection_mode": "via-proxy"'
assert_log_contains proxied.log '"configured_target": "pgbouncer:6432"'
assert_log_contains proxied.log '"backend_port": 5432'

printf 'Recorded checks in PostgreSQL:\n'
checks="$("${compose[@]}" exec -T postgres psql -U poc -d proxy_demo -At -F '|' -c \
  'SELECT service_name, connection_mode, configured_target, client_host, backend_port FROM connection_checks ORDER BY id;')"
printf '%s\n' "$checks"

direct_client_host="$(awk -F'|' '$1 == "direct-client" { print $4 }' <<<"$checks")"
proxied_client_host="$(awk -F'|' '$1 == "proxied-client" { print $4 }' <<<"$checks")"

grep -Eq '^direct-client\|direct\|postgres:5432\|[^|]+\|5432$' <<<"$checks" || {
  printf 'verification failed: direct-client did not record the expected path\n' >&2
  exit 1
}
grep -Eq '^proxied-client\|via-proxy\|pgbouncer:6432\|[^|]+\|5432$' <<<"$checks" || {
  printf 'verification failed: proxied-client did not record the expected path\n' >&2
  exit 1
}
if [[ -z "$direct_client_host" || -z "$proxied_client_host" || "$direct_client_host" == "$proxied_client_host" ]]; then
  printf 'verification failed: PostgreSQL saw the same client address for both paths\n' >&2
  exit 1
fi

printf '\nPASS: direct-client used postgres:5432; proxied-client used pgbouncer:6432; PostgreSQL saw different client addresses; both reached the backend on port 5432.\n'
if [[ "$keep_containers" == "1" ]]; then
  printf 'Containers left running because KEEP_CONTAINERS=1.\n'
fi
