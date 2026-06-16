from pathlib import Path

from typer.testing import CliRunner

from dt.cli import app


def test_init_creates_minimal_scaffold(tmp_path: Path):
    runner = CliRunner()

    result = runner.invoke(app, ["init", "--root", str(tmp_path)])

    assert result.exit_code == 0, result.output
    assert (tmp_path / "decisions" / ".gitkeep").exists()
    assert (tmp_path / "docs" / "README.md").exists()
    workflow = tmp_path / ".github" / "workflows" / "pages.yml"
    assert workflow.exists()
    text = workflow.read_text(encoding="utf-8")
    assert "dt validate --all" in text
    assert "dt report" in text
    assert "dt build-site --root ." in text


def test_init_does_not_overwrite_existing_files_without_force(tmp_path: Path):
    runner = CliRunner()
    workflow = tmp_path / ".github" / "workflows" / "pages.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text("custom workflow\n", encoding="utf-8")

    result = runner.invoke(app, ["init", "--root", str(tmp_path)])

    assert result.exit_code == 0, result.output
    assert workflow.read_text(encoding="utf-8") == "custom workflow\n"
    assert "Exists" in result.output


def test_init_force_overwrites_scaffolded_files(tmp_path: Path):
    runner = CliRunner()
    workflow = tmp_path / ".github" / "workflows" / "pages.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text("custom workflow\n", encoding="utf-8")

    result = runner.invoke(app, ["init", "--root", str(tmp_path), "--force"])

    assert result.exit_code == 0, result.output
    assert "dt build-site --root ." in workflow.read_text(encoding="utf-8")
