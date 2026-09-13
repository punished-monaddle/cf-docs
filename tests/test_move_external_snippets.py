from __future__ import annotations

import json
import stat
from pathlib import Path

import pytest

from scripts import manage_external_snippets as author
from tests.snippet_authoring_helpers import commit_source, write_manifest


def test_move_preserves_name_and_regenerates_output(
    authoring_fixture: tuple[Path, Path, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    root, manifest, source_dir = authoring_fixture
    name = "stable-example"
    write_manifest(
        manifest,
        [
            {
                "snippetName": name,
                "sourceRepo": "splice",
                "sourceFilepath": "old.yaml",
                "location": {"type": "fullFile"},
                "description": "keep this",
                "options": {"language": "yaml", "normalizeIndent": False},
            }
        ],
    )
    source = source_dir / "new.yaml"
    source.write_text(
        "# CURRENT_START\n  nested: true\n# CURRENT_END\n",
        encoding="utf-8",
    )
    commit_source(source_dir)

    manifest.chmod(0o640)
    result = author.main(
        [
            "move",
            "splice",
            name,
            "--source-dir",
            str(source_dir),
            "--source",
            "new.yaml",
            "--marker",
            "CURRENT",
        ]
    )

    assert result == 0
    entry = json.loads(manifest.read_text(encoding="utf-8"))["snippets"][0]
    assert entry["snippetName"] == name
    assert entry["sourceFilepath"] == "new.yaml"
    assert entry["location"] == {
        "type": "stringMarker",
        "start": "CURRENT_START",
        "end": "CURRENT_END",
    }
    assert entry["description"] == "keep this"
    assert entry["options"] == {"language": "yaml", "normalizeIndent": False}
    assert stat.S_IMODE(manifest.stat().st_mode) == 0o640
    output = (
        root / "docs-main" / "snippets" / "external" / "splice" / "main" / f"{name}.mdx"
    )
    assert output.read_text(encoding="utf-8") == "```yaml\n  nested: true\n```"
    captured = capsys.readouterr().out
    assert "Moved stable-example; its import path is unchanged" in captured
    assert "origin/main" in captured



def test_edit_dry_run_diffs_manifest_and_existing_output_without_writing(
    authoring_fixture: tuple[Path, Path, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    root, manifest, source_dir = authoring_fixture
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
    source = source_dir / "example.py"
    source.write_text("print('new')\n", encoding="utf-8")
    commit_source(source_dir)
    generated = (
        root / "docs-main" / "snippets" / "external" / "splice" / "main" / f"{name}.mdx"
    )
    generated.parent.mkdir(parents=True)
    generated.write_text("```python\nprint('old')\n```", encoding="utf-8")
    original_manifest = manifest.read_bytes()
    original_generated = generated.read_bytes()

    result = author.main(
        [
            "edit",
            "splice",
            name,
            "--source-dir",
            str(source_dir),
            "--language",
            "javascript",
            "--dry-run",
        ]
    )

    assert result == 0
    assert manifest.read_bytes() == original_manifest
    assert generated.read_bytes() == original_generated
    output = capsys.readouterr().out
    assert "Dry run: would edit stable-example; no files written" in output
    assert '-        "language": "python"' in output
    assert '+        "language": "javascript"' in output
    assert "-```python" in output
    assert "+```javascript" in output
    assert "-print('old')" in output
    assert "+print('new')" in output



@pytest.mark.parametrize("command", ["edit", "move"])
def test_update_rejects_dirty_symlink_target_without_changing_files(
    authoring_fixture: tuple[Path, Path, Path],
    capsys: pytest.CaptureFixture[str],
    command: str,
) -> None:
    _, manifest, source_dir = authoring_fixture
    name = "stable-example"
    source = source_dir / "real.py"
    source.write_text("print('committed')\n", encoding="utf-8")
    (source_dir / "linked.py").symlink_to("real.py")
    commit_source(source_dir)
    source.write_text("print('uncommitted')\n", encoding="utf-8")
    write_manifest(manifest, [{
        "snippetName": name,
        "sourceFilepath": "linked.py" if command == "edit" else "old.py",
        "location": {"type": "fullFile"},
        "options": {"language": "python"},
    }])
    output = author.output_path(author.REPOS["splice"], name)
    output.parent.mkdir(parents=True)
    output.write_text("previous output", encoding="utf-8")
    original_manifest = manifest.read_bytes()
    arguments = [command, "splice", name, "--source-dir", str(source_dir)]
    arguments += ["--source", "linked.py"] if command == "move" else ["--language", "python"]

    assert author.main(arguments) == 1

    assert "must not contain symlinks" in capsys.readouterr().err
    assert manifest.read_bytes() == original_manifest
    assert output.read_text(encoding="utf-8") == "previous output"
    assert not author.source_lock_path().exists()


def test_move_dry_run_keeps_existing_selector_and_language(
    authoring_fixture: tuple[Path, Path, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    _, manifest, source_dir = authoring_fixture
    name = "stable-example"
    write_manifest(manifest, [{
        "snippetName": name,
        "sourceFilepath": "old.yaml",
        "location": {"type": "fullFile"},
        "options": {"language": "yaml"},
    }])
    (source_dir / "new.yaml").write_text("enabled: true\n", encoding="utf-8")
    commit_source(source_dir)
    output = author.output_path(author.REPOS["splice"], name)
    output.parent.mkdir(parents=True)
    output.write_text("```yaml\nenabled: false\n```", encoding="utf-8")
    before = {manifest: manifest.read_bytes(), output: output.read_bytes()}

    assert author.main([
        "move", "splice", name, "--source-dir", str(source_dir),
        "--source", "new.yaml", "--dry-run",
    ]) == 0

    assert all(path.read_bytes() == content for path, content in before.items())
    assert not author.source_lock_path().exists()
    preview = capsys.readouterr().out
    assert '+      "sourceFilepath": "new.yaml"' in preview
    assert "+enabled: true" in preview
    assert '-      "location"' not in preview
    assert '-        "language"' not in preview
