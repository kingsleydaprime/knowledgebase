# 04 — Python project setup and shell

See also: [[01-research-basics]] · [[02-pose-estimation]] · [[03-preprocessing]] · general: [[devops/01-linux/index|linux]]

## uv

`uv` manages the Python version, the virtual environment (`.venv/`) and the dependencies.
`pyproject.toml` lists what you asked for, and `uv.lock` pins the exact versions installed, so
the same code gives the same results on another machine. That matters for a thesis
("results were produced with mediapipe X.Y").

- `uv sync`: make `.venv` match the lock file.
- `uv run python ...`: run inside that environment, with no manual `activate`.

## `src/` layout and `python -m`

The code lives in `src/sbfd/` (a package). `uv run python -m sbfd.extract` means "run the
module `sbfd.extract` as a script". `-m` finds it through the installed package rather than by
file path, so imports like `from sbfd import ...` work the same everywhere.

## Writing files safely: `.part` then rename

`extract.py` writes `name.npz.part` first, then `tmp.replace(out_path)`. A rename on the same
disk is **atomic**: it either happens completely or not at all. If the script crashes mid-write,
you're left with a `.part` file, never a half-written `.npz` that looks finished. That matters
because the script **skips files that already exist**. A corrupt file would be skipped forever.

## Commands used so far

```bash
find data/raw/urfd data/skeletons -maxdepth 3   # list files, at most 3 folders deep
printf '__pycache__/\nmentor.md\n' >> .gitignore  # append two lines (>> appends, > would overwrite)
```

```bash
mkdir -p docs/report/figures                      # -p: create parent folders too; no error if it exists
uv run python -c "import mediapipe, sys; print(sys.version.split()[0], mediapipe.__version__)"  # exact versions for the report
```

`find ... -maxdepth N` stops it from walking the whole tree. `printf` beats `echo` for this
because `\n` behaves the same in every shell.
