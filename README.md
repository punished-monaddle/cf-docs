# Canton Network Docs

This repo manages the contents of the [docs.canton.network](https://docs.canton.network) website.

Copyright (c) 2026 Canton Network. All rights reserved.
SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0


## Provide Feedback on a Docs Page

Every page on docs.canton.network has two feedback buttons in the footer:
- `Suggest edits`
- `Raise issue`

<img width="340" height="77" alt="image" src="https://github.com/user-attachments/assets/e143643a-484a-43a3-a4cb-b6ccda5f4fef" />

### Suggest edits:
Use this to propose a direct change to the page, fix a typo, update a code sample, improve wording, etc.

**How it works:**

- Click “Suggest edits” in the footer of any page.
- GitHub opens the source file for that exact page.
- Fork the repo, make your edits, and open a Pull Request.
- Canton docs team reviews and merges accepted changes if all checks out.

### Raise Issue:
Use this to report a problem or request new content without editing the source yourself.

**How it works:**

- Click “Raise Issue” in the footer of any page.
- A GitHub Issue opens *Pre-filled* with the Path of the page you were on.
- Describe in detail what's wrong or missing along with the source of information to verify and submit.
- The team reviews it and responds.


## Local Development

### Prerequisites

Install [Nix](https://nixos.org/download/). The repository’s `nix-shell` provides
the development tools and installs npm dependencies on first use.

### Authoring and generated content

Edit pages, navigation, and images in `docs-main/`, either directly or through
the Mintlify editor. Ordinary content has no separate source copy and is not
rewritten by documentation generation.

Network-dependent sections use templates in `docs-main/snippets/networkvars/`.
Edit those templates, then run `npm run generate:network-variable-tabs` to update
the marked `NETWORKVARS_START` / `NETWORKVARS_END` regions. Generation preserves
content outside those regions. Edit generated reference pages through their
owning generators, as before.

Run `npm run validate:network-variable-tabs` to check generated regions without
modifying files. Direct edits inside those regions fail validation; edit the
referenced template instead. Ordinary page edits and new images do not require
regeneration.

### Running the dev server

```bash
nix-shell
cd docs-main && mintlify dev
```

The site will be available at http://localhost:3000.

### Check for broken links

```bash
mintlify broken-links
```

## Snippets

See [Snippets](docs/snippets/README.md) for setup, authoring commands, and upstream refreshes.

## License

This repository uses a dual-license model:

- **Documentation prose** (`.mdx` files, text content): [Creative Commons Attribution 4.0 International (CC-BY-4.0)](https://creativecommons.org/licenses/by/4.0/) — see [LICENSE-DOCS](LICENSE-DOCS)
- **Code snippets and configuration** (embedded code examples, scripts, JSON config): [Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0) — see [LICENSE](LICENSE)
