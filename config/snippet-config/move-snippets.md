# Move or edit an external snippet

Use `snippets:move` when the source file has moved within the same source
repository. Use `snippets:edit` to change the selector or language at the existing
source path. Both preserve the stable `snippetName` and generated MDX path, so
consuming pages keep their existing imports.

These commands update the cf-docs manifest and generated output. They do not move
or edit files in the source checkout. Prepare, commit, and push source changes
first, following the [source prerequisites](add-snippets.md#prerequisites).
Tracked regular files are required; source paths containing symlinks are rejected.

## Move to a new source path

Find the existing `snippetName` in
`config/snippet-config/<repo>-snippet-list-remote.json` or the page's import.
Pass that name without the `.mdx` suffix. For example, after moving the source
file from `apps/example.yaml` to `apps/renamed-example.yaml` in Splice:

```bash
npm run snippets:move -- splice \
  splice-literal-marker-apps-example-sweep-start \
  --source-dir ../splice \
  --source apps/renamed-example.yaml \
  --dry-run
```

The example paths and name are illustrative; substitute the existing snippet
and new source path in your checkout. The old source file need not still exist.
Run again without `--dry-run` to apply the change.

Move keeps the existing selector and language unless you override them. If the
new file uses different markers, add `--marker NEW_REGION`, or both
`--start-marker` and `--end-marker`. If its language changes, pass `--language`
explicitly: moving from YAML to JSON does not automatically replace an existing
`yaml` language setting. This command moves the source path within one repository;
it does not rename the snippet or transfer it between repository manifests.

## Edit the selector or language

Edit requires at least one selector option or `--language`. For example, preview
switching the existing source from its old marker pair to a new one:

```bash
npm run snippets:edit -- splice \
  splice-literal-marker-apps-example-sweep-start \
  --source-dir ../splice \
  --marker NEW_REGION \
  --dry-run
```

Use `--full-file` to replace the selector with the entire source file. Marker
selection uses `--marker NAME` for `NAME_START`/`NAME_END`, or an exact start/end
pair. Each marker must appear exactly once and in order; marker lines are excluded.
A language-only edit preserves the selector, including an existing legacy line,
JSON-index, or regex selector. New selectors can only be full-file or markers.

## Review the changes

A dry run validates and extracts the source, then prints manifest, source-lock,
and generated-MDX diffs. Run without `--dry-run` to write those same changes.
Descriptions and unrelated formatting options are preserved. Both commands
refresh the source-lock record with the revision used for extraction; the record
does not pin later bulk generation.

Missing or ambiguous snippet names, invalid or dirty sources, symlinks, unavailable
remote-tracking refs, failed extraction, and duplicate source/selector pairs stop
the operation before writing. Review and commit the manifest, generated MDX, and
source-lock changes together. Confirm the content diff is expected; the printed
output path and all existing page imports should stay unchanged.

See [external snippet updates](update-workflows.md) for the subsequent refresh
workflow.
