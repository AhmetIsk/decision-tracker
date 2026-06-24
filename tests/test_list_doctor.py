import json
import shutil
import subprocess
from pathlib import Path


def _prepare_workdir(tmp_path: Path) -> Path:
    repo = Path(__file__).resolve().parents[1]
    fixtures = repo / "fixtures" / "decisions"
    work = tmp_path / "work"
    work.mkdir()
    decisions = work / "decisions"
    decisions.mkdir()
    for path in fixtures.glob("*.md"):
        shutil.copy2(path, decisions / path.name)
    return work


def test_list_prints_table_in_id_order(tmp_path: Path):
    work = _prepare_workdir(tmp_path)

    result = subprocess.run(["dt", "list"], cwd=work, capture_output=True, text=True)

    assert result.returncode == 0, result.stdout + result.stderr
    lines = result.stdout.splitlines()
    assert lines[0].startswith("ID")
    assert "DR-0001" in lines[2]
    assert "DR-0006" in lines[-1]


def test_list_filters_and_outputs_json(tmp_path: Path):
    work = _prepare_workdir(tmp_path)

    result = subprocess.run(
        ["dt", "list", "--type", "model", "--stage", "training", "--format", "json"],
        cwd=work,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    rows = json.loads(result.stdout)
    assert [row["id"] for row in rows] == ["DR-0002"]
    assert rows[0]["type"] == "model"
    assert rows[0]["stage"] == "training"
    assert rows[0]["parse_error"] is False
    assert rows[0]["parse_error_message"] == ""


def test_list_marks_parse_error_records_in_table(tmp_path: Path):
    work = tmp_path / "work"
    work.mkdir()
    decisions = work / "decisions"
    decisions.mkdir()
    (decisions / "DR-0001-broken.md").write_text(
        "---\n"
        "id: DR-0001\n"
        "title: Broken\n"
        "links: [\n"
        "---\n",
        encoding="utf-8",
    )

    result = subprocess.run(["dt", "list"], cwd=work, capture_output=True, text=True)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "DR-0001" in result.stdout
    assert "(parse error)" in result.stdout
    assert "Invalid YAML front matter" in result.stdout


def test_list_marks_parse_error_records_in_json(tmp_path: Path):
    work = tmp_path / "work"
    work.mkdir()
    decisions = work / "decisions"
    decisions.mkdir()
    (decisions / "DR-0001-broken.md").write_text(
        "---\n"
        "id: DR-0001\n"
        "title: Broken\n"
        "links: [\n"
        "---\n",
        encoding="utf-8",
    )

    result = subprocess.run(["dt", "list", "--format", "json"], cwd=work, capture_output=True, text=True)

    assert result.returncode == 0, result.stdout + result.stderr
    rows = json.loads(result.stdout)
    assert rows == [
        {
            "date": "",
            "id": "DR-0001",
            "owner": "",
            "parse_error": True,
            "parse_error_message": "Invalid YAML front matter",
            "stage": "",
            "status": "(parse error)",
            "title": "Invalid YAML front matter",
            "type": "",
        }
    ]


def test_list_keeps_parse_error_records_under_filters(tmp_path: Path):
    work = tmp_path / "work"
    work.mkdir()
    decisions = work / "decisions"
    decisions.mkdir()
    (decisions / "DR-0001-good.md").write_text(
        "---\n"
        "id: DR-0001\n"
        "title: Good\n"
        "status: proposed\n"
        "type: generic\n"
        "stage: training\n"
        "date: '2026-03-14'\n"
        "owner: ahmet\n"
        "stakeholders: []\n"
        "template_version: '1.0'\n"
        "links: []\n"
        "---\n"
        "\n"
        "## Context\nx\n\n## Decision\nx\n\n## Rationale\nx\n\n## Alternatives\nx\n\n## Consequences\nx\n",
        encoding="utf-8",
    )
    (decisions / "DR-0002-broken.md").write_text("---\nid: DR-0002\nlinks: [\n---\n", encoding="utf-8")

    table = subprocess.run(["dt", "list", "--status", "accepted"], cwd=work, capture_output=True, text=True)
    as_json = subprocess.run(
        ["dt", "list", "--status", "accepted", "--format", "json"],
        cwd=work,
        capture_output=True,
        text=True,
    )

    assert table.returncode == 0, table.stdout + table.stderr
    assert "DR-0001" not in table.stdout
    assert "DR-0002" in table.stdout
    assert "(parse error)" in table.stdout

    assert as_json.returncode == 0, as_json.stdout + as_json.stderr
    rows = json.loads(as_json.stdout)
    assert [row["id"] for row in rows] == ["DR-0002"]
    assert rows[0]["parse_error"] is True


def test_list_empty_table_prints_friendly_message(tmp_path: Path):
    work = tmp_path / "work"
    work.mkdir()
    (work / "decisions").mkdir()

    result = subprocess.run(["dt", "list"], cwd=work, capture_output=True, text=True)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == "No decisions found. Run `dt new ...` to create one."


def test_list_empty_filtered_table_prints_friendly_message(tmp_path: Path):
    work = _prepare_workdir(tmp_path)

    result = subprocess.run(["dt", "list", "--status", "rejected"], cwd=work, capture_output=True, text=True)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == "No decisions match the given filters."


def test_list_empty_json_outputs_empty_array(tmp_path: Path):
    work = tmp_path / "work"
    work.mkdir()
    (work / "decisions").mkdir()

    result = subprocess.run(["dt", "list", "--format", "json"], cwd=work, capture_output=True, text=True)

    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout) == []


def test_list_missing_decisions_dir_is_filesystem_error(tmp_path: Path):
    result = subprocess.run(["dt", "list"], cwd=tmp_path, capture_output=True, text=True)

    assert result.returncode == 2
    assert "FAIL DECISIONS_DIR_MISSING" in result.stdout


def test_doctor_reports_missing_decisions_dir(tmp_path: Path):
    result = subprocess.run(["dt", "doctor", "--root", str(tmp_path)], cwd=tmp_path, capture_output=True, text=True)

    assert result.returncode == 2
    assert "FAIL decisions_dir" in result.stdout


def test_doctor_json_is_parseable_for_initialized_project(tmp_path: Path):
    work = tmp_path / "repo"
    work.mkdir()
    init = subprocess.run(["dt", "init", "--root", str(work)], cwd=tmp_path, capture_output=True, text=True)
    assert init.returncode == 0, init.stdout + init.stderr

    result = subprocess.run(
        ["dt", "doctor", "--root", str(work), "--format", "json"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    checks = json.loads(result.stdout)
    by_name = {item["name"]: item for item in checks}
    assert by_name["decisions_dir"]["status"] == "OK"
    assert by_name["viewer_assets"]["status"] == "OK"
