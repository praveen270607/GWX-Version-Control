# GWX-Version-Control

A Git-like Version Control System for ICONICS GraphWorX displays (.gdfx) and Symbol Libraries.

## Project Goal

This project provides version control specifically for GraphWorX engineering files.

Instead of comparing raw XML files, it understands GraphWorX engineering concepts such as:

- Display Objects
- Object Properties
- Dynamics
- Commands
- Symbol Libraries

## Current local workflow

### Windows users without Python

Download the `GWX-Version-Control-v*-windows.zip` asset from the project's
GitHub Releases page, extract it, and run `gwx.exe`. The portable release does
not require Python, pip, Git, or a GitHub account. See
[`INSTALL-WINDOWS.txt`](INSTALL-WINDOWS.txt) in the ZIP for details.

### Python installation

Install the command in a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

Then use the `gwx` command from the project folder:

```powershell
gwx init
gwx add Displays\Pump.gdfx
gwx diff Displays\Pump.gdfx
gwx commit -m "Add pump display"
gwx branch alarm-viewer
gwx checkout alarm-viewer
gwx status
gwx log
```

`add` creates an immutable stored copy and records the revision on which the
change was based. `commit` rejects stale staged changes, so a later update
cannot silently overwrite a colleague's committed display. `checkout` restores
the selected branch's tracked files and refuses to overwrite local edits unless
`-f` is explicitly used.

### Commit IDs and file versions

Repository commits use one global sequence (`000001`, `000002`, and so on),
while each display or symbol has its own file version. For example, a display
first added in commit `000001` is file version `1`; a symbol first added later
in commit `000002` is also file version `1`. Updating only the display creates
its file version `2` without changing the symbol's file version. Use `gwx
status` to see each tracked file's version and last commit, and `gwx log` to
see the per-file version changes made by each commit.

```powershell
gwx checkout main
gwx merge alarm-viewer
```

Merges fast-forward when possible. If branches changed different files, they are
merged safely. If both branches changed the same display or symbol, `merge`
stops and asks for a manual resolution; compare the files, resolve in GraphWorX,
then `add` and `commit` the resolved file.

## Supported commands

- `gwx init`
- `gwx status`
- `gwx branch [name]`
- `gwx checkout [-f] <branch>`
- `gwx add <file>`
- `gwx diff <file.gdfx>`
- `gwx rm <file>`
- `gwx restore <file>`
- `gwx commit -m "message"`
- `gwx log`
- `gwx merge <branch>`

`python main.py` supports the same commands if the package has not been
installed yet.

## Roadmap

- Remote repositories, clone, push and pull
- Per-object semantic merge resolution
- Rename and move detection
- Ignore rules for generated GraphWorX metadata
- A desktop GUI

## Current Status

The local repository workflow and semantic `.gdfx` comparison are implemented.
Remote collaboration and per-object automatic conflict resolution are not yet
implemented.
