# Build Your Own Shell

**[Intermediate]** — The best small project on this list. A few hundred lines gets you a working shell, and it teaches the process model better than any amount of reading.

## What you're building

An interactive shell: read a line, parse it, run the command, repeat. By the end it will handle redirection, pipelines, background jobs, and the builtins that can't be external programs.

**What you're deliberately not building:** a full POSIX shell (the grammar is large, and quoting rules alone are a project), scripting features (functions, arrays, arithmetic expansion), or line editing from scratch (use readline — writing a line editor is a different project).

**Why this one:** it's the smallest build here that produces something you can genuinely use, and it makes `fork`/`exec`, file descriptors, pipes and signals concrete in a way nothing else does. If you've ever wondered why `cd` can't be an external program, you'll know by milestone 6.

## What you need first

| You should know | Where |
|---|---|
| **Processes** — `fork`, `exec`, `wait`, and zombies | [[foundations/os/02-processes-and-threads\|os/02]] — **the core prerequisite** |
| **File descriptors** — what 0, 1, 2 are, and `dup2` | [[foundations/os/01-what-an-os-is\|os/01]] |
| **Pipes and signals** | [[foundations/os/10-signals-and-ipc\|os/10]] |
| **Basic tokenising** | [[foundations/compilers/02-lexical-analysis\|compilers/02]] — light touch; the grammar is tiny |

You **don't** need: parsing theory beyond splitting on whitespace, networking, or threads.

**This is a Unix project.** The `fork`/`exec` model doesn't exist on Windows — use WSL or a Linux VM.

## The build order

### 1. The read-eval loop

Print a prompt, read a line, echo it back, loop. Exit on EOF (Ctrl-D).

```
$ hello
you typed: hello
$ ^D
```

**Test:** it prompts, echoes, and exits cleanly on Ctrl-D.

**Watch for:** handle EOF (a null return from your read function), not just an empty line — otherwise Ctrl-D spins forever.

### 2. Tokenise

Split the line into words on whitespace. `ls -l /tmp` → `["ls", "-l", "/tmp"]`.

**Test:** print the token vector for various inputs, including multiple spaces and leading/trailing whitespace.

**Watch for:** you'll want quoting later (`echo "hello world"` is two tokens, not three). Note where it goes and move on — quoting properly is a surprising amount of work and it isn't the interesting part yet.

### 3. `fork` and `exec` — run a command

**The milestone that matters.**

```c
pid_t pid = fork();
if (pid == 0) {
    execvp(argv[0], argv);          // become the new program
    perror("execvp");                // only reached if exec FAILED
    _exit(127);
} else if (pid > 0) {
    int status;
    waitpid(pid, &status, 0);        // parent waits
}
```

**Test:** `ls`, `echo hello`, `/bin/date`, and a nonexistent command (should report an error, not crash).

**Watch for:**

- **After a successful `exec`, nothing below it runs** — the process image is replaced. Code after `execvp` is the failure path only
- **`_exit`, not `exit`, in the child** after a failed exec — `exit` flushes stdio buffers the child inherited, which duplicates output
- **`execvp` searches `$PATH`; `execv` doesn't.** Use `execvp` unless you're implementing PATH lookup yourself (which is a worthwhile exercise)
- **Reap your children**, or you accumulate zombies → [[foundations/os/02-processes-and-threads|Processes and Threads]]

### 4. Exit status

Capture the child's exit code and expose it as `$?`.

```c
if (WIFEXITED(status))        code = WEXITSTATUS(status);
else if (WIFSIGNALED(status)) code = 128 + WTERMSIG(status);
```

**Test:** `false` then `echo $?` → 1. `true` → 0.

**Watch for:** `status` from `waitpid` is **not** the exit code — it's a packed value needing the `W*` macros. This trips everyone once. The `128 + signal` convention is why a segfaulting program reports 139.

### 5. Redirection

```bash
ls > out.txt
wc -l < in.txt
cmd 2> err.txt
cmd >> append.txt
```

In the child, **after `fork` but before `exec`**:

```c
int fd = open("out.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
dup2(fd, STDOUT_FILENO);         // fd 1 now refers to the file
close(fd);
execvp(...);
```

**Test:** `ls > out.txt` creates the file with the listing. `cat < out.txt` reads it.

**Watch for:** **this is why `fork` and `exec` are separate calls** — the child rearranges its own descriptors before becoming the new program, and the program being run needs no cooperation. That design elegance is the lesson of this milestone.

`dup2` closes its target first if it's open. Close the original `fd` after duplicating, or you leak it. Redirection tokens must be removed from `argv` before `exec`.

### 6. Builtins

Some commands **cannot** be external programs:

```
cd      — must change THIS process's directory; a child's chdir dies with it
exit    — must exit this process
export  — must modify this process's environment
pwd, echo  — could be external, usually builtin for speed
```

**Test:** `cd /tmp` then `pwd` shows `/tmp`. Confirm that `/usr/bin/cd` either doesn't exist or does nothing useful.

**Watch for:** **check for builtins before forking.** This is the milestone that answers "why is `cd` special?" — a forked child that calls `chdir` changes its own directory and then exits, leaving the shell exactly where it was.

### 7. Pipelines

```bash
ls | grep .txt | wc -l
```

For each pipe, create one, fork, and wire the ends:

```c
int fd[2];
pipe(fd);

if (fork() == 0) {                    // left side
    dup2(fd[1], STDOUT_FILENO);
    close(fd[0]); close(fd[1]);
    execvp(...);
}
if (fork() == 0) {                    // right side
    dup2(fd[0], STDIN_FILENO);
    close(fd[0]); close(fd[1]);
    execvp(...);
}
close(fd[0]); close(fd[1]);           // THE PARENT MUST CLOSE BOTH
wait for both children
```

**Test:** `ls | wc -l`, then a three-stage pipeline. Compare output with the real shell's.

**Watch for — this is the hardest milestone:**

> **The parent must close both ends of every pipe.** `wc` sees EOF only when *every* write end is closed, including the parent's copy. Forget it and your pipeline hangs forever with no error.

Every child must also close the descriptors it isn't using. For N stages you need N−1 pipes, and each child closes all pipe fds except its own two. Getting the bookkeeping right is fiddly, and generalising from two stages to N is where the real learning is.

### 8. Background jobs and signals

```bash
sleep 10 &
jobs
fg %1
```

Background: don't `waitpid` immediately. Track the PID in a job table, and reap asynchronously via `SIGCHLD` or `waitpid(-1, &st, WNOHANG)`.

**Test:** `sleep 5 &` returns immediately; `jobs` lists it; it reports completion.

**Watch for:**

- **Ctrl-C must kill the foreground job, not your shell.** The shell ignores `SIGINT`; the child gets the default handler restored after `fork`
- **Process groups.** Each job gets its own group (`setpgid`), and the terminal's foreground group is set with `tcsetpgrp` — that's what makes Ctrl-C reach the right processes
- **Reap in the handler carefully** — only async-signal-safe functions → [[foundations/os/10-signals-and-ipc|Signals]]

Job control is genuinely the hardest part of a shell and the least essential. **Background jobs are worth doing; full `fg`/`bg`/Ctrl-Z is optional.**

### 9. Extras, in order of value

**Quoting** — `"hello world"` as one token, `'no $expansion'`, backslash escapes. More work than it looks.

**Variable expansion** — `$HOME`, `$?`, `$1`. Needs an environment table and expansion before tokenising (or during).

**Globbing** — `*.txt`. `glob()` in C, or your language's equivalent. Note the shell expands it, **not** the program — which is why `ls *.txt` sees a list of filenames.

**Line editing and history** — use **readline** or **linenoise**. Writing a line editor means raw terminal mode, escape sequences, and cursor management: a separate project.

**`&&`, `||`, `;`** — command sequencing based on exit status.

## Per-language toolkit

| Milestone | C | C++ | Rust | Go | Python | JS/Node |
|---|---|---|---|---|---|---|
| **Read line** | `getline`, **readline** | same | `rustyline` | `bufio.Scanner` | `input()`, `readline` | `readline` |
| **Tokenise** | by hand | `std::istringstream` | `split_whitespace` | `strings.Fields` | `shlex` (handles quoting!) | by hand |
| **fork/exec** | `fork`+`execvp` | same | `Command` or `nix` crate | `os/exec` (**no raw fork**) | `os.fork`, `subprocess` | `child_process` |
| **Redirection** | `dup2` | `dup2` | `Stdio::from(file)` | `cmd.Stdout = file` | `subprocess` stdout= | `stdio` option |
| **Pipes** | `pipe` | `pipe` | `Stdio::piped()` | `cmd.StdoutPipe()` | `subprocess.PIPE` | `stdio: 'pipe'` |
| **Signals** | `sigaction` | same | `signal-hook` | `os/signal` | `signal` | `process.on` |

**The important caveat: high-level languages hide the lesson.**

Rust's `Command`, Go's `exec.Command`, and Python's `subprocess` all wrap `fork`/`exec`/`dup2` behind a builder API. You'll get a working shell faster and learn much less — the whole point of milestones 3, 5 and 7 is doing the wiring yourself.

**Recommendation by goal:**

- **To learn the process model: C.** It's the language the API was designed for, and every call maps directly
- **Rust with the `nix` crate** gives you raw `fork`/`execvp`/`dup2`/`pipe` with safer types — a good middle path
- **Go deliberately makes raw `fork` unsafe** (its runtime has threads, and `fork` in a threaded program is treacherous), so `os/exec` is the only sane route. Fine for a shell, poor for learning the syscalls
- **Python** with `os.fork`/`os.execvp`/`os.dup2` — the raw calls are all exposed, so you can do it properly with far less ceremony than C. **The best compromise** if C feels like too much

## The parts that will bite you

**Not closing pipe ends in the parent.** Your pipeline hangs with no error, no output, and no clue. This is the number-one shell bug.

**`exec` doesn't return.** Code after it is the error path.

**`waitpid`'s status is packed.** Use `WIFEXITED`/`WEXITSTATUS`.

**Zombies.** Reap every child, including background ones.

**Builtins must not fork.** `cd` in a child is a no-op from the shell's perspective.

**Signal handlers reset across `exec` but are inherited across `fork`.** A child that inherited "ignore SIGINT" from your shell can't be Ctrl-C'd — restore defaults in the child before `exec`.

**Buffered output duplicating after `fork`.** The child inherits the parent's stdio buffer; if it exits with `exit()` rather than `_exit()`, buffered content is flushed twice. `fflush` before forking, or use `_exit`.

**Argument arrays must be NULL-terminated** in C. Forgetting is a segfault inside `execvp`.

## How to know it works

```bash
$ echo hello                 # basic exec
$ ls -la /tmp                # arguments
$ nosuchcommand              # error, no crash
$ false; echo $?             # → 1
$ ls > out.txt; cat out.txt  # redirection
$ ls | wc -l                 # pipeline
$ ls | grep . | wc -l        # three stages
$ cd /tmp; pwd               # builtin
$ sleep 3 &                  # background
$ jobs
$ ^C                         # kills the child, NOT the shell
$ ^D                         # exits cleanly
```

**Compare against `bash` for every case** — same input, same output and exit code.

**Check for leaks** while it runs:

```bash
ls -l /proc/$(pgrep myshell)/fd     # descriptor count should be STABLE
ps aux | awk '$8 ~ /^Z/'            # no zombies accumulating
```

A file-descriptor count that grows with each command means you're leaking pipe ends — a common and otherwise invisible bug.

**Run it as your actual shell for an hour.** Nothing surfaces missing features faster.

## Where to stop

**Stop after pipelines (milestone 7), or after background jobs if you want the satisfaction.** You'll have learned:

- Why `fork` and `exec` are two calls, and what the gap between them is for
- What a file descriptor is, and that redirection is just renumbering them
- Why `cd` can't be a program
- How pipes create backpressure, and why closing ends matters
- What process groups and controlling terminals are for
- Why `$?` is 139 when something segfaults

**Real shells additionally have:** a full grammar (POSIX shell is genuinely complex), functions, arrays, arithmetic and parameter expansion, here-documents, subshells and command substitution, complete job control, programmable completion, and decades of compatibility handling.

**If you want to go further:** add **command substitution** (`$(...)` — it's a pipe plus a recursive shell invocation, and it's satisfying), or **implement `$PATH` lookup yourself** with `execv` instead of `execvp`. Both are small and illuminating.

This pairs naturally with [[build-your-own-shit/01-http-server|the HTTP server]] — same process and descriptor machinery, different problem — and it's the best preparation for **writing an OS** (guide 05, planned), where you implement the other side of these calls.

---

## Related
- [[foundations/os/02-processes-and-threads|Processes and Threads]] — `fork`/`exec`, the core prerequisite
- [[foundations/os/10-signals-and-ipc|Signals and IPC]] — pipes, `dup2`, signal handling
- [[devops/01-linux/12-bash-scripting|Bash Scripting]] — the thing you're reimplementing
- [[devops/01-linux/06-process-management|Linux: Process Management]] — jobs and signals from the user side
- [[build-your-own-shit/README|build-your-own-shit]]
