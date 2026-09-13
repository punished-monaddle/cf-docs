from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from scripts import manage_external_snippets as author


def write_manifest(path: Path, snippets: list[dict] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "urlSubstitutions": {"https://example.invalid": "replacement"},
                "snippets": snippets or [],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )



def commit_source(source_dir: Path, message: str = "Record source") -> str:
    subprocess.run(["git", "-C", source_dir, "add", "--all"], check=True)
    subprocess.run(["git", "-C", source_dir, "commit", "-q", "-m", message], check=True)
    commit = subprocess.run(
        ["git", "-C", source_dir, "rev-parse", "HEAD"],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    subprocess.run(
        ["git", "-C", source_dir, "update-ref", "refs/remotes/origin/main", commit],
        check=True,
    )
    subprocess.run(
        ["git", "-C", source_dir, "branch", "--set-upstream-to=origin/main"],
        check=True,
        capture_output=True,
    )
    return commit



@pytest.fixture
def authoring_fixture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, Path, Path]:
    real_helper = author.helper_path()
    root = tmp_path / "cf-docs"
    helper = root / "scripts" / "helpers" / "generateOutputDocs.js"
    helper.parent.mkdir(parents=True)
    shutil.copy2(real_helper, helper)
    manifest = root / "config" / "snippet-config" / "splice-snippet-list-remote.json"
    write_manifest(manifest)
    source_dir = tmp_path / "splice"
    subprocess.run(["git", "init", "-q", "-b", "main", source_dir], check=True)
    subprocess.run(
        ["git", "-C", source_dir, "config", "user.name", "Snippet Tests"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", source_dir, "config", "user.email", "snippets@example.com"],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            source_dir,
            "remote",
            "add",
            "origin",
            "git@github.com:canton-network/splice.git",
        ],
        check=True,
    )
    monkeypatch.setattr(author, "CF_DOCS_ROOT", root)
    return root, manifest, source_dir

