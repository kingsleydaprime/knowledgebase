## Environment Variables

Variables that are available system-wide to any process, not just your current shell session.

---

### Viewing them

```bash
env                    # all environment variables
printenv               # same thing
printenv HOME          # specific variable
echo $HOME             # access one directly
```

---

### Setting them

```bash
# temporary — only exists in current terminal session
export MY_VAR="hello"
echo $MY_VAR

# open a new terminal and try echo $MY_VAR — it's gone
```

To make it permanent add it to your shell config:

```bash
nano ~/.zshrc           # since you use zsh
```

Add at the bottom:
```bash
export MY_VAR="hello"
export PATH="$PATH:/some/new/path"
```

Then reload:
```bash
source ~/.zshrc
```

---

### .env files

Projects store environment variables in a `.env` file:

```bash
nano .env
```

```bash
DATABASE_URL=postgresql://localhost:5432/mydb
REDIS_URL=redis://localhost:6379
API_KEY=supersecretkey
PORT=3000
```

Load it into your current shell:
```bash
source .env
echo $DATABASE_URL
```

**Always add `.env` to `.gitignore`:**
```bash
echo ".env" >> .gitignore
```

---

### Important built-in variables

| Variable | Meaning |
|---|---|
| `$HOME` | your home directory |
| `$USER` | current username |
| `$PATH` | directories searched for commands |
| `$SHELL` | your current shell |
| `$PWD` | current directory |
| `$EDITOR` | default text editor |
| `$LANG` | system language |

---

Run these:

```bash
echo $PATH
echo $SHELL
echo $USER
export TEST_VAR="spectroniq"
echo $TEST_VAR
unset TEST_VAR
echo $TEST_VAR
```

Tell me what you get.

```zsh
> echo $PATH
echo $SHELL
echo $USER
export TEST_VAR="spectroniq"
echo $TEST_VAR
unset TEST_VAR
echo $TEST_VAR

/home/kijuchihe/.local/bin:/home/kijuchihe/.local/share/pnpm:/home/linuxbrew/.linuxbrew/bin:/home/kijuchihe/.bun/bin:/home/kijuchihe/.nvm/versions/node/v22.14.0/bin:/home/kijuchihe/.nvm/versions/node/v22.14.0/bin:/home/kijuchihe/.cargo/bin:/home/kijuchihe/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/snap/bin
/usr/bin/zsh
kijuchihe
spectroniq
```

All working. A few things your `$PATH` reveals about your setup:

- `pnpm` — you use pnpm as your Node package manager
- `linuxbrew` — you have Homebrew on Linux installed
- `bun` — you have Bun runtime installed
- `nvm` — Node version manager (node v22.14.0 currently active)
- `cargo` — you have Rust installed

That's a serious dev setup.

Notice the last `echo $TEST_VAR` printed nothing — `unset` wiped it. That's correct.

---

