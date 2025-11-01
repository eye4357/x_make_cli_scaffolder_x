from __future__ import annotations

# ruff: noqa: S101
import json
import pathlib
from typing import TYPE_CHECKING, cast

import pytest

from x_make_cli_scaffolder_x.x_cls_make_cli_scaffolder_x import (
    CliScaffolder,
    ProjectConfig,
    RunResult,
    main,
    run,
)

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


def _load_json_object(raw: str) -> dict[str, object]:
    loaded = cast("object", json.loads(raw))
    assert isinstance(loaded, dict)
    return cast("dict[str, object]", loaded)


def _collect_relative_paths(root: pathlib.Path) -> set[str]:
    return {
        str(path.relative_to(root)).replace("\\", "/")
        for path in root.rglob("*")
        if path.is_file()
    }


def test_project_config_from_mapping_defaults() -> None:
    config = ProjectConfig.from_mapping({"project_name": "My CLI"})
    assert config.package_name == "my_cli"
    assert config.resolved_script_name == "my-cli"
    assert config.console_entrypoint == "my_cli.cli:main"
    assert config.include_tests is True
    assert config.include_license is True


def test_cli_scaffolder_creates_expected_structure(
    tmp_workspace: pathlib.Path,
) -> None:
    config = ProjectConfig(
        project_name="Demo",
        package_name="demo",
        description="Demo app",
        author="Legatus",
        version="0.2.0",
        python_version="3.11",
    )
    result = CliScaffolder().scaffold(tmp_workspace, config)
    expected_files = {
        "README.md",
        "pyproject.toml",
        ".gitignore",
        "LICENSE",
        "src/demo/__init__.py",
        "src/demo/cli.py",
        "src/demo/__main__.py",
        "src/demo/py.typed",
        "tests/__init__.py",
        "tests/test_cli.py",
    }
    assert _collect_relative_paths(result.root_path) == expected_files


def test_cli_scaffolder_respects_overwrite(tmp_workspace: pathlib.Path) -> None:
    config = ProjectConfig(
        project_name="Overwrite",
        package_name="overwrite",
    )
    scaffolder = CliScaffolder()
    first = scaffolder.scaffold(tmp_workspace, config)
    (first.root_path / "README.md").write_text("updated", encoding="utf-8")
    with pytest.raises(FileExistsError):
        scaffolder.scaffold(tmp_workspace, config)
    overwriting = CliScaffolder(overwrite=True)
    result = overwriting.scaffold(tmp_workspace, config)
    assert (
        (result.root_path / "README.md")
        .read_text(encoding="utf-8")
        .startswith("# Overwrite")
    )


def test_run_entrypoint(tmp_workspace: pathlib.Path) -> None:
    payload: dict[str, object] = {
        "parameters": {
            "project_name": "Runner",
            "target_dir": str(tmp_workspace),
        }
    }
    output: RunResult = run(payload)
    assert output["status"] == "success"
    created = {pathlib.Path(path) for path in output["created_files"]}
    assert created
    root_path = pathlib.Path(output["root_path"])
    assert root_path.exists()


def test_cli_entrypoint_json(
    tmp_workspace: pathlib.Path, capsys: CaptureFixture[str]
) -> None:
    args = [
        "--project-name",
        "JsonCli",
        "--target-dir",
        str(tmp_workspace),
        "--json",
    ]
    exit_code = main(args)
    assert exit_code == 0
    output = _load_json_object(capsys.readouterr().out)
    assert output.get("status") == "success"
    assert "root_path" in output
