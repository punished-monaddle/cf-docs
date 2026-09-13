# Snippets

## Setup

Install [Nix](https://nixos.org/download/), then run from the repository root:

```bash
nix-shell
```

The shell provides Python, Node.js, npm, and Git. No separate tool installs are needed.

## Commands

- [Add a snippet](add.md)
- [Move or edit a snippet](move.md)
- [Refresh snippets from upstream](../../config/snippet-config/update-workflows.md#local-one-command-extraction)

For authoring, use a local source checkout at a fetched or pushed branch tip.
Source files must be tracked, unchanged, and free of symlinks.

Add `--dry-run` to preview changes. Run any command with `--help` for all options.
