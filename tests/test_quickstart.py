from pathlib import Path


def test_quickstart_references_existing_project_artifacts():
    root = Path(__file__).parents[1]
    assert (root / "docker-compose.yml").exists()
    assert (root / "README.md").exists()
    assert (root / "docs" / "architecture.md").exists()
    assert "docker compose up" in (root / "README.md").read_text(encoding="utf-8")
