# Shell Completions

`ext-tool` ships completion scripts for bash, zsh, and fish.

---

## Bash

Install permanently:

```bash
ext completions bash > ~/.local/share/bash-completion/completions/ext
```

Or activate for the current session only:

```bash
source <(ext completions bash)
```

---

## Zsh

```bash
mkdir -p ~/.zsh/completions
ext completions zsh > ~/.zsh/completions/_ext
```

Add the completions directory to your `fpath` in `~/.zshrc` if it isn't there already:

```zsh
fpath=(~/.zsh/completions $fpath)
autoload -Uz compinit && compinit
```

Restart your shell or run `exec zsh`.

---

## Fish

```bash
ext completions fish > ~/.config/fish/completions/ext.fish
```

Fish picks up completions from that directory automatically. No further config needed.

---

## Show install instructions

Each shell subcommand also accepts `--show-install` to print the instructions above
without emitting the script:

```bash
ext completions zsh --show-install
```
