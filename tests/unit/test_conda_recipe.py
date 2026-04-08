from importlib.resources import files
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


def test_conda_recipe_copies_meta_yaml_for_recipe_regression_checks() -> None:
    recipe = Path("meta.yaml").read_text(encoding="utf-8")

    assert "    - meta.yaml" in recipe


def test_package_declares_py_typed_marker() -> None:
    assert (files("pkonfig") / "py.typed").is_file()
