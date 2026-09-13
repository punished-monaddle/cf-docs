# Snippets

## Setup

Install [Nix](https://nixos.org/download/) and [direnv](https://direnv.net/),
and [enable direnv’s shell hook](https://direnv.net/docs/hook.html). From the repository root:

```bash
direnv allow
```

The checked-in `.envrc` loads Nix automatically, providing Python, Node.js, npm,
and Git. No manual `nix-shell` step is needed.

## Commands

- [Add a snippet](add.md)
- [Move or edit a snippet](move.md)
- [Delete a snippet](delete.md)
- [Refresh snippets from upstream](../../config/snippet-config/update-workflows.md#local-one-command-extraction)

For authoring, use a local source checkout at a fetched or pushed branch tip.
Source files must be tracked, unchanged, and free of symlinks.

Add `--dry-run` to preview changes. Run any command with `--help` for all options.
