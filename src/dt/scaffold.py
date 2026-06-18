from __future__ import annotations

from pathlib import Path

import typer

from dt.models import ScaffoldChanges
from dt.paths import _display_path
from dt.site import workflow_template


def _write_scaffold_file(path: Path, content: str, force: bool, changes: ScaffoldChanges) -> None:
    if path.exists() and not force:
        changes.skipped.append(path.as_posix())
        return
    existed = path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    (changes.replaced if existed else changes.created).append(path.as_posix())


def _touch_scaffold_file(path: Path, force: bool, changes: ScaffoldChanges) -> None:
    if path.exists() and not force:
        changes.skipped.append(path.as_posix())
        return
    existed = path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")
    (changes.replaced if existed else changes.created).append(path.as_posix())


def initialize_project(root: Path, force: bool) -> None:
    changes = ScaffoldChanges()

    try:
        (root / "decisions").mkdir(parents=True, exist_ok=True)
        (root / "docs").mkdir(parents=True, exist_ok=True)
        _touch_scaffold_file(root / "decisions" / ".gitkeep", force, changes)
        _write_scaffold_file(
            root / ".gitignore",
            "# Decision Tracker generated outputs\n"
            "_site/\n"
            "reports/\n"
            "decisions/index.json\n"
            "decisions/graph.json\n"
            "decisions/artifacts.json\n",
            force,
            changes,
        )
        _write_scaffold_file(
            root / "docs" / "README.md",
            "# Decision support notes\n\nUse this directory for notes linked from Decision Records with `path:docs/...` refs.\n",
            force,
            changes,
        )
        _write_scaffold_file(root / ".github" / "workflows" / "pages.yml", workflow_template(), force, changes)
    except OSError as exc:
        typer.echo(f"FAIL INIT_IO_ERROR: {exc}")
        raise typer.Exit(code=2)

    for path in changes.created:
        typer.echo(f"Created {_display_path(path, root)}")
    for path in changes.replaced:
        typer.echo(f"Replaced {_display_path(path, root)}")
    for path in changes.skipped:
        typer.echo(f"Exists {_display_path(path, root)}")
    if not changes.created and not changes.replaced and not changes.skipped:
        typer.echo("No scaffold changes needed")
