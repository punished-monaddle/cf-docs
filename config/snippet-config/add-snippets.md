# Add an external snippet

Run `snippets:add` from the cf-docs repository to register an external source file
and generate its initial MDX snippet. The command writes to the `main` output
folder; it does not add an import to a documentation page automatically.

## Prerequisites

- Install Python 3.11 or later, Node.js, npm, and Git, or use this repository's
  `nix-shell` environment.
- Have a local checkout of the source repository. Run
  `npm run generate:external-snippets -- --list` to see supported repository keys.
- Use a tracked regular source file that is unchanged at `HEAD`. Symlinks in the
  source path, including directory symlinks inside the checkout, are rejected.
- Ensure the source checkout's `HEAD` is exactly at a remote-tracking ref. Fetch
  an existing remote commit or push a local commit before authoring. Merely
  having a remote configured is insufficient.

Examples below use an illustrative `apps/example.yaml` in a sibling Splice
checkout. Substitute a real path in your checkout. `--source` is relative to that
checkout, not to cf-docs. `--source-dir` can be omitted when the existing checkout
search finds a unique match.

## Select the source

A complete file is the default:

```bash
npm run snippets:add -- splice \
  --source-dir ../splice \
  --source apps/example.yaml
```

For a named region, put `SWEEP_START` and `SWEEP_END` on separate marker lines in
the source, commit and push them, then run:

```bash
npm run snippets:add -- splice \
  --source-dir ../splice \
  --source apps/example.yaml \
  --marker SWEEP
```

Each marker must occur exactly once, with the end after the start. The marker
lines are excluded. For another convention, use both `--start-marker` and
`--end-marker` instead of `--marker`. `--full-file` explicitly selects the whole
file. These selector forms are mutually exclusive; the command does not create
line-number, JSON-index, or regular-expression selectors.

Language is inferred from the source extension. Use `--language` when the
extension is unknown or the inferred language is unsuitable, for example
`--language hocon` for a `.conf` file.

## Preview and add the page import

Append `--dry-run` to either example to validate the source and see unified diffs
for all three proposed files without writing them:

```bash
npm run snippets:add -- splice \
  --source-dir ../splice \
  --source apps/example.yaml \
  --marker SWEEP \
  --dry-run
```

Run again without `--dry-run` to write the change. For this marker example, the
command derives `splice-literal-marker-apps-example-sweep-start` and prints:

```mdx
import ExternalSpliceMainSpliceLiteralMarkerAppsExampleSweepStart from '/snippets/external/splice/main/splice-literal-marker-apps-example-sweep-start.mdx';

<ExternalSpliceMainSpliceLiteralMarkerAppsExampleSweepStart />
```

Copy the import and component usage into the consuming page. Use `--name` only
when you need to override the derived stable name, for example to resolve a
collision between paths that normalize to the same name.

## Files changed and failure behavior

The command updates:

- `config/snippet-config/<repo>-snippet-list-remote.json`: source path, selector,
  language, and stable `snippetName`.
- `docs-main/snippets/external/<repo>/main/<snippetName>.mdx`: extracted content.
- `config/snippet-config/snippet-source-lock.json`: source commit, normalized
  remote URL, and remote-tracking ref, keyed by snippet name.

The source-lock record describes the revision used for this authoring operation.
It does not pin subsequent bulk generation or change the existing automation.
Review and commit these files together with the consuming page.

Missing, dirty, untracked, or symlinked sources, missing remote-tracking refs,
invalid markers, duplicate names or source/selector pairs, and orphaned output
files stop the command before it writes. An ordinary write failure triggers
rollback of the affected files. A dry run performs the same validation and
extraction as an actual add.

For the subsequent update workflow, see [external snippet updates](update-workflows.md).
