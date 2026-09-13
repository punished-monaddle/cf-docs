# Move or edit a snippet

[Setup](README.md#setup). Use the existing snippet name without `.mdx`.

After moving and pushing the source file, update its path:

```bash
npm run snippets:move -- splice SNIPPET_NAME \
  --source-dir ../splice --source apps/renamed-example.yaml
```

To change its marker region at the current path:

```bash
npm run snippets:edit -- splice SNIPPET_NAME \
  --source-dir ../splice --marker NEW_REGION
```

Use `--full-file` for the whole file, or `--language` to change its language.
Move keeps the existing selector and language unless you override them.

Both commands preserve the snippet name and page imports. Commit the generated changes.
