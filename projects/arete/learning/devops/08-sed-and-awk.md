# Arete DevOps — sed & awk (the Stream Editors)

Split out from the original single-file `devops-learning.md`. See also
`07-regex-from-zero-to-advanced.md`.

---

## Part 8 — sed & awk (the stream editors)

### sed — substitute, print, delete by line

```bash
# SUBSTITUTE
sed 's/foo/bar/' file          # first occurrence per line
sed 's/foo/bar/g' file         # every occurrence (g = global)
sed 's/foo/bar/gi' file        # + case-insensitive
sed -E 's/(user)_id/\1Id/g'    # ERE + backreference: user_id → userId
sed 's|/old/path|/new/path|g'  # any delimiter works — use | when the pattern has slashes

# IN-PLACE editing (writes the file):
sed -i 's/foo/bar/g' file      # GNU sed (Linux). macOS needs: sed -i '' 's/foo/bar/g'

# PRINT a line range (-n = quiet except explicit prints):
sed -n '325,345p' seed.ts      # ← used on the project to view seed.ts lines 325–345

# DELETE a line range in place:
sed -i '335,388d' seed.ts      # ← used to remove the legacy message block
                               #   (line numbers came from grep -n first!)
```

The two-step surgical pattern from this project is worth naming:
1. `grep -n "landmark" file` → get exact line numbers.
2. `sed -n 'A,Bp'` to **preview** the range, then `sed -i 'A,Bd'` to cut it.
Never delete by line number without previewing the range first.

### awk — columns and quick reports

awk splits each line into fields (`$1`, `$2`... on whitespace by default; `$0` = whole line).

```bash
awk '{print $1}' access.log                   # first column
awk -F: '{print $1}' /etc/passwd              # -F sets the delimiter
awk '$3 > 100 {print $1, $3}' data.txt        # filter rows by a numeric condition
awk '{sum += $2} END {print sum}' file        # sum a column
podman ps | awk 'NR>1 {print $NF}'            # NR>1 skips header, $NF = last field
```

Rule of thumb: **grep finds lines, sed edits lines, awk understands columns.** Reach for them in that order.

---

