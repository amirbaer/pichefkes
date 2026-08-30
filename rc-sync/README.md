# rc-sync

Keep rc files (`~/.bashrc`, `~/.tmux.conf`, `.alias`, …) working **even when
Google Drive isn't mounted**, while still syncing edits across machines.

## The problem it solves

These files used to be **symlinked into Google Drive**. If Drive wasn't mounted
yet at login (fresh boot, slow mount), the symlinks were broken, so bash and
tmux silently fell back to their defaults — wrong prompt, wrong tmux prefix, no
aliases.

## How it works

Each managed file is a **real local file** in `$HOME` (always readable). When
Drive is mounted, `rc-sync sync` reconciles each local file with its canonical
copy in `rc-files-hidden` using **newest-wins by mtime, both directions**.
`cp -p` preserves mtimes, so a settled pair copies nothing (no ping-pong). The
sync runs automatically at login via a hook in `~/.bash_profile` / `~/.zshrc`.

Managed files: `.alias .bashrc .git-completion.bash .inputrc .screenrc
.tmux.conf .vimrc` (edit `RC_FILES` in the script to change the set).

## Install

From a pichefkes checkout:

```bash
bash rc-sync/rc-sync.sh install
```

Or standalone from the public repo:

```bash
wget -qO /tmp/rc-sync.sh https://raw.githubusercontent.com/amirbaer/pichefkes/master/rc-sync/rc-sync.sh
bash /tmp/rc-sync.sh install
```

`install` migrates any existing Drive symlinks to local files, drops the script
at `~/.local/bin/rc-sync`, wires the login hook, and runs an initial sync.

## Commands

| Command             | What it does                                                        |
|---------------------|---------------------------------------------------------------------|
| `rc-sync sync`      | Reconcile local ↔ Drive now (default; safe, idempotent)             |
| `rc-sync install`   | Migrate symlinks → local, install to `~/.local/bin`, wire, sync     |
| `rc-sync status`    | Show each file's local/Drive mtime                                  |

## Editing the script

Edit here in pichefkes — this is the single source of truth. On a fresh
machine, `setup-new-computer.sh` runs it from a local pichefkes clone if
present, otherwise fetches it from the public repo.
