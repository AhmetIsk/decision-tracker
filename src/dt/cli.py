from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from dt import __version__
from dt.commands import (
    DEFAULT_DISCOVER_KEYWORDS,
    backfill_command,
    build_site_command_handler,
    discover_command,
    init_command,
    new_command,
    report_command,
    validate_command,
)

app = typer.Typer(help="Decision Tracker CLI", invoke_without_command=True, no_args_is_help=True)


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", help="Show the installed Decision Tracker version.", is_eager=True),
) -> None:
    if version:
        typer.echo(f"decision-tracker {__version__}")
        raise typer.Exit()


@app.command()
def init(
    root: Optional[Path] = typer.Option(None, "--root", help="Repository root to initialize."),
    force: bool = typer.Option(False, "--force", help="Overwrite scaffolded files if they already exist."),
) -> None:
    """Initialize Decision Tracker files in the current repository."""
    init_command(root, force)


@app.command("build-site")
def build_site_command(
    root: Optional[Path] = typer.Option(None, "--root", help="Repository root containing decisions/."),
    site_dir: Optional[Path] = typer.Option(None, "--site-dir", help="Output directory. Defaults to ROOT/_site."),
    force: bool = typer.Option(False, "--force", help="Replace a non-empty output directory."),
) -> None:
    """Build the static viewer site."""
    build_site_command_handler(root, site_dir, force)


@app.command()
def report(root: Optional[Path] = typer.Option(None, "--root", help="Repository root containing decisions/.")) -> None:
    """Generate exports and metrics."""
    report_command(root)


@app.command()
def discover(
    root: Optional[Path] = typer.Option(None, "--root", help="Repository root to scan."),
    since: Optional[str] = typer.Option(None, "--since", help="Only scan commits after this Git date expression."),
    limit: int = typer.Option(20, "--limit", help="Maximum candidate count to print."),
    keywords: str = typer.Option(
        DEFAULT_DISCOVER_KEYWORDS,
        "--keywords",
        help="Comma-separated commit-message keywords to match.",
    ),
) -> None:
    """Suggest possible historical decision evidence from local Git history."""
    discover_command(root, since, limit, keywords)


@app.command()
def backfill(
    title: Optional[str] = typer.Option(None, "--title", help="Historical decision title."),
    stage: Optional[str] = typer.Option(None, "--stage", help="Decision stage."),
    type: Optional[str] = typer.Option(None, "--type", help="Decision type."),
    owner: Optional[str] = typer.Option(None, "--owner", help="Record owner."),
    stakeholders: str = typer.Option("", "--stakeholders", help="Comma-separated stakeholders."),
    original_decision_date: Optional[str] = typer.Option(
        None,
        "--original-decision-date",
        help='Original decision date as YYYY-MM-DD, or "unknown".',
    ),
    evidence_refs: Optional[str] = typer.Option(
        None,
        "--evidence",
        help="Comma-separated evidence refs to preserve and map into links.",
    ),
    confidence: Optional[str] = typer.Option(None, "--confidence", help="Evidence confidence: low|medium|high."),
    known_gaps: str = typer.Option("", "--known-gaps", help="Semicolon-separated known evidence gaps."),
    context: Optional[str] = typer.Option(None, "--context", help="Context section text."),
    decision: Optional[str] = typer.Option(None, "--decision", help="Decision section text."),
    rationale: Optional[str] = typer.Option(None, "--rationale", help="Rationale section text."),
    alternatives: Optional[str] = typer.Option(None, "--alternatives", help="Alternatives section text."),
    consequences: Optional[str] = typer.Option(None, "--consequences", help="Consequences section text."),
    root: Optional[Path] = typer.Option(None, "--root", help="Repository root containing decisions/."),
) -> None:
    """Create a proposed Decision Record by guiding historical reconstruction."""
    backfill_command(
        title,
        stage,
        type,
        owner,
        stakeholders,
        original_decision_date,
        evidence_refs,
        confidence,
        known_gaps,
        context,
        decision,
        rationale,
        alternatives,
        consequences,
        root,
    )


@app.command()
def validate(
    all: bool = typer.Option(False, "--all"),
    id: str = typer.Option(None, "--id"),
    root: Optional[Path] = typer.Option(None, "--root", help="Repository root containing decisions/."),
) -> None:
    """Validate one record or all records."""
    validate_command(all, id, root)


@app.command()
def new(
    title: str = typer.Option(..., "--title"),
    stage: str = typer.Option(..., "--stage"),
    type: str = typer.Option(..., "--type"),
    owner: str = typer.Option(..., "--owner"),
    stakeholders: str = typer.Option("", "--stakeholders"),
    git_head: bool = typer.Option(False, "--git-head", help="Add the current Git HEAD commit as a code link."),
    root: Optional[Path] = typer.Option(None, "--root", help="Repository root containing decisions/."),
) -> None:
    """Create a new Decision Record."""
    new_command(title, stage, type, owner, stakeholders, git_head, root)


if __name__ == "__main__":
    app()
