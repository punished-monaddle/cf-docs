# Add a snippet

[Setup](README.md#setup), then run:

```bash
npm run snippets:add -- splice \
  --source-dir ../splice \
  --source apps/example.yaml
```

Replace the example with your source repository and file. This adds the whole file.
For a region between `SWEEP_START` and `SWEEP_END`, append `--marker SWEEP`.
Each marker must appear once; marker lines are excluded.

The command generates the snippet and prints an import and component. Paste both
into your docs page. Commit the page and generated changes together.

Use `--language` to override the inferred language, or `--name` to set the snippet name.
