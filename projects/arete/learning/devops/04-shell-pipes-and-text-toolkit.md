# Arete DevOps — Shell Mastery: Pipes & the Text Toolkit

Split out from the original single-file `devops-learning.md`. See also `05-grep-in-depth.md`,
`06-find-in-depth.md`, and `08-sed-and-awk.md`.

---

## Part 4 — Shell Mastery: pipes, and the text toolkit

### The pipeline model — why the shell is powerful

Every command reads **stdin**, writes **stdout**, and errors to **stderr**. `|` connects stdout → stdin. Small tools compose into queries:

```bash
grep -rn "cache.del" src | wc -l        # how many cache-invalidation call sites?
#  produce lines            count them
```

Redirection:
```bash
cmd >  file      # stdout to file (overwrite)
cmd >> file      # append
cmd 2>&1         # merge stderr INTO stdout (so pipes/`tail` see errors too)
cmd 2>/dev/null  # discard errors
cmd1 && cmd2     # run cmd2 only if cmd1 succeeded (exit code 0)
cmd1 || cmd2     # run cmd2 only if cmd1 FAILED
cmd1 ;  cmd2     # run both regardless
```

You saw `2>&1 | tail -5` constantly in my commands — without `2>&1`, error output bypasses the pipe and you'd tail nothing useful when a command fails.

### cat, head, tail, wc, sort, uniq

```bash
cat file.ts                 # print whole file (concatenate)
head -30 file.ts            # first 30 lines
tail -12 file.ts            # last 12 lines
tail -f server.log          # follow live — THE log-watching command
wc -l file.ts               # line count
wc -l *.tsx                 # per-file + total (how I checked quests.tsx was 1173 lines)
sort | uniq -c | sort -rn   # the classic "frequency count" pipeline
```

Heredoc — feeding a multi-line file from the shell (used to write the verify script):

```bash
cat > verify.ts << 'EOF'
import { PrismaClient } from '@prisma/client';
...
EOF
# quoting 'EOF' prevents the shell from expanding $vars inside the block — almost always what you want for code
```

---

