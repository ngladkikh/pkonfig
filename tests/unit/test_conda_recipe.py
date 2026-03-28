from pathlib import Path


def test_conda_recipe_installs_unit_test_dependencies() -> None:
    recipe = Path("meta.yaml").read_text(encoding="utf-8")

    assert "    - mypy" in recipe
    assert "    - pydantic" in recipe
    assert "    - pydantic-settings" in recipe


def test_conda_recipe_runs_unit_tests_only() -> None:
    recipe = Path("meta.yaml").read_text(encoding="utf-8")

    assert "    - python -m pytest tests/unit" in recipe
    assert "    - python -m pytest tests\n" not in recipe
