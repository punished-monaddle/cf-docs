from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import manage_external_snippets as author
from tests.snippet_authoring_helpers import write_manifest


def write_lock(path: Path, snippets: dict[str, dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"schemaVersion": 1, "snippets": snippets}, indent=2) + "\n",
        encoding="utf-8",
    )


def test_delete_dry_run_then_delete_removes_manifest_lock_and_output(
    authoring_fixture: tuple[Path, Path, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    root, manifest, _ = authoring_fixture
    name = "stable-example"
    entry = {
        "snippetName": name,
        "sourceRepo": "splice",
        "sourceFilepath": "example.py",
        "location": {"type": "fullFile"},
        "description": "",
        "options": {"language": "python"},
    }
    write_manifest(manifest, [entry])
    lock_path = root / "config" / "snippet-config" / "snippet-source-lock.json"
    write_lock(
        lock_path,
        {
            name: {
                "repository": "splice",
                "commit": "a" * 40,
                "remote": "https://github.com/canton-network/splice",
                "ref": "origin/main",
            }
        },
    )
    generated = (
        root / "docs-main" / "snippets" / "external" / "splice" / "main" / f"{name}.mdx"
    )
    generated.parent.mkdir(parents=True)
    generated.write_text("```python\nprint('old')\n```", encoding="utf-8")
    original_manifest = manifest.read_bytes()
    original_lock = lock_path.read_bytes()
    original_generated = generated.read_bytes()

    dry_run = author.main(["delete", "splice", name, "--dry-run"])

    assert dry_run == 0
    assert manifest.read_bytes() == original_manifest
    assert lock_path.read_bytes() == original_lock
    assert generated.read_bytes() == original_generated
    preview = capsys.readouterr().out
    assert "Dry run: would delete stable-example; no files written" in preview
    assert "--- a/config/snippet-config/splice-snippet-list-remote.json" in preview
    assert "--- a/config/snippet-config/snippet-source-lock.json" in preview
    assert "+++ /dev/null" in preview

    result = author.main(["delete", "splice", name])

    assert result == 0
    assert json.loads(manifest.read_text(encoding="utf-8"))["snippets"] == []
    assert json.loads(lock_path.read_text(encoding="utf-8"))["snippets"] == {}
    assert not generated.exists()


def test_delete_refuses_while_page_import_remains(
    authoring_fixture: tuple[Path, Path, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    root, manifest, _ = authoring_fixture
    name = "stable-example"
    write_manifest(
        manifest,
        [
            {
                "snippetName": name,
                "sourceRepo": "splice",
                "sourceFilepath": "example.py",
                "location": {"type": "fullFile"},
                "description": "",
                "options": {"language": "python"},
            }
        ],
    )
    generated = (
        root / "docs-main" / "snippets" / "external" / "splice" / "main" / f"{name}.mdx"
    )
    generated.parent.mkdir(parents=True)
    generated.write_text("content", encoding="utf-8")
    page = root / "docs-main" / "guide.mdx"
    page.write_text(
        f"import Example from '/snippets/external/splice/main/{name}';\n",
        encoding="utf-8",
    )
    original_manifest = manifest.read_bytes()

    result = author.main(["delete", "splice", name])

    assert result == 1
    assert manifest.read_bytes() == original_manifest
    assert generated.exists()
    error = capsys.readouterr().err
    assert "page references remain" in error
    assert "docs-main/guide.mdx:1" in error


@pytest.mark.parametrize("dry_run", [False, True])
@pytest.mark.parametrize(
    ("consumer", "reference"),
    [
        (
            "snippets/external/splice/main/wrapper.mdx",
            "import Example from './stable-example.mdx';",
        ),
        (
            "snippets/external/splice/main/wrapper.mdx",
            'import Example from "./stable-example";',
        ),
        (
            "snippets/external/splice/common/wrapper.mdx",
            "import Example from '../main/stable-example.mdx';",
        ),
        (
            "snippets/external/splice/main/wrapper.mdx",
            "import Example from '../main/./stable-example.mdx';",
        ),
        (
            "snippets/external/splice/main/wrapper.mdx",
            "import Example from\n  './stable-example.mdx';",
        ),
        (
            "snippets/external/splice/main/wrapper.js",
            "export { default as Example } from './stable-example.mdx';",
        ),
        (
            "snippets/external/splice/main/wrapper.tsx",
            "const Example = import('./stable-example.mdx');",
        ),
        (
            "snippets/external/splice/main/wrapper.jsx",
            "const Example = import(`./stable-example.mdx`);",
        ),
        (
            "snippets/external/splice/main/wrapper.mdx",
            "import Example from './stable-example.mdx?raw';",
        ),
        (
            "guide.mdx",
            "import Example from '/snippets/external/splice/main/stable-example.mdx#example';",
        ),
    ],
)
def test_delete_rejects_resolved_references_without_writing(
    authoring_fixture: tuple[Path, Path, Path],
    capsys: pytest.CaptureFixture[str],
    consumer: str,
    reference: str,
    dry_run: bool,
) -> None:
    root, manifest, _ = authoring_fixture
    name = "stable-example"
    write_manifest(manifest, [{"snippetName": name}])
    lock_path = author.source_lock_path()
    write_lock(lock_path, {name: {"repository": "splice", "commit": "a" * 40}})
    generated = author.output_path(author.REPOS["splice"], name)
    generated.parent.mkdir(parents=True)
    generated.write_text("example content", encoding="utf-8")
    page = root / "docs-main" / consumer
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(reference + "\n", encoding="utf-8")
    before = {
        path: path.read_bytes() for path in (manifest, lock_path, generated, page)
    }
    arguments = ["delete", "splice", name]
    if dry_run:
        arguments.append("--dry-run")

    assert author.main(arguments) == 1

    assert all(path.read_bytes() == content for path, content in before.items())
    error = capsys.readouterr().err
    assert "page references remain" in error
    assert f"docs-main/{consumer}:" in error


def test_delete_does_not_confuse_relative_import_of_another_snippet(
    authoring_fixture: tuple[Path, Path, Path],
) -> None:
    root, manifest, _ = authoring_fixture
    name = "stable-example"
    write_manifest(manifest, [{"snippetName": name}])
    generated = author.output_path(author.REPOS["splice"], name)
    generated.parent.mkdir(parents=True)
    generated.write_text("delete this", encoding="utf-8")
    other = root / "docs-main" / "snippets" / "internal" / f"{name}.mdx"
    other.parent.mkdir(parents=True)
    other.write_text("keep this", encoding="utf-8")
    page = other.parent / "wrapper.mdx"
    page.write_text("import Example from './stable-example.mdx';\n", encoding="utf-8")

    assert author.main(["delete", "splice", name]) == 0

    assert not generated.exists()
    assert other.read_text(encoding="utf-8") == "keep this"
    assert page.exists()
