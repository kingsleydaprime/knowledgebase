#!/bin/sh
# Without the Mutex, the shared field can't be written from two threads at all: rustc refuses.
set -eu
export LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
mkdir -p "$work/src"
cp Cargo.toml "$work/"
cat > "$work/src/lib.rs" <<'RS'
pub struct BuggyService {
    pub current_user: String,
}

pub fn handle_two_requests(service: &BuggyService) {
    std::thread::scope(|s| {
        s.spawn(|| service.current_user = "ada".to_string());
        s.spawn(|| service.current_user = "bayo".to_string());
    });
}
RS
if (cd "$work" && cargo build --quiet 2>"$work/err.txt"); then
  echo "FAIL: a shared field was written from two threads without a lock, and it compiled"; exit 1
fi
grep -q "error\[E0524\]: two closures require unique access to \`\*service\` at the same time" "$work/err.txt" \
  || { echo "failed, but not with E0524:"; cat "$work/err.txt"; exit 1; }
echo "ok: rustc refused the unsynchronised shared write"
