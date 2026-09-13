# Delete a snippet

[Setup](README.md#setup), then preview using the snippet name without `.mdx`:

```bash
npm run snippets:delete -- splice SNIPPET_NAME --dry-run
```

If references remain, the command lists their files and line numbers. Remove or
replace those imports and component usages, then run again without `--dry-run`.

This deletes the manifest entry, generated snippet, and source record. Commit
those changes with your page edits. The original source file is untouched.
