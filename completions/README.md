# EOS Shell Completion

The EOS provides dynamic completion for Bash, Zsh, and Fish. Candidate IDs are read from the live repository registries, so newly created PI/WC/WP, change, maintenance, release, and artifact IDs appear automatically.

## Install

```bash
./scripts/eos completion install
```

The shell is inferred from `$SHELL`, or choose it explicitly:

```bash
./scripts/eos completion install bash
./scripts/eos completion install zsh
./scripts/eos completion install fish
./scripts/eos completion install all
```
