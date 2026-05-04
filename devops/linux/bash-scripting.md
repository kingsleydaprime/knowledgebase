## Shell Scripting

A shell script is just a file containing commands you'd normally type in the terminal — automated and reusable.

---

### Your first script

```bash
touch hello.sh
nano hello.sh
```

Type this inside:

```bash
#!/bin/bash

echo "Hello, Kingsley"
echo "Today is: $(date)"
echo "You are logged in as: $(whoami)"
echo "Current directory: $(pwd)"
```

Save and exit nano (`Ctrl+X` → `Y` → `Enter`), then:

```bash
chmod +x hello.sh
./hello.sh
```

---

### The shebang `#!/bin/bash`

That first line tells the OS which interpreter to use to run the script. Without it, the OS doesn't know what to do with the file.

| Shebang | Meaning |
|---|---|
| `#!/bin/bash` | run with bash |
| `#!/usr/bin/env python3` | run with python3 |
| `#!/usr/bin/env node` | run with node |

---

### `$()` — command substitution

```bash
echo "Today is: $(date)"
```

`$()` runs a command and inserts its output inline. So `$(date)` gets replaced with the actual date output.

---

```bash
> touch hello.sh
> chmod +x hello.sh
> nano hello.sh
> hello.sh
zsh: command not found: hello.sh
> ./hello.sh
Hello, Kingsley
Today is: Mon 04 May 2026 20:18:27 GMT
You are logged in as: kijuchihe
Current directory: /home/kijuchihe

```

Perfect. Everything worked.

One thing to note — you ran `hello.sh` without `./` first and got "command not found". That's intentional Linux behavior.

When you type a command, the shell only looks in directories listed in your `PATH` environment variable. Your current directory is not in `PATH` by default — for security reasons. So you must explicitly say "run this from here" with `./`.

---

Check your PATH:
```bash
echo $PATH
```

You'll see a list of directories separated by `:`. Those are the only places the shell looks for commands automatically.

---

Now let's make the script actually do something useful. Variables, conditionals, loops — ready?


## Variables

```bash
#!/bin/bash

name="Kingsley"
age=21
greeting="Hello, $name. You are $age years old."

echo $greeting
echo "Name is: $name"
echo "In 10 years you'll be: $((age + 10))"
```

Rules:
- No spaces around `=`
- Access variable with `$`
- Math goes inside `$(())`

---

## Conditionals

```bash
#!/bin/bash

age=21

if [ $age -ge 18 ]; then
    echo "You are an adult"
elif [ $age -ge 13 ]; then
    echo "You are a teenager"
else
    echo "You are a child"
fi
```

### Comparison operators

| Operator | Meaning |
|---|---|
| `-eq` | equal to |
| `-ne` | not equal |
| `-gt` | greater than |
| `-lt` | less than |
| `-ge` | greater than or equal |
| `-le` | less than or equal |
| `=` | string equal |
| `!=` | string not equal |

---

## Loops

```bash
#!/bin/bash

# for loop
for i in 1 2 3 4 5; do
    echo "Number: $i"
done

# while loop
count=1
while [ $count -le 5 ]; do
    echo "Count: $count"
    count=$((count + 1))
done
```
