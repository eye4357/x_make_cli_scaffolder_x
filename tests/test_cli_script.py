from __future__ import annotations

# ruff: noqa: S101
import os
import subprocess
import sys
from typing import TYPE_CHECKING

from x_make_cli_scaffolder_x.x_cls_make_cli_scaffolder_x import (
    CliScaffolder,
    ProjectConfig,
)

if TYPE_CHECKING:
    import pathlib


def test_generated_cli_runs(tmp_path: pathlib.Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    config = ProjectConfig(project_name="LiveRun", package_name="live_run")
    result = CliScaffolder().scaffold(workspace, config)
    module_path = result.root_path / "src"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(module_path)
    completed = subprocess.run(  # noqa: S603
        [sys.executable, "-m", config.package_name, "--name", "Tester"],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    assert "Hello, Tester!" in completed.stdout
