# Delete an external snippet

Use `snippets:delete` to remove a snippet after its documentation references have
been removed or replaced. It removes the manifest entry, generated MDX under
`docs-main/snippets/external/<repo>/main/`, and any matching source-lock record.
It does not delete the original source file or outputs in other version folders.
A source checkout is not required.

## Preview a deletion

Find the stable `snippetName` in the repository's remote snippet manifest or in
a page import. Pass the name without the `.mdx` suffix. For example:

```bash
npm run snippets:delete -- splice \
  splice-literal-marker-apps-example-sweep-start \
  --dry-run
```

Substitute an existing name in your manifest. A successful preview prints unified
diffs for the manifest, source lock, and generated output, without writing files.
An older snippet need not already have a source-lock record to be deleted.

## Remove references first

If a reference remains, both the preview and actual deletion fail and print the
consumer's file path and line number. Update those pages or wrapper snippets:
remove the obsolete import and component usage, or replace them with another
snippet. Then run the preview again.

The reference check searches Markdown, MDX, JavaScript, TypeScript, JSX, TSX, and
JSON under `docs-main`. It recognizes the full snippet path and resolves quoted
root-relative and relative paths, with or without the `.mdx` extension. For
example, a wrapper importing `./example.mdx` or `../main/example` prevents deletion
of that file. Literal dynamic imports and re-exports are checked as well.

The scan is conservative: a path in a comment or code example can also prevent
deletion. It does not evaluate expressions that construct paths dynamically or
search outside `docs-main`. Review such consumers separately if your pages use
them; there is no force-delete flag that bypasses reference checking.

## Apply and verify

After the preview succeeds, run the same command without `--dry-run`:

```bash
npm run snippets:delete -- splice \
  splice-literal-marker-apps-example-sweep-start
```

The command requires exactly one matching manifest entry. It checks references
before writing, then removes the entry, generated file, and source-lock record.
An ordinary write failure triggers rollback of the affected files. A previously
missing generated file does not prevent removal of the stale manifest entry.

Review the deletion together with your page changes and run the documentation
validation used by the repository:

```bash
nix-shell --run 'cd docs-main && npx mint validate'
```

Commit the page edits, manifest, generated-file deletion, and source-lock changes
together. See [external snippet updates](update-workflows.md) for the surrounding
workflow, or [move and edit](move-snippets.md) if the snippet should be retained
with a new source.
