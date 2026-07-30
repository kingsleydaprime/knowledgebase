# Accessing the Command Line

> RHCSA V10

Part of [[README|RHCSA V10]]. Leads into [[devops/01-linux/02-navigating-file-system|Navigating the Filesystem]] for the commands themselves.

---

## The ways in

| Method | When you'd use it |
|---|---|
| GUI terminal emulator | Desktop install, working locally |
| Virtual console (tty) | No GUI, physically at the machine, or GUI crashed |
| SSH | Remote administration — the normal way you touch a real server |

### Virtual consoles

RHEL (like most Linux) gives you multiple independent text login sessions on one physical machine, switchable with **Ctrl+Alt+F1** through **F6**. On a desktop install, one of these (usually F1 or a dedicated one) is running the graphical session; the rest are plain `login:` prompts.

```bash
Ctrl+Alt+F2    # switch to tty2 — independent login, independent shell session
Ctrl+Alt+F1    # back to the GUI (if that's where it lives)
```
Each tty is a fully separate session — logging out of tty2 doesn't touch what's running on tty3. Useful when a GUI session hangs and you need a way in that doesn't depend on it.

### SSH

The real answer for servers, which usually have no GUI and no physical access at all. Full setup and hardening is already covered in [[devops/01-linux/14-basic-ssh-config|Basic SSH Config]] — this section is just about *why* it's the primary access method: the machine could be in a data center you'll never physically visit.

---

## Reading the prompt

```
[kingsley@rhel-server ~]$
[root@rhel-server ~]#
```

| Part | Meaning |
|---|---|
| `kingsley@rhel-server` | user@hostname |
| `~` | current directory (`~` = home) |
| `$` | regular user prompt |
| `#` | **root** prompt — the single most important character to notice before running anything destructive |

That `$` vs `#` distinction is worth internalizing as a reflex — a `#` prompt means every command runs with full system privileges, no confirmation, no undo.

---

## Command syntax

```
command [options] [arguments]
```

```bash
ls -la /etc          # command: ls, options: -l -a combined, argument: /etc
ls -l -a /etc         # same thing, options split out
ls --all --long /etc  # same thing, long-form options
```

Short options (`-x`) can usually be combined (`-la` = `-l -a`); long options (`--all`) generally can't be combined and take `--option=value` or `--option value` for arguments.

---

## Bash shortcuts worth having as muscle memory

| Shortcut | Effect |
|---|---|
| `Tab` | Auto-complete command/path — press twice to list all possibilities |
| `Ctrl+R` | Reverse search command history — start typing, it finds the last matching command |
| `Ctrl+A` | Jump to start of line |
| `Ctrl+E` | Jump to end of line |
| `Ctrl+U` | Delete from cursor to start of line |
| `Ctrl+K` | Delete from cursor to end of line |
| `Ctrl+W` | Delete the word before the cursor |
| `Ctrl+C` | Kill the currently running foreground command |
| `Ctrl+D` | Send **EOF (End Of File)** — a signal meaning "no more input is coming." On an empty command line this closes the shell (same as typing `exit`); fed to a program reading from stdin, it tells that program the input stream has ended |
| `Ctrl+Z` | Suspend the current process to the background — see [[devops/01-linux/06-process-management|Process Management]] |
| `!!` | Re-run the last command |
| `!n` | Re-run history entry number `n` (see it with `history`) |
| `sudo !!` | Extremely common combo — re-run the last command with sudo after forgetting it |

Reverse search (`Ctrl+R`) is worth trying hands-on once rather than just reading about it — press `Ctrl+R`, start typing part of a command you ran earlier (say `syst`), and the prompt itself changes to show what it found:
```
(reverse-i-search)`syst': systemctl status sshd
```
Press `Ctrl+R` again to cycle to the next older match, `Enter` to run it as-is, or any arrow key to drop the found command onto the normal prompt for editing first.

---

## Redirecting input and output

Every process starts with three numbered channels, called **file descriptors** — this is worth knowing by number, not just by name, since redirection syntax refers to them numerically:

| # | Name | Default connection | Direction |
|---|---|---|---|
| 0 | stdin (standard input) | Keyboard | Read |
| 1 | stdout (standard output) | Terminal | Write |
| 2 | stderr (standard error) | Terminal | Write |

Redirection changes where a channel reads from or writes to — a file instead of the keyboard/terminal, or `/dev/null` to discard it entirely.

| Operator | Effect |
|---|---|
| `> file` | stdout **overwrites** file |
| `>> file` | stdout **appends** to file |
| `2> file` | stderr overwrites file |
| `2> /dev/null` | discard stderr entirely |
| `> file 2>&1` or `&> file` | stdout AND stderr, overwrite, to the same file |
| `>> file 2>&1` or `&>> file` | stdout AND stderr, append, to the same file |

```bash
find /etc > results.txt 2> errors.txt      # split: normal output here, permission-denied noise there
find /etc -name passwd > out.txt 2> /dev/null   # keep the result, throw away the "permission denied" clutter
```

**Order matters** with `2>&1` — it means "point this channel at wherever the other one currently goes," evaluated left to right at that moment, not "link them together permanently":
```bash
command > output.log 2>&1     # stdout → file, THEN stderr → same place stdout now points (the file). Both end up in output.log — correct.
command 2>&1 > output.log     # stderr → wherever stdout currently is (the terminal), THEN stdout → file. stderr still prints to the terminal — probably not what you wanted.
```
This is exactly why the merged forms `&>` / `&>>` exist — they sidestep the ordering gotcha entirely by doing both in one step (though some non-Bash shells don't support them, so scripts aiming for portability still use the two-step `2>&1` form).

### Pipelines — chaining commands instead of files

A pipe (`|`) connects one command's stdout directly to the next command's stdin, without an intermediate file:

```bash
ls -l /usr/bin | less              # page through long output
ls | wc -l                          # count how many files ls listed
ls -t | head -n 10 > recent.txt     # 10 most-recently-modified files, saved to a file
```

**Redirection inside a pipeline redirects to a file instead of passing along the pipe** — `ls > out.txt | less` sends everything to `out.txt` and `less` receives nothing. When you need output to go both to a file *and* onward through the pipeline, use `tee` (named for a plumbing T-joint — it splits the stream in two):

```bash
ls -l | tee saved.txt | less        # saved to a file AND still displayed, in the same command
ls -l | tee -a saved.txt             # -a appends instead of overwriting
```

---

## Login shell vs. non-login shell

This distinction shows up on the exam indirectly whenever a variable or `$PATH` change "doesn't stick." Bash reads different startup files depending on how the shell was invoked:

| Shell type | Reads | When it happens |
|---|---|---|
| Login shell | `/etc/profile`, then `~/.bash_profile` | SSH login, virtual console login |
| Non-login interactive shell | `~/.bashrc` | Opening a new terminal tab/window on top of an existing session |

`~/.bash_profile` on RHEL typically sources `~/.bashrc` itself, so in practice both end up loaded on login — but if you ever add something to the wrong file and it "works in one terminal but not another," this is why. `$PATH` and environment variables in general get their own deeper note: [[devops/01-linux/10-environment-variables|Environment Variables]].
